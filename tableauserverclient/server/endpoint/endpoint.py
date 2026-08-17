from email.message import Message
import io
import os
from contextlib import closing
from typing_extensions import Concatenate, ParamSpec
from urllib.parse import urljoin, urlparse
from tableauserverclient import datetime_helpers as datetime

import abc
from packaging.version import Version
from functools import wraps
from xml.etree.ElementTree import ParseError
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    Union,
)
from typing_extensions import Self

from tableauserverclient.models.pagination_item import PaginationItem
from tableauserverclient.server.request_options import RequestOptions
from tableauserverclient.filesys_helpers import to_filename, make_download_path

from tableauserverclient.server.endpoint.exceptions import (
    FailedSignInError,
    ServerResponseError,
    InternalServerError,
    NonXMLResponseError,
    NotSignedInError,
    RedirectError,
)
from tableauserverclient.server.exceptions import EndpointUnavailableError

from tableauserverclient.server.query import QuerySet
from tableauserverclient import helpers, get_versions

from tableauserverclient.helpers.logging import logger

if TYPE_CHECKING:
    from tableauserverclient.server.server import Server
    from requests import Response


Success_codes = [200, 201, 202, 204]

# 301/302/303/307/308 all indicate the caller should re-request at a new URL.
# `requests`' default handler converts POST -> GET on 301/302/303, which drops
# the POST body and breaks sign-in / addusers / publish / any write endpoint
# whose target sits behind a redirect. We disable that and walk the chain
# manually, keeping the original method and body across every hop.
#
# RFC 7231 §6.4.4 says 303 SHOULD change the method to GET on retry. We do NOT
# follow that recommendation, deliberately: Tableau Server does not emit 303
# for POST endpoints in normal operation (writes redirect via 301/302 in
# proxy/HA setups), and preserving the method + body uniformly is the
# behavior that fixes the reported bug (#1127). If a Tableau deployment ever
# starts emitting 303 for writes, revisit; treating it identically today is
# a conscious deviation, not an oversight.
Redirect_codes = [301, 302, 303, 307, 308]

XML_CONTENT_TYPE = "text/xml"
JSON_CONTENT_TYPE = "application/json"

CONTENT_TYPE_HEADER = "content-type"
TABLEAU_AUTH_HEADER = "x-tableau-auth"
USER_AGENT_HEADER = "User-Agent"


class Endpoint:
    def __init__(self, parent_srv: "Server"):
        self.parent_srv = parent_srv

    async_response = None

    @staticmethod
    def set_parameters(http_options, auth_token, content, content_type, parameters) -> dict[str, Any]:
        parameters = parameters or {}
        parameters.update(http_options)
        if "headers" not in parameters:
            parameters["headers"] = {}

        if auth_token is not None:
            parameters["headers"][TABLEAU_AUTH_HEADER] = auth_token
        if content_type is not None:
            parameters["headers"][CONTENT_TYPE_HEADER] = content_type

        Endpoint.set_user_agent(parameters)
        if content is not None:
            parameters["data"] = content
        return parameters or {}

    @staticmethod
    def set_user_agent(parameters):
        if "headers" not in parameters:
            parameters["headers"] = {}
        if USER_AGENT_HEADER not in parameters["headers"]:
            if USER_AGENT_HEADER in parameters:
                parameters["headers"][USER_AGENT_HEADER] = parameters[USER_AGENT_HEADER]
            else:
                # only set the TSC user agent if not already populated
                _client_version: str | None = get_versions()["version"]
                parameters["headers"][USER_AGENT_HEADER] = f"Tableau Server Client/{_client_version}"

        # result: parameters["headers"]["User-Agent"] is set
        # return explicitly for testing only
        return parameters

    def _blocking_request(self, method, url, parameters={}) -> "Response | Exception | None":
        response = None
        logger.debug(f"[{datetime.timestamp()}] Begin blocking request to {url}")
        try:
            response = method(url, **parameters)
            logger.debug(f"[{datetime.timestamp()}] Call finished")
        except Exception as e:
            logger.debug(f"Error making request to server: {e}")
            raise e
        return response

    def send_request_while_show_progress_threaded(
        self, method, url, parameters={}, request_timeout=None
    ) -> "Response | Exception | None":
        return self._blocking_request(method, url, parameters)

    def _make_request(
        self,
        method: Callable[..., "Response"],
        url: str,
        content: bytes | None = None,
        auth_token: str | None = None,
        content_type: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> "Response":
        parameters = Endpoint.set_parameters(
            self.parent_srv.http_options, auth_token, content, content_type, parameters
        )
        # Manual redirect handling: see Redirect_codes comment. `requests`
        # follows 301/302/303 by converting POST to GET (RFC-conforming but
        # loses the body). We disable it here and re-issue the same method
        # ourselves in _follow_redirect_if_any.
        parameters["allow_redirects"] = False

        logger.debug(f"request method {method.__name__}, url: {url}")
        if content:
            redacted = helpers.strings.redact_xml(content[:200])
            # this needs to be under a trace or something, it's a LOT
            # logger.debug("request content: {}".format(redacted))

        # a request can, for stuff like publishing, spin for ages waiting for a response.
        # we need some user-facing activity so they know it's not dead.
        request_timeout = self.parent_srv.http_options.get("timeout") or 0
        server_response: "Response | Exception | None" = self.send_request_while_show_progress_threaded(
            method, url, parameters, request_timeout
        )
        logger.debug(f"[{datetime.timestamp()}] Async request returned: received {server_response}")
        # is this blocking retry really necessary? I guess if it was just the threading messing it up?
        if server_response is None:
            logger.debug(server_response)
            logger.debug(f"[{datetime.timestamp()}] Async request failed: retrying")
            server_response = self._blocking_request(method, url, parameters)
        if server_response is None:
            logger.debug(f"[{datetime.timestamp()}] Request failed")
            raise RuntimeError
        if isinstance(server_response, Exception):
            raise server_response
        server_response, url = self._follow_redirect_if_any(method, url, parameters, server_response)
        self._check_status(server_response, url)

        loggable_response = self.log_response_safely(server_response)
        logger.debug(f"Server response from {url}")
        # uncomment the following to log full responses in debug mode
        # BE CAREFUL WHEN SHARING THESE RESULTS - MAY CONTAIN YOUR SENSITIVE DATA
        # logger.debug(loggable_response)

        if content_type == "application/xml":
            self.parent_srv._namespace.detect(server_response.content)

        return server_response

    def _follow_redirect_if_any(
        self,
        method: Callable[..., "Response"],
        url: str,
        parameters: dict[str, Any],
        server_response: "Response",
    ) -> tuple["Response", str]:
        # Walk a 301/302/303/307/308 chain up to session.max_redirects hops,
        # preserving method and body. Rejects HTTPS -> HTTP scheme downgrades
        # (silent security regression). Raises RedirectError on a missing
        # Location header instead of the KeyError requests emits deep in its
        # internals, and on exceeding the session hop limit.
        try:
            max_hops = int(self.parent_srv.session.max_redirects)
        except (AttributeError, TypeError):
            max_hops = 30  # requests' library default
        current_url = url
        response = server_response
        # Not a redirect? Return immediately regardless of max_hops (including 0).
        if response.status_code not in Redirect_codes:
            return response, current_url
        method_name = getattr(method, "__name__", "REQUEST").upper()
        for _ in range(max_hops):
            location = response.headers.get("Location")
            if not location:
                raise RedirectError(
                    f"{method_name} {current_url} returned HTTP {response.status_code} "
                    f"without a Location header; can't follow the redirect."
                )
            # Support relative Locations per RFC 7231.
            next_url = urljoin(current_url, location)
            current_scheme = urlparse(current_url).scheme
            next_scheme = urlparse(next_url).scheme
            if current_scheme == "https" and next_scheme == "http":
                raise RedirectError(
                    f"Refusing to follow redirect from {current_url} to {next_url}: "
                    f"HTTPS -> HTTP scheme downgrade would send request data over plaintext."
                )
            # http -> https upgrade on the same host: promote the stored server
            # address so subsequent requests skip this redirect round-trip.
            # Only rewrite on same-host, same-path-root redirects to avoid
            # accidentally pointing the client at an unrelated server.
            if current_scheme == "http" and next_scheme == "https":
                current_parsed = urlparse(current_url)
                next_parsed = urlparse(next_url)
                if current_parsed.netloc == next_parsed.netloc:
                    old_address = self.parent_srv._server_address
                    if old_address.startswith("http://") and old_address[7:].startswith(current_parsed.netloc):
                        new_address = "https://" + old_address[7:]
                        self.parent_srv._server_address = new_address
                        logger.info(f"Server redirected to HTTPS; updated server address to {new_address}")
            # Auth-material policy: the request `parameters` (including the
            # X-Tableau-Auth header and any session cookies) are forwarded
            # to the redirect target unchanged. This is intentional and
            # required. TSC is a client library for a specific server the
            # caller has already agreed to trust, and customers routinely
            # deploy Tableau Server behind reverse proxies, load balancers,
            # and SSO front-ends that redirect between hosts within their
            # own infrastructure (e.g. tableau.corp.example -> east.tableau.
            # corp.example, or an SSO IdP -> the auth-callback endpoint on
            # a different subdomain). Stripping X-Tableau-Auth on cross-
            # host redirects would break sign-in against every such
            # deployment. The HTTPS -> HTTP downgrade guard above (line 208)
            # is the boundary that keeps this from becoming a security
            # regression: once the caller connects over HTTPS, the token
            # never leaves TLS.
            logger.debug(f"Following {response.status_code} redirect: {current_url} -> {next_url}")
            current_url = next_url
            next_response = self._blocking_request(method, current_url, parameters)
            if next_response is None:
                raise RuntimeError(f"No response after redirect to {current_url}")
            if isinstance(next_response, Exception):
                # _blocking_request already re-raises via except -> raise, so this
                # branch is defensive; keep it to satisfy the Response|Exception|None
                # return type.
                raise next_response
            response = next_response
            if response.status_code not in Redirect_codes:
                return response, current_url
        # Still a redirect after max_hops hops -> loop / misconfiguration.
        raise RedirectError(
            f"Exceeded {max_hops} redirect hops starting from {url}; last Location was {current_url}. "
            f"Increase session.max_redirects if this is legitimate."
        )

    def _check_status(self, server_response: "Response", url: str | None = None):
        logger.debug(f"Response status: {server_response}")
        if not hasattr(server_response, "status_code"):
            raise OSError("Response is not a http response?")
        if server_response.status_code >= 500:
            raise InternalServerError(server_response, url)
        elif server_response.status_code not in Success_codes:
            try:
                if server_response.status_code == 401:
                    # TODO: catch this in server.py and attempt to sign in again, in case it's a session expiry
                    raise FailedSignInError.from_response(server_response.content, self.parent_srv.namespace, url)

                raise ServerResponseError.from_response(server_response.content, self.parent_srv.namespace, url)
            except ParseError:
                # This will happen if we get a non-success HTTP code that doesn't return an xml error object
                # e.g. metadata endpoints, 503 pages, totally different servers
                # we convert this to a better exception and pass through the raw response body
                raise NonXMLResponseError(server_response.content)
            except Exception:
                # anything else re-raise here
                raise

    def log_response_safely(self, server_response: "Response") -> str:
        # Checking the content type header prevents eager evaluation of streaming requests.
        content_type = server_response.headers.get("Content-Type")

        # Response.content is a property. Calling it will load the entire response into memory. Checking if the
        # content-type is an octet-stream accomplishes the same goal without eagerly loading content.
        # This check is to determine if the response is a text response (xml or otherwise)
        # so that we do not attempt to log bytes and other binary data.
        loggable_response = f"Content type `{content_type}`"
        if content_type == "application/octet-stream":
            loggable_response = f"A stream of type {content_type} [Truncated File Contents]"
        elif server_response.encoding and len(server_response.content) > 0:
            loggable_response = helpers.strings.redact_xml(server_response.content.decode(server_response.encoding))
        return loggable_response

    def get_unauthenticated_request(self, url):
        return self._make_request(self.parent_srv.session.get, url)

    def get_request(self, url, request_object=None, parameters=None):
        if request_object is not None:
            try:
                # Query param delimiters don't need to be encoded for versions before 3.7 (2020.1)
                self.parent_srv.assert_at_least_version("3.7", "Query param encoding")
                parameters = parameters or {}
                parameters["params"] = request_object.get_query_params()
            except EndpointUnavailableError:
                url = request_object.apply_query_params(url)

        return self._make_request(
            self.parent_srv.session.get,
            url,
            auth_token=self.parent_srv.auth_token,
            parameters=parameters,
        )

    def delete_request(self, url):
        # We don't return anything for a delete request
        self._make_request(self.parent_srv.session.delete, url, auth_token=self.parent_srv.auth_token)

    def put_request(self, url, xml_request=None, content_type=XML_CONTENT_TYPE, parameters=None):
        return self._make_request(
            self.parent_srv.session.put,
            url,
            content=xml_request,
            auth_token=self.parent_srv.auth_token,
            content_type=content_type,
            parameters=parameters,
        )

    def post_request(self, url, xml_request, content_type=XML_CONTENT_TYPE, parameters=None):
        return self._make_request(
            self.parent_srv.session.post,
            url,
            content=xml_request,
            auth_token=self.parent_srv.auth_token,
            content_type=content_type,
            parameters=parameters,
        )

    def patch_request(self, url, xml_request, content_type=XML_CONTENT_TYPE, parameters=None):
        return self._make_request(
            self.parent_srv.session.patch,
            url,
            content=xml_request,
            auth_token=self.parent_srv.auth_token,
            content_type=content_type,
            parameters=parameters,
        )


E = TypeVar("E", bound="Endpoint")
P = ParamSpec("P")
R = TypeVar("R")


def api(version: str) -> Callable[[Callable[Concatenate[E, P], R]], Callable[Concatenate[E, P], R]]:
    """Annotate the minimum supported version for an endpoint.

    Checks the version on the server object and compares normalized versions.
    It will raise an exception if the server version is > the version specified.

    Args:
        `version` minimum version that supports the endpoint. String.
    Raises:
        EndpointUnavailableError
    Returns:
        None

    Example:
    >>> @api(version="2.3")
    >>> def get(self, req_options=None):
    >>>     ...
    """

    def _decorator(func: Callable[Concatenate[E, P], R]) -> Callable[Concatenate[E, P], R]:
        @wraps(func)
        def wrapper(self: E, *args: P.args, **kwargs: P.kwargs) -> R:
            self.parent_srv.assert_at_least_version(version, self.__class__.__name__)
            return func(self, *args, **kwargs)

        return wrapper

    return _decorator


def parameter_added_in(**params: str) -> Callable[[Callable[Concatenate[E, P], R]], Callable[Concatenate[E, P], R]]:
    """Annotate minimum versions for new parameters or request options on an endpoint.

    The api decorator documents when an endpoint was added, this decorator annotates
    keyword arguments on endpoints that may control functionality added after an endpoint was introduced.

    The REST API will ignore invalid parameters in most cases, so this raises a warning instead of throwing
    an exception.

    Args:
        Key/value pairs of the form `parameter`=`version`. Kwargs.
    Raises:
        UserWarning
    Returns:
        None

    Example:
    >>> @api(version="2.0")
    >>> @parameter_added_in(no_extract='2.5')
    >>> def download(self, workbook_id, filepath=None, extract_only=False):
    >>>     ...
    """

    def _decorator(func: Callable[Concatenate[E, P], R]) -> Callable[Concatenate[E, P], R]:
        @wraps(func)
        def wrapper(self: E, *args: P.args, **kwargs: P.kwargs) -> R:
            import warnings

            server_ver = Version(self.parent_srv.version or "0.0")
            params_to_check = set(params) & set(kwargs)
            for p in params_to_check:
                min_ver = Version(str(params[p]))
                if server_ver < min_ver:
                    error = f"{p!r} not available in {server_ver}, it will be ignored. Added in {min_ver}"
                    warnings.warn(error)
            return func(self, *args, **kwargs)

        return wrapper

    return _decorator


T = TypeVar("T")

_io_types_w = (io.BytesIO, io.BufferedWriter)

FilePath = str | os.PathLike
FileObjectW = io.BufferedWriter | io.BytesIO
PathOrFileW = FilePath | FileObjectW


class DownloadableMixin:
    """Mixin for endpoints whose resources can be downloaded as binary files.

    Provides a single private helper that streams a server response to a file
    path or writable file object, avoiding copy-paste of the identical streaming
    loop in Workbooks, Datasources, and Flows.
    """

    def _download_content(
        self,
        url: str,
        filepath: PathOrFileW | None,
    ) -> PathOrFileW:
        """Stream content at url to filepath and return the resolved path.

        Parameters
        ----------
        url : str
            Fully-qualified URL whose response body should be saved.
        filepath : PathOrFileW | None
            Destination file path or writable file object.  When None the file
            is saved to the current working directory using the server-supplied
            filename from the Content-Disposition header.

        Returns
        -------
        PathOrFileW
            The absolute file path written, or the caller-supplied file object.
        """
        with closing(self.get_request(url, parameters={"stream": True})) as server_response:  # type: ignore[attr-defined]
            m = Message()
            m["Content-Disposition"] = server_response.headers["Content-Disposition"]
            filename = m.get_filename(failobj="")
            if isinstance(filepath, _io_types_w):
                for chunk in server_response.iter_content(1024):  # 1KB
                    filepath.write(chunk)
                return filepath
            else:
                filename = to_filename(os.path.basename(filename))
                download_path = make_download_path(filepath, filename)
                with open(download_path, "wb") as f:
                    for chunk in server_response.iter_content(1024):  # 1KB
                        f.write(chunk)
                return os.path.abspath(download_path)


class QuerysetEndpoint(Endpoint, Generic[T]):
    @api(version="2.0")
    def all(self, *args, page_size: int | None = None, **kwargs) -> QuerySet[T]:
        if args or kwargs:
            raise ValueError(".all method takes no arguments.")
        queryset = QuerySet(self, page_size=page_size)
        return queryset

    @api(version="2.0")
    def filter(self, *_, page_size: int | None = None, **kwargs) -> QuerySet[T]:
        if _:
            raise RuntimeError("Only keyword arguments accepted.")
        queryset = QuerySet(self, page_size=page_size).filter(**kwargs)
        return queryset

    @api(version="2.0")
    def order_by(self, *args, **kwargs) -> QuerySet[T]:
        if kwargs:
            raise ValueError(".order_by does not accept keyword arguments.")
        queryset = QuerySet(self).order_by(*args)
        return queryset

    @api(version="2.0")
    def paginate(self, **kwargs) -> QuerySet[T]:
        queryset = QuerySet(self).paginate(**kwargs)
        return queryset

    @abc.abstractmethod
    def get(self, request_options: RequestOptions | None = None) -> tuple[list[T], PaginationItem]:
        raise NotImplementedError(f".get has not been implemented for {self.__class__.__qualname__}")

    def fields(self: Self, *fields: str) -> QuerySet:
        """
        Add fields to the request options. If no fields are provided, the
        default fields will be used. If fields are provided, the default fields
        will be used in addition to the provided fields.

        Parameters
        ----------
        fields : str
            The fields to include in the request options.

        Returns
        -------
        QuerySet
        """
        queryset = QuerySet(self)
        queryset.request_options.fields |= set(fields) | set(("_default_",))
        return queryset

    def only_fields(self: Self, *fields: str) -> QuerySet:
        """
        Add fields to the request options. If no fields are provided, the
        default fields will be used. If fields are provided, the default fields
        will be replaced by the provided fields.

        Parameters
        ----------
        fields : str
            The fields to include in the request options.

        Returns
        -------
        QuerySet
        """
        queryset = QuerySet(self)
        queryset.request_options.fields |= set(fields)
        return queryset

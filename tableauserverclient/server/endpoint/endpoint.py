import requests
import logging
from packaging.version import Version
from functools import wraps
from xml.etree.ElementTree import ParseError
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

from .exceptions import (
    ServerResponseError,
    InternalServerError,
    NonXMLResponseError,
    EndpointUnavailableError,
)
from ..query import QuerySet
from ... import helpers, get_versions

if TYPE_CHECKING:
    from ..server import Server
    from requests import Response

logger = logging.getLogger("tableau.endpoint")

Success_codes = [200, 201, 202, 204]

XML_CONTENT_TYPE = "text/xml"
JSON_CONTENT_TYPE = "application/json"

CONTENT_TYPE_HEADER = "content-type"
TABLEAU_AUTH_HEADER = "x-tableau-auth"
USER_AGENT_HEADER = "User-Agent"


class Endpoint(object):
    def __init__(self, parent_srv: "Server"):
        self.parent_srv = parent_srv

    @staticmethod
    def _make_common_headers(auth_token, content_type):
        _client_version: Optional[str] = get_versions()["version"]
        headers = {}
        if auth_token is not None:
            headers[TABLEAU_AUTH_HEADER] = auth_token
        if content_type is not None:
            headers[CONTENT_TYPE_HEADER] = content_type
        headers[USER_AGENT_HEADER] = "Tableau Server Client/{}".format(_client_version)
        return headers

    def _make_request(
        self,
        method: Callable[..., "Response"],
        url: str,
        content: Optional[bytes] = None,
        auth_token: Optional[str] = None,
        content_type: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> "Response":
        parameters = parameters or {}
        if "headers" not in parameters:
            parameters["headers"] = {}
        parameters.update(self.parent_srv.http_options)
        parameters["headers"].update(Endpoint._make_common_headers(auth_token, content_type))

        if content is not None:
            parameters["data"] = content

        logger.debug("request {}, url: {}".format(method.__name__, url))
        if content:
            logger.debug("request content: {}".format(helpers.strings.redact_xml(content[:1000])))

        server_response = method(url, **parameters)
        self._check_status(server_response, url)

        loggable_response = self.log_response_safely(server_response)
        logger.debug("Server response from {0}:\n\t{1}".format(url, loggable_response))

        if content_type == "application/xml":
            self.parent_srv._namespace.detect(server_response.content)

        return server_response

    def _check_status(self, server_response, url: str = None):
        if server_response.status_code >= 500:
            raise InternalServerError(server_response, url)
        elif server_response.status_code not in Success_codes:
            try:
                raise ServerResponseError.from_response(server_response.content, self.parent_srv.namespace, url)
            except ParseError:
                # This will happen if we get a non-success HTTP code that doesn't return an xml error object
                # e.g metadata endpoints, 503 pages, totally different servers
                # we convert this to a better exception and pass through the raw response body
                raise NonXMLResponseError(server_response.content)
            except Exception:
                # anything else re-raise here
                raise

    def log_response_safely(self, server_response: requests.Response) -> str:
        # Checking the content type header prevents eager evaluation of streaming requests.
        content_type = server_response.headers.get("Content-Type")

        # Response.content is a property. Calling it will load the entire response into memory. Checking if the
        # content-type is an octet-stream accomplishes the same goal without eagerly loading content.
        # This check is to determine if the response is a text response (xml or otherwise)
        # so that we do not attempt to log bytes and other binary data.
        loggable_response = "Content type {}".format(content_type)
        if content_type == "application/octet-stream":
            loggable_response = "A stream of type {} [Truncated File Contents]".format(content_type)
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


def api(version):
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

    def _decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.parent_srv.assert_at_least_version(version, self.__class__.__name__)
            return func(self, *args, **kwargs)

        return wrapper

    return _decorator


def parameter_added_in(**params):
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

    def _decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            import warnings

            server_ver = Version(self.parent_srv.version or "0.0")
            params_to_check = set(params) & set(kwargs)
            for p in params_to_check:
                min_ver = Version(str(params[p]))
                if server_ver < min_ver:
                    error = "{!r} not available in {}, it will be ignored. Added in {}".format(p, server_ver, min_ver)
                    warnings.warn(error)
            return func(self, *args, **kwargs)

        return wrapper

    return _decorator


class QuerysetEndpoint(Endpoint):
    @api(version="2.0")
    def all(self, *args, **kwargs):
        queryset = QuerySet(self)
        return queryset

    @api(version="2.0")
    def filter(self, *_, **kwargs):
        if _:
            raise RuntimeError("Only keyword arguments accepted.")
        queryset = QuerySet(self).filter(**kwargs)
        return queryset

    @api(version="2.0")
    def order_by(self, *args, **kwargs):
        queryset = QuerySet(self).order_by(*args)
        return queryset

    @api(version="2.0")
    def paginate(self, **kwargs):
        queryset = QuerySet(self).paginate(**kwargs)
        return queryset

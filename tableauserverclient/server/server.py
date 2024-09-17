from tableauserverclient.helpers.logging import logger

import requests
import urllib3

from defusedxml.ElementTree import fromstring, ParseError
from packaging.version import Version
from tableauserverclient.server.endpoint import (
    Sites,
    Views,
    Users,
    Groups,
    Workbooks,
    Datasources,
    Projects,
    Auth,
    Schedules,
    ServerInfo,
    Tasks,
    Subscriptions,
    Jobs,
    Metadata,
    Databases,
    Tables,
    Flows,
    FlowTasks,
    Webhooks,
    DataAccelerationReport,
    Favorites,
    DataAlerts,
    Fileuploads,
    FlowRuns,
    Metrics,
    Endpoint,
    CustomViews,
    LinkedTasks,
    GroupSets,
    Tags,
    VirtualConnections,
)
from tableauserverclient.server.exceptions import (
    ServerInfoEndpointNotFoundError,
    EndpointUnavailableError,
)
from tableauserverclient.server.endpoint.exceptions import NotSignedInError
from tableauserverclient.namespace import Namespace


_PRODUCT_TO_REST_VERSION = {
    "10.0": "2.3",
    "9.3": "2.2",
    "9.2": "2.1",
    "9.1": "2.0",
    "9.0": "2.0",
}

minimum_supported_server_version = "2.3"
default_server_version = "2.4"  # first version that dropped the legacy auth endpoint


class Server(object):
    class PublishMode:
        Append = "Append"
        Overwrite = "Overwrite"
        CreateNew = "CreateNew"

    def __init__(self, server_address, use_server_version=False, http_options=None, session_factory=None):
        self._auth_token = None
        self._site_id = None
        self._user_id = None

        # TODO: this needs to change to default to https, but without breaking existing code
        if not server_address.startswith("http://") and not server_address.startswith("https://"):
            server_address = "http://" + server_address

        self._server_address: str = server_address
        self._session_factory = session_factory or requests.session

        self.auth = Auth(self)
        self.views = Views(self)
        self.users = Users(self)
        self.sites = Sites(self)
        self.groups = Groups(self)
        self.jobs = Jobs(self)
        self.workbooks = Workbooks(self)
        self.datasources = Datasources(self)
        self.favorites = Favorites(self)
        self.flows = Flows(self)
        self.flow_tasks = FlowTasks(self)
        self.projects = Projects(self)
        self.schedules = Schedules(self)
        self.server_info = ServerInfo(self)
        self.tasks = Tasks(self)
        self.subscriptions = Subscriptions(self)
        self.metadata = Metadata(self)
        self.databases = Databases(self)
        self.tables = Tables(self)
        self.webhooks = Webhooks(self)
        self.data_acceleration_report = DataAccelerationReport(self)
        self.data_alerts = DataAlerts(self)
        self.fileuploads = Fileuploads(self)
        self._namespace = Namespace()
        self.flow_runs = FlowRuns(self)
        self.metrics = Metrics(self)
        self.custom_views = CustomViews(self)
        self.linked_tasks = LinkedTasks(self)
        self.group_sets = GroupSets(self)
        self.tags = Tags(self)
        self.virtual_connections = VirtualConnections(self)

        self._session = self._session_factory()
        self._http_options = dict()  # must set this before making a server call
        if http_options:
            self.add_http_options(http_options)

        self.validate_connection_settings()  # does not make an actual outgoing request

        self.version = default_server_version
        if use_server_version:
            self.use_server_version()  # this makes a server call

    def validate_connection_settings(self):
        try:
            params = Endpoint(self).set_parameters(self._http_options, None, None, None, None)
            Endpoint.set_user_agent(params)
            if not self._server_address.startswith("http://") and not self._server_address.startswith("https://"):
                self._server_address = "http://" + self._server_address
            self._session.prepare_request(requests.Request("GET", url=self._server_address, params=self._http_options))
        except Exception as req_ex:
            raise ValueError("Server connection settings not valid", req_ex)

    def __repr__(self):
        return "<TableauServerClient [Connection: {}, {}]>".format(self.baseurl, self.server_info.serverInfo)

    def add_http_options(self, options_dict: dict):
        try:
            self._http_options.update(options_dict)
            if "verify" in options_dict.keys() and self._http_options.get("verify") is False:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                # would be nice if you could turn them back on
        except Exception as be:
            # expected errors on invalid input:
            # 'set' object has no attribute 'keys', 'list' object has no attribute 'keys'
            # TypeError: cannot convert dictionary update sequence element #0 to a sequence (input is a tuple)
            raise ValueError("Invalid http options given: {}".format(options_dict))

    def clear_http_options(self):
        self._http_options = dict()

    def _clear_auth(self):
        self._site_id = None
        self._user_id = None
        self._auth_token = None
        self._session = self._session_factory()

    def _set_auth(self, site_id, user_id, auth_token):
        self._site_id = site_id
        self._user_id = user_id
        self._auth_token = auth_token

    def _get_legacy_version(self):
        # the serverInfo call was introduced in 2.4, earlier than that we have this different call
        response = self._session.get(self.server_address + "/auth?format=xml")
        try:
            info_xml = fromstring(response.content)
        except ParseError as parseError:
            logger.info(parseError)
            logger.info("Could not read server version info. The server may not be running or configured.")
            return self.version
        prod_version = info_xml.find(".//product_version").text
        version = _PRODUCT_TO_REST_VERSION.get(prod_version, minimum_supported_server_version)
        return version

    def _determine_highest_version(self):
        try:
            old_version = self.version
            version = self.server_info.get().rest_api_version
        except ServerInfoEndpointNotFoundError as e:
            logger.info("Could not get version info from server: {}{}".format(e.__class__, e))
            version = self._get_legacy_version()
        except EndpointUnavailableError as e:
            logger.info("Could not get version info from server: {}{}".format(e.__class__, e))
            version = self._get_legacy_version()
        except Exception as e:
            logger.info("Could not get version info from server: {}{}".format(e.__class__, e))
            version = None
        logger.info("versions: {}, {}".format(version, old_version))
        return version or old_version

    def use_server_version(self):
        self.version = self._determine_highest_version()

    def use_highest_version(self):
        self.use_server_version()
        logger.info("use use_server_version instead", DeprecationWarning)

    def check_at_least_version(self, target: str):
        server_version = Version(self.version or "2.4")
        target_version = Version(target)
        return server_version >= target_version

    def assert_at_least_version(self, comparison: str, reason: str):
        if not self.check_at_least_version(comparison):
            error = "{} is not available in API version {}. Requires {}".format(reason, self.version, comparison)
            raise EndpointUnavailableError(error)

    @property
    def baseurl(self):
        return "{0}/api/{1}".format(self._server_address, str(self.version))

    @property
    def namespace(self):
        return self._namespace()

    @property
    def auth_token(self):
        if self._auth_token is None:
            error = "Missing authentication token. You must sign in first."
            raise NotSignedInError(error)
        return self._auth_token

    @property
    def site_id(self):
        if self._site_id is None:
            error = "Missing site ID. You must sign in first."
            raise NotSignedInError(error)
        return self._site_id

    @property
    def user_id(self):
        if self._user_id is None:
            error = "Missing user ID. You must sign in first."
            raise NotSignedInError(error)
        return self._user_id

    @property
    def server_address(self):
        return self._server_address

    @property
    def http_options(self):
        return self._http_options

    @property
    def session(self):
        return self._session

    def is_signed_in(self):
        return self._auth_token is not None

from .exceptions import NotSignedInError
from .endpoint import Sites, Views, Users, Groups, Workbooks, Datasources, Projects, Auth, Schedules, ServerInfo
from . import RequestOptions

import requests


class Pager(object):
    """ This class returns a generator that will iterate over all of the results.

    server is the server object that will be used when calling the callback.  It will be passed
    to the callback on each iteration

    Callback is expected to take a server object and a request options and return two values, an array of results,
    and the pagination item from the current call.  This will be used to build subsequent requests.
    """

    def __init__(self, fetcher, opts=None):
        self._fetcher = fetcher.get
        self._options = opts

    def __call__(self):
        current_item_list, last_pagination_item = self._fetcher(self._options)
        count = 0

        while count < last_pagination_item.total_available:
            if len(current_item_list) == 0:
                current_item_list, last_pagination_item = self._load_next_page(current_item_list, last_pagination_item)

            yield current_item_list.pop(0)
            count += 1

    def __iter__(self):
        return self()

    def _load_next_page(self, current_item_list, last_pagination_item):
        next_page = last_pagination_item.page_number + 1
        opts = RequestOptions(pagenumber=next_page, pagesize=last_pagination_item.page_size)
        if self._options is not None:
            opts.sort, opts.filter = self._options.sort, self._options.filter
        current_item_list, last_pagination_item = self._fetcher(opts)
        return current_item_list, last_pagination_item


class Server(object):
    class PublishMode:
        Append = 'Append'
        Overwrite = 'Overwrite'
        CreateNew = 'CreateNew'

    def __init__(self, server_address):
        self._server_address = server_address
        self._auth_token = None
        self._site_id = None
        self._user_id = None
        self._session = requests.Session()
        self._http_options = dict()

        self.version = 2.3
        self.auth = Auth(self)
        self.views = Views(self)
        self.users = Users(self)
        self.sites = Sites(self)
        self.groups = Groups(self)
        self.workbooks = Workbooks(self)
        self.datasources = Datasources(self)
        self.projects = Projects(self)
        self.schedules = Schedules(self)
        self.server_info = ServerInfo(self)

    def add_http_options(self, options_dict):
        self._http_options.update(options_dict)

    def clear_http_options(self):
        self._http_options = dict()

    def _clear_auth(self):
        self._site_id = None
        self._user_id = None
        self._auth_token = None
        self._session = requests.Session()

    def _set_auth(self, site_id, user_id, auth_token):
        self._site_id = site_id
        self._user_id = user_id
        self._auth_token = auth_token

    @property
    def baseurl(self):
        return "{0}/api/{1}".format(self._server_address, str(self.version))

    @property
    def auth_token(self):
        if self._auth_token is None:
            error = 'Missing authentication token. You must sign in first.'
            raise NotSignedInError(error)
        return self._auth_token

    @property
    def site_id(self):
        if self._site_id is None:
            error = 'Missing site ID. You must sign in first.'
            raise NotSignedInError(error)
        return self._site_id

    @property
    def user_id(self):
        if self._user_id is None:
            error = 'Missing user ID. You must sign in first.'
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

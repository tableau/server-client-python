from typing import Optional
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api
from tableauserverclient.server.request_options import RequestOptions

class LinkedTasks(QuerysetEndpoint):
    def __init__(self, parent_srv):
        super().__init__(parent_srv)
        self._parent_srv = parent_srv

    @property
    def baseurl(self):
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/tasks/linked"

    @api(version="3.15")
    def get(self, req_options: Optional[RequestOptions] = None):
        ...


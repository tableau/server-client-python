from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, WorkbookItem, ViewItem, ProjectItem, DatasourceItem
from ..pager import Pager
import logging
import copy

logger = logging.getLogger('tableau.endpoint.favorites')


class Favorites(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/favorites".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Gets all users
    @api(version="2.5")
    def get(self, user_item, req_options=None):
        logger.info('Querying all favorites for user {0}'.format(user_item.name))
        url = '{0}/{1}'.format(self.baseurl, user_item.id)
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_favorite_items = UserItem.from_response(server_response.content, self.parent_srv.namespace)
        parsed_response = ET.fromstring(server_response)
        favorites = []
        for workbook in parsed_response.findall('.//t:favorite/t:workbook', self.parent_srv.namespace):
            i = WorkbookItem('')
            i._set_values(*i._parse_element(workbook, self.parent_srv.namespace))
            if i:
                favorites.append(i)
        for view in parsed_response.findall('.//t:favorite[t:view]', self.parent_srv.namespace):
            i = ViewItem()
            i.from_xml_element(view, self.parent_srv.namespace)
            if i:
                favorites.append(i)
        for datasource in parsed_response.findall('.//t:favorite/t:datasource', self.parent_srv.namespace):
            i = DatasourceItem('')
            i._set_values(*i._parse_element(datasource, self.parent_srv.namespace))
            if i:
                favorites.append(i)
        for project in parsed_response.findall('.//t:favorite/t:project', self.parent_srv.namespace):
            i = ProjectItem('p')
            i._set_values(*i._parse_element(project))
            if i:
                favorites.append(i)

        return favorites

from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, projectItem, ViewItem, ProjectItem, DatasourceItem
from ..pager import Pager
import xml.etree.ElementTree as ET
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

    @api(version="1.0")
    def add_favorite_workbook(self, user_item, workbook_item):
        url = '{0}/{1}'.format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_workbook_req(workbook_item.id, workbook_item.name)
        server_response = self.put_request(url, add_req)
        logger.info('Favorited {0} for user (ID: {1})'.format(workbook_item.name, user_item.id))

    @api(version="1.0")
    def add_favorite_view(self, user_item, view_item):
        url = '{0}/{1}'.format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_view_req(view_item.id, view_item.name)
        server_response = self.put_request(url, add_req)
        logger.info('Favorited {0} for user (ID: {1})'.format(view_item.name, user_item.id))

    @api(version="2.3")
    def add_favorite_datasource(self, user_item, datasource_item):
        url = '{0}/{1}'.format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_datasource_req(datasource_item.id, datasource_item.name)
        server_response = self.put_request(url, add_req)
        logger.info('Favorited {0} for user (ID: {1})'.format(datasource_item.name, user_item.id))

    @api(version="3.1")
    def add_favorite_project(self, user_item, project_item):
        url = '{0}/{1}'.format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_project_req(project_item.id, project_item.name)
        server_response = self.put_request(url, add_req)
        logger.info('Favorited {0} for user (ID: {1})'.format(project_item.name, user_item.id))

import unittest
import os
import requests_mock
import xml.etree.ElementTree as ET
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.server.endpoint.exceptions import InternalServerError
from tableauserverclient.server.request_factory import RequestFactory
from ._utils import read_xml_asset, read_xml_assets, asset

GET_FAVORITES_XML = 'favorites_get.xml'
ADD_FAVORITE_WORKBOOK_XML = 'favorites_add_workbook.xml'
ADD_FAVORITE_VIEW_XML = 'favorites_add_view.xml'
ADD_FAVORITE_DATASOURCE_XML = 'favorites_add_datasource.xml'
ADD_FAVORITE_PROJECT_XML = 'favorites_add_project.xml'


class FavoritesTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.server.version = '2.5'

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.favorites.baseurl
        self.user = TSC.UserItem('alice', TSC.UserItem.Roles.Viewer)
        self.user._id = 'dd2239f6-ddf1-4107-981a-4cf94e415794'

    def test_get(self):
        response_xml = read_xml_asset(GET_FAVORITES_XML)
        with requests_mock.mock() as m:
            m.get('{0}/{1}'.format(self.baseurl, self.user.id),
                  text=response_xml)
            self.server.favorites.get(self.user)
        self.assertIsNotNone(self.user._favorites)
        self.assertEqual(len(self.user.favorites['workbooks']), 1)
        self.assertEqual(len(self.user.favorites['views']), 1)
        self.assertEqual(len(self.user.favorites['projects']), 1)
        self.assertEqual(len(self.user.favorites['datasources']), 1)

        workbook = self.user.favorites['workbooks'][0]
        view = self.user.favorites['views'][0]
        datasource = self.user.favorites['datasources'][0]
        project = self.user.favorites['projects'][0]

        self.assertEqual(workbook.id, '6d13b0ca-043d-4d42-8c9d-3f3313ea3a00')
        self.assertEqual(view.id, 'd79634e1-6063-4ec9-95ff-50acbf609ff5')
        self.assertEqual(datasource.id, 'e76a1461-3b1d-4588-bf1b-17551a879ad9')
        self.assertEqual(project.id, '1d0304cd-3796-429f-b815-7258370b9b74')

    def test_add_favorite_workbook(self):
        response_xml = read_xml_asset(ADD_FAVORITE_WORKBOOK_XML)
        workbook = TSC.WorkbookItem('')
        workbook._id = '6d13b0ca-043d-4d42-8c9d-3f3313ea3a00'
        workbook.name = 'Superstore'
        with requests_mock.mock() as m:
            m.put('{0}/{1}'.format(self.baseurl, self.user.id),
                  text=response_xml)
            self.server.favorites.add_favorite_workbook(self.user, workbook)

    def test_add_favorite_view(self):
        response_xml = read_xml_asset(ADD_FAVORITE_VIEW_XML)
        view = TSC.ViewItem()
        view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'
        view._name = 'ENDANGERED SAFARI'
        with requests_mock.mock() as m:
            m.put('{0}/{1}'.format(self.baseurl, self.user.id),
                  text=response_xml)
            self.server.favorites.add_favorite_view(self.user, view)

    def test_add_favorite_datasource(self):
        response_xml = read_xml_asset(ADD_FAVORITE_DATASOURCE_XML)
        datasource = TSC.DatasourceItem('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')
        datasource._id = 'e76a1461-3b1d-4588-bf1b-17551a879ad9'
        datasource.name = 'SampleDS'
        with requests_mock.mock() as m:
            m.put('{0}/{1}'.format(self.baseurl, self.user.id),
                  text=response_xml)
            self.server.favorites.add_favorite_datasource(self.user, datasource)

    def test_add_favorite_project(self):
        self.server.version = '3.1'
        baseurl = self.server.favorites.baseurl
        response_xml = read_xml_asset(ADD_FAVORITE_PROJECT_XML)
        project = TSC.ProjectItem('Tableau')
        project._id = '1d0304cd-3796-429f-b815-7258370b9b74'
        with requests_mock.mock() as m:
            m.put('{0}/{1}'.format(baseurl, self.user.id),
                  text=response_xml)
            self.server.favorites.add_favorite_project(self.user, project)

    def test_delete_favorite_workbook(self):
        workbook = TSC.WorkbookItem('')
        workbook._id = '6d13b0ca-043d-4d42-8c9d-3f3313ea3a00'
        workbook.name = 'Superstore'
        with requests_mock.mock() as m:
            m.delete('{0}/{1}/workbooks/{2}'.format(self.baseurl, self.user.id,
                     workbook.id))
            self.server.favorites.delete_favorite_workbook(self.user, workbook)

    def test_delete_favorite_view(self):
        view = TSC.ViewItem()
        view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'
        view._name = 'ENDANGERED SAFARI'
        with requests_mock.mock() as m:
            m.delete('{0}/{1}/views/{2}'.format(self.baseurl, self.user.id,
                     view.id))
            self.server.favorites.delete_favorite_view(self.user, view)

    def test_delete_favorite_datasource(self):
        datasource = TSC.DatasourceItem('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')
        datasource._id = 'e76a1461-3b1d-4588-bf1b-17551a879ad9'
        datasource.name = 'SampleDS'
        with requests_mock.mock() as m:
            m.delete('{0}/{1}/datasources/{2}'.format(self.baseurl, self.user.id,
                     datasource.id))
            self.server.favorites.delete_favorite_datasource(self.user, datasource)

    def test_delete_favorite_project(self):
        self.server.version = '3.1'
        baseurl = self.server.favorites.baseurl
        project = TSC.ProjectItem('Tableau')
        project._id = '1d0304cd-3796-429f-b815-7258370b9b74'
        with requests_mock.mock() as m:
            m.delete('{0}/{1}/projects/{2}'.format(baseurl, self.user.id,
                     project.id))
            self.server.favorites.delete_favorite_project(self.user, project)

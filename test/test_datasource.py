import unittest
import os
import requests_mock
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

ADD_TAGS_XML = os.path.join(TEST_ASSET_DIR, 'datasource_add_tags.xml')
GET_XML = os.path.join(TEST_ASSET_DIR, 'datasource_get.xml')
GET_EMPTY_XML = os.path.join(TEST_ASSET_DIR, 'datasource_get_empty.xml')
GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, 'datasource_get_by_id.xml')
PUBLISH_XML = os.path.join(TEST_ASSET_DIR, 'datasource_publish.xml')
UPDATE_XML = os.path.join(TEST_ASSET_DIR, 'datasource_update.xml')


class DatasourceTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.datasources.baseurl

    def test_get(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_datasources, pagination_item = self.server.datasources.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual('e76a1461-3b1d-4588-bf1b-17551a879ad9', all_datasources[0].id)
        self.assertEqual('dataengine', all_datasources[0].datasource_type)
        self.assertEqual('SampleDS', all_datasources[0].content_url)
        self.assertEqual('2016-08-11T21:22:40Z', format_datetime(all_datasources[0].created_at))
        self.assertEqual('2016-08-11T21:34:17Z', format_datetime(all_datasources[0].updated_at))
        self.assertEqual('default', all_datasources[0].project_name)
        self.assertEqual('SampleDS', all_datasources[0].name)
        self.assertEqual('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', all_datasources[0].project_id)
        self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', all_datasources[0].owner_id)

        self.assertEqual('9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', all_datasources[1].id)
        self.assertEqual('dataengine', all_datasources[1].datasource_type)
        self.assertEqual('Sampledatasource', all_datasources[1].content_url)
        self.assertEqual('2016-08-04T21:31:55Z', format_datetime(all_datasources[1].created_at))
        self.assertEqual('2016-08-04T21:31:55Z', format_datetime(all_datasources[1].updated_at))
        self.assertEqual('default', all_datasources[1].project_name)
        self.assertEqual('Sample datasource', all_datasources[1].name)
        self.assertEqual('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', all_datasources[1].project_id)
        self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', all_datasources[1].owner_id)
        self.assertEqual(set(['world', 'indicators', 'sample']), all_datasources[1].tags)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.datasources.get)

    def test_get_empty(self):
        with open(GET_EMPTY_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_datasources, pagination_item = self.server.datasources.get()

        self.assertEqual(0, pagination_item.total_available)
        self.assertEqual([], all_datasources)

    def test_get_by_id(self):
        with open(GET_BY_ID_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', text=response_xml)
            single_datasource = self.server.datasources.get_by_id('9dbd2263-16b5-46e1-9c43-a76bb8ab65fb')

        self.assertEqual('9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', single_datasource.id)
        self.assertEqual('dataengine', single_datasource.datasource_type)
        self.assertEqual('Sampledatasource', single_datasource.content_url)
        self.assertEqual('2016-08-04T21:31:55Z', format_datetime(single_datasource.created_at))
        self.assertEqual('2016-08-04T21:31:55Z', format_datetime(single_datasource.updated_at))
        self.assertEqual('default', single_datasource.project_name)
        self.assertEqual('Sample datasource', single_datasource.name)
        self.assertEqual('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', single_datasource.project_id)
        self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', single_datasource.owner_id)
        self.assertEqual(set(['world', 'indicators', 'sample']), single_datasource.tags)

    def test_update(self):
        with open(UPDATE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', text=response_xml)
            single_datasource = TSC.DatasourceItem('test', '1d0304cd-3796-429f-b815-7258370b9b74')
            single_datasource.owner_id = 'dd2239f6-ddf1-4107-981a-4cf94e415794'
            single_datasource._id = '9dbd2263-16b5-46e1-9c43-a76bb8ab65fb'
            single_datasource.certified = True
            single_datasource.certification_note = "Warning, here be dragons."
            single_datasource = self.server.datasources.update(single_datasource)

        self.assertEqual('9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', single_datasource.id)
        self.assertEqual('1d0304cd-3796-429f-b815-7258370b9b74', single_datasource.project_id)
        self.assertEqual('dd2239f6-ddf1-4107-981a-4cf94e415794', single_datasource.owner_id)
        self.assertEqual(True, single_datasource.certified)
        self.assertEqual("Warning, here be dragons.", single_datasource.certification_note)

    def test_update_copy_fields(self):
        with open(UPDATE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', text=response_xml)
            single_datasource = TSC.DatasourceItem('test', '1d0304cd-3796-429f-b815-7258370b9b74')
            single_datasource._id = '9dbd2263-16b5-46e1-9c43-a76bb8ab65fb'
            single_datasource._project_name = 'Tester'
            updated_datasource = self.server.datasources.update(single_datasource)

        self.assertEqual(single_datasource.tags, updated_datasource.tags)
        self.assertEqual(single_datasource._project_name, updated_datasource._project_name)

    def test_update_tags(self):
        with open(ADD_TAGS_XML, 'rb') as f:
            add_tags_xml = f.read().decode('utf-8')
        with open(UPDATE_XML, 'rb') as f:
            update_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags', text=add_tags_xml)
            m.delete(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags/b', status_code=204)
            m.delete(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags/d', status_code=204)
            m.put(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', text=update_xml)
            single_datasource = TSC.DatasourceItem('1d0304cd-3796-429f-b815-7258370b9b74')
            single_datasource._id = '9dbd2263-16b5-46e1-9c43-a76bb8ab65fb'
            single_datasource._initial_tags.update(['a', 'b', 'c', 'd'])
            single_datasource.tags.update(['a', 'c', 'e'])
            updated_datasource = self.server.datasources.update(single_datasource)

        self.assertEqual(single_datasource.tags, updated_datasource.tags)
        self.assertEqual(single_datasource._initial_tags, updated_datasource._initial_tags)

    def test_publish(self):
        with open(PUBLISH_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            new_datasource = TSC.DatasourceItem('SampleDS', 'ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')
            new_datasource = self.server.datasources.publish(new_datasource,
                                                             os.path.join(TEST_ASSET_DIR, 'SampleDS.tds'),
                                                             mode=self.server.PublishMode.CreateNew)

        self.assertEqual('e76a1461-3b1d-4588-bf1b-17551a879ad9', new_datasource.id)
        self.assertEqual('SampleDS', new_datasource.name)
        self.assertEqual('SampleDS', new_datasource.content_url)
        self.assertEqual('dataengine', new_datasource.datasource_type)
        self.assertEqual('2016-08-11T21:22:40Z', format_datetime(new_datasource.created_at))
        self.assertEqual('2016-08-17T23:37:08Z', format_datetime(new_datasource.updated_at))
        self.assertEqual('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', new_datasource.project_id)
        self.assertEqual('default', new_datasource.project_name)
        self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', new_datasource.owner_id)

    def test_delete(self):
        with requests_mock.mock() as m:
            m.delete(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', status_code=204)
            self.server.datasources.delete('9dbd2263-16b5-46e1-9c43-a76bb8ab65fb')

    def test_download(self):
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content',
                  headers={'Content-Disposition': 'name="tableau_datasource"; filename="Sample datasource.tds"'})
            file_path = self.server.datasources.download('9dbd2263-16b5-46e1-9c43-a76bb8ab65fb')
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_download_sanitizes_name(self):
        filename = "Name,With,Commas.tds"
        disposition = 'name="tableau_workbook"; filename="{}"'.format(filename)
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/1f951daf-4061-451a-9df1-69a8062664f2/content',
                  headers={'Content-Disposition': disposition})
            file_path = self.server.datasources.download('1f951daf-4061-451a-9df1-69a8062664f2')
            self.assertEqual(os.path.basename(file_path), "NameWithCommas.tds")
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_download_extract_only(self):
        # Pretend we're 2.5 for 'extract_only'
        self.server.version = "2.5"
        self.baseurl = self.server.datasources.baseurl

        with requests_mock.mock() as m:
            m.get(self.baseurl + '/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content?includeExtract=False',
                  headers={'Content-Disposition': 'name="tableau_datasource"; filename="Sample datasource.tds"'},
                  complete_qs=True)
            file_path = self.server.datasources.download('9dbd2263-16b5-46e1-9c43-a76bb8ab65fb', include_extract=False)
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_update_missing_id(self):
        single_datasource = TSC.DatasourceItem('test', 'ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.datasources.update, single_datasource)

    def test_publish_missing_path(self):
        new_datasource = TSC.DatasourceItem('test', 'ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')
        self.assertRaises(IOError, self.server.datasources.publish, new_datasource,
                          '', self.server.PublishMode.CreateNew)

    def test_publish_missing_mode(self):
        new_datasource = TSC.DatasourceItem('test', 'ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')
        self.assertRaises(ValueError, self.server.datasources.publish, new_datasource,
                          os.path.join(TEST_ASSET_DIR, 'SampleDS.tds'), None)

    def test_publish_invalid_file_type(self):
        new_datasource = TSC.DatasourceItem('test', 'ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')
        self.assertRaises(ValueError, self.server.datasources.publish, new_datasource,
                          os.path.join(TEST_ASSET_DIR, 'SampleWB.twbx'), self.server.PublishMode.Append)

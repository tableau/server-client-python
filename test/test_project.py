import unittest
import os
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

GET_XML = os.path.join(TEST_ASSET_DIR, 'project_get.xml')
UPDATE_XML = os.path.join(TEST_ASSET_DIR, 'project_update.xml')
CREATE_XML = os.path.join(TEST_ASSET_DIR, 'project_create.xml')


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.projects.baseurl

    def test_get(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_projects, pagination_item = self.server.projects.get()

        self.assertEqual(3, pagination_item.total_available)
        self.assertEqual('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', all_projects[0].id)
        self.assertEqual('default', all_projects[0].name)
        self.assertEqual('The default project that was automatically created by Tableau.',
                         all_projects[0].description)
        self.assertEqual('ManagedByOwner', all_projects[0].content_permissions)
        self.assertEqual(None, all_projects[0].parent_id)

        self.assertEqual('1d0304cd-3796-429f-b815-7258370b9b74', all_projects[1].id)
        self.assertEqual('Tableau', all_projects[1].name)
        self.assertEqual('ManagedByOwner', all_projects[1].content_permissions)
        self.assertEqual(None, all_projects[1].parent_id)

        self.assertEqual('4cc52973-5e3a-4d1f-a4fb-5b5f73796edf', all_projects[2].id)
        self.assertEqual('Tableau > Child 1', all_projects[2].name)
        self.assertEqual('ManagedByOwner', all_projects[2].content_permissions)
        self.assertEqual('1d0304cd-3796-429f-b815-7258370b9b74', all_projects[2].parent_id)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.projects.get)

    def test_delete(self):
        with requests_mock.mock() as m:
            m.delete(self.baseurl + '/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', status_code=204)
            self.server.projects.delete('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')

    def test_delete_missing_id(self):
        self.assertRaises(ValueError, self.server.projects.delete, '')

    def test_update(self):
        with open(UPDATE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/1d0304cd-3796-429f-b815-7258370b9b74', text=response_xml)
            single_project = TSC.ProjectItem(name='Test Project',
                                             content_permissions='LockedToProject',
                                             description='Project created for testing',
                                             parent_id='9a8f2265-70f3-4494-96c5-e5949d7a1120')
            single_project._id = '1d0304cd-3796-429f-b815-7258370b9b74'
            single_project = self.server.projects.update(single_project)

        self.assertEqual('1d0304cd-3796-429f-b815-7258370b9b74', single_project.id)
        self.assertEqual('Test Project', single_project.name)
        self.assertEqual('Project created for testing', single_project.description)
        self.assertEqual('LockedToProject', single_project.content_permissions)
        self.assertEqual('9a8f2265-70f3-4494-96c5-e5949d7a1120', single_project.parent_id)

    def test_update_missing_id(self):
        single_project = TSC.ProjectItem('test')
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.projects.update, single_project)

    def test_create(self):
        with open(CREATE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            new_project = TSC.ProjectItem(name='Test Project', description='Project created for testing')
            new_project.content_permissions = 'ManagedByOwner'
            new_project.parent_id = '9a8f2265-70f3-4494-96c5-e5949d7a1120'
            new_project = self.server.projects.create(new_project)

        self.assertEqual('ccbea03f-77c4-4209-8774-f67bc59c3cef', new_project.id)
        self.assertEqual('Test Project', new_project.name)
        self.assertEqual('Project created for testing', new_project.description)
        self.assertEqual('ManagedByOwner', new_project.content_permissions)
        self.assertEqual('9a8f2265-70f3-4494-96c5-e5949d7a1120', new_project.parent_id)

    def test_create_missing_name(self):
        self.assertRaises(ValueError, TSC.ProjectItem, '')

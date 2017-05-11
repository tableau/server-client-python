import os
import time
import unittest

import tableauserverclient as TSC


class SmokeTest(unittest.TestCase):

    def setUp(self):
        self.username = os.environ.get('TABLEAU_USERNAME', None)
        self.server = os.environ.get('TABLEAU_SERVER', None)
        self.password = os.environ.get('TABLEAU_PASSWORD', None)
        self.site_id = os.environ.get('TABLEAU_SITE_ID', '')

        if not (self.username and self.server and self.password):
            raise unittest.SkipTest("Environment variables must be set when run from inside UnitTest")


class ReadOnlySmokeTests(SmokeTest):

    def test_sign_in_sign_out(self):

        authz = TSC.TableauAuth(self.username, self.password)
        server = TSC.Server(self.server)

        server.auth.sign_in(authz)
        server.auth.sign_out()

    def test_get_calls(self):

        authz = TSC.TableauAuth(self.username, self.password)
        server = TSC.Server(self.server)

        server.auth.sign_in(authz)

        for w in TSC.Pager(server.workbooks):
            print(w.name)

        for u in TSC.Pager(server.users):
            print(u.name)

        for p in TSC.Pager(server.projects):
            print(p.name)

        for h in TSC.Pager(server.schedules):
            print(h.name)

        for d in TSC.Pager(server.datasources):
            print(d.name)

        for v in TSC.Pager(server.views):
            print(v.name)

        for s in TSC.Pager(server.sites):
            print(s.name)

        server.auth.sign_out()


class ReadWriteSmokeTests(SmokeTest):

    def test_provision_site(self):
        import functools

        authz = TSC.TableauAuth(self.username, self.password)
        server1 = TSC.Server(self.server)
        server1.auth.sign_in(authz)

        # Create the site
        print("Creating test site...")
        new_site = TSC.SiteItem(name='SMOKE_TEST_SITE', content_url='sts')
        try:
            created_site = server1.sites.create(new_site)
        except TSC.server.endpoint.exceptions.ServerResponseError:
            print("Site already existed. Deleting and recreating...")
            delete_me = next(s for s in TSC.Pager(server1.sites) if s.name == 'SMOKE_TEST_SITE')

            authz2 = TSC.TableauAuth(self.username, self.password, site_id='sts')
            server2 = TSC.Server(self.server)
            server2.auth.sign_in(authz2)
            server2.sites.delete(delete_me.id)
            server2.auth.sign_out()

            created_site = server1.sites.create(new_site)

        # Sign in to the new site
        print("Sign in to test site...")
        authz2 = TSC.TableauAuth(self.username, self.password, site_id='sts')
        server2 = TSC.Server(self.server)
        server2.auth.sign_in(authz2)

        # Add users and verify
        print("Creaing test users...")
        user_item = functools.partial(TSC.UserItem, site_role='Interactor')
        users_to_create = list(user_item(name="user{}".format(i)) for i in range(100))

        for user in users_to_create:
            server2.users.add(user)

        queried_users = list(u.name for u in TSC.Pager(server2.users) if u.name.startswith('user'))

        self.assertTrue(len(users_to_create) == len(queried_users))
        self.assertIn('user1', queried_users)
        self.assertIn('user95', queried_users)

        # Create projects and verify
        print("Creating test project...")
        new_project = TSC.ProjectItem(name='America')
        server2.projects.create(new_project)
        # It finally happened, sleep little one, sleep.
        time.sleep(2)
        found_project = next(p for p in TSC.Pager(server2.projects) if p.name == 'America')
        self.assertTrue(found_project.name == new_project.name)

        print("Publishing test workbook...")
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        twbx = os.path.join(parent_dir, 'test', 'assets', 'SampleWB.twbx')
        wb_item = TSC.WorkbookItem(found_project.id, 'SMOKE_TEST_WB')
        new_wb = server2.workbooks.publish(wb_item, twbx, 'Overwrite')

        self.assertTrue(wb_item.name == new_wb.name)

        # Sweet dreams my little solr
        time.sleep(2)
        found = next((w for w in TSC.Pager(server2.workbooks) if w.name == 'SMOKE_TEST_WB'), None)
        self.assertIsNotNone(found)

        # Check the views
        print("Populating views from test workbook...")
        server2.workbooks.populate_views(new_wb)
        view_names = [v.name for v in new_wb.views]
        self.assertAlmostEqual(len(view_names), 6)
        self.assertIn('Interest rates', view_names)

        # Cleanup
        print("Deleting test site...")
        server2.sites.delete(created_site.id)
        print("Signing out...")
        server2.auth.sign_out()
        server1.auth.sign_out()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Run basic smoke tests against a live Tableau Server instance')
    parser.add_argument('--server', '-s', default=None, help='Server address')
    parser.add_argument('--site-id', '-si', default=None, help='Site to use for ReadOnlySmokeTests')
    parser.add_argument('--username', '-u', default=None, help='Username. Must be sysadmin for ReadWriteSmokeTests')
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()

    # This could probably be made smarter, but after trying too hard
    # to be clever, I opted for this simple and readable approach.
    # This will merge whatever is provided in the command line into
    # your environment variables

    if os.environ.get('TABLEAU_SERVER', None) is None:
        os.environ['TABLEAU_SERVER'] = args.server

    if os.environ.get('TABLEAU_USERNAME', None) is None:
        os.environ['TABLEAU_USERNAME'] = args.username

    if os.environ.get('TABLEAU_SITE_ID', None) is None:
        os.environ['TABLEAU_SITE_ID'] = args.site_id or ''

    if os.environ.get('TABLEAU_PASSWORD', None) is None:
        import getpass
        password = getpass.getpass("Password: ")
        os.environ['TABLEAU_PASSWORD'] = password

    # Makes unittest and standalone play nice see http://stackoverflow.com/questions/1029891/
    sys.argv[1:] = args.unittest_args
    unittest.main()

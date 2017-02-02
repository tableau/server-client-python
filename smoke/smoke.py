import os
import unittest

import tableauserverclient as TSC

class SignInSignOutSmokeTest(unittest.TestCase):

    def setUp(self):
        self.username = os.environ.get('TABLEAU_USERNAME', None)
        self.server = os.environ.get('TABLEAU_SERVER', None)
        self.password = os.environ.get('TABLEAU_PASSWORD', None)
        self.site_id = os.environ.get('TABLEAU_SITE_ID', '')

        if not (self.username and self.server and self.password):
            raise unittest.SkipTest("Environment variables must be set when run from inside UnitTest")


    def test_sign_in_sign_out(self):

        authz = TSC.TableauAuth(self.username, self.password)
        server = TSC.Server(self.server)

        server.auth.sign_in(authz)
        server.auth.sign_out()

    def test_sign_in_get_sign_out(self):

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

        server.auth.sign_out()

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Initialize a server with content.')
    parser.add_argument('--server', '-s', default=None, help='server address')
    parser.add_argument('--site-id', '-si', default=None, help='site to use')
    parser.add_argument('--username', '-u', default=None, help='username to sign into server')
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

    if os.environ.get('TABLEAU_PASSWORD', None) is None:
        import getpass
        password = getpass.getpass("Password: ")
        os.environ['TABLEAU_PASSWORD'] = password

    # Makes unittest and standalone play nice see http://stackoverflow.com/questions/1029891/
    sys.argv[1:] = args.unittest_args
    unittest.main()
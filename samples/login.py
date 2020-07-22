####
# This script demonstrates how to log in to Tableau Server Client.
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='Logs in to the server.')

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    parser.add_argument('--server', '-s', required=True, help='server address')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--username', '-u', help='username to sign into the server')
    group.add_argument('--token-name', '-n', help='name of the personal access token used to sign into the server')
    parser.add_argument('--sitename', '-S', default='')

    args = parser.parse_args()

    # Set logging level based on user input, or error by default.
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Make sure we use an updated version of the rest apis.
    server = TSC.Server(args.server, use_server_version=True)

    if args.username:
        # Trying to authenticate using username and password.
        password = getpass.getpass("Password: ")

        print("\nSigning in...\nServer: {}\nSite: {}\nUsername: {}".format(args.server, args.sitename, args.username))
        tableau_auth = TSC.TableauAuth(args.username, password, site_id=args.sitename)
        with server.auth.sign_in(tableau_auth):
            print('Logged in successfully')

    else:
        # Trying to authenticate using personal access tokens.
        personal_access_token = getpass.getpass("Personal Access Token: ")

        print("\nSigning in...\nServer: {}\nSite: {}\nToken name: {}"
              .format(args.server, args.sitename, args.token_name))
        tableau_auth = TSC.PersonalAccessTokenAuth(token_name=args.token_name,
                                                   personal_access_token=personal_access_token, site_id=args.sitename)
        with server.auth.sign_in_with_personal_access_token(tableau_auth):
            print('Logged in successfully')


if __name__ == '__main__':
    main()

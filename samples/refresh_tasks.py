####
# TODO
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Get all of the refresh tasks available on a server')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site', '-S', default=None)
    parser.add_argument('--id', '-i', default=None)
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    server = TSC.Server(args.server)
    server.version = '2.5'
    with server.auth.sign_in(tableau_auth):
        import pprint

        if args.id:
            task = server.tasks.get_by_id(args.id)
            pprint.pprint(task)
        else:
            tasks, pagination = server.tasks.get()
            pprint.pprint(tasks)


if __name__ == '__main__':
    main()

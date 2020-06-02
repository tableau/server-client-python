####
# This script demonstrates how to use the Tableau Server Client
# to query extract refresh tasks and run them as needed.
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def handle_run(server, args):
    task = server.tasks.get_by_id(args.id)
    print(server.tasks.run(task))


def handle_list(server, _):
    tasks, pagination = server.tasks.get()
    for task in tasks:
        print("{}".format(task))


def handle_info(server, args):
    task = server.tasks.get_by_id(args.id)
    print("{}".format(task))


def main():
    parser = argparse.ArgumentParser(description='Get all of the refresh tasks available on a server')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site', '-S', default=None)
    parser.add_argument('-p', default=None)

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    subcommands = parser.add_subparsers()

    list_arguments = subcommands.add_parser('list')
    list_arguments.set_defaults(func=handle_list)

    run_arguments = subcommands.add_parser('run')
    run_arguments.add_argument('id', default=None)
    run_arguments.set_defaults(func=handle_run)

    info_arguments = subcommands.add_parser('info')
    info_arguments.add_argument('id', default=None)
    info_arguments.set_defaults(func=handle_info)

    args = parser.parse_args()

    if args.p is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.p

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    server = TSC.Server(args.server)
    server.version = '2.6'
    with server.auth.sign_in(tableau_auth):
        args.func(server, args)


if __name__ == '__main__':
    main()

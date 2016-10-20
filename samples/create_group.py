####
# This script demonstrates how to create groups using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 2.7.9 or later.
####


import argparse
import getpass
import logging

from datetime import time

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Creates sample schedules for each type of frequency.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    args = parser.parse_args()

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)
    with server.auth.sign_in(tableau_auth):
        group = TSC.GroupItem('test')
        group = server.groups.create(group)
        print(group)


if __name__ == '__main__':
    main()

####
# This script demonstrates how to use trigger a refresh on a datasource or workbook
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='Trigger a refresh task on a workbook or datasource.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site', '-S', default=None)
    parser.add_argument('--password', '-p', default=None, help='if not specified, you will be prompted')

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    parser.add_argument('resource_type', choices=['workbook', 'datasource'])
    parser.add_argument('resource_id')

    args = parser.parse_args()

    if args.password is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.password

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        if args.resource_type == "workbook":
            # Get the workbook by its Id to make sure it exists
            resource = server.workbooks.get_by_id(args.resource_id)

            # trigger the refresh, you'll get a job id back which can be used to poll for when the refresh is done
            results = server.workbooks.refresh(args.resource_id)
        else:
            # Get the datasource by its Id to make sure it exists
            resource = server.datasources.get_by_id(args.resource_id)

            # trigger the refresh, you'll get a job id back which can be used to poll for when the refresh is done
            results = server.datasources.refresh(resource)

        print(results)
        # TODO: Add a flag that will poll and wait for the returned job to be done


if __name__ == '__main__':
    main()

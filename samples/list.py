####
# This script demonstrates how to list all of the workbooks or datasources
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging
import os
import sys

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='List out the names and LUIDs for different resource types.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-S', default="", help='site to log into, do not specify for default site')
    parser.add_argument('--token-name', '-n', required=True, help='username to signin under')
    parser.add_argument('--token', '-t', help='personal access token for logging in')

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    parser.add_argument('resource_type', choices=['workbook', 'datasource', 'project', 'view', 'job', 'webhooks'])

    args = parser.parse_args()
    token = os.environ.get('TOKEN', args.token)
    if not token:
        print("--token or TOKEN environment variable needs to be set")
        sys.exit(1)

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, token, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        endpoint = {
            'workbook': server.workbooks,
            'datasource': server.datasources,
            'view': server.views,
            'job': server.jobs,
            'project': server.projects,
            'webhooks': server.webhooks,
        }.get(args.resource_type)

        for resource in TSC.Pager(endpoint.get):
            print(resource.id, resource.name)


if __name__ == '__main__':
    main()

####
# This script demonstrates how to list all of the workbooks or datasources
#
# To run the script, you must have installed Python 3.6 or later.
####

import argparse
import logging
import os
import sys

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='List out the names and LUIDs for different resource types.')
    # Common options; please keep those in sync across all samples
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-S', help='site name')
    parser.add_argument('--token-name', '-n', required=True,
                        help='name of the personal access token used to sign into the server')
    parser.add_argument('--token-value', '-v', required=True,
                        help='value of the personal access token used to sign into the server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    # Options specific to this sample
    parser.add_argument('resource_type', choices=['workbook', 'datasource', 'project', 'view', 'job', 'webhooks'])

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in to server
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
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

####
# This script demonstrates how to query for permissions using TSC
# To run the script, you must have installed Python 3.5 and later.
#
# Example usage: 'python query_permissions.py -s https://10ax.online.tableau.com --site
#       devSite123 -u tabby@tableau.com workbook b4065286-80f0-11ea-af1b-cb7191f48e45'
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='Query permissions of a given resource.')
    parser.add_argument('--server', '-s', required=True, help='Server address')
    parser.add_argument('--username', '-u', required=True, help='Username to sign into server')
    parser.add_argument('--site', '-S', default=None, help='Site to sign into - default site if not provided')
    parser.add_argument('-p', default=None, help='Password to sign into server')

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    parser.add_argument('resource_type', choices=['workbook', 'datasource', 'flow', 'table', 'database'])
    parser.add_argument('resource_id')

    args = parser.parse_args()

    if args.p is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.p

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in
    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):

        # Mapping to grab the handler for the user-inputted resource type
        endpoint = {
            'workbook': server.workbooks,
            'datasource': server.datasources,
            'flow': server.flows,
            'table': server.tables,
            'database': server.databases
        }.get(args.resource_type)

        # Get the resource by its ID
        resource = endpoint.get_by_id(args.resource_id)

        # Populate permissions for the resource
        endpoint.populate_permissions(resource)
        permissions = resource.permissions

        # Print result
        print("\n{0} permission rule(s) found for {1} {2}."
              .format(len(permissions), args.resource_type, args.resource_id))

        for permission in permissions:
            grantee = permission.grantee
            capabilities = permission.capabilities
            print("\nCapabilities for {0} {1}:".format(grantee.tag_name, grantee.id))

            for capability in capabilities:
                print("\t{0} - {1}".format(capability, capabilities[capability]))


if __name__ == '__main__':
    main()

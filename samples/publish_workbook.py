####
# This script demonstrates how to use the Tableau Server Client
# to publish a workbook to a Tableau server. It will publish
# a specified workbook to the 'default' project of the given server.
#
# Note: The REST API publish process cannot automatically include
# extracts or other resources that the workbook uses. Therefore,
# a .twb file with data from a local computer cannot be published,
# unless packaged into a .twbx file.
#
# For more information, refer to the documentations on 'Publish Workbook'
# (https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm)
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC
from tableauserverclient import ConnectionCredentials, ConnectionItem


def main():

    parser = argparse.ArgumentParser(description='Publish a workbook to server.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--filepath', '-f', required=True, help='computer filepath of the workbook to publish')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('--as-job', '-a', help='Publishing asynchronously', action='store_true')
    parser.add_argument('--skip-connection-check', '-c', help='Skip live connection check', action='store_true')
    parser.add_argument('--site', '-S', default='', help='id (contentUrl) of site to sign into')

    args = parser.parse_args()

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=args.site)
    server = TSC.Server(args.server)

    overwrite_true = TSC.Server.PublishMode.Overwrite

    with server.auth.sign_in(tableau_auth):

        # Step 2: Get all the projects on server, then look for the default one.
        all_projects, pagination_item = server.projects.get()
        default_project = next((project for project in all_projects if project.is_default()), None)

        connection1 = ConnectionItem()
        connection1.server_address = "mssql.test.com"
        connection1.connection_credentials = ConnectionCredentials("test", "password", True)

        connection2 = ConnectionItem()
        connection2.server_address = "postgres.test.com"
        connection2.server_port = "5432"
        connection2.connection_credentials = ConnectionCredentials("test", "password", True)

        all_connections = list()
        all_connections.append(connection1)
        all_connections.append(connection2)

        # Step 3: If default project is found, form a new workbook item and publish.
        if default_project is not None:
            new_workbook = TSC.WorkbookItem(default_project.id)
            if args.as_job:
                new_job = server.workbooks.publish(new_workbook, args.filepath, overwrite_true,
                                                   connections=all_connections, as_job=args.as_job,
                                                   skip_connection_check=args.skip_connection_check)
                print("Workbook published. JOB ID: {0}".format(new_job.id))
            else:
                new_workbook = server.workbooks.publish(new_workbook, args.filepath, overwrite_true,
                                                        connections=all_connections, as_job=args.as_job,
                                                        skip_connection_check=args.skip_connection_check)
                print("Workbook published. ID: {0}".format(new_workbook.id))
        else:
            error = "The default project could not be found."
            raise LookupError(error)


if __name__ == '__main__':
    main()

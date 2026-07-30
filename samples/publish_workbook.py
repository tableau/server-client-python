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
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging

import tableauserverclient as TSC
from tableauserverclient import ConnectionCredentials, ConnectionItem

from _shared import add_common_arguments, build_auth, resolve_credentials


def main():
    parser = argparse.ArgumentParser(description="Publish a workbook to server.")
    # Common options -- credentials come from CLI args, env vars, a .env file,
    # or an interactive prompt. See samples/_shared.py.
    add_common_arguments(parser)
    # Options specific to this sample
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--thumbnails-user-id", "-u", help="User ID to use for thumbnails")
    group.add_argument("--thumbnails-group-id", "-g", help="Group ID to use for thumbnails")

    parser.add_argument("--workbook-name", "-n", help="Name with which to publish the workbook")
    parser.add_argument("--file", "-f", help="local filepath of the workbook to publish")
    parser.add_argument("--as-job", "-a", help="Publishing asynchronously", action="store_true")
    parser.add_argument("--skip-connection-check", "-c", help="Skip live connection check", action="store_true")
    parser.add_argument("--project", help="Project within which to publish the workbook")
    parser.add_argument("--show-tabs", help="Publish workbooks with tabs displayed", action="store_true")

    args = parser.parse_args()

    resolve_credentials(args)

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    tableau_auth = build_auth(args)
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": False})
    with server.auth.sign_in(tableau_auth):
        # Step2: Retrieve the project id, if a project name was passed
        if args.project is not None:
            req_options = TSC.RequestOptions()
            req_options.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, args.project)
            )
            projects = list(TSC.Pager(server.projects, req_options))
            if len(projects) > 1:
                raise ValueError("The project name is not unique")
            project_id = projects[0].id
        else:
            # Get all the projects on server, then look for the default one.
            # Use TSC.Pager because `.get()` only returns the first page.
            default_project = next((project for project in TSC.Pager(server.projects) if project.is_default()), None)
            if default_project is None:
                raise LookupError("The destination project could not be found.")
            project_id = default_project.id

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

        # Step 3: Form a new workbook item and publish.
        overwrite_true = TSC.Server.PublishMode.Overwrite
        if project_id is not None:
            new_workbook = TSC.WorkbookItem(
                project_id=project_id,
                name=args.workbook_name,
                show_tabs=args.show_tabs,
                thumbnails_user_id=args.thumbnails_user_id,
                thumbnails_group_id=args.thumbnails_group_id,
            )
            if args.as_job:
                new_job = server.workbooks.publish(
                    new_workbook,
                    args.file,
                    overwrite_true,
                    connections=all_connections,
                    as_job=args.as_job,
                    skip_connection_check=args.skip_connection_check,
                )
                print(f"Workbook published. JOB ID: {new_job.id}")
            else:
                new_workbook = server.workbooks.publish(
                    new_workbook,
                    args.file,
                    overwrite_true,
                    connections=all_connections,
                    as_job=args.as_job,
                    skip_connection_check=args.skip_connection_check,
                )
                print(f"Workbook published. ID: {new_workbook.id}")
        else:
            error = "The destination project could not be found."
            raise LookupError(error)


if __name__ == "__main__":
    main()

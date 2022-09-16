####
# This script demonstrates how to use the Tableau Server Client
# to publish a datasource to a Tableau server. It will publish
# a specified datasource to the 'default' project of the provided site.
#
# Some optional arguments are provided to demonstrate async publishing,
# as well as providing connection credentials when publishing. If the
# provided datasource file is over 64MB in size, TSC will automatically
# publish the datasource using the chunking method.
#
# For more information, refer to the documentations:
# (https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_datasources.htm#publish_data_source)
#
# For signing into server, this script uses personal access tokens. For
# more information on personal access tokens, refer to the documentations:
# (https://help.tableau.com/current/server/en-us/security_personal_access_tokens.htm)
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Publish a datasource to server.")
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", required=True, help="server address")
    parser.add_argument("--site", "-S", help="site name")
    parser.add_argument(
        "--token-name", "-p", required=True, help="name of the personal access token used to sign into the server"
    )
    parser.add_argument(
        "--token-value", "-v", required=True, help="value of the personal access token used to sign into the server"
    )
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )
    # Options specific to this sample
    parser.add_argument("--file", "-f", required=True, help="filepath to the datasource to publish")
    parser.add_argument("--project", help="Project within which to publish the datasource")
    parser.add_argument("--async", "-a", help="Publishing asynchronously", dest="async_", action="store_true")
    parser.add_argument("--conn-username", help="connection username")
    parser.add_argument("--conn-password", help="connection password")
    parser.add_argument("--conn-embed", help="embed connection password to datasource", action="store_true")
    parser.add_argument("--conn-oauth", help="connection is configured to use oAuth", action="store_true")

    args = parser.parse_args()

    # Ensure that both the connection username and password are provided, or none at all
    if (args.conn_username and not args.conn_password) or (not args.conn_username and args.conn_password):
        parser.error("Both the connection username and password must be provided")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in to server
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Empty project_id field will default the publish to the site's default project
        project_id = ""

        # Retrieve the project id, if a project name was passed
        if args.project is not None:
            req_options = TSC.RequestOptions()
            req_options.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, args.project)
            )
            projects = list(TSC.Pager(server.projects, req_options))
            if len(projects) > 1:
                raise ValueError("The project name is not unique")
            project_id = projects[0].id

        # Create a new datasource item to publish
        new_datasource = TSC.DatasourceItem(project_id=project_id)

        # Create a connection_credentials item if connection details are provided
        new_conn_creds = None
        if args.conn_username:
            new_conn_creds = TSC.ConnectionCredentials(
                args.conn_username, args.conn_password, embed=args.conn_embed, oauth=args.conn_oauth
            )

        # Define publish mode - Overwrite, Append, or CreateNew
        publish_mode = TSC.Server.PublishMode.Overwrite

        # Publish datasource
        if args.async_:
            # Async publishing, returns a job_item
            new_job = server.datasources.publish(
                new_datasource, args.file, publish_mode, connection_credentials=new_conn_creds, as_job=True
            )
            print("Datasource published asynchronously. Job ID: {0}".format(new_job.id))
        else:
            # Normal publishing, returns a datasource_item
            new_datasource = server.datasources.publish(
                new_datasource, args.file, publish_mode, connection_credentials=new_conn_creds
            )
            print("Datasource published. Datasource ID: {0}".format(new_datasource.id))


if __name__ == "__main__":
    main()

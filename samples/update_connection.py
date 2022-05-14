####
# This script demonstrates how to update a connections credentials on a server to embed the credentials
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Update a connection on a datasource or workbook to embed credentials")
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
    parser.add_argument("resource_type", choices=["workbook", "datasource"])
    parser.add_argument("resource_id")
    parser.add_argument("connection_id")
    parser.add_argument("datasource_username")
    parser.add_argument("datasource_password")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        endpoint = {"workbook": server.workbooks, "datasource": server.datasources}.get(args.resource_type)

        update_function = endpoint.update_connection
        resource = endpoint.get_by_id(args.resource_id)
        endpoint.populate_connections(resource)
        connections = list(filter(lambda x: x.id == args.connection_id, resource.connections))
        assert len(connections) == 1
        connection = connections[0]
        connection.username = args.datasource_username
        connection.password = args.datasource_password
        connection.embed_password = True
        print(update_function(resource, connection).__dict__)


if __name__ == "__main__":
    main()

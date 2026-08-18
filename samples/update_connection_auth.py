####
# This script updates a single connection on a datasource or workbook to embed
# credentials. It's a generic authentication-change helper: the same code path
# works whether you're setting username+password or moving a Snowflake
# connection to keypair auth.
#
# Common authentication_type values (case-sensitive wire values):
#   - "UsernamePassword"       -- username + password auth
#   - "auth-keypair"           -- Snowflake keypair auth (see prerequisite below)
#   - "AD Service Principal"   -- Azure AD Service Principal
#
# SECURITY: datasource_password is a positional CLI argument. For keypair auth
# it carries the private-key material, which will leak into shell history, ps
# output, and audit logs on the machine running this script. Prefer supplying
# the key via an environment variable or stdin, or adapt this sample to read
# the key from a file that is protected by filesystem permissions.
#
# When embed_password=True the server binds the connection to a matching
# pre-saved credential on the site (looked up by attributes including username
# and connection class). For keypair-auth conversions this means the Snowflake
# private key MUST already be saved on the site under Site Settings -> Saved
# Credentials for Data Sources before running this script. If not, the update
# writes the new auth type into metadata but subsequent extract refreshes and
# connection tests fail because no bound credential is found.
#
# See:
#   https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_data_sources.htm#update_data_source_connection
#   https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_workbooks_and_views.htm#update_workbook_connection
####

import argparse
import logging
import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(
        description="Update a single connection on a datasource or workbook to embed credentials"
    )

    # Common options
    parser.add_argument("--server", "-s", help="Server address", required=True)
    parser.add_argument("--site", "-S", help="Site name", required=True)
    parser.add_argument("--token-name", "-p", help="Personal access token name", required=True)
    parser.add_argument("--token-value", "-v", help="Personal access token value", required=True)
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="Logging level (default: error)",
    )

    # Resource and connection details
    parser.add_argument("resource_type", choices=["workbook", "datasource"])
    parser.add_argument("resource_id", help="Workbook or datasource ID")
    parser.add_argument("connection_id", help="Connection ID to update")
    parser.add_argument("datasource_username", help="Username to set for the connection")
    parser.add_argument("datasource_password", help="Password to set for the connection")
    parser.add_argument("authentication_type", help="Authentication type")

    args = parser.parse_args()

    # Logging setup
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        endpoint = {"workbook": server.workbooks, "datasource": server.datasources}.get(args.resource_type)

        update_function = endpoint.update_connection
        resource = endpoint.get_by_id(args.resource_id)
        endpoint.populate_connections(resource)

        connections = [conn for conn in resource.connections if conn.id == args.connection_id]
        assert len(connections) == 1, f"Connection ID '{args.connection_id}' not found."

        connection = connections[0]
        connection.username = args.datasource_username
        connection.password = args.datasource_password
        connection.auth_type = args.authentication_type
        connection.embed_password = True

        updated_connection = update_function(resource, connection)
        print(f"Updated connection: {updated_connection.__dict__}")


if __name__ == "__main__":
    main()

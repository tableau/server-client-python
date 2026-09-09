####
# This script updates a single connection on a datasource or workbook to embed
# credentials. It's a generic authentication-change helper: the same code path
# works whether you're setting username+password or moving a Snowflake
# connection to keypair auth.
#
# Common authentication_type wire values (case-sensitive; see
# codegen/constants.data in the monolith for the canonical list):
#   - "auth-user-pass"                -- username + password (canonical)
#   - "username-password"             -- alternate spelling used by some
#                                        connectors (SAP HANA, SAP Sybase ASE,
#                                        SAP NetWeaver BW, Denodo, Salesforce)
#   - "auth-keypair"                  -- Snowflake keypair (see prerequisite
#                                        below)
#   - "auth-user"                     -- username only
#   - "auth-pass"                     -- password only
#   - "oauth"                         -- OAuth
#   - "auth-oauth-service-account"    -- OAuth service account
#   - "auth-integrated"               -- integrated auth (Kerberos, Windows AD)
#   - "auth-none"                     -- no auth on the connection
# Some connectors present UI labels that differ from the wire value (e.g. an
# Azure SQL DB "authentication" field with entries like "AD Service Principal"
# maps to the wire value "auth-client-creds"). To find the exact value your
# connector expects, run `endpoint.populate_connections(resource)` on an
# existing resource and read `connection.auth_type`.
#
# !!! SECURITY: the connection password (or private-key material for keypair
# auth) can leak into shell history, ps output, and audit logs when it is
# passed on the command line. To keep it off the CLI, set the
# TABLEAU_CONNECTION_PASSWORD environment variable and OMIT the last
# positional argument; this script reads it from the environment when the
# CLI value is not provided.
#
# When embed_password=True the server binds the connection to a matching
# pre-saved credential on the site (looked up by attributes including username
# and connection class). For keypair-auth conversions this means the Snowflake
# private key MUST already be saved on the site under Site Settings -> Saved
# Credentials for Data Sources before running this script. Verify at that page
# first; the update will silently succeed even if no matching credential is
# saved, but subsequent extract refreshes and connection tests will fail.
#
# Example (Snowflake keypair conversion, key material from a file, no secret
# on the command line):
#   export TABLEAU_CONNECTION_PASSWORD="$(cat snowflake_pkcs8.key)"
#   python update_connection_auth.py \
#     --server https://prod-useast-a.online.tableau.com --site MySite \
#     --token-name mytoken --token-value <pat-value> \
#     datasource <ds-luid> <connection-luid> \
#     snowflake_user auth-keypair
#
# See:
#   https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_data_sources.htm#update_data_source_connection
#   https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_workbooks_and_views.htm#update_workbook_connection
####

import argparse
import logging
import os
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
    parser.add_argument(
        "datasource_password",
        nargs="?",
        default=None,
        help=(
            "Password (or private-key material for keypair auth) to set on the "
            "connection. Prefer omitting this positional and setting the "
            "TABLEAU_CONNECTION_PASSWORD environment variable so the value does "
            "not land in shell history."
        ),
    )
    parser.add_argument("authentication_type", help="Authentication type")

    args = parser.parse_args()

    # Resolve the connection secret: CLI positional wins, otherwise fall back
    # to TABLEAU_CONNECTION_PASSWORD from the environment. This keeps
    # private-key material out of shell history and ps output.
    connection_password = args.datasource_password or os.environ.get("TABLEAU_CONNECTION_PASSWORD")
    if not connection_password:
        raise SystemExit(
            "No connection password provided. Pass it as the last positional argument "
            "or set the TABLEAU_CONNECTION_PASSWORD environment variable."
        )

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
        connection.password = connection_password
        connection.auth_type = args.authentication_type
        connection.embed_password = True

        updated_connection = update_function(resource, connection)
        print(f"Updated connection: {updated_connection.__dict__}")


if __name__ == "__main__":
    main()

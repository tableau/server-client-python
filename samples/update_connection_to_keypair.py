####
# This script demonstrates how to convert an existing Tableau Cloud connection
# from username/password authentication to Snowflake keypair authentication.
#
# PREREQUISITE: The Snowflake private key MUST already be saved on the site
# under Site Settings -> Saved Credentials for Data Sources before running this
# sample. Tableau Cloud stores the private key at the site level, keyed on
# (server address, username). If the credential has not been saved first, the
# update will succeed but subsequent extract refreshes / connection tests will
# fail authentication.
#
# Supported since REST API v3.27.
# See: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_data_sources.htm#update_data_source_connection
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert an existing datasource or workbook connection from "
            "username/password auth to Snowflake keypair auth. Requires the "
            "private key to be pre-saved under Site Settings -> Saved "
            "Credentials for Data Sources."
        )
    )
    # Common options; please keep these in sync across all samples
    parser.add_argument("--server", "-s", help="server address", required=True)
    parser.add_argument("--site", "-S", help="site name", required=True)
    parser.add_argument("--token-name", "-p", help="name of the personal access token used to sign into the server")
    parser.add_argument("--token-value", "-v", help="value of the personal access token used to sign into the server")
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )

    # Options specific to this sample
    parser.add_argument(
        "--content-type",
        choices=["workbook", "datasource"],
        default="datasource",
        help="type of content to update (default: datasource)",
    )
    parser.add_argument("resource_id", help="LUID of the workbook or datasource to update")
    parser.add_argument(
        "keypair_username",
        help="Snowflake account username configured with keypair authentication",
    )
    parser.add_argument(
        "--connection-id",
        help=(
            "Optional LUID of a specific connection to update. If omitted, "
            "the first Snowflake connection on the item is used."
        ),
    )

    args = parser.parse_args()

    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    print(
        "\nReminder: this sample assumes the Snowflake private key has already been "
        "saved on your site under Site Settings -> Saved Credentials for Data Sources.\n"
        "If it has not, the update will succeed but the connection will fail to authenticate.\n"
    )

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        endpoint = {"workbook": server.workbooks, "datasource": server.datasources}[args.content_type]

        resource = endpoint.get_by_id(args.resource_id)
        endpoint.populate_connections(resource)

        if args.connection_id:
            matches = [c for c in resource.connections if c.id == args.connection_id]
            if not matches:
                raise SystemExit(
                    f"Connection ID '{args.connection_id}' not found on {args.content_type} '{args.resource_id}'."
                )
            connection = matches[0]
        else:
            snowflake_conns = [c for c in resource.connections if c.connection_type == "snowflake"]
            if not snowflake_conns:
                raise SystemExit(
                    f"No Snowflake connections found on {args.content_type} '{args.resource_id}'. "
                    "Available connection types: "
                    + ", ".join(sorted({c.connection_type or "unknown" for c in resource.connections}))
                )
            connection = snowflake_conns[0]
            print(f"Using first Snowflake connection: {connection.id}")

        print(f"Before: {connection}")

        connection.auth_type = "auth-keypair"
        connection.username = args.keypair_username
        # embedPassword=true tells the server to use the pre-saved credential
        # from Site Settings -> Saved Credentials rather than prompt at query time.
        connection.embed_password = True

        endpoint.update_connection(resource, connection)

        # Re-fetch to confirm the change stuck.
        endpoint.populate_connections(resource)
        updated = next((c for c in resource.connections if c.id == connection.id), None)
        if updated is None:
            raise SystemExit(f"Connection {connection.id} disappeared after update.")

        print(f"After:  {updated}")
        print(f"\nauth_type is now: {updated.auth_type}")


if __name__ == "__main__":
    main()

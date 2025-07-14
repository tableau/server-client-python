import argparse
import logging
import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Update a single connection on a datasource or workbook to embed credentials")

    # Common options
    parser.add_argument("--server", "-s", help="Server address", required=True)
    parser.add_argument("--site", "-S", help="Site name", required=True)
    parser.add_argument("--token-name", "-p", help="Personal access token name", required=True)
    parser.add_argument("--token-value", "-v", help="Personal access token value", required=True)
    parser.add_argument(
        "--logging-level", "-l",
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
        endpoint = {
            "workbook": server.workbooks,
            "datasource": server.datasources
        }.get(args.resource_type)

        update_function = endpoint.update_connection
        resource = endpoint.get_by_id(args.resource_id)
        endpoint.populate_connections(resource)

        connections = [conn for conn in resource.connections if conn.id == args.connection_id]
        assert len(connections) == 1, f"Connection ID '{args.connection_id}' not found."

        connection = connections[0]
        connection.username = args.datasource_username
        connection.password = args.datasource_password
        connection.authentication_type = args.authentication_type
        connection.embed_password = True

        updated_connection = update_function(resource, connection)
        print(f"Updated connection: {updated_connection.__dict__}")


if __name__ == "__main__":
    main()

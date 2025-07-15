import argparse
import logging
import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Bulk update all workbook or datasource connections")

    # Common options
    parser.add_argument("--server", "-s", help="Server address", required=True)
    parser.add_argument("--site", "-S", help="Site name", required=True)
    parser.add_argument("--username", "-p", help="Personal access token name", required=True)
    parser.add_argument("--password", "-v", help="Personal access token value", required=True)
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="Logging level (default: error)",
    )

    # Resource-specific
    parser.add_argument("resource_type", choices=["workbook", "datasource"])
    parser.add_argument("resource_id")
    parser.add_argument("datasource_username")
    parser.add_argument("authentication_type")
    parser.add_argument("--datasource_password", default=None, help="Datasource password (optional)")
    parser.add_argument("--embed_password", default="true", choices=["true", "false"], help="Embed password (default: true)")

    args = parser.parse_args()

    # Set logging level
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.TableauAuth(args.username, args.password, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        endpoint = {
            "workbook": server.workbooks,
            "datasource": server.datasources
        }.get(args.resource_type)

        resource = endpoint.get_by_id(args.resource_id)
        endpoint.populate_connections(resource)

        connection_luids = [conn.id for conn in resource.connections]
        embed_password = args.embed_password.lower() == "true"

        # Call unified update_connections method
        updated_ids = endpoint.update_connections(
            resource,
            connection_luids=connection_luids,
            authentication_type=args.authentication_type,
            username=args.datasource_username,
            password=args.datasource_password,
            embed_password=embed_password
        )

        print(f"Updated connections on {args.resource_type} {args.resource_id}: {updated_ids}")


if __name__ == "__main__":
    main()

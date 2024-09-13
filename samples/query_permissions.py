####
# This script demonstrates how to query for permissions using TSC
# To run the script, you must have installed Python 3.7 or later.
#
# Example usage: 'python query_permissions.py -s https://10ax.online.tableau.com --site
#       devSite123 -u tabby@tableau.com workbook b4065286-80f0-11ea-af1b-cb7191f48e45'
####

import argparse
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Query permissions of a given resource.")
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", help="server address")
    parser.add_argument("--site", "-S", help="site name")
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
    parser.add_argument("resource_type", choices=["workbook", "datasource", "flow", "table", "database"])
    parser.add_argument("resource_id")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Mapping to grab the handler for the user-inputted resource type
        endpoint = {
            "workbook": server.workbooks,
            "datasource": server.datasources,
            "flow": server.flows,
            "table": server.tables,
            "database": server.databases,
        }.get(args.resource_type)

        # Get the resource by its ID
        resource = endpoint.get_by_id(args.resource_id)

        # Populate permissions for the resource
        endpoint.populate_permissions(resource)
        permissions = resource.permissions

        # Print result
        print(f"\n{len(permissions)} permission rule(s) found for {args.resource_type} {args.resource_id}.")

        for permission in permissions:
            grantee = permission.grantee
            capabilities = permission.capabilities
            print(f"\nCapabilities for {grantee.tag_name} {grantee.id}:")

            for capability in capabilities:
                print(f"\t{capability} - {capabilities[capability]}")


if __name__ == "__main__":
    main()

####
# This script demonstrates how to list all of the workbooks or datasources
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging
import os
import sys

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="List out the names and LUIDs for different resource types.")
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", required=True, help="server address")
    parser.add_argument("--site", "-S", help="site name")
    parser.add_argument(
        "--token-name", "-n", required=True, help="name of the personal access token used to sign into the server"
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
    parser.add_argument("resource_type", choices=["workbook", "datasource", "project", "view", "job", "webhooks"])

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in to server
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        endpoint = {
            "datasource": server.datasources,
            "job": server.jobs,
            "metric": server.metrics,
            "project": server.projects,
            "view": server.views,
            "webhooks": server.webhooks,
            "workbook": server.workbooks,
        }.get(args.resource_type)

        options = TSC.RequestOptions()
        options.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Desc))

        count = 0
        for resource in TSC.Pager(endpoint.get, options):
            count = count + 1
            # endpoint.populate_connections(resource)
            print(resource.name[:18], " ")  # , resource._connections())
            if count > 100:
                break
        print("Total: {}".format(count))


if __name__ == "__main__":
    main()

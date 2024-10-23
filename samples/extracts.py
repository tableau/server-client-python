####
# This script demonstrates how to use the Tableau Server Client to interact with extracts.
# It explores the different functions that the REST API supports on extracts.
#####

import argparse
import logging
import os.path

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Explore extract functions supported by the Server API.")
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", help="server address")
    parser.add_argument("--site", help="site name")
    parser.add_argument("--token-name", "-tn", help="name of the personal access token used to sign into the server")
    parser.add_argument("--token-value", "-tv", help="value of the personal access token used to sign into the server")
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )
    # Options specific to this sample
    parser.add_argument("--delete")
    parser.add_argument("--create")
    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=False)
    server.add_http_options({"verify": False})
    server.use_server_version()
    with server.auth.sign_in(tableau_auth):
        # Gets all workbook items
        all_workbooks, pagination_item = server.workbooks.get()
        print(f"\nThere are {pagination_item.total_available} workbooks on site: ")
        print([workbook.name for workbook in all_workbooks])

        if all_workbooks:
            # Pick one workbook from the list
            wb = all_workbooks[3]

        if args.create:
            print("create extract on wb ", wb.name)
            extract_job = server.workbooks.create_extract(wb, includeAll=True)
            print(extract_job)

        if args.delete:
            print("delete extract on wb ", wb.name)
            jj = server.workbooks.delete_extract(wb)
            print(jj)


if __name__ == "__main__":
    main()

####
# This script demonstrates how to work with pagination in the .get() method calls, and how to use
# the QuerySet item that is an alternative interface for filtering and sorting these calls.
#
# In Part 1, this script will iterate over every workbook that exists on the server using the
# pagination item to fetch additional pages as needed.
# In Part 2, the script will iterate over the same workbooks with an easy-to-read filter.
#
# While this sample uses workbooks, this same technique will work with any of the .get() methods that return
# a pagination item
####

import argparse
import logging
import os.path

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description="Demonstrate pagination on the list of workbooks on the server.")
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
    # Options specific to this sample:
    # No additional options, yet. If you add some, please add them here

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in to server
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):

        # 1. Pager: Pager takes a server Endpoint as its first parameter, and a RequestOptions
        # object as the second parameter. The Endpoint defines which type of objects it returns, and
        # RequestOptions defines any restrictions on the objects: filter by name, sort, or select a page
        print("Your server contains the following workbooks:\n")
        count = 0
        # Using a small number here so that you can see it work. Default is 100 and mostly doesn't need to change
        page_size = 5
        page_options = TSC.RequestOptions(1, page_size)
        print("Fetching workbooks in pages of 5")
        for wb in TSC.Pager(server.workbooks, page_options):
            print(wb.name)
            count = count + 1
        print("Total: {}\n".format(count))

        count = 0
        new_page_options = TSC.RequestOptions(2, page_size)
        print("Fetching workbooks again, starting at the 2nd page of results")
        for wb in TSC.Pager(server.workbooks, new_page_options):
            print(wb.name)
            count = count + 1
        print("2nd Total: {}\n".format(count))

        # 2. QuerySet offers a fluent interface on top of the RequestOptions object
        # TODO: (bug) QuerySet doesn't have a way to page through more results yet
        count = 0
        for wb in server.workbooks.filter(ownerEmail="jfitzgerald@tableau.com").paginate(page_size=3):
            print(wb.name)
            count = count + 1
        print("QuerySet Total: {}".format(count))


if __name__ == "__main__":
    main()

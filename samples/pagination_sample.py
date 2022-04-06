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
        you = server.users.get_by_id(server.user_id)
        print(you.name, you.id)
        # 1. Pager: Pager takes a server Endpoint as its first parameter, and a RequestOptions
        # object as the second parameter. The Endpoint defines which type of objects it returns, and
        # RequestOptions defines any restrictions on the objects: filter by name, sort, or select a page
        print("Your server contains the following workbooks:\n")
        count = 0
        # Using a small number here so that you can see it work. Default is 100 and mostly doesn't need to change
        page_options = TSC.RequestOptions(1, 5)
        print("Fetching workbooks in pages of 5")
        for wb in TSC.Pager(server.workbooks, page_options):
            print(wb.name)
            count = count + 1
        print("Total: {}\n".format(count))

        count = 0
        page_options = TSC.RequestOptions(2, 3)
        print("Paging: start at the second page of workbooks, using pagesize = 3")
        for wb in TSC.Pager(server.workbooks, page_options):
            print(wb.name)
            count = count + 1
        print("Truncated Total: {}\n".format(count))

        print("Your id: ", you.name, you.id, "\n")
        count = 0
        filtered_page_options = TSC.RequestOptions(1, 3)
        filter_owner = TSC.Filter("ownerEmail", TSC.RequestOptions.Operator.Equals, "jfitzgerald@tableau.com")
        filtered_page_options.filter.add(filter_owner)
        print("Fetching workbooks again, filtering by owner")
        for wb in TSC.Pager(server.workbooks, filtered_page_options):
            print(wb.name, " -- ", wb.owner_id)
            count = count + 1
        print("Filtered Total: {}\n".format(count))

        # 2. QuerySet offers a fluent interface on top of the RequestOptions object
        print("Fetching workbooks again - this time filtered with QuerySet")
        count = 0
        page = 1
        more = True
        while more:
            queryset = server.workbooks.filter(ownerEmail="jfitzgerald@tableau.com")
            for wb in queryset.paginate(page_number=page, page_size=3):
                print(wb.name, " -- ", wb.owner_id)
                count = count + 1
            more = queryset.total_available > count
            page = page + 1
        print("QuerySet Total: {}".format(count))

        # 3. QuerySet also allows you to iterate over all objects without explicitly paging.
        print("Fetching again - this time without manually paging")
        for i, wb in enumerate(server.workbooks.filter(owner_email="jfitzgerald@tableau.com"), start=1):
            print(wb.name, "--", wb.owner_id)

        print(f"QuerySet Total, implicit paging: {i}")


if __name__ == "__main__":
    main()

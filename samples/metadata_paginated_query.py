####
# This script demonstrates how to use the metadata API to query information on a published data source
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging
from pprint import pprint

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Use the metadata API to get information on a published data source.")
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", help="server address")
    parser.add_argument("--site", "-S", help="site name")
    parser.add_argument("--token-name", "-n", help="name of the personal access token used to sign into the server")
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
        "datasource_name",
        nargs="?",
        help="The name of the published datasource. If not present, we query all data sources.",
    )

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in to server
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Execute the query
        result = server.metadata.query(
            """
            # Query must declare that it accepts first and afterToken variables
            query paged($first:Int, $afterToken:String) {
              workbooksConnection(first: $first, after:$afterToken) {
                nodes {
                  luid
                  name
                  projectName
                  description
                }
                totalCount
                pageInfo {
                  endCursor
                  hasNextPage
                }
              }
            }
            """,
            # "first" adjusts the page size. Here we set it to 5 to demonstrate pagination.
            # Set it to a higher number to reduce the number of pages. Including
            # first and afterToken is optional, and if not included, TSC will
            # use its default page size of 100.
            variables={"first": 5, "afterToken": None},
        )

        # Multiple pages are captured in result["pages"]. Each page contains
        # the result of one execution of the query above.
        for page in result["pages"]:
            # Display warnings/errors (if any)
            if page.get("errors"):
                print("### Errors/Warnings:")
                pprint(result["errors"])

            # Print the results
            if result.get("data"):
                print("### Results:")
                pprint(result["data"]["workbooksConnection"]["nodes"])


if __name__ == "__main__":
    main()

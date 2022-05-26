####
# This script demonstrates how to use the Tableau Server Client
# to move a workbook from one project to another. It will find
# a workbook that matches a given name and update it to be in
# the desired project.
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging
import urllib.parse

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description="Move one workbook from the default project to another.")
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", required=True, help="server address")
    parser.add_argument("--site", "-S", help="site name")
    parser.add_argument(
        "--token-name", "-p", required=True, help="name of the personal access token used to sign into the server"
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
    parser.add_argument("--workbook-name", "-w", required=True, help="name of workbook to move")
    parser.add_argument("--destination-project", "-d", required=True, help="name of project to move workbook into")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Step 2: Find destination project
        try:
            dest_project = server.projects.filter(name=urllib.parse.quote_plus(args.destination_project))[0]
        except IndexError:
            raise LookupError(f"No project named {args.destination_project} found.")

        # Step 3: Query workbook to move
        try:
            workbook = server.workbooks.filter(name=urllib.parse.quote_plus(args.workbook_name))[0]
        except IndexError:
            raise LookupError(f"No workbook named {args.workbook_name} found")

        # Step 4: Update workbook with new project id
        workbook.project_id = dest_project.id
        target_workbook = server.workbooks.update(workbook)
        print(f"New project: {target_workbook.project_name}")


if __name__ == "__main__":
    main()

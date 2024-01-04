####
# This script demonstrates how to create extract tasks in Tableau Cloud
# using the Tableau Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####


import argparse
import logging

from datetime import time

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Creates sample extract refresh task.")
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
    # Options specific to this sample:
    # This sample has no additional options, yet. If you add some, please add them here

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=False)
    server.add_http_options({"verify": False})
    server.use_server_version()
    with server.auth.sign_in(tableau_auth):
        # Monthly Schedule
        # This schedule will run on the 15th of every month at 11:30PM
        monthly_interval = TSC.MonthlyInterval(start_time=time(23, 30), interval_value=15)
        monthly_schedule = TSC.ScheduleItem(
            None,
            None,
            None,
            None,
            monthly_interval,
        )

        # Default to using first workbook found in server
        all_workbook_items, pagination_item = server.workbooks.get()
        my_workbook: TSC.WorkbookItem = all_workbook_items[0]

        target_item = TSC.Target(
            my_workbook.id,  # the id of the workbook or datasource
            "workbook",  # alternatively can be "datasource"
        )

        extract_item = TSC.TaskItem(
            None,
            "FullRefresh",
            None,
            None,
            None,
            monthly_schedule,
            None,
            target_item,
        )

        try:
            response = server.tasks.create(extract_item)
            print(response)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()

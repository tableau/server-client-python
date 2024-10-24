####
# This script demonstrates how to update workbook data acceleration  using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####


import argparse
import logging

import tableauserverclient as TSC
from tableauserverclient import IntervalItem


def main():
    parser = argparse.ArgumentParser(description="Creates sample schedules for each type of frequency.")
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
        # Get workbook
        all_workbooks, pagination_item = server.workbooks.get()
        print("\nThere are {} workbooks on site: ".format(pagination_item.total_available))
        print([workbook.name for workbook in all_workbooks])

        if all_workbooks:
            # Pick 1 workbook to try data acceleration.
            # Note that data acceleration has a couple of requirements, please check the Tableau help page
            # to verify your workbook/view is eligible for data acceleration.

            # Assuming 1st workbook is eligible for sample purposes
            sample_workbook = all_workbooks[2]

            # Enable acceleration for all the views in the workbook
            enable_config = dict()
            enable_config["acceleration_enabled"] = True
            enable_config["accelerate_now"] = True

            sample_workbook.data_acceleration_config = enable_config
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            # Since we did not set any specific view, we will enable all views in the workbook
            print("Enable acceleration for all the views in the workbook " + updated.name + ".")

            # Disable acceleration on one of the view in the workbook
            # You have to populate_views first, then set the views of the workbook
            # to the ones you want to update.
            server.workbooks.populate_views(sample_workbook)
            view_to_disable = sample_workbook.views[0]
            sample_workbook.views = [view_to_disable]

            disable_config = dict()
            disable_config["acceleration_enabled"] = False
            disable_config["accelerate_now"] = True

            sample_workbook.data_acceleration_config = disable_config
            # To get the acceleration status on the response, set includeViewAccelerationStatus=true
            # Note that you have to populate_views first to get the acceleration status, since
            # acceleration status is per view basis (not per workbook)
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook, True)
            view1 = updated.views[0]
            print('Disabled acceleration for 1 view "' + view1.name + '" in the workbook ' + updated.name + ".")

            # Get acceleration status of the views in workbook using workbooks.get_by_id
            # This won't need to do populate_views beforehand
            my_workbook = server.workbooks.get_by_id(sample_workbook.id)
            view1 = my_workbook.views[0]
            view2 = my_workbook.views[1]
            print(
                "Fetching acceleration status for views in the workbook "
                + updated.name
                + ".\n"
                + 'View "'
                + view1.name
                + '" has acceleration_status = '
                + view1.data_acceleration_config["acceleration_status"]
                + ".\n"
                + 'View "'
                + view2.name
                + '" has acceleration_status = '
                + view2.data_acceleration_config["acceleration_status"]
                + "."
            )


if __name__ == "__main__":
    main()

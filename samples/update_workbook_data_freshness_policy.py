####
# This script demonstrates how to update workbook data freshness policy using the Tableau
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
    parser.add_argument("--token-name", "-p", help="name of the personal access token " "used to sign into the server")
    parser.add_argument(
        "--token-value", "-v", help="value of the personal access token " "used to sign into the server"
    )
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
            # Pick 1 workbook that has live datasource connection.
            # Assuming 1st workbook met the criteria for sample purposes
            # Data Freshness Policy is not available on extract & file-based datasource.
            sample_workbook = all_workbooks[2]

            # Get more info from the workbook selected
            # Troubleshoot: if sample_workbook_extended.data_freshness_policy.option returns with AttributeError
            # it could mean the workbook selected does not have live connection, which means it doesn't have
            # data freshness policy. Change to another workbook with live datasource connection.
            sample_workbook_extended = server.workbooks.get_by_id(sample_workbook.id)
            try:
                print(
                    "Workbook "
                    + sample_workbook.name
                    + " has data freshness policy option set to: "
                    + sample_workbook_extended.data_freshness_policy.option
                )
            except AttributeError as e:
                print(
                    "Workbook does not have data freshness policy, possibly due to the workbook selected "
                    "does not have live connection. Change to another workbook using live datasource connection."
                )

            # Update Workbook Data Freshness Policy to "AlwaysLive"
            sample_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.AlwaysLive
            )
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            print(
                "Workbook "
                + updated.name
                + " updated data freshness policy option to: "
                + updated.data_freshness_policy.option
            )

            # Update Workbook Data Freshness Policy to "SiteDefault"
            sample_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.SiteDefault
            )
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            print(
                "Workbook "
                + updated.name
                + " updated data freshness policy option to: "
                + updated.data_freshness_policy.option
            )

            # Update Workbook Data Freshness Policy to "FreshEvery" schedule.
            # Set the schedule to be fresh every 10 hours
            # Once the data_freshness_policy is already populated (e.g. due to previous calls),
            # it is possible to directly change the option & other parameters directly like below
            sample_workbook.data_freshness_policy.option = TSC.DataFreshnessPolicyItem.Option.FreshEvery
            fresh_every_ten_hours = TSC.DataFreshnessPolicyItem.FreshEvery(
                TSC.DataFreshnessPolicyItem.FreshEvery.Frequency.Hours, 10
            )
            sample_workbook.data_freshness_policy.fresh_every_schedule = fresh_every_ten_hours
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            print(
                "Workbook "
                + updated.name
                + " updated data freshness policy option to: "
                + updated.data_freshness_policy.option
                + " with frequency of "
                + str(updated.data_freshness_policy.fresh_every_schedule.value)
                + " "
                + updated.data_freshness_policy.fresh_every_schedule.frequency
            )

            # Update Workbook Data Freshness Policy to "FreshAt" schedule.
            # Set the schedule to be fresh at 10AM every day
            sample_workbook.data_freshness_policy.option = TSC.DataFreshnessPolicyItem.Option.FreshAt
            fresh_at_ten_daily = TSC.DataFreshnessPolicyItem.FreshAt(
                TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Day, "10:00:00", "America/Los_Angeles"
            )
            sample_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_ten_daily
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            print(
                "Workbook "
                + updated.name
                + " updated data freshness policy option to: "
                + updated.data_freshness_policy.option
                + " with frequency of "
                + str(updated.data_freshness_policy.fresh_at_schedule.time)
                + " every "
                + updated.data_freshness_policy.fresh_at_schedule.frequency
            )

            # Set the schedule to be fresh at 6PM every week on Wednesday and Sunday
            sample_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshAt
            )
            fresh_at_6pm_wed_sun = TSC.DataFreshnessPolicyItem.FreshAt(
                TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Week,
                "18:00:00",
                "America/Los_Angeles",
                [IntervalItem.Day.Wednesday, "Sunday"],
            )

            sample_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_6pm_wed_sun
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            new_fresh_at_schedule = updated.data_freshness_policy.fresh_at_schedule
            print(
                "Workbook "
                + updated.name
                + " updated data freshness policy option to: "
                + updated.data_freshness_policy.option
                + " with frequency of "
                + str(new_fresh_at_schedule.time)
                + " every "
                + new_fresh_at_schedule.frequency
                + " on "
                + new_fresh_at_schedule.interval_item[0]
                + ","
                + new_fresh_at_schedule.interval_item[1]
            )

            # Set the schedule to be fresh at 12AM every last day of the month
            sample_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshAt
            )
            fresh_at_last_day_of_month = TSC.DataFreshnessPolicyItem.FreshAt(
                TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Month, "00:00:00", "America/Los_Angeles", ["LastDay"]
            )

            sample_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_last_day_of_month
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            new_fresh_at_schedule = updated.data_freshness_policy.fresh_at_schedule
            print(
                "Workbook "
                + updated.name
                + " updated data freshness policy option to: "
                + updated.data_freshness_policy.option
                + " with frequency of "
                + str(new_fresh_at_schedule.time)
                + " every "
                + new_fresh_at_schedule.frequency
                + " on "
                + new_fresh_at_schedule.interval_item[0]
            )

            # Set the schedule to be fresh at 8PM every 1st,13th,20th day of the month
            fresh_at_dates_of_month = TSC.DataFreshnessPolicyItem.FreshAt(
                TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Month,
                "00:00:00",
                "America/Los_Angeles",
                ["1", "13", "20"],
            )

            sample_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_dates_of_month
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            new_fresh_at_schedule = updated.data_freshness_policy.fresh_at_schedule
            print(
                "Workbook "
                + updated.name
                + " updated data freshness policy option to: "
                + updated.data_freshness_policy.option
                + " with frequency of "
                + str(new_fresh_at_schedule.time)
                + " every "
                + new_fresh_at_schedule.frequency
                + " on "
                + str(new_fresh_at_schedule.interval_item)
            )


if __name__ == "__main__":
    main()

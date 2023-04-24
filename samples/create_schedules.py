####
# This script demonstrates how to create schedules using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####


import argparse
import logging

from datetime import time

import tableauserverclient as TSC


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
        # Hourly Schedule
        # This schedule will run every 2 hours between 2:30AM and 11:00PM
        hourly_interval = TSC.HourlyInterval(start_time=time(2, 30), end_time=time(23, 0), interval_value=2)

        hourly_schedule = TSC.ScheduleItem(
            "Hourly-Schedule",
            50,
            TSC.ScheduleItem.Type.Extract,
            TSC.ScheduleItem.ExecutionOrder.Parallel,
            hourly_interval,
        )
        try:
            hourly_schedule = server.schedules.create(hourly_schedule)
            print("Hourly schedule created (ID: {}).".format(hourly_schedule.id))
        except Exception as e:
            print(e)

        # Daily Schedule
        # This schedule will run every day at 5AM
        daily_interval = TSC.DailyInterval(start_time=time(5))
        daily_schedule = TSC.ScheduleItem(
            "Daily-Schedule",
            60,
            TSC.ScheduleItem.Type.Subscription,
            TSC.ScheduleItem.ExecutionOrder.Serial,
            daily_interval,
        )
        try:
            daily_schedule = server.schedules.create(daily_schedule)
            print("Daily schedule created (ID: {}).".format(daily_schedule.id))
        except Exception as e:
            print(e)

        # Weekly Schedule
        # This schedule will wun every Monday, Wednesday, and Friday at 7:15PM
        weekly_interval = TSC.WeeklyInterval(
            time(19, 15), TSC.IntervalItem.Day.Monday, TSC.IntervalItem.Day.Wednesday, TSC.IntervalItem.Day.Friday
        )
        weekly_schedule = TSC.ScheduleItem(
            "Weekly-Schedule",
            70,
            TSC.ScheduleItem.Type.Extract,
            TSC.ScheduleItem.ExecutionOrder.Serial,
            weekly_interval,
        )
        try:
            weekly_schedule = server.schedules.create(weekly_schedule)
            print("Weekly schedule created (ID: {}).".format(weekly_schedule.id))
        except Exception as e:
            print(e)
            options = TSC.RequestOptions()
            options.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "Weekly Schedule")
            )
            schedules, _ = server.schedules.get(req_options=options)
            weekly_schedule = schedules[0]
            print(weekly_schedule)

        # Monthly Schedule
        # This schedule will run on the 15th of every month at 11:30PM
        monthly_interval = TSC.MonthlyInterval(start_time=time(23, 30), interval_value=15)
        monthly_schedule = TSC.ScheduleItem(
            "Monthly-Schedule",
            80,
            TSC.ScheduleItem.Type.Subscription,
            TSC.ScheduleItem.ExecutionOrder.Parallel,
            monthly_interval,
        )
        try:
            monthly_schedule = server.schedules.create(monthly_schedule)
            print("Monthly schedule created (ID: {}).".format(monthly_schedule.id))
        except Exception as e:
            print(e)

        # Now fetch the weekly schedule by id
        fetched_schedule = server.schedules.get_by_id(weekly_schedule.id)
        fetched_interval = fetched_schedule.interval_item
        print("Fetched back our weekly schedule, it shows interval ", fetched_interval)


if __name__ == "__main__":
    main()

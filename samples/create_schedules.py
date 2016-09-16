####
# This script demonstrates how to create schedules using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 2.7.9 or later.
####

import tableauserverclient as TSC
import argparse
import getpass
import logging
from datetime import time

parser = argparse.ArgumentParser(description='Creates sample schedules for each type of frequency.')
parser.add_argument('--server', '-s', required=True, help='server address')
parser.add_argument('--username', '-u', required=True, help='username to sign into server')
parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                    help='desired logging level (set to error by default)')
args = parser.parse_args()

password = getpass.getpass("Password: ")

# Set logging level based on user input, or error by default
logging_level = getattr(logging, args.logging_level.upper())
logging.basicConfig(level=logging_level)

tableau_auth = TSC.TableauAuth(args.username, password)
server = TSC.Server(args.server)
with server.auth.sign_in(tableau_auth):
    # Hourly Schedule
    hourly_interval = TSC.IntervalItem.create_hourly(time(2, 30), time(23, 0), TSC.IntervalItem.Occurrence.Hours, 2)
    hourly_schedule = TSC.ScheduleItem("Hourly-Schedule", 50, TSC.ScheduleItem.Type.Extract,
                                       TSC.ScheduleItem.ExecutionOrder.Parallel, hourly_interval)
    hourly_schedule = server.schedules.create(hourly_schedule)
    print("Hourly schedule created (ID: {}).".format(hourly_schedule.id))

    # Daily Schedule
    daily_interval = TSC.IntervalItem.create_daily(time(5))
    daily_schedule = TSC.ScheduleItem("Daily-Schedule", 60, TSC.ScheduleItem.Type.Subscription,
                                      TSC.ScheduleItem.ExecutionOrder.Serial, daily_interval)
    daily_schedule = server.schedules.create(daily_schedule)
    print("Daily schedule created (ID: {}).".format(daily_schedule.id))

    # Weekly Schedule
    weekly_interval = TSC.IntervalItem.create_weekly(time(19, 15), TSC.IntervalItem.Day.Monday,
                                                     TSC.IntervalItem.Day.Wednesday, TSC.IntervalItem.Day.Friday)
    weekly_schedule = TSC.ScheduleItem("Weekly-Schedule", 70, TSC.ScheduleItem.Type.Extract,
                                       TSC.ScheduleItem.ExecutionOrder.Serial, weekly_interval)
    weekly_schedule = server.schedules.create(weekly_schedule)
    print("Weekly schedule created (ID: {}).".format(weekly_schedule.id))

    # Monthly Schedule
    monthly_interval = TSC.IntervalItem.create_monthly(time(23, 30), 15)
    monthly_schedule = TSC.ScheduleItem("Monthly-Schedule", 80, TSC.ScheduleItem.Type.Subscription,
                                        TSC.ScheduleItem.ExecutionOrder.Parallel, monthly_interval)
    monthly_schedule = server.schedules.create(monthly_schedule)
    print("Monthly schedule created (ID: {}).".format(monthly_schedule.id))

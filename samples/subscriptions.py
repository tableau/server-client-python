####
# This script demonstrates how to create a subscription on a schedule
#
# To run the script, you must have installed Python 3.7 or later.
####


import argparse
import logging

import tableauserverclient as TSC


def usage(args):
    parser = argparse.ArgumentParser(description="Set refresh schedule for a workbook or datasource.")
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
    # Options specific to this sample
    parser.add_argument("schedule", help="The *name* of a schedule to use")

    return parser.parse_args(args)


def create_subscription(schedule: TSC.ScheduleItem, user: TSC.UserItem, target: TSC.Target):
    # Create the new SubscriptionItem object with variables from above.
    new_sub = TSC.SubscriptionItem("My scheduled subscription", schedule.id, user.id, target)

    # (Optional) Set other fields. Any of these can be added or removed.
    new_sub.attach_image = True
    new_sub.attach_pdf = True
    new_sub.message = "An update from Tableau!"
    new_sub.page_orientation = TSC.PDFRequestOptions.Orientation.Portrait
    new_sub.page_size_option = TSC.PDFRequestOptions.PageType.A4
    new_sub.send_if_view_empty = True

    return new_sub


def get_schedule_by_name(server, name):
    schedules = [x for x in TSC.Pager(server.schedules) if x.name == name]
    assert len(schedules) == 1
    return schedules.pop()


def run(args):
    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": False})
    with server.auth.sign_in(tableau_auth):
        target = TSC.Target(server.workbooks.get()[0][0].id, "workbook")
        print(target)
        schedule = get_schedule_by_name(server, args.schedule)
        user = server.users.get_by_id(server.user_id)
        sub_values = create_subscription(schedule, user, target)

        # Create the new subscription on the site you are logged in.
        sub = server.subscriptions.create(sub_values)
        print(sub)


def main():
    import sys

    args = usage(sys.argv[1:])
    run(args)


if __name__ == "__main__":
    main()

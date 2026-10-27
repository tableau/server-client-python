####
# This script creates a Tableau Cloud "On Extract Refresh" subscription:
# a subscription that fires when an extract-refresh schedule completes,
# rather than on the schedule's time trigger. Recipients get the email
# alongside the refresh, so they always see the freshest data.
#
# What it does:
#   1. Sign in.
#   2. Look up the target view or workbook by name.
#   3. List extract-refresh schedules and pick the one you named.
#   4. Build the subscription via SubscriptionItem.on_extract_refresh().
#   5. Call subscriptions.create() and print the new subscription id.
#
# On Tableau Server this same script works as long as the schedule you
# reference is an extract-refresh schedule; the "On Extract Refresh"
# terminology is Cloud-UI-specific but the REST attribute
# (refreshExtractTriggered) is the same on both.
#
# Requires Python 3.10 or later.
####


import argparse
import logging

import tableauserverclient as TSC


def usage(args):
    parser = argparse.ArgumentParser(description="Create an On Extract Refresh subscription for a view or workbook.")
    # Common options; keep in sync across samples.
    parser.add_argument("--server", "-s", required=True, help="server address")
    parser.add_argument("--site", "-S", default="", help="site content URL")
    parser.add_argument("--token-name", "-p", required=True, help="personal access token name")
    parser.add_argument("--token-value", "-v", required=True, help="personal access token value")
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
    )
    # Sample-specific options.
    parser.add_argument("--subject", required=True, help="subscription subject line")
    parser.add_argument("--schedule", required=True, help="name of the extract-refresh schedule to attach to")
    parser.add_argument("--user", required=True, help="username of the subscription recipient")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--view", help="name of the view to send")
    target.add_argument("--workbook", help="name of the workbook to send")
    return parser.parse_args(args)


def _find_one(items, label, name):
    matches = [i for i in items if i.name == name]
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one {label} named {name!r}, found {len(matches)}")
    return matches[0]


def find_extract_refresh_schedule(server, name):
    schedules = [s for s in TSC.Pager(server.schedules) if s.schedule_type == TSC.ScheduleItem.Type.Extract]
    return _find_one(schedules, "extract-refresh schedule", name)


def find_view(server, name):
    return _find_one(list(TSC.Pager(server.views)), "view", name)


def find_workbook(server, name):
    return _find_one(list(TSC.Pager(server.workbooks)), "workbook", name)


def find_user(server, name):
    return _find_one(list(TSC.Pager(server.users)), "user", name)


def run(args):
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(auth):
        schedule = find_extract_refresh_schedule(server, args.schedule)
        user = find_user(server, args.user)
        if args.view:
            content = find_view(server, args.view)
            target = TSC.Target(content.id, "view")
        else:
            content = find_workbook(server, args.workbook)
            target = TSC.Target(content.id, "workbook")

        subscription = TSC.SubscriptionItem.on_extract_refresh(
            subject=args.subject,
            extract_refresh_schedule_id=schedule.id,
            user_id=user.id,
            target=target,
        )
        created = server.subscriptions.create(subscription)
        print(f"Created subscription {created.id}: {created.subject!r} on schedule {schedule.name!r}")


def main():
    import sys

    run(usage(sys.argv[1:]))


if __name__ == "__main__":
    main()

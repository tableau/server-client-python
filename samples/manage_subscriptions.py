####
# This script demonstrates how to list, create, and delete subscriptions
# on a Tableau site.
#
# A subscription pairs a user, a schedule, and a target (workbook or view);
# the user is emailed a snapshot of the target on each schedule tick.
# See the REST API "Subscriptions" reference for full details.
#
# Examples:
#
#   # List every subscription on the site.
#   python samples/manage_subscriptions.py list
#
#   # Create a subscription for the signed-in user against a view + schedule.
#   python samples/manage_subscriptions.py create \
#       --target-type view \
#       --target-id <view_id> \
#       --schedule-id <schedule_id> \
#       --subject "Daily sales snapshot"
#
#   # Create an "On Extract Refresh" subscription (fires when the referenced
#   # extract-refresh schedule completes, rather than on the schedule's time
#   # trigger). --schedule-id must reference an extract-refresh schedule.
#   python samples/manage_subscriptions.py create \
#       --target-type view \
#       --target-id <view_id> \
#       --schedule-id <extract_refresh_schedule_id> \
#       --subject "Snapshot when refresh finishes" \
#       --on-extract-refresh
#
#   # Delete an existing subscription.
#   python samples/manage_subscriptions.py delete --id <subscription_id>
#
# To run the script, you must have installed Python 3.10 or later.
####

import argparse
import logging

import tableauserverclient as TSC

from _shared import add_common_arguments, build_auth, resolve_credentials


def handle_list(server, args):
    """List every subscription on the site, iterating every page."""
    # `server.subscriptions.get()` returns only the first page. Pass the
    # endpoint to TSC.Pager to iterate every subscription without hand-
    # rolling pagination logic.
    count = 0
    for sub in TSC.Pager(server.subscriptions):
        print(
            f"{sub.id}  subject={sub.subject!r}  "
            f"user_id={sub.user_id}  schedule_id={sub.schedule_id}  target={sub.target}"
        )
        count += 1
    if count == 0:
        print("No subscriptions found on this site.")


def handle_create(server, args):
    """Create a new subscription for the signed-in user (unless --user-id given)."""
    user_id = args.user_id or server.user_id
    if not user_id:
        raise SystemExit("Could not determine user_id. Pass --user-id or ensure sign-in succeeded.")

    # The REST API expects lowercase content types ("workbook" or "view").
    target = TSC.Target(args.target_id, args.target_type.lower())

    if args.on_extract_refresh:
        # Extract-refresh-triggered: the subscription fires when the referenced
        # extract-refresh schedule finishes running the refresh. On Tableau
        # Cloud this shows up as schedule type "On Extract Refresh" in the UI.
        # `SubscriptionItem.on_extract_refresh` wires up schedule_id and the
        # refreshExtractTriggered flag together so the server accepts the
        # payload; --schedule-id must reference an extract-refresh schedule.
        new_sub = TSC.SubscriptionItem.on_extract_refresh(
            subject=args.subject,
            extract_refresh_schedule_id=args.schedule_id,
            user_id=user_id,
            target=target,
        )
    else:
        new_sub = TSC.SubscriptionItem(
            subject=args.subject,
            schedule_id=args.schedule_id,
            user_id=user_id,
            target=target,
        )
    if args.message:
        new_sub.message = args.message
    new_sub.attach_image = args.attach_image
    new_sub.attach_pdf = args.attach_pdf

    created = server.subscriptions.create(new_sub)
    trigger = "on-extract-refresh" if args.on_extract_refresh else "on-schedule"
    print(f"Created {trigger} subscription {created.id} " f"for user {created.user_id} against {created.target}")


def handle_delete(server, args):
    """Delete a subscription by ID."""
    server.subscriptions.delete(args.id)
    print(f"Deleted subscription {args.id}.")


def main():
    parser = argparse.ArgumentParser(description="List, create, and delete Tableau subscriptions.")
    add_common_arguments(parser)

    subcommands = parser.add_subparsers(dest="command", required=True)

    list_p = subcommands.add_parser("list", help="List every subscription on the site.")
    list_p.set_defaults(func=handle_list)

    create_p = subcommands.add_parser("create", help="Create a new subscription.")
    create_p.add_argument("--target-type", required=True, choices=["Workbook", "View", "workbook", "view"])
    create_p.add_argument("--target-id", required=True, help="ID of the workbook or view to subscribe to.")
    create_p.add_argument(
        "--schedule-id", required=True, help="ID of the schedule to attach to (see create_schedules.py)."
    )
    create_p.add_argument("--subject", required=True, help="Email subject line.")
    create_p.add_argument("--message", help="Optional email body message.")
    create_p.add_argument(
        "--user-id",
        help="User to subscribe. Defaults to the signed-in user.",
    )
    # BooleanOptionalAction (Python 3.9+) gives us --attach-image / --no-attach-image
    # so users can opt out of the default PNG snapshot. Same for the PDF pair for
    # symmetry, even though its default is False.
    create_p.add_argument(
        "--attach-image",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Attach a PNG snapshot (default: on; pass --no-attach-image to disable).",
    )
    create_p.add_argument(
        "--attach-pdf",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Also attach a PDF snapshot (default: off).",
    )
    create_p.add_argument(
        "--on-extract-refresh",
        action="store_true",
        default=False,
        help=(
            "Fire this subscription when the referenced extract-refresh schedule "
            "completes, rather than on the schedule's time trigger. --schedule-id "
            "must reference an extract-refresh schedule (see create_extract_refresh_"
            "subscription.py for the fully worked example)."
        ),
    )
    create_p.set_defaults(func=handle_create)

    delete_p = subcommands.add_parser("delete", help="Delete a subscription by ID.")
    delete_p.add_argument("--id", required=True, help="Subscription ID to delete.")
    delete_p.set_defaults(func=handle_delete)

    args = parser.parse_args()

    resolve_credentials(args)
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    tableau_auth = build_auth(args)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        args.func(server, args)


if __name__ == "__main__":
    main()

####
# This script demonstrates how to list background jobs on a Tableau site
# and (optionally) wait for a specific job to finish.
#
# Background jobs are created when you run an extract refresh, publish
# asynchronously, run a flow, delete a site asynchronously, and so on.
# See the REST API "Query Jobs" reference for the full list of job types.
#
# Examples:
#
#   # List every job on the site, most recent first.
#   python samples/list_jobs.py
#
#   # Only jobs from the last 24 hours.
#   python samples/list_jobs.py --hours 24
#
#   # Only in-progress refresh_extracts jobs.
#   python samples/list_jobs.py --status InProgress --type refresh_extracts
#
#   # Wait for a specific job to finish.
#   python samples/list_jobs.py --wait <job_id>
#
# To run the script, you must have installed Python 3.9 or later.
####

import argparse
import datetime
import logging

import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import JobCancelledException, JobFailedException

from _shared import add_common_arguments, build_auth, resolve_credentials


def main():
    parser = argparse.ArgumentParser(description="List background jobs on the site, or wait for one to finish.")
    add_common_arguments(parser)

    parser.add_argument(
        "--hours",
        type=int,
        help="Only show jobs created in the last N hours (uses the filter endpoint).",
    )
    parser.add_argument(
        "--status",
        help="Filter by job status, e.g. Success, Failed, InProgress, Cancelled, Pending.",
    )
    parser.add_argument(
        "--type",
        dest="job_type",
        help="Filter by job type, e.g. refresh_extracts, publish, run_flow.",
    )
    parser.add_argument(
        "--wait",
        metavar="JOB_ID",
        help="Instead of listing, wait for the given job ID to complete and print the result.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        help="Max seconds to wait when --wait is used. Defaults to no timeout.",
    )

    args = parser.parse_args()

    resolve_credentials(args)
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    tableau_auth = build_auth(args)
    server = TSC.Server(args.server, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        if args.wait:
            _wait_for_job(server, args.wait, args.timeout)
            return

        _list_jobs(server, args)


def _list_jobs(server, args):
    """List jobs using the queryset filter API, which handles pagination for us."""

    # `server.jobs.filter(...)` returns a QuerySet that is directly iterable
    # and pages through the server automatically. This is the recommended
    # way to iterate every job on the site -- do NOT use a raw
    # `server.jobs.get()`, which only returns the first page.
    query = server.jobs.filter()

    if args.hours is not None:
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=args.hours)
        # Filter operator suffixes: __gt / __gte / __lt / __lte / __in / __has
        # See tableauserverclient.server.query.QuerySet for the full list.
        query = query.filter(created_at__gte=cutoff.isoformat())

    if args.status:
        query = query.filter(status=args.status)

    if args.job_type:
        query = query.filter(job_type=args.job_type)

    # Newest first is usually what a human wants when scanning.
    query = query.order_by("-created_at")

    printed = 0
    for job in query:
        # BackgroundJobItem fields: id, type, status, created_at, started_at, ended_at, ...
        print(
            f"{job.id}  {job.type or '-':<24}  {job.status or '-':<12}  "
            f"created={job.created_at}  ended={job.ended_at}"
        )
        printed += 1

    if printed == 0:
        print("No jobs matched the given filters.")


def _wait_for_job(server, job_id, timeout):
    """Poll a single job until it finishes, using the built-in helper."""
    try:
        job = server.jobs.wait_for_job(job_id, timeout=timeout)
    except JobFailedException as exc:
        # The exception carries the failed JobItem so callers can inspect it.
        print(f"Job {job_id} failed: notes={exc.job.notes}")
        raise SystemExit(1) from exc
    except JobCancelledException:
        print(f"Job {job_id} was cancelled.")
        raise SystemExit(2)

    print(f"Job {job_id} finished. finish_code={job.finish_code}  notes={job.notes}")


if __name__ == "__main__":
    main()

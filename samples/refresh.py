####
# This script demonstrates how to use trigger a refresh on a datasource or workbook
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Trigger a refresh task on a workbook or datasource.")
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
    parser.add_argument("resource_type", choices=["workbook", "datasource"])
    parser.add_argument("resource_id")
    parser.add_argument("--incremental")
    parser.add_argument("--synchronous")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    refresh_type = "FullRefresh"
    incremental = False
    if args.incremental:
        refresh_type = "Incremental"
        incremental = True

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": False})
    with server.auth.sign_in(tableau_auth):
        if args.resource_type == "workbook":
            # Get the workbook by its Id to make sure it exists
            resource = server.workbooks.get_by_id(args.resource_id)
            print(resource)

            # trigger the refresh, you'll get a job id back which can be used to poll for when the refresh is done
            job = server.workbooks.refresh(args.resource_id, incremental=incremental)
        else:
            # Get the datasource by its Id to make sure it exists
            resource = server.datasources.get_by_id(args.resource_id)
            print(resource)

            # server.datasources.create_extract(resource)

            # trigger the refresh, you'll get a job id back which can be used to poll for when the refresh is done
            job = server.datasources.refresh(resource, incremental=incremental)  # by default runs as a sync task,

            print(f"{refresh_type} job posted (ID: {job.id})")
        if args.synchronous:
            # equivalent to tabcmd --synchnronous: wait for the job to complete
            try:
                # `wait_for_job` will throw if the job isn't executed successfully
                print("Waiting for job...")
                server.jobs.wait_for_job(job)
                print("Job finished succesfully")
            except Exception as e:
                print(f"Job failed! {e}")


if __name__ == "__main__":
    main()

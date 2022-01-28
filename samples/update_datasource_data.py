####
# This script demonstrates how to update the data within a published
# live-to-Hyper datasource on server.
#
# The sample is hardcoded against the `World Indicators` dataset and
# expects to receive the LUID of a published datasource containing
# that data. To create such a published datasource, you can use:
#   ./publish_datasource.py --file ../test/assets/World\ Indicators.hyper
# which will print you the LUID of the datasource.
#
# Before running this script, the datasource will contain a region `Europe`.
# After running this script, that region will be gone.
#
####

import argparse
import uuid
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(
        description="Delete the `Europe` region from a published `World Indicators` datasource."
    )
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", required=True, help="server address")
    parser.add_argument("--site", "-S", help="site name")
    parser.add_argument(
        "--token-name", "-p", required=True, help="name of the personal access token used to sign into the server"
    )
    parser.add_argument(
        "--token-value", "-v", required=True, help="value of the personal access token used to sign into the server"
    )
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )
    # Options specific to this sample
    parser.add_argument("datasource_id", help="The LUID of the `World Indicators` datasource")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # We use a unique `request_id` for every request.
        # In case the submission of the update job fails, we won't know wether the job was submitted
        # or not. It could be that the server received the request, changed the data, but then the
        # network connection broke down.
        # If you want to have a way to retry, e.g., inserts while making sure they aren't duplicated,
        # you need to use `request_id` for that purpose.
        # In our case, we don't care about retries. And the delete is idempotent anyway.
        # Hence, we simply use a randomly generated request id.
        request_id = str(uuid.uuid4())

        # This action will delete all rows with `Region=Europe` from the published data source.
        # Other actions (inserts, updates, ...) are also available. For more information see
        # https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_how_to_update_data_to_hyper.htm
        actions = [
            {
                "action": "delete",
                "target-table": "Extract",
                "target-schema": "Extract",
                "condition": {"op": "eq", "target-col": "Region", "const": {"type": "string", "v": "Europe"}},
            }
        ]

        job = server.datasources.update_hyper_data(args.datasource_id, request_id=request_id, actions=actions)

        print(f"Update job posted (ID: {job.id})")
        print("Waiting for job...")
        # `wait_for_job` will throw if the job isn't executed successfully
        job = server.jobs.wait_for_job(job)
        print("Job finished succesfully")


if __name__ == "__main__":
    main()

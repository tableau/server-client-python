####
# This script demonstrates how to query for permissions using TSC
# To run the script, you must have installed Python 3.7 or later.
#
# Example usage: 'python query_permissions.py -s https://10ax.online.tableau.com --site
#       devSite123 -u tabby@tableau.com b4065286-80f0-11ea-af1b-cb7191f48e45'
####

import argparse
import logging
import requests
import json

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Query permissions of a given resource.")
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
    parser.add_argument("resource_id")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        endpoint = server.datasources

        # Get the resource by its ID
        resource = endpoint.get_by_id(args.resource_id)
        print(server)


        url = "https://" + args.server + "/api/v1/vizql-data-service/read-metadata"

        payload = "{\n  \"datasource\": {\n    \"datasourceLuid\": \"" + args.resource_id + "\"\n  },\n  \"options\": {\n    \"debug\": true\n  }\n}"
        headers = {
        'X-Tableau-Auth': server.auth_token,
        'Content-Type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)



if __name__ == "__main__":
    main()



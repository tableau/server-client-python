####
# This script is for smoke testing VizQL Data Service.
# To run the script, you must have installed Python 3.7 or later.
#
# Example usage: 'python vizql_data_service_smoke_test_cap.py  --token-name token 
# --token-value DUCg0rbPROuuAMz9rDI4+Q==:OM2SzwPVK7dNITHo4nfUgsTZvVBQj8iW 
# --server stage-dataplane7.online.vnext.tabint.net 
# --site hbistagedp7 
# --datasouce-luid ebe79f30-bdff-425a-8a9c-3cda79dbbbfd
# --cap 2000'

####

import argparse
import logging
import requests
import json

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Query permissions of a given resource.")
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
    parser.add_argument("--datasource-luid", "-ds", help="The luid of the datasource to query", required=True)
    parser.add_argument("--cap", "-c", type=int, help="The cap on the current cloud site", required=True)

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        url = "https://" + args.server + "/api/v1/vizql-data-service/read-metadata"

        payload = json.dumps({
            "datasource": {
                "datasourceLuid": args.datasource_luid
            },
            "options": {
                "debug": True
            }
        })
        headers = {
            'X-Tableau-Auth': server.auth_token,
            'Content-Type': 'application/json',
        }

        # Test cap limit
        for i in range(args.cap + 1):
            response = requests.post(url, headers=headers, data=payload)
            status_code = response.status_code

            if i < args.cap and status_code != 200:
                response_message = response.text
                exceptionMsg = f"Unexpected status code for call {i + 1}: {status_code} (Expected: 200). Response message: {response_message}";
                raise Exception(exceptionMsg)
            elif i >= args.cap and status_code != 429:
                exceptionMsg = f"Call not rate limited: Unexpected status code for call {i + 1}: {status_code} (Expected: 429)";
                raise Exception(exceptionMsg)

            logging.info(f"Call {i + 1}/{args.cap}: Status Code {status_code}")

        print(f"Completed {args.cap} calls to VizQL Data Service.")



if __name__ == "__main__":
    main()



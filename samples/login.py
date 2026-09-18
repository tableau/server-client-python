####
# This script demonstrates how to log in to Tableau Server Client.
#
# To run the script, you must have installed Python 3.10 or later.
#
# Credentials can be supplied on the command line, from environment variables
# (TABLEAU_SERVER, TABLEAU_SITE, TABLEAU_TOKEN_NAME, TABLEAU_TOKEN_VALUE,
# TABLEAU_USERNAME, TABLEAU_PASSWORD, TABLEAU_JWT, TABLEAU_JWT_FILE), from a
# `.env` file in the current working directory (or samples/, or repo root),
# or interactively via getpass. Prefer env or a .env file over CLI args so
# secrets do not end up in your shell history.
####

import argparse
import logging

import tableauserverclient as TSC

from _shared import add_common_arguments, build_auth, resolve_credentials


# If a sample has additional arguments, then it should copy this code and insert them after the call to
# add_common_arguments. If it has no additional arguments, it can just call this method.
def set_up_and_log_in():
    parser = argparse.ArgumentParser(description="Logs in to the server.")
    add_common_arguments(parser)
    args = parser.parse_args()

    resolve_credentials(args)
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    server = sample_connect_to_server(args)
    print(server.server_info.get())
    print(server.server_address, "site:", server.site_id, "user:", server.user_id)


def sample_connect_to_server(args):
    tableau_auth = build_auth(args)
    if isinstance(tableau_auth, TSC.JWTAuth):
        identifier = "JWT (Connected App)"
    elif isinstance(tableau_auth, TSC.PersonalAccessTokenAuth):
        identifier = f"Token name: {args.token_name}"
    else:
        identifier = f"Username: {args.username}"
    print(f"\nSigning in...\nServer: {args.server}\nSite: {args.site}\n{identifier}")

    # Only set this to False if you are running against a server you trust AND you know why the cert is broken
    check_ssl_certificate = True

    # Make sure we use an updated version of the rest apis, and pass in our cert handling choice
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": check_ssl_certificate})
    server.auth.sign_in(tableau_auth)
    return server


if __name__ == "__main__":
    set_up_and_log_in()

####
# This script demonstrates how to log in to Tableau Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import getpass
import logging
import os

import tableauserverclient as TSC


def get_env(key):
    if key in os.environ:
        return os.environ[key]
    return None


# If a sample has additional arguments, then it should copy this code and insert them after the call to
# sample_define_common_options
# If it has no additional arguments, it can just call this method
def set_up_and_log_in():
    parser = argparse.ArgumentParser(description="Logs in to the server.")
    sample_define_common_options(parser)
    args = parser.parse_args()
    if not args.server:
        args.server = get_env("SERVER")
    if not args.site:
        args.site = get_env("SITE")
    if not args.token_name:
        args.token_name = get_env("TOKEN_NAME")
    if not args.token_value:
        args.token_value = get_env("TOKEN_VALUE")
    args.logging_level = "debug"

    server = sample_connect_to_server(args)
    print(server.server_info.get())
    print(server.server_address, "site:", server.site_id, "user:", server.user_id)


def sample_define_common_options(parser):
    # Common options; please keep these in sync across all samples by copying or calling this method directly
    parser.add_argument("--server", "-s", help="server address")
    parser.add_argument("--site", "-t", help="site name")
    auth = parser.add_mutually_exclusive_group(required=False)
    auth.add_argument("--token-name", "-tn", help="name of the personal access token used to sign into the server")
    auth.add_argument("--username", "-u", help="username to sign into the server")

    parser.add_argument("--token-value", "-tv", help="value of the personal access token used to sign into the server")
    parser.add_argument("--password", "-p", help="value of the password used to sign into the server")
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )


def sample_connect_to_server(args):
    if args.username:
        # Trying to authenticate using username and password.
        password = args.password or getpass.getpass("Password: ")

        tableau_auth = TSC.TableauAuth(args.username, password, site_id=args.site)
        print(f"\nSigning in...\nServer: {args.server}\nSite: {args.site}\nUsername: {args.username}")

    else:
        # Trying to authenticate using personal access tokens.
        token = args.token_value or getpass.getpass("Personal Access Token: ")

        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name=args.token_name, personal_access_token=token, site_id=args.site
        )
        print(f"\nSigning in...\nServer: {args.server}\nSite: {args.site}\nToken name: {args.token_name}")

    if not tableau_auth:
        raise TabError("Did not create authentication object. Check arguments.")

    # Only set this to False if you are running against a server you trust AND you know why the cert is broken
    check_ssl_certificate = True

    # Make sure we use an updated version of the rest apis, and pass in our cert handling choice
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": check_ssl_certificate})
    server.auth.sign_in(tableau_auth)
    server.version = "3.19"

    return server


if __name__ == "__main__":
    set_up_and_log_in()

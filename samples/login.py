####
# This script demonstrates how to log in to Tableau Server Client.
#
# To run the script, you must have installed Python 3.6 or later.
####

import argparse
from contextlib import nullcontext
import getpass
import logging
import enum

import tableauserverclient as TSC

# from tableauserverclient.models import json_web_token_auth

# If a sample has additional arguments, then it should copy this code and insert them after the call to
# sample_define_common_options
# If it has no additional arguments, it can just call this method
def set_up_and_log_in():
    parser = argparse.ArgumentParser(description="Logs in to the server.")
    sample_define_common_options(parser)
    args = parser.parse_args()

    # Set logging level based on user input, or error by default.
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    server = sample_connect_to_server(args)
    print(server.server_info.get())
    print(server.server_address, "site:", server.site_id, "user:", server.user_id)


def sample_define_common_options(parser):
    # Common options; please keep these in sync across all samples by copying or calling this method directly
    parser.add_argument("--server", "-s", required=True, help="server address")
    parser.add_argument("--site", "-t", help="site name")
    auth = parser.add_mutually_exclusive_group(required=False)
    auth.add_argument("--token-name", "-tn", help="name of the personal access token used to sign into the server")
    auth.add_argument("--username", "-u", help="username to sign into the server")

    parser.add_argument("--token-value", "-tv", help="value of the personal access token used to sign into the server")
    parser.add_argument("--password", "-p", help="value of the password used to sign into the server")
    parser.add_argument("--jwt", "-j", help="sigin in using json web token")

    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )


def sample_connect_to_server(args):

    credential = getSingleCredentialType(args)

    if credential == credentialType.PAT:
        # Trying to authenticate using personal access tokens.
        token = args.token_value or getpass.getpass("Personal Access Token: ")

        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name=args.token_name, personal_access_token=token, site_id=args.site
        )
        print("\nSigning in...\nServer: {}\nSite: {}\nToken name: {}".format(args.server, args.site, args.token_name))
    elif credential == credentialType.JWT:
        # Trying to authenticate using json web tokens.
        tableau_auth = TSC.JsonWebTokenAuth(json_web_token_auth=args.jwt, site_id=args.site)
        print("\nSigning in...\nServer: {}\nSite: {}\nToken name: {}".format(args.server, args.site, args.token_name))

    elif credential == credentialType.USERNAMEANDPASSWORD:
        # Trying to authenticate using username and password.
        password = args.password or getpass.getpass("Password: ")

        tableau_auth = TSC.TableauAuth(args.username, password, site_id=args.site)
        print("\nSigning in...\nServer: {}\nSite: {}\nUsername: {}".format(args.server, args.site, args.username))
    else:
        raise TabError("Did not create authentication object. Check arguments.")

    # Only set this to False if you are running against a server you trust AND you know why the cert is broken
    check_ssl_certificate = False

    # Make sure we use an updated version of the rest apis, and pass in our cert handling choice
    server = TSC.Server(args.server, use_server_version=True)
    server.auth.sign_in(tableau_auth)
    print("Logged in successfully")

    return server


def getSingleCredentialType(args):
    credential = nullcontext
    credentialCount = 0

    if args.username:
        credentialCount += 1
        credential = credentialType.USERNAMEANDPASSWORD

    if args.jwt:
        credentialCount += 1
        credential = credentialType.JWT

    if args.token_name:
        credentialCount += 1
        credential = credentialType.PAT

    if credentialCount == 0:
        raise TabError("The credential is empty in the request")
    elif credentialCount > 1:
        raise TabError("The request contains two or more different types of credentials")
    return credential


class credentialType(enum.Enum):
    PAT = 1
    JWT = 2
    USERNAMEANDPASSWORD = 3


if __name__ == "__main__":
    set_up_and_log_in()

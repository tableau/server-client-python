####
# This script demonstrates how to create a user using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####


import argparse
import logging
import os
import sys
from typing import Sequence

import tableauserverclient as TSC


def parse_args(args: Sequence[str] | None) -> argparse.Namespace:
    """
    Parse command line parameters
    """
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Creates a sample user group.")
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
    # This sample has no additional options, yet. If you add some, please add them here
    parser.add_argument("--role", "-r", help="Site Role for the new user", default="Unlicensed")
    parser.add_argument(
        "--user",
        "-u",
        help="Username for the new user. If using active directory, it should be in the format of SAMAccountName@FullyQualifiedDomainName",
    )
    parser.add_argument(
        "--email", "-e", help="Email address of the new user. If using active directory, this field is optional."
    )

    return parser.parse_args(args)


def main():
    args = parse_args(None)

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": False})
    with server.auth.sign_in(tableau_auth):
        # this code shows 2 different error codes for common mistakes
        # 400013: Invalid site role
        # 409000: user already exists on site

        user = TSC.UserItem(args.user, args.role)
        if args.email:
            user.email = args.email
        user = server.users.add(user)


if __name__ == "__main__":
    main()

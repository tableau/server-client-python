####
# This script demonstrates how to create a group using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####


import argparse
import logging
import os

from datetime import time
from typing import List

import tableauserverclient as TSC
from tableauserverclient import ServerResponseError


def main():

    parser = argparse.ArgumentParser(description="Creates a sample user group.")
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
    # This sample has no additional options, yet. If you add some, please add them here
    parser.add_argument("--file", help="csv file containing user info", required=False)
    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": False})
    with server.auth.sign_in(tableau_auth):
        # this code shows 3 different error codes that mean "resource is already in collection"
        # 409009: group already exists on server
        # 409107: user is already on site
        # 409011: user is already in group

        group = TSC.GroupItem("test")
        try:
            group = server.groups.create(group)
        except TSC.server.endpoint.exceptions.ServerResponseError as rError:
            if rError.code == "409009":
                print("Group already exists")
                group = server.groups.filter(name=group.name)[0]
            else:
                raise rError
        server.groups.populate_users(group)
        for user in group.users:
            print(user.name)

        if args.file:
            filepath = os.path.abspath(args.file)
            print("Add users to site from file {}:".format(filepath))
            added: List[TSC.UserItem]
            failed: List[TSC.UserItem, TSC.ServerResponseError]
            added, failed = server.users.create_from_file(filepath)
            for user, error in failed:
                print(user, error.code)
                if error.code == "409017":
                    user = server.users.filter(name=user.name)[0]
                    added.append(user)
            print("Adding users to group:{}".format(added))
            for user in added:
                print("Adding user {}".format(user))
                try:
                    server.groups.add_user(group, user.id)
                except ServerResponseError as serverError:
                    if serverError.code == "409011":
                        print("user {} is already a member of group {}".format(user.name, group.name))
                    else:
                        raise rError

        for user in group.users:
            print(user.name)


if __name__ == "__main__":
    main()

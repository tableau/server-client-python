####
# This script demonstrates how to use the Tableau Server Client
# to interact with sites.
####

import argparse
import logging
import os.path
import sys

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Explore site updates by the Server API.")
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

    parser.add_argument("--delete")
    parser.add_argument("--create")
    parser.add_argument("--url")
    parser.add_argument("--new_site_name")
    parser.add_argument("--user_quota")
    parser.add_argument("--storage_quota")
    parser.add_argument("--status")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    new_site = None
    with server.auth.sign_in(tableau_auth):
        current_site = server.sites.get_by_id(server.site_id)

        if args.delete:
            print("You can only delete the site you are currently in")
            print("Delete site `{}`?".format(current_site.name))
            # server.sites.delete(server.site_id)

        elif args.create:
            new_site = TSC.SiteItem(args.create, args.url or args.create)
            site_item = server.sites.create(new_site)
            print(site_item)
            # to do anything further with the site, you need to log into it
            # if a PAT is required, that means going to the UI to create one

        else:
            new_site = current_site
            print(current_site, "current user quota:", current_site.user_quota)
            print("Remember, you can only update the site you are currently in")
            if args.url:
                new_site.content_url = args.url
            if args.user_quota:
                new_site.user_quota = args.user_quota
            try:
                updated_site = server.sites.update(new_site)
                print(updated_site, "new user quota:", updated_site.user_quota)
            except TSC.ServerResponseError as e:
                print(e)


if __name__ == "__main__":
    main()

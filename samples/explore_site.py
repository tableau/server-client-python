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

    parser.add_argument("--delete")
    parser.add_argument("--create")
    parser.add_argument("--url")
    parser.add_argument("--new_site_name")
    parser.add_argument("--user_quota")
    parser.add_argument("--storage_quota")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    print("Logging into `{}`".format(args.site))
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        current_site = server.sites.get_by_id(server.site_id)
        print(current_site)
        current_site = server.sites.get_by_content_url(args.site)
        print(current_site)
        current_site = server.sites.get_by_name(current_site.name)
        print(current_site)

        if args.delete:
            print("Warning: You are deleting the site you are currently in")
            server.sites.delete(server.site_id)

        elif args.create:
            new_site = TSC.SiteItem(args.create, args.url or args.create)
            site_item = server.sites.create(new_site)
            print(site_item)
            # to do anything further with the site, you need to log into it
            # if a PAT is required, that means going to the UI to create one

        else:
            print("Updating site...")
            new_site = current_site
            if args.user_quota:
                new_site.user_quota = args.user_quota
            if args.url:
                new_site.content_url = args.url
            else:
                new_site.content_url = current_site.content_url + "_updated"
            if args.new_site_name:
                new_site.name = args.new_site_name
            if args.storage_quota:
                new_site.storage_quota = args.storage_quota
            try:
                updated_site = server.sites.update(new_site)
                print(updated_site)
                if args.user_quota:
                    print(updated_site, "new user quota:", updated_site.user_quota)
            except TSC.ServerResponseError as e:
                print(e)


if __name__ == "__main__":
    main()

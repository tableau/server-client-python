####
# This script demonstrates how to filter and sort groups using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####


import argparse
import logging
import urllib.parse

import tableauserverclient as TSC


def create_example_group(group_name="Example Group", server=None):
    new_group = TSC.GroupItem(group_name)
    try:
        new_group = server.groups.create(new_group)
        print("Created a new project called: '%s'" % group_name)
        print(new_group)
    except TSC.ServerResponseError:
        print("Group '%s' already existed" % group_name)


def main():
    parser = argparse.ArgumentParser(description="Filter and sort groups.")
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

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": False})
    with server.auth.sign_in(tableau_auth):
        group_name = "SALES NORTHWEST"
        # Try to create a group named "SALES NORTHWEST"
        create_example_group(group_name, server)

        group_name = "SALES ROMANIA"
        # Try to create a group named "SALES ROMANIA"
        create_example_group(group_name, server)

        # we no longer need to encode the space
        options = TSC.RequestOptions()
        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, group_name))

        filtered_groups, _ = server.groups.get(req_options=options)
        # Result can either be a matching group or an empty list
        if filtered_groups:
            group = filtered_groups.pop()
            print(group)
        else:
            error = f"No group named '{group_name}' found"
            print(error)

        print("---")

        # Or, try the above with the django style filtering
        try:
            group = server.groups.filter(name=group_name)[0]
            print(group)
        except IndexError:
            print(f"No group named '{group_name}' found")

        print("====")

        options = TSC.RequestOptions()
        options.filter.add(
            TSC.Filter(
                TSC.RequestOptions.Field.Name,
                TSC.RequestOptions.Operator.In,
                ["SALES NORTHWEST", "SALES ROMANIA", "this_group"],
            )
        )

        options.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Desc))

        matching_groups, pagination_item = server.groups.get(req_options=options)
        print("Filtered groups are:")
        for group in matching_groups:
            print(group.name)

        print("----")
        # or, try the above with the django style filtering.
        all_g = server.groups.all()
        print(f"Searching locally among {all_g.total_available} groups")
        for a in all_g:
            print(a)
        groups = [urllib.parse.quote_plus(group) for group in ["SALES NORTHWEST", "SALES ROMANIA", "this_group"]]
        print(groups)

        for group in server.groups.filter(name__in=groups).order_by("-name"):
            print(group.name)

        print("done")


if __name__ == "__main__":
    main()

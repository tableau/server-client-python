# This script demonstrates how to get all favorites, or add/delete a favorite.

import argparse
import logging
import tableauserverclient as TSC
from tableauserverclient.models import Resource


def main():
    parser = argparse.ArgumentParser(description="Explore favoriting functions supported by the Server API.")
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

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        print(server)
        my_workbook = None
        my_view = None
        my_datasource = None

        # get all favorites on site for the logged on user
        user: TSC.UserItem = TSC.UserItem()
        user.id = server.user_id
        print(f"Favorites for user: {user.id}")
        server.favorites.get(user)
        print(user.favorites)

        # get list of workbooks
        all_workbook_items, pagination_item = server.workbooks.get()
        if all_workbook_items is not None and len(all_workbook_items) > 0:
            my_workbook = all_workbook_items[0]
            server.favorites.add_favorite(user, Resource.Workbook, all_workbook_items[0])
            print(
                "Workbook added to favorites. Workbook Name: {}, Workbook ID: {}".format(
                    my_workbook.name, my_workbook.id
                )
            )
            views = server.workbooks.populate_views(my_workbook)
            if views is not None and len(views) > 0:
                my_view = views[0]
                server.favorites.add_favorite_view(user, my_view)
                print(f"View added to favorites. View Name: {my_view.name}, View ID: {my_view.id}")

        all_datasource_items, pagination_item = server.datasources.get()
        if all_datasource_items:
            my_datasource = all_datasource_items[0]
        server.favorites.add_favorite_datasource(user, my_datasource)
        print(
            "Datasource added to favorites. Datasource Name: {}, Datasource ID: {}".format(
                my_datasource.name, my_datasource.id
            )
        )

    server.favorites.delete_favorite_workbook(user, my_workbook)
    print(f"Workbook deleted from favorites. Workbook Name: {my_workbook.name}, Workbook ID: {my_workbook.id}")

    server.favorites.delete_favorite_view(user, my_view)
    print(f"View deleted from favorites. View Name: {my_view.name}, View ID: {my_view.id}")

    server.favorites.delete_favorite_datasource(user, my_datasource)
    print(
        "Datasource deleted from favorites. Datasource Name: {}, Datasource ID: {}".format(
            my_datasource.name, my_datasource.id
        )
    )

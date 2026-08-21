# This script demonstrates how to get all favorites, or add/delete a favorite.

import argparse
import logging
import tableauserverclient as TSC
from tableauserverclient.models import Resource

from _shared import add_common_arguments, build_auth, resolve_credentials


def main():
    parser = argparse.ArgumentParser(description="Explore favoriting functions supported by the Server API.")
    add_common_arguments(parser)

    args = parser.parse_args()

    resolve_credentials(args)
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    tableau_auth = build_auth(args)
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

        # get list of workbooks. `.get()` only returns one page; use
        # TSC.Pager to iterate every workbook on the site.
        all_workbook_items = list(TSC.Pager(server.workbooks))
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

        all_datasource_items = list(TSC.Pager(server.datasources))
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

    if my_datasource is not None:
        server.favorites.delete_favorite_datasource(user, my_datasource)
        print(
            "Datasource deleted from favorites. Datasource Name: {}, Datasource ID: {}".format(
                my_datasource.name, my_datasource.id
            )
        )

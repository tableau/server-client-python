# This script demonstrates how to get all favorites, or add/delete a favorite. 
# favorites_item and favorites_endpoint may be updated
# these method examples were made prior to any updates to the favorites code

import argparse
import logging
import tableauserverclient as TSC

def main():

    parser = argparse.ArgumentParser(description="Explore datasource functions supported by the Server API.")
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", required = True, help = "server address")
    parser.add_argument("--site", "-S", help = "site name")
    parser.add_argument(
        "--token-name", "-p", required = True, help = "name of the personal access token used to sign into the server"
    )
    parser.add_argument(
        "--token-value", "-v", required = True, help = "value of the personal access token used to sign into the server"
    )
    parser.add_argument(
        "--logging-level",
        "-l",
        choices = ["debug", "info", "error"],
        default = "error",
        help = "desired logging level (set to error by default)",
    )
    
    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level = logging_level)

    # SIGN IN
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id = args.site)
    server = TSC.Server(args.server, use_server_version = True)
    with server.auth.sign_in(tableau_auth):

        def get(self, user_item: "UserItem", req_options: Optional["RequestOptions"] = None) -> None:
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # get all favorites on site
            print("Getting all favorites for user: {}".format(user.id))
            server.favorites.get(user)
            # return favorites
            print("Favorites for user: {}".format(user.id))
            print(user.favorites)

        def add_favorite_workbook(self, user_item: "UserItem", workbook_item: "WorkbookItem") -> None:
            # get list of workbooks
            all_workbook_items, pagination_item = server.workbooks.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # add to favorites 
            if all_workbook_items:
                my_workbook = all_workbook_items[0]
            add_workbook = server.favorites.add_favorite_workbook(user, my_workbook)
            print("Workbook added to favorites. Workbook Name: {}, Workbook ID: {}".format(my_workbook.name, my_workbook.id))

        def add_favorite_view(self, user_item: "UserItem", view_item: "ViewItem") -> None:
            # get list of views
            all_view_items, pagination_item = server.views.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # add to favorites
            if all_view_items:
                my_view = all_view_items[0]
            add_view = server.favorites.add_favorite_view(user, my_view)
            print("View added to favorites. View Name: {}, View ID: {}".format(my_view.name, my_view.id))

        def add_favorite_datasource(self, user_item: "UserItem", datasource_item: "DatasourceItem") -> None:
            # get list of datasources
            all_datasource_items, pagination_item = server.datasources.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # add to favorites
            if all_datasource_items:
                my_datasource = all_datasource_items[0]
            add_datasource = server.favorites.add_favorite_datasource(user, my_datasource)
            print("Datasource added to favorites. Datasource Name: {}, Datasource ID: {}".format(my_datasource.name, my_datasource.id))

        def add_favorite_project(self, user_item: "UserItem", project_item: "ProjectItem") -> None:
            # get list of projects
            all_project_items, pagination_item = server.projects.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # add to favorites
            if all_project_items:
                my_project = all_project_items[0]
            add_project = server.favorites.add_favorite_project(user, my_project)
            print("Project added to favorites. Project Name: {}, Project ID: {}".format(my_project.name, my_project.id))

        def add_favorite_flow(self, user_item: "UserItem", flow_item: "FlowItem") -> None:
            # get list of flows
            all_flow_items, pagination_item = server.flows.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # add to favorites
            if all_flow_items:
                my_flow = all_flow_items[0]
            add_flow = server.favorites.add_favorite_flow(user, my_flow)
            print("Flow added to favorites. Flow Name: {}, Flow ID: {}".format(my_flow.name, my_flow.id))

        def delete_favorite_workbook(self, user_item: "UserItem", workbook_item: "WorkbookItem") -> None:
            # get list of workbooks
            all_workbook_items, pagination_item = server.workbooks.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # delete from favorites 
            if all_workbook_items:
                my_workbook = all_workbook_items[0]
            delete_workbook = server.favorites.delete_favorite_workbook(user, my_workbook)
            print("Workbook deleted from favorites. Workbook Name: {}, Workbook ID: {}".format(my_workbook.name, my_workbook.id))

        def delete_favorite_view(self, user_item: "UserItem", view_item: "ViewItem") -> None:
            # get list of views
            all_view_items, pagination_item = server.views.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # delete from favorites
            if all_view_items:
                my_view = all_view_items[0]
            delete_view = server.favorites.delete_favorite_view(user, my_view)
            print("View deleted from favorites. View Name: {}, View ID: {}".format(my_view.name, my_view.id))

        def delete_favorite_datasource(self, user_item: "UserItem", datasource_item: "DatasourceItem") -> None:
            # get list of datasources
            all_datasource_items, pagination_item = server.datasources.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # delete from favorites
            if all_datasource_items:
                my_datasource = all_datasource_items[0]
            delete_datasource = server.favorites.delete_favorite_datasource(user, my_datasource)
            print("Datasource deleted from favorites. Datasource Name: {}, Datasource ID: {}".format(my_datasource.name, my_datasource.id))
        
        def delete_favorite_project(self, user_item: "UserItem", project_item: "ProjectItem") -> None:
            # get list of projects
            all_project_items, pagination_item = server.projects.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # delete from favorites favorites
            if all_project_items:
                my_project = all_project_items[0]
            delete_project = server.favorites.delete_favorite_project(user, my_project)
            print("Project deleted from favorites. Project Name: {}, Project ID: {}".format(my_project.name, my_project.id))

        def delete_favorite_flow(self, user_item: "UserItem", flow_item: "FlowItem") -> None:
            # get list of flows
            all_flow_items, pagination_item = server.flows.get()
            # specify user
            user = server.users.get_by_id('96d4fd52-5169-4de5-hapa-fe90fae2018p')
            # delete from favorites
            if all_flow_items:
                my_flow = all_flow_items[0]
            delete_flow = server.favorites.delete_favorite_flow(user, my_flow)
            print("Flow deleted from favorites. Flow Name: {}, Flow ID: {}".format(my_flow.name, my_flow.id))
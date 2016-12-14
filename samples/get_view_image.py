####
# This script demonstrates how to use the Tableau Server Client
# to query a high resolution image of a view from Tableau Server.
#
# For more information, refer to the documentations on 'Query View Image'
# (https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm)
#
# To run the script, you must have installed Python 2.7.X or 3.3 and later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Query View Image From Server')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--view-name', '-v', required=True, help='name of view')
    parser.add_argument('--filepath', '-f', required=True, help='filepath to save the image returned')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)
    server.version = 2.5

    with server.auth.sign_in(tableau_auth):

        # Step 2: Get all the projects on server, then look for the default one.
        all_projects, pagination_item = server.projects.get()
        default_project = next((project for project in all_projects if project.is_default()), None)

        # Step 3: If default project is found, download the image for the specified view name
        if default_project is not None:
            req_option = TSC.RequestOptions()
            req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                             TSC.RequestOptions.Operator.Equals, args.view_name))
            all_views, pagination_item = server.views.get(req_option)
            view_item = all_views[0]
            image_req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High)
            server.views.populate_image(view_item, image_req_option)

            with open(args.filepath, "wb") as image_file:
                image_file.write(view_item.image)

            print("View image saved to {0}".format(args.filepath))
        else:
            error = "The default project could not be found."
            raise LookupError(error)


if __name__ == '__main__':
    main()

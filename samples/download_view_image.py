####
# This script demonstrates how to use the Tableau Server Client
# to download a high resolution image of a view from Tableau Server.
#
# For more information, refer to the documentations on 'Query View Image'
# (https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm)
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Download image of a specified view.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site-id', '-si', required=False,
                        help='content url for site the view is on')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--view-name', '-v', required=True,
                        help='name of view to download an image of')
    parser.add_argument('--filepath', '-f', required=True, help='filepath to save the image returned')
    parser.add_argument('--maxage', '-m', required=False, help='max age of the image in the cache in minutes.')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    site_id = args.site_id
    if not site_id:
        site_id = ""
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_id)
    server = TSC.Server(args.server)
    # The new endpoint was introduced in Version 2.5
    server.version = "2.5"

    with server.auth.sign_in(tableau_auth):
        # Step 2: Query for the view that we want an image of
        req_option = TSC.RequestOptions()
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                         TSC.RequestOptions.Operator.Equals, args.view_name))
        all_views, pagination_item = server.views.get(req_option)
        if not all_views:
            raise LookupError("View with the specified name was not found.")
        view_item = all_views[0]

        max_age = args.maxage
        if not max_age:
            max_age = 1

        image_req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High,
                                                   maxage=max_age)
        server.views.populate_image(view_item, image_req_option)

        with open(args.filepath, "wb") as image_file:
            image_file.write(view_item.image)

        print("View image saved to {0}".format(args.filepath))


if __name__ == '__main__':
    main()

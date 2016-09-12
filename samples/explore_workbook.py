####
# This script demonstrates how to use the Tableau Server API
# to interact with workbooks. It explores the different
# functions that the Server API supports on workbooks.
#
# With no flags set, this sample will query all workbooks,
# pick one workbook and populate its connections/views, and update
# the workbook. Adding flags will demonstrate the specific feature
# on top of the general operations.
####

import tableauserverclient as TSC
import os.path
import copy
import argparse
import getpass
import logging

parser = argparse.ArgumentParser(description='Explore workbook functions supported by the Server API.')
parser.add_argument('--server', '-s', required=True, help='server address')
parser.add_argument('--username', '-u', required=True, help='username to sign into server')
parser.add_argument('--publish', '-p', metavar='FILEPATH', help='path to workbook to publish')
parser.add_argument('--download', '-d', metavar='FILEPATH', help='path to save downloaded workbook')
parser.add_argument('--preview-image', '-i', metavar='FILENAME',
                    help='filename (a .png file) to save the preview image')
parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                    help='desired logging level (set to error by default)')
args = parser.parse_args()

password = getpass.getpass("Password: ")

# Set logging level based on user input, or error by default
logging_level = getattr(logging, args.logging_level.upper())
logging.basicConfig(level=logging_level)

# SIGN IN
tableau_auth = TSC.TableauAuth(args.username, password)
server = TSC.Server(args.server)
with server.auth.sign_in(tableau_auth):

    # Publish workbook if publish flag is set (-publish, -p)
    if args.publish:
        pagination_info, all_projects = server.projects.get()
        default_project = next((project for project in all_projects if project.is_default()), None)

        if default_project is not None:
            new_workbook = TSC.WorkbookItem(default_project.id)
            new_workbook = server.workbooks.publish(new_workbook, args.publish, server.PublishMode.Overwrite)
            print("Workbook published. ID: {}".format(new_workbook.id))
        else:
            print('Publish failed. Could not find the default project.')

    # Gets all workbook items
    pagination_item, all_workbooks = server.workbooks.get()
    print("\nThere are {} workbooks on site: ".format(pagination_item.total_available))
    print([workbook.name for workbook in all_workbooks])

    if all_workbooks:
        # Pick one workbook from the list
        sample_workbook = all_workbooks[0]

        # Populate views
        server.workbooks.populate_views(sample_workbook)
        print("\nName of views in {}: ".format(sample_workbook.name))
        print([view.name for view in sample_workbook.views])

        # Populate connections
        server.workbooks.populate_connections(sample_workbook)
        print("\nConnections for {}: ".format(sample_workbook.name))
        print(["{0}({1})".format(connection.id, connection.datasource_name)
               for connection in sample_workbook.connections])

        # Update tags and show_tabs flag
        original_tag_set = copy.copy(sample_workbook.tags)
        sample_workbook.tags.update('a', 'b', 'c', 'd')
        sample_workbook.show_tabs = True
        server.workbooks.update(sample_workbook)
        print("\nOld tag set: {}".format(original_tag_set))
        print("New tag set: {}".format(sample_workbook.tags))
        print("Workbook tabbed: {}".format(sample_workbook.show_tabs))

        # Delete all tags that were added by setting tags to original
        sample_workbook.tags = original_tag_set
        server.workbooks.update(sample_workbook)

        if args.download:
            # Download
            path = server.workbooks.download(sample_workbook.id, args.download)
            print("\nDownloaded workbook to {}".format(path))

        if args.preview_image:
            # Populate workbook preview image
            server.workbooks.populate_preview_image(sample_workbook)
            with open(args.preview_image, 'wb') as f:
                f.write(sample_workbook.preview_image)
            print("\nDownloaded preview image of workbook to {}".format(os.path.abspath(args.preview_image)))

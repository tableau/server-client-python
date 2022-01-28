####
# This script demonstrates how to use the Tableau Server Client
# to interact with workbooks. It explores the different
# functions that the Server API supports on workbooks.
#
# With no flags set, this sample will query all workbooks,
# pick one workbook and populate its connections/views, and update
# the workbook. Adding flags will demonstrate the specific feature
# on top of the general operations.
####

import argparse
import logging
import os.path

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description="Explore workbook functions supported by the Server API.")
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
    parser.add_argument("--publish", metavar="FILEPATH", help="path to workbook to publish")
    parser.add_argument("--download", metavar="FILEPATH", help="path to save downloaded workbook")
    parser.add_argument(
        "--preview-image", "-i", metavar="FILENAME", help="filename (a .png file) to save the preview image"
    )

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):

        # Publish workbook if publish flag is set (-publish, -p)
        overwrite_true = TSC.Server.PublishMode.Overwrite
        if args.publish:
            all_projects, pagination_item = server.projects.get()
            default_project = next((project for project in all_projects if project.is_default()), None)

            if default_project is not None:
                new_workbook = TSC.WorkbookItem(default_project.id)
                new_workbook = server.workbooks.publish(new_workbook, args.publish, overwrite_true)
                print("Workbook published. ID: {}".format(new_workbook.id))
            else:
                print("Publish failed. Could not find the default project.")

        # Gets all workbook items
        all_workbooks, pagination_item = server.workbooks.get()
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
            print(
                [
                    "{0}({1})".format(connection.id, connection.datasource_name)
                    for connection in sample_workbook.connections
                ]
            )

            # Update tags and show_tabs flag
            original_tag_set = set(sample_workbook.tags)
            sample_workbook.tags.update("a", "b", "c", "d")
            sample_workbook.show_tabs = True
            server.workbooks.update(sample_workbook)
            print("\nWorkbook's old tag set: {}".format(original_tag_set))
            print("Workbook's new tag set: {}".format(sample_workbook.tags))
            print("Workbook tabbed: {}".format(sample_workbook.show_tabs))

            # Delete all tags that were added by setting tags to original
            sample_workbook.tags = original_tag_set
            server.workbooks.update(sample_workbook)

            # Add tag to just one view
            sample_view = sample_workbook.views[0]
            original_tag_set = set(sample_view.tags)
            sample_view.tags.add("view_tag")
            server.views.update(sample_view)
            print("\nView's old tag set: {}".format(original_tag_set))
            print("View's new tag set: {}".format(sample_view.tags))

            # Delete tag from just one view
            sample_view.tags = original_tag_set
            server.views.update(sample_view)

            if args.download:
                # Download
                path = server.workbooks.download(sample_workbook.id, args.download)
                print("\nDownloaded workbook to {}".format(path))

            if args.preview_image:
                # Populate workbook preview image
                server.workbooks.populate_preview_image(sample_workbook)
                with open(args.preview_image, "wb") as f:
                    f.write(sample_workbook.preview_image)
                print("\nDownloaded preview image of workbook to {}".format(os.path.abspath(args.preview_image)))


if __name__ == "__main__":
    main()

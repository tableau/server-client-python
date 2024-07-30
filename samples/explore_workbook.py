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
    parser.add_argument("--publish", metavar="FILEPATH", help="path to workbook to publish")
    parser.add_argument("--download", metavar="FILEPATH", help="path to save downloaded workbook")
    parser.add_argument(
        "--preview-image", "-i", metavar="FILENAME", help="filename (a .png file) to save the preview image"
    )
    parser.add_argument(
        "--powerpoint", "-ppt", metavar="FILENAME", help="filename (a .ppt file) to save the powerpoint deck"
    )
    parser.add_argument("--id", help="specific workbook luid to use")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True, http_options={'verify': False})
    with server.auth.sign_in(tableau_auth):
        # Publish workbook if publish flag is set (-publish, -p)
        overwrite_true = TSC.Server.PublishMode.Overwrite
        if args.publish:
            all_projects, pagination_item = server.projects.get()
            default_project = next((project for project in all_projects if project.is_default()), None)

            if default_project is not None:
                new_workbook = TSC.WorkbookItem(default_project.id)
                new_workbook = server.workbooks.publish(new_workbook, args.publish, overwrite_true)
                print(f"Workbook published. ID: {new_workbook.id}")
            else:
                print("Publish failed. Could not find the default project.")


        # Gets all workbook items
        all_workbooks, pagination_item = server.workbooks.get()
        print(f"\nThere are {pagination_item.total_available} workbooks on site: ")
        print([workbook.name for workbook in all_workbooks])

        if all_workbooks:
            # Pick one workbook from the list
            if args.id:
                sample_workbook = server.workbooks.get_by_id(args.id)
            else:
                sample_workbook = all_workbooks[0]
            """
            sample_workbook.name = "Name me something cooler"
            sample_workbook.description = "That doesn't work"
            updated: TSC.WorkbookItem = server.workbooks.update(sample_workbook)
            print(updated.name, updated.description)
            """
            
            # Populate views
            server.workbooks.populate_views(sample_workbook)
            print(f"\nName of views in {sample_workbook.name}: ")
            print([view.name for view in sample_workbook.views])

            """_summary_
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
            print(f"\nWorkbook's old tag set: {original_tag_set}")
            print(f"Workbook's new tag set: {sample_workbook.tags}")
            print(f"Workbook tabbed: {sample_workbook.show_tabs}")

            # Delete all tags that were added by setting tags to original
            sample_workbook.tags = original_tag_set
            server.workbooks.update(sample_workbook)

            # Add tag to just one view
            sample_view = sample_workbook.views[0]
            original_tag_set = set(sample_view.tags)
            sample_view.tags.add("view_tag")
            server.views.update(sample_view)
            print(f"\nView's old tag set: {original_tag_set}")
            print(f"View's new tag set: {sample_view.tags}")

            # Delete tag from just one view
            sample_view.tags = original_tag_set
            server.views.update(sample_view)

            if args.download:
                # Download
                path = server.workbooks.download(sample_workbook.id, args.download)
                print(f"\nDownloaded workbook to {path}")

            if args.preview_image:
                # Populate workbook preview image
                server.workbooks.populate_preview_image(sample_workbook)
                with open(args.preview_image, "wb") as f:
                    f.write(sample_workbook.preview_image)
                print(f"\nDownloaded preview image of workbook to {os.path.abspath(args.preview_image)}")
             """
            # get custom views
            cvs, _ = server.custom_views.get()

            my_custom_view = None
            if len(cvs) > 0:
                print("Custom views:")
                for c in cvs:
                    print(c)
                    
                my_custom_view = c
                print(my_custom_view.id)

                # for the first custom view in the list

                # update the name
                # note that this will fail if the name is already changed to this value
                """_summary_
                changed = TSC.CustomViewItem(id=my_custom_view.id, name="I was again changed by tsc")
                verified_change = server.custom_views.update(changed)
                print("Change name of the custom view:")
                print(verified_change)
                """
    

                # export as image. Filters etc could be added here as usual
                server.custom_views.populate_image(my_custom_view)
                filename = my_custom_view.id + "-image-export.png"
                with open(filename, "wb") as f:
                    f.write(my_custom_view.image)
                print("png saved to " + filename)
                
                # export as data. Filters etc could be added here as usual
                server.custom_views.populate_csv(my_custom_view)
                filename = my_custom_view.id + "-image-export.csv"
                with open(filename, "wb") as f:
                    f.write(my_custom_view.csv)
                print("csv saved to " + filename)
                
                # export as pdf. Filters etc could be added here as usual
                server.custom_views.populate_pdf(my_custom_view)
                filename = my_custom_view.id + "-image-export.pdf"
                with open(filename, "wb") as f:
                    f.write(my_custom_view.pdf)
                print("pdf saved to " + filename)
                

            if args.powerpoint:
                # Populate workbook preview image
                server.workbooks.populate_powerpoint(sample_workbook)
                with open(args.powerpoint, "wb") as f:
                    f.write(sample_workbook.powerpoint)
                print(f"\nDownloaded powerpoint of workbook to {os.path.abspath(args.powerpoint)}")

            if args.delete:
                print(f"deleting {c.id}")
                unlucky = TSC.CustomViewItem(c.id)
                server.custom_views.delete(unlucky.id)


if __name__ == "__main__":
    main()

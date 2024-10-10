####
# This script sets up a server. It uploads datasources and workbooks from the local filesystem.
#
# By default, all content is published to the Default project on the Default site.
####

import argparse
import glob
import logging
import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Initialize a server with content.")
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
    parser.add_argument("--datasources-folder", "-df", help="folder containing datasources")
    parser.add_argument("--workbooks-folder", "-wf", help="folder containing workbooks")
    parser.add_argument("--project", required=False, default="Default", help="project to use")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    ################################################################################
    # Step 1: Sign in to server.
    ################################################################################
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        ################################################################################
        # Step 2: Create the site we need only if it doesn't exist
        ################################################################################
        print("Checking to see if we need to create the site...")

        all_sites = TSC.Pager(server.sites)
        existing_site = next((s for s in all_sites if s.content_url == args.site_id), None)

        # Create the site if it doesn't exist
        if existing_site is None:
            print(f"Site not found: {args.site_id} Creating it...")
            new_site = TSC.SiteItem(
                name=args.site_id,
                content_url=args.site_id.replace(" ", ""),
                admin_mode=TSC.SiteItem.AdminMode.ContentAndUsers,
            )
            server.sites.create(new_site)
        else:
            print(f"Site {args.site_id} exists. Moving on...")

    ################################################################################
    # Step 3: Sign-in to our target site
    ################################################################################
    print("Starting our content upload...")
    server_upload = TSC.Server(args.server)

    tableau_auth.site_id = args.site_id

    with server_upload.auth.sign_in(tableau_auth):
        ################################################################################
        # Step 4: Create the project we need only if it doesn't exist
        ################################################################################
        import time

        time.sleep(2)  # sad panda...something about eventually consistent model
        all_projects = TSC.Pager(server_upload.projects)
        project = next((p for p in all_projects if p.name.lower() == args.project.lower()), None)

        # Create our project if it doesn't exist
        if project is None:
            print(f"Project not found: {args.project} Creating it...")
            new_project = TSC.ProjectItem(name=args.project)
            project = server_upload.projects.create(new_project)

        ################################################################################
        # Step 5:  Set up our content
        #     Publish datasources to our site and project
        #     Publish workbooks to our site and project
        ################################################################################
        publish_datasources_to_site(server_upload, project, args.datasources_folder)
        publish_workbooks_to_site(server_upload, project, args.workbooks_folder)


def publish_datasources_to_site(server_object, project, folder):
    path = folder + "/*.tds*"

    for fname in glob.glob(path):
        new_ds = TSC.DatasourceItem(project.id)
        new_ds = server_object.datasources.publish(new_ds, fname, server_object.PublishMode.Overwrite)
        print(f"Datasource published. ID: {new_ds.id}")


def publish_workbooks_to_site(server_object, project, folder):
    path = folder + "/*.twb*"

    for fname in glob.glob(path):
        new_workbook = TSC.WorkbookItem(project.id)
        new_workbook.show_tabs = True
        new_workbook = server_object.workbooks.publish(new_workbook, fname, server_object.PublishMode.Overwrite)
        print(f"Workbook published. ID: {new_workbook.id}")


if __name__ == "__main__":
    main()

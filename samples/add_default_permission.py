####
# This script demonstrates how to add default permissions using TSC
# To run the script, you must have installed Python 3.7 or later.
#
# In order to demonstrate adding a new default permission, this sample will create
# a new project and add a new capability to the new project, for the default "All users" group.
#
# Example usage: 'python add_default_permission.py -s
#       https://10ax.online.tableau.com --site devSite123 -u tabby@tableau.com'
####

import argparse
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Add workbook default permissions for a given project.")
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
    # This sample has no additional options, yet. If you add some, please add them here

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in to server
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):

        # Create a sample project
        project = TSC.ProjectItem("sample_project")
        project = server.projects.create(project)

        # Query for existing workbook default-permissions
        server.projects.populate_workbook_default_permissions(project)
        default_permissions = project.default_workbook_permissions[0]  # new projects have 1 grantee group

        # Add "ExportXml (Allow)" workbook capability to "All Users" default group if it does not already exist
        if TSC.Permission.Capability.ExportXml not in default_permissions.capabilities:
            new_capabilities = {TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Allow}

            # Each PermissionRule in the list contains a grantee and a dict of capabilities
            new_rules = [TSC.PermissionsRule(grantee=default_permissions.grantee, capabilities=new_capabilities)]

            new_default_permissions = server.projects.update_workbook_default_permissions(project, new_rules)

            # Print result from adding a new default permission
            for permission in new_default_permissions:
                grantee = permission.grantee
                capabilities = permission.capabilities
                print("\nCapabilities for {0} {1}:".format(grantee.tag_name, grantee.id))

                for capability in capabilities:
                    print("\t{0} - {1}".format(capability, capabilities[capability]))

        # Uncomment lines below to DELETE the new capability and the new project
        # rules_to_delete = TSC.PermissionsRule(
        #     grantee=default_permissions.grantee,
        #     capabilities=new_capabilities
        # )
        # server.projects.delete_workbook_default_permissions(project, rules_to_delete)
        # server.projects.delete(project.id)


if __name__ == "__main__":
    main()

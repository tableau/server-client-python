####
# This script demonstrates how to use the Tableau Server Client
# to create new projects, both at the root level and how to nest them using
# parent_id.
#
#
# To run the script, you must have installed Python 3.6 or later.
####

import argparse
import logging
import sys

import tableauserverclient as TSC


def create_project(server, project_item):
    try:
        project_item = server.projects.create(project_item)
        print('Created a new project called: %s' % project_item.name)
        return project_item
    except TSC.ServerResponseError:
        print('We have already created this project: %s' % project_item.name)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Create new projects.')
    # Common options; please keep those in sync across all samples
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-S', help='site name')
    parser.add_argument('--token-name', '-p', required=True,
                        help='name of the personal access token used to sign into the server')
    parser.add_argument('--token-value', '-v', required=True,
                        help='value of the personal access token used to sign into the server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    # Options specific to this sample
    # This sample has no additional options, yet. If you add some, please add them here

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Use highest Server REST API version available
        server.use_server_version()

        # Without parent_id specified, projects are created at the top level.
        top_level_project = TSC.ProjectItem(name='Top Level Project')
        top_level_project = create_project(server, top_level_project)

        # Specifying parent_id creates a nested projects.
        child_project = TSC.ProjectItem(name='Child Project', parent_id=top_level_project.id)
        child_project = create_project(server, child_project)

        # Projects can be nested at any level.
        grand_child_project = TSC.ProjectItem(name='Grand Child Project', parent_id=child_project.id)
        grand_child_project = create_project(server, grand_child_project)


if __name__ == '__main__':
    main()

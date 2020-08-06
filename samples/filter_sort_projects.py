####
# This script demonstrates how to use the Tableau Server Client
# to filter and sort on the name of the projects present on site.
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def create_example_project(name='Example Project', content_permissions='LockedToProject',
                           description='Project created for testing', server=None):

    new_project = TSC.ProjectItem(name=name, content_permissions=content_permissions,
                                  description=description)
    try:
        server.projects.create(new_project)
        print('Created a new project called: %s' % name)
    except TSC.ServerResponseError:
        print('We have already created this resource: %s' % name)


def main():
    parser = argparse.ArgumentParser(description='Filter and sort projects.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site', '-S', default=None)
    parser.add_argument('-p', default=None)

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    if args.p is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.p

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)

    with server.auth.sign_in(tableau_auth):
        # Use highest Server REST API version available
        server.use_server_version()

        filter_project_name = 'default'
        options = TSC.RequestOptions()

        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                      TSC.RequestOptions.Operator.Equals,
                                      filter_project_name))

        filtered_projects, _ = server.projects.get(req_options=options)
        # Result can either be a matching project or an empty list
        if filtered_projects:
            project_name = filtered_projects.pop().name
            print(project_name)
        else:
            error = "No project named '{}' found".format(filter_project_name)
            print(error)

        create_example_project(name='Example 1', server=server)
        create_example_project(name='Example 2', server=server)
        create_example_project(name='Example 3', server=server)
        create_example_project(name='Proiect ca Exemplu', server=server)

        options = TSC.RequestOptions()

        # don't forget to URL encode the query names
        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                      TSC.RequestOptions.Operator.In,
                                      ['Example+1', 'Example+2', 'Example+3']))

        options.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name,
                                  TSC.RequestOptions.Direction.Desc))

        matching_projects, pagination_item = server.projects.get(req_options=options)
        print('Filtered projects are:')
        for project in matching_projects:
            print(project.name, project.id)


if __name__ == '__main__':
    main()

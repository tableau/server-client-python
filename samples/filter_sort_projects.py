####
# This script demonstrates how to use the Tableau Server Client
# to filter and sort on the name of the projects present on site.
#
#
# To run the script, you must have installed Python 2.7.X or 3.3 and later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC

def create_example_project(_name='Example Project', _content_permissions='LockedToProject',
                           _description='Project created for testing', _server=None):

    new_project = TSC.ProjectItem(name=_name, content_permissions=_content_permissions,
                                  description=_description)
    try:
        _server.projects.create(new_project)
        print('Created a new project called: %s' % _name)
    except TSC.ServerResponseError:
        print('We have already created this resource: %s' % _name)


def main():
    parser = argparse.ArgumentParser(description='Get all of the refresh tasks available on a server')
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
        server.version = '2.7'

        filter_project_name = 'default'
        options = TSC.RequestOptions()

        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                      TSC.RequestOptions.Operator.Equals,
                                      filter_project_name))

        filter_projects_paged = server.projects.get(req_options=options)
        print(filter_projects_paged[0][0].name)

        create_example_project(_name='Example 1', _server=server)
        create_example_project(_name='Example 2', _server=server)
        create_example_project(_name='Example 3', _server=server)
        create_example_project(_name='Proiect ca Exemplu', _server=server)

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
####
# This script demonstrates how to use the Tableau Server Client
# to move a workbook from one project to another. It will find
# a workbook that matches a given name and update it to be in
# the desired project.
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Move one workbook from the default project to another.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--workbook-name', '-w', required=True, help='name of workbook to move')
    parser.add_argument('--destination-project', '-d', required=True, help='name of project to move workbook into')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server
    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)

    with server.auth.sign_in(tableau_auth):
        # Step 2: Query workbook to move
        req_option = TSC.RequestOptions()
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                         TSC.RequestOptions.Operator.Equals, args.workbook_name))
        all_workbooks, pagination_item = server.workbooks.get(req_option)

        # Step 3: Find destination project
        all_projects, pagination_item = server.projects.get()
        dest_project = next((project for project in all_projects if project.name == args.destination_project), None)

        if dest_project is not None:
            # Step 4: Update workbook with new project id
            if all_workbooks:
                print("Old project: {}".format(all_workbooks[0].project_name))
                all_workbooks[0].project_id = dest_project.id
                target_workbook = server.workbooks.update(all_workbooks[0])
                print("New project: {}".format(target_workbook.project_name))
            else:
                error = "No workbook named {} found.".format(args.workbook_name)
                raise LookupError(error)
        else:
            error = "No project named {} found.".format(args.destination_project)
            raise LookupError(error)


if __name__ == '__main__':
    main()

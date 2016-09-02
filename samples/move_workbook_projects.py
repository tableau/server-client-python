####
# This script demonstrates how to use the Tableau Server API
# to move a workbook from one project to another. It will find
# a workbook that matches a given name and update it to be in
# the desired project.
#
# To run the script, you must have installed Python 2.7.9 or later.
####

import tableauserverapi as TSA
import argparse

# import logging
# logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Move one workbook from the default project to another.')
parser.add_argument('server', help='server address')
parser.add_argument('username', help='username to sign into server')
parser.add_argument('password', help='password to sign into server')
parser.add_argument('workbook_name', help='name of workbook to move')
parser.add_argument('destination_project', help='name of project to move workbook into')
args = parser.parse_args()

# Step 1: Sign in to server
tableau_auth = TSA.TableauAuth(args.username, args.password)
server = TSA.Server(args.server)
with server.auth.sign_in(tableau_auth):
    # Step 2: Query workbook to move
    req_option = TSA.RequestOptions()
    req_option.filter.add(TSA.Filter(TSA.RequestOptions.Field.Name,
                                     TSA.RequestOptions.Operator.Equals, args.workbook_name))
    pagination_info, all_workbooks = server.workbooks.get(req_option)

    # Step 3: Find destination project
    pagination_info, all_projects = server.projects.get()
    dest_project = next((project for project in all_projects if project.name == args.destination_project), None)

    # Step 4: Update workbook with new project id
    if all_workbooks:
        print("Old project: {}".format(all_workbooks[0].project_name))
        all_workbooks[0].project_id = dest_project.id
        target_workbook = server.workbooks.update(all_workbooks[0])
        print("New project: {}".format(target_workbook.project_name))
    else:
        print('No workbook named {} found.'.format(args.workbook_name))

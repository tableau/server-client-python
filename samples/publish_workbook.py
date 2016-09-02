####
# This script demonstrates how to use the Tableau Server API
# to publish a workbook to a Tableau server. It will publish
# a specified workbook to the 'default' project of the given server.
#
# Note: The REST API publish process cannot automatically include
# extracts or other resources that the workbook uses. Therefore,
# a .twb file with data from a local computer cannot be published,
# unless packaged into a .twbx file.
#
# For more information, refer to the documentations on 'Publish Workbook'
# (https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm)
#
# To run the script, you must have installed Python 2.7.9 or later.
####

import tableauserverapi as TSA
import argparse

parser = argparse.ArgumentParser(description='Publish a workbook to server.')
parser.add_argument('server', help='server address')
parser.add_argument('username', help='username to sign into server')
parser.add_argument('password', help='password to sign into server')
parser.add_argument('filepath', help='filepath to the workbook to publish')
args = parser.parse_args()

# Step 1: Sign in to server.
tableau_auth = TSA.TableauAuth(args.username, args.password)
server = TSA.Server(args.server)
with server.auth.sign_in(tableau_auth):

    # Step 2: Get all the projects on server, then look for the default one.
    pagination_info, all_projects = server.projects.get()
    default_project = next((project for project in all_projects if project.is_default()), None)

    # Step 3: If default project is found, form a new workbook item and publish.
    if default_project is not None:
        new_workbook = TSA.WorkbookItem(default_project.id)
        new_workbook = server.workbooks.publish(new_workbook, args.filepath, server.PublishMode.Overwrite)
        print("Workbook published. ID: {0}".format(new_workbook.id))
    else:
        error = "The default project could not be found."
        raise LookupError(error)

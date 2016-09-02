####
# This script demonstrates how to use the Tableau Server API
# to move a workbook from one site to another. It will find
# a workbook that matches a given name, download the workbook,
# and then publish it to the destination site.
#
# To run the script, you must have installed Python 2.7.9 or later.
####

import tableauserverapi as TSA
import shutil
import argparse
import tempfile

parser = argparse.ArgumentParser(description="Move one workbook from the"
                                             "default project of the default site to"
                                             "the default project of another site.")
parser.add_argument('server', help='server address')
parser.add_argument('username', help='username to sign into server')
parser.add_argument('password', help='password to sign into server')
parser.add_argument('workbook_name', help='name of workbook to move')
parser.add_argument('destination_site', help='name of site to move workbook into')
args = parser.parse_args()

# Step 1: Sign in to both sites on server
tableau_auth = TSA.TableauAuth(args.username, args.password)

source_server = TSA.Server(args.server)
dest_server = TSA.Server(args.server)

with source_server.auth.sign_in(tableau_auth):
    # Step 2: Query workbook to move
    req_option = TSA.RequestOptions()
    req_option.filter.add(TSA.Filter(TSA.RequestOptions.Field.Name,
                                     TSA.RequestOptions.Operator.Equals, args.workbook_name))
    pagination_info, all_workbooks = source_server.workbooks.get(req_option)

    # Step 3: Download workbook to a temp directory
    if len(all_workbooks) == 0:
        print('No workbook named {} found.'.format(args.workbook_name))
    else:
        tmpdir = tempfile.mkdtemp()
        try:
            workbook_path = source_server.workbooks.download(all_workbooks[0].id, tmpdir)

            # Step 4: Sign in to destination site
            tableau_auth.site = args.destination_site
            with dest_server.auth.sign_in(tableau_auth):

                # Step 5: Find destination site's default project
                pagination_info, dest_projects = dest_server.projects.get()
                target_project = next((project for project in dest_projects if project.is_default()), None)

                # Step 6: If default project is found, form a new workbook item and publish.
                if target_project is not None:
                    new_workbook = TSA.WorkbookItem(name=args.workbook_name, project_id=target_project.id)
                    new_workbook = dest_server.workbooks.publish(new_workbook, workbook_path,
                                                                 mode=dest_server.PublishMode.Overwrite)

            # Step 7: Delete workbook from source site and delete temp directory
            source_server.workbooks.delete(all_workbooks[0].id)
        finally:
            shutil.rmtree(tmpdir)

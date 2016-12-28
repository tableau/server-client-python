####
# This script will move workbooks from one site to another. It will find workbooks with a given tag, download them,
# and then publish them to the destination site. Before moving the workbooks, we (optionally) modify them to point to
# production datasources based on information contained in a CSV file.
#
# If a CSV file is used, it is assumed to have two columns: source_ds and dest_ds.
#
# To run the script, you must have installed Python 2.7.9 or later.
####


import argparse
import csv
import getpass
import logging
import shutil
import tableaudocumentapi as TDA
import tableauserverclient as TSC
import tempfile


def main():
    parser = argparse.ArgumentParser(description='Move workbooks with the given tag from one project to another.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--source-site', '-ss', required=True, help='source site to get workbooks from')
    parser.add_argument('--dest-site', '-ds', required=True, help='destination site to copy workbooks to')
    parser.add_argument('--tag', '-t', required=True, help='tag to search for')
    parser.add_argument('--csv', '-c', required=False, help='CSV file containing database info')
    parser.add_argument('--delete-source', '-d', required=False, help='use true to delete source wbs after migration')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info',
                        'error'], default='error', help='desired logging level (set to error by default)')
    args = parser.parse_args()
    db_info = None
    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign-in to server twice because the destination site has a
    # different site id and requires second server object
    auth_source = TSC.TableauAuth(args.username, password, args.source_site)
    auth_dest = TSC.TableauAuth(args.username, password, args.dest_site)

    server = TSC.Server(args.server)
    dest_server = TSC.Server(args.server)

    with server.auth.sign_in(auth_source):
        # Step 2: Verify our source and destination sites exist
        found_source_site = False
        found_dest_site = False

        found_source_site, found_dest_site = verify_sites(server, args.source_site, args.dest_site)

        # Step 3: get all workbooks with the tag (e.g. 'ready-for-prod') using a filter
        req_option = TSC.RequestOptions()
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.Equals, args.tag))
        all_workbooks, pagination_item = server.workbooks.get(req_option)

        # Step 4: Download workbooks to a temp dir and loop thru them
        if len(all_workbooks) > 0:
            tmpdir = tempfile.mkdtemp()

            try:
                # We got a CSV so let's make a dictionary
                if args.csv:
                    db_info = dict_from_csv(args.csv)

                # Signing into another site requires another server object b/c of the different auth token and site ID
                with dest_server.auth.sign_in(auth_dest):
                    for wb in all_workbooks:
                        wb_path = server.workbooks.download(wb.id, tmpdir)

                        # Step 5: If we have a CSV of data sources then update each workbook db connection per our CSV
                        if db_info:
                            source_wb = TDA.Workbook(wb_path)

                            # if we have more than one datasource we need to loop
                            for ds in source_wb.datasources:
                                for c in ds.connections:
                                    if c.dbname in db_info.keys():
                                        c.dbname = db_info[c.dbname]
                                        ds.caption = c.dbname

                            source_wb.save_as(wb_path)

                        # Step 6: Find destination site's default project
                        dest_sites, _ = dest_server.projects.get()
                        target_project = next((project for project in dest_sites if project.is_default()), None)

                        # Step 7: If default project is found, form a new workbook item and publish
                        if target_project is not None:
                            new_workbook = TSC.WorkbookItem(name=wb.name, project_id=target_project.id)
                            new_workbook = dest_server.workbooks.publish(
                                new_workbook, wb_path, mode=TSC.Server.PublishMode.Overwrite)

                            print("Successfully moved {0} ({1})".format(
                                new_workbook.name, new_workbook.id))
                        else:
                            error = "The default project could not be found."
                            raise LookupError(error)

                        # Step 8: (if requested) Delete workbook from source site and delete temp directory
                        if args.delete_source:
                            server.workbooks.delete(wb.id)
            finally:
                shutil.rmtree(tmpdir)

        # No workbooks found
        else:
            print('No workbooks with tag {} found.'.format(args.tag))


# Takes a Tableau Server URL and two site names. Returns true, true if the sites exist on the server

def verify_sites(server, site1, site2):
    found_site1 = False
    found_site2 = False

    # Use the Pager to get all the sites
    for site in TSC.Pager(server.sites):
        if site1.lower() == site.content_url.lower():
            found_site1 = True
        if site2.lower() == site.content_url.lower():
            found_site2 = True

    if not found_site1:
        error = "Site named {} not found.".format(site1)
        raise LookupError(error)

    if not found_site2:
        error = "Site named {} not found.".format(site2)
        raise LookupError(error)

    return found_site1, found_site2


# Returns a dictionary from a CSV file

def dict_from_csv(csv_file):
    with open(csv_file) as csvfile:
        return {value['source_ds']: value['dest_ds'] for value in csv.DictReader(csvfile)}


if __name__ == "__main__":
    main()

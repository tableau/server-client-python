import argparse
import getpass
import logging
import json

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='Materialized views settings to site/workbook.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--password', '-p', required=False, help='password to sign into server')
    parser.add_argument('--file-path', '-fp', required=False,
                        help='JSON file that stores objects to change mateiralized views setting')
    parser.add_argument('--mode', '-m', required=False, choices=['enable', 'disable'],
                        help='enable/disable materialized views for site/workbook')
    parser.add_argument('--status', '-st', required=False, action='store_true',
                        help='show materialized views enabled sites/workbooks')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Password: ")

    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    enable_materialized_views = args.mode == 'enable'

    server_responses = list()
    workbook_status = list()

    # TODO: the situation when filename is not given
    # TODO: if filename is given, mode must be present too
    server = TSC.Server(args.server)
    if args.file_path:
        with open(args.file_path) as infile:
            data = json.load(infile)

        for site in data['workbooks']:
            workbook_items = list()
            tableau_auth = TSC.TableauAuth(args.username, password, site_id=site)

            with server.auth.sign_in(tableau_auth):
                # update materialized views settings
                for project_path in data['workbooks'][site]:
                    for workbook in data['workbooks'][site][project_path]:
                        workbook_item = TSC.WorkbookItem('None', name=workbook)
                        workbook_item.project_path = project_path
                        workbook_items.append(workbook_item)

                server_responses.append(server.workbooks.materialize(workbook_items, enable_materialized_views))

        for site in data['sites']:
            tableau_auth = TSC.TableauAuth(args.username, password, site_id=site)

            with server.auth.sign_in(tableau_auth):
                site_to_update = server.sites.get_by_content_url(site)
                site_to_update.materialized_views_enabled = args.mode == 'enable'

                server.sites.update(site_to_update)

    if args.status:
        tableau_auth = TSC.TableauAuth(args.username, password)
        server.auth.sign_in(tableau_auth)
        all_sites = server.sites.get()[0]
        server.auth.sign_out()

        for site in all_sites:
            tableau_auth = TSC.TableauAuth(args.username, password, site_id=site.content_url)
            with server.auth.sign_in(tableau_auth):
                server.workbooks.get_materialization_status(workbook_status)

        print('Materialized views are enable for the following workbooks:')
        for status in workbook_status:
            message = "Project Id: {0}, workbook name: {1}".format(status.project_id, status.name)
            print(message)

        print('\n')
        print('And all the workbooks from the following sites:')
        for site in all_sites:
            if site.materialized_views_enabled == 'true':
                message = "Site Id: {0}".format(site.content_url)
                print(message)


if __name__ == "__main__":
    main()

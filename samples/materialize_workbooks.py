import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='Materialized views settings for sites/workbooks.')
    parser.add_argument('--server', '-s', required=True, help='Tableau server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--password', '-p', required=False, help='password to sign into server')
    parser.add_argument('--mode', '-m', required=False, choices=['enable', 'disable'],
                        help='enable/disable materialized views for sites/workbooks')
    parser.add_argument('--status', '-st', required=False, action='store_true',
                        help='show materialized views enabled sites/workbooks')
    parser.add_argument('--site-id', '-si', required=False,
                        help='set to Default site by default')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('--type', '-t', required=False, choices=['site', 'workbook'],
                        help='type of content you want to update materialized views settings on')

    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Password: ")

    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    enable_materialized_views = args.mode == "enable"
    site_content_url = args.site_id if args.site_id is not None else ""

    if args.type is not None and args.mode is None:
        print("Use '--mode <enable/disable>' to specify how you want to change materialized views settings.")
        return

    if args.type is None and args.mode is not None:
        print("Use '--type <workbook/site>' to specify the level of materialized views setting you want to change.")
        return

    if args.type is None and args.mode is None and args.status is None:
        print("Use '--type <workbook/site> --mode <enable/disable>' to change materialized views settings.")
        print("Or use '--status' to show currently materialized views enabled workbooks and sites.")
        return

    if args.type is not None and enable_materialized_views is not None:
        if args.type == 'site':
            tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
            server = TSC.Server(args.server)

            with server.auth.sign_in(tableau_auth):
                site_to_update = server.sites.get_by_content_url(site_content_url)
                site_to_update.materialized_views_enabled = enable_materialized_views

                server.sites.update(site_to_update)
                print("Site updated. ID: {0}".format(site_content_url))
            print

        elif args.type == 'workbook':
            tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
            server = TSC.Server(args.server)

            # Now it updates all the workbooks in the site
            # To update selected ones pass filter into 'workbooks = server.workbooks.get()[0]'
            with server.auth.sign_in(tableau_auth):
                for workbook in TSC.Pager(server.workbooks):
                    workbook.materialized_views_enabled = enable_materialized_views

                    server.workbooks.update(workbook)
                    print "workbook updated: ", workbook.name
            print

    if args.status:
        tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
        server = TSC.Server(args.server)

        enabled_site_content_urls = set()
        with server.auth.sign_in(tableau_auth):
            # For server admin, this will prints all the materialized views enabled sites
            # For other users, this only prints the status of the site they belong to
            print("enabled sites:")
            for site in TSC.Pager(server.sites):
                if site.materialized_views_enabled:
                    enabled_site_content_urls.add(site.content_url)
                    print "Site name: ", site.name
            print

        print("enabled workbooks:")
        for site_content_url in enabled_site_content_urls:
            site_auth = TSC.TableauAuth(args.username, password, site_content_url)
            with server.auth.sign_in(site_auth):
                for workbook in TSC.Pager(server.workbooks):
                    if workbook.materialized_views_enabled:
                        print "Workbook name: ", workbook.name, " site id: ", site_content_url
        print


if __name__ == "__main__":
    main()
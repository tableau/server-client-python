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

    # site content url is the TSC term for site id
    site_content_url = args.site_id if args.site_id is not None else ""
    enable_materialized_views = args.mode == "enable"

    if (args.type is None) != (args.mode is None):
        print("Use '--type <workbook/site> --mode <enable/disable>' to update materialized views settings.")
        return

    if args.type == 'site':
        update_site(args, enable_materialized_views, password, site_content_url)

    elif args.type == 'workbook':
        update_workbook(args, enable_materialized_views, password, site_content_url)

    if args.status:
        show_materialized_views_status(args, password, site_content_url)


def show_materialized_views_status(args, password, site_content_url):
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
    server = TSC.Server(args.server, use_server_version=True)
    enabled_sites = set()
    with server.auth.sign_in(tableau_auth):
        # For server admin, this will prints all the materialized views enabled sites
        # For other users, this only prints the status of the site they belong to
        print "Materialized views is enabled on sites:"
        for site in TSC.Pager(server.sites):
            if site.materialized_views_enabled:
                enabled_sites.add(site)
                print "Site name:", site.name
        print '\n'

    print("Materialized views is enabled on workbooks:")
    # Individual workbooks can be enabled only when the sites they belong to are enabled too
    for site in enabled_sites:
        site_auth = TSC.TableauAuth(args.username, password, site.content_url)
        with server.auth.sign_in(site_auth):
            for workbook in TSC.Pager(server.workbooks):
                if workbook.materialized_views_enabled:
                    print "Workbook:", workbook.name, "from site:", site.name


def update_workbook(args, enable_materialized_views, password, site_content_url):
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
    server = TSC.Server(args.server, use_server_version=True)
    # Now it updates all the workbooks in the site
    # To update selected ones please use filter:
    # https://github.com/tableau/server-client-python/blob/master/docs/docs/filter-sort.md
    # This only updates the workbooks in the site you are signing into
    with server.auth.sign_in(tableau_auth):
        for workbook in TSC.Pager(server.workbooks):
            workbook.materialized_views_enabled = enable_materialized_views

            server.workbooks.update(workbook)
            site = server.sites.get_by_content_url(site_content_url)
            print "Updated materialized views settings for workbook:", workbook.name, "from site:", site.name
    print '\n'


def update_site(args, enable_materialized_views, password, site_content_url):
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        site_to_update = server.sites.get_by_content_url(site_content_url)
        site_to_update.materialized_views_enabled = enable_materialized_views

        server.sites.update(site_to_update)
        print "Updated materialized views settings for site:", site_to_update.name
    print '\n'


if __name__ == "__main__":
    main()

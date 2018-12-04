import argparse
import logging
import getpass
import tableauserverclient as TSC

def main():
    parser = argparse.ArgumentParser(description='Update site settings.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site-id', '-cu', required=True, default='', help='site id of the site to update')
    parser.add_argument('--site-name', '-sn', required=False, help='site name of the site to update')
    parser.add_argument('--password', '-p', required=False, help='password to sign into server')
    parser.add_argument('--user-quota', '-uq', required=False, help='user quota for the site to update')
    parser.add_argument('--storage-quota', '-sq', required=False, help='storage quota for the site to update')
    parser.add_argument('--subscription', '-sb', required=False, choices=['enable', 'disable'],
                        help='enable/disable subscription')
    parser.add_argument('--revision-history', '-rh', required=False, choices=['enable', 'disable'],
                        help='enable/disable revision history')
    parser.add_argument('--subscribe-others', '-so', required=False, choices=['enable', 'disable'],
                        help='enable/disable subscribe others')
    parser.add_argument('--admin-mode', '-am', required=False, help='admin mode for the site to be updated')
    parser.add_argument('--materialized-views', '-mv', required=False, choices=['enable', 'disable'], default='disable',
                        help='enable/disable materialized views')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Password: ")


    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.TableauAuth(args.username, password, site_id=args.site_id)
    server = TSC.Server(args.server)

    with server.auth.sign_in(tableau_auth):
        site_to_update = server.sites.get_by_content_url(args.site_id)

        if args.user_quota:
            site_to_update.user_quota = args.user_quota
        if args.storage_quota:
            site_to_update.storage_quota = args.storage_quota
        if args.subscription:
            site_to_update.disable_subscriptions = args.subscription == 'disable'
        if args.revision_history:
            site_to_update.revision_history_enabled = args.revision_history == 'enable'
        if args.subscribe_others:
            site_to_update.subscribe_others_enabled = args.subscribe_others == 'enable'
        if args.admin_mode:
            site_to_update.admin_mode = args.admin_mode
        if args.materialized_views:
            site_to_update.materialized_views_enabled = args.materialized_views == 'enable'

        server.sites.update(site_to_update)
        print("Site updated. ID: {0}".format(args.site_id))


if __name__ == "__main__":
    main()

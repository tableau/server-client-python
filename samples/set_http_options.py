####
# This script demonstrates how to set http options. It will set the option
# to not verify SSL certificate, and query all workbooks on site.
#
# To run the script, you must have installed Python 3.6 or later.
####

import argparse
import logging

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='List workbooks on site, with option set to ignore SSL verification.')
    # Common options; please keep those in sync across all samples
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-S', help='site name')
    parser.add_argument('--token-name', '-p', required=True,
                        help='name of the personal access token used to sign into the server')
    parser.add_argument('--token-value', '-v', required=True,
                        help='value of the personal access token used to sign into the server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    # Options specific to this sample
    # This sample has no additional options, yet. If you add some, please add them here

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Create required objects for sign in
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server)

    # Step 2: Set http options to disable verifying SSL
    server.add_http_options({'verify': False})

    with server.auth.sign_in(tableau_auth):

        # Step 3: Query all workbooks and list them
        all_workbooks, pagination_item = server.workbooks.get()
        print('{0} workbooks found. Showing {1}:'.format(pagination_item.total_available, pagination_item.page_size))
        for workbook in all_workbooks:
            print('\t{0} (ID: {1})'.format(workbook.name, workbook.id))


if __name__ == '__main__':
    main()

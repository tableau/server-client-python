####
# This script demonstrates how to export a view using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='Export a view as an image, PDF, or CSV')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site', '-S', default=None)
    parser.add_argument('-p', default=None)

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--pdf', dest='type', action='store_const', const=('populate_pdf', 'PDFRequestOptions', 'pdf',
                                                                          'pdf'))
    group.add_argument('--png', dest='type', action='store_const', const=('populate_image', 'ImageRequestOptions',
                                                                          'image', 'png'))
    group.add_argument('--csv', dest='type', action='store_const', const=('populate_csv', 'CSVRequestOptions', 'csv',
                                                                          'csv'))

    parser.add_argument('--file', '-f', help='filename to store the exported data')
    parser.add_argument('--filter', '-vf', metavar='COLUMN:VALUE',
                        help='View filter to apply to the view')
    parser.add_argument('resource_id', help='LUID for the view')

    args = parser.parse_args()

    if args.p is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.p

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        views = filter(lambda x: x.id == args.resource_id,
                       TSC.Pager(server.views.get))
        view = views.pop()

        # We have a number of different types and functions for each different export type.
        # We encode that information above in the const=(...) parameter to the add_argument function to make
        # the code automatically adapt for the type of export the user is doing.
        # We unroll that information into methods we can call, or objects we can create by using getattr()
        (populate_func_name, option_factory_name, member_name, extension) = args.type
        populate = getattr(server.views, populate_func_name)
        option_factory = getattr(TSC, option_factory_name)

        if args.filter:
            options = option_factory().vf(*args.filter.split(':'))
        else:
            options = None
        if args.file:
            filename = args.file
        else:
            filename = 'out.{}'.format(extension)

        populate(view, options)
        with file(filename, 'wb') as f:
            if member_name == 'csv':
                f.writelines(getattr(view, member_name))
            else:
                f.write(getattr(view, member_name))


if __name__ == '__main__':
    main()

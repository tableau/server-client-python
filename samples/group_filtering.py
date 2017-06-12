####
# This script demonstrates how to filter groups using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 2.7.9 or later.
####


import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Filter on groups')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('-p', default=None)
    args = parser.parse_args()

    password = ''
    if args.p is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.p

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)

    with server.auth.sign_in(tableau_auth):
        server.version = '2.7'
        group_name = 'SALES NORTHWEST'
        # Try to create a group named "SALES NORTHWEST"
        try:
            group1 = TSC.GroupItem(group_name)
            group1 = server.groups.create(group1)
            print(group1)
        except:
            print('Group \'%s\' already existed' % group_name)

        group_name = 'SALES ROMANIA'
        # Try to create a group named "SALES ROMANIA"
        try:
            group2 = TSC.GroupItem(group_name)
            group2 = server.groups.create(group2)
            print(group2)
        except:
            print('Group \'%s\' already existed' % group_name)

        group_name = 'SALES+ROMANIA'
        options = TSC.RequestOptions()
        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                              TSC.RequestOptions.Operator.Equals,
                              group_name))

        filtered_group_paged = server.groups.get(req_options=options)
        print(filtered_group_paged[0][0].name)

        options = TSC.RequestOptions()
        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                      TSC.RequestOptions.Operator.In,
                                      ['SALES+NORTHWEST', 'SALES+ROMANIA', 'this_group']))

        options.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name,
                                  TSC.RequestOptions.Direction.Desc))

        matching_groups, pagination_item = server.groups.get(req_options=options)
        print('Filtered groups are:')
        for group in matching_groups:
            print(group.name)

if __name__ == '__main__':
    main()

####
# This script demonstrates how to filter and sort groups using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 3.5 or later.
####


import argparse
import getpass
import logging

import tableauserverclient as TSC


def create_example_group(group_name='Example Group', server=None):
    new_group = TSC.GroupItem(group_name)
    try:
        new_group = server.groups.create(new_group)
        print('Created a new project called: \'%s\'' % group_name)
        print(new_group)
    except TSC.ServerResponseError:
        print('Group \'%s\' already existed' % group_name)


def main():
    parser = argparse.ArgumentParser(description='Filter and sort groups.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('-p', default=None)
    args = parser.parse_args()

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

        # Determine and use the highest api version for the server
        server.use_server_version()

        group_name = 'SALES NORTHWEST'
        # Try to create a group named "SALES NORTHWEST"
        create_example_group(group_name, server)

        group_name = 'SALES ROMANIA'
        # Try to create a group named "SALES ROMANIA"
        create_example_group(group_name, server)

        # URL Encode the name of the group that we want to filter on
        # i.e. turn spaces into plus signs
        filter_group_name = 'SALES+ROMANIA'
        options = TSC.RequestOptions()
        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                      TSC.RequestOptions.Operator.Equals,
                                      filter_group_name))

        filtered_groups, _ = server.groups.get(req_options=options)
        # Result can either be a matching group or an empty list
        if filtered_groups:
            group_name = filtered_groups.pop().name
            print(group_name)
        else:
            error = "No project named '{}' found".format(filter_group_name)
            print(error)

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

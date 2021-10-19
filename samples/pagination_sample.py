####
# This script demonstrates how to use pagination item that is returned as part
# of many of the .get() method calls.
#
# This script will iterate over every workbook that exists on the server using the
# pagination item to fetch additional pages as needed.
#
# While this sample uses workbook, this same technique will work with any of the .get() methods that return
# a pagination item
####

import argparse
import logging
import os.path

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Demonstrate pagination on the list of workbooks on the server.')
    # Common options; please keep those in sync across all samples
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-S', help='site name')
    parser.add_argument('--token-name', '-n', required=True,
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

    # Sign in to server
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Pager returns a generator that yields one item at a time fetching
        # from Server only when necessary. Pager takes a server Endpoint as its
        # first parameter. It will call 'get' on that endpoint. To get workbooks
        # pass `server.workbooks`, to get users pass` server.users`, etc
        # You can then loop over the generator to get the objects one at a time
        # Here we print the workbook id for each workbook

        print("Your server contains the following workbooks:\n")
        for wb in TSC.Pager(server.workbooks):
            print(wb.name)

        # Pager can also be used in list comprehensions or generator expressions
        # for compactness and easy filtering. Generator expressions will use less
        # memory than list comprehsnsions. Consult the Python laguage documentation for
        # best practices on which are best for your use case. Here we loop over the
        # Pager and only keep workbooks where the name starts with the letter 'a'
        # >>> [wb for wb in TSC.Pager(server.workbooks) if wb.name.startswith('a')] # List Comprehension
        # >>> (wb for wb in TSC.Pager(server.workbooks) if wb.name.startswith('a')) # Generator Expression

        # Since Pager is a generator it follows the standard conventions and can
        # be fed to a list if you really need all the workbooks in memory at once.
        # If you need everything, it may be faster to use a larger page size

        # >>> request_options = TSC.RequestOptions(pagesize=1000)
        # >>> all_workbooks = list(TSC.Pager(server.workbooks, request_options))


if __name__ == '__main__':
    main()

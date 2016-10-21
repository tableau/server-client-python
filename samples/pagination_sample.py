####
# This script demonstrates how to use pagination item that is returned as part
# of mayn of the .get() method calls.
#
# This script will iterate over every workbook that exists on the server using the
# pagination item to fetch additional pages as needed.
#
# While this sample uses workbook, this same technique will work with any of the .get() methods that return
# a pagination item
####

import argparse
import getpass
import logging
import os.path

import tableauserverclient as TSC

class pagination_generator(object):
    """ This class returns a generator that will iterate over all of the results.

    server is the server object that will be used when calling the callback.  It will be passed
    to the callback on each iteration

    Callback is expected to take a server object and a request options and return two values, an array of results, and the pagination item
    from the current call.  This will be used to build subsequent requests.
    """

    def __init__(self, server, callback):
        self._server = server
        self._callback = callback

    def __call__(self):
        current_item_list, last_pagination_item = self._callback(self._server, None)  # Prime the generator
        count = 0

        while count < last_pagination_item.total_available:
            if len(current_item_list) == 0:
                current_item_list, last_pagination_item = self._load_next_page(current_item_list, last_pagination_item)

            yield current_item_list.pop(0)
            count += 1

    def _load_next_page(self, current_item_list, last_pagination_item):
        next_page = last_pagination_item.page_number + 1
        opts = TSC.RequestOptions(pagenumber=next_page, pagesize=last_pagination_item.page_size)
        current_item_list, last_pagination_item = self._callback(self._server, opts)
        return current_item_list, last_pagination_item


def main():

    parser = argparse.ArgumentParser(description='Explore workbook functions supported by the Server API.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)

    with server.auth.sign_in(tableau_auth):
        generator = pagination_generator(server, lambda srv, opts: srv.workbooks.get(req_options=opts))
        print("Your server contains the following workbooks:\n")
        for wb in generator():
            print(wb.name)

if __name__ == '__main__':
    main()

####
# This script demonstrates how to connect to the server without authentication.
# It can be helpful if you are debugging issues with connection and logging in.
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():

    server = '' # Use a link from http://webhook.site to troubleshoot outgoing requests

    server = TSC.Server(server)
    print(server)
    server.use_highest_version()

if __name__ == '__main__':
    main()

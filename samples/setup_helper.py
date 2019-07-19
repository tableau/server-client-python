####
# This script provides the shared login logic and server creation for all other samples.
#
# To run the script, you must have installed Python 2.7.9 or later.
####

import argparse
import getpass
import logging

from datetime import time

import tableauserverclient as TSC

class SetupHelper(object):
    def __init__(self, description):
        self._parser = argparse.ArgumentParser(description=description)
        self._addServerArgs()
        self._addLoginArgs()
        self._addLoggerArgs()

    def _addLoginArgs(self):
        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--username', '-u', help='username to sign into the server')
        group.add_argument('--token-name', '-n', help='name of the personal access token used to sign into the server')

    def _addServerArgs(self):
        self._parser.add_argument('--server', '-s', required=True, help='server address')

    def _addLoggerArgs(self):
        self._parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                    help='desired logging level (set to error by default)')

    def getParser(self):
        return self._parser

    def createServer(self):
        args = self._parser.parse_args()

        # Set logging level based on user input, or error by default
        logging_level = getattr(logging, args.logging_level.upper())
        logging.basicConfig(level=logging_level)

        self._server = TSC.Server(args.server)
        return self._server

    def login(self):
        if not self._server:
            raise RuntimeError('Please call createServer first')

        args = self._parser.parse_args()

        if args.username:
            # Trying to authenticate using username and password.
            password = getpass.getpass("Password: ")
            tableau_auth = TSC.TableauAuth(args.username, password)
        else:
            # Trying to authenticate using personal access tokens.
            personal_access_token = getpass.getpass("Personal Access Token: ")
            tableau_auth = TSC.TableauAuth(token_name=args.token_name, personal_access_token=personal_access_token)

        return self._server.auth.sign_in(tableau_auth)

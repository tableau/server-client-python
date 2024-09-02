####
# This script demonstrates how to create a flow using the Tableau Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####

import logging

from datetime import time
from typing import List

import tableauserverclient as TSC
from tableauserverclient import ServerResponseError


def main():


    # Set logging level based on user input, or error by default
    logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level)

    server_url = "url_here"
    tableau_auth = TSC.PersonalAccessTokenAuth( )
    server = TSC.Server(server_url, use_server_version=True, http_options={"verify": False})
    with server.auth.sign_in(tableau_auth):
        flow = TSC.FlowItem("test")
        try:
            flow = server.flows.get_by_id("ab5f66c6-39d2-440f-89ad-3e45bc0bb341")
            print(flow)
        except TSC.server.endpoint.exceptions.ServerResponseError as rError:
            raise rError


if __name__ == "__main__":
    main()

####
# Getting started Part One of Three
# This script demonstrates how to use the Tableau Server Client to connect to a server
# You don't need to have a site or any experience with Tableau to run it
#
####

import tableauserverclient as TSC


def main():
    # This is the domain for Tableau's Developer Program
    server_url = "https://10ax.online.tableau.com"
    server = TSC.Server(server_url)

    # OPTIONAL, FOR A TEST SERVER ONLY: turn off certificate verification.
    # If your test server uses a self-signed certificate, requests fail with
    # SSL: CERTIFICATE_VERIFY_FAILED. Turning verification off lets anyone between
    # you and the server read or change the traffic, including your credentials,
    # so never do this for a production server. Prefer giving TSC the server's
    # certificate instead, see
    # https://tableau.github.io/server-client-python/docs/sign-in-out#handling-ssl-certificates-for-tableau-server
    # To opt in, uncomment the next line:
    # server.add_http_options({"verify": False})

    print(f"Connected to {server.server_info.baseurl}")
    print(f"Server information: {server.server_info}")
    print("Sign up for a test site at https://www.tableau.com/developer")


if __name__ == "__main__":
    main()

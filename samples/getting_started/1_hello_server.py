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
    print(f"Connected to {server.server_info.baseurl}")
    print(f"Server information: {server.server_info}")
    print("Sign up for a test site at https://www.tableau.com/developer")


if __name__ == "__main__":
    main()

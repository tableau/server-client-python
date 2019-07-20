####
# This script demonstrates how to log in to Tableau Server Client.
#
# To run the script, you must have installed Python 2.7.9 or later.
####


import tableauserverclient as TSC

import setup_helper as Helper


def main():

    setup_helper = Helper.SetupHelper('Create a user group.')
    setup_helper.createServer()

    with setup_helper.login():
        print('Logged in successfully')


if __name__ == '__main__':
    main()

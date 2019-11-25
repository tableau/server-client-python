####
# This script demonstrates how to use the Tableau Server Client
# to interact with webhooks. It explores the different
# functions that the Server API supports on webhooks.
#
# With no flags set, this sample will query all webhooks,
# pick one webhook and print the name of the webhook.
# Adding flags will demonstrate the specific feature
# on top of the general operations.
####

import argparse
import getpass
import logging
import os.path

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Explore webhook functions supported by the Server API.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site', '-S', default=None)
    parser.add_argument('-p', default=None, help='password')
    parser.add_argument('--create', '-c', help='create a webhook')
    parser.add_argument('--delete', '-d', help='delete a webhook', action='store_true')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()
    if args.p is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.p

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    print("Signing in to " + args.server + " [" + args.site + "] as " + args.username)
    server = TSC.Server(args.server)

    # Set http options to disable verifying SSL
    server.add_http_options({'verify': False})

    server.use_server_version()

    with server.auth.sign_in(tableau_auth):

        # Create webhook if create flag is set (-create, -c)
        if args.create:

            new_webhook = TSC.WebhookItem()
            new_webhook.name = args.create
            new_webhook.url = "https://ifttt.com/maker-url"
            new_webhook.event = "datasource-created"
            print(new_webhook)
            new_webhook = server.webhooks.create(new_webhook)
            print("Webhook created. ID: {}".format(new_webhook.id))

        # Gets all webhook items
        all_webhooks, pagination_item = server.webhooks.get()
        print("\nThere are {} webhooks on site: ".format(pagination_item.total_available))
        print([webhook.name for webhook in all_webhooks])

        if all_webhooks:
            # Pick one webhook from the list and delete it
            sample_webhook = all_webhooks[0]
            # sample_webhook.delete()
            print("+++"+sample_webhook.name)

            if (args.delete):
                print("Deleting webhook " + sample_webhook.name)
                server.webhooks.delete(sample_webhook.id)


if __name__ == '__main__':
    main()

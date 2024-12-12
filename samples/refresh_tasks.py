####
# This script demonstrates how to use the Tableau Server Client
# to query extract refresh tasks and run them as needed.
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging

import tableauserverclient as TSC


def handle_run(server, args):
    task = server.tasks.get_by_id(args.id)
    print(server.tasks.run(task))


def handle_list(server, _):
    tasks, pagination = server.tasks.get()
    for task in tasks:
        print(f"{task}")


def handle_info(server, args):
    task = server.tasks.get_by_id(args.id)
    print(f"{task}")


def main():
    parser = argparse.ArgumentParser(description="Get all of the refresh tasks available on a server")
    # Common options; please keep those in sync across all samples
    parser.add_argument("--server", "-s", help="server address")
    parser.add_argument("--site", "-S", help="site name")
    parser.add_argument("--token-name", "-p", help="name of the personal access token used to sign into the server")
    parser.add_argument("--token-value", "-v", help="value of the personal access token used to sign into the server")
    parser.add_argument(
        "--logging-level",
        "-l",
        choices=["debug", "info", "error"],
        default="error",
        help="desired logging level (set to error by default)",
    )
    # Options specific to this sample
    subcommands = parser.add_subparsers()

    list_arguments = subcommands.add_parser("list")
    list_arguments.set_defaults(func=handle_list)

    run_arguments = subcommands.add_parser("run")
    run_arguments.add_argument("id", default=None)
    run_arguments.set_defaults(func=handle_run)

    info_arguments = subcommands.add_parser("info")
    info_arguments.add_argument("id", default=None)
    info_arguments.set_defaults(func=handle_info)

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        args.func(server, args)


if __name__ == "__main__":
    main()

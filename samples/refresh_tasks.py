####
# This script demonstrates how to use the Tableau Server Client
# to query extract refresh tasks and run them as needed.
#
# To run the script, you must have installed Python 3.10 or later.
####

import argparse
import logging

import tableauserverclient as TSC

from _shared import add_common_arguments, build_auth, resolve_credentials


def handle_run(server, args):
    task = server.tasks.get_by_id(args.id)
    print(server.tasks.run(task))


def handle_list(server, _):
    # Use TSC.Pager to iterate every task; `.get()` returns only the first page.
    for task in TSC.Pager(server.tasks):
        print(f"{task}")


def handle_info(server, args):
    task = server.tasks.get_by_id(args.id)
    print(f"{task}")


def main():
    parser = argparse.ArgumentParser(description="Get all of the refresh tasks available on a server")
    add_common_arguments(parser)
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

    resolve_credentials(args)
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    tableau_auth = build_auth(args)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        args.func(server, args)


if __name__ == "__main__":
    main()

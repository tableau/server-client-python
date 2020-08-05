####
# This script demonstrates how to set the refresh schedule for
# a workbook or datasource.
#
# To run the script, you must have installed Python 3.5 or later.
####


import argparse
import getpass
import logging

import tableauserverclient as TSC


def usage(args):
    parser = argparse.ArgumentParser(description='Set refresh schedule for a workbook or datasource.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('--password', '-p', default=None)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--workbook', '-w')
    group.add_argument('--datasource', '-d')
    parser.add_argument('schedule')

    return parser.parse_args(args)


def make_filter(**kwargs):
    options = TSC.RequestOptions()
    for item, value in kwargs.items():
        name = getattr(TSC.RequestOptions.Field, item)
        options.filter.add(TSC.Filter(name, TSC.RequestOptions.Operator.Equals, value))
    return options


def get_workbook_by_name(server, name):
    request_filter = make_filter(Name=name)
    workbooks, _ = server.workbooks.get(request_filter)
    assert len(workbooks) == 1
    return workbooks.pop()


def get_datasource_by_name(server, name):
    request_filter = make_filter(Name=name)
    datasources, _ = server.datasources.get(request_filter)
    assert len(datasources) == 1
    return datasources.pop()


def get_schedule_by_name(server, name):
    schedules = [x for x in TSC.Pager(server.schedules) if x.name == name]
    assert len(schedules) == 1
    return schedules.pop()


def assign_to_schedule(server, workbook_or_datasource, schedule):
    server.schedules.add_to_schedule(schedule.id, workbook_or_datasource)


def run(args):
    password = args.password
    if password is None:
        password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        if args.workbook:
            item = get_workbook_by_name(server, args.workbook)
        else:
            item = get_datasource_by_name(server, args.datasource)
        schedule = get_schedule_by_name(server, args.schedule)

        assign_to_schedule(server, item, schedule)


def main():
    import sys
    args = usage(sys.argv[1:])
    run(args)


if __name__ == "__main__":
    main()

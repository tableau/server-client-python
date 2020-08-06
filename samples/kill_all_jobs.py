####
# This script demonstrates how to kill all of the running jobs
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='Cancel all of the running background jobs.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-S', default=None, help='site to log into, do not specify for default site')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--password', '-p', default=None, help='password for the user')

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    if args.password is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.password

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        req = TSC.RequestOptions()

        req.filter.add(TSC.Filter("progress", TSC.RequestOptions.Operator.LessThanOrEqual, 0))
        for job in TSC.Pager(server.jobs, request_opts=req):
            print(server.jobs.cancel(job.id), job.id, job.status, job.type)


if __name__ == '__main__':
    main()

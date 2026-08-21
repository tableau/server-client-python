####
# This script demonstrates how to use the Tableau Server Client to interact with extracts.
# It explores the different functions that the REST API supports on extracts.
#####

import argparse
import logging

import tableauserverclient as TSC

from _shared import add_common_arguments, build_auth, resolve_credentials


def main():
    parser = argparse.ArgumentParser(description="Explore extract functions supported by the Server API.")
    add_common_arguments(parser)
    # Options specific to this sample
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--workbook", required=False)
    parser.add_argument("--datasource", required=False)
    args = parser.parse_args()

    resolve_credentials(args)
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    tableau_auth = build_auth(args)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        wb = None
        ds = None
        if args.workbook:
            wb = server.workbooks.get_by_id(args.workbook)
            if wb is None:
                raise ValueError(f"Workbook not found for id {args.workbook}")
        elif args.datasource:
            ds = server.datasources.get_by_id(args.datasource)
            if ds is None:
                raise ValueError(f"Datasource not found for id {args.datasource}")
        else:
            # Gets all workbook items. `.get()` returns only the first page,
            # so we use TSC.Pager to iterate every page.
            first_page, pagination_item = server.workbooks.get()
            print(f"\nThere are {pagination_item.total_available} workbooks on site: ")
            all_workbooks = list(TSC.Pager(server.workbooks))
            print([workbook.name for workbook in all_workbooks])

            if all_workbooks:
                # Pick one workbook from the list
                wb = all_workbooks[3]

        if args.create:
            print("create extract on wb ", wb.name)
            extract_job = server.workbooks.create_extract(wb, includeAll=True)
            print(extract_job)

        if args.refresh:
            extract_job = None
            if ds is not None:
                print(f"refresh extract on datasource {ds.name}")
                extract_job = server.datasources.refresh(ds, includeAll=True, incremental=True)
            elif wb is not None:
                print(f"refresh extract on workbook {wb.name}")
                extract_job = server.workbooks.refresh(wb)
            else:
                print("no content item selected to refresh")

            print(extract_job)

        if args.delete:
            print("delete extract on wb ", wb.name)
            jj = server.workbooks.delete_extract(wb)
            print(jj)


if __name__ == "__main__":
    main()

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
    # --workbook / --datasource are mutually exclusive; if neither is passed we
    # fall back to picking the first workbook on the site (see below).
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--workbook")
    target.add_argument("--datasource")
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
                # Fall back to the first workbook on the site. For a real run,
                # pass --workbook <id> for a workbook you know has an extract.
                wb = all_workbooks[0]

        if args.create:
            if wb is None:
                print("no workbook selected to create an extract on")
            else:
                print(f"create extract on workbook {wb.name}")
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
            if wb is None:
                print("no workbook selected to delete an extract from")
            else:
                print(f"delete extract on workbook {wb.name}")
                jj = server.workbooks.delete_extract(wb)
                print(jj)


if __name__ == "__main__":
    main()

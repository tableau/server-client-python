####
# This script demonstrates how to export a view using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description="Export a view as an image, PDF, or CSV")
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--pdf", dest="type", action="store_const", const=("populate_pdf", "PDFRequestOptions", "pdf", "pdf")
    )
    group.add_argument(
        "--png", dest="type", action="store_const", const=("populate_image", "ImageRequestOptions", "image", "png")
    )
    group.add_argument(
        "--csv", dest="type", action="store_const", const=("populate_csv", "CSVRequestOptions", "csv", "csv")
    )
    # other options shown in explore_workbooks: workbook.download, workbook.preview_image
    parser.add_argument(
        "--language", help="Text such as 'Average' will appear in this language. Use values like fr, de, es, en"
    )
    parser.add_argument("--workbook", action="store_true")
    parser.add_argument("--custom_view", action="store_true")

    parser.add_argument("--file", "-f", help="filename to store the exported data")
    parser.add_argument("--filter", "-vf", metavar="COLUMN:VALUE", help="View filter to apply to the view")
    parser.add_argument("resource_id", help="LUID for the view or workbook")

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True, http_options={"verify": False})
    with server.auth.sign_in(tableau_auth):
        print("Connected")
        if args.workbook:
            item = server.workbooks.get_by_id(args.resource_id)
        elif args.custom_view:
            item = server.custom_views.get_by_id(args.resource_id)
        else:
            item = server.views.get_by_id(args.resource_id)

        if not item:
            print(f"No item found for id {args.resource_id}")
            exit(1)

        print(f"Item found: {item.name}")
        # We have a number of different types and functions for each different export type.
        # We encode that information above in the const=(...) parameter to the add_argument function to make
        # the code automatically adapt for the type of export the user is doing.
        # We unroll that information into methods we can call, or objects we can create by using getattr()
        (populate_func_name, option_factory_name, member_name, extension) = args.type
        populate = getattr(server.views, populate_func_name)
        if args.workbook:
            populate = getattr(server.workbooks, populate_func_name)
        elif args.custom_view:
            populate = getattr(server.custom_views, populate_func_name)

        option_factory = getattr(TSC, option_factory_name)
        options: TSC.PDFRequestOptions = option_factory()

        if args.filter:
            options = options.vf(*args.filter.split(":"))

        if args.language:
            options.language = args.language

        if args.file:
            filename = args.file
        else:
            filename = f"out-{options.language}.{extension}"

        populate(item, options)
        with open(filename, "wb") as f:
            if member_name == "csv":
                f.writelines(getattr(item, member_name))
            else:
                f.write(getattr(item, member_name))
        print("saved to " + filename)


if __name__ == "__main__":
    main()

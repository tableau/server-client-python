####
# This script demonstrates how to use the Tableau Server Client
# to interact with datasources. It explores the different
# functions that the Server API supports on datasources.
#
# With no flags set, this sample will query all datasources,
# pick one datasource and populate its connections, and update
# the datasource. Adding flags will demonstrate the specific feature
# on top of the general operations.
####

import argparse
import logging

import tableauserverclient as TSC

from _shared import add_common_arguments, build_auth, resolve_credentials


def main():
    parser = argparse.ArgumentParser(description="Explore datasource functions supported by the Server API.")
    add_common_arguments(parser)
    # Options specific to this sample
    parser.add_argument("--publish", metavar="FILEPATH", help="path to datasource to publish")
    parser.add_argument("--download", metavar="FILEPATH", help="path to save downloaded datasource")

    args = parser.parse_args()

    resolve_credentials(args)
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    tableau_auth = build_auth(args)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Query projects for use when demonstrating publishing and updating.
        # Use TSC.Pager (or `.all()` / `.filter()`) to iterate every page;
        # a raw `server.projects.get()` only returns the first page.
        default_project = next((project for project in TSC.Pager(server.projects) if project.is_default()), None)

        # Publish datasource if publish flag is set (-publish, -p)
        if args.publish:
            if default_project is not None:
                new_datasource = TSC.DatasourceItem(default_project.id)
                new_datasource.description = "Published with a description"
                new_datasource = server.datasources.publish(
                    new_datasource, args.publish, TSC.Server.PublishMode.Overwrite
                )
                print(f"Datasource published. ID: {new_datasource.id}")
            else:
                print("Publish failed. Could not find the default project.")

        # Gets all datasource items. `.get()` returns only one page; use
        # TSC.Pager to iterate every page. The first response also gives us
        # the total_available count without paging through everything.
        first_page, pagination_item = server.datasources.get()
        print(f"\nThere are {pagination_item.total_available} datasources on site: ")
        all_datasources = list(TSC.Pager(server.datasources))
        print([datasource.name for datasource in all_datasources])

        if all_datasources:
            # Pick one datasource from the list
            sample_datasource = all_datasources[0]

            # Populate connections
            server.datasources.populate_connections(sample_datasource)
            print(f"\nConnections for {sample_datasource.name}: ")
            print([f"{connection.id}({connection.datasource_name})" for connection in sample_datasource.connections])

            # Demonstrate that description is editable
            sample_datasource.description = "Description updated by TSC"
            server.datasources.update(sample_datasource)

            # Add some tags to the datasource
            original_tag_set = set(sample_datasource.tags)
            sample_datasource.tags.update("a", "b", "c", "d")
            server.datasources.update(sample_datasource)
            print(f"\nOld tag set: {original_tag_set}")
            print(f"New tag set: {sample_datasource.tags}")

            # Delete all tags that were added by setting tags to original
            sample_datasource.tags = original_tag_set
            server.datasources.update(sample_datasource)


if __name__ == "__main__":
    main()

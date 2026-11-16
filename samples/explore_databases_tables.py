####
# This script demonstrates how to use the Tableau Server Client
# to read database and table assets. It explores the read-only
# functions that the Server API supports on databases and tables.
#
# With no flags set, this sample will query all databases, pick one
# database and print its details, list the tables in that database,
# then populate and list the columns of one table. Adding the
# --permissions flag also prints the permissions on the database
# and table.
#
# Databases and tables are external assets. Your site must be
# licensed with Data Management for the server to return them.
####

import argparse
import logging

import tableauserverclient as TSC

from _shared import add_common_arguments, build_auth, resolve_credentials

# databases.populate_tables is not enabled in TSC, so we use the Metadata API
# to find which tables belong to a database, then read them over REST.
DATABASE_TABLES_QUERY = """
query tablesInDatabase($luid: String) {
    databases(filter: {luid: $luid}) {
        name
        tables {
            luid
            name
        }
    }
}
"""


def print_permissions(item):
    for rule in item.permissions:
        print(f"    {rule.grantee.tag_name} {rule.grantee.id}: {rule.capabilities}")


def main():
    parser = argparse.ArgumentParser(description="Explore database and table functions supported by the Server API.")
    add_common_arguments(parser)
    # Options specific to this sample
    parser.add_argument("--database-name", help="name of the database to explore (defaults to the first one found)")
    parser.add_argument("--permissions", help="also print database and table permissions", action="store_true")

    args = parser.parse_args()

    resolve_credentials(args)
    logging.basicConfig(level=getattr(logging, args.logging_level.upper()))

    tableau_auth = build_auth(args)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Gets all database items. `.get()` returns only one page; use
        # TSC.Pager to iterate every database on the site.
        first_page, pagination_item = server.databases.get()
        print(f"\nThere are {pagination_item.total_available} databases on site: ")
        all_databases = list(TSC.Pager(server.databases))
        print([database.name for database in all_databases])

        if args.database_name:
            matches = [database for database in all_databases if database.name == args.database_name]
        else:
            matches = all_databases
        if not matches:
            print("\nNo matching database found.")
            return

        sample_database = server.databases.get_by_id(matches[0].id)
        print(f"\nDetails for database {sample_database.name}:")
        print(f"    id: {sample_database.id}")
        print(f"    connection type: {sample_database.connection_type}")
        print(f"    host: {sample_database.host_name}:{sample_database.port}")
        print(f"    embedded: {sample_database.embedded}")
        print(f"    certified: {sample_database.certified}")
        print(f"    description: {sample_database.description}")
        print(f"    contact id: {sample_database.contact_id}")

        if args.permissions:
            server.databases.populate_permissions(sample_database)
            print(f"\nPermissions for database {sample_database.name}:")
            print_permissions(sample_database)

        result = server.metadata.query(DATABASE_TABLES_QUERY, {"luid": sample_database.id})
        databases_data = (result.get("data") or {}).get("databases") or []
        if result.get("errors"):
            print(f"\nMetadata API returned errors: {result['errors']}")
            if not databases_data:
                return
        table_refs = databases_data[0]["tables"] if databases_data else []
        print(f"\nThere are {len(table_refs)} tables in database {sample_database.name}: ")
        print([table_ref["name"] for table_ref in table_refs])

        if not table_refs:
            return

        sample_table = server.tables.get_by_id(table_refs[0]["luid"])
        print(f"\nDetails for table {sample_table.name}:")
        print(f"    id: {sample_table.id}")
        print(f"    schema: {sample_table.schema}")
        print(f"    certified: {sample_table.certified}")
        print(f"    description: {sample_table.description}")

        # `columns` is a Pager, so this iterates every page of columns.
        server.tables.populate_columns(sample_table)
        print(f"\nColumns in table {sample_table.name}: ")
        for column in sample_table.columns:
            print(f"    {column.name} ({column.remote_type})")

        if args.permissions:
            server.tables.populate_permissions(sample_table)
            print(f"\nPermissions for table {sample_table.name}:")
            print_permissions(sample_table)


if __name__ == "__main__":
    main()

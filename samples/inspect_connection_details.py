####
# This script demonstrates how to read connector-specific connection attributes
# (Oracle service, Snowflake schema, Teradata query-band, initial SQL, etc.) that
# the Tableau REST API's `<connection>` element does NOT expose.
#
# The REST API's `.populate_connections()` surface only carries generic fields
# (id, type, server_address, server_port, username, embed_password, auth_type).
# The full set of connector-specific attributes lives inside the workbook or
# datasource file itself. This sample downloads the file via TSC, then parses it
# with the community `tableaudocumentapi` library to reach the extra attributes.
#
# Requires:
#   pip install tableauserverclient tableau-document-api
#
# Related GitHub issues:
#   - server-client-python#1807 (Oracle service on ConnectionItem)
#   - server-client-python#1571 (database_name on ConnectionItem)
#   - server-client-python#160  (queryband, initial_sql)
#   - server-client-python#353  (SQL Server database + schema + table)
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging
import tempfile

import tableauserverclient as TSC

try:
    from tableaudocumentapi import Datasource, Workbook
except ImportError:
    raise SystemExit(
        "This sample requires the tableau-document-api package.\n" "Install it with: pip install tableau-document-api"
    )


def dump_connections_from_datasource_file(path):
    """Print connector-specific attributes for every connection inside a .tds/.tdsx file."""
    ds = Datasource.from_file(path)
    for i, c in enumerate(ds.connections, start=1):
        _print_connection(f"datasource conn #{i}", c)


def dump_connections_from_workbook_file(path):
    """Print connector-specific attributes for every connection across every
    embedded datasource inside a .twb/.twbx file."""
    wb = Workbook(path)
    for di, ds in enumerate(wb.datasources, start=1):
        for ci, c in enumerate(ds.connections, start=1):
            _print_connection(f"workbook datasource #{di}, conn #{ci}", c)


def _print_connection(label, c):
    print(f"--- {label} ---")
    # Every attribute below comes from the raw XML embedded in the file; none of
    # these are exposed by TSC's ConnectionItem today.
    print(f"  dbclass:      {c.dbclass}")
    print(f"  server:       {c.server}")
    print(f"  port:         {c.port}")
    print(f"  username:     {c.username}")
    print(f"  dbname:       {c.dbname}")
    print(f"  schema:       {c.schema}")
    print(f"  service:      {c.service}")
    print(f"  authentication: {c.authentication}")
    print(f"  query_band:   {c.query_band}")
    print(f"  initial_sql:  {c.initial_sql}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Inspect connector-specific connection attributes for a datasource or workbook. "
            "Downloads the item via TSC, then parses its embedded XML with tableau-document-api."
        )
    )
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
    parser.add_argument("resource_type", choices=["workbook", "datasource"])
    parser.add_argument("resource_id", help="LUID of the workbook or datasource")

    args = parser.parse_args()

    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)

    with server.auth.sign_in(tableau_auth):
        endpoint = server.workbooks if args.resource_type == "workbook" else server.datasources
        with tempfile.TemporaryDirectory() as tmp:
            # include_extract=False keeps downloads small; extract bytes are not
            # needed to read the <connection> XML.
            path = endpoint.download(args.resource_id, filepath=tmp, include_extract=False)
            print(f"Downloaded to {path}")
            if args.resource_type == "workbook":
                dump_connections_from_workbook_file(path)
            else:
                dump_connections_from_datasource_file(path)


if __name__ == "__main__":
    main()

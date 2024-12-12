####
# This script demonstrates how to use the Tableau Server Client
# to filter and sort on the name of the projects present on site.
#
# To run the script, you must have installed Python 3.7 or later.
####

import argparse
import logging
import urllib.parse

import tableauserverclient as TSC


def create_example_project(
    name="Example Project",
    content_permissions="LockedToProject",
    description="Project created for testing",
    server=None,
):
    new_project = TSC.ProjectItem(name=name, content_permissions=content_permissions, description=description)
    try:
        server.projects.create(new_project)
        print("Created a new project called: %s" % name)
    except TSC.ServerResponseError:
        print("We have already created this resource: %s" % name)


def main():
    parser = argparse.ArgumentParser(description="Filter and sort projects.")
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
    # This sample has no additional options, yet. If you add some, please add them here

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.PersonalAccessTokenAuth(args.token_name, args.token_value, site_id=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Use highest Server REST API version available
        server.use_server_version()

        filter_project_name = "default"
        options = TSC.RequestOptions()

        options.filter.add(
            TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, filter_project_name)
        )

        filtered_projects, _ = server.projects.get(req_options=options)
        # Result can either be a matching project or an empty list
        if filtered_projects:
            project_name = filtered_projects.pop().name
            print(project_name)
        else:
            error = f"No project named '{filter_project_name}' found"
            print(error)

        create_example_project(name="Example 1", server=server)
        create_example_project(name="Example 2", server=server)
        create_example_project(name="Example 3", server=server)
        create_example_project(name="Proiect ca Exemplu", server=server)

        options = TSC.RequestOptions()

        # don't forget to URL encode the query names
        options.filter.add(
            TSC.Filter(
                TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.In, ["Example+1", "Example+2", "Example+3"]
            )
        )

        options.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Desc))

        matching_projects, pagination_item = server.projects.get(req_options=options)
        print("Filtered projects are:")
        for project in matching_projects:
            print(project.name, project.id)

        # Or, try the django style filtering.
        projects = ["Example 1", "Example 2", "Example 3"]
        projects = [urllib.parse.quote_plus(p) for p in projects]
        for project in server.projects.filter(name__in=projects).sort("-name"):
            print(project.name, project.id)


if __name__ == "__main__":
    main()

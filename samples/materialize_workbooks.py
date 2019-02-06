import argparse
import getpass
import logging
import tableauserverclient as TSC
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(description='Materialized views settings for sites/workbooks.')
    parser.add_argument('--server', '-s', required=True, help='Tableau server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--password', '-p', required=False, help='password to sign into server')
    parser.add_argument('--mode', '-m', required=False, choices=['disable', 'enable', 'enable_all', 'enable_selective'],
                        help='enable/disable materialized views for sites/workbooks')
    parser.add_argument('--status', '-st', required=False, action='store_true',
                        help='show materialized views enabled sites/workbooks')
    parser.add_argument('--site-id', '-si', required=False,
                        help='set to Default site by default')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('--type', '-t', required=False, choices=['site', 'workbook', 'project_name', 'project_path'],
                        help='type of content you want to update materialized views settings on')
    parser.add_argument('--path-list', '-pl', required=False, help='path to a list of workbook paths')
    parser.add_argument('--name-list', '-nl', required=False, help='path to a list of workbook names')
    parser.add_argument('--project-name', '-pn', required=False, help='name of the project')
    parser.add_argument('--project-path', '-pp', required=False, help="path of the project")
    parser.add_argument('--materialize-now', '-mn', required=False, action='store_true',
                        help='create materialized views for workbooks immediately')

    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Password: ")

    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # site content url is the TSC term for site id
    site_content_url = args.site_id if args.site_id is not None else ""

    if not assert_options_valid(args):
        return

    materialized_views_config = create_materialized_views_config(args)

    # enable/disable materialized views for site
    if args.type == 'site':
        if not update_site(args, password, site_content_url):
            return

    # enable/disable materialized views for workbook
    # works only when the site the workbooks belong to are enabled too
    elif args.type == 'workbook':
        if not update_workbook(args, materialized_views_config, password, site_content_url):
            return

    # enable/disable materialized views for project by project name
    # will show possible projects when project name is not unique
    elif args.type == 'project_name':
        if not update_project_by_name(args, materialized_views_config, password, site_content_url):
            return

    # enable/disable materialized views for project by project path, for example: project1/project2
    elif args.type == 'project_path':
        if not update_project_by_path(args, materialized_views_config, password, site_content_url):
            return

    # show enabled sites and workbooks
    if args.status:
        show_materialized_views_status(args, password, site_content_url)


def find_project_path(project, all_projects, path):
    # project stores the id of it's parent
    # this method is to run recursively to find the path from root project to given project
    path = project.name if len(path) == 0 else project.name + '/' + path

    if project.parent_id is None:
        return path
    else:
        return find_project_path(all_projects[project.parent_id], all_projects, path)


def get_project_paths(server, projects):
    # most likely user won't have too many projects so we store them in a dict to search
    all_projects = {project.id: project for project in TSC.Pager(server.projects)}

    result = dict()
    for project in projects:
        result[find_project_path(project, all_projects, "")] = project
    return result


def print_paths(paths):
    for path in paths.keys():
        print(path)


def show_materialized_views_status(args, password, site_content_url):
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
    server = TSC.Server(args.server, use_server_version=True)
    enabled_sites = set()
    with server.auth.sign_in(tableau_auth):
        # For server admin, this will prints all the materialized views enabled sites
        # For other users, this only prints the status of the site they belong to
        print("Materialized views is enabled on sites:")
        # only server admins can get all the sites in the server
        # other users can only get the site they are in
        for site in TSC.Pager(server.sites):
            if site.materialized_views_mode != "disable":
                enabled_sites.add(site)
                print("Site name: {}".format(site.name))
        print('\n')

    print("Materialized views is enabled on workbooks:")
    # Individual workbooks can be enabled only when the sites they belong to are enabled too
    for site in enabled_sites:
        site_auth = TSC.TableauAuth(args.username, password, site.content_url)
        with server.auth.sign_in(site_auth):
            for workbook in TSC.Pager(server.workbooks):
                if workbook.materialized_views_config['materialized_views_enabled']:
                    print("Workbook: {} from site: {}".format(workbook.name, site.name))


def update_project_by_path(args, materialized_views_mode, password, site_content_url):
    if args.project_path is None:
        print("Use --project_path <project path> to specify the path of the project")
        return False
    tableau_auth = TSC.TableauAuth(args.username, password, site_content_url)
    server = TSC.Server(args.server, use_server_version=True)
    project_name = args.project_path.split('/')[-1]
    with server.auth.sign_in(tableau_auth):
        if not assert_site_enabled_for_materialized_views(server, site_content_url):
            return False
        projects = [project for project in TSC.Pager(server.projects) if project.name == project_name]
        if not assert_project_valid(args.project_path, projects):
            return False

        possible_paths = get_project_paths(server, projects)
        update_project(possible_paths[args.project_path], server, materialized_views_mode)
    return True


def update_project_by_name(args, materialized_views_config, password, site_content_url):
    if args.project_name is None:
        print("Use --project-name <project name> to specify the name of the project")
        return False
    tableau_auth = TSC.TableauAuth(args.username, password, site_content_url)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        if not assert_site_enabled_for_materialized_views(server, site_content_url):
            return False
        # get all projects with given name
        projects = [project for project in TSC.Pager(server.projects) if project.name == args.project_name]
        if not assert_project_valid(args.project_name, projects):
            return False

        if len(projects) > 1:
            possible_paths = get_project_paths(server, projects)
            print("Project name is not unique, use '--project_path <path>'")
            print("Possible project paths:")
            print_paths(possible_paths)
            print('\n')
            return False
        else:
            update_project(projects[0], server, materialized_views_config)
    return True


def update_project(project, server, materialized_views_config):
    for workbook in TSC.Pager(server.workbooks):
        if workbook.project_id == project.id:
            workbook.materialized_views_config = materialized_views_config
            server.workbooks.update(workbook)

    print("Updated materialized views settings for project: {}".format(project.name))
    print('\n')


def parse_workbook_path(file_path):
    # parse the list of project path of workbooks
    workbook_paths = open(file_path, 'r')
    workbook_path_mapping = defaultdict(list)
    for workbook_path in workbook_paths:
        workbook_project = workbook_path.rstrip().split('/')
        workbook_path_mapping[workbook_project[-1]].append('/'.join(workbook_project[:-1]))
    return workbook_path_mapping


def update_workbook(args, materialized_views_config, password, site_content_url):
    if args.path_list is None and args.name_list is None:
        print("Use '--path-list <filename>' or '--name-list <filename>' to specify the path of a list of workbooks")
        print('\n')
        return False
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        if not assert_site_enabled_for_materialized_views(server, site_content_url):
            return False
        if args.path_list is not None:
            workbook_path_mapping = parse_workbook_path(args.path_list)
            all_projects = {project.id: project for project in TSC.Pager(server.projects)}
            update_workbooks_by_paths(all_projects, materialized_views_config, server, workbook_path_mapping)
        elif args.name_list is not None:
            update_workbooks_by_names(args.name_list, server, materialized_views_config)
    return True


def update_workbooks_by_paths(all_projects, materialized_views_config, server, workbook_path_mapping):
    for workbook_name, workbook_paths in workbook_path_mapping.items():
        req_option = TSC.RequestOptions()
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                         TSC.RequestOptions.Operator.Equals,
                                         workbook_name))
        workbooks = list(TSC.Pager(server.workbooks, req_option))
        for workbook in workbooks:
            path = find_project_path(all_projects[workbook.project_id], all_projects, "")
            if path in workbook_paths:
                workbook.materialized_views_config = materialized_views_config
                server.workbooks.update(workbook)
                print("Updated materialized views settings for workbook: {}".format(path + '/' + workbook.name))
    print('\n')


def update_workbooks_by_names(name_list, server, materialized_views_config):
    workbook_names = open(name_list, 'r')
    for workbook_name in workbook_names:
        req_option = TSC.RequestOptions()
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                         TSC.RequestOptions.Operator.Equals,
                                         workbook_name.rstrip()))
        workbooks = list(TSC.Pager(server.workbooks, req_option))
        for workbook in workbooks:
            workbook.materialized_views_config = materialized_views_config
            server.workbooks.update(workbook)
            print("Updated materialized views settings for workbook: {}".format(workbook.name))
    print('\n')


def update_site(args, password, site_content_url):
    if not assert_site_options_valid(args):
        return False
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=site_content_url)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        site_to_update = server.sites.get_by_content_url(site_content_url)
        site_to_update.materialized_views_mode = args.mode

        server.sites.update(site_to_update)
        print("Updated materialized views settings for site: {}".format(site_to_update.name))
    print('\n')
    return True


def create_materialized_views_config(args):
    materialized_views_config = dict()
    materialized_views_config['materialized_views_enabled'] = args.mode == "enable"
    materialized_views_config['run_materialization_now'] = True if args.materialize_now else False
    return materialized_views_config


def assert_site_options_valid(args):
    if args.materialize_now:
        print('"--materialize-now" only applies to workbook/project type')
        return False
    if args.mode == 'enable':
        print('For site type please choose from "disable", "enable_all", or "enable_selective"')
        return False
    return True


def assert_options_valid(args):
    if args.type != "site" and args.mode in ("enable_all", "enable_selective"):
        print('"enable_all" and "enable_selective" do not apply to workbook/project type')
        return False
    if (args.type is None) != (args.mode is None):
        print("Use '--type <content type> --mode <mode>' to update materialized views settings.")
        return False
    return True


def assert_site_enabled_for_materialized_views(server, site_content_url):
    parent_site = server.sites.get_by_content_url(site_content_url)
    if parent_site.materialized_views_mode == "disable":
        print('Cannot update workbook/project because site is disabled for materialized views')
        return False
    return True


def assert_project_valid(project_name, projects):
    if len(projects) == 0:
        print("Cannot find project: {}".format(project_name))
        return False
    return True


if __name__ == "__main__":
    main()

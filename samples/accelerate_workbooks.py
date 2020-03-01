import requests  # Contains methods used to make HTTP requests
import requests
from urllib3.exceptions import InsecureRequestWarning
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML
import sys

import argparse
import getpass
import logging
import os
from prettytable import PrettyTable
import textwrap

from dateutil import tz

import tableauserverclient as TSC
from collections import defaultdict
from datetime import time

from tableauserverclient import ServerResponseError

# The following packages are used to build a multi-part/mixed request.
# They are contained in the 'requests' library
from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata

# The namespace for the REST API is 'http://tableausoftware.com/api' for Tableau Server 9.0
# or 'http://tableau.com/api' for Tableau Server 9.1 or later
xmlns = {'t': 'http://tableau.com/api'}

VERSION = 3.6
tokenFile = ".token_profile"

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64  # 64MB

# For when a workbook is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB

# If using python version 3.x, 'raw_input()' is changed to 'input()'
if sys.version[0] == '3': raw_input = input


class ApiCallError(Exception):
    pass


class UserDefinedFieldError(Exception):
    pass


def _encode_for_display(text):
    """
    Encodes strings so they can display as ASCII in a Windows terminal window.
    This function also encodes strings for processing by xml.etree.ElementTree functions.

    Returns an ASCII-encoded version of the text.
    Unicode characters are converted to ASCII placeholders (for example, "?").
    """
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')


def sign_out_existing_connection(server):
    """
    Destroys the active session and invalidates authentication token.
    'server'        server
    """
    removeTokenFile()
    try:
        if server is not None:
            server.auth.sign_out()
            print("Signed out from current connection to {} successfully".format(server.server_address))
    except Exception as ex:
        print("Unable to sign out {} due to {}.".format(server.server_address, ex))
    return


def sign_in_to_server(server, username, password, site="", ssl_cert_pem=None):
    """
    Signs in to the server specified with the given credentials
    'server'   specified server address
    'username' is the name (not ID) of the user to sign in as.
               Note that most of the functions in this example require that the user
               have server administrator permissions.
    'password' is the password for the user.
    'site'     is the ID (as a string) of the site on the server to sign in to. The
               default is "", which signs in to the default site.
    'ssl_cert_pem' is the file path to the ssl certificate in pem format
    Returns the authentication token and the site ID.
    """
    url = None
    if "http:" in server.lower() or "https:" in server.lower():
        url = "{}/api/{}/auth/signin".format(server, VERSION)
    else:
        url = "http://{}/api/{}/auth/signin".format(server, VERSION)

    ssl_cert_pem = ssl_cert_pem if ssl_cert_pem is not None else False

    # Builds the request
    xml_request = ET.Element('tsRequest')
    credentials_element = ET.SubElement(xml_request, 'credentials', name=username, password=password)
    ET.SubElement(credentials_element, 'site', contentUrl=site)
    xml_request = ET.tostring(xml_request)

    # Make the request to server
    server_response = requests.post(url, data=xml_request, verify=ssl_cert_pem)
    _check_status(server_response, 200)

    # ASCII encode server response to enable displaying to console
    server_response = _encode_for_display(server_response.text)

    # Reads and parses the response
    parsed_response = ET.fromstring(server_response)

    # Gets the auth token and site ID
    token = parsed_response.find('t:credentials', namespaces=xmlns).get('token')
    site_id = parsed_response.find('.//t:site', namespaces=xmlns).get('id')
    user_id = parsed_response.find('.//t:user', namespaces=xmlns).get('id')
    writeTokenToFile(token, site_id, user_id, server, ssl_cert_pem)
    putTokenInEnv(token, site_id, user_id, server, ssl_cert_pem)
    return token, site_id, user_id


def _check_status(server_response, success_code):
    """
    Checks the server response for possible errors.
    'server_response'       the response received from the server
    'success_code'          the expected success code for the response
    Throws an ApiCallError exception if the API call fails.
    """
    if server_response.status_code != success_code:
        parsed_response = ET.fromstring(server_response.text)

        # Obtain the 3 xml tags from the response: error, summary, and detail tags
        error_element = parsed_response.find('t:error', namespaces=xmlns)
        summary_element = parsed_response.find('.//t:summary', namespaces=xmlns)
        detail_element = parsed_response.find('.//t:detail', namespaces=xmlns)

        # Retrieve the error code, summary, and detail if the response contains them
        code = error_element.get('code', 'unknown') if error_element is not None else 'unknown code'
        summary = summary_element.text if summary_element is not None else 'unknown summary'
        detail = detail_element.text if detail_element is not None else 'unknown detail'
        error_message = '{0}: {1} - {2}'.format(code, summary, detail)
        raise ApiCallError(error_message)
    return


def removeTokenFile():
    if os.path.exists(tokenFile):
        try:
            os.remove(tokenFile)
        except OSError as e:
            pass


def writeTokenToFile(token="", site_id="", user_id="", server_url="", ssl_cert_pem=""):
    f = open(tokenFile, "w+")
    f.write(token + " " + site_id + " " + user_id + " " + server_url + " " + ssl_cert_pem)
    f.close()


def promptUsernamePass(args, current_server_address=None):
    if args.server is not None:
        server_url = args.server
    elif current_server_address is not None:
        server_url = current_server_address
    else:
        server_url = raw_input("server: ")

    site = raw_input("site (hit enter for the Default site): ") if args.site is None else args.site
    username = raw_input("username: ") if args.username is None else args.username
    password = getpass.getpass("password: ") if args.password is None else args.password

    if not ("http://" in server_url.lower() or "https://" in server_url.lower()):
        server_url = "http://" + server_url

    ssl_cert_pem = ""
    if "https:" in server_url.lower():
        ssl_cert_pem = raw_input("path to ssl certificate (hit enter to ignore): ") \
            if args.ssl_cert_pem is None else args.ssl_cert_pem

    return server_url, site, username, password, ssl_cert_pem


def readTokenFromFile():
    token = None
    if os.path.exists(tokenFile):
        f = open(tokenFile, "r")
        if f.mode == 'r':
            token = f.read()

        f.close()

    if token:
        return token.split(' ')

    return None, None, None, None, None


def readTokenFromEnv():
    return os.getenv('auth_token'), os.getenv('site_id'), os.getenv('user_id'), \
           os.getenv('server_url'), os.getenv('ssl_cert_pem')


def putTokenInEnv(auth_token, site_id, user_id, serverurl, ssl_cert_pem):
    os.environ['auth_token'] = auth_token
    os.environ['site_id'] = site_id
    os.environ['user_id'] = user_id
    os.environ['server_url'] = serverurl
    os.environ['ssl_cert_pem'] = ssl_cert_pem


def sign_in(args, current_server_address=None):
    serverurl, site, username, password, ssl_cert_pem = promptUsernamePass(args, current_server_address)

    try:
        auth_token, site_id, user_id = sign_in_to_server(serverurl, username, password, site, ssl_cert_pem)
        server = set_up_tsc_server(serverurl, site_id, user_id, auth_token, ssl_cert_pem)
        if server is not None:
            print("Signed in to {} successfully".format(serverurl))
        return server
    except ApiCallError as error:
        print("\n{}, please verify your username, password, and site.".format(error))
        return None
    except:
        print("Unable to connect to {}".format(serverurl))
        return None


def set_up_tsc_server(serverurl, site_id, user_id,
                      auth_token, ssl_cert_pem):
    server = TSC.Server(serverurl)

    if "https:" in serverurl.lower():
        server.add_http_options({'verify': ssl_cert_pem if len(ssl_cert_pem) > 0 else False})

    server._set_auth(site_id, user_id, auth_token)

    server.use_server_version()

    return server if connection_alive(server) else None


def connection_alive(server):
    try:
        server.sites.get()
        return True
    except:
        return False


def cleanStrings(auth_token, site_id, user_id, serverurl, ssl_cert_pem):
    return auth_token.strip(), site_id.strip(), user_id.strip(), serverurl.strip(), ssl_cert_pem.strip()


def get_session_connection_to_server():
    try:
        auth_token, site_id, user_id, serverurl, ssl_cert_pem = readTokenFromEnv()
        if not auth_token:
            auth_token, site_id, user_id, serverurl, ssl_cert_pem = readTokenFromFile()
            if auth_token:
                try:
                    auth_token, site_id, user_id, serverurl, ssl_cert_pem = cleanStrings(auth_token, site_id,
                                                                                         user_id, serverurl,
                                                                                         ssl_cert_pem)
                except:
                    pass

        if auth_token is not None:
            if not ("http://" in serverurl.lower() or "https:" in serverurl.lower()):
                serverurl = "http:" + serverurl

            return set_up_tsc_server(serverurl, site_id,
                                     user_id, auth_token, ssl_cert_pem)
    except:
        pass
    return None


def sign_out():
    server = get_session_connection_to_server()
    if server is not None:
        sign_out_existing_connection(server)
    else:
        removeTokenFile()  # in case the auth token expires
        print("No existing connection to any server.")


def need_to_relogin(args, server):
    if server is None:
        return True

    current_site = None
    try:
        current_site = server.sites.get_by_id(server.site_id)
    except:
        pass

    current_site = current_site.content_url if current_site is not None else None
    current_server_address = server.server_address
    if not "http://" in current_server_address:
        current_server_address = "http://" + current_server_address

    new_site = args.site if args.site is not None else current_site
    new_server_address = args.server if args.server is not None else current_server_address
    if new_server_address is not None and not "http://" in new_server_address:
        new_server_address = "http://" + new_server_address

    return current_site != new_site or current_server_address != new_server_address


def get_authenticated_connection_to_server(args):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    server = get_session_connection_to_server()
    current_server_address = server.server_address if server is not None else None
    if need_to_relogin(args, server):
        sign_out_existing_connection(server)
    elif server is not None:
        return server
    return sign_in(args, current_server_address)


class UserResponse:
    YES = "y"
    NO = "n"
    YES_FOR_ALL = "a"
    NO_FOR_ALL = "q"


def assert_add_to_or_remove_from_schedule(schedule_action, args, schedule_string):
    if schedule_action is None:
        return True

    num_schedule_args = len(schedule_action)
    if num_schedule_args not in [1, 2]:
        print("{} should be followed by a schedule name and optionally a workbook path".format(schedule_string))
        return False
    elif num_schedule_args == 1 and args.path_list is None and args.workbook_path is None:
        print("Use --path-list and --workbook-path to specify workbooks")
        return False
    return True


def assert_show_schedules(show_schedules):
    if show_schedules is None:
        return True

    if not len(show_schedules) in [0, 1]:
        print("--show-schedules should be followed by a workbook path or use"
              "--path-list or -workbook-path to specify workbooks.")
        return False
    return True


def assert_create_schedule(args):
    if args.create_schedule is None:
        return True
    if sum(interval is not None for interval in [args.weekly_interval, args.daily_interval,
                                                 args.monthly_interval, args.hourly_interval]) != 1:
        print("Use --hourly-interval or --daily-interval or --weekly-interval or "
              "--monthly-interval to specify the schedule type\n")
        return False
    elif sum(option is not None for option in [args.workbook_path, args.path_list,
                                               args.enable, args.disable]) > 0:
        print("Create schedule with specifing interval only\n")
        return False
    return True


def assert_options_valid(args):
    if args.logout is not None and (args.server is not None or args.site is not None):
        print("Do not use --logout and --server at the same time.")
        return False

    if args.logout is not None or args.server is not None or args.site is not None:
        return True

    num_schedule_actions = sum(action is not None for action in
                               [args.add_to_schedule, args.remove_from_schedule, args.create_schedule,
                                args.show_schedules])

    num_enable_actions = sum(action is not None for action in
                             [args.enable, args.disable])

    if num_schedule_actions > 0 and num_enable_actions > 0 or num_schedule_actions > 1 or num_enable_actions > 1:
        print("Use --add-to-schedule, --remove-from-schedule, --create-schedule, or --show-schedules to "
              "schedule Workbook Acceleration tasks, or use --enable or --disable to enable or disable "
              "workbooks for Workbook Acceleration.\n")
        return False

    if num_schedule_actions == 1:
        if not assert_add_to_or_remove_from_schedule(args.add_to_schedule, args, "--add-to-schedule") \
                or not assert_add_to_or_remove_from_schedule(args.remove_from_schedule, args,
                                                             "--remove-from-schedule"):
            return False
        elif not assert_show_schedules(args.show_schedules):
            return False
        elif not assert_create_schedule(args):
            return False
        else:
            return True

    if num_enable_actions == 1:
        if args.enable is not None and len(args.enable) > 1:
            print('--enable can only be followed by one workbook path')
            return False
        elif args.disable is not None and len(args.disable) > 1:
            print('--disable can only followed by one workbook path')
            return False
        else:
            return True

    return args.status is not None


def handle_enable_disable_command(server, args, site_content_url):
    data_acceleration_config = create_data_acceleration_config(args)

    # enable/disable materialized views for site
    if args.type == 'site':
        return update_site(server, args, site_content_url)

    # enable/disable materialized views for workbook
    # works only when the site the workbooks belong to are enabled too
    elif args.type == 'workbook':
        return update_workbook(server, args, data_acceleration_config, site_content_url)

    # enable/disable materialized views for project by project path, for example: project1/project2
    elif args.type == 'project-path':
        return update_project_by_path(server, args, data_acceleration_config, site_content_url)
    else:
        print('Type unrecognized. Accepted : site|workbook|project-path')
        return False


def handle_schedule_command(server, args):
    if args.show_schedules is not None:
        return show_materialized_views_schedules(server, args)
    elif args.remove_from_schedule is not None:
        return remove_workbook_from_materialized_views(server, args)
    elif args.add_to_schedule is not None:
        return add_workbooks_to_schedule(server, args)
    elif args.create_schedule:
        return create_materialized_view_schedule(server, args)
    else:
        print('Schedule option unrecognized. Accepted schedule options: create|add|delete|show')
        return False


def find_workbook_path(args):
    if args is None:
        return None
    if args.workbook_path is not None:
        return args.workbook_path
    if args.add_to_schedule is not None and len(args.add_to_schedule) > 1:
        return args.add_to_schedule[1]
    if args.remove_from_schedule is not None and len(args.remove_from_schedule) > 1:
        return args.remove_from_schedule[1]
    if args.enable is not None and len(args.enable) > 0:
        return args.enable[0]
    if args.disable is not None and len(args.disable) > 0:
        return args.disable[0]
    if args.show_schedules is not None and len(args.show_schedules) == 1:
        return args.show_schedules[0]


def main():
    parser = argparse.ArgumentParser(description='Workbook Acceleration settings for sites/workbooks.')
    parser.add_argument('--server', '-s', required=False, help='Tableau server address')
    parser.add_argument('--username', '-u', required=False, help='username to sign into server')
    parser.add_argument('--password', '-p', required=False, help='password to sign into server')
    parser.add_argument('--ssl-cert-pem', '-ssl', required=False,
                        help='ssl certificate in Privacy Enhanced Mail (PEM) encoding')
    parser.add_argument('--status', '-st', required=False, action='store_const', const=True,
                        help='show Workbook Acceleration enabled sites/workbooks')
    parser.add_argument('--enable', '-en', required=False, nargs='*', metavar="WORKBOOK_PATH",
                        help='enable Workbook Acceleration')
    parser.add_argument('--disable', '-dis', required=False, nargs='*', metavar="WORKBOOK_PATH",
                        help='disable Workbook Acceleration')
    parser.add_argument('--site', '-si', required=False,
                        help='the server Default site will be use unless the site name is specified')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('--type', '-t', required=False, default='workbook',
                        choices=['site', 'workbook', 'project-path'],
                        help='type of content you want to update or see Workbook Acceleration settings on')
    parser.add_argument('--path-list', '-pl', required=False, help='path to a list of workbook paths')
    parser.add_argument('--workbook-path', '-wp', required=False, help='a workbook path (project/workbook)')
    parser.add_argument('--project-path', '-pp', required=False, help="path of the project")
    parser.add_argument('--logout', '-lo', required=False, help="logout the current active session",
                        action='store_const', const=True)
    parser.add_argument('--accelerate-now', '-an', required=False, action='store_true',
                        help='create Workbook Acceleration Views for workbooks immediately')
    parser.add_argument('--create-schedule', '-cs', required=False, metavar="SCHEDULE_NAME",
                        help='create Workbook Acceleration schedule')
    parser.add_argument('--show-schedules', '-ss', required=False, nargs='*', metavar="WORKBOOK_PATH",
                        help='show Workbook Acceleration schedules')
    parser.add_argument('--remove-from-schedule', '-rfs', required=False, nargs='*', metavar="SCHEDULE_NAME",
                        help='remove workbooks from an Workbook Acceleration schedule')
    parser.add_argument('--add-to-schedule', '-ats', required=False, nargs='*', metavar="SCHEDULE_NAME",
                        help='add workbooks to an Workbook Acceleration schedule')
    parser.add_argument('--hourly-interval', '-hi', choices=['0.25', '0.5', '1', '2', '4', '6', '8', '12'],
                        required=False, help='schedule interval in hours')
    parser.add_argument('--weekly-interval', '-wi',
                        metavar='WEEKDAY',
                        choices=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                        nargs="+", required=False,
                        help='Choices: Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday')
    parser.add_argument('--daily-interval', '-di', action='store_const', const=True,
                        required=False, help='daily schedule interval')
    parser.add_argument('--monthly-interval', '-mi',
                        required=False, help='monthly schedule interval')
    parser.add_argument('--start-hour', '-sh', required=False, help='start time hour: Default=0', type=int, default=0)
    parser.add_argument('--start-minute', '-sm', required=False,
                        choices=[0, 15, 30, 45], help='start time minute: Default=0', type=int, default=0)
    parser.add_argument('--end-hour', '-eh', required=False, help='end time hour: Default=0', type=int, default=0)
    parser.add_argument('--end-minute', '-em', required=False,
                        choices=[0, 15, 30, 45], help='end time minute: Default=0', type=int, default=0)

    args = parser.parse_args()

    if not assert_options_valid(args):
        parser.print_usage()
        return

    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # ignore warnings for missing ssl cert for https connections
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if args.logout is not None:
        sign_out()
        return

    server = get_authenticated_connection_to_server(args)

    if server is None:
        return

    # site content url is the TSC term for site id
    site = server.sites.get_by_id(server.site_id)
    site_content_url = site.content_url

    if args.show_schedules is not None or args.create_schedule is not None or \
            args.remove_from_schedule is not None or args.add_to_schedule is not None:
        if not handle_schedule_command(server, args):
            return

    elif args.enable is not None or args.disable is not None:
        if not handle_enable_disable_command(server, args, site_content_url):
            return

    # show enabled sites and workbooks
    if args.status:
        show_materialized_views_status(server, args, site_content_url)


def left_align_table(table):
    for field_name in table.field_names:
        table.align[field_name] = 'l'


def normalize_site_content_url(site_content_url):
    return "Default" if len(site_content_url) == 0 else site_content_url


def print_materialized_views_tasks(server, tasks, workbook_id_to_workbook=None):
    local_tz = tz.tzlocal()

    rows = list()

    project_id_to_project_path = None
    if workbook_id_to_workbook is None:
        project_id_to_project_path = get_project_id_to_project_path_map(server)
    workbook_id_with_tasks = set()
    for task in tasks:
        workbook_id_with_tasks.add(task.target.id)
        workbook = server.workbooks.get_by_id(task.target.id)
        if workbook is not None and \
                (workbook_id_to_workbook is None or workbook.id in workbook_id_to_workbook):
            if workbook_id_to_workbook is not None:
                workbook, path = workbook_id_to_workbook[workbook.id]
            elif project_id_to_project_path is not None:
                path = project_id_to_project_path[workbook.project_id]
            else:
                path = workbook.project_name
            rows.append(['{}/{}'.format(path, workbook.name),
                         task.schedule_item.name,
                         task.schedule_item.next_run_at.astimezone(local_tz)
                         if task.schedule_item.next_run_at is not None else None])

    workbook_id_without_tasks = set(workbook_id_to_workbook.keys()).difference(workbook_id_with_tasks) \
        if workbook_id_to_workbook is not None else set()

    workbooks_not_enabled = set()
    for workbook_id in workbook_id_without_tasks:
        workbook, path = workbook_id_to_workbook[workbook_id]
        if workbook.data_acceleration_config["acceleration_enabled"]:
            rows.append(['{}/{}'.format(path, workbook.name), '*', ''])
        else:
            workbooks_not_enabled.add(workbook.id)

    workbook_id_without_tasks = workbook_id_without_tasks.difference(workbooks_not_enabled)

    rows.sort(key=lambda x: x[0])
    unique_workbook_paths = set()
    for row_index in range(len(rows)):
        if rows[row_index][0] not in unique_workbook_paths:
            unique_workbook_paths.add(rows[row_index][0])
        else:
            rows[row_index][0] = ''

    columns = ['Project/Workbook', 'Schedule', 'Next Run At']
    header = "\nScheduled Tasks for Workbook Acceleration"
    print_table(rows, columns, header)
    if len(workbook_id_without_tasks) > 0:
        print("*The Workbook Acceleration views for these workbooks will be updated when they "
              "are published, or when their extract is refreshed.")


def get_workbooks_from_paths(server, args):
    all_projects = {project.id: project for project in TSC.Pager(server.projects)}
    workbook_id_to_workbook = dict()
    workbook_path_mapping = parse_workbook_path(args.path_list)
    for workbook_name, workbook_paths in workbook_path_mapping.items():
        req_option = TSC.RequestOptions()
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                         TSC.RequestOptions.Operator.Equals,
                                         workbook_name))
        workbooks = list(TSC.Pager(server.workbooks, req_option))
        all_paths = set(workbook_paths[:])
        for workbook in workbooks:
            path = find_project_path(all_projects[workbook.project_id], all_projects, "")
            if path in workbook_paths:
                all_paths.remove(path)
                workbook_id_to_workbook[workbook.id] = workbook, path

        for path in all_paths:
            print("Cannot find workbook path: {}, each line should only contain one workbook path"
                  .format(path + '/' + workbook_name))
    return workbook_id_to_workbook


def get_workbook_from_path(server, workbook_path):
    all_projects = {project.id: project for project in TSC.Pager(server.projects)}
    workbook_id_to_workbook = dict()
    workbook_path_list = workbook_path.rstrip().split('/')
    workbook_project = '/'.join(workbook_path_list[:-1])
    workbook_name = workbook_path_list[-1]

    req_option = TSC.RequestOptions()
    req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                     TSC.RequestOptions.Operator.Equals,
                                     workbook_name))
    workbooks = list(TSC.Pager(server.workbooks, req_option))
    for workbook in workbooks:
        path = find_project_path(all_projects[workbook.project_id], all_projects, "")
        if path == workbook_project:
            workbook_id_to_workbook[workbook.id] = workbook, workbook_project
            break

    if len(workbook_id_to_workbook) == 0:
        print("Unable to find {}".format(workbook_path))
    return workbook_id_to_workbook


def show_materialized_views_schedules(server, args=None, workbook_id_to_workbook=None):
    tasks = list(TSC.Pager(lambda options: server.tasks.get(task_type=TSC.TaskItem.Type.DataAcceleration)))
    if workbook_id_to_workbook is None and args is not None:
        workbook_path = find_workbook_path(args)
        if args.path_list is not None:
            workbook_id_to_workbook = get_workbooks_from_paths(server, args)
        elif workbook_path is not None:
            workbook_id_to_workbook = get_workbook_from_path(server, workbook_path)
    print_materialized_views_tasks(server, tasks, workbook_id_to_workbook)
    return True


def remove_materialized_views_tasks(server, tasks, workbook_id_to_workbook, schedule_name):
    if workbook_id_to_workbook is None or len(workbook_id_to_workbook) == 0:
        return False

    if tasks is None or len(tasks) == 0:
        print("Unable to find any MaterializeViews tasks")
        return False

    columns = ['Project/Workbook', 'Removed From Schedule']
    header = "Workbooks removed from schedule"
    rows = list()

    removed_workbook_ids = set()
    for task in tasks:
        if task.target.id in workbook_id_to_workbook and task.schedule_item.name == schedule_name:
            try:
                server.tasks.delete(task.id, task_type=TSC.TaskItem.Type.DataAcceleration)
                workbook, path = workbook_id_to_workbook[task.target.id]
                removed_workbook_ids.add(workbook.id)
                rows.append(['{}/{}'.format(path, workbook.name), task.schedule_item.name])
            except ServerResponseError as error:
                print("{}: {}".format(error.summary, error.detail))

    if len(rows) > 0:
        print_table(rows, columns, header)

    if len(rows) < len(workbook_id_to_workbook):
        no_removed_rows = list()
        for workbook, path in workbook_id_to_workbook.values():
            if workbook.id not in removed_workbook_ids:
                no_removed_rows.append(["{}/{}".format(path, workbook.name)])
        print_table(no_removed_rows, ["Project/Workbook"], "\nWorkbooks not on schedule \"{}\"".format(schedule_name))


def find_schedule_name(args):
    if args.create_schedule is not None:
        return args.create_schedule
    if args.add_to_schedule is not None:
        return args.add_to_schedule[0]
    if args.remove_from_schedule is not None:
        return args.remove_from_schedule[0]


def remove_workbook_from_materialized_views(server, args):
    workbook_path = find_workbook_path(args)
    schedule_name = find_schedule_name(args)

    schedule = find_schedule(server, schedule_name)
    if schedule is None:
        print("Unable to find the schedule {}".format(schedule_name))
        show_materialized_views_schedules(server, args)
        return False

    tasks = list(TSC.Pager(lambda options: server.tasks.get(task_type=TSC.TaskItem.Type.DataAcceleration)))
    workbook_id_to_workbook = None
    if workbook_path is not None:
        workbook_id_to_workbook = get_workbook_from_path(server, workbook_path)
    elif args.path_list is not None:
        workbook_id_to_workbook = get_workbooks_from_paths(server, args)
    remove_materialized_views_tasks(server, tasks, workbook_id_to_workbook, schedule_name)
    return True


def find_schedule(server, schedule_name):
    if schedule_name is None:
        return None

    schedules = list(TSC.Pager(server.schedules.get))
    for schedule in schedules:
        if schedule_name == schedule.name:
            return schedule
    return None


def confirm(message, options):
    """
    Ask user to enter Y or N (case-insensitive).
    :return: True if the answer is Y.
    :rtype: bool
    """
    answer = ""
    while answer not in options:
        answer = raw_input(message).lower()
    return answer


def add_to_materialized_views_schedule(server, tasks, schedule, workbook_id_to_workbook):
    if schedule is None or workbook_id_to_workbook is None:
        return

    workbook_id_to_schedules = dict()
    if tasks is not None:
        for task in tasks:
            if task.target.type != 'workbook':
                continue
            workbook_id_to_schedules.setdefault(task.target.id, set()).add(task.schedule_item.name)

    rows = list()
    warnings = set()
    for workbook, path in workbook_id_to_workbook.values():
        warnings_error_message = "Unable to add workbook \"{}/{}\" to schedule due to".format(
            path, workbook.name)

        try:
            server_response = server.schedules.add_to_schedule(schedule.id, workbook, task_type="dataAcceleration")

            # add_to_schedule returns a non-empty list when there was an error or warning coming from the server
            # when there was a warning, needs to check if the task was created
            if len(server_response) == 0 or server_response[0].task_created:
                workbook_id_to_schedules.setdefault(workbook.id, set()).add(schedule.name)
                rows.append(["{}/{}".format(path, workbook.name),
                             "\n".join(sorted(workbook_id_to_schedules[workbook.id]))])

            # Case 1: no warnings or error
            if len(server_response) == 0:
                continue

            if server_response[0].task_created:
                # Case 2: warnings exist, but the task was created
                warnings.update(server_response[0].warnings)
            elif server_response[0].warnings is not None:
                # Case 3: task was not created, warnings exists
                for warning in server_response[0].warnings:
                    warnings.add("{} {}".format(warnings_error_message, warning))
            elif server_response[0].error is not None:
                # Case 4: task was created, error occurred
                warnings.add("{} {}".format(warnings_error_message, server_response[0].error))
        except ServerResponseError as error:
            print("{} {}".format(warnings_error_message, error.detail))

    print_messages("Warning", sorted(warnings))
    header = "Workbooks added to schedule"
    columns = ['Project/Workbook', 'Schedules']
    print_table(rows, columns, header)


def is_workbook_enable(workbook):
    return workbook.data_acceleration_config["acceleration_enabled"]


def add_workbooks_to_schedule(server, args):
    schedule_name = find_schedule_name(args)

    schedule = find_schedule(server, schedule_name)
    if schedule is None:
        print('Unable to find the schedule "{}"'.format(schedule_name))
        return False

    if schedule.schedule_type != TSC.ScheduleItem.Type.DataAcceleration:
        print('Schedule {} is an existing schedule but is an Extract, Flow, or Subscription schedule. '
              'Use a Workbook Acceleration schedule.'.format(schedule_name))
        return False

    tasks = list(TSC.Pager(lambda options: server.tasks.get(task_type=TSC.TaskItem.Type.DataAcceleration)))

    workbook_path = find_workbook_path(args)
    workbook_id_to_workbook = None
    if workbook_path is not None:
        workbook_id_to_workbook = get_workbook_from_path(server, workbook_path)
    if args.path_list is not None:
        workbook_id_to_workbook = get_workbooks_from_paths(server, args)
    add_to_materialized_views_schedule(server, tasks, schedule, workbook_id_to_workbook)
    return True


def verify_time_arguments(args):
    def schedule_type_none(schedule_type):
        if schedule_type is not None:
            print('Please select one of the schedule types: hourly-interval, daily-interval, '
                  'weekly-interval, monthly-interval')
            return False
        else:
            return True

    # verify start_time
    if args.start_hour is None or not (0 <= args.start_hour <= 23):
        print("Please provide the schedule start hour between 0 and 23.")
        return False

    schedule_type_selected = None
    if args.daily_interval is not None:
        if args.end_hour is not None or args.end_minute is not None:
            print("--end-hour and --end-minutes will be ignored for --daily-interval")
        schedule_type_selected = "daily-interval"

    if args.weekly_interval is not None:
        if schedule_type_none(schedule_type_selected):
            schedule_type_selected = "weekly-interval"
        else:
            return False

    if args.monthly_interval is not None:
        if schedule_type_none(schedule_type_selected):
            if not (1 <= int(args.monthly_interval) <= 31):
                print('Please provide the day of month between 1 and 31')
                return False
            schedule_type_selected = "monthly-interval"
        else:
            return False

    if args.hourly_interval is not None:
        if schedule_type_none(schedule_type_selected):
            if args.end_hour is None or not (0 <= args.end_hour <= 23):
                print("Please provide the schedule end hour between 0 and 23")
                return False
            elif not (args.end_hour == 0 and args.end_minute == 0) and \
                    (args.end_hour < args.start_hour or
                     args.end_hour == args.start_hour
                     and args.end_minute < args.start_minute):
                print("Invalid start time {:02d}:{:02d} and end time {:02d}:{:02d}".format(
                    args.start_hour, args.start_minute, args.end_hour, args.end_minute
                ))
            else:
                schedule_type_selected = 'hourly-schedule'
        else:
            return False

    return schedule_type_selected is not None


def get_hour_interval(hour_interval):
    if hour_interval in ['0.25', '0.5']:
        return float(hour_interval)
    else:
        return int(hour_interval)


def create_hourly_schedule(server, args):
    hourly_interval = TSC.HourlyInterval(start_time=time(args.start_hour, args.start_minute),
                                         end_time=time(args.end_hour, args.end_minute),
                                         interval_value=get_hour_interval(args.hourly_interval))
    schedule_name = args.create_schedule

    hourly_schedule = TSC.ScheduleItem(schedule_name, 75, TSC.ScheduleItem.Type.DataAcceleration,
                                       TSC.ScheduleItem.ExecutionOrder.Parallel, hourly_interval)
    hourly_schedule = server.schedules.create(hourly_schedule)
    if hourly_schedule is not None:
        print("Hourly schedule \"{}\" created with an interval of {} hours.".format(
            schedule_name, args.hourly_interval))
        if hasattr(hourly_schedule, "warnings"):
            print_messages("Warning", hourly_schedule.warnings)
    else:
        print("Failed to create schedule {}".format(schedule_name))


def create_daily_schedule(server, args):
    daily_interval = TSC.DailyInterval(start_time=time(args.start_hour, args.start_minute))

    schedule_name = args.create_schedule

    daily_schedule = TSC.ScheduleItem(schedule_name, 75, TSC.ScheduleItem.Type.DataAcceleration,
                                      TSC.ScheduleItem.ExecutionOrder.Parallel, daily_interval)
    daily_schedule = server.schedules.create(daily_schedule)
    if daily_schedule is not None:
        print("Daily schedule \"{}\" created to run at {:02d}:{:02d}.".format(
            schedule_name, int(args.start_hour), int(args.start_minute)))
        if hasattr(daily_schedule, "warnings"):
            print_messages("Warning", daily_schedule.warnings)
    else:
        print("Failed to create schedule {}".format(schedule_name))


def create_weekly_schedule(server, args):
    weekly_interval = TSC.WeeklyInterval(time(args.start_hour, args.start_minute),
                                         *args.weekly_interval)

    schedule_name = args.create_schedule

    weekly_schedule = TSC.ScheduleItem(schedule_name, 75, TSC.ScheduleItem.Type.DataAcceleration,
                                       TSC.ScheduleItem.ExecutionOrder.Parallel, weekly_interval)
    weekly_schedule = server.schedules.create(weekly_schedule)
    if weekly_schedule is not None:
        print("Weekly schedule \"{}\" created to run on {} at  {:02d}:{:02d}.".format(
            schedule_name, args.weekly_interval, int(args.start_hour), int(args.start_minute)))
        if hasattr(weekly_schedule, "warnings"):
            print_messages("Warning", weekly_schedule.warnings)
    else:
        print("Failed to create schedule {}".format(schedule_name))


def create_monthly_schedule(server, args):
    monthly_interval = TSC.MonthlyInterval(start_time=time(args.start_hour, args.start_minute),
                                           interval_value=args.monthly_interval)

    schedule_name = args.create_schedule

    monthly_schedule = TSC.ScheduleItem(schedule_name, 75, TSC.ScheduleItem.Type.DataAcceleration,
                                        TSC.ScheduleItem.ExecutionOrder.Parallel, monthly_interval)
    monthly_schedule = server.schedules.create(monthly_schedule)
    if monthly_schedule is not None:
        print("Monthly schedule \"{}\" created to run on {}th at {:02d}:{:02d}.".format(
            schedule_name, args.monthly_interval, int(args.start_hour), int(args.start_minute)))
        if hasattr(monthly_schedule, "warnings"):
            print_messages("Warning", monthly_schedule.warnings)
    else:
        print("Failed to create schedule {}".format(schedule_name))


def print_messages(header, messages):
    output = ""
    if messages is not None and len(messages) > 0:
        starter = "* " if len(messages) > 1 else " "
        end = "\n" if len(messages) > 1 else ""
        if header is not None and len(header) > 0:
            output = header + (":\n" if len(messages) > 1 else ":")
        for message in messages:
            output = output + starter + message + end
    print(output)


def create_materialized_view_schedule(server, args):
    # verifies start and end times
    if not verify_time_arguments(args):
        return False

    try:
        if args.hourly_interval is not None:
            create_hourly_schedule(server, args)
        elif args.daily_interval is not None:
            create_daily_schedule(server, args)
        elif args.weekly_interval is not None:
            create_weekly_schedule(server, args)
        else:
            create_monthly_schedule(server, args)
    except ServerResponseError as error:
        print("{}: {}".format(error.summary, error.detail))
        return False

    return True


def find_project_path(project, all_projects, path):
    # project stores the id of it's parent
    # this method is to run recursively to find the path from root project to given project
    path = project.name if len(path) == 0 else project.name + '/' + path

    if project.parent_id is None:
        return path
    else:
        return find_project_path(all_projects[project.parent_id], all_projects, path)


def get_project_id_to_project_path_map(server, projects=None):
    # most likely user won't have too many projects so we store them in a dict to search
    all_projects = {project.id: project for project in TSC.Pager(server.projects)}

    if projects is None:
        projects = all_projects.values()

    result = dict()
    for project in projects:
        result[project.id] = find_project_path(project, all_projects, "")
    return result


def get_project_path_to_project_map(server, projects):
    # most likely user won't have too many projects so we store them in a dict to search
    all_projects = {project.id: project for project in TSC.Pager(server.projects)}

    result = dict()
    for project in projects:
        result[find_project_path(project, all_projects, "")] = project
    return result


def print_paths(paths):
    for path in paths.keys():
        print(path)


def init_table(header):
    table = PrettyTable()
    table.field_names = header
    left_align_table(table)
    return table


def get_and_print_acceleration_enabled_sites(server):
    enabled_sites = set()
    # For server admin, this will prints all the materialized views enabled sites
    # For other users, this only prints the status of the site they belong to
    # only server admins can get all the sites in the server
    # other users can only get the site they are in
    for site in TSC.Pager(server.sites):
        if site.data_acceleration_mode != "disable":
            enabled_sites.add(site)

    return enabled_sites


def print_acceleration_enabled_workbooks(server, site):
    # Individual workbooks can be enabled only when the sites they belong to are enabled too
    workbooks = list()
    project_id_to_project_path = dict()
    project_id_to_project_path.update(get_project_id_to_project_path_map(server))
    workbooks.extend(list(TSC.Pager(server.workbooks)))

    rows = list()
    enabled_workbooks = list()
    for workbook in workbooks:
        if workbook.data_acceleration_config['acceleration_enabled']:
            project_path = project_id_to_project_path[workbook.project_id]
            enabled_workbooks.append((workbook, project_path))
            rows.append([
                normalize_site_content_url(site), '{}/{}'.format(project_path, workbook.name)])

    header = "\nWorkbook Acceleration is enabled for the following workbooks"
    columns = ["Site", "Project/Workbook"]
    print_table(rows, columns, header)

    return enabled_workbooks


def show_materialized_views_status(server, args, site_content_url):
    enabled_workbooks = print_acceleration_enabled_workbooks(server, site_content_url)

    workbook_id_to_workbook = dict()
    for workbook, path in enabled_workbooks:
        workbook_id_to_workbook[workbook.id] = workbook, path
    show_materialized_views_schedules(server, args, workbook_id_to_workbook)


def update_project_by_path(server, args, data_acceleration_config, site_content_url):
    if args.project_path is None:
        print("Use --project_path <project path> to specify the path of the project")
        return False
    project_name = args.project_path.split('/')[-1]

    if not assert_site_enabled_for_materialized_views(server, site_content_url):
        return False
    projects = [project for project in TSC.Pager(server.projects) if project.name == project_name]
    if not assert_project_valid(args.project_path, projects):
        return False

    possible_paths = get_project_path_to_project_map(server, projects)
    update_project(possible_paths[args.project_path], server, data_acceleration_config)
    return True


def update_project(project, server, data_acceleration_config):
    all_projects = list(TSC.Pager(server.projects))
    project_ids = find_project_ids_to_update(all_projects, project)
    for workbook in TSC.Pager(server.workbooks):
        if workbook.project_id in project_ids:
            workbook.data_acceleration_config = data_acceleration_config
            update_workbook_internal(server, workbook)

    print("Updated Workbook Acceleration settings for project: {}".format(project.name))
    print('\n')


def find_project_ids_to_update(all_projects, project):
    projects_to_update = []
    find_projects_to_update(project, all_projects, projects_to_update)
    return set([project_to_update.id for project_to_update in projects_to_update])


def parse_workbook_path(file_path):
    # parse the list of project path of workbooks
    workbook_paths = sanitize_workbook_list(file_path, "path")

    workbook_path_mapping = defaultdict(list)
    for workbook_path in workbook_paths:
        workbook_project = workbook_path.rstrip().split('/')
        workbook_path_mapping[workbook_project[-1]].append('/'.join(workbook_project[:-1]))
    return workbook_path_mapping


def update_workbook_internal(server, workbook):
    # without removing the workbook name, the rest api server code will
    # think the user would change the name of the workbook
    try:
        workbook_name = workbook.name
        workbook.name = None
        server.workbooks.update(workbook)
    finally:
        workbook.name = workbook_name


def update_workbook_by_path(workbook_path, server, data_acceleration_config, workbook_id_to_schedules):
    workbook_id_to_workbook = get_workbook_from_path(server, workbook_path)
    rows = list()
    for workbook, path in workbook_id_to_workbook.values():
        try:
            workbook.data_acceleration_config = data_acceleration_config

            if confirm_workbook_update(workbook, path, workbook_id_to_schedules, data_acceleration_config, None) \
                    in [UserResponse.YES, UserResponse.YES_FOR_ALL]:
                update_workbook_internal(server, workbook)
                rows.append(["{}/{}".format(path, workbook.name)])
        except ServerResponseError as error:
            print("Unable to {} {}/{}. {}".format(
                "enable" if data_acceleration_config["acceleration_enabled"] else "disable",
                path, workbook.name, error.detail
            ))
            return False
    enabled_or_disabled = data_acceleration_config["acceleration_enabled"]
    print_table(rows, ["Project/Workbook"], "Workbooks {}".format(
        "Enabled" if enabled_or_disabled else "Disabled"))


def get_all_materialized_views_tasks(server):
    tasks = list(TSC.Pager(lambda options: server.tasks.get(task_type=TSC.TaskItem.Type.DataAcceleration)))
    workbook_id_to_schedules = dict()
    for task in tasks:
        if task.target.id not in workbook_id_to_schedules:
            workbook_id_to_schedules[task.target.id] = list()
        workbook_id_to_schedules[task.target.id].append(task.schedule_item.name)
    return workbook_id_to_schedules


def update_workbook(server, args, data_acceleration_config, site_content_url):
    workbook_path = find_workbook_path(args)
    if args.path_list is None and workbook_path is None:
        print("Use '--path-list <filename>' or --workbook-path <workbook-path> "
              "to specify the path of workbooks")
        print('\n')
        return False

    if not assert_site_enabled_for_materialized_views(server, site_content_url):
        return False

    workbook_id_to_schedules = None
    if not data_acceleration_config["acceleration_enabled"]:
        workbook_id_to_schedules = get_all_materialized_views_tasks(server)

    if args.path_list is not None:
        workbook_path_mapping = parse_workbook_path(args.path_list)
        all_projects = {project.id: project for project in TSC.Pager(server.projects)}
        update_workbooks_by_paths(all_projects, data_acceleration_config,
                                  server, workbook_path_mapping, workbook_id_to_schedules)
    elif workbook_path is not None:
        update_workbook_by_path(workbook_path, server, data_acceleration_config, workbook_id_to_schedules)

    return True


def print_table(rows, columns, header):
    if rows is None or len(rows) == 0:
        print("{}: None".format(header))
    else:
        table = init_table(columns)
        for row in rows:
            if not isinstance(row, list):
                row = [row]
            table.add_row(row)
        print(header)
        print(table)


def confirm_workbook_update(workbook, path, workbook_id_to_schedules,
                            data_acceleration_config, previous_confirmation):
    if previous_confirmation in [UserResponse.YES_FOR_ALL, UserResponse.NO_FOR_ALL]:
        return previous_confirmation

    if data_acceleration_config["acceleration_enabled"]:
        return UserResponse.YES_FOR_ALL

    if workbook.id not in workbook_id_to_schedules:
        return UserResponse.YES

    return confirm("{}/{} is on schedules {}. Disabling it will "
                   "remove it from the schedules. Would you confirm? \n"
                   "Press Y for yes, N for No, A for yes_for_all, Q for no_for_all: ".
                   format(path, workbook.name, workbook_id_to_schedules[workbook.id]),
                   [UserResponse.YES, UserResponse.NO, UserResponse.YES_FOR_ALL, UserResponse.NO_FOR_ALL])


def update_workbooks_by_paths(all_projects, data_acceleration_config, server,
                              workbook_path_mapping, workbook_id_to_schedules):
    rows = list()
    update_confirmation = None
    for workbook_name, workbook_paths in workbook_path_mapping.items():
        req_option = TSC.RequestOptions()
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                         TSC.RequestOptions.Operator.Equals,
                                         workbook_name))
        workbooks = list(TSC.Pager(server.workbooks, req_option))
        all_paths = set(workbook_paths[:])

        for workbook in workbooks:
            path = find_project_path(all_projects[workbook.project_id], all_projects, "")
            if path in workbook_paths:
                all_paths.remove(path)
                workbook.data_acceleration_config = data_acceleration_config

                update_confirmation = confirm_workbook_update(workbook, path, workbook_id_to_schedules,
                                                              data_acceleration_config, update_confirmation)

                if update_confirmation in [UserResponse.YES_FOR_ALL, UserResponse.YES]:
                    try:
                        update_workbook_internal(server, workbook)
                        rows.append(["{}/{}".format(path, workbook.name)])
                    except ServerResponseError as error:
                        print("Unable to {} {}/{} due to {}".format(
                            "enable" if data_acceleration_config["acceleration_enabled"] else "disable",
                            path, workbook.name, error.detail
                        ))
        for path in all_paths:
            print("Cannot find workbook path: {}, each line should only contain one workbook path"
                  .format(path + '/' + workbook_name))

    enabled_or_disabled = "Enabled" if data_acceleration_config["acceleration_enabled"] else "Disabled"
    print_table(rows, ["Project/Workbook"], "Workbooks {}".format(enabled_or_disabled))


def update_site(server, args, site_content_url):
    if not assert_site_options_valid(args):
        return False

    site_to_update = server.sites.get_by_content_url(site_content_url)
    site_to_update.data_acceleration_mode = "enable_selective" if args.enable is not None else "disable"
    server.sites.update(site_to_update)
    print("Updated Workbook Acceleration settings for site: {}\n".format(site_to_update.name))
    return True


def create_data_acceleration_config(args):
    data_acceleration_config = dict()
    data_acceleration_config['acceleration_enabled'] = args.disable is None and args.enable is not None
    data_acceleration_config['accelerate_now'] = True if args.accelerate_now else False
    return data_acceleration_config


def assert_site_options_valid(args):
    if args.accelerate_now:
        print('"--accelerate-now" only applies to workbook/project type')
        return False
    return True


def assert_site_enabled_for_materialized_views(server, site_content_url):
    parent_site = server.sites.get_by_content_url(site_content_url)
    if parent_site.data_acceleration_mode == "disable":
        print('Cannot update workbook/project because site is disabled for Workbook Acceleration')
        return False
    return True


def assert_project_valid(project_name, projects):
    if len(projects) == 0:
        print("Cannot find project: {}".format(project_name))
        return False
    return True


def find_projects_to_update(project, all_projects, projects_to_update):
    # Use recursion to find all the sub-projects and enable/disable the workbooks in them
    projects_to_update.append(project)
    children_projects = [child for child in all_projects if child.parent_id == project.id]
    if len(children_projects) == 0:
        return

    for child in children_projects:
        find_projects_to_update(child, all_projects, projects_to_update)


def sanitize_workbook_list(file_name, file_type):
    if not os.path.isfile(file_name):
        print("Invalid file name '{}'".format(file_name))
        return []
    file_list = open(file_name, "r")

    if file_type == "name":
        return [workbook.rstrip() for workbook in file_list if not workbook.isspace()]
    if file_type == "path":
        return [workbook.rstrip() for workbook in file_list if not workbook.isspace()]


if __name__ == "__main__":
    main()

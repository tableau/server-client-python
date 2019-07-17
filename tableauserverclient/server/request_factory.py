from ..datetime_helpers import format_datetime
import xml.etree.ElementTree as ET
from functools import wraps

from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata


def _add_multipart(parts):
    mime_multipart_parts = list()
    for name, (filename, data, content_type) in parts.items():
        multipart_part = RequestField(name=name, data=data, filename=filename)
        multipart_part.make_multipart(content_type=content_type)
        mime_multipart_parts.append(multipart_part)
    xml_request, content_type = encode_multipart_formdata(mime_multipart_parts)
    content_type = ''.join(('multipart/mixed',) + content_type.partition(';')[1:])
    return xml_request, content_type


def _tsrequest_wrapped(func):
    def wrapper(self, *args, **kwargs):
        xml_request = ET.Element('tsRequest')
        func(self, xml_request, *args, **kwargs)
        return ET.tostring(xml_request)
    return wrapper


def _add_connections_element(connections_element, connection):
    connection_element = ET.SubElement(connections_element, 'connection')
    connection_element.attrib['serverAddress'] = connection.server_address
    if connection.server_port:
        connection_element.attrib['serverPort'] = connection.server_port
    if connection.connection_credentials:
        connection_credentials = connection.connection_credentials
        _add_credentials_element(connection_element, connection_credentials)


def _add_credentials_element(parent_element, connection_credentials):
    credentials_element = ET.SubElement(parent_element, 'connectionCredentials')
    credentials_element.attrib['name'] = connection_credentials.name
    credentials_element.attrib['password'] = connection_credentials.password
    credentials_element.attrib['embed'] = 'true' if connection_credentials.embed else 'false'
    if connection_credentials.oauth:
        credentials_element.attrib['oAuth'] = 'true'


class AuthRequest(object):
    def signin_req(self, auth_item):
        xml_request = ET.Element('tsRequest')
        credentials_element = ET.SubElement(xml_request, 'credentials')
        credentials_element.attrib['name'] = auth_item.username
        credentials_element.attrib['password'] = auth_item.password
        site_element = ET.SubElement(credentials_element, 'site')
        site_element.attrib['contentUrl'] = auth_item.site_id
        if auth_item.user_id_to_impersonate:
            user_element = ET.SubElement(credentials_element, 'user')
            user_element.attrib['id'] = auth_item.user_id_to_impersonate
        return ET.tostring(xml_request)


class DatasourceRequest(object):
    def _generate_xml(self, datasource_item, connection_credentials=None, connections=None):
        xml_request = ET.Element('tsRequest')
        datasource_element = ET.SubElement(xml_request, 'datasource')
        datasource_element.attrib['name'] = datasource_item.name
        project_element = ET.SubElement(datasource_element, 'project')
        project_element.attrib['id'] = datasource_item.project_id

        if connection_credentials is not None and connections is not None:
            raise RuntimeError('You cannot set both `connections` and `connection_credentials`')

        if connection_credentials is not None:
            _add_credentials_element(datasource_element, connection_credentials)

        if connections is not None:
            connections_element = ET.SubElement(datasource_element, 'connections')
            for connection in connections:
                _add_connections_element(connections_element, connection)
        return ET.tostring(xml_request)

    def update_req(self, datasource_item):
        xml_request = ET.Element('tsRequest')
        datasource_element = ET.SubElement(xml_request, 'datasource')
        if datasource_item.project_id:
            project_element = ET.SubElement(datasource_element, 'project')
            project_element.attrib['id'] = datasource_item.project_id
        if datasource_item.owner_id:
            owner_element = ET.SubElement(datasource_element, 'owner')
            owner_element.attrib['id'] = datasource_item.owner_id

        datasource_element.attrib['isCertified'] = str(datasource_item.certified).lower()

        if datasource_item.certification_note:
            datasource_element.attrib['certificationNote'] = str(datasource_item.certification_note)

        return ET.tostring(xml_request)

    def publish_req(self, datasource_item, filename, file_contents, connection_credentials=None, connections=None):
        xml_request = self._generate_xml(datasource_item, connection_credentials, connections)

        parts = {'request_payload': ('', xml_request, 'text/xml'),
                 'tableau_datasource': (filename, file_contents, 'application/octet-stream')}
        return _add_multipart(parts)

    def publish_req_chunked(self, datasource_item, connection_credentials=None, connections=None):
        xml_request = self._generate_xml(datasource_item, connection_credentials, connections)

        parts = {'request_payload': ('', xml_request, 'text/xml')}
        return _add_multipart(parts)


class FileuploadRequest(object):
    def chunk_req(self, chunk):
        parts = {'request_payload': ('', '', 'text/xml'),
                 'tableau_file': ('file', chunk, 'application/octet-stream')}
        return _add_multipart(parts)


class GroupRequest(object):
    def add_user_req(self, user_id):
        xml_request = ET.Element('tsRequest')
        user_element = ET.SubElement(xml_request, 'user')
        user_element.attrib['id'] = user_id
        return ET.tostring(xml_request)

    def create_req(self, group_item):
        xml_request = ET.Element('tsRequest')
        group_element = ET.SubElement(xml_request, 'group')
        group_element.attrib['name'] = group_item.name
        return ET.tostring(xml_request)

    def update_req(self, group_item, default_site_role):
        xml_request = ET.Element('tsRequest')
        group_element = ET.SubElement(xml_request, 'group')
        group_element.attrib['name'] = group_item.name
        if group_item.domain_name != 'local':
            project_element = ET.SubElement(group_element, 'import')
            project_element.attrib['source'] = "ActiveDirectory"
            project_element.attrib['domainName'] = group_item.domain_name
            project_element.attrib['siteRole'] = default_site_role
        return ET.tostring(xml_request)


class PermissionRequest(object):
    def _add_capability(self, parent_element, capability_set, mode):
        for capability_item in capability_set:
            capability_element = ET.SubElement(parent_element, 'capability')
            capability_element.attrib['name'] = capability_item
            capability_element.attrib['mode'] = mode

    def add_req(self, permission_item):
        xml_request = ET.Element('tsRequest')
        permissions_element = ET.SubElement(xml_request, 'permissions')

        for user_capability in permission_item.user_capabilities:
            grantee_element = ET.SubElement(permissions_element, 'granteeCapabilities')
            grantee_capabilities_element = ET.SubElement(grantee_element, user_capability.User)
            grantee_capabilities_element.attrib['id'] = user_capability.grantee_id
            capabilities_element = ET.SubElement(grantee_element, 'capabilities')
            self._add_capability(capabilities_element, user_capability.allowed, user_capability.Allow)
            self._add_capability(capabilities_element, user_capability.denied, user_capability.Deny)

        for group_capability in permission_item.group_capabilities:
            grantee_element = ET.SubElement(permissions_element, 'granteeCapabilities')
            ET.SubElement(grantee_element, group_capability, id=group_capability.grantee_id)
            capabilities_element = ET.SubElement(grantee_element, 'capabilities')
            self._add_capability(capabilities_element, group_capability.allowed, group_capability.Allow)
            self._add_capability(capabilities_element, group_capability.denied, group_capability.Deny)
        return ET.tostring(xml_request)


class ProjectRequest(object):
    def update_req(self, project_item):
        xml_request = ET.Element('tsRequest')
        project_element = ET.SubElement(xml_request, 'project')
        if project_item.name:
            project_element.attrib['name'] = project_item.name
        if project_item.description:
            project_element.attrib['description'] = project_item.description
        if project_item.content_permissions:
            project_element.attrib['contentPermissions'] = project_item.content_permissions
        return ET.tostring(xml_request)

    def create_req(self, project_item):
        xml_request = ET.Element('tsRequest')
        project_element = ET.SubElement(xml_request, 'project')
        project_element.attrib['name'] = project_item.name
        if project_item.description:
            project_element.attrib['description'] = project_item.description
        if project_item.content_permissions:
            project_element.attrib['contentPermissions'] = project_item.content_permissions
        if project_item.parent_id:
            project_element.attrib['parentProjectId'] = project_item.parent_id
        return ET.tostring(xml_request)


class ScheduleRequest(object):
    def create_req(self, schedule_item):
        xml_request = ET.Element('tsRequest')
        schedule_element = ET.SubElement(xml_request, 'schedule')
        schedule_element.attrib['name'] = schedule_item.name
        schedule_element.attrib['priority'] = str(schedule_item.priority)
        schedule_element.attrib['type'] = schedule_item.schedule_type
        schedule_element.attrib['executionOrder'] = schedule_item.execution_order
        interval_item = schedule_item.interval_item
        schedule_element.attrib['frequency'] = interval_item._frequency
        frequency_element = ET.SubElement(schedule_element, 'frequencyDetails')
        frequency_element.attrib['start'] = str(interval_item.start_time)
        if hasattr(interval_item, 'end_time') and interval_item.end_time:
            frequency_element.attrib['end'] = str(interval_item.end_time)
        if hasattr(interval_item, 'interval') and interval_item.interval:
            intervals_element = ET.SubElement(frequency_element, 'intervals')
            for interval in interval_item._interval_type_pairs():
                expression, value = interval
                single_interval_element = ET.SubElement(intervals_element, 'interval')
                single_interval_element.attrib[expression] = value
        return ET.tostring(xml_request)

    def update_req(self, schedule_item):
        xml_request = ET.Element('tsRequest')
        schedule_element = ET.SubElement(xml_request, 'schedule')
        if schedule_item.name:
            schedule_element.attrib['name'] = schedule_item.name
        if schedule_item.priority:
            schedule_element.attrib['priority'] = str(schedule_item.priority)
        if schedule_item.execution_order:
            schedule_element.attrib['executionOrder'] = schedule_item.execution_order
        if schedule_item.state:
            schedule_element.attrib['state'] = schedule_item.state
        interval_item = schedule_item.interval_item
        if interval_item._frequency:
            schedule_element.attrib['frequency'] = interval_item._frequency
        frequency_element = ET.SubElement(schedule_element, 'frequencyDetails')
        frequency_element.attrib['start'] = str(interval_item.start_time)
        if hasattr(interval_item, 'end_time') and interval_item.end_time:
            frequency_element.attrib['end'] = str(interval_item.end_time)
        intervals_element = ET.SubElement(frequency_element, 'intervals')
        if hasattr(interval_item, 'interval'):
            for interval in interval_item._interval_type_pairs():
                (expression, value) = interval
                single_interval_element = ET.SubElement(intervals_element, 'interval')
                single_interval_element.attrib[expression] = value
        return ET.tostring(xml_request)

    def _add_to_req(self, id_, type_):
        """
        <task>
          <extractRefresh>
            <workbook/datasource id="..."/>
          </extractRefresh>
        </task>

        """
        xml_request = ET.Element('tsRequest')
        task_element = ET.SubElement(xml_request, 'task')
        refresh = ET.SubElement(task_element, 'extractRefresh')
        workbook = ET.SubElement(refresh, type_)
        workbook.attrib['id'] = id_

        return ET.tostring(xml_request)

    def add_workbook_req(self, id_):
        return self._add_to_req(id_, "workbook")

    def add_datasource_req(self, id_):
        return self._add_to_req(id_, "datasource")


class SiteRequest(object):
    def update_req(self, site_item):
        xml_request = ET.Element('tsRequest')
        site_element = ET.SubElement(xml_request, 'site')
        if site_item.name:
            site_element.attrib['name'] = site_item.name
        if site_item.content_url:
            site_element.attrib['contentUrl'] = site_item.content_url
        if site_item.admin_mode:
            site_element.attrib['adminMode'] = site_item.admin_mode
        if site_item.user_quota:
            site_element.attrib['userQuota'] = str(site_item.user_quota)
        if site_item.state:
            site_element.attrib['state'] = site_item.state
        if site_item.storage_quota:
            site_element.attrib['storageQuota'] = str(site_item.storage_quota)
        if site_item.disable_subscriptions:
            site_element.attrib['disableSubscriptions'] = str(site_item.disable_subscriptions).lower()
        if site_item.subscribe_others_enabled:
            site_element.attrib['subscribeOthersEnabled'] = str(site_item.subscribe_others_enabled).lower()
        if site_item.revision_limit:
            site_element.attrib['revisionLimit'] = str(site_item.revision_limit)
        if site_item.subscribe_others_enabled:
            site_element.attrib['revisionHistoryEnabled'] = str(site_item.revision_history_enabled).lower()
        if site_item.materialized_views_mode is not None:
            site_element.attrib['materializedViewsMode'] = str(site_item.materialized_views_mode).lower()
        return ET.tostring(xml_request)

    def create_req(self, site_item):
        xml_request = ET.Element('tsRequest')
        site_element = ET.SubElement(xml_request, 'site')
        site_element.attrib['name'] = site_item.name
        site_element.attrib['contentUrl'] = site_item.content_url
        if site_item.admin_mode:
            site_element.attrib['adminMode'] = site_item.admin_mode
        if site_item.user_quota:
            site_element.attrib['userQuota'] = str(site_item.user_quota)
        if site_item.storage_quota:
            site_element.attrib['storageQuota'] = str(site_item.storage_quota)
        if site_item.disable_subscriptions:
            site_element.attrib['disableSubscriptions'] = str(site_item.disable_subscriptions).lower()
        return ET.tostring(xml_request)


class TagRequest(object):
    def add_req(self, tag_set):
        xml_request = ET.Element('tsRequest')
        tags_element = ET.SubElement(xml_request, 'tags')
        for tag in tag_set:
            tag_element = ET.SubElement(tags_element, 'tag')
            tag_element.attrib['label'] = tag
        return ET.tostring(xml_request)


class UserRequest(object):
    def update_req(self, user_item, password):
        xml_request = ET.Element('tsRequest')
        user_element = ET.SubElement(xml_request, 'user')
        if user_item.fullname:
            user_element.attrib['fullName'] = user_item.fullname
        if user_item.email:
            user_element.attrib['email'] = user_item.email
        if user_item.site_role:
            if user_item.site_role != 'ServerAdministrator':
                user_element.attrib['siteRole'] = user_item.site_role
        if user_item.auth_setting:
            user_element.attrib['authSetting'] = user_item.auth_setting
        if password:
            user_element.attrib['password'] = password
        return ET.tostring(xml_request)

    def add_req(self, user_item):
        xml_request = ET.Element('tsRequest')
        user_element = ET.SubElement(xml_request, 'user')
        user_element.attrib['name'] = user_item.name
        user_element.attrib['siteRole'] = user_item.site_role
        if user_item.auth_setting:
            user_element.attrib['authSetting'] = user_item.auth_setting
        return ET.tostring(xml_request)


class WorkbookRequest(object):
    def _generate_xml(self, workbook_item, connection_credentials=None, connections=None):
        xml_request = ET.Element('tsRequest')
        workbook_element = ET.SubElement(xml_request, 'workbook')
        workbook_element.attrib['name'] = workbook_item.name
        if workbook_item.show_tabs:
            workbook_element.attrib['showTabs'] = str(workbook_item.show_tabs).lower()
        project_element = ET.SubElement(workbook_element, 'project')
        project_element.attrib['id'] = workbook_item.project_id

        if connection_credentials is not None and connections is not None:
            raise RuntimeError('You cannot set both `connections` and `connection_credentials`')

        if connection_credentials is not None:
            _add_credentials_element(workbook_element, connection_credentials)

        if connections is not None:
            connections_element = ET.SubElement(workbook_element, 'connections')
            for connection in connections:
                _add_connections_element(connections_element, connection)
        return ET.tostring(xml_request)

    def update_req(self, workbook_item):
        xml_request = ET.Element('tsRequest')
        workbook_element = ET.SubElement(xml_request, 'workbook')
        if workbook_item.name:
            workbook_element.attrib['name'] = workbook_item.name
        if workbook_item.show_tabs is not None:
            workbook_element.attrib['showTabs'] = str(workbook_item.show_tabs).lower()
        if workbook_item.project_id:
            project_element = ET.SubElement(workbook_element, 'project')
            project_element.attrib['id'] = workbook_item.project_id
        if workbook_item.owner_id:
            owner_element = ET.SubElement(workbook_element, 'owner')
            owner_element.attrib['id'] = workbook_item.owner_id
        if workbook_item.materialized_views_config['materialized_views_enabled']\
                and workbook_item.materialized_views_config['run_materialization_now']:
            materialized_views_config = workbook_item.materialized_views_config
            materialized_views_element = ET.SubElement(workbook_element, 'materializedViewsEnablementConfig')
            materialized_views_element.attrib['materializedViewsEnabled'] = str(materialized_views_config
                                                                                ["materialized_views_enabled"]).lower()
            materialized_views_element.attrib['materializeNow'] = str(materialized_views_config
                                                                      ["run_materialization_now"]).lower()

        return ET.tostring(xml_request)

    def publish_req(self, workbook_item, filename, file_contents, connection_credentials=None, connections=None):
        xml_request = self._generate_xml(workbook_item,
                                         connection_credentials=connection_credentials,
                                         connections=connections)

        parts = {'request_payload': ('', xml_request, 'text/xml'),
                 'tableau_workbook': (filename, file_contents, 'application/octet-stream')}
        return _add_multipart(parts)

    def publish_req_chunked(self, workbook_item, connection_credentials=None, connections=None):
        xml_request = self._generate_xml(workbook_item,
                                         connection_credentials=connection_credentials,
                                         connections=connections)

        parts = {'request_payload': ('', xml_request, 'text/xml')}
        return _add_multipart(parts)


class Connection(object):
    @_tsrequest_wrapped
    def update_req(self, xml_request, connection_item):
        connection_element = ET.SubElement(xml_request, 'connection')
        if connection_item.server_address:
            connection_element.attrib['serverAddress'] = connection_item.server_address.lower()
        if connection_item.server_port:
            connection_element.attrib['serverPort'] = str(connection_item.server_port)
        if connection_item.username:
            connection_element.attrib['userName'] = connection_item.username
        if connection_item.password:
            connection_element.attrib['password'] = connection_item.password
        if connection_item.embed_password is not None:
            connection_element.attrib['embedPassword'] = str(connection_item.embed_password).lower()


class TaskRequest(object):
    @_tsrequest_wrapped
    def run_req(self, xml_request, task_item):
        # Send an empty tsRequest
        pass


class SubscriptionRequest(object):
    def create_req(self, subscription_item):
        xml_request = ET.Element('tsRequest')
        subscription_element = ET.SubElement(xml_request, 'subscription')
        subscription_element.attrib['subject'] = subscription_item.subject

        content_element = ET.SubElement(subscription_element, 'content')
        content_element.attrib['id'] = subscription_item.target.id
        content_element.attrib['type'] = subscription_item.target.type

        schedule_element = ET.SubElement(subscription_element, 'schedule')
        schedule_element.attrib['id'] = subscription_item.schedule_id

        user_element = ET.SubElement(subscription_element, 'user')
        user_element.attrib['id'] = subscription_item.user_id
        return ET.tostring(xml_request)


class EmptyRequest(object):
    @_tsrequest_wrapped
    def empty_req(self, xml_request):
        pass


class RequestFactory(object):
    Auth = AuthRequest()
    Connection = Connection()
    Datasource = DatasourceRequest()
    Empty = EmptyRequest()
    Fileupload = FileuploadRequest()
    Group = GroupRequest()
    Permission = PermissionRequest()
    Project = ProjectRequest()
    Schedule = ScheduleRequest()
    Site = SiteRequest()
    Tag = TagRequest()
    Task = TaskRequest()
    User = UserRequest()
    Workbook = WorkbookRequest()
    Subscription = SubscriptionRequest()

import requests
import lxml.objectify as O
import lxml.etree as ET
import re

from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata


# TODO
# Add all calls
# Fix routing to be more scalable
# Refactor making the requests and remove duplicated logic
# Add error handling
# Pagination to all calls?

Routes = {
    'SIGN_IN': "/api/2.0/auth/signin",
    'SIGN_OUT': "/api/2.0/auth/signout",
    'CREATE_SITE': "/api/2.0/sites",
    'UPDATE_SITE': "/api/2.0/sites/{site_id}",
    'QUERY_SITE': "/api/2.0/sites/{site_id}",
    'DELETE_SITE': "/api/2.0/sites/{site_id}",
    'ADD_USER_TO_SITE': "/api/2.0/sites/{site_id}/users",
    'GET_USERS_ON_SITE': "/api/2.0/sites/{site_id}/users",
    'REMOVE_USER_FROM_SITE': "/api/2.0/sites/{site_id}/users/{user_id}",
    'UPDATE_USER': "/api/2.0/sites/{site_id}/users/{user_id}",
    'QUERY_GROUPS': "/api/2.0/sites/{site_id}/groups",
    'CREATE_GROUP': "/api/2.0/sites/{site_id}/groups",
    'QUERY_PROJECTS': "/api/2.0/sites/{site_id}/projects",
    'PUBLISH_DATASOURCE': "/api/2.0/sites/{site_id}/datasources",
    'PUBLISH_WORKBOOK': "/api/2.0/sites/{site_id}/workbooks",
    'ADD_USER_TO_GROUP': "/api/2.0/sites/{site_id}/groups/{group_id}/users/",
    'QUERY_WORKBOOKS_FOR_USER': "/api/2.0/sites/{site_id}/users/{user_id}/workbooks",
    'REMOVE_USER_FROM_GROUP': "/api/2.0/sites/{site_id}/groups/{group_id}/users/{user_id}",
    'DOWNLOAD_WORKBOOK': "/api/2.0/sites/{site_id}/workbooks/{workbook_id}/content",
    'CREATE_PROJECT': "/api/2.0/sites/{site_id}/projects"
}


class TableauREST:

    def __init__(self, server, username, password, site=""):
        self.server = server
        self.user = username
        self.pw = password
        self.site_url = site
        self.token = None
        self.site_id = None
        self.verbose = False  # Add in verbosity someday

    def _make_signin_payload(self, imp_user=None):
        root = O.Element('tsRequest')
        root.credentials = O.Element(
            'credentials', name=self.user, password=self.pw)
        root.credentials.site = O.Element('site', contentUrl=self.site_url)
        if imp_user is not None:
            root.credentials.user = O.Element('user', id=imp_user.get('id'))
        O.deannotate(root, cleanup_namespaces=True)
        return ET.tostring(root)

    def _query_site_id(self):
        '''gets the id for the site specified'''
        url = "{}/api/2.0/sites/Default?key=name".format(self.server)
        # Parse the XML and grab the site-id
        print(url)
        r = requests.get(url,
                         headers={"x-tableau-auth": self.token})
        tsResponse = O.fromstring(r.text.encode())
        site_id = tsResponse.site.get('id')
        return site_id

    def _read_in_chunks(self, file_object, chunk_size=None):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        if chunk_size is None:
            chunk_size = 1024
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def sign_in(self, contentUrl=""):
        signin_xml = self._make_signin_payload()
        url = self.server + Routes['SIGN_IN']
        r = requests.post(
            self.server + Routes['SIGN_IN'],
            data=signin_xml
        )
        print(signin_xml)
        if r.status_code != 200:
            print(r.text)
            raise Exception("Could not sign in")
        tsResponse = O.fromstring(r.text.encode("utf-8"))
        print(tsResponse)
        self.token = tsResponse.credentials.get('token')
        self.site_id = tsResponse.credentials.site.get("id")
        if self.site_id is None:
            self.site_id = self._query_site_id()

        print("Your signin token is: " + self.token + "\n"
              + "Your site luid is: " + self.site_id)

    def sign_in_as(self, user, contentUrl=""):
        signin_xml = self._make_signin_payload(imp_user=user)
        print(signin_xml)
        url = self.server + Routes['SIGN_IN']
        r = requests.post(
            self.server + Routes['SIGN_IN'],
            data=signin_xml
        )
        if r.status_code != 200:
            print(r.text)
            raise Exception("Could not sign in")
        tsResponse = O.fromstring(r.text.encode("utf-8"))
        self.token = tsResponse.credentials.get('token')
        self.site_id = tsResponse.credentials.site.get("id")
        if self.site_id is None:
            self.site_id = self._query_site_id()

        print("Your signin token is: " + self.token + "\n"
              + "Your site luid is: " + self.site_id)

    def get_users(self):
        url = self.server + \
            Routes['GET_USERS_ON_SITE'].format(site_id=self.site_id)
        r = requests.get(url, headers={'x-tableau-auth': self.token})
        tsResponse = O.fromstring(r.text.encode("utf-8"))
        return [user for user in tsResponse.users.iterchildren()]

    def update_user(self, user, **kwargs):
        url = self.server + Routes['UPDATE_USER'].format(
            site_id=self.site_id, user_id=user.get('id'))
        tsRequest = O.Element('tsRequest')
        tsRequest.user = O.Element('user', **kwargs)
        O.deannotate(tsRequest, cleanup_namespaces=True)
        payload = ET.tostring(tsRequest)
        r = requests.put(url,
                         data=payload,
                         headers={'x-tableau-auth': self.token})
        print(r.text)
        # NOT DONE

    def query_groups(self):
        url = self.server + Routes['QUERY_GROUPS'].format(site_id=self.site_id)
        r = requests.get(url,
                         headers={"x-tableau-auth": self.token})
        tsResponse = O.fromstring(r.text.encode('utf-8'))
        number_of_groups = int(tsResponse.pagination.get('totalAvailable'))
        pageSize = int(tsResponse.pagination.get('pageSize'))

        groups = []
        groups.extend([g for g in tsResponse.groups.iterchildren()])

        if number_of_groups > pageSize:  # Need to page through responses
            number_of_pages = (int(number_of_groups) // int(pageSize))
            if number_of_pages % pageSize > 0:
                number_of_pages += 1
                print(str(number_of_pages) + " pages")

            for pagenum in range(2, number_of_pages + 1):
                r = requests.get(
                    url +
                    "?pageSize={}&pageNumber={}".format(
                        pageSize, str(pagenum)),
                    headers={"x-tableau-auth": self.token})
                tsResponse = O.fromstring(r.text.encode('utf-8'))
                groups.extend([g for g in tsResponse.groups.iterchildren()])

        return groups

    def create_group(self, name, is_ad=False, **kwargs):
        url = self.server + Routes['CREATE_GROUP'].format(site_id=self.site_id)
        tsRequest = O.Element('tsRequest')
        tsRequest.group = O.Element('group', name=name)
        if is_ad:
            # Can't have a method named 'import' so must use append
            tsRequest.group.append(O.Element('import',
                                             source="activeDirectory",
                                             **kwargs))
        O.deannotate(tsRequest, cleanup_namespaces=True)
        payload = ET.tostring(tsRequest)
        r = requests.post(url,
                          data=payload,
                          headers={"x-tableau-auth": self.token})
        tsResponse = O.fromstring(r.text.encode('utf-8'))
        return tsResponse.group

    def add_user(self, name, siteRole="Interactor"):
        url = self.server + \
            Routes['ADD_USER_TO_SITE'].format(site_id=self.site_id)
        tsRequest = O.Element('tsRequest')
        tsRequest.user = O.Element('user', name=name, siteRole=siteRole)
        O.deannotate(tsRequest, cleanup_namespaces=True)
        payload = ET.tostring(tsRequest)
        r = requests.post(url,
                          data=payload,
                          headers={"x-tableau-auth": self.token})
        print(r.status_code)
        tsResponse = O.fromstring(r.text.encode('utf-8'))
        return tsResponse

    def remove_user(self, user):
        url = self.server + Routes['REMOVE_USER_FROM_SITE'].format(
            site_id=self.site_id, user_id=user.get('id'))
        r = requests.delete(url, headers={"x-tableau-auth": self.token})
        print(r.text)
        if status_code == 204:
            return
        else:
            raise Exception()

    def create_site(self, **kwargs):
        url = self.server + Routes['CREATE_SITE']
        tsRequest = O.Element('tsRequest')
        tsRequest.site = O.Element('site', **kwargs)
        payload = ET.tostring(tsRequest)
        print(payload)
        r = requests.post(url,
                          data=payload,
                          headers={"x-tableau-auth": self.token})
        tsResponse = O.fromstring(r.text.encode())
        return tsResponse.site.get('id')

    def create_project(self, **kwargs):
        url = self.server + Routes['CREATE_PROJECT']
        tsRequest = O.Element('tsRequest')
        tsRequest.site = O.Element('project', **kwargs)
        payload = ET.tostring(tsRequest)
        r = requests.post(url,
                          data=payload,
                          headers={"x-tableau-auth": self.token})
        tsResponse = O.fromstring(r.text.encode())
        return tsResponse.project.get('id')


    def query_projects(self):
        url = self.server + \
            Routes['QUERY_PROJECTS'].format(site_id=self.site_id)
        r = requests.get(url,
                         headers={'x-tableau-auth': self.token})

        tsResponse = O.fromstring(r.text.encode('utf-8'))
        print(r.text)
        return [project for project in tsResponse.projects.iterchildren()]

    def _make_multipart(self, payload, blob_name):

        if blob_name.split('.')[1] in ('tde', 'tds', 'tdsx'):
            blob_type = 'tableau_datasource'
        else:
            blob_type = 'tableau_workbook'

        with open(blob_name, 'rb') as f:
            file_blob = f.read()

        request_fields = []
        request_payload = RequestField(
            name='request_payload', data=payload.decode("utf-8"), filename=None)
        request_payload.make_multipart(content_type='text/xml')
        request_fields.append(request_payload)

        blob_stream = RequestField(
            name=blob_type, data=file_blob, filename=blob_name)
        blob_stream.make_multipart(content_type='application/octet-stream')
        request_fields.append(blob_stream)

        post_body, content_type = encode_multipart_formdata(request_fields)
        content_type = ''.join(
            ('multipart/mixed',) + content_type.partition(';')[1:])

        return post_body, content_type

    def publish_datasource(self, ds_file, name, project):
        url = self.server + \
            Routes['PUBLISH_DATASOURCE'].format(site_id=self.site_id)
        tsRequest = O.Element('tsRequest')
        tsRequest.datasource = O.Element('datasource', name=name)
        tsRequest.datasource.project = O.Element('project', id=project)
        O.deannotate(tsRequest, cleanup_namespaces=True)
        payload = ET.tostring(tsRequest)

        post_body, content_type = self._make_multipart(payload, ds_file)

        r = requests.post(url,
                          data=post_body,
                          headers={
                              "x-tableau-auth": self.token,
                              'Content-Type': content_type
                          },
                          )

        tsResponse = O.fromstring(r.text.encode('utf-8'))
        print("Published datasource with id {}".format(
            tsResponse.datasource.get('id')))
        return tsResponse

    def publish_workbook(self, wb_file, name, project):
        url = self.server + \
            Routes['PUBLISH_WORKBOOK'].format(site_id=self.site_id)
        tsRequest = O.Element('tsRequest')
        tsRequest.workbook = O.Element('workbook', name=name)
        tsRequest.workbook.project = O.Element('project', id=project.get('id'))
        O.deannotate(tsRequest, cleanup_namespaces=True)
        payload = ET.tostring(tsRequest)

        post_body, content_type = self._make_multipart(payload, wb_file)

        r = requests.post(url,
                          data=post_body,
                          headers={
                              "x-tableau-auth": self.token, "Content-Type": content_type}
                          )
        tsResponse = O.fromstring(r.text.encode('utf-8'))
        print("Published workbook with id {}".format(
            tsResponse.workbook.get('id')))
        return tsResponse

    def publish_chunked_ds(self, file_name, chunk_size=None):
        init_upload_url = self.server + \
            "/api/2.0/sites/{}/fileUploads".format(self.site_id)
        r = requests.post(init_upload_url,
                          headers={'x-tableau-auth': self.token})

        upload_id = O.fromstring(
            r.text.encode('utf-8')).fileUpload.get('uploadSessionId')
        ds_type = file_name.split('.')[1]  # ugly
        blob = open(file_name, 'rb')
        file_chunks_to_upload = self._read_in_chunks(blob, chunk_size)
        upload_session_url = self.server + \
            "/api/2.0/sites/{}/fileUploads/{}".format(self.site_id, upload_id)
        for chunk in file_chunks_to_upload:
            r = requests.put(upload_session_url, files={
                             'request_payload': ('',
                                                 '',
                                                 'text/xml'),
                             'tableau_file': ('awesome.tdsx',
                                              chunk,
                                              'application/octet-stream',)
                             },
                             headers={"x-tableau-auth": self.token})
            if r.status_code != 200:
                break
        print("file uploaded")

        commit_url = self.server + \
            "/api/2.0/sites/{}/datasources?uploadSessionId={}&datasourceType={}".format(
                self.site_id, upload_id, ds_type)
        print(commit_url)

        req_xml = O.Element('tsRequest')
        req_xml.datasource = O.Element('datasource', name=name)
        req_xml.datasource.project = O.Element('project', id=PROJECT_ID)
        O.deannotate(req_xml, cleanup_namespaces=True)
        payload = ET.tostring(req_xml)
        r = requests.post(commit_url,
                          files={"request_payload": ('', payload, 'text/xml')})
        # TODO Not done yet

    def add_user_to_group(self, user, group):
        url = self.server + \
            Routes['ADD_USER_TO_GROUP'].format(
                site_id=self.site_id, group_id=group.get('id'))
        req_xml = O.Element('tsRequest')
        req_xml.user = O.Element('user', id=user.get('id'))
        O.deannotate(req_xml, cleanup_namespaces=True)
        payload = ET.tostring(req_xml)
        r = requests.post(url,
                          data=payload,
                          headers={"x-tableau-auth": self.token})
        tsResponse = O.fromstring(r.text.encode('utf-8'))
        return tsResponse

    def get_effective_permissions(self, user):
        url = self.server + \
            Routes['QUERY_WORKBOOKS_FOR_USER'].format(
                site_id=self.site_id, user_id=user.get('id'))
        r = requests.get(url,
                         headers={'x-tableau-auth': self.token})
        tsRequest = O.fromstring(r.text.encode())
        return tsRequest.workbooks.iterchildren()

    def remove_user_from_group(self, user, group):
        url = self.server + Routes['REMOVE_USER_FROM_GROUP'].format(
            site_id=self.site_id, user_id=user.get('id'), group=group.get('id'))
        r = requests.delete(url,
                            headers={'x-tableau-auth': self.token})
        return

    def download_workbook(self, workbook):
        url = self.server + Routes['DOWNLOAD_WORKBOOK'].format(site_id=self.site_id, workbook_id=workbook.get('id'))
        print(url)
        r = requests.get(url,
                         headers={"x-tableau-auth": self.token})
        filename = re.findall(r'filename="(.*)"', r.headers['Content-Disposition'])[0]
        print(filename)
        with open(filename, 'wb') as f:
            f.write(r.content)
        return

if __name__ == '__main__':
    client = TableauREST(
        server="http://qa-server", username="workgroupuser", password="HardW0rker")
    client.sign_in()




import xml.etree.ElementTree as ET
from .. import NAMESPACE


class TableauAuth(object):
    def __init__(self, username, password, site='', impersonate_id=None):
        # CHECK FOR USERNAME AND PASSWORD
        self.password = password
        self.username = username
        self.site = site
        self.impersonate_id = impersonate_id

    @staticmethod
    def from_response(parent_srv, resp):
        parsed_response = ET.fromstring(resp)
        parent_srv._site_id = parsed_response.find('.//t:site', namespaces=NAMESPACE).get('id', None)
        parent_srv._user_id = parsed_response.find('.//t:user', namespaces=NAMESPACE).get('id', None)
        auth_token = parsed_response.find('t:credentials', namespaces=NAMESPACE).get('token', None)
        parent_srv._auth_token = auth_token

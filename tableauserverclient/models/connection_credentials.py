from .property_decorators import property_is_boolean
import xml.etree.ElementTree as ET
from typing import Dict, TypeVar

T = TypeVar('T', bound='ConnectionCredentials')


class ConnectionCredentials(object):
    """Connection Credentials for Workbooks and Datasources publish request.

    Consider removing this object and other variables holding secrets
    as soon as possible after use to avoid them hanging around in memory.

    """

    def __init__(self, name: str, password: str, embed: bool = True,
                 oauth: bool = False) -> T:
        self.name = name
        self.password = password
        self.embed = embed
        self.oauth = oauth

    @property
    def embed(self):
        return self._embed

    @embed.setter
    @property_is_boolean
    def embed(self, value: bool):
        self._embed = value

    @property
    def oauth(self):
        return self._oauth

    @oauth.setter
    @property_is_boolean
    def oauth(self, value: bool):
        self._oauth = value

    @classmethod
    def from_xml_element(cls, parsed_response: ET.ElementTree, ns: Dict) -> T:
        connection_creds_xml = parsed_response.find('.//t:connectionCredentials', namespaces=ns)

        name = connection_creds_xml.get('name', None)
        password = connection_creds_xml.get('password', None)
        embed = connection_creds_xml.get('embed', None)
        oAuth = connection_creds_xml.get('oAuth', None)

        connection_creds = cls(name, password, embed, oAuth)
        return connection_creds

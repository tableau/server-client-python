import xml.etree.ElementTree as ET
from .exceptions import UnpopulatedPropertyError
from .property_decorators import property_not_nullable
from .tag_item import TagItem
from .. import NAMESPACE


class DatasourceItem(object):

    ALLOWED_ATTRIBUTES = {'id': '_id',
                          'name': 'name',
                          'datasource_type': '_datasource_type',
                          'content_url': '_content_url',
                          'created_at': '_created_at',
                          'updated_at': '_updated_at',
                          'tags': '_tags',
                          'project_id': 'project_id',
                          'project_name': '_project_name',
                          'owner_id': 'owner_id'}

    def __init__(self, project_id, name=None):
        self._connections = None
        self._content_url = None
        self._created_at = None
        self._id = None
        self._project_name = None
        self._tags = set()
        self._datasource_type = None
        self._updated_at = None
        self.name = name
        self.owner_id = None
        self.project_id = project_id

    @property
    def connections(self):
        if self._connections is None:
            error = 'Datasource item must be populated with connections first.'
            raise UnpopulatedPropertyError(error)
        return self._connections

    @property
    def content_url(self):
        return self._content_url

    @property
    def created_at(self):
        return self._created_at

    @property
    def id(self):
        return self._id

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    @property_not_nullable
    def project_id(self, value):
        self._project_id = value

    @property
    def project_name(self):
        return self._project_name

    @property
    def tags(self):
        return self._tags

    @property
    def datasource_type(self):
        return self._datasource_type

    @property
    def updated_at(self):
        return self._updated_at

    def _set_connections(self, connections):
        self._connections = connections

    def _parse_common_tags(self, datasource_xml):
        if not isinstance(datasource_xml, ET.Element):
            datasource_xml = ET.fromstring(datasource_xml).find('.//t:datasource', namespaces=NAMESPACE)
        if datasource_xml is not None:
            attribs = self._parse_element(datasource_xml)
            self._set_values(attribs)
        return self

    def _set_values(self, ds_attributes):

        for attribute in DatasourceItem.ALLOWED_ATTRIBUTES:
            if attribute in ds_attributes and ds_attributes[attribute]:
                setattr(self, DatasourceItem.ALLOWED_ATTRIBUTES[attribute], ds_attributes[attribute])


    @classmethod
    def from_response(cls, resp):
        all_datasource_items = list()
        parsed_response = ET.fromstring(resp)
        all_datasource_xml = parsed_response.findall('.//t:datasource', namespaces=NAMESPACE)

        for datasource_xml in all_datasource_xml:
            attribs = cls._parse_element(datasource_xml)
            datasource_item = cls(attribs['project_id'])
            datasource_item._set_values(attribs)
            all_datasource_items.append(datasource_item)
        return all_datasource_items

    @staticmethod
    def _parse_element(datasource_xml):
        id = datasource_xml.get('id', None)
        name = datasource_xml.get('name', None)
        datasource_type = datasource_xml.get('type', None)
        content_url = datasource_xml.get('contentUrl', None)
        created_at = datasource_xml.get('createdAt', None)
        updated_at = datasource_xml.get('updatedAt', None)

        tags = None
        tags_elem = datasource_xml.find('.//t:tags', namespaces=NAMESPACE)
        if tags_elem is not None:
            tags = TagItem.from_xml_element(tags_elem)

        project_id = None
        project_name = None
        project_elem = datasource_xml.find('.//t:project', namespaces=NAMESPACE)
        if project_elem is not None:
            project_id = project_elem.get('id', None)
            project_name = project_elem.get('name', None)

        owner_id = None
        owner_elem = datasource_xml.find('.//t:owner', namespaces=NAMESPACE)
        if owner_elem is not None:
            owner_id = owner_elem.get('id', None)

        return {k: v for k, v in locals().items()}

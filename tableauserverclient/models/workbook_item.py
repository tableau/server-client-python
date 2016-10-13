import xml.etree.ElementTree as ET
from .exceptions import UnpopulatedPropertyError
from .property_decorators import property_not_nullable, property_is_boolean
from .tag_item import TagItem
from .view_item import ViewItem
from .. import NAMESPACE
import copy


def string_to_bool(s):
    return s.lower() == 'true'


def _get_project_id(workbook_xml):
        project_id = None
        project_elem = workbook_xml.find('.//t:project', namespaces=NAMESPACE)
        if project_elem is not None:
            project_id = project_elem.get('id', None)
        return project_id


def _get_project_name(workbook_xml):
        project_name = None
        project_elem = workbook_xml.find('.//t:project', namespaces=NAMESPACE)
        if project_elem is not None:
            project_name = project_elem.get('name', None)
        return project_name


def _get_owner_id(workbook_xml):
        owner_id = None
        owner_tag = workbook_xml.find('.//t:owner', namespaces=NAMESPACE)
        if owner_tag is not None:
            owner_id = owner_tag.get('id', None)
        return owner_id


def _get_tags(workbook_xml):
    tags = None
    tags_elem = workbook_xml.find('.//t:tags', namespaces=NAMESPACE)
    if tags_elem is not None:
        tags = TagItem.from_xml_element(tags_elem)
    return tags


def _get_views(workbook_xml):
    views = None
    views_elem = workbook_xml.find('.//t:views', namespaces=NAMESPACE)
    if views_elem is not None:
        views = ViewItem.from_xml_element(views_elem)
    return views


class WorkbookItem(object):

    SCHEMA = {'_id': lambda x: x.get('id', None),
              'name': lambda x: x.get('name', None),
              '_content_url': lambda x: x.get('contentUrl', None),
              '_created_at': lambda x: x.get('createdAt', None),
              '_updated_at': lambda x: x.get('updatedAt', None),
              '_size': lambda x: int(x.get('size', None)),
              'show_tabs': lambda x: string_to_bool(x.get('showTabs', '')),
              'project_id': _get_project_id,
              '_project_name': _get_project_name,
              'owner_id': _get_owner_id,
              'tags': _get_tags,
              '_views': _get_views,
              }

    def __init__(self, project_id, name=None, show_tabs=False):
        self._connections = None
        self._content_url = None
        self._created_at = None
        self._id = None
        self._initial_tags = set()
        self._preview_image = None
        self._project_name = None
        self._size = None
        self._updated_at = None
        self._views = None
        self.name = name
        self.owner_id = None
        self.tags = set()
        self.project_id = project_id
        self.show_tabs = show_tabs

    @property
    def connections(self):
        if self._connections is None:
            error = "Workbook item must be populated with connections first."
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
    def preview_image(self):
        if self._preview_image is None:
            error = "Workbook item must be populated with its preview image first."
            raise UnpopulatedPropertyError(error)
        return self._preview_image

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
    def show_tabs(self):
        return self._show_tabs

    @show_tabs.setter
    @property_is_boolean
    def show_tabs(self, value):
        self._show_tabs = value

    @property
    def size(self):
        return self._size

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def views(self):
        if self._views is None:
            error = "Workbook item must be populated with views first."
            raise UnpopulatedPropertyError(error)
        return self._views

    def _set_connections(self, connections):
        self._connections = connections

    def _set_views(self, views):
        self._views = views

    def _set_preview_image(self, preview_image):
        self._preview_image = preview_image

    def _set_initial_tags(self, initial_tags):
        self._initial_tags = initial_tags

    def _get_initial_tags(self):
        return self._initial_tags

    def _parse_and_set_attribs(self, workbook_xml, attributes):
        if not isinstance(workbook_xml, ET.Element):
            workbook_xml = ET.fromstring(workbook_xml).find('.//t:workbook', namespaces=NAMESPACE)
        if workbook_xml is not None:
            attribs = {k: v for k, v in WorkbookItem._parse_xml(workbook_xml).items() if k in attributes}
            self._set_values(attribs)

        return self

    def _set_values(self, wb_attributes):
        for attribute in wb_attributes:
            setattr(self, attribute, wb_attributes[attribute])

    @classmethod
    def from_response(cls, resp):
        all_workbook_items = list()
        parsed_response = ET.fromstring(resp)
        all_workbook_xml = parsed_response.findall('.//t:workbook', namespaces=NAMESPACE)
        for workbook_xml in all_workbook_xml:
            attribs = WorkbookItem._parse_xml(workbook_xml)

            workbook_item = cls(attribs['project_id'])
            workbook_item._set_values(attribs)
            all_workbook_items.append(workbook_item)
        return all_workbook_items

    @staticmethod
    def _parse_xml(workbook_xml):
        attribs = {}
        for attribute, getter in WorkbookItem.SCHEMA.items():
            attribs[attribute] = getter(workbook_xml)
        return attribs

import xml.etree.ElementTree as ET
import re
from .. import NAMESPACE


class FavoriteItem(object):
    # Note that name must be the same as string value
    class Types:
        Workbook = 'Workbook'
        View = 'View'
        Datasource = 'Datasource'

    def __init__(self, label, id, type):
        self._label = None
        self._id = None
        self._type = None
        self.label = label
        self.id = id
        self.type = type

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        if not value:
            error = 'Label must be defined.'
            raise ValueError(error)
        else:
            self._label = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not value:
            error = 'ID must be defined.'
            raise ValueError(error)
        else:
            self._id = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if not value:
            error = 'Type must be defined.'
            raise ValueError(error)
        elif not hasattr(FavoriteItem.Types, value):
            error = 'Invalid type for favorite.'
            raise ValueError(error)
        else:
            self._type = value

    @classmethod
    def from_response(cls, resp):
        all_favorite_items = set()
        parsed_response = ET.fromstring(resp)
        all_favorite_xml = parsed_response.findall('.//t:favorite', namespaces=NAMESPACE)
        for favorite_xml in all_favorite_xml:
            child_elem = favorite_xml.getchildren()[0]
            leading_namespace = '{{{0}}}'.format(NAMESPACE['t'])
            favorite_type = child_elem.tag.replace(leading_namespace, '')
            subject_elem = favorite_xml.find('.//t:' + favorite_type, namespaces=NAMESPACE)
            id = subject_elem.get('id', None)
            label = favorite_xml.get('label', None)
            type = favorite_type.title()
            favorite_item = cls(label, id, type)
            all_favorite_items.add(favorite_item)
        return all_favorite_items

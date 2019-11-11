import xml.etree.ElementTree as ET
from .exceptions import UnpopulatedPropertyError
from .property_decorators import property_not_nullable, property_is_boolean, property_is_materialized_views_config
from .tag_item import TagItem
from .view_item import ViewItem
from .permissions_item import PermissionsRule
from ..datetime_helpers import parse_datetime
import copy


class WebhookItem(object):
    def __init__(self):
        self._id = None
        self.name = None
        self.url = None
        self._event = None

    def _set_values(self, id, name, url):
        if id is not None:
            self._id = id
        if name:
            self.name = name
        if url:
            self.url = url

    @property
    def id(self): return self._id

    @property
    def event(self): return "event"

    @classmethod
    def from_response(cls, resp, ns):
        all_webhooks_items = list()
        parsed_response = ET.fromstring(resp)
        all_webhooks_xml = parsed_response.findall('.//t:webhook', namespaces=ns)
        for webhook_xml in all_webhooks_xml:
            (id, name, url) = cls._parse_element(webhook_xml, ns)

            webhook_item = cls()
            webhook_item._set_values(id, name, url)
            all_webhooks_items.append(webhook_item)
        return all_webhooks_items

    @staticmethod
    def _parse_element(webhook_xml, ns):
        id = webhook_xml.get('id', None)
        name = webhook_xml.get('name', None)
        url = webhook_xml.get('.//t:webhook-destination-http[@url]')

        return id, name, url

    def __repr__(self):
        return "<Webhook id={} name={} url={} event={}>".format(self.id, self.name, self.url, self.event)
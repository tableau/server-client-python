import re
import xml.etree.ElementTree as ET

from defusedxml.ElementTree import fromstring

NAMESPACE_RE = re.compile(r"^{.*}")


def _parse_event(events):
    event = events[0]
    # Strip out the namespace from the tag name
    return NAMESPACE_RE.sub("", event.tag)


class WebhookItem:
    """
    The WebhookItem represents the webhook resources on Tableau Server or
    Tableau Cloud. This is the information that can be sent or returned in
    response to a REST API request for webhooks.

    Attributes
    ----------
    id : str | None
        The identifier (luid) for the webhook. You need this value to query a
        specific webhook with the get_by_id method or to delete a webhook with
        the delete method.

    name : str | None
        The name of the webhook. You must specify this when you create an
        instance of the WebhookItem.

    url : str | None
        The destination URL for the webhook. The webhook destination URL must
        be https and have a valid certificate. You must specify this when you
        create an instance of the WebhookItem.

    event : str | None
        The name of the Tableau event that triggers your webhook.This is either
        api-event-name or webhook-source-api-event-name: one of these is
        required to create an instance of the WebhookItem. We recommend using
        the api-event-name. The event name must be one of the supported events
        listed in the Trigger Events table.
        https://help.tableau.com/current/developer/webhooks/en-us/docs/webhooks-events-payload.html

    owner_id : str | None
        The identifier (luid) of the user who owns the webhook.

    is_enabled : bool | None
        Whether the webhook is enabled. Disabled webhooks do not fire.

    status_change_reason : str | None
        The reason the webhook status last changed (e.g. why it was disabled).
    """

    def __init__(self):
        self._id: str | None = None
        self.name: str | None = None
        self.url: str | None = None
        self._event: str | None = None
        self.owner_id: str | None = None
        self.is_enabled: bool | None = None
        self.status_change_reason: str | None = None

    def _set_values(self, id, name, url, event, owner_id, is_enabled=None, status_change_reason=None):
        if id is not None:
            self._id = id
        if name:
            self.name = name
        if url:
            self.url = url
        if event:
            self.event = event
        if owner_id:
            self.owner_id = owner_id
        if is_enabled is not None:
            self.is_enabled = is_enabled
        if status_change_reason is not None:
            self.status_change_reason = status_change_reason

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def event(self) -> str | None:
        if self._event:
            return self._event.removeprefix("webhook-source-event-")
        return None

    @event.setter
    def event(self, value: str | None) -> None:
        if value is None:
            self._event = None
        elif value.startswith("webhook-source-event-") or value.startswith("webhook-event-"):
            self._event = value
        else:
            self._event = f"webhook-source-event-{value}"

    @classmethod
    def from_response(cls: type["WebhookItem"], resp: bytes, ns) -> list["WebhookItem"]:
        all_webhooks_items = list()
        parsed_response = fromstring(resp)
        all_webhooks_xml = parsed_response.findall(".//t:webhook", namespaces=ns)
        for webhook_xml in all_webhooks_xml:
            values = cls._parse_element(webhook_xml, ns)

            webhook_item = cls()
            webhook_item._set_values(*values)
            all_webhooks_items.append(webhook_item)
        return all_webhooks_items

    def _parse_common_tags(self, webhook_xml, ns) -> "WebhookItem":
        """Merge fields from a server response into this item.

        Used by the update endpoint (matching the convention in users_endpoint
        and datasources_endpoint) so that locally-set fields are preserved
        when the server's response omits them.
        """
        if not isinstance(webhook_xml, ET.Element):
            parsed = fromstring(webhook_xml)
            webhook_xml = parsed.find(".//t:webhook", namespaces=ns)
        if webhook_xml is not None:
            values = self._parse_element(webhook_xml, ns)
            self._set_values(*values)
        return self

    @staticmethod
    def _parse_element(webhook_xml: ET.Element, ns) -> tuple:
        id = webhook_xml.get("id", None)
        name = webhook_xml.get("name", None)

        url = None
        url_tag = webhook_xml.find(".//t:webhook-destination-http", namespaces=ns)
        if url_tag is not None:
            url = url_tag.get("url", None)

        event = webhook_xml.findall(".//t:webhook-source/*", namespaces=ns)
        if event is not None and len(event) > 0:
            event = _parse_event(event)

        owner_id = None
        owner_tag = webhook_xml.find(".//t:owner", namespaces=ns)
        if owner_tag is not None:
            owner_id = owner_tag.get("id", None)

        is_enabled = None
        is_enabled_str = webhook_xml.get("isEnabled", None)
        if is_enabled_str is not None:
            is_enabled = is_enabled_str.lower() == "true"

        status_change_reason = webhook_xml.get("statusChangeReason", None)

        return id, name, url, event, owner_id, is_enabled, status_change_reason

    def __repr__(self) -> str:
        return f"<Webhook id={self.id} name={self.name} url={self.url} event={self.event} is_enabled={self.is_enabled}>"

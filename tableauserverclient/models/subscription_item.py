from typing import TYPE_CHECKING, Optional

from defusedxml.ElementTree import fromstring

from .property_decorators import property_is_boolean
from .schedule_item import ScheduleItem
from .target import Target

if TYPE_CHECKING:
    from .target import Target


class SubscriptionItem:
    """Represents a subscription returned by the Tableau REST API.

    Tableau **Server** and Tableau **Cloud** return a subscription's schedule in
    two different shapes:

    * **Server** references a named schedule by id::

        <schedule id="cfb2..." name="Weekday mornings"/>

    * **Cloud** inlines the schedule -- there is *no* ``id`` attribute; the
      ``frequency``, ``nextRunAt`` and a nested ``<frequencyDetails>`` describe
      it directly::

        <schedule frequency="Daily" nextRunAt="2026-08-29T16:55:00-0700">
          <frequencyDetails start="16:55:00" end="16:55:00">
            <intervals>
              <interval hours="24"/>
              <interval weekDay="Saturday"/>
            </intervals>
          </frequencyDetails>
        </schedule>

    The reliable Cloud-vs-Server discriminator on a parsed ``SubscriptionItem``
    is ``schedule.interval_item is not None`` (Cloud inlines the interval
    detail; Server only sends an ``id``/``name`` reference and this field will
    always be ``None`` there). ``schedule.id is None`` also identifies Cloud
    but only in combination with ``schedule is not None`` -- see below.

    Attributes
    ----------
    schedule_id : str | None
        The referenced schedule's id. **Populated on Server**; **always** ``None``
        on Tableau Cloud because the REST API does not send a schedule id for
        inlined schedules. Client code that filters subscriptions with
        ``sub.schedule_id == some_id`` will silently return no results on Cloud
        -- use :attr:`schedule` instead, or branch on the server type.

    schedule : ScheduleItem | None
        A :class:`ScheduleItem` populated with whatever the server returned.
        On Server: ``schedule.id`` and ``schedule.name`` are set. On Cloud:
        ``schedule.frequency``, ``schedule.next_run_at`` and
        ``schedule.interval_item`` (a ``DailyInterval`` / ``WeeklyInterval`` /
        etc. carrying the parsed ``<frequencyDetails>``) are set. May be
        ``None`` if the API returned a subscription with no ``<schedule>``
        child at all -- always guard before dereferencing.
    """

    def __init__(self, subject: str, schedule_id: str, user_id: str, target: "Target") -> None:
        self._id = None
        self.attach_image = True
        self.attach_pdf = False
        self.message = None
        self.page_orientation = None
        self.page_size_option = None
        self.schedule_id = schedule_id
        self.send_if_view_empty = True
        self.subject = subject
        self.suspended = False
        self.target = target
        self.user_id = user_id
        self.schedule: Optional[ScheduleItem] = None

    def __repr__(self) -> str:
        if self.id is not None:
            return "<Subscription#{_id} subject({subject}) schedule_id({schedule_id}) user_id({user_id}) \
                target({target})".format(**self.__dict__)
        else:
            return "<Subscription subject({subject}) schedule_id({schedule_id}) user_id({user_id}) \
                target({target})".format(**self.__dict__)

    @property
    def id(self):
        return self._id

    @property
    def attach_image(self) -> bool:
        return self._attach_image

    @attach_image.setter
    @property_is_boolean
    def attach_image(self, value: bool):
        self._attach_image = value

    @property
    def attach_pdf(self) -> bool:
        return self._attach_pdf

    @attach_pdf.setter
    @property_is_boolean
    def attach_pdf(self, value: bool) -> None:
        self._attach_pdf = value

    @property
    def send_if_view_empty(self) -> bool:
        return self._send_if_view_empty

    @send_if_view_empty.setter
    @property_is_boolean
    def send_if_view_empty(self, value: bool) -> None:
        self._send_if_view_empty = value

    @property
    def suspended(self) -> bool:
        return self._suspended

    @suspended.setter
    @property_is_boolean
    def suspended(self, value: bool) -> None:
        self._suspended = value

    @classmethod
    def from_response(cls: type, xml: bytes, ns) -> list["SubscriptionItem"]:
        parsed_response = fromstring(xml)
        all_subscriptions_xml = parsed_response.findall(".//t:subscription", namespaces=ns)

        all_subscriptions = [SubscriptionItem._parse_element(x, ns) for x in all_subscriptions_xml]
        return all_subscriptions

    @classmethod
    def _parse_element(cls, element, ns):
        schedule_element = element.find(".//t:schedule", namespaces=ns)
        content_element = element.find(".//t:content", namespaces=ns)
        user_element = element.find(".//t:user", namespaces=ns)

        # Schedule element -- shape differs between Server (id + name reference)
        # and Cloud (inlined frequency + frequencyDetails, no id). Populate the
        # structured ``schedule`` attribute for both, and keep ``schedule_id``
        # populated on Server for backward compatibility.
        schedule_id = None
        schedule: Optional[ScheduleItem] = None
        if schedule_element is not None:
            schedule_id = schedule_element.get("id", None)
            # ScheduleItem.from_element does its own ``.//t:schedule`` lookup;
            # pass the <subscription> element so the descendant search finds
            # the inlined child. The XSD constrains this to ``1..1`` so the
            # returned list is length 1; if the API ever returns two we take
            # the first.
            parsed = ScheduleItem.from_element(element, ns)
            if parsed:
                schedule = parsed[0]

        # Content element
        target = None
        send_if_view_empty = None
        if content_element is not None:
            target = Target(content_element.get("id", None), content_element.get("type"))
            send_if_view_empty = string_to_bool(content_element.get("sendIfViewEmpty", ""))

        # User element
        user_id = None
        if user_element is not None:
            user_id = user_element.get("id", None)

        # Main attributes
        id_ = element.get("id", None)
        subject = element.get("subject", None)
        attach_image = string_to_bool(element.get("attachImage", ""))
        attach_pdf = string_to_bool(element.get("attachPdf", ""))
        message = element.get("message", None)
        page_orientation = element.get("pageOrientation", None)
        page_size_option = element.get("pageSizeOption", None)
        suspended = string_to_bool(element.get("suspended", ""))

        # Create SubscriptionItem and set fields
        sub = cls(subject, schedule_id, user_id, target)
        sub._id = id_
        sub.attach_image = attach_image
        sub.attach_pdf = attach_pdf
        sub.message = message
        sub.page_orientation = page_orientation
        sub.page_size_option = page_size_option
        sub.send_if_view_empty = send_if_view_empty
        sub.suspended = suspended
        sub.schedule = schedule

        return sub


# Used to convert string represented boolean to a boolean type
def string_to_bool(s: str) -> bool:
    return s.lower() == "true"

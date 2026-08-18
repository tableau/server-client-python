from typing import TYPE_CHECKING

from defusedxml.ElementTree import fromstring

from .property_decorators import property_is_boolean
from .target import Target
from tableauserverclient.models import ScheduleItem

if TYPE_CHECKING:
    from .target import Target


class SubscriptionItem:
    """A subscription that sends a view or workbook to a user on a schedule.

    Subscriptions fire on one of two triggers:

    1. **Time-based** (the common case): the referenced schedule's time
       trigger runs -- e.g. a "Weekly Monday 8am" schedule fires the
       subscription every Monday at 8am. Construct these with the normal
       ``SubscriptionItem(subject, schedule_id, user_id, target)`` form.

    2. **Extract-refresh-triggered**: the referenced schedule's extract
       refresh completes -- the subscription fires alongside the refresh,
       so recipients always get the freshest data. Use the
       :meth:`on_extract_refresh` classmethod to construct these; it sets
       :attr:`refresh_extract_triggered` to ``True`` for you.

    In the Cloud web UI, extract-refresh-triggered subscriptions show up
    as schedule "On Extract Refresh". At the REST API level there is no
    "On Extract Refresh" schedule type; instead the subscription
    references an existing extract-refresh schedule *and* sets
    ``refreshExtractTriggered=true`` on the payload.

    Examples
    --------
    Time-based subscription:

    >>> sub = TSC.SubscriptionItem(
    ...     subject="Weekly report",
    ...     schedule_id=weekly_schedule.id,
    ...     user_id=user.id,
    ...     target=TSC.Target(view.id, "view"),
    ... )
    >>> server.subscriptions.create(sub)

    Extract-refresh-triggered subscription:

    >>> sub = TSC.SubscriptionItem.on_extract_refresh(
    ...     subject="Send when refresh finishes",
    ...     extract_refresh_schedule_id=nightly_refresh_schedule.id,
    ...     user_id=user.id,
    ...     target=TSC.Target(view.id, "view"),
    ... )
    >>> server.subscriptions.create(sub)
    """

    def __init__(self, subject: str, schedule_id: str | None, user_id: str, target: "Target") -> None:
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
        self.schedule = None
        self._refresh_extract_triggered: bool = False

    @classmethod
    def on_extract_refresh(
        cls,
        subject: str,
        extract_refresh_schedule_id: str,
        user_id: str,
        target: "Target",
    ) -> "SubscriptionItem":
        """Construct a subscription that fires when an extract refresh runs.

        The subscription references an existing extract-refresh schedule and
        will fire alongside that schedule's extract refresh, so recipients
        get the freshest data. Server-side this maps to
        ``refreshExtractTriggered=true`` on the subscription entity; the Cloud
        UI surfaces the same state as schedule type "On Extract Refresh".

        Parameters
        ----------
        subject : str
            Subscription subject line, shown in the delivered email.
        extract_refresh_schedule_id : str
            ID of an existing schedule that owns an extract refresh. On Cloud
            list schedules with ``server.schedules.get()`` and filter to the
            extract-refresh schedules; on-prem the same list is populated by
            the site's server-authored schedules.
        user_id : str
            ID of the recipient user.
        target : Target
            The workbook or view to send.

        Returns
        -------
        SubscriptionItem
            A subscription with ``refresh_extract_triggered`` set to True.
            Pass to ``server.subscriptions.create(...)`` to create it.

        Notes
        -----
        This factory does not validate that ``extract_refresh_schedule_id``
        actually references an extract-refresh schedule. Referencing a
        non-extract schedule with ``refresh_extract_triggered=True`` is a
        server-side error and will surface when ``create()`` is called.

        Related to tableau/server-client-python#1658.
        """
        sub = cls(subject, extract_refresh_schedule_id, user_id, target)
        sub.refresh_extract_triggered = True
        return sub

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

    @property
    def refresh_extract_triggered(self) -> bool:
        """Whether this subscription fires when its schedule's extract refresh runs.

        When True, the subscription must reference an existing extract-refresh
        schedule (via ``schedule_id``) and will fire alongside that schedule's
        extract refresh. When False (the default), the subscription fires on
        the schedule's time trigger like every other subscription.

        The Cloud web UI surfaces the True state as schedule type "On Extract
        Refresh"; there is no such REST-API schedule type, so callers must set
        this flag explicitly. Prefer :meth:`on_extract_refresh` when
        constructing new extract-refresh-triggered subscriptions -- it wires
        up ``schedule_id`` and this flag together in one call.

        Setting this to True on a subscription that references a non-extract
        schedule (Subscription, Flow, System, etc.) is a server-side error;
        the ``create()``/``update()`` call will raise. TSC does not fetch the
        referenced schedule to validate this client-side.

        **Updating an existing subscription:** if an update changes the
        referenced schedule, the server silently forces this flag back to
        False on that same call, regardless of what the client sent. To
        convert a time-based subscription into an extract-refresh-triggered
        one, issue two updates: first change ``schedule_id``, then set
        ``refresh_extract_triggered = True`` on a second call.

        **Manual-build update() footgun:** every ``subscriptions.update()``
        payload now carries ``refreshExtractTriggered="true"`` or
        ``"false"``. The safe pattern is fetch-then-mutate-then-update, so
        the value round-trips through the parser. If instead you build a
        fresh ``SubscriptionItem`` locally, assign ``_id`` yourself, and
        call ``update()``, the default False on the new item will flip an
        existing extract-refresh-triggered subscription off on the server.
        Fetch first.
        """
        return self._refresh_extract_triggered

    @refresh_extract_triggered.setter
    @property_is_boolean
    def refresh_extract_triggered(self, value: bool) -> None:
        self._refresh_extract_triggered = value

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

        # Schedule element
        schedule_id = None
        schedule = None
        if schedule_element is not None:
            schedule_id = schedule_element.get("id", None)

            # If schedule id is not provided, then TOL with full schedule provided
            if schedule_id is None:
                schedule = ScheduleItem.from_element(element, ns)

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
        refresh_extract_triggered = string_to_bool(element.get("refreshExtractTriggered", ""))

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
        sub.refresh_extract_triggered = refresh_extract_triggered

        return sub


# Used to convert string represented boolean to a boolean type
def string_to_bool(s: str) -> bool:
    return s.lower() == "true"

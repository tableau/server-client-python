import xml.etree.ElementTree as ET

from .property_decorators import property_not_empty, property_is_enum, property_is_boolean
from .user_item import UserItem
from .view_item import ViewItem


class DataAlertItem(object):
    class Frequency:
        Once = 'Once'
        Frequently = 'Frequently'
        Hourly = 'Hourly'
        Daily = 'Daily'
        Weekly = 'Weekly'

    def __init__(self):
        self._id = None
        self._subject = None
        self._creatorId = None
        self._createdAt = None
        self._updatedAt = None
        self._frequency = None
        self._public = None
        self._owner_id = None
        self._owner_name = None
        self._view_id = None
        self._view_name = None
        self._workbook_id = None
        self._workbook_name = None
        self._project_id = None
        self._project_name = None
        self._recipients = None

    def __repr__(self):
        return "<Data Alert {id} subject={subject} frequency={frequency} \
                public={public}>".format(**self.__dict__)

    @property
    def id(self):
        return self._id

    @property
    def subject(self):
        return self._subject

    @subject.setter
    @property_not_empty
    def subject(self, value):
        self._subject = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    @property_is_enum(Frequency)
    def frequency(self, value):
        self._frequency = value

    @property
    def public(self):
        return self._public

    @public.setter
    @property_is_boolean
    def public(self, value):
        self._public = value

    @property
    def creatorId(self):
        return self._creatorId

    @property
    def recipients(self):
        return self._recipients or list()

    @property
    def createdAt(self):
        return self._createdAt

    @property
    def updatedAt(self):
        return self._updatedAt

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def owner_name(self):
        return self._owner_name

    @property
    def view_id(self):
        return self._view_id

    @property
    def view_name(self):
        return self._view_name

    @property
    def workbook_id(self):
        return self._workbook_id

    @property
    def workbook_name(self):
        return self._workbook_name

    @property
    def project_id(self):
        return self._project_id

    @property
    def project_name(self):
        return self._project_name

    def _set_values(self, id, subject, creatorId, createdAt, updatedAt,
                    frequency, public, recipients, owner_id, owner_name,
                    view_id, view_name, workbook_id, workbook_name, project_id,
                    project_name):
        if id is not None:
            self._id = id
        if subject:
            self._subject = subject
        if creatorId:
            self._creatorId = creatorId
        if createdAt:
            self._createdAt = createdAt
        if updatedAt:
            self._updatedAt = updatedAt
        if frequency:
            self._frequency = frequency
        if public:
            self._public = public
        if owner_id:
            self._owner_id = owner_id
        if owner_name:
            self._owner_name = owner_name
        if view_id:
            self._view_id = view_id
        if view_name:
            self._view_name = view_name
        if workbook_id:
            self._workbook_id = workbook_id
        if workbook_name:
            self._workbook_name = workbook_name
        if project_id:
            self._project_id = project_id
        if project_name:
            self._project_name = project_name
        if recipients:
            self._recipients = recipients

    @classmethod
    def from_response(cls, resp, ns):
        all_alert_items = list()
        parsed_response = ET.fromstring(resp)
        all_alert_xml = parsed_response.findall('.//t:dataAlert', namespaces=ns)

        for alert_xml in all_alert_xml:
            kwargs = cls._parse_element(alert_xml, ns)
            alert_item = cls()
            alert_item._set_values(**kwargs)
            all_alert_items.append(alert_item)

        return all_alert_items

    @staticmethod
    def _parse_element(alert_xml, ns):
        kwargs = dict()
        kwargs['id'] = alert_xml.get('id', None)
        kwargs['subject'] = alert_xml.get('subject', None)
        kwargs['creatorId'] = alert_xml.get('creatorId', None)
        kwargs['createdAt'] = alert_xml.get('createdAt', None)
        kwargs['updatedAt'] = alert_xml.get('updatedAt', None)
        kwargs['frequency'] = alert_xml.get('frequency', None)
        kwargs['public'] = alert_xml.get('public', None)

        owner = alert_xml.findall('.//t:owner', namespaces=ns)[0]
        kwargs['owner_id'] = owner.get('id', None)
        kwargs['owner_name'] = owner.get('name', None)

        view_response = alert_xml.findall('.//t:view', namespaces=ns)[0]
        kwargs['view_id'] = view_response.get('id', None)
        kwargs['view_name'] = view_response.get('name', None)

        workbook_response = view_response.findall('.//t:workbook', namespaces=ns)[0]
        kwargs['workbook_id'] = workbook_response.get('id', None)
        kwargs['workbook_name'] = workbook_response.get('name', None)
        project_response = view_response.findall('.//t:project', namespaces=ns)[0]
        kwargs['project_id'] = project_response.get('id', None)
        kwargs['project_name'] = project_response.get('name', None)

        recipients = alert_xml.findall('.//t:recipient', namespaces=ns)
        kwargs['recipients'] = [recipient.get('id', None) for recipient in recipients]

        return kwargs

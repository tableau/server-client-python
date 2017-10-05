import xml.etree.ElementTree as ET
from .exceptions import UnpopulatedPropertyError
from .. import NAMESPACE
from .target import Target

class SubscriptionItem(object):

    def __init__(self, id_, schedule_id, user_id, target):
        self.id = id_
        self.schedule_id = schedule_id
        self.user_id = user_id
        self.target = target

    def __repr__(self):
        return "<Subscription#{id} schedule_id({schedule_id}) user_id({user_id}) \
            target({target})".format(**self.__dict__)

    @classmethod
    def from_response(cls, xml):
        parsed_response = ET.fromstring(xml)
        all_subscriptions_xml = parsed_response.findall(
            './/t:subscription', namespaces=NAMESPACE)

        all_subscriptions = (SubscriptionItem._parse_element(x) for x in all_subscriptions_xml)

        return list(all_subscriptions)

    @classmethod
    def _parse_element(cls, element):
        schedule_id = None
        target = None

        schedule_element = element.find('.//t:schedule', namespaces=NAMESPACE)
        content_element = element.find('.//t:content', namespaces=NAMESPACE)
        user_element = element.find('.//t:user', namespaces=NAMESPACE)

        if schedule_element is not None:
            schedule_id = schedule_element.get('id', None)

        if content_element is not None:
            target = Target(content_element.get('id', None), content_element.get('type'))

        if user_element is not None:
            user_id = user_element.get('id')


        id_ = element.get('id', None)
        return cls(id_, schedule_id, user_id, target)

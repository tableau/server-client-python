import xml.etree.ElementTree as ET
from .target import Target


class JobItem(object):
    def __init__(self, id_, job_type, created_at, started_at=None, completed_at=None, finish_code=0):
        self._id = id_
        self._type = job_type
        self._created_at = created_at
        self._started_at = started_at
        self._completed_at = completed_at
        self._finish_code = finish_code

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def created_at(self):
        return self._created_at

    @property
    def started_at(self):
        return self._started_at

    @property
    def completed_at(self):
        return self._completed_at

    @property
    def finish_code(self):
        return self._finish_code

    def __repr__(self):
        return "<Job#{_id} {_type} created_at({_created_at}) started_at({_started_at}) completed_at({_completed_at})" \
               " finish_code({_finish_code})>".format(**self.__dict__)

    @classmethod
    def from_response(cls, xml, ns):
        parsed_response = ET.fromstring(xml)
        all_tasks_xml = parsed_response.findall(
            './/t:job', namespaces=ns)

        all_tasks = [JobItem._parse_element(x, ns) for x in all_tasks_xml]

        return all_tasks

    @classmethod
    def _parse_element(cls, element, ns):
        id_ = element.get('id', None)
        type_ = element.get('type', None)
        created_at = element.get('createdAt', None)
        started_at = element.get('startedAt', None)
        completed_at = element.get('completedAt', None)
        finish_code = element.get('finishCode', -1)
        return cls(id_, type_, created_at, started_at, completed_at, finish_code)

from typing import List, Optional, TYPE_CHECKING

from defusedxml.ElementTree import fromstring

from .flow_run_item import FlowRunItem
from ..datetime_helpers import parse_datetime

if TYPE_CHECKING:
    import datetime


class JobItem(object):
    class FinishCode:
        """
        Status codes as documented on
        https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_jobs_tasks_and_schedules.htm#query_job
        """

        Success: int = 0
        Failed: int = 1
        Cancelled: int = 2

    def __init__(
        self,
        id_: str,
        job_type: str,
        progress: str,
        created_at: "datetime.datetime",
        started_at: Optional["datetime.datetime"] = None,
        completed_at: Optional["datetime.datetime"] = None,
        finish_code: int = 0,
        notes: Optional[List[str]] = None,
        mode: Optional[str] = None,
        workbook_id: Optional[str] = None,
        datasource_id: Optional[str] = None,
        flow_run: Optional[FlowRunItem] = None,
    ):
        self._id = id_
        self._type = job_type
        self._progress = progress
        self._created_at = created_at
        self._started_at = started_at
        self._completed_at = completed_at
        self._finish_code = finish_code
        self._notes: List[str] = notes or []
        self._mode = mode
        self._workbook_id = workbook_id
        self._datasource_id = datasource_id
        self._flow_run = flow_run

    @property
    def id(self) -> str:
        return self._id

    @property
    def type(self) -> str:
        return self._type

    @property
    def progress(self) -> str:
        return self._progress

    @property
    def created_at(self) -> "datetime.datetime":
        return self._created_at

    @property
    def started_at(self) -> Optional["datetime.datetime"]:
        return self._started_at

    @property
    def completed_at(self) -> Optional["datetime.datetime"]:
        return self._completed_at

    @property
    def finish_code(self) -> int:
        return self._finish_code

    @property
    def notes(self) -> List[str]:
        return self._notes

    @property
    def mode(self) -> Optional[str]:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        # check for valid data here
        self._mode = value

    @property
    def workbook_id(self) -> Optional[str]:
        return self._workbook_id

    @workbook_id.setter
    def workbook_id(self, value: Optional[str]) -> None:
        self._workbook_id = value

    @property
    def datasource_id(self) -> Optional[str]:
        return self._datasource_id

    @datasource_id.setter
    def datasource_id(self, value: Optional[str]) -> None:
        self._datasource_id = value

    @property
    def flow_run(self):
        return self._flow_run

    @flow_run.setter
    def flow_run(self, value):
        self._flow_run = value

    def __repr__(self):
        return (
            "<Job#{_id} {_type} created_at({_created_at}) started_at({_started_at}) completed_at({_completed_at})"
            " progress ({_progress}) finish_code({_finish_code})>".format(**self.__dict__)
        )

    @classmethod
    def from_response(cls, xml, ns) -> List["JobItem"]:
        parsed_response = fromstring(xml)
        all_tasks_xml = parsed_response.findall(".//t:job", namespaces=ns)

        all_tasks = [JobItem._parse_element(x, ns) for x in all_tasks_xml]

        return all_tasks

    @classmethod
    def _parse_element(cls, element, ns):
        id_ = element.get("id", None)
        type_ = element.get("type", None)
        progress = element.get("progress", None)
        created_at = parse_datetime(element.get("createdAt", None))
        started_at = parse_datetime(element.get("startedAt", None))
        completed_at = parse_datetime(element.get("completedAt", None))
        finish_code = int(element.get("finishCode", -1))
        notes = [note.text for note in element.findall(".//t:notes", namespaces=ns)] or None
        mode = element.get("mode", None)
        workbook = element.find(".//t:workbook[@id]", namespaces=ns)
        workbook_id = workbook.get("id") if workbook is not None else None
        datasource = element.find(".//t:datasource[@id]", namespaces=ns)
        datasource_id = datasource.get("id") if datasource is not None else None
        flow_run = None
        for flow_job in element.findall(".//t:runFlowJobType", namespaces=ns):
            flow_run = FlowRunItem()
            flow_run._id = flow_job.get("flowRunId", None)
            for flow in flow_job.findall(".//t:flow", namespaces=ns):
                flow_run._flow_id = flow.get("id", None)
                flow_run._started_at = created_at or started_at
        return cls(
            id_,
            type_,
            progress,
            created_at,
            started_at,
            completed_at,
            finish_code,
            notes,
            mode,
            workbook_id,
            datasource_id,
            flow_run,
        )


class BackgroundJobItem(object):
    class Status:
        Pending: str = "Pending"
        InProgress: str = "InProgress"
        Success: str = "Success"
        Failed: str = "Failed"
        Cancelled: str = "Cancelled"

    def __init__(
        self,
        id_: str,
        created_at: "datetime.datetime",
        priority: int,
        job_type: str,
        status: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        started_at: Optional["datetime.datetime"] = None,
        ended_at: Optional["datetime.datetime"] = None,
    ):
        self._id = id_
        self._type = job_type
        self._status = status
        self._created_at = created_at
        self._started_at = started_at
        self._ended_at = ended_at
        self._priority = priority
        self._title = title
        self._subtitle = subtitle

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> Optional[str]:
        """For API consistency - all other resource endpoints have a name attribute which is used to display what
        they are.  Alias title as name to allow consistent handling of resources in the list sample."""
        return self._title

    @property
    def status(self) -> str:
        return self._status

    @property
    def type(self) -> str:
        return self._type

    @property
    def created_at(self) -> "datetime.datetime":
        return self._created_at

    @property
    def started_at(self) -> Optional["datetime.datetime"]:
        return self._started_at

    @property
    def ended_at(self) -> Optional["datetime.datetime"]:
        return self._ended_at

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def subtitle(self) -> Optional[str]:
        return self._subtitle

    @property
    def priority(self) -> int:
        return self._priority

    @classmethod
    def from_response(cls, xml, ns) -> List["BackgroundJobItem"]:
        parsed_response = fromstring(xml)
        all_tasks_xml = parsed_response.findall(".//t:backgroundJob", namespaces=ns)
        return [cls._parse_element(x, ns) for x in all_tasks_xml]

    @classmethod
    def _parse_element(cls, element, ns):
        id_ = element.get("id", None)
        type_ = element.get("jobType", None)
        status = element.get("status", None)
        created_at = parse_datetime(element.get("createdAt", None))
        started_at = parse_datetime(element.get("startedAt", None))
        ended_at = parse_datetime(element.get("endedAt", None))
        priority = element.get("priority", None)
        title = element.get("title", None)
        subtitle = element.get("subtitle", None)

        return cls(
            id_,
            created_at,
            priority,
            type_,
            status,
            title,
            subtitle,
            started_at,
            ended_at,
        )

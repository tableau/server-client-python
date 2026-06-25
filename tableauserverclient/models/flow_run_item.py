import itertools
from datetime import datetime

from defusedxml.ElementTree import fromstring

from tableauserverclient.datetime_helpers import parse_datetime


class FlowRunItem:
    def __init__(self) -> None:
        self._id: str = ""
        self._flow_id: str | None = None
        self._status: str | None = None
        self._started_at: datetime | None = None
        self._completed_at: datetime | None = None
        self._progress: str | None = None
        self._background_job_id: str | None = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def flow_id(self) -> str | None:
        return self._flow_id

    @property
    def status(self) -> str | None:
        return self._status

    @property
    def started_at(self) -> datetime | None:
        return self._started_at

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def progress(self) -> str | None:
        return self._progress

    @property
    def background_job_id(self) -> str | None:
        return self._background_job_id

    def _set_values(
        self,
        id,
        flow_id,
        status,
        started_at,
        completed_at,
        progress,
        background_job_id,
    ):
        if id is not None:
            self._id = id
        if flow_id is not None:
            self._flow_id = flow_id
        if status is not None:
            self._status = status
        if started_at is not None:
            self._started_at = started_at
        if completed_at is not None:
            self._completed_at = completed_at
        if progress is not None:
            self._progress = progress
        if background_job_id is not None:
            self._background_job_id = background_job_id

    @classmethod
    def from_response(cls: type["FlowRunItem"], resp: bytes, ns: dict | None) -> list["FlowRunItem"]:
        all_flowrun_items = list()
        parsed_response = fromstring(resp)
        all_flowrun_xml = itertools.chain(
            parsed_response.findall(".//t:flowRun[@id]", namespaces=ns),
            parsed_response.findall(".//t:flowRuns[@id]", namespaces=ns),
        )

        for flowrun_xml in all_flowrun_xml:
            parsed = cls._parse_element(flowrun_xml, ns)
            flowrun_item = cls()
            flowrun_item._set_values(**parsed)
            all_flowrun_items.append(flowrun_item)
        return all_flowrun_items

    @staticmethod
    def _parse_element(flowrun_xml, ns):
        result = {}
        result["id"] = flowrun_xml.get("id", None)
        result["flow_id"] = flowrun_xml.get("flowId", None)
        result["status"] = flowrun_xml.get("status", None)
        result["started_at"] = parse_datetime(flowrun_xml.get("startedAt", None))
        result["completed_at"] = parse_datetime(flowrun_xml.get("completedAt", None))
        result["progress"] = flowrun_xml.get("progress", None)
        result["background_job_id"] = flowrun_xml.get("backgroundJobId", None)

        return result

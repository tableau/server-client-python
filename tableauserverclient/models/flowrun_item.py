from typing import Any, Dict, Mapping
import xml.etree.ElementTree as ET
from .property_decorators import property_not_nullable
from ..datetime_helpers import parse_datetime
import itertools
from datetime import datetime


class FlowRunItem(object):
    def __init__(self) -> None:
        self._id: str = None
        self._flow_id: str = None
        self._status: str = None
        self._started_at: datetime = None
        self._completed_at: datetime = None
        self._progress: str = None
        self._background_job_id: str = None

    
    @property
    def id(self):
        return self._id


    @property
    def flow_id(self):
        return self._flow_id


    @property
    def status(self):
        return self._status


    @property
    def started_at(self):
        return self._started_at


    @property
    def completed_at(self):
        return self._completed_at


    @property
    def progress(self):
        return self._progress


    @property
    def background_job_id(self):
        return self._background_job_id


    def _set_values(
        self,
        id: str,
        flow_id: str,
        status: str,
        started_at: datetime,
        completed_at: datetime,
        progress: str,
        background_job_id: str
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
    def from_response(cls, resp, ns):
        all_flowrun_items = list()
        parsed_response = ET.fromstring(resp)
        all_flowrun_xml = itertools.chain(
            parsed_response.findall(".//t:flowRun[@id]", namespaces=ns),
            parsed_response.findall(".//t:flowRuns[@id]", namespaces=ns)
        )

        for flowrun_xml in all_flowrun_xml:
            parsed = cls._parse_element(flowrun_xml, ns)
            flowrun_item = cls()
            flowrun_item._set_values(**parsed)
            all_flowrun_items.append(flowrun_item)
        return all_flowrun_items


    @staticmethod
    def _parse_element(flowrun_xml: ET.Element, ns: Mapping[str, str]) -> Dict[str, Any]:
        result = {}
        result['id'] = flowrun_xml.get("id", None)
        result['flow_id'] = flowrun_xml.get("flowId", None)
        result['status'] = flowrun_xml.get("status", None)
        result['started_at'] = parse_datetime(flowrun_xml.get("startedAt", None))
        result['completed_at'] = parse_datetime(flowrun_xml.get("completedAt", None))
        result['progress'] = flowrun_xml.get("progress", None)
        result['background_job_id'] = flowrun_xml.get("backgroundJobId", None)

        return result

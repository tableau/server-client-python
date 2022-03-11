import logging

from defusedxml.ElementTree import fromstring

from .datasource_item import DatasourceItem
from .flow_item import FlowItem
from .project_item import ProjectItem
from .view_item import ViewItem
from .workbook_item import WorkbookItem

logger = logging.getLogger("tableau.models.favorites_item")

from typing import Dict, List, Union

FavoriteType = Dict[
    str,
    List[
        Union[
            DatasourceItem,
            ProjectItem,
            FlowItem,
            ViewItem,
            WorkbookItem,
        ]
    ],
]


class FavoriteItem:
    class Type:
        Workbook: str = "workbook"
        Datasource: str = "datasource"
        View: str = "view"
        Project: str = "project"
        Flow: str = "flow"

    @classmethod
    def from_response(cls, xml: str, namespace: Dict) -> FavoriteType:
        favorites: FavoriteType = {
            "datasources": [],
            "flows": [],
            "projects": [],
            "views": [],
            "workbooks": [],
        }

        parsed_response = fromstring(xml)
        for workbook in parsed_response.findall(".//t:favorite/t:workbook", namespace):
            fav_workbook = WorkbookItem("")
            fav_workbook._set_values(*fav_workbook._parse_element(workbook, namespace))
            if fav_workbook:
                favorites["workbooks"].append(fav_workbook)
        for view in parsed_response.findall(".//t:favorite[t:view]", namespace):
            fav_views = ViewItem.from_xml_element(view, namespace)
            if fav_views:
                for fav_view in fav_views:
                    favorites["views"].append(fav_view)
        for datasource in parsed_response.findall(".//t:favorite/t:datasource", namespace):
            fav_datasource = DatasourceItem("")
            fav_datasource._set_values(*fav_datasource._parse_element(datasource, namespace))
            if fav_datasource:
                favorites["datasources"].append(fav_datasource)
        for project in parsed_response.findall(".//t:favorite/t:project", namespace):
            fav_project = ProjectItem("p")
            fav_project._set_values(*fav_project._parse_element(project))
            if fav_project:
                favorites["projects"].append(fav_project)
        for flow in parsed_response.findall(".//t:favorite/t:flow", namespace):
            fav_flow = FlowItem("flows")
            fav_flow._set_values(*fav_flow._parse_element(flow, namespace))
            if fav_flow:
                favorites["flows"].append(fav_flow)

        return favorites

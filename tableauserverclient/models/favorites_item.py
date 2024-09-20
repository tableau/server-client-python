import logging

from typing import Union
from defusedxml.ElementTree import fromstring

from tableauserverclient.models.tableau_types import TableauItem
from tableauserverclient.models.datasource_item import DatasourceItem
from tableauserverclient.models.flow_item import FlowItem
from tableauserverclient.models.project_item import ProjectItem
from tableauserverclient.models.metric_item import MetricItem
from tableauserverclient.models.view_item import ViewItem
from tableauserverclient.models.workbook_item import WorkbookItem

from tableauserverclient.helpers.logging import logger

FavoriteType = dict[
    str,
    list[TableauItem],
]


class FavoriteItem:
    @classmethod
    def from_response(cls, xml: Union[str, bytes], namespace: dict) -> FavoriteType:
        favorites: FavoriteType = {
            "datasources": [],
            "flows": [],
            "projects": [],
            "metrics": [],
            "views": [],
            "workbooks": [],
        }
        parsed_response = fromstring(xml)

        datasources_xml = parsed_response.findall(".//t:favorite/t:datasource", namespace)
        flows_xml = parsed_response.findall(".//t:favorite/t:flow", namespace)
        metrics_xml = parsed_response.findall(".//t:favorite/t:metric", namespace)
        projects_xml = parsed_response.findall(".//t:favorite/t:project", namespace)
        views_xml = parsed_response.findall(".//t:favorite/t:view", namespace)
        workbooks_xml = parsed_response.findall(".//t:favorite/t:workbook", namespace)

        logger.debug(
            "ds: {}, flows: {}, metrics: {}, projects: {}, views: {}, wbs: {}".format(
                len(datasources_xml),
                len(flows_xml),
                len(metrics_xml),
                len(projects_xml),
                len(views_xml),
                len(workbooks_xml),
            )
        )
        for datasource in datasources_xml:
            fav_datasource = DatasourceItem.from_xml(datasource, namespace)
            if fav_datasource:
                logger.debug(fav_datasource)
                favorites["datasources"].append(fav_datasource)

        for flow in flows_xml:
            fav_flow = FlowItem.from_xml(flow, namespace)
            if fav_flow:
                logger.debug(fav_flow)
                favorites["flows"].append(fav_flow)

        for metric in metrics_xml:
            fav_metric = MetricItem.from_xml(metric, namespace)
            if fav_metric:
                logger.debug(fav_metric)
                favorites["metrics"].append(fav_metric)

        for project in projects_xml:
            fav_project = ProjectItem.from_xml(project, namespace)
            if fav_project:
                logger.debug(fav_project)
                favorites["projects"].append(fav_project)

        for view in views_xml:
            fav_view = ViewItem.from_xml(view, namespace)
            if fav_view:
                logger.debug(fav_view)
                favorites["views"].append(fav_view)

        for workbook in workbooks_xml:
            fav_workbook = WorkbookItem.from_xml(workbook, namespace)
            if fav_workbook:
                logger.debug(fav_workbook)
                favorites["workbooks"].append(fav_workbook)

        logger.debug(favorites)
        return favorites

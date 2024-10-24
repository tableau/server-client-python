from tableauserverclient.server.endpoint.endpoint import Endpoint, api
from requests import Response
from tableauserverclient.helpers.logging import logger
from tableauserverclient.models import (
    DatasourceItem,
    FavoriteItem,
    FlowItem,
    MetricItem,
    ProjectItem,
    Resource,
    TableauItem,
    UserItem,
    ViewItem,
    WorkbookItem,
)
from tableauserverclient.server import RequestFactory, RequestOptions
from typing import Optional


class Favorites(Endpoint):
    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/favorites".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Gets all favorites
    @api(version="2.5")
    def get(self, user_item: UserItem, req_options: Optional[RequestOptions] = None) -> None:
        logger.info("Querying all favorites for user {0}".format(user_item.name))
        url = "{0}/{1}".format(self.baseurl, user_item.id)
        server_response = self.get_request(url, req_options)
        user_item._favorites = FavoriteItem.from_response(server_response.content, self.parent_srv.namespace)

    # ---------add to favorites

    @api(version="3.15")
    def add_favorite(self, user_item: UserItem, content_type: str, item: TableauItem) -> "Response":
        url = "{0}/{1}".format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_request(item.id, content_type, item.name)
        server_response = self.put_request(url, add_req)
        logger.info("Favorited {0} for user (ID: {1})".format(item.name, user_item.id))
        return server_response

    @api(version="2.0")
    def add_favorite_workbook(self, user_item: UserItem, workbook_item: WorkbookItem) -> None:
        url = "{0}/{1}".format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_workbook_req(workbook_item.id, workbook_item.name)
        server_response = self.put_request(url, add_req)
        logger.info("Favorited {0} for user (ID: {1})".format(workbook_item.name, user_item.id))

    @api(version="2.0")
    def add_favorite_view(self, user_item: UserItem, view_item: ViewItem) -> None:
        url = "{0}/{1}".format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_view_req(view_item.id, view_item.name)
        server_response = self.put_request(url, add_req)
        logger.info("Favorited {0} for user (ID: {1})".format(view_item.name, user_item.id))

    @api(version="2.3")
    def add_favorite_datasource(self, user_item: UserItem, datasource_item: DatasourceItem) -> None:
        url = "{0}/{1}".format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_datasource_req(datasource_item.id, datasource_item.name)
        server_response = self.put_request(url, add_req)
        logger.info("Favorited {0} for user (ID: {1})".format(datasource_item.name, user_item.id))

    @api(version="3.1")
    def add_favorite_project(self, user_item: UserItem, project_item: ProjectItem) -> None:
        url = "{0}/{1}".format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_project_req(project_item.id, project_item.name)
        server_response = self.put_request(url, add_req)
        logger.info("Favorited {0} for user (ID: {1})".format(project_item.name, user_item.id))

    @api(version="3.3")
    def add_favorite_flow(self, user_item: UserItem, flow_item: FlowItem) -> None:
        url = "{0}/{1}".format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_flow_req(flow_item.id, flow_item.name)
        server_response = self.put_request(url, add_req)
        logger.info("Favorited {0} for user (ID: {1})".format(flow_item.name, user_item.id))

    @api(version="3.3")
    def add_favorite_metric(self, user_item: UserItem, metric_item: MetricItem) -> None:
        url = "{0}/{1}".format(self.baseurl, user_item.id)
        add_req = RequestFactory.Favorite.add_request(metric_item.id, Resource.Metric, metric_item.name)
        server_response = self.put_request(url, add_req)
        logger.info("Favorited metric {0} for user (ID: {1})".format(metric_item.name, user_item.id))

    # ------- delete from favorites
    # Response:
    """
    <tsResponse>
      <favorites>
        <favorite label="favorite-label">
      </favorites>
    </tsResponse>
    """

    @api(version="3.15")
    def delete_favorite(self, user_item: UserItem, content_type: Resource, item: TableauItem) -> None:
        url = "{0}/{1}/{2}/{3}".format(self.baseurl, user_item.id, content_type, item.id)
        logger.info("Removing favorite {0}({1}) for user (ID: {2})".format(content_type, item.id, user_item.id))
        self.delete_request(url)

    @api(version="2.0")
    def delete_favorite_workbook(self, user_item: UserItem, workbook_item: WorkbookItem) -> None:
        url = "{0}/{1}/workbooks/{2}".format(self.baseurl, user_item.id, workbook_item.id)
        logger.info("Removing favorite workbook {0} for user (ID: {1})".format(workbook_item.id, user_item.id))
        self.delete_request(url)

    @api(version="2.0")
    def delete_favorite_view(self, user_item: UserItem, view_item: ViewItem) -> None:
        url = "{0}/{1}/views/{2}".format(self.baseurl, user_item.id, view_item.id)
        logger.info("Removing favorite view {0} for user (ID: {1})".format(view_item.id, user_item.id))
        self.delete_request(url)

    @api(version="2.3")
    def delete_favorite_datasource(self, user_item: UserItem, datasource_item: DatasourceItem) -> None:
        url = "{0}/{1}/datasources/{2}".format(self.baseurl, user_item.id, datasource_item.id)
        logger.info("Removing favorite {0} for user (ID: {1})".format(datasource_item.id, user_item.id))
        self.delete_request(url)

    @api(version="3.1")
    def delete_favorite_project(self, user_item: UserItem, project_item: ProjectItem) -> None:
        url = "{0}/{1}/projects/{2}".format(self.baseurl, user_item.id, project_item.id)
        logger.info("Removing favorite project {0} for user (ID: {1})".format(project_item.id, user_item.id))
        self.delete_request(url)

    @api(version="3.3")
    def delete_favorite_flow(self, user_item: UserItem, flow_item: FlowItem) -> None:
        url = "{0}/{1}/flows/{2}".format(self.baseurl, user_item.id, flow_item.id)
        logger.info("Removing favorite flow {0} for user (ID: {1})".format(flow_item.id, user_item.id))
        self.delete_request(url)

    @api(version="3.15")
    def delete_favorite_metric(self, user_item: UserItem, metric_item: MetricItem) -> None:
        url = "{0}/{1}/metrics/{2}".format(self.baseurl, user_item.id, metric_item.id)
        logger.info("Removing favorite metric {0} for user (ID: {1})".format(metric_item.id, user_item.id))
        self.delete_request(url)

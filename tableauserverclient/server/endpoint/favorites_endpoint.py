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


class Favorites(Endpoint):
    """Get, add, and remove favorites for a user.

    Favorites can be workbooks, views, datasources, flows, projects, metrics,
    or collections. Retrieved favorites are stored on the target ``UserItem``
    object as a dictionary keyed by content type (e.g. ``"workbooks"``,
    ``"views"``, ``"datasources"``, ``"flows"``, ``"projects"``, ``"metrics"``,
    ``"collections"``), where each value is a list of the corresponding item
    objects.

    REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm
    """

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/favorites"

    # Gets all favorites
    @api(version="2.5")
    def get(self, user_item: UserItem, req_options: RequestOptions | None = None) -> None:
        """Populate the favorites on the specified user.

        After calling this method, the favorites are available through
        ``user_item.favorites``, keyed by content type.

        REST API: `Get Favorites for User <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#get_favorites_for_user>`_

        Parameters
        ----------
        user_item : UserItem
            The user for whom to retrieve favorites. The user's ``id`` attribute
            must be set.

        req_options : RequestOptions, optional
            Request options such as page size and page number.

        Returns
        -------
        None
            Favorites are populated on ``user_item.favorites``.

        Examples
        --------
        >>> server.favorites.get(user_item)
        >>> for workbook in user_item.favorites["workbooks"]:
        ...     print(workbook.name)
        """
        logger.info(f"Querying all favorites for user {user_item.name}")
        url = f"{self.baseurl}/{user_item.id}"
        server_response = self.get_request(url, req_options)
        user_item._favorites = FavoriteItem.from_response(server_response.content, self.parent_srv.namespace)

    # ---------add to favorites

    @api(version="3.15")
    def add_favorite(self, user_item: UserItem, content_type: str, item: TableauItem) -> "Response":
        """Add a content item of any supported type to the user's favorites.

        Type-specific helpers (``add_favorite_workbook``, ``add_favorite_view``,
        etc.) exist for each individual content type; this method is the
        polymorphic entry point.

        REST API: `Favorites Methods <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm>`_

        Parameters
        ----------
        user_item : UserItem
            The user to add the favorite for.

        content_type : str
            The type of content as a string (e.g. ``"workbook"``, ``"view"``,
            ``"datasource"``, ``"flow"``, ``"project"``, ``"metric"``).

        item : TableauItem
            The content item to favorite. Must have ``id`` and ``name``
            attributes.

        Returns
        -------
        requests.Response
            The server response.
        """
        url = f"{self.baseurl}/{user_item.id}"
        add_req = RequestFactory.Favorite.add_request(item.id, content_type, item.name)
        server_response = self.put_request(url, add_req)
        logger.info(f"Favorited {item.name} for user (ID: {user_item.id})")
        return server_response

    @api(version="2.0")
    def add_favorite_workbook(self, user_item: UserItem, workbook_item: WorkbookItem) -> None:
        """Add a workbook to the user's favorites.

        REST API: `Add Workbook to Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#add_workbook_to_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to add the favorite for.

        workbook_item : WorkbookItem
            The workbook to add to favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}"
        add_req = RequestFactory.Favorite.add_workbook_req(workbook_item.id, workbook_item.name)
        server_response = self.put_request(url, add_req)
        logger.info(f"Favorited {workbook_item.name} for user (ID: {user_item.id})")

    @api(version="2.0")
    def add_favorite_view(self, user_item: UserItem, view_item: ViewItem) -> None:
        """Add a view to the user's favorites.

        REST API: `Add View to Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#add_view_to_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to add the favorite for.

        view_item : ViewItem
            The view to add to favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}"
        add_req = RequestFactory.Favorite.add_view_req(view_item.id, view_item.name)
        server_response = self.put_request(url, add_req)
        logger.info(f"Favorited {view_item.name} for user (ID: {user_item.id})")

    @api(version="2.3")
    def add_favorite_datasource(self, user_item: UserItem, datasource_item: DatasourceItem) -> None:
        """Add a datasource to the user's favorites.

        REST API: `Add Data Source to Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#add_data_source_to_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to add the favorite for.

        datasource_item : DatasourceItem
            The datasource to add to favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}"
        add_req = RequestFactory.Favorite.add_datasource_req(datasource_item.id, datasource_item.name)
        server_response = self.put_request(url, add_req)
        logger.info(f"Favorited {datasource_item.name} for user (ID: {user_item.id})")

    @api(version="3.1")
    def add_favorite_project(self, user_item: UserItem, project_item: ProjectItem) -> None:
        """Add a project to the user's favorites.

        REST API: `Add Project to Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#add_project_to_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to add the favorite for.

        project_item : ProjectItem
            The project to add to favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}"
        add_req = RequestFactory.Favorite.add_project_req(project_item.id, project_item.name)
        server_response = self.put_request(url, add_req)
        logger.info(f"Favorited {project_item.name} for user (ID: {user_item.id})")

    @api(version="3.3")
    def add_favorite_flow(self, user_item: UserItem, flow_item: FlowItem) -> None:
        """Add a flow to the user's favorites.

        REST API: `Add Flow to Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#add_flow_to_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to add the favorite for.

        flow_item : FlowItem
            The flow to add to favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}"
        add_req = RequestFactory.Favorite.add_flow_req(flow_item.id, flow_item.name)
        server_response = self.put_request(url, add_req)
        logger.info(f"Favorited {flow_item.name} for user (ID: {user_item.id})")

    @api(version="3.3")
    def add_favorite_metric(self, user_item: UserItem, metric_item: MetricItem) -> None:
        """Add a metric to the user's favorites.

        REST API: `Add Metric to Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#add_metric_to_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to add the favorite for.

        metric_item : MetricItem
            The metric to add to favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}"
        add_req = RequestFactory.Favorite.add_request(metric_item.id, Resource.Metric, metric_item.name)
        server_response = self.put_request(url, add_req)
        logger.info(f"Favorited metric {metric_item.name} for user (ID: {user_item.id})")

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
        """Remove a content item of any supported type from the user's favorites.

        Type-specific helpers (``delete_favorite_workbook``,
        ``delete_favorite_view``, etc.) exist for each individual content
        type; this method is the polymorphic entry point.

        REST API: `Favorites Methods <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm>`_

        Parameters
        ----------
        user_item : UserItem
            The user to remove the favorite from.

        content_type : Resource
            The ``Resource`` type of the content (e.g. ``Resource.Workbook``,
            ``Resource.View``).

        item : TableauItem
            The content item to remove from favorites. Must have an ``id``
            attribute.

        Returns
        -------
        None

        Examples
        --------
        >>> server.favorites.delete_favorite(user_item, TSC.Resource.Workbook, workbook_item)
        """
        url = f"{self.baseurl}/{user_item.id}/{content_type}/{item.id}"
        logger.info(f"Removing favorite {content_type}({item.id}) for user (ID: {user_item.id})")
        self.delete_request(url)

    @api(version="2.0")
    def delete_favorite_workbook(self, user_item: UserItem, workbook_item: WorkbookItem) -> None:
        """Remove a workbook from the user's favorites.

        REST API: `Delete Workbook from Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#delete_workbook_from_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to remove the favorite from.

        workbook_item : WorkbookItem
            The workbook to remove from favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}/workbooks/{workbook_item.id}"
        logger.info(f"Removing favorite workbook {workbook_item.id} for user (ID: {user_item.id})")
        self.delete_request(url)

    @api(version="2.0")
    def delete_favorite_view(self, user_item: UserItem, view_item: ViewItem) -> None:
        """Remove a view from the user's favorites.

        REST API: `Delete View from Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#delete_view_from_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to remove the favorite from.

        view_item : ViewItem
            The view to remove from favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}/views/{view_item.id}"
        logger.info(f"Removing favorite view {view_item.id} for user (ID: {user_item.id})")
        self.delete_request(url)

    @api(version="2.3")
    def delete_favorite_datasource(self, user_item: UserItem, datasource_item: DatasourceItem) -> None:
        """Remove a datasource from the user's favorites.

        REST API: `Delete Data Source from Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#delete_data_source_from_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to remove the favorite from.

        datasource_item : DatasourceItem
            The datasource to remove from favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}/datasources/{datasource_item.id}"
        logger.info(f"Removing favorite {datasource_item.id} for user (ID: {user_item.id})")
        self.delete_request(url)

    @api(version="3.1")
    def delete_favorite_project(self, user_item: UserItem, project_item: ProjectItem) -> None:
        """Remove a project from the user's favorites.

        REST API: `Delete Project from Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#delete_project_from_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to remove the favorite from.

        project_item : ProjectItem
            The project to remove from favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}/projects/{project_item.id}"
        logger.info(f"Removing favorite project {project_item.id} for user (ID: {user_item.id})")
        self.delete_request(url)

    @api(version="3.3")
    def delete_favorite_flow(self, user_item: UserItem, flow_item: FlowItem) -> None:
        """Remove a flow from the user's favorites.

        REST API: `Delete Flow from Favorites <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm#ref_delete_flow_from_favorites>`_

        Parameters
        ----------
        user_item : UserItem
            The user to remove the favorite from.

        flow_item : FlowItem
            The flow to remove from favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}/flows/{flow_item.id}"
        logger.info(f"Removing favorite flow {flow_item.id} for user (ID: {user_item.id})")
        self.delete_request(url)

    @api(version="3.15")
    def delete_favorite_metric(self, user_item: UserItem, metric_item: MetricItem) -> None:
        """Remove a metric from the user's favorites.

        REST API: `Favorites Methods <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_favorites.htm>`_

        Parameters
        ----------
        user_item : UserItem
            The user to remove the favorite from.

        metric_item : MetricItem
            The metric to remove from favorites.

        Returns
        -------
        None
        """
        url = f"{self.baseurl}/{user_item.id}/metrics/{metric_item.id}"
        logger.info(f"Removing favorite metric {metric_item.id} for user (ID: {user_item.id})")
        self.delete_request(url)

from typing import Literal, TypeAlias, TYPE_CHECKING, overload

from tableauserverclient.helpers.logging import logger
from tableauserverclient.models.job_item import JobItem
from tableauserverclient.models.pagination_item import PaginationItem
from tableauserverclient.models.project_item import ProjectItem
from tableauserverclient.models.recycle_bin_item import RecycleBinItem
from tableauserverclient.server.endpoint.endpoint import Endpoint, api
from tableauserverclient.server.request_options import RequestOptions

if TYPE_CHECKING:
    from tableauserverclient.server.server import Server

RecycleBinContentType: TypeAlias = Literal["workbooks", "datasources", "flows", "projects"]

_URL_SEGMENTS = {"workbook", "datasource", "flow", "project"}


class RecycleBin(Endpoint):
    """
    The recycle bin holds workbooks, data sources, flows and projects that have
    been deleted from a site, until they are restored or permanently deleted.

    Content types are given as one of "workbooks", "datasources", "flows" or
    "projects". The singular form reported by the server on a RecycleBinItem
    (for example "workbook") is accepted as well.
    """

    def __init__(self, parent_srv: "Server") -> None:
        super().__init__(parent_srv)

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/recyclebin"

    @staticmethod
    def _content_type_segment(content_type: str) -> str:
        singular = content_type[:-1] if content_type.endswith("s") else content_type
        if singular not in _URL_SEGMENTS:
            raise ValueError(
                f"Unknown recycle bin content type '{content_type}'. "
                "Expected one of: workbooks, datasources, flows, projects."
            )
        return f"{singular}s"

    def _item_url(self, content_type: str | None, item: "RecycleBinItem | str") -> str:
        if isinstance(item, RecycleBinItem):
            if not item.id:
                raise ValueError("The recycle bin item must have an id.")
            content_type = content_type or item.content_type
            item_id = item.id
        else:
            item_id = item
        if not content_type:
            raise ValueError("content_type is required when the item is given as an id.")
        return f"{self.baseurl}/{self._content_type_segment(content_type)}/{item_id}"

    @api(version="3.29")
    def get(
        self, content_type: RecycleBinContentType, req_options: RequestOptions | None = None
    ) -> tuple[list[RecycleBinItem], PaginationItem]:
        """
        List the deleted content of one type in the recycle bin. Supports
        filtering on name, ownerId, deleterId, createdAt, updatedAt and path,
        and sorting and paging through RequestOptions.

        REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_recycle_bin.htm#list_recycle_bin_content_by_type

        Parameters
        ----------
        content_type : "workbooks" | "datasources" | "flows" | "projects"
            The type of content to list.

        req_options : RequestOptions, optional
            Filter, sort and paging options.

        Returns
        -------
        tuple[list[RecycleBinItem], PaginationItem]
        """
        logger.info(f"Querying the recycle bin for {content_type}")
        url = f"{self.baseurl}/{self._content_type_segment(content_type)}"
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        items = RecycleBinItem.from_response(server_response.content, self.parent_srv.namespace)
        return items, pagination_item

    @api(version="3.29")
    def get_by_id(self, content_type: RecycleBinContentType, content_id: str) -> RecycleBinItem:
        """
        Get a single deleted item from the recycle bin.

        REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_recycle_bin.htm#get_recycle_bin_content_item

        Parameters
        ----------
        content_type : "workbooks" | "datasources" | "flows" | "projects"
            The type of the content.

        content_id : str
            The identifier of the deleted content.

        Returns
        -------
        RecycleBinItem
        """
        if not content_id:
            raise ValueError("content_id is required.")
        logger.info(f"Querying the recycle bin for {content_type} (ID: {content_id})")
        url = self._item_url(content_type, content_id)
        server_response = self.get_request(url)
        return RecycleBinItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.29")
    def restore(
        self,
        item: RecycleBinItem | str,
        project: ProjectItem | str,
        content_type: RecycleBinContentType | None = None,
    ) -> None:
        """
        Restore a deleted item from the recycle bin into a project. The caller
        needs Publish permission on the destination project.

        REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_recycle_bin.htm#restore_recycle_bin_content_item

        Parameters
        ----------
        item : RecycleBinItem | str
            The item to restore, or its id. When an id is given, content_type
            is required.

        project : ProjectItem | str
            The project, or project id, to restore the content into.

        content_type : "workbooks" | "datasources" | "flows" | "projects", optional
            The type of the content. Defaults to the type of a RecycleBinItem.
        """
        project_id = project.id if isinstance(project, ProjectItem) else project
        if not project_id:
            raise ValueError("A destination project id is required to restore content.")
        url = f"{self._item_url(content_type, item)}/restore"
        logger.info(f"Restoring recycle bin content to project (ID: {project_id}): {url}")
        self.post_request(url, "", parameters={"params": {"projectId": project_id}})

    @api(version="3.29")
    def delete(self, item: RecycleBinItem | str, content_type: RecycleBinContentType | None = None) -> None:
        """
        Permanently delete one item from the recycle bin. This cannot be undone.

        REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_recycle_bin.htm#delete_recycle_bin_content_item

        Parameters
        ----------
        item : RecycleBinItem | str
            The item to delete, or its id. When an id is given, content_type
            is required.

        content_type : "workbooks" | "datasources" | "flows" | "projects", optional
            The type of the content. Defaults to the type of a RecycleBinItem.
        """
        url = self._item_url(content_type, item)
        logger.info(f"Permanently deleting recycle bin content: {url}")
        self.delete_request(url)

    @overload
    def empty(self, as_job: Literal[False] = False) -> None: ...

    @overload
    def empty(self, as_job: Literal[True]) -> JobItem: ...

    @api(version="3.29")
    def empty(self, as_job: bool = False) -> JobItem | None:
        """
        Permanently delete everything in the recycle bin. This cannot be undone.

        REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_recycle_bin.htm#delete_all_recycle_bin_contents

        Parameters
        ----------
        as_job : bool, default False
            Run the deletion as an asynchronous EmptyRecycleBin job and return
            the JobItem, which can be passed to `server.jobs.wait_for_job`.

        Returns
        -------
        JobItem | None
            The job when as_job is True, otherwise None.
        """
        logger.info("Emptying the recycle bin")
        if not as_job:
            self.delete_request(self.baseurl)
            return None
        server_response = self._make_request(
            self.parent_srv.session.delete,
            self.baseurl,
            auth_token=self.parent_srv.auth_token,
            parameters={"params": {"asJob": "true"}},
        )
        return JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]

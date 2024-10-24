from email.message import Message
import copy
import io
import logging
import os
from contextlib import closing
from pathlib import Path

from tableauserverclient.helpers.headers import fix_filename
from tableauserverclient.server.query import QuerySet

from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api, parameter_added_in
from tableauserverclient.server.endpoint.exceptions import InternalServerError, MissingRequiredFieldError
from tableauserverclient.server.endpoint.permissions_endpoint import _PermissionsEndpoint
from tableauserverclient.server.endpoint.resource_tagger import TaggingMixin

from tableauserverclient.filesys_helpers import (
    to_filename,
    make_download_path,
    get_file_type,
    get_file_object_size,
)
from tableauserverclient.helpers import redact_xml
from tableauserverclient.models import WorkbookItem, ConnectionItem, ViewItem, PaginationItem, JobItem, RevisionItem
from tableauserverclient.server import RequestFactory

from typing import (
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    TYPE_CHECKING,
    Union,
)

if TYPE_CHECKING:
    from tableauserverclient.server import Server
    from tableauserverclient.server.request_options import RequestOptions
    from tableauserverclient.models import DatasourceItem
    from tableauserverclient.server.endpoint.schedules_endpoint import AddResponse

io_types_r = (io.BytesIO, io.BufferedReader)
io_types_w = (io.BytesIO, io.BufferedWriter)

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64  # 64MB

ALLOWED_FILE_EXTENSIONS = ["twb", "twbx"]

from tableauserverclient.helpers.logging import logger

FilePath = Union[str, os.PathLike]
FileObject = Union[io.BufferedReader, io.BytesIO]
FileObjectR = Union[io.BufferedReader, io.BytesIO]
FileObjectW = Union[io.BufferedWriter, io.BytesIO]
PathOrFileR = Union[FilePath, FileObjectR]
PathOrFileW = Union[FilePath, FileObjectW]


class Workbooks(QuerysetEndpoint[WorkbookItem], TaggingMixin[WorkbookItem]):
    def __init__(self, parent_srv: "Server") -> None:
        super(Workbooks, self).__init__(parent_srv)
        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)

        return None

    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/workbooks".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Get all workbooks on site
    @api(version="2.0")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[WorkbookItem], PaginationItem]:
        logger.info("Querying all workbooks on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_workbook_items = WorkbookItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_workbook_items, pagination_item

    # Get 1 workbook
    @api(version="2.0")
    def get_by_id(self, workbook_id: str) -> WorkbookItem:
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        logger.info("Querying single workbook (ID: {0})".format(workbook_id))
        url = "{0}/{1}".format(self.baseurl, workbook_id)
        server_response = self.get_request(url)
        return WorkbookItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="2.8")
    def refresh(self, workbook_item: Union[WorkbookItem, str]) -> JobItem:
        id_ = getattr(workbook_item, "id", workbook_item)
        url = "{0}/{1}/refresh".format(self.baseurl, id_)
        empty_req = RequestFactory.Empty.empty_req()
        server_response = self.post_request(url, empty_req)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

    # create one or more extracts on 1 workbook, optionally encrypted
    @api(version="3.5")
    def create_extract(
        self,
        workbook_item: WorkbookItem,
        encrypt: bool = False,
        includeAll: bool = True,
        datasources: Optional[List["DatasourceItem"]] = None,
    ) -> JobItem:
        id_ = getattr(workbook_item, "id", workbook_item)
        url = "{0}/{1}/createExtract?encrypt={2}".format(self.baseurl, id_, encrypt)

        datasource_req = RequestFactory.Workbook.embedded_extract_req(includeAll, datasources)
        server_response = self.post_request(url, datasource_req)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

    # delete all the extracts on 1 workbook
    @api(version="3.3")
    def delete_extract(self, workbook_item: WorkbookItem, includeAll: bool = True, datasources=None) -> JobItem:
        id_ = getattr(workbook_item, "id", workbook_item)
        url = "{0}/{1}/deleteExtract".format(self.baseurl, id_)
        datasource_req = RequestFactory.Workbook.embedded_extract_req(includeAll, datasources)
        server_response = self.post_request(url, datasource_req)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

    # Delete 1 workbook by id
    @api(version="2.0")
    def delete(self, workbook_id: str) -> None:
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, workbook_id)
        self.delete_request(url)
        logger.info("Deleted single workbook (ID: {0})".format(workbook_id))

    # Update workbook
    @api(version="2.0")
    @parameter_added_in(include_view_acceleration_status="3.22")
    def update(
        self,
        workbook_item: WorkbookItem,
        include_view_acceleration_status: bool = False,
    ) -> WorkbookItem:
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        self.update_tags(workbook_item)

        # Update the workbook itself
        url = "{0}/{1}".format(self.baseurl, workbook_item.id)
        if include_view_acceleration_status:
            url += "?includeViewAccelerationStatus=True"

        update_req = RequestFactory.Workbook.update_req(workbook_item)
        server_response = self.put_request(url, update_req)
        logger.info("Updated workbook item (ID: {0})".format(workbook_item.id))
        updated_workbook = copy.copy(workbook_item)
        return updated_workbook._parse_common_tags(server_response.content, self.parent_srv.namespace)

    # Update workbook_connection
    @api(version="2.3")
    def update_connection(self, workbook_item: WorkbookItem, connection_item: ConnectionItem) -> ConnectionItem:
        url = "{0}/{1}/connections/{2}".format(self.baseurl, workbook_item.id, connection_item.id)
        update_req = RequestFactory.Connection.update_req(connection_item)
        server_response = self.put_request(url, update_req)
        connection = ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

        logger.info(
            "Updated workbook item (ID: {0} & connection item {1})".format(workbook_item.id, connection_item.id)
        )
        return connection

    # Download workbook contents with option of passing in filepath
    @api(version="2.0")
    @parameter_added_in(no_extract="2.5")
    @parameter_added_in(include_extract="2.5")
    def download(
        self,
        workbook_id: str,
        filepath: Optional[PathOrFileW] = None,
        include_extract: bool = True,
    ) -> PathOrFileW:
        return self.download_revision(
            workbook_id,
            None,
            filepath,
            include_extract,
        )

    # Get all views of workbook
    @api(version="2.0")
    def populate_views(self, workbook_item: WorkbookItem, usage: bool = False) -> None:
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def view_fetcher() -> List[ViewItem]:
            return self._get_views_for_workbook(workbook_item, usage)

        workbook_item._set_views(view_fetcher)
        logger.info("Populated views for workbook (ID: {0})".format(workbook_item.id))

    def _get_views_for_workbook(self, workbook_item: WorkbookItem, usage: bool) -> List[ViewItem]:
        url = "{0}/{1}/views".format(self.baseurl, workbook_item.id)
        if usage:
            url += "?includeUsageStatistics=true"
        server_response = self.get_request(url)
        views = ViewItem.from_response(
            server_response.content,
            self.parent_srv.namespace,
            workbook_id=workbook_item.id,
        )
        return views

    # Get all connections of workbook
    @api(version="2.0")
    def populate_connections(self, workbook_item: WorkbookItem) -> None:
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def connection_fetcher():
            return self._get_workbook_connections(workbook_item)

        workbook_item._set_connections(connection_fetcher)
        logger.info("Populated connections for workbook (ID: {0})".format(workbook_item.id))

    def _get_workbook_connections(
        self, workbook_item: WorkbookItem, req_options: Optional["RequestOptions"] = None
    ) -> List[ConnectionItem]:
        url = "{0}/{1}/connections".format(self.baseurl, workbook_item.id)
        server_response = self.get_request(url, req_options)
        connections = ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)
        return connections

    # Get the pdf of the entire workbook if its tabs are enabled, pdf of the default view if its tabs are disabled
    @api(version="3.4")
    def populate_pdf(self, workbook_item: WorkbookItem, req_options: Optional["RequestOptions"] = None) -> None:
        if not workbook_item.id:
            error = "Workbook item missing ID."
            raise MissingRequiredFieldError(error)

        def pdf_fetcher() -> bytes:
            return self._get_wb_pdf(workbook_item, req_options)

        workbook_item._set_pdf(pdf_fetcher)
        logger.info("Populated pdf for workbook (ID: {0})".format(workbook_item.id))

    def _get_wb_pdf(self, workbook_item: WorkbookItem, req_options: Optional["RequestOptions"]) -> bytes:
        url = "{0}/{1}/pdf".format(self.baseurl, workbook_item.id)
        server_response = self.get_request(url, req_options)
        pdf = server_response.content
        return pdf

    @api(version="3.8")
    def populate_powerpoint(self, workbook_item: WorkbookItem, req_options: Optional["RequestOptions"] = None) -> None:
        if not workbook_item.id:
            error = "Workbook item missing ID."
            raise MissingRequiredFieldError(error)

        def pptx_fetcher() -> bytes:
            return self._get_wb_pptx(workbook_item, req_options)

        workbook_item._set_powerpoint(pptx_fetcher)
        logger.info("Populated powerpoint for workbook (ID: {0})".format(workbook_item.id))

    def _get_wb_pptx(self, workbook_item: WorkbookItem, req_options: Optional["RequestOptions"]) -> bytes:
        url = "{0}/{1}/powerpoint".format(self.baseurl, workbook_item.id)
        server_response = self.get_request(url, req_options)
        pptx = server_response.content
        return pptx

    # Get preview image of workbook
    @api(version="2.0")
    def populate_preview_image(self, workbook_item: WorkbookItem) -> None:
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def image_fetcher() -> bytes:
            return self._get_wb_preview_image(workbook_item)

        workbook_item._set_preview_image(image_fetcher)
        logger.info("Populated preview image for workbook (ID: {0})".format(workbook_item.id))

    def _get_wb_preview_image(self, workbook_item: WorkbookItem) -> bytes:
        url = "{0}/{1}/previewImage".format(self.baseurl, workbook_item.id)
        server_response = self.get_request(url)
        preview_image = server_response.content
        return preview_image

    @api(version="2.0")
    def populate_permissions(self, item: WorkbookItem) -> None:
        self._permissions.populate(item)

    @api(version="2.0")
    def update_permissions(self, resource, rules):
        return self._permissions.update(resource, rules)

    @api(version="2.0")
    def delete_permission(self, item, capability_item):
        return self._permissions.delete(item, capability_item)

    @api(version="2.0")
    @parameter_added_in(as_job="3.0")
    @parameter_added_in(connections="2.8")
    def publish(
        self,
        workbook_item: WorkbookItem,
        file: PathOrFileR,
        mode: str,
        connections: Optional[Sequence[ConnectionItem]] = None,
        as_job: bool = False,
        skip_connection_check: bool = False,
        parameters=None,
    ):
        if isinstance(file, (str, os.PathLike)):
            if not os.path.isfile(file):
                error = "File path does not lead to an existing file."
                raise IOError(error)

            filename = os.path.basename(file)
            file_extension = os.path.splitext(filename)[1][1:]
            file_size = os.path.getsize(file)

            # If name is not defined, grab the name from the file to publish
            if not workbook_item.name:
                workbook_item.name = os.path.splitext(filename)[0]
            if file_extension not in ALLOWED_FILE_EXTENSIONS:
                error = "Only {} files can be published as workbooks.".format(", ".join(ALLOWED_FILE_EXTENSIONS))
                raise ValueError(error)

        elif isinstance(file, io_types_r):
            if not workbook_item.name:
                error = "Workbook item must have a name when passing a file object"
                raise ValueError(error)

            file_type = get_file_type(file)
            if file_type == "zip":
                file_extension = "twbx"
            elif file_type == "xml":
                file_extension = "twb"
            else:
                error = "Unsupported file type {}!".format(file_type)
                raise ValueError(error)

            # Generate filename for file object.
            # This is needed when publishing the workbook in a single request
            filename = "{}.{}".format(workbook_item.name, file_extension)
            file_size = get_file_object_size(file)

        else:
            raise TypeError("file should be a filepath or file object.")

        if not hasattr(self.parent_srv.PublishMode, mode):
            error = "Invalid mode defined."
            raise ValueError(error)

        # Construct the url with the defined mode
        url = "{0}?workbookType={1}".format(self.baseurl, file_extension)
        if mode == self.parent_srv.PublishMode.Overwrite:
            url += "&{0}=true".format(mode.lower())
        elif mode == self.parent_srv.PublishMode.Append:
            error = "Workbooks cannot be appended."
            raise ValueError(error)

        if as_job:
            url += "&{0}=true".format("asJob")

        if skip_connection_check:
            url += "&{0}=true".format("skipConnectionCheck")

        # Determine if chunking is required (64MB is the limit for single upload method)
        if file_size >= FILESIZE_LIMIT:
            logger.info("Publishing {0} to server with chunking method (workbook over 64MB)".format(workbook_item.name))
            upload_session_id = self.parent_srv.fileuploads.upload(file)
            url = "{0}&uploadSessionId={1}".format(url, upload_session_id)
            xml_request, content_type = RequestFactory.Workbook.publish_req_chunked(
                workbook_item,
                connections=connections,
            )
        else:
            logger.info("Publishing {0} to server".format(filename))

            if isinstance(file, (str, Path)):
                with open(file, "rb") as f:
                    file_contents = f.read()

            elif isinstance(file, io_types_r):
                file_contents = file.read()

            else:
                raise TypeError("file should be a filepath or file object.")

            xml_request, content_type = RequestFactory.Workbook.publish_req(
                workbook_item,
                filename,
                file_contents,
                connections=connections,
            )
        logger.debug("Request xml: {0} ".format(redact_xml(xml_request[:1000])))

        # Send the publishing request to server
        try:
            server_response = self.post_request(url, xml_request, content_type, parameters)
        except InternalServerError as err:
            if err.code == 504 and not as_job:
                err.content = "Timeout error while publishing. Please use asynchronous publishing to avoid timeouts."
            raise err

        if as_job:
            new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
            logger.info("Published {0} (JOB_ID: {1}".format(workbook_item.name, new_job.id))
            return new_job
        else:
            new_workbook = WorkbookItem.from_response(server_response.content, self.parent_srv.namespace)[0]
            logger.info("Published {0} (ID: {1})".format(workbook_item.name, new_workbook.id))
            return new_workbook

    # Populate workbook item's revisions
    @api(version="2.3")
    def populate_revisions(self, workbook_item: WorkbookItem) -> None:
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def revisions_fetcher():
            return self._get_workbook_revisions(workbook_item)

        workbook_item._set_revisions(revisions_fetcher)
        logger.info("Populated revisions for workbook (ID: {0})".format(workbook_item.id))

    def _get_workbook_revisions(
        self, workbook_item: WorkbookItem, req_options: Optional["RequestOptions"] = None
    ) -> List[RevisionItem]:
        url = "{0}/{1}/revisions".format(self.baseurl, workbook_item.id)
        server_response = self.get_request(url, req_options)
        revisions = RevisionItem.from_response(server_response.content, self.parent_srv.namespace, workbook_item)
        return revisions

    # Download 1 workbook revision by revision number
    @api(version="2.3")
    def download_revision(
        self,
        workbook_id: str,
        revision_number: Optional[str],
        filepath: Optional[PathOrFileW] = None,
        include_extract: bool = True,
    ) -> PathOrFileW:
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        if revision_number is None:
            url = "{0}/{1}/content".format(self.baseurl, workbook_id)
        else:
            url = "{0}/{1}/revisions/{2}/content".format(self.baseurl, workbook_id, revision_number)

        if not include_extract:
            url += "?includeExtract=False"

        with closing(self.get_request(url, parameters={"stream": True})) as server_response:
            m = Message()
            m["Content-Disposition"] = server_response.headers["Content-Disposition"]
            params = m.get_filename(failobj="")
            if isinstance(filepath, io_types_w):
                for chunk in server_response.iter_content(1024):  # 1KB
                    filepath.write(chunk)
                return_path = filepath
            else:
                params = fix_filename(params)
                filename = to_filename(os.path.basename(params))
                download_path = make_download_path(filepath, filename)
                with open(download_path, "wb") as f:
                    for chunk in server_response.iter_content(1024):  # 1KB
                        f.write(chunk)
                return_path = os.path.abspath(download_path)

        logger.info(
            "Downloaded workbook revision {0} to {1} (ID: {2})".format(revision_number, return_path, workbook_id)
        )
        return return_path

    @api(version="2.3")
    def delete_revision(self, workbook_id: str, revision_number: str) -> None:
        if workbook_id is None or revision_number is None:
            raise ValueError
        url = "/".join([self.baseurl, workbook_id, "revisions", revision_number])

        self.delete_request(url)
        logger.info("Deleted single workbook revision (ID: {0}) (Revision: {1})".format(workbook_id, revision_number))

    # a convenience method
    @api(version="2.8")
    def schedule_extract_refresh(
        self, schedule_id: str, item: WorkbookItem
    ) -> List["AddResponse"]:  # actually should return a task
        return self.parent_srv.schedules.add_to_schedule(schedule_id, workbook=item)

    @api(version="1.0")
    def add_tags(self, item: Union[WorkbookItem, str], tags: Union[Iterable[str], str]) -> Set[str]:
        return super().add_tags(item, tags)

    @api(version="1.0")
    def delete_tags(self, item: Union[WorkbookItem, str], tags: Union[Iterable[str], str]) -> None:
        return super().delete_tags(item, tags)

    @api(version="1.0")
    def update_tags(self, item: WorkbookItem) -> None:
        return super().update_tags(item)

    def filter(self, *invalid, page_size: Optional[int] = None, **kwargs) -> QuerySet[WorkbookItem]:
        """
        Queries the Tableau Server for items using the specified filters. Page
        size can be specified to limit the number of items returned in a single
        request. If not specified, the default page size is 100. Page size can
        be an integer between 1 and 1000.

        No positional arguments are allowed. All filters must be specified as
        keyword arguments. If you use the equality operator, you can specify it
        through <field_name>=<value>. If you want to use a different operator,
        you can specify it through <field_name>__<operator>=<value>. Field
        names can either be in snake_case or camelCase.

        This endpoint supports the following fields and operators:


        created_at=...
        created_at__gt=...
        created_at__gte=...
        created_at__lt=...
        created_at__lte=...
        content_url=...
        content_url__in=...
        display_tabs=...
        favorites_total=...
        favorites_total__gt=...
        favorites_total__gte=...
        favorites_total__lt=...
        favorites_total__lte=...
        has_alerts=...
        has_extracts=...
        name=...
        name__in=...
        owner_domain=...
        owner_domain__in=...
        owner_email=...
        owner_email__in=...
        owner_name=...
        owner_name__in=...
        project_name=...
        project_name__in=...
        sheet_count=...
        sheet_count__gt=...
        sheet_count__gte=...
        sheet_count__lt=...
        sheet_count__lte=...
        size=...
        size__gt=...
        size__gte=...
        size__lt=...
        size__lte=...
        subscriptions_total=...
        subscriptions_total__gt=...
        subscriptions_total__gte=...
        subscriptions_total__lt=...
        subscriptions_total__lte=...
        tags=...
        tags__in=...
        updated_at=...
        updated_at__gt=...
        updated_at__gte=...
        updated_at__lt=...
        updated_at__lte=...
        """

        return super().filter(*invalid, page_size=page_size, **kwargs)

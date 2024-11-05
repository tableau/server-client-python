from email.message import Message
import copy
import io
import logging
import os
from contextlib import closing
from pathlib import Path
from typing import Optional, TYPE_CHECKING, Union
from collections.abc import Iterable

from tableauserverclient.helpers.headers import fix_filename

from tableauserverclient.server.endpoint.dqw_endpoint import _DataQualityWarningEndpoint
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api
from tableauserverclient.server.endpoint.exceptions import InternalServerError, MissingRequiredFieldError
from tableauserverclient.server.endpoint.permissions_endpoint import _PermissionsEndpoint
from tableauserverclient.server.endpoint.resource_tagger import _ResourceTagger, TaggingMixin
from tableauserverclient.models import FlowItem, PaginationItem, ConnectionItem, JobItem
from tableauserverclient.server import RequestFactory
from tableauserverclient.filesys_helpers import (
    to_filename,
    make_download_path,
    get_file_type,
    get_file_object_size,
)
from tableauserverclient.server.query import QuerySet

io_types_r = (io.BytesIO, io.BufferedReader)
io_types_w = (io.BytesIO, io.BufferedWriter)

io_types_r = (io.BytesIO, io.BufferedReader)
io_types_w = (io.BytesIO, io.BufferedWriter)

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64  # 64MB

ALLOWED_FILE_EXTENSIONS = ["tfl", "tflx"]

from tableauserverclient.helpers.logging import logger

if TYPE_CHECKING:
    from tableauserverclient.models import DQWItem
    from tableauserverclient.models.permissions_item import PermissionsRule
    from tableauserverclient.server.request_options import RequestOptions
    from tableauserverclient.server.endpoint.schedules_endpoint import AddResponse


FilePath = Union[str, os.PathLike]
FileObjectR = Union[io.BufferedReader, io.BytesIO]
FileObjectW = Union[io.BufferedWriter, io.BytesIO]
PathOrFileR = Union[FilePath, FileObjectR]
PathOrFileW = Union[FilePath, FileObjectW]


class Flows(QuerysetEndpoint[FlowItem], TaggingMixin[FlowItem]):
    def __init__(self, parent_srv):
        super().__init__(parent_srv)
        self._resource_tagger = _ResourceTagger(parent_srv)
        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._data_quality_warnings = _DataQualityWarningEndpoint(self.parent_srv, "flow")

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/flows"

    # Get all flows
    @api(version="3.3")
    def get(self, req_options: Optional["RequestOptions"] = None) -> tuple[list[FlowItem], PaginationItem]:
        logger.info("Querying all flows on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_flow_items = FlowItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_flow_items, pagination_item

    # Get 1 flow by id
    @api(version="3.3")
    def get_by_id(self, flow_id: str) -> FlowItem:
        if not flow_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        logger.info(f"Querying single flow (ID: {flow_id})")
        url = f"{self.baseurl}/{flow_id}"
        server_response = self.get_request(url)
        return FlowItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Populate flow item's connections
    @api(version="3.3")
    def populate_connections(self, flow_item: FlowItem) -> None:
        if not flow_item.id:
            error = "Flow item missing ID. Flow must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def connections_fetcher():
            return self._get_flow_connections(flow_item)

        flow_item._set_connections(connections_fetcher)
        logger.info(f"Populated connections for flow (ID: {flow_item.id})")

    def _get_flow_connections(self, flow_item, req_options: Optional["RequestOptions"] = None) -> list[ConnectionItem]:
        url = f"{self.baseurl}/{flow_item.id}/connections"
        server_response = self.get_request(url, req_options)
        connections = ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)
        return connections

    # Delete 1 flow by id
    @api(version="3.3")
    def delete(self, flow_id: str) -> None:
        if not flow_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{flow_id}"
        self.delete_request(url)
        logger.info(f"Deleted single flow (ID: {flow_id})")

    # Download 1 flow by id
    @api(version="3.3")
    def download(self, flow_id: str, filepath: Optional[PathOrFileW] = None) -> PathOrFileW:
        if not flow_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{flow_id}/content"

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

        logger.info(f"Downloaded flow to {return_path} (ID: {flow_id})")
        return return_path

    # Update flow
    @api(version="3.3")
    def update(self, flow_item: FlowItem) -> FlowItem:
        if not flow_item.id:
            error = "Flow item missing ID. Flow must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        self._resource_tagger.update_tags(self.baseurl, flow_item)

        # Update the flow itself
        url = f"{self.baseurl}/{flow_item.id}"
        update_req = RequestFactory.Flow.update_req(flow_item)
        server_response = self.put_request(url, update_req)
        logger.info(f"Updated flow item (ID: {flow_item.id})")
        updated_flow = copy.copy(flow_item)
        return updated_flow._parse_common_elements(server_response.content, self.parent_srv.namespace)

    # Update flow connections
    @api(version="3.3")
    def update_connection(self, flow_item: FlowItem, connection_item: ConnectionItem) -> ConnectionItem:
        url = f"{self.baseurl}/{flow_item.id}/connections/{connection_item.id}"

        update_req = RequestFactory.Connection.update_req(connection_item)
        server_response = self.put_request(url, update_req)
        connection = ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

        logger.info(f"Updated flow item (ID: {flow_item.id} & connection item {connection_item.id}")
        return connection

    @api(version="3.3")
    def refresh(self, flow_item: FlowItem) -> JobItem:
        url = f"{self.baseurl}/{flow_item.id}/run"
        empty_req = RequestFactory.Empty.empty_req()
        server_response = self.post_request(url, empty_req)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

    # Publish flow
    @api(version="3.3")
    def publish(
        self, flow_item: FlowItem, file: PathOrFileR, mode: str, connections: Optional[list[ConnectionItem]] = None
    ) -> FlowItem:
        if not mode or not hasattr(self.parent_srv.PublishMode, mode):
            error = "Invalid mode defined."
            raise ValueError(error)

        if isinstance(file, (str, os.PathLike)):
            if not os.path.isfile(file):
                error = "File path does not lead to an existing file."
                raise OSError(error)

            filename = os.path.basename(file)
            file_extension = os.path.splitext(filename)[1][1:]
            file_size = os.path.getsize(file)

            # If name is not defined, grab the name from the file to publish
            if not flow_item.name:
                flow_item.name = os.path.splitext(filename)[0]
            if file_extension not in ALLOWED_FILE_EXTENSIONS:
                error = "Only {} files can be published as flows.".format(", ".join(ALLOWED_FILE_EXTENSIONS))
                raise ValueError(error)

        elif isinstance(file, io_types_r):
            if not flow_item.name:
                error = "Flow item must have a name when passing a file object"
                raise ValueError(error)

            file_type = get_file_type(file)
            if file_type == "zip":
                file_extension = "tflx"
            elif file_type == "xml":
                file_extension = "tfl"
            else:
                error = f"Unsupported file type {file_type}!"
                raise ValueError(error)

            # Generate filename for file object.
            # This is needed when publishing the flow in a single request
            filename = f"{flow_item.name}.{file_extension}"
            file_size = get_file_object_size(file)

        else:
            raise TypeError("file should be a filepath or file object.")

        # Construct the url with the defined mode
        url = f"{self.baseurl}?flowType={file_extension}"
        if mode == self.parent_srv.PublishMode.Overwrite or mode == self.parent_srv.PublishMode.Append:
            url += f"&{mode.lower()}=true"

        # Determine if chunking is required (64MB is the limit for single upload method)
        if file_size >= FILESIZE_LIMIT:
            logger.info(f"Publishing {filename} to server with chunking method (flow over 64MB)")
            upload_session_id = self.parent_srv.fileuploads.upload(file)
            url = f"{url}&uploadSessionId={upload_session_id}"
            xml_request, content_type = RequestFactory.Flow.publish_req_chunked(flow_item, connections)
        else:
            logger.info(f"Publishing {filename} to server")

            if isinstance(file, (str, Path)):
                with open(file, "rb") as f:
                    file_contents = f.read()

            elif isinstance(file, io_types_r):
                file_contents = file.read()

            else:
                raise TypeError("file should be a filepath or file object.")

            xml_request, content_type = RequestFactory.Flow.publish_req(flow_item, filename, file_contents, connections)

        # Send the publishing request to server
        try:
            server_response = self.post_request(url, xml_request, content_type)
        except InternalServerError as err:
            if err.code == 504:
                err.content = "Timeout error while publishing. Please use asynchronous publishing to avoid timeouts."
            raise err
        else:
            new_flow = FlowItem.from_response(server_response.content, self.parent_srv.namespace)[0]
            logger.info(f"Published {filename} (ID: {new_flow.id})")
            return new_flow

    @api(version="3.3")
    def populate_permissions(self, item: FlowItem) -> None:
        self._permissions.populate(item)

    @api(version="3.3")
    def update_permissions(self, item: FlowItem, permission_item: Iterable["PermissionsRule"]) -> None:
        self._permissions.update(item, permission_item)

    @api(version="3.3")
    def delete_permission(self, item: FlowItem, capability_item: "PermissionsRule") -> None:
        self._permissions.delete(item, capability_item)

    @api(version="3.5")
    def populate_dqw(self, item: FlowItem) -> None:
        self._data_quality_warnings.populate(item)

    @api(version="3.5")
    def update_dqw(self, item: FlowItem, warning: "DQWItem") -> None:
        return self._data_quality_warnings.update(item, warning)

    @api(version="3.5")
    def add_dqw(self, item: FlowItem, warning: "DQWItem") -> None:
        return self._data_quality_warnings.add(item, warning)

    @api(version="3.5")
    def delete_dqw(self, item: FlowItem) -> None:
        self._data_quality_warnings.clear(item)

    # a convenience method
    @api(version="3.3")
    def schedule_flow_run(
        self, schedule_id: str, item: FlowItem
    ) -> list["AddResponse"]:  # actually should return a task
        return self.parent_srv.schedules.add_to_schedule(schedule_id, flow=item)

    def filter(self, *invalid, page_size: Optional[int] = None, **kwargs) -> QuerySet[FlowItem]:
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
        name=...
        name__in=...
        owner_name=...
        project_id=...
        project_name=...
        project_name__in=...
        updated=...
        updated__gt=...
        updated__gte=...
        updated__lt=...
        updated__lte=...
        """

        return super().filter(*invalid, page_size=page_size, **kwargs)

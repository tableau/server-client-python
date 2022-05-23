import cgi
import copy
import io
import json
import logging
import os
from contextlib import closing
from pathlib import Path
from typing import (
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TYPE_CHECKING,
    Union,
)

from .dqw_endpoint import _DataQualityWarningEndpoint
from .endpoint import QuerysetEndpoint, api, parameter_added_in
from .exceptions import InternalServerError, MissingRequiredFieldError
from .permissions_endpoint import _PermissionsEndpoint
from .resource_tagger import _ResourceTagger
from .. import RequestFactory, DatasourceItem, PaginationItem, ConnectionItem, RequestOptions
from ..query import QuerySet
from ...filesys_helpers import (
    to_filename,
    make_download_path,
    get_file_type,
    get_file_object_size,
)
from ...models import ConnectionCredentials, RevisionItem
from ...models.job_item import JobItem
from ...models import ConnectionCredentials

io_types = (io.BytesIO, io.BufferedReader)

from pathlib import Path
from typing import (
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TYPE_CHECKING,
    Union,
)

io_types = (io.BytesIO, io.BufferedReader)

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64  # 64MB

ALLOWED_FILE_EXTENSIONS = ["tds", "tdsx", "tde", "hyper", "parquet"]

logger = logging.getLogger("tableau.endpoint.datasources")

if TYPE_CHECKING:
    from ..server import Server
    from ...models import PermissionsRule
    from .schedules_endpoint import AddResponse

FilePath = Union[str, os.PathLike]
FileObject = Union[io.BufferedReader, io.BytesIO]
PathOrFile = Union[FilePath, FileObject]


class Datasources(QuerysetEndpoint):
    def __init__(self, parent_srv: "Server") -> None:
        super(Datasources, self).__init__(parent_srv)
        self._resource_tagger = _ResourceTagger(parent_srv)
        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._data_quality_warnings = _DataQualityWarningEndpoint(self.parent_srv, "datasource")

        return None

    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/datasources".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Get all datasources
    @api(version="2.0")
    def get(self, req_options: RequestOptions = None) -> Tuple[List[DatasourceItem], PaginationItem]:
        logger.info("Querying all datasources on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_datasource_items = DatasourceItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_datasource_items, pagination_item

    # Get 1 datasource by id
    @api(version="2.0")
    def get_by_id(self, datasource_id: str) -> DatasourceItem:
        if not datasource_id:
            error = "Datasource ID undefined."
            raise ValueError(error)
        logger.info("Querying single datasource (ID: {0})".format(datasource_id))
        url = "{0}/{1}".format(self.baseurl, datasource_id)
        server_response = self.get_request(url)
        return DatasourceItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Populate datasource item's connections
    @api(version="2.0")
    def populate_connections(self, datasource_item: DatasourceItem) -> None:
        if not datasource_item.id:
            error = "Datasource item missing ID. Datasource must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def connections_fetcher():
            return self._get_datasource_connections(datasource_item)

        datasource_item._set_connections(connections_fetcher)
        logger.info("Populated connections for datasource (ID: {0})".format(datasource_item.id))

    def _get_datasource_connections(self, datasource_item, req_options=None):
        url = "{0}/{1}/connections".format(self.baseurl, datasource_item.id)
        server_response = self.get_request(url, req_options)
        connections = ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)
        return connections

    # Delete 1 datasource by id
    @api(version="2.0")
    def delete(self, datasource_id: str) -> None:
        if not datasource_id:
            error = "Datasource ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, datasource_id)
        self.delete_request(url)
        logger.info("Deleted single datasource (ID: {0})".format(datasource_id))

    # Download 1 datasource by id
    @api(version="2.0")
    @parameter_added_in(no_extract="2.5")
    @parameter_added_in(include_extract="2.5")
    def download(
        self,
        datasource_id: str,
        filepath: FilePath = None,
        include_extract: bool = True,
        no_extract: Optional[bool] = None,
    ) -> str:
        if not datasource_id:
            error = "Datasource ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/content".format(self.baseurl, datasource_id)

        if no_extract is False or no_extract is True:
            import warnings

            warnings.warn(
                "no_extract is deprecated, use include_extract instead.",
                DeprecationWarning,
            )
            include_extract = not no_extract

        if not include_extract:
            url += "?includeExtract=False"

        with closing(self.get_request(url, parameters={"stream": True})) as server_response:
            _, params = cgi.parse_header(server_response.headers["Content-Disposition"])
            filename = to_filename(os.path.basename(params["filename"]))

            download_path = make_download_path(filepath, filename)

            with open(download_path, "wb") as f:
                for chunk in server_response.iter_content(1024):  # 1KB
                    f.write(chunk)

        logger.info("Downloaded datasource to {0} (ID: {1})".format(download_path, datasource_id))
        return os.path.abspath(download_path)

    # Update datasource
    @api(version="2.0")
    def update(self, datasource_item: DatasourceItem) -> DatasourceItem:
        if not datasource_item.id:
            error = "Datasource item missing ID. Datasource must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        self._resource_tagger.update_tags(self.baseurl, datasource_item)

        # Update the datasource itself
        url = "{0}/{1}".format(self.baseurl, datasource_item.id)
        update_req = RequestFactory.Datasource.update_req(datasource_item)
        server_response = self.put_request(url, update_req)
        logger.info("Updated datasource item (ID: {0})".format(datasource_item.id))
        updated_datasource = copy.copy(datasource_item)
        return updated_datasource._parse_common_elements(server_response.content, self.parent_srv.namespace)

    # Update datasource connections
    @api(version="2.3")
    def update_connection(self, datasource_item: DatasourceItem, connection_item: ConnectionItem) -> ConnectionItem:
        url = "{0}/{1}/connections/{2}".format(self.baseurl, datasource_item.id, connection_item.id)

        update_req = RequestFactory.Connection.update_req(connection_item)
        server_response = self.put_request(url, update_req)
        connection = ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

        logger.info(
            "Updated datasource item (ID: {0} & connection item {1}".format(datasource_item.id, connection_item.id)
        )
        return connection

    @api(version="2.8")
    def refresh(self, datasource_item: DatasourceItem) -> JobItem:
        id_ = getattr(datasource_item, "id", datasource_item)
        url = "{0}/{1}/refresh".format(self.baseurl, id_)
        empty_req = RequestFactory.Empty.empty_req()
        server_response = self.post_request(url, empty_req)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

    @api(version="3.5")
    def create_extract(self, datasource_item: DatasourceItem, encrypt: bool = False) -> JobItem:
        id_ = getattr(datasource_item, "id", datasource_item)
        url = "{0}/{1}/createExtract?encrypt={2}".format(self.baseurl, id_, encrypt)
        empty_req = RequestFactory.Empty.empty_req()
        server_response = self.post_request(url, empty_req)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

    @api(version="3.5")
    def delete_extract(self, datasource_item: DatasourceItem) -> None:
        id_ = getattr(datasource_item, "id", datasource_item)
        url = "{0}/{1}/deleteExtract".format(self.baseurl, id_)
        empty_req = RequestFactory.Empty.empty_req()
        self.post_request(url, empty_req)

    # Publish datasource
    @api(version="2.0")
    @parameter_added_in(connections="2.8")
    @parameter_added_in(as_job="3.0")
    def publish(
        self,
        datasource_item: DatasourceItem,
        file: PathOrFile,
        mode: str,
        connection_credentials: ConnectionCredentials = None,
        connections: Sequence[ConnectionItem] = None,
        as_job: bool = False,
    ) -> Union[DatasourceItem, JobItem]:

        if isinstance(file, (os.PathLike, str)):
            if not os.path.isfile(file):
                error = "File path does not lead to an existing file."
                raise IOError(error)

            filename = os.path.basename(file)
            file_extension = os.path.splitext(filename)[1][1:]
            file_size = os.path.getsize(file)

            # If name is not defined, grab the name from the file to publish
            if not datasource_item.name:
                datasource_item.name = os.path.splitext(filename)[0]
            if file_extension not in ALLOWED_FILE_EXTENSIONS:
                error = "Only {} files can be published as datasources.".format(", ".join(ALLOWED_FILE_EXTENSIONS))
                raise ValueError(error)

        elif isinstance(file, io_types):

            if not datasource_item.name:
                error = "Datasource item must have a name when passing a file object"
                raise ValueError(error)

            file_type = get_file_type(file)
            if file_type == "zip":
                file_extension = "tdsx"
            elif file_type == "xml":
                file_extension = "tds"
            else:
                error = "Unsupported file type {}".format(file_type)
                raise ValueError(error)

            filename = "{}.{}".format(datasource_item.name, file_extension)
            file_size = get_file_object_size(file)

        else:
            raise TypeError("file should be a filepath or file object.")

        if not mode or not hasattr(self.parent_srv.PublishMode, mode):
            error = "Invalid mode defined."
            raise ValueError(error)

        # Construct the url with the defined mode
        url = "{0}?datasourceType={1}".format(self.baseurl, file_extension)
        if mode == self.parent_srv.PublishMode.Overwrite or mode == self.parent_srv.PublishMode.Append:
            url += "&{0}=true".format(mode.lower())

        if as_job:
            url += "&{0}=true".format("asJob")

        # Determine if chunking is required (64MB is the limit for single upload method)
        if file_size >= FILESIZE_LIMIT:
            logger.info("Publishing {0} to server with chunking method (datasource over 64MB)".format(filename))
            upload_session_id = self.parent_srv.fileuploads.upload(file)
            url = "{0}&uploadSessionId={1}".format(url, upload_session_id)
            xml_request, content_type = RequestFactory.Datasource.publish_req_chunked(
                datasource_item, connection_credentials, connections
            )
        else:
            logger.info("Publishing {0} to server".format(filename))

            if isinstance(file, (Path, str)):
                with open(file, "rb") as f:
                    file_contents = f.read()
            elif isinstance(file, io_types):
                file_contents = file.read()
            else:
                raise TypeError("file should be a filepath or file object.")

            xml_request, content_type = RequestFactory.Datasource.publish_req(
                datasource_item,
                filename,
                file_contents,
                connection_credentials,
                connections,
            )

        # Send the publishing request to server
        try:
            server_response = self.post_request(url, xml_request, content_type)
        except InternalServerError as err:
            if err.code == 504 and not as_job:
                err.content = "Timeout error while publishing. Please use asynchronous publishing to avoid timeouts."
            raise err

        if as_job:
            new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
            logger.info("Published {0} (JOB_ID: {1}".format(filename, new_job.id))
            return new_job
        else:
            new_datasource = DatasourceItem.from_response(server_response.content, self.parent_srv.namespace)[0]
            logger.info("Published {0} (ID: {1})".format(filename, new_datasource.id))
            return new_datasource

    @api(version="3.13")
    def update_hyper_data(
        self,
        datasource_or_connection_item: Union[DatasourceItem, ConnectionItem, str],
        *,
        request_id: str,
        actions: Sequence[Mapping],
        payload: Optional[FilePath] = None,
    ) -> JobItem:
        if isinstance(datasource_or_connection_item, DatasourceItem):
            datasource_id = datasource_or_connection_item.id
            url = "{0}/{1}/data".format(self.baseurl, datasource_id)
        elif isinstance(datasource_or_connection_item, ConnectionItem):
            datasource_id = datasource_or_connection_item.datasource_id
            connection_id = datasource_or_connection_item.id
            url = "{0}/{1}/connections/{2}/data".format(self.baseurl, datasource_id, connection_id)
        else:
            assert isinstance(datasource_or_connection_item, str)
            url = "{0}/{1}/data".format(self.baseurl, datasource_or_connection_item)

        if payload is not None:
            if not os.path.isfile(payload):
                error = "File path does not lead to an existing file."
                raise IOError(error)

            logger.info("Uploading {0} to server with chunking method for Update job".format(payload))
            upload_session_id = self.parent_srv.fileuploads.upload(payload)
            url = "{0}?uploadSessionId={1}".format(url, upload_session_id)

        json_request = json.dumps({"actions": actions})
        parameters = {"headers": {"requestid": request_id}}
        server_response = self.patch_request(url, json_request, "application/json", parameters=parameters)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

    @api(version="2.0")
    def populate_permissions(self, item: DatasourceItem) -> None:
        self._permissions.populate(item)

    @api(version="2.0")
    def update_permission(self, item, permission_item):
        import warnings

        warnings.warn(
            "Server.datasources.update_permission is deprecated, "
            "please use Server.datasources.update_permissions instead.",
            DeprecationWarning,
        )
        self._permissions.update(item, permission_item)

    @api(version="2.0")
    def update_permissions(self, item: DatasourceItem, permission_item: List["PermissionsRule"]) -> None:
        self._permissions.update(item, permission_item)

    @api(version="2.0")
    def delete_permission(self, item: DatasourceItem, capability_item: "PermissionsRule") -> None:
        self._permissions.delete(item, capability_item)

    @api(version="3.5")
    def populate_dqw(self, item):
        self._data_quality_warnings.populate(item)

    @api(version="3.5")
    def update_dqw(self, item, warning):
        return self._data_quality_warnings.update(item, warning)

    @api(version="3.5")
    def add_dqw(self, item, warning):
        return self._data_quality_warnings.add(item, warning)

    @api(version="3.5")
    def delete_dqw(self, item):
        self._data_quality_warnings.clear(item)

    # Populate datasource item's revisions
    @api(version="2.3")
    def populate_revisions(self, datasource_item: DatasourceItem) -> None:
        if not datasource_item.id:
            error = "Datasource item missing ID. Datasource must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def revisions_fetcher():
            return self._get_datasource_revisions(datasource_item)

        datasource_item._set_revisions(revisions_fetcher)
        logger.info("Populated revisions for datasource (ID: {0})".format(datasource_item.id))

    def _get_datasource_revisions(
        self, datasource_item: DatasourceItem, req_options: Optional["RequestOptions"] = None
    ) -> List[RevisionItem]:
        url = "{0}/{1}/revisions".format(self.baseurl, datasource_item.id)
        server_response = self.get_request(url, req_options)
        revisions = RevisionItem.from_response(server_response.content, self.parent_srv.namespace, datasource_item)
        return revisions

    # Download 1 datasource revision by revision number
    @api(version="2.3")
    def download_revision(
        self,
        datasource_id: str,
        revision_number: str,
        filepath: Optional[PathOrFile] = None,
        include_extract: bool = True,
        no_extract: Optional[bool] = None,
    ) -> str:
        if not datasource_id:
            error = "Datasource ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/revisions/{2}/content".format(self.baseurl, datasource_id, revision_number)
        if no_extract is False or no_extract is True:
            import warnings

            warnings.warn(
                "no_extract is deprecated, use include_extract instead.",
                DeprecationWarning,
            )
            include_extract = not no_extract

        if not include_extract:
            url += "?includeExtract=False"

        with closing(self.get_request(url, parameters={"stream": True})) as server_response:
            _, params = cgi.parse_header(server_response.headers["Content-Disposition"])
            filename = to_filename(os.path.basename(params["filename"]))

            download_path = make_download_path(filepath, filename)

            with open(download_path, "wb") as f:
                for chunk in server_response.iter_content(1024):  # 1KB
                    f.write(chunk)

        logger.info(
            "Downloaded datasource revision {0} to {1} (ID: {2})".format(revision_number, download_path, datasource_id)
        )
        return os.path.abspath(download_path)

    @api(version="2.3")
    def delete_revision(self, datasource_id: str, revision_number: str) -> None:
        if datasource_id is None or revision_number is None:
            raise ValueError
        url = "/".join([self.baseurl, datasource_id, "revisions", revision_number])

        self.delete_request(url)
        logger.info(
            "Deleted single datasource revision (ID: {0}) (Revision: {1})".format(datasource_id, revision_number)
        )

    # a convenience method
    @api(version="2.8")
    def schedule_extract_refresh(
        self, schedule_id: str, item: DatasourceItem
    ) -> List["AddResponse"]:  # actually should return a task
        return self.parent_srv.schedules.add_to_schedule(schedule_id, datasource=item)

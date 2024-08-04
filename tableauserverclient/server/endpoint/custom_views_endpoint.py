import io
import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple, Union

from tableauserverclient.config import BYTES_PER_MB, FILESIZE_LIMIT_MB
from tableauserverclient.filesys_helpers import get_file_object_size
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api
from tableauserverclient.server.endpoint.exceptions import MissingRequiredFieldError
from tableauserverclient.models import CustomViewItem, PaginationItem
from tableauserverclient.server import RequestFactory, RequestOptions, ImageRequestOptions

from tableauserverclient.helpers.logging import logger

"""
Get a list of custom views on a site
get the details of a custom view
download an image of a custom view.
Delete a custom view 
update the name or owner of a custom view.
"""

FilePath = Union[str, os.PathLike]
FileObject = Union[io.BufferedReader, io.BytesIO]
FileObjectR = Union[io.BufferedReader, io.BytesIO]
FileObjectW = Union[io.BufferedWriter, io.BytesIO]
PathOrFileR = Union[FilePath, FileObjectR]
PathOrFileW = Union[FilePath, FileObjectW]
io_types_r = (io.BufferedReader, io.BytesIO)
io_types_w = (io.BufferedWriter, io.BytesIO)


class CustomViews(QuerysetEndpoint[CustomViewItem]):
    def __init__(self, parent_srv):
        super(CustomViews, self).__init__(parent_srv)

    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/customviews".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @property
    def expurl(self) -> str:
        return f"{self.parent_srv._server_address}/api/exp/sites/{self.parent_srv.site_id}/customviews"

    """
    If the request has no filter parameters: Administrators will see all custom views. 
        Other users will see only custom views that they own.
    If the filter parameters include ownerId: Users will see only custom views that they own.
    If the filter parameters include viewId and/or workbookId, and don't include ownerId:
        Users will see those custom views that they have Write and WebAuthoring permissions for.
    If site user visibility is not set to Limited, the Users will see those custom views that are "public",
     meaning the value of their shared attribute is true.
    If site user visibility is set to Limited, ????
    """

    @api(version="3.18")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[CustomViewItem], PaginationItem]:
        logger.info("Querying all custom views on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_view_items = CustomViewItem.list_from_response(server_response.content, self.parent_srv.namespace)
        return all_view_items, pagination_item

    @api(version="3.18")
    def get_by_id(self, view_id: str) -> Optional[CustomViewItem]:
        if not view_id:
            error = "Custom view item missing ID."
            raise MissingRequiredFieldError(error)
        logger.info("Querying custom view (ID: {0})".format(view_id))
        url = "{0}/{1}".format(self.baseurl, view_id)
        server_response = self.get_request(url)
        return CustomViewItem.from_response(server_response.content, self.parent_srv.namespace)

    @api(version="3.18")
    def populate_image(self, view_item: CustomViewItem, req_options: Optional["ImageRequestOptions"] = None) -> None:
        if not view_item.id:
            error = "Custom View item missing ID."
            raise MissingRequiredFieldError(error)

        def image_fetcher():
            return self._get_view_image(view_item, req_options)

        view_item._set_image(image_fetcher)
        logger.info("Populated image for custom view (ID: {0})".format(view_item.id))

    def _get_view_image(self, view_item: CustomViewItem, req_options: Optional["ImageRequestOptions"]) -> bytes:
        url = "{0}/{1}/image".format(self.baseurl, view_item.id)
        server_response = self.get_request(url, req_options)
        image = server_response.content
        return image

    """
    Not yet implemented: pdf or csv exports
    """

    @api(version="3.18")
    def update(self, view_item: CustomViewItem) -> Optional[CustomViewItem]:
        if not view_item.id:
            error = "Custom view item missing ID."
            raise MissingRequiredFieldError(error)
        if not (view_item.owner or view_item.name or view_item.shared):
            logger.debug("No changes to make")
            return view_item

        # Update the custom view owner or name
        url = "{0}/{1}".format(self.baseurl, view_item.id)
        update_req = RequestFactory.CustomView.update_req(view_item)
        server_response = self.put_request(url, update_req)
        logger.info("Updated custom view (ID: {0})".format(view_item.id))
        return CustomViewItem.from_response(server_response.content, self.parent_srv.namespace)

    # Delete 1 view by id
    @api(version="3.19")
    def delete(self, view_id: str) -> None:
        if not view_id:
            error = "Custom View ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, view_id)
        self.delete_request(url)
        logger.info("Deleted single custom view (ID: {0})".format(view_id))

    @api(version="3.21")
    def download(self, view_item: CustomViewItem, file: PathOrFileW) -> PathOrFileW:
        url = f"{self.expurl}/{view_item.id}/content"
        server_response = self.get_request(url)
        if isinstance(file, io_types_w):
            file.write(server_response.content)
            return file

        with open(file, "wb") as f:
            f.write(server_response.content)

        return file

    @api(version="3.21")
    def publish(self, view_item: CustomViewItem, file: PathOrFileR) -> Optional[CustomViewItem]:
        url = self.expurl
        if isinstance(file, io_types_r):
            size = get_file_object_size(file)
        elif isinstance(file, (str, Path)) and (p := Path(file)).is_file():
            size = p.stat().st_size
        else:
            raise ValueError("File path or file object required for publishing custom view.")

        if size >= FILESIZE_LIMIT_MB * BYTES_PER_MB:
            upload_session_id = self.parent_srv.fileuploads.upload(file)
            url = f"{url}?uploadSessionId={upload_session_id}"
            xml_request, content_type = RequestFactory.CustomView.publish_req_chunked(view_item)
        else:
            if isinstance(file, io_types_r):
                file.seek(0)
                contents = file.read()
                if view_item.name is None:
                    raise MissingRequiredFieldError("Custom view item missing name.")
                filename = view_item.name
            elif isinstance(file, (str, Path)):
                filename = Path(file).name
                contents = Path(file).read_bytes()

            xml_request, content_type = RequestFactory.CustomView.publish_req(view_item, filename, contents)

        server_response = self.post_request(url, xml_request, content_type)
        return CustomViewItem.from_response(server_response.content, self.parent_srv.namespace)

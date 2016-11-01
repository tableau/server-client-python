from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .fileuploads_endpoint import Fileuploads
from .. import RequestFactory, WorkbookItem, ConnectionItem, ViewItem, PaginationItem
from ...models.tag_item import TagItem
import os
import logging
import copy
import cgi

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64   # 64MB

ALLOWED_FILE_EXTENSIONS = ['twb', 'twbx']

logger = logging.getLogger('tableau.endpoint.workbooks')


class Workbooks(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/workbooks".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Add new tags to workbook
    def _add_tags(self, workbook_id, tag_set):
        url = "{0}/{1}/tags".format(self.baseurl, workbook_id)
        add_req = RequestFactory.Tag.add_req(tag_set)
        server_response = self.put_request(url, add_req)
        return TagItem.from_response(server_response.content)

    # Delete a workbook's tag by name
    def _delete_tag(self, workbook_id, tag_name):
        url = "{0}/{1}/tags/{2}".format(self.baseurl, workbook_id, tag_name)
        self.delete_request(url)

    # Get all workbooks on site
    def get(self, req_options=None):
        logger.info('Querying all workbooks on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content)
        all_workbook_items = WorkbookItem.from_response(server_response.content)
        return all_workbook_items, pagination_item

    # Get 1 workbook
    def get_by_id(self, workbook_id):
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        logger.info('Querying single workbook (ID: {0})'.format(workbook_id))
        url = "{0}/{1}".format(self.baseurl, workbook_id)
        server_response = self.get_request(url)
        return WorkbookItem.from_response(server_response.content)[0]

    # Delete 1 workbook by id
    def delete(self, workbook_id):
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, workbook_id)
        self.delete_request(url)
        logger.info('Deleted single workbook (ID: {0})'.format(workbook_id))

    # Update workbook
    def update(self, workbook_item):
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        # Remove and add tags to match the workbook item's tag set
        if workbook_item.tags != workbook_item._initial_tags:
            add_set = workbook_item.tags - workbook_item._initial_tags
            remove_set = workbook_item._initial_tags - workbook_item.tags
            for tag in remove_set:
                self._delete_tag(workbook_item.id, tag)
            if add_set:
                workbook_item.tags = self._add_tags(workbook_item.id, add_set)
            workbook_item._initial_tags = copy.copy(workbook_item.tags)
        logger.info('Updated workbook tags to {0}'.format(workbook_item.tags))

        # Update the workbook itself
        url = "{0}/{1}".format(self.baseurl, workbook_item.id)
        update_req = RequestFactory.Workbook.update_req(workbook_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated workbook item (ID: {0}'.format(workbook_item.id))
        updated_workbook = copy.copy(workbook_item)
        return updated_workbook._parse_common_tags(server_response.content)

    # Download workbook contents with option of passing in filepath
    def download(self, workbook_id, filepath=None):
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/content".format(self.baseurl, workbook_id)
        server_response = self.get_request(url)
        _, params = cgi.parse_header(server_response.headers['Content-Disposition'])
        filename = os.path.basename(params['filename'])
        if filepath is None:
            filepath = filename
        elif os.path.isdir(filepath):
            filepath = os.path.join(filepath, filename)

        with open(filepath, 'wb') as f:
            f.write(server_response.content)
        logger.info('Downloaded workbook to {0} (ID: {1})'.format(filepath, workbook_id))
        return os.path.abspath(filepath)

    # Get all views of workbook
    def populate_views(self, workbook_item):
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/views".format(self.baseurl, workbook_item.id)
        server_response = self.get_request(url)
        workbook_item._set_views(ViewItem.from_response(server_response.content, workbook_id=workbook_item.id))
        logger.info('Populated views for workbook (ID: {0}'.format(workbook_item.id))

    # Get all connections of workbook
    def populate_connections(self, workbook_item):
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/connections".format(self.baseurl, workbook_item.id)
        server_response = self.get_request(url)
        workbook_item._set_connections(ConnectionItem.from_response(server_response.content))
        logger.info('Populated connections for workbook (ID: {0})'.format(workbook_item.id))

    # Get preview image of workbook
    def populate_preview_image(self, workbook_item):
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/previewImage".format(self.baseurl, workbook_item.id)
        server_response = self.get_request(url)
        workbook_item._set_preview_image(server_response.content)
        logger.info('Populated preview image for workbook (ID: {0})'.format(workbook_item.id))

    # Publishes workbook. Chunking method if file over 64MB
    def publish(self, workbook_item, file_path, mode, connection_credentials=None):
        if not os.path.isfile(file_path):
            error = "File path does not lead to an existing file."
            raise IOError(error)
        if not hasattr(self.parent_srv.PublishMode, mode):
            error = 'Invalid mode defined.'
            raise ValueError(error)

        filename = os.path.basename(file_path)
        file_extension = os.path.splitext(filename)[1][1:]

        # If name is not defined, grab the name from the file to publish
        if not workbook_item.name:
            workbook_item.name = os.path.splitext(filename)[0]
        if file_extension not in ALLOWED_FILE_EXTENSIONS:
            error = "Only {} files can be published as workbooks.".format(', '.join(ALLOWED_FILE_EXTENSIONS))
            raise ValueError(error)

        # Construct the url with the defined mode
        url = "{0}?workbookType={1}".format(self.baseurl, file_extension)
        if mode == self.parent_srv.PublishMode.Overwrite:
            url += '&{0}=true'.format(mode.lower())
        elif mode == self.parent_srv.PublishMode.Append:
            error = 'Workbooks cannot be appended.'
            raise ValueError(error)

        # Determine if chunking is required (64MB is the limit for single upload method)
        if os.path.getsize(file_path) >= FILESIZE_LIMIT:
            logger.info('Publishing {0} to server with chunking method (workbook over 64MB)'.format(filename))
            upload_session_id = Fileuploads.upload_chunks(self.parent_srv, file_path)
            url = "{0}&uploadSessionId={1}".format(url, upload_session_id)
            xml_request, content_type = RequestFactory.Workbook.publish_req_chunked(workbook_item,
                                                                                    connection_credentials)
        else:
            logger.info('Publishing {0} to server'.format(filename))
            with open(file_path, 'rb') as f:
                file_contents = f.read()
            xml_request, content_type = RequestFactory.Workbook.publish_req(workbook_item,
                                                                            filename,
                                                                            file_contents,
                                                                            connection_credentials)
        server_response = self.post_request(url, xml_request, content_type)
        new_workbook = WorkbookItem.from_response(server_response.content)[0]
        logger.info('Published {0} (ID: {1})'.format(filename, new_workbook.id))
        return new_workbook

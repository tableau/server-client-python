from endpoint import Endpoint
from exceptions import MissingRequiredFieldError
from .fileuploads_endpoint import Fileuploads
from .. import RequestFactory, WorkbookItem, ConnectionItem, ViewItem, PaginationItem
from ...models.tag_item import TagItem
import os
import logging
import copy
import cgi


# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64   # 64MB

# For when a workbook is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB

logger = logging.getLogger('tableau.endpoint.workbooks')

class Workbooks(Endpoint):
    def __init__(self, parent_srv):
        super(Endpoint, self).__init__()
        self.baseurl = "{0}/sites/{1}/workbooks"
        self.parent_srv = parent_srv

    def _construct_url(self):
        return self.baseurl.format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Add new tags to workbook
    def _add_tags(self, workbook_id, tag_set):
        url = "{0}/{1}/tags".format(self._construct_url(), workbook_id)
        add_req = RequestFactory.Tag.add_req(tag_set)
        server_response = self.put_request(url, add_req)
        return TagItem.from_response(server_response.text)

    # Delete a workbook's tag by name
    def _delete_tag(self, workbook_id, tag_name):
        url = "{0}/{1}/tags/{2}".format(self._construct_url(), workbook_id, tag_name)
        self.delete_request(url)

    def _upload_chunks(self, file_path):
        file_upload = Fileuploads(self.parent_srv)
        upload_id = file_upload.initiate()
        chunks = self._read_chunks(file_path)
        for chunk in chunks:
            req_body, content_type = RequestFactory.Workbook.chunk_req(chunk)
            fileupload_item = file_upload.append(req_body, content_type)
            logger.info('Published {0}MB of workbook'.format(fileupload_item.file_size))
        logger.info('Committing file upload...')
        return upload_id

    def _read_chunks(self, file_path):
        with open(file_path, 'rb') as f:
            while True:
                chunked_content = f.read(CHUNK_SIZE)
                if not chunked_content:
                    break
                yield chunked_content

    # Get all workbooks on site
    def get(self, req_options=None):
        logger.info('Querying all workbooks on site')
        url = self._construct_url()
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.text)
        all_workbook_items = WorkbookItem.from_response(server_response.text)
        return pagination_item, all_workbook_items

    # Get 1 workbook
    def get_by_id(self, workbook_id):
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        logger.info('Querying single workbook (ID: {0})'.format(workbook_id))
        url = "{0}/{1}".format(self._construct_url(), workbook_id)
        server_response = self.get_request(url)
        return WorkbookItem.from_response(server_response.text)[0]

    # Delete 1 workbook by id
    def delete(self, workbook_id):
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self._construct_url(), workbook_id)
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
        url = "{0}/{1}".format(self._construct_url(), workbook_item.id)
        update_req = RequestFactory.Workbook.update_req(workbook_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated workbook item (ID: {0}'.format(workbook_item.id))
        updated_workbook = copy.copy(workbook_item)
        return updated_workbook._parse_common_tags(server_response.text)

    # Download workbook contents with option of passing in filepath
    def download(self, workbook_id, filepath=None):
        if not workbook_id:
            error = "Workbook ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/content".format(self._construct_url(), workbook_id)
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
        url = "{0}/{1}/views".format(self._construct_url(), workbook_item.id)
        server_response = self.get_request(url)
        workbook_item._set_views(ViewItem.from_response(server_response.text, workbook_id=workbook_item.id))
        logger.info('Populated views for workbook (ID: {0}'.format(workbook_item.id))

    # Get all connections of workbook
    def populate_connections(self, workbook_item):
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/connections".format(self._construct_url(), workbook_item.id)
        server_response = self.get_request(url)
        workbook_item._set_connections(ConnectionItem.from_response(server_response.text))
        logger.info('Populated connections for workbook (ID: {0})'.format(workbook_item.id))

    # Get preview image of workbook
    def populate_preview_image(self, workbook_item):
        if not workbook_item.id:
            error = "Workbook item missing ID. Workbook must be retrieved from server first."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/previewImage".format(self._construct_url(), workbook_item.id)
        server_response = self.get_request(url)
        workbook_item._set_preview_image(server_response.content)
        logger.info('Populated preview image for workbook (ID: {0})'.format(workbook_item.id))

    # Publishes workbook. Chunking method if file over 64MB
    def publish(self, workbook_item, file_path, mode):
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
        if file_extension != 'twb' and file_extension != 'twbx':
            error = "Only .twb and .twbx files can be published as workbooks."
            raise ValueError(error)

        # Construct the url with the defined mode
        url = "{0}?workbookType={1}".format(self._construct_url(), file_extension)
        if mode == self.parent_srv.PublishMode.Overwrite:
            url += '&{0}=true'.format(mode.lower())
        elif mode == self.parent_srv.PublishMode.Append:
            error = 'Workbooks cannot be appended.'
            raise ValueError(error)

        # Determine if chunking is required (64MB is the limit for single upload method)
        if os.path.getsize(file_path) >= FILESIZE_LIMIT:
            logger.info('Publishing {0} to server with chunking method (workbook over 64MB)'.format(filename))
            upload_session_id = self._upload_chunks(file_path)
            url = "{0}&uploadSessionId={1}".format(url, upload_session_id)
            req_body, content_type = RequestFactory.Workbook.publish_req_chunked(workbook_item)
        else:
            logger.info('Publishing {0} to server'.format(filename))
            with open(file_path, 'rb') as f:
                file_contents = f.read()
            req_body, content_type = RequestFactory.Workbook.publish_req(workbook_item,
                                                                           filename,
                                                                           file_contents)
        server_response = self.post_multipart_request(url, req_body, content_type)
        new_workbook = WorkbookItem.from_response(server_response.text)[0]
        logger.info('Published {0} (ID: {1})'.format(filename, new_workbook.id))
        return new_workbook

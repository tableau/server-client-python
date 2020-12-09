from .exceptions import MissingRequiredFieldError
from .endpoint import Endpoint, api
from .. import RequestFactory
from ...models.fileupload_item import FileuploadItem
import os.path
import logging

# For when a datasource is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB

logger = logging.getLogger('tableau.endpoint.fileuploads')


class Fileuploads(Endpoint):
    def __init__(self, parent_srv):
        super(Fileuploads, self).__init__(parent_srv)
        self.upload_id = ''

    @property
    def baseurl(self):
        return "{0}/sites/{1}/fileUploads".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="2.0")
    def initiate(self):
        url = self.baseurl
        server_response = self.post_request(url, '')
        fileupload_item = FileuploadItem.from_response(server_response.content, self.parent_srv.namespace)
        self.upload_id = fileupload_item.upload_session_id
        logger.info('Initiated file upload session (ID: {0})'.format(self.upload_id))
        return self.upload_id

    @api(version="2.0")
    def append(self, xml_request, content_type):
        if not self.upload_id:
            error = "File upload session must be initiated first."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}".format(self.baseurl, self.upload_id)
        server_response = self.put_request(url, xml_request, content_type)
        logger.info('Uploading a chunk to session (ID: {0})'.format(self.upload_id))
        return FileuploadItem.from_response(server_response.content, self.parent_srv.namespace)

    def read_chunks(self, file):
        file_opened = False
        try:
            file_content = open(file, 'rb')
            file_opened = True
        except TypeError:
            file_content = file

        while True:
            chunked_content = file_content.read(CHUNK_SIZE)
            if not chunked_content:
                if file_opened:
                    file_content.close()
                break
            yield chunked_content

    @classmethod
    def upload_chunks(cls, parent_srv, file):
        file_uploader = cls(parent_srv)
        upload_id = file_uploader.initiate()

        chunks = file_uploader.read_chunks(file)
        for chunk in chunks:
            xml_request, content_type = RequestFactory.Fileupload.chunk_req(chunk)
            fileupload_item = file_uploader.append(xml_request, content_type)
            logger.info("\tPublished {0}MB".format(fileupload_item.file_size))
        logger.info("\tCommitting file upload...")
        return upload_id

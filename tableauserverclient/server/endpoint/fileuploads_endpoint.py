import logging

from .endpoint import Endpoint, api
from .. import RequestFactory
from ...models.fileupload_item import FileuploadItem

# For when a datasource is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB

logger = logging.getLogger("tableau.endpoint.fileuploads")


class Fileuploads(Endpoint):
    def __init__(self, parent_srv):
        super(Fileuploads, self).__init__(parent_srv)

    @property
    def baseurl(self):
        return "{0}/sites/{1}/fileUploads".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="2.0")
    def initiate(self):
        url = self.baseurl
        server_response = self.post_request(url, "")
        fileupload_item = FileuploadItem.from_response(server_response.content, self.parent_srv.namespace)
        upload_id = fileupload_item.upload_session_id
        logger.info("Initiated file upload session (ID: {0})".format(upload_id))
        return upload_id

    @api(version="2.0")
    def append(self, upload_id, data, content_type):
        url = "{0}/{1}".format(self.baseurl, upload_id)
        server_response = self.put_request(url, data, content_type)
        logger.info("Uploading a chunk to session (ID: {0})".format(upload_id))
        return FileuploadItem.from_response(server_response.content, self.parent_srv.namespace)

    def _read_chunks(self, file):
        file_opened = False
        try:
            file_content = open(file, "rb")
            file_opened = True
        except TypeError:
            file_content = file

        try:
            while True:
                chunked_content = file_content.read(CHUNK_SIZE)
                if not chunked_content:
                    break
                yield chunked_content
        finally:
            if file_opened:
                file_content.close()

    def upload(self, file):
        upload_id = self.initiate()
        for chunk in self._read_chunks(file):
            request, content_type = RequestFactory.Fileupload.chunk_req(chunk)
            fileupload_item = self.append(upload_id, request, content_type)
            logger.info("\tPublished {0}MB".format(fileupload_item.file_size))
        logger.info("File upload finished (ID: {0})".format(upload_id))
        return upload_id

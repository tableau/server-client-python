from .endpoint import Endpoint, api
from tableauserverclient import datetime_helpers as datetime
from tableauserverclient.helpers.logging import logger

from tableauserverclient.config import BYTES_PER_MB, config
from tableauserverclient.models import FileuploadItem
from tableauserverclient.server import RequestFactory


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
                chunked_content = file_content.read(config.CHUNK_SIZE_MB * BYTES_PER_MB)
                if not chunked_content:
                    break
                yield chunked_content
        finally:
            if file_opened:
                file_content.close()

    def upload(self, file):
        upload_id = self.initiate()
        for chunk in self._read_chunks(file):
            logger.debug("{} processing chunk...".format(datetime.timestamp()))
            request, content_type = RequestFactory.Fileupload.chunk_req(chunk)
            logger.debug("{} created chunk request".format(datetime.timestamp()))
            fileupload_item = self.append(upload_id, request, content_type)
            logger.info(
                "\t{0} Published {1}MB".format(datetime.timestamp(), (fileupload_item.file_size / BYTES_PER_MB))
            )
        logger.info("File upload finished (ID: {0})".format(upload_id))
        return upload_id

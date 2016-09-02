from endpoint import Endpoint
from exceptions import MissingRequiredFieldError
from ...models.fileupload_item import FileuploadItem
import logging

logger = logging.getLogger('tableau.endpoint.fileuploads')


class Fileuploads(Endpoint):
    def __init__(self, parent_srv):
        super(Endpoint, self).__init__()
        self.base_url = "{0}/sites/{1}/fileUploads"
        self.parent_srv = parent_srv
        self.upload_id = ''

    def _construct_url(self):
        return self.base_url.format(self.parent_srv.baseurl, self.parent_srv.site_id)

    def initiate(self):
        url = self._construct_url()
        server_response = self.post_request(url, '')
        fileupload_item = FileuploadItem.from_response(server_response.text)
        self.upload_id = fileupload_item.upload_session_id
        logger.info('Initiated file upload session (ID: {0})'.format(self.upload_id))
        return self.upload_id

    def append(self, req_body, content_type):
        if not self.upload_id:
            error = "File upload session must be initiated first."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}".format(self._construct_url(), self.upload_id)
        server_response = self.put_multipart_request(url, req_body, content_type)
        logger.info('Uploading a chunk to session (ID: {0})'.format(self.upload_id))
        return FileuploadItem.from_response(server_response.text)

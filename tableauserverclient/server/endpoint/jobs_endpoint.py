from .endpoint import Endpoint, api
from .. import JobItem
import logging

logger = logging.getLogger('tableau.endpoint.jobs')


class Jobs(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/jobs".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version='2.6')
    def get(self, job_id):
        logger.info('Query for information about job ' + job_id)
        url = "{0}/{1}".format(self.baseurl, job_id)
        server_response = self.get_request(url)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

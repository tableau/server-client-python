import logging

from .endpoint import QuerysetEndpoint, api
from .exceptions import JobCancelledException, JobFailedException
from .. import JobItem, BackgroundJobItem, PaginationItem
from ..request_options import RequestOptionsBase
from ...exponential_backoff import ExponentialBackoffTimer

logger = logging.getLogger("tableau.endpoint.jobs")

from typing import List, Optional, Tuple, Union


class Jobs(QuerysetEndpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/jobs".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="2.6")
    def get(
        self, job_id: Optional[str] = None, req_options: Optional[RequestOptionsBase] = None
    ) -> Tuple[List[BackgroundJobItem], PaginationItem]:
        # Backwards Compatibility fix until we rev the major version
        if job_id is not None and isinstance(job_id, str):
            import warnings

            warnings.warn("Jobs.get(job_id) is deprecated, update code to use Jobs.get_by_id(job_id)")
            return self.get_by_id(job_id)
        if isinstance(job_id, RequestOptionsBase):
            req_options = job_id

        self.parent_srv.assert_at_least_version("3.1", "Jobs.get_by_id(job_id)")
        server_response = self.get_request(self.baseurl, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        jobs = BackgroundJobItem.from_response(server_response.content, self.parent_srv.namespace)
        return jobs, pagination_item

    @api(version="3.1")
    def cancel(self, job_id: Union[str, JobItem]):
        if isinstance(job_id, JobItem):
            job_id = job_id.id
        assert isinstance(job_id, str)
        url = "{0}/{1}".format(self.baseurl, job_id)
        return self.put_request(url)

    @api(version="2.6")
    def get_by_id(self, job_id: str) -> JobItem:
        logger.info("Query for information about job " + job_id)
        url = "{0}/{1}".format(self.baseurl, job_id)
        server_response = self.get_request(url)
        new_job = JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return new_job

    def wait_for_job(self, job_id: Union[str, JobItem], *, timeout: Optional[float] = None) -> JobItem:
        if isinstance(job_id, JobItem):
            job_id = job_id.id
        assert isinstance(job_id, str)
        logger.debug(f"Waiting for job {job_id}")

        backoffTimer = ExponentialBackoffTimer(timeout=timeout)
        job = self.get_by_id(job_id)
        while job.completed_at is None:
            backoffTimer.sleep()
            job = self.get_by_id(job_id)
            logger.debug(f"\tJob {job_id} progress={job.progress}")

        logger.info("Job {} Completed: Finish Code: {} - Notes:{}".format(job_id, job.finish_code, job.notes))

        if job.finish_code == JobItem.FinishCode.Success:
            return job
        elif job.finish_code == JobItem.FinishCode.Failed:
            raise JobFailedException(job)
        elif job.finish_code == JobItem.FinishCode.Cancelled:
            raise JobCancelledException(job)
        else:
            raise AssertionError("Unexpected finish_code in job", job)

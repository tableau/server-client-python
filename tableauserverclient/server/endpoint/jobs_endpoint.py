import logging
from typing_extensions import Self, overload


from tableauserverclient.models import JobItem, BackgroundJobItem, PaginationItem
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api
from tableauserverclient.server.endpoint.exceptions import JobCancelledException, JobFailedException
from tableauserverclient.server.query import QuerySet
from tableauserverclient.server.request_options import RequestOptionsBase
from tableauserverclient.exponential_backoff import ExponentialBackoffTimer

from tableauserverclient.helpers.logging import logger

from typing import List, Optional, Tuple, Union


class Jobs(QuerysetEndpoint[BackgroundJobItem]):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/jobs".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @overload  # type: ignore[override]
    def get(self: Self, job_id: str, req_options: Optional[RequestOptionsBase] = None) -> JobItem:  # type: ignore[override]
        ...

    @overload  # type: ignore[override]
    def get(self: Self, job_id: RequestOptionsBase, req_options: None) -> Tuple[List[BackgroundJobItem], PaginationItem]:  # type: ignore[override]
        ...

    @overload  # type: ignore[override]
    def get(self: Self, job_id: None, req_options: Optional[RequestOptionsBase]) -> Tuple[List[BackgroundJobItem], PaginationItem]:  # type: ignore[override]
        ...

    @api(version="2.6")
    def get(self, job_id=None, req_options=None):
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

    def filter(self, *invalid, page_size: Optional[int] = None, **kwargs) -> QuerySet[BackgroundJobItem]:
        """
        Queries the Tableau Server for items using the specified filters. Page
        size can be specified to limit the number of items returned in a single
        request. If not specified, the default page size is 100. Page size can
        be an integer between 1 and 1000.

        No positional arguments are allowed. All filters must be specified as
        keyword arguments. If you use the equality operator, you can specify it
        through <field_name>=<value>. If you want to use a different operator,
        you can specify it through <field_name>__<operator>=<value>. Field
        names can either be in snake_case or camelCase.

        This endpoint supports the following fields and operators:


        args__has=...
        completed_at=...
        completed_at__gt=...
        completed_at__gte=...
        completed_at__lt=...
        completed_at__lte=...
        created_at=...
        created_at__gt=...
        created_at__gte=...
        created_at__lt=...
        created_at__lte=...
        job_type=...
        job_type__in=...
        notes__has=...
        priority=...
        priority__gt=...
        priority__gte=...
        priority__lt=...
        priority__lte=...
        progress=...
        progress__gt=...
        progress__gte=...
        progress__lt=...
        progress__lte=...
        started_at=...
        started_at__gt=...
        started_at__gte=...
        started_at__lt=...
        started_at__lte=...
        status=...
        subtitle=...
        subtitle__has=...
        title=...
        title__has=...
        """

        return super().filter(*invalid, page_size=page_size, **kwargs)

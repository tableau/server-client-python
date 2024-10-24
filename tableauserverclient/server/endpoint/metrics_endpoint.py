from .endpoint import QuerysetEndpoint, api
from .exceptions import MissingRequiredFieldError
from .permissions_endpoint import _PermissionsEndpoint
from .dqw_endpoint import _DataQualityWarningEndpoint
from .resource_tagger import _ResourceTagger
from tableauserverclient.server import RequestFactory
from tableauserverclient.models import MetricItem, PaginationItem

import logging

from typing import List, Optional, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..request_options import RequestOptions
    from ...server import Server


from tableauserverclient.helpers.logging import logger


class Metrics(QuerysetEndpoint[MetricItem]):
    def __init__(self, parent_srv: "Server") -> None:
        super(Metrics, self).__init__(parent_srv)
        self._resource_tagger = _ResourceTagger(parent_srv)
        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._data_quality_warnings = _DataQualityWarningEndpoint(self.parent_srv, "metric")

    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/metrics".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Get all metrics
    @api(version="3.9")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[MetricItem], PaginationItem]:
        logger.info("Querying all metrics on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_metric_items = MetricItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_metric_items, pagination_item

    # Get 1 metric by id
    @api(version="3.9")
    def get_by_id(self, metric_id: str) -> MetricItem:
        if not metric_id:
            error = "Metric ID undefined."
            raise ValueError(error)
        logger.info("Querying single metric (ID: {0})".format(metric_id))
        url = "{0}/{1}".format(self.baseurl, metric_id)
        server_response = self.get_request(url)
        return MetricItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Delete 1 metric by id
    @api(version="3.9")
    def delete(self, metric_id: str) -> None:
        if not metric_id:
            error = "Metric ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, metric_id)
        self.delete_request(url)
        logger.info("Deleted single metric (ID: {0})".format(metric_id))

    # Update metric
    @api(version="3.9")
    def update(self, metric_item: MetricItem) -> MetricItem:
        if not metric_item.id:
            error = "Metric item missing ID. Metric must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        self._resource_tagger.update_tags(self.baseurl, metric_item)

        # Update the metric itself
        url = "{0}/{1}".format(self.baseurl, metric_item.id)
        update_req = RequestFactory.Metric.update_req(metric_item)
        server_response = self.put_request(url, update_req)
        logger.info("Updated metric item (ID: {0})".format(metric_item.id))
        return MetricItem.from_response(server_response.content, self.parent_srv.namespace)[0]

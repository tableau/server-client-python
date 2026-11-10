import logging
import warnings

from .default_permissions_endpoint import _DefaultPermissionsEndpoint
from .endpoint import api, Endpoint
from .permissions_endpoint import _PermissionsEndpoint
from tableauserverclient.models import DataAccelerationReportItem

from tableauserverclient.helpers.logging import logger


class DataAccelerationReport(Endpoint):
    def __init__(self, parent_srv):
        super().__init__(parent_srv)

        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._default_permissions = _DefaultPermissionsEndpoint(parent_srv, lambda: self.baseurl)

    @property
    def baseurl(self):
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/dataAccelerationReport"

    @api(version="3.8")
    def get(self, req_options=None):
        """
        Gets the data acceleration report for the current site, which compares
        page load times for sheets before and after data acceleration.

        Deprecated: this method will be removed in a future release of this
        library. Tableau retired data acceleration and its REST API methods
        in Tableau Server 2026.2 (REST API 3.29). The method is not available
        on Tableau Cloud.

        REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_site.htm#get_data_acceleration_report

        Parameters
        ----------
        req_options : RequestOptions, optional
            Options to pass to the request.

        Returns
        -------
        DataAccelerationReportItem
            The report, with one comparison record per accelerated sheet.

        Warnings
        --------
        This method is deprecated. Tableau Cloud and Tableau Server 2026.2 and
        later respond to this request with a 404 (error code 404003).
        """
        warnings.warn(
            "DataAccelerationReport.get is deprecated and will be removed. Tableau retired data acceleration "
            "in Tableau Server 2026.2.",
            DeprecationWarning,
            # 3, not 2: the @api wrapper adds a frame, and the warning should point at the caller.
            stacklevel=3,
        )
        logger.info("Querying data acceleration report")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        data_acceleration_report = DataAccelerationReportItem.from_response(
            server_response.content, self.parent_srv.namespace
        )
        return data_acceleration_report

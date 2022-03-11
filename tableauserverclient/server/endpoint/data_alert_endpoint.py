import logging

from .endpoint import api, Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, DataAlertItem, PaginationItem, UserItem

logger = logging.getLogger("tableau.endpoint.dataAlerts")

from typing import List, Optional, TYPE_CHECKING, Tuple, Union


if TYPE_CHECKING:
    from ..server import Server
    from ..request_options import RequestOptions


class DataAlerts(Endpoint):
    def __init__(self, parent_srv: "Server") -> None:
        super(DataAlerts, self).__init__(parent_srv)

    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/dataAlerts".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="3.2")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[DataAlertItem], PaginationItem]:
        logger.info("Querying all dataAlerts on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_dataAlert_items = DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_dataAlert_items, pagination_item

    # Get 1 dataAlert
    @api(version="3.2")
    def get_by_id(self, dataAlert_id: str) -> DataAlertItem:
        if not dataAlert_id:
            error = "dataAlert ID undefined."
            raise ValueError(error)
        logger.info("Querying single dataAlert (ID: {0})".format(dataAlert_id))
        url = "{0}/{1}".format(self.baseurl, dataAlert_id)
        server_response = self.get_request(url)
        return DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.2")
    def delete(self, dataAlert: Union[DataAlertItem, str]) -> None:
        if isinstance(dataAlert, DataAlertItem):
            dataAlert_id = dataAlert.id
        elif isinstance(dataAlert, str):
            dataAlert_id = dataAlert
        else:
            raise TypeError("dataAlert should be a DataAlertItem or a string of an id.")
        if not dataAlert_id:
            error = "Dataalert ID undefined."
            raise ValueError(error)
        # DELETE /api/api-version/sites/site-id/dataAlerts/data-alert-id/users/user-id
        url = "{0}/{1}".format(self.baseurl, dataAlert_id)
        self.delete_request(url)
        logger.info("Deleted single dataAlert (ID: {0})".format(dataAlert_id))

    @api(version="3.2")
    def delete_user_from_alert(self, dataAlert: Union[DataAlertItem, str], user: Union[UserItem, str]) -> None:
        if isinstance(dataAlert, DataAlertItem):
            dataAlert_id = dataAlert.id
        elif isinstance(dataAlert, str):
            dataAlert_id = dataAlert
        else:
            raise TypeError("dataAlert should be a DataAlertItem or a string of an id.")
        if isinstance(user, UserItem):
            user_id = user.id
        elif isinstance(user, str):
            user_id = user
        else:
            raise TypeError("user should be a UserItem or a string of an id.")
        if not dataAlert_id:
            error = "Dataalert ID undefined."
            raise ValueError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        # DELETE /api/api-version/sites/site-id/dataAlerts/data-alert-id/users/user-id
        url = "{0}/{1}/users/{2}".format(self.baseurl, dataAlert_id, user_id)
        self.delete_request(url)
        logger.info("Deleted User (ID {0}) from dataAlert (ID: {1})".format(user_id, dataAlert_id))

    @api(version="3.2")
    def add_user_to_alert(self, dataAlert_item: DataAlertItem, user: Union[UserItem, str]) -> UserItem:
        if isinstance(user, UserItem):
            user_id = user.id
        elif isinstance(user, str):
            user_id = user
        else:
            raise TypeError("user should be a UserItem or a string of an id.")
        if not dataAlert_item.id:
            error = "Dataalert item missing ID."
            raise MissingRequiredFieldError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/users".format(self.baseurl, dataAlert_item.id)
        update_req = RequestFactory.DataAlert.add_user_to_alert(dataAlert_item, user_id)
        server_response = self.post_request(url, update_req)
        logger.info("Added user (ID {0}) to dataAlert item (ID: {1})".format(user_id, dataAlert_item.id))
        added_user = UserItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return added_user

    @api(version="3.2")
    def update(self, dataAlert_item: DataAlertItem) -> DataAlertItem:
        if not dataAlert_item.id:
            error = "Dataalert item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, dataAlert_item.id)
        update_req = RequestFactory.DataAlert.update_req(dataAlert_item)
        server_response = self.put_request(url, update_req)
        logger.info("Updated dataAlert item (ID: {0})".format(dataAlert_item.id))
        updated_dataAlert = DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_dataAlert

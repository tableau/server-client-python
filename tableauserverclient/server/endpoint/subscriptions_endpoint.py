import logging

from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError
from tableauserverclient.server import RequestFactory
from tableauserverclient.models import SubscriptionItem, PaginationItem

from tableauserverclient.helpers.logging import logger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..request_options import RequestOptions


class Subscriptions(Endpoint):
    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/subscriptions"

    @api(version="2.3")
    def get(self, req_options: "RequestOptions | None" = None) -> tuple[list[SubscriptionItem], PaginationItem]:
        logger.info("Querying all subscriptions for the site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)

        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_subscriptions = SubscriptionItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_subscriptions, pagination_item

    @api(version="2.3")
    def get_by_id(self, subscription_id: str) -> SubscriptionItem:
        if not subscription_id:
            error = "No Subscription ID provided"
            raise ValueError(error)
        logger.info(f"Querying a single subscription by id ({subscription_id})")
        url = f"{self.baseurl}/{subscription_id}"
        server_response = self.get_request(url)
        return SubscriptionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="2.3")
    def create(self, subscription_item: SubscriptionItem) -> SubscriptionItem:
        if not subscription_item:
            error = "No Susbcription provided"
            raise ValueError(error)
        if not subscription_item.schedule_id:
            # See tableau/server-client-python#1658: users trying to create an
            # "On Extract Refresh" subscription pass schedule_id=None and hit
            # a confusing wire-layer error. Point them at the factory.
            raise ValueError(
                "schedule_id is required; for on-extract-refresh subscriptions "
                "use SubscriptionItem.on_extract_refresh(...)"
            )
        logger.info(f"Creating a subscription ({subscription_item})")
        url = self.baseurl
        create_req = RequestFactory.Subscription.create_req(subscription_item)
        server_response = self.post_request(url, create_req)
        return SubscriptionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="2.3")
    def delete(self, subscription_id: str) -> None:
        if not subscription_id:
            error = "Subscription ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{subscription_id}"
        self.delete_request(url)
        logger.info(f"Deleted subscription (ID: {subscription_id})")

    @api(version="2.3")
    def update(self, subscription_item: SubscriptionItem) -> SubscriptionItem:
        if not subscription_item.id:
            error = "Subscription item missing ID. Subscription must be retrieved from server first."
            raise MissingRequiredFieldError(error)
        # Cloud subscriptions parsed from a GET response can arrive with
        # schedule_id=None when the server inlines a full <schedule> element
        # in place of a bare <schedule id=...> reference. When the inlined
        # element still carries an id attribute we can lift it into
        # schedule_id so fetch-then-update works. When it does not carry an
        # id (some Cloud responses inline the schedule with only name +
        # frequencyDetails), no fallback is possible — the caller must
        # supply schedule_id explicitly.
        schedule_id = subscription_item.schedule_id
        if schedule_id is None and subscription_item.schedule is not None:
            schedule_id = subscription_item.schedule.id
            if schedule_id is not None:
                subscription_item.schedule_id = schedule_id
        if not schedule_id:
            raise ValueError(
                "schedule_id is required to update a subscription. On Tableau "
                "Cloud, subscriptions parsed from a GET response may inline the "
                "referenced schedule without an id attribute; those subscriptions "
                "cannot be updated via fetch-then-mutate-then-update because the "
                "server did not return the schedule's id. Look up the schedule "
                "separately (server.schedules.get(...)) and set schedule_id on "
                "the SubscriptionItem before calling update()."
            )
        url = f"{self.baseurl}/{subscription_item.id}"
        update_req = RequestFactory.Subscription.update_req(subscription_item)
        server_response = self.put_request(url, update_req)
        logger.info(f"Updated subscription item (ID: {subscription_item.id})")
        return SubscriptionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

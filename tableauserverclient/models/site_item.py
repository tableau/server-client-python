import xml.etree.ElementTree as ET
from .property_decorators import (property_is_enum, property_is_boolean, property_matches,
                                  property_not_empty, property_not_nullable, property_is_positive_int,
                                  property_is_int_range)


VALID_CONTENT_URL_RE = r"^[a-zA-Z0-9_\-]*$"


class SiteItem(object):
    class AdminMode:
        ContentAndUsers = 'ContentAndUsers'
        ContentOnly = 'ContentOnly'

    class State:
        Active = 'Active'
        Suspended = 'Suspended'

    def __init__(self, name, content_url, admin_mode=None, cache_warmup_enabled=None, commenting_enabled=None,
                 disable_subscriptions=None, extract_encryption_mode=None, flows_enabled=None,
                 guest_access_enabled=None, materialized_views_mode=None, revision_history_enabled=None,
                 revision_limit=None, storage_quota=None, subscribe_others_enabled=None, tier_creator_capacity=None,
                 tier_explorer_capacity=None, tier_viewer_capacity=None, user_quota=None):
        self._id = None
        self._num_creators = None
        self._num_explorers = None
        self._num_users = None
        self._num_viewers = None
        self._state = None
        self._storage = None

        self.admin_mode = admin_mode
        self.cache_warmup_enabled = cache_warmup_enabled
        self.content_url = content_url
        self.commenting_enabled = commenting_enabled
        self.disable_subscriptions = disable_subscriptions
        self.extract_encryption_mode = extract_encryption_mode
        self.flows_enabled = flows_enabled
        self.guest_access_enabled = guest_access_enabled
        self.materialized_views_mode = materialized_views_mode
        self.name = name
        self.revision_history_enabled = revision_history_enabled
        self.revision_limit = revision_limit
        self.storage_quota = storage_quota
        self.subscribe_others_enabled = subscribe_others_enabled
        self.tier_creator_capacity = tier_creator_capacity
        self.tier_explorer_capacity = tier_explorer_capacity
        self.tier_viewer_capacity = tier_viewer_capacity
        self.user_quota = user_quota

    @property
    def id(self):
        return self._id

    @property
    def num_creators(self):
        return self._num_creators

    @property
    def num_explorers(self):
        return self._num_explorers

    @property
    def num_users(self):
        return self._num_users

    @property
    def num_viewers(self):
        return self._num_viewers

    @property
    def state(self):
        return self._state

    @state.setter
    @property_is_enum(State)
    def state(self, value):
        self._state = value

    @property
    def storage(self):
        return self._storage

    @property
    def admin_mode(self):
        return self._admin_mode

    @admin_mode.setter
    @property_is_enum(AdminMode)
    def admin_mode(self, value):
        self._admin_mode = value

    @property
    def cache_warmup_enabled(self):
        return self._cache_warmup_enabled

    @cache_warmup_enabled.setter
    @property_is_boolean
    def cache_warmup_enabled(self, value):
        self._cache_warmup_enabled = value

    @property
    def content_url(self):
        return self._content_url

    @content_url.setter
    @property_not_nullable
    @property_matches(VALID_CONTENT_URL_RE, "content_url can contain only letters, numbers, dashes, and underscores")
    def content_url(self, value):
        self._content_url = value

    @property
    def commenting_enabled(self):
        return self._commenting_enabled

    @commenting_enabled.setter
    @property_is_boolean
    def commenting_enabled(self, value):
        self._commenting_enabled = value

    @property
    def disable_subscriptions(self):
        return self._disable_subscriptions

    @disable_subscriptions.setter
    @property_is_boolean
    def disable_subscriptions(self, value):
        self._disable_subscriptions = value

    @property
    def extract_encryption_mode(self):
        return self._extract_encryption_mode

    @extract_encryption_mode.setter
    def extract_encryption_mode(self, value):
        self._extract_encryption_mode = value

    @property
    def flows_enabled(self):
        return self._flows_enabled

    @flows_enabled.setter
    @property_is_boolean
    def flows_enabled(self, value):
        self._flows_enabled = value

    @property
    def guest_access_enabled(self):
        return self._guest_access_enabled

    @guest_access_enabled.setter
    @property_is_boolean
    def guest_access_enabled(self, value):
        self._guest_access_enabled = value

    @property
    def materialized_views_mode(self):
        return self._materialized_views_mode

    @materialized_views_mode.setter
    def materialized_views_mode(self, value):
        self._materialized_views_mode = value

    @property
    def name(self):
        return self._name

    @name.setter
    @property_not_empty
    @property_not_nullable
    def name(self, value):
        self._name = value

    @property
    def revision_history_enabled(self):
        return self._revision_history_enabled

    @revision_history_enabled.setter
    @property_is_boolean
    def revision_history_enabled(self, value):
        self._revision_history_enabled = value

    @property
    def revision_limit(self):
        return self._revision_limit

    @revision_limit.setter
    @property_is_int_range((2, 10000), allowed=[-1])
    def revision_limit(self, value):
        self._revision_limit = value

    @property
    def storage_quota(self):
        return self._storage_quota

    @storage_quota.setter
    @property_is_positive_int()
    def storage_quota(self, value):
        self._storage_quota = value

    @property
    def subscribe_others_enabled(self):
        return self._subscribe_others_enabled

    @subscribe_others_enabled.setter
    @property_is_boolean
    def subscribe_others_enabled(self, value):
        self._subscribe_others_enabled = value

    @property
    def tier_creator_capacity(self):
        return self._tier_creator_capacity

    @tier_creator_capacity.setter
    @property_is_positive_int(allowed=[-1])
    def tier_creator_capacity(self, value):
        self._tier_creator_capacity = value

    @property
    def tier_explorer_capacity(self):
        return self._tier_explorer_capacity

    @tier_explorer_capacity.setter
    @property_is_positive_int(allowed=[-1])
    def tier_explorer_capacity(self, value):
        self._tier_explorer_capacity = value

    @property
    def tier_viewer_capacity(self):
        return self._tier_viewer_capacity

    @tier_viewer_capacity.setter
    @property_is_positive_int(allowed=[-1])
    def tier_viewer_capacity(self, value):
        self._tier_viewer_capacity = value

    @property
    def user_quota(self):
        return self._user_quota

    @user_quota.setter
    @property_is_positive_int(allowed=[-1])
    def user_quota(self, value):
        self._user_quota = value

    def is_default(self):
        return self.content_url == ''

    def _parse_updated_tags(self, site_xml, ns):
        if not isinstance(site_xml, ET.Element):
            site_xml = ET.fromstring(site_xml).find('.//t:site', namespaces=ns)
        if site_xml is not None:
            site_fields = self._parse_element(site_xml, ns)
            self._set_values(site_fields)
            if not self.revision_history_enabled:
                self.revision_limit = None
        return self

    def _set_values(self, site_fields):
        if 'id' in site_fields:
            self._id = site_fields['id']
        if 'state' in site_fields:
            self.state = site_fields['state']
        if 'adminMode' in site_fields:
            self.admin_mode = site_fields['adminMode']
        if 'cacheWarmupEnabled' in site_fields:
            self.cache_warmup_enabled = string_to_bool(site_fields['cacheWarmupEnabled'])
        if 'contentUrl' in site_fields:
            self.content_url = site_fields['contentUrl']
        if 'commentingEnabled' in site_fields:
            self.commenting_enabled = string_to_bool(site_fields['commentingEnabled'])
        if 'disableSubscriptions' in site_fields:
            self.disable_subscriptions = string_to_bool(site_fields['disableSubscriptions'])
        if 'extractEncryptionMode' in site_fields:
            self.extract_encryption_mode = site_fields['extractEncryptionMode']
        if 'flowsEnabled' in site_fields:
            self.flows_enabled = string_to_bool(site_fields['flowsEnabled'])
        if 'guestAccessEnabled' in site_fields:
            self.guest_access_enabled = string_to_bool(site_fields['guestAccessEnabled'])
        if 'materializedViewsMode' in site_fields:
            self.materialized_views_mode = site_fields['materializedViewsMode']
        if 'name' in site_fields:
            self.name = site_fields['name']
        if 'revisionHistoryEnabled' in site_fields:
            self.revision_history_enabled = string_to_bool(site_fields['revisionHistoryEnabled'])
        if 'revisionLimit' in site_fields:
            self.revision_limit = int(site_fields['revisionLimit'])
        if 'storageQuota' in site_fields:
            self.storage_quota = int(site_fields['storageQuota'])
        if 'subscribeOthersEnabled' in site_fields:
            self.subscribe_others_enabled = string_to_bool(site_fields['subscribeOthersEnabled'])
        if 'tierCreatorCapacity' in site_fields:
            self.tier_creator_capacity = int(site_fields['tierCreatorCapacity'])
        if 'tierExplorerCapacity' in site_fields:
            self.tier_explorer_capacity = int(site_fields['tierExplorerCapacity'])
        if 'tierViewerCapacity' in site_fields:
            self.tier_viewer_capacity = int(site_fields['tierViewerCapacity'])
        if 'userQuota' in site_fields:
            self.user_quota = int(site_fields['userQuota'])
        if 'usage' in site_fields:
            usage_fields = site_fields['usage']
            if 'numCreators' in usage_fields:
                self._num_creators = int(usage_fields['numCreators'])
            if 'numExplorers' in usage_fields:
                self._num_explorers = int(usage_fields['numExplorers'])
            if 'numUsers' in usage_fields:
                self._num_users = int(usage_fields['numUsers'])
            if 'numViewers' in usage_fields:
                self._num_viewers = int(usage_fields['numViewers'])
            if 'storage' in usage_fields:
                self._storage = int(usage_fields['storage'])

    @classmethod
    def from_response(cls, resp, ns):
        all_site_items = list()
        parsed_response = ET.fromstring(resp)
        all_site_xml = parsed_response.findall('.//t:site', namespaces=ns)
        for site_xml in all_site_xml:
            site_fields = cls._parse_element(site_xml, ns)
            site_item = cls(site_fields['name'], site_fields['contentUrl'])
            site_item._set_values(site_fields)
            all_site_items.append(site_item)
        return all_site_items

    @staticmethod
    def _parse_element(site_xml, ns):
        site_fields = site_xml.attrib
        usage_elem = site_xml.find('.//t:usage', namespaces=ns)
        if usage_elem is not None:
            usage_fields = usage_elem.attrib
            site_fields['usage'] = usage_fields

        return site_fields


# Used to convert string represented boolean to a boolean type
def string_to_bool(s):
    return s.lower() == 'true'

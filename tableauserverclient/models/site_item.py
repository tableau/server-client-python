import xml.etree.ElementTree as ET
from .property_decorators import (property_is_enum, property_is_boolean, property_matches,
                                  property_not_empty, property_not_nullable, property_is_int)


VALID_CONTENT_URL_RE = r"^[a-zA-Z0-9_\-]*$"


class SiteItem(object):
    class AdminMode:
        ContentAndUsers = 'ContentAndUsers'
        ContentOnly = 'ContentOnly'

    class State:
        Active = 'Active'
        Suspended = 'Suspended'

    def __init__(self, name, content_url, admin_mode=None, user_quota=None, storage_quota=None,
                 disable_subscriptions=False, subscribe_others_enabled=True, revision_history_enabled=False,
                 revision_limit=None, data_acceleration_mode=None, flows_enabled=True, cataloging_enabled=True,
                 editing_flows_enabled=True, scheduling_flows_enabled=True, allow_subscription_attachments=True,
                 guest_access_enabled=False, cache_warmup_enabled=True, commenting_enabled=True,
                 extract_encryption_mode=None, request_access_enabled=False, run_now_enabled=True,
                 tier_explorer_capacity=None, tier_creator_capacity=None, tier_viewer_capacity=None,
                 data_alerts_enabled=True, commenting_mentions_enabled=True, catalog_obfuscation_enabled=False,
                 flow_auto_save_enabled=True, web_extraction_enabled=True, metrics_content_type_enabled=True,
                 notify_site_admins_on_throttle=False, authoring_enabled=True, custom_subscription_email_enabled=False,
                 custom_subscription_email=False, custom_subscription_footer_enabled=False,
                 custom_subscription_footer=False, ask_data_mode='EnabledByDefault', named_sharing_enabled=True,
                 mobile_biometrics_enabled=False, sheet_image_enabled=True, derived_permissions_enabled=False,
                 user_visibility_mode='FULL', use_default_time_zone=True, time_zone=None,
                 auto_suspend_refresh_enabled=True, auto_suspend_refresh_inactivity_window=30):
        self._admin_mode = None
        self._id = None
        self._num_users = None
        self._state = None
        self._status_reason = None
        self._storage = None
        self._revision_limit = None
        self.user_quota = user_quota
        self.storage_quota = storage_quota
        self.content_url = content_url
        self.disable_subscriptions = disable_subscriptions
        self.name = name
        self.revision_history_enabled = revision_history_enabled
        self.subscribe_others_enabled = subscribe_others_enabled
        self.admin_mode = admin_mode
        self.data_acceleration_mode = data_acceleration_mode
        self.cataloging_enabled = cataloging_enabled
        self.flows_enabled = flows_enabled
        self.editing_flows_enabled = editing_flows_enabled
        self.scheduling_flows_enabled = scheduling_flows_enabled
        self.allow_subscription_attachments = allow_subscription_attachments
        self.guest_access_enabled = guest_access_enabled
        self.cache_warmup_enabled = cache_warmup_enabled
        self.commenting_enabled = commenting_enabled
        self.extract_encryption_mode = extract_encryption_mode
        self.request_access_enabled = request_access_enabled
        self.run_now_enabled = run_now_enabled
        self.tier_explorer_capacity = tier_explorer_capacity
        self.tier_creator_capacity = tier_creator_capacity
        self.tier_viewer_capacity = tier_viewer_capacity
        self.data_alerts_enabled = data_alerts_enabled
        self.commenting_mentions_enabled = commenting_mentions_enabled
        self.catalog_obfuscation_enabled = catalog_obfuscation_enabled
        self.flow_auto_save_enabled = flow_auto_save_enabled
        self.web_extraction_enabled = web_extraction_enabled
        self.metrics_content_type_enabled = metrics_content_type_enabled
        self.notify_site_admins_on_throttle = notify_site_admins_on_throttle
        self.authoring_enabled = authoring_enabled
        self.custom_subscription_footer_enabled = custom_subscription_footer_enabled
        self.custom_subscription_email_enabled = custom_subscription_email_enabled
        self.custom_subscription_email = custom_subscription_email
        self.custom_subscription_footer = custom_subscription_footer
        self.ask_data_mode = ask_data_mode
        self.named_sharing_enabled = named_sharing_enabled
        self.mobile_biometrics_enabled = mobile_biometrics_enabled
        self.sheet_image_enabled = sheet_image_enabled
        self.derived_permissions_enabled = derived_permissions_enabled
        self.user_visibility_mode = user_visibility_mode
        self.use_default_time_zone = use_default_time_zone
        self.time_zone = time_zone
        self.auto_suspend_refresh_enabled = auto_suspend_refresh_enabled
        self.auto_suspend_refresh_inactivity_window = auto_suspend_refresh_inactivity_window

    @property
    def admin_mode(self):
        return self._admin_mode

    @admin_mode.setter
    @property_is_enum(AdminMode)
    def admin_mode(self, value):
        self._admin_mode = value

    @property
    def content_url(self):
        return self._content_url

    @content_url.setter
    @property_not_nullable
    @property_matches(VALID_CONTENT_URL_RE, "content_url can contain only letters, numbers, dashes, and underscores")
    def content_url(self, value):
        self._content_url = value

    @property
    def disable_subscriptions(self):
        return self._disable_subscriptions

    @disable_subscriptions.setter
    @property_is_boolean
    def disable_subscriptions(self, value):
        self._disable_subscriptions = value

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    @property_not_empty
    def name(self, value):
        self._name = value

    @property
    def num_users(self):
        return self._num_users

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
    @property_is_int((2, 10000), allowed=[-1])
    def revision_limit(self, value):
        self._revision_limit = value

    @property
    def state(self):
        return self._state

    @state.setter
    @property_is_enum(State)
    def state(self, value):
        self._state = value

    @property
    def status_reason(self):
        return self._status_reason

    @property
    def storage(self):
        return self._storage

    @property
    def subscribe_others_enabled(self):
        return self._subscribe_others_enabled

    @subscribe_others_enabled.setter
    @property_is_boolean
    def subscribe_others_enabled(self, value):
        self._subscribe_others_enabled = value

    @property
    def data_acceleration_mode(self):
        return self._data_acceleration_mode

    @data_acceleration_mode.setter
    def data_acceleration_mode(self, value):
        self._data_acceleration_mode = value

    @property
    def cataloging_enabled(self):
        return self._cataloging_enabled

    @cataloging_enabled.setter
    def cataloging_enabled(self, value):
        self._cataloging_enabled = value

    @property
    def flows_enabled(self):
        return self._flows_enabled

    @flows_enabled.setter
    @property_is_boolean
    def flows_enabled(self, value):
        self._flows_enabled = value

    def is_default(self):
        return self.name.lower() == 'default'

    @property
    def editing_flows_enabled(self):
        return self._editing_flows_enabled

    @editing_flows_enabled.setter
    @property_is_boolean
    def editing_flows_enabled(self, value):
        self._editing_flows_enabled = value

    @property
    def scheduling_flows_enabled(self):
        return self._scheduling_flows_enabled

    @scheduling_flows_enabled.setter
    @property_is_boolean
    def scheduling_flows_enabled(self, value):
        self._scheduling_flows_enabled = value

    @property
    def allow_subscription_attachments(self):
        return self._allow_subscription_attachments

    @allow_subscription_attachments.setter
    @property_is_boolean
    def allow_subscription_attachments(self, value):
        self._allow_subscription_attachments = value

    @property
    def guest_access_enabled(self):
        return self._guest_access_enabled

    @guest_access_enabled.setter
    @property_is_boolean
    def guest_access_enabled(self, value):
        self._guest_access_enabled = value

    @property
    def cache_warmup_enabled(self):
        return self._cache_warmup_enabled

    @cache_warmup_enabled.setter
    @property_is_boolean
    def cache_warmup_enabled(self, value):
        self._cache_warmup_enabled = value

    @property
    def commenting_enabled(self):
        return self._commenting_enabled

    @commenting_enabled.setter
    @property_is_boolean
    def commenting_enabled(self, value):
        self._commenting_enabled = value

    @property
    def extract_encryption_mode(self):
        return self._extract_encryption_mode

    @extract_encryption_mode.setter
    def extract_encryption_mode(self, value):
        self._extract_encryption_mode = value

    @property
    def request_access_enabled(self):
        return self._request_access_enabled

    @request_access_enabled.setter
    @property_is_boolean
    def request_access_enabled(self, value):
        self._request_access_enabled = value

    @property
    def run_now_enabled(self):
        return self._run_now_enabled

    @run_now_enabled.setter
    @property_is_boolean
    def run_now_enabled(self, value):
        self._run_now_enabled = value

    @property
    def tier_explorer_capacity(self):
        return self._tier_explorer_capacity

    @tier_explorer_capacity.setter
    def tier_explorer_capacity(self, value):
        self._tier_explorer_capacity = value

    @property
    def tier_creator_capacity(self):
        return self._tier_creator_capacity

    @tier_creator_capacity.setter
    def tier_creator_capacity(self, value):
        self._tier_creator_capacity = value

    @property
    def tier_viewer_capacity(self):
        return self._tier_viewer_capacity

    @tier_viewer_capacity.setter
    def tier_viewer_capacity(self, value):
        self._tier_viewer_capacity = value

    @property
    def data_alerts_enabled(self):
        return self._data_alerts_enabled

    @data_alerts_enabled.setter
    @property_is_boolean
    def data_alerts_enabled(self, value):
        self._data_alerts_enabled = value

    @property
    def commenting_mentions_enabled(self):
        return self._commenting_mentions_enabled

    @commenting_mentions_enabled.setter
    @property_is_boolean
    def commenting_mentions_enabled(self, value):
        self._commenting_mentions_enabled = value

    @property
    def catalog_obfuscation_enabled(self):
        return self._catalog_obfuscation_enabled

    @catalog_obfuscation_enabled.setter
    @property_is_boolean
    def catalog_obfuscation_enabled(self, value):
        self._catalog_obfuscation_enabled = value

    @property
    def flow_auto_save_enabled(self):
        return self._flow_auto_save_enabled

    @flow_auto_save_enabled.setter
    @property_is_boolean
    def flow_auto_save_enabled(self, value):
        self._flow_auto_save_enabled = value

    @property
    def web_extraction_enabled(self):
        return self._web_extraction_enabled

    @web_extraction_enabled.setter
    @property_is_boolean
    def web_extraction_enabled(self, value):
        self._web_extraction_enabled = value

    @property
    def metrics_content_type_enabled(self):
        return self._metrics_content_type_enabled

    @metrics_content_type_enabled.setter
    @property_is_boolean
    def metrics_content_type_enabled(self, value):
        self._metrics_content_type_enabled = value

    @property
    def notify_site_admins_on_throttle(self):
        return self._notify_site_admins_on_throttle

    @notify_site_admins_on_throttle.setter
    @property_is_boolean
    def notify_site_admins_on_throttle(self, value):
        self._notify_site_admins_on_throttle = value

    @property
    def authoring_enabled(self):
        return self._authoring_enabled

    @authoring_enabled.setter
    @property_is_boolean
    def authoring_enabled(self, value):
        self._authoring_enabled = value

    @property
    def custom_subscription_email_enabled(self):
        return self._custom_subscription_email_enabled

    @custom_subscription_email_enabled.setter
    @property_is_boolean
    def custom_subscription_email_enabled(self, value):
        self._custom_subscription_email_enabled = value

    @property
    def custom_subscription_email(self):
        return self._custom_subscription_email

    @custom_subscription_email.setter
    def custom_subscription_email(self, value):
        self._custom_subscription_email = value

    @property
    def custom_subscription_footer_enabled(self):
        return self._custom_subscription_footer_enabled

    @custom_subscription_footer_enabled.setter
    @property_is_boolean
    def custom_subscription_footer_enabled(self, value):
        self._custom_subscription_footer_enabled = value

    @property
    def custom_subscription_footer(self):
        return self._custom_subscription_footer

    @custom_subscription_footer.setter
    def custom_subscription_footer(self, value):
        self._custom_subscription_footer = value

    @property
    def ask_data_mode(self):
        return self._ask_data_mode

    @ask_data_mode.setter
    def ask_data_mode(self, value):
        self._ask_data_mode = value

    @property
    def named_sharing_enabled(self):
        return self._named_sharing_enabled

    @named_sharing_enabled.setter
    @property_is_boolean
    def named_sharing_enabled(self, value):
        self._named_sharing_enabled = value

    @property
    def mobile_biometrics_enabled(self):
        return self._mobile_biometrics_enabled

    @mobile_biometrics_enabled.setter
    @property_is_boolean
    def mobile_biometrics_enabled(self, value):
        self._mobile_biometrics_enabled = value

    @property
    def sheet_image_enabled(self):
        return self._sheet_image_enabled

    @sheet_image_enabled.setter
    @property_is_boolean
    def sheet_image_enabled(self, value):
        self._sheet_image_enabled = value

    @property
    def derived_permissions_enabled(self):
        return self._derived_permissions_enabled

    @derived_permissions_enabled.setter
    @property_is_boolean
    def derived_permissions_enabled(self, value):
        self._derived_permissions_enabled = value

    @property
    def user_visibility_mode(self):
        return self._user_visibility_mode

    @user_visibility_mode.setter
    def user_visibility_mode(self, value):
        self._user_visibility_mode = value

    @property
    def use_default_time_zone(self):
        return self._use_default_time_zone

    @use_default_time_zone.setter
    def use_default_time_zone(self, value):
        self._use_default_time_zone = value

    @property
    def time_zone(self):
        return self._time_zone

    @time_zone.setter
    def time_zone(self, value):
        self._time_zone = value

    @property
    def auto_suspend_refresh_inactivity_window(self):
        return self._auto_suspend_refresh_inactivity_window

    @auto_suspend_refresh_inactivity_window.setter
    def auto_suspend_refresh_inactivity_window(self, value):
        self._auto_suspend_refresh_inactivity_window = value

    @property
    def auto_suspend_refresh_enabled(self):
        return self._auto_suspend_refresh_enabled

    @auto_suspend_refresh_enabled.setter
    def auto_suspend_refresh_enabled(self, value):
        self._auto_suspend_refresh_enabled = value

    def _parse_common_tags(self, site_xml, ns):
        if not isinstance(site_xml, ET.Element):
            site_xml = ET.fromstring(site_xml).find('.//t:site', namespaces=ns)
        if site_xml is not None:
            (_, name, content_url, _, admin_mode, state,
             subscribe_others_enabled, disable_subscriptions, revision_history_enabled,
             user_quota, storage_quota, revision_limit, num_users, storage,
             data_acceleration_mode, flows_enabled, cataloging_enabled, editing_flows_enabled,
             scheduling_flows_enabled, allow_subscription_attachments, guest_access_enabled,
             cache_warmup_enabled, commenting_enabled, extract_encryption_mode, request_access_enabled,
             run_now_enabled, tier_explorer_capacity, tier_creator_capacity, tier_viewer_capacity, data_alerts_enabled,
             commenting_mentions_enabled, catalog_obfuscation_enabled, flow_auto_save_enabled, web_extraction_enabled,
             metrics_content_type_enabled, notify_site_admins_on_throttle, authoring_enabled,
             custom_subscription_email_enabled, custom_subscription_email, custom_subscription_footer_enabled,
             custom_subscription_footer, ask_data_mode, named_sharing_enabled, mobile_biometrics_enabled,
             sheet_image_enabled, derived_permissions_enabled, user_visibility_mode, use_default_time_zone, time_zone,
             auto_suspend_refresh_enabled, auto_suspend_refresh_inactivity_window) = self._parse_element(site_xml, ns)

            self._set_values(None, name, content_url, None, admin_mode, state, subscribe_others_enabled,
                             disable_subscriptions, revision_history_enabled, user_quota, storage_quota,
                             revision_limit, num_users, storage, data_acceleration_mode, flows_enabled,
                             cataloging_enabled, editing_flows_enabled, scheduling_flows_enabled,
                             allow_subscription_attachments, guest_access_enabled, cache_warmup_enabled,
                             commenting_enabled, extract_encryption_mode, request_access_enabled, run_now_enabled,
                             tier_explorer_capacity, tier_creator_capacity, tier_viewer_capacity, data_alerts_enabled,
                             commenting_mentions_enabled, catalog_obfuscation_enabled, flow_auto_save_enabled,
                             web_extraction_enabled, metrics_content_type_enabled, notify_site_admins_on_throttle,
                             authoring_enabled, custom_subscription_email_enabled, custom_subscription_email,
                             custom_subscription_footer_enabled, custom_subscription_footer, ask_data_mode,
                             named_sharing_enabled, mobile_biometrics_enabled, sheet_image_enabled,
                             derived_permissions_enabled, user_visibility_mode, use_default_time_zone, time_zone,
                             auto_suspend_refresh_enabled, auto_suspend_refresh_inactivity_window)
        return self

    def _set_values(self, id, name, content_url, status_reason, admin_mode, state,
                    subscribe_others_enabled, disable_subscriptions, revision_history_enabled,
                    user_quota, storage_quota, revision_limit, num_users, storage, data_acceleration_mode,
                    flows_enabled, cataloging_enabled, editing_flows_enabled, scheduling_flows_enabled,
                    allow_subscription_attachments, guest_access_enabled, cache_warmup_enabled, commenting_enabled,
                    extract_encryption_mode, request_access_enabled, run_now_enabled, tier_explorer_capacity,
                    tier_creator_capacity, tier_viewer_capacity, data_alerts_enabled, commenting_mentions_enabled,
                    catalog_obfuscation_enabled, flow_auto_save_enabled, web_extraction_enabled,
                    metrics_content_type_enabled, notify_site_admins_on_throttle, authoring_enabled,
                    custom_subscription_email_enabled, custom_subscription_email, custom_subscription_footer_enabled,
                    custom_subscription_footer, ask_data_mode, named_sharing_enabled, mobile_biometrics_enabled,
                    sheet_image_enabled, derived_permissions_enabled, user_visibility_mode, use_default_time_zone,
                    time_zone, auto_suspend_refresh_enabled, auto_suspend_refresh_inactivity_window):
        if id is not None:
            self._id = id
        if name:
            self._name = name
        if content_url:
            self._content_url = content_url
        if status_reason:
            self._status_reason = status_reason
        if admin_mode:
            self._admin_mode = admin_mode
        if state:
            self._state = state
        if subscribe_others_enabled is not None:
            self._subscribe_others_enabled = subscribe_others_enabled
        if disable_subscriptions is not None:
            self._disable_subscriptions = disable_subscriptions
        if revision_history_enabled is not None:
            self._revision_history_enabled = revision_history_enabled
        if user_quota:
            self.user_quota = user_quota
        if storage_quota:
            self.storage_quota = storage_quota
        if revision_limit:
            self.revision_limit = revision_limit
        if num_users:
            self._num_users = num_users
        if storage:
            self._storage = storage
        if data_acceleration_mode:
            self._data_acceleration_mode = data_acceleration_mode
        if flows_enabled is not None:
            self.flows_enabled = flows_enabled
        if cataloging_enabled is not None:
            self.cataloging_enabled = cataloging_enabled
        if editing_flows_enabled is not None:
            self.editing_flows_enabled = editing_flows_enabled
        if scheduling_flows_enabled is not None:
            self.scheduling_flows_enabled = scheduling_flows_enabled
        if allow_subscription_attachments is not None:
            self.allow_subscription_attachments = allow_subscription_attachments
        if guest_access_enabled is not None:
            self.guest_access_enabled = guest_access_enabled
        if cache_warmup_enabled is not None:
            self.cache_warmup_enabled = cache_warmup_enabled
        if commenting_enabled is not None:
            self.commenting_enabled = commenting_enabled
        if extract_encryption_mode is not None:
            self.extract_encryption_mode = extract_encryption_mode
        if request_access_enabled is not None:
            self.request_access_enabled = request_access_enabled
        if run_now_enabled is not None:
            self.run_now_enabled = run_now_enabled
        if tier_explorer_capacity:
            self.tier_explorer_capacity = tier_explorer_capacity
        if tier_creator_capacity:
            self.tier_creator_capacity = tier_creator_capacity
        if tier_viewer_capacity:
            self.tier_viewer_capacity = tier_viewer_capacity
        if data_alerts_enabled is not None:
            self.data_alerts_enabled = data_alerts_enabled
        if commenting_mentions_enabled is not None:
            self.commenting_mentions_enabled = commenting_mentions_enabled
        if catalog_obfuscation_enabled is not None:
            self.catalog_obfuscation_enabled = catalog_obfuscation_enabled
        if flow_auto_save_enabled is not None:
            self.flow_auto_save_enabled = flow_auto_save_enabled
        if web_extraction_enabled is not None:
            self.web_extraction_enabled = web_extraction_enabled
        if metrics_content_type_enabled is not None:
            self.metrics_content_type_enabled = metrics_content_type_enabled
        if notify_site_admins_on_throttle is not None:
            self.notify_site_admins_on_throttle = notify_site_admins_on_throttle
        if authoring_enabled is not None:
            self.authoring_enabled = authoring_enabled
        if custom_subscription_email_enabled is not None:
            self.custom_subscription_email_enabled = custom_subscription_email_enabled
        if custom_subscription_email is not None:
            self.custom_subscription_email = custom_subscription_email
        if custom_subscription_footer_enabled is not None:
            self.custom_subscription_footer_enabled = custom_subscription_footer_enabled
        if custom_subscription_footer is not None:
            self.custom_subscription_footer = custom_subscription_footer
        if ask_data_mode is not None:
            self.ask_data_mode = ask_data_mode
        if named_sharing_enabled is not None:
            self.named_sharing_enabled = named_sharing_enabled
        if mobile_biometrics_enabled is not None:
            self.mobile_biometrics_enabled = mobile_biometrics_enabled
        if sheet_image_enabled is not None:
            self.sheet_image_enabled = sheet_image_enabled
        if derived_permissions_enabled is not None:
            self.derived_permissions_enabled = derived_permissions_enabled
        if user_visibility_mode is not None:
            self.user_visibility_mode = user_visibility_mode
        if use_default_time_zone is not None:
            self.use_default_time_zone = use_default_time_zone
        if time_zone is not None:
            self.time_zone = time_zone
        if auto_suspend_refresh_enabled is not None:
            self.auto_suspend_refresh_enabled = auto_suspend_refresh_enabled
        if auto_suspend_refresh_inactivity_window is not None:
            self.auto_suspend_refresh_inactivity_window = auto_suspend_refresh_inactivity_window

    @classmethod
    def from_response(cls, resp, ns):
        all_site_items = list()
        parsed_response = ET.fromstring(resp)
        all_site_xml = parsed_response.findall('.//t:site', namespaces=ns)
        for site_xml in all_site_xml:
            (id, name, content_url, status_reason, admin_mode, state, subscribe_others_enabled,
                disable_subscriptions, revision_history_enabled, user_quota, storage_quota,
                revision_limit, num_users, storage, data_acceleration_mode, flows_enabled, cataloging_enabled,
                editing_flows_enabled, scheduling_flows_enabled, allow_subscription_attachments, guest_access_enabled,
                cache_warmup_enabled, commenting_enabled, extract_encryption_mode, request_access_enabled,
                run_now_enabled, tier_explorer_capacity, tier_creator_capacity, tier_viewer_capacity,
                data_alerts_enabled, commenting_mentions_enabled, catalog_obfuscation_enabled, flow_auto_save_enabled,
                web_extraction_enabled, metrics_content_type_enabled, notify_site_admins_on_throttle,
                authoring_enabled, custom_subscription_email_enabled, custom_subscription_email,
                custom_subscription_footer_enabled, custom_subscription_footer, ask_data_mode, named_sharing_enabled,
                mobile_biometrics_enabled, sheet_image_enabled, derived_permissions_enabled, user_visibility_mode,
                use_default_time_zone, time_zone, auto_suspend_refresh_enabled,
                auto_suspend_refresh_inactivity_window) = cls._parse_element(site_xml, ns)

            site_item = cls(name, content_url)
            site_item._set_values(id, name, content_url, status_reason, admin_mode, state, subscribe_others_enabled,
                                  disable_subscriptions, revision_history_enabled, user_quota, storage_quota,
                                  revision_limit, num_users, storage, data_acceleration_mode, flows_enabled,
                                  cataloging_enabled, editing_flows_enabled, scheduling_flows_enabled,
                                  allow_subscription_attachments, guest_access_enabled, cache_warmup_enabled,
                                  commenting_enabled, extract_encryption_mode, request_access_enabled, run_now_enabled,
                                  tier_explorer_capacity, tier_creator_capacity, tier_viewer_capacity,
                                  data_alerts_enabled, commenting_mentions_enabled, catalog_obfuscation_enabled,
                                  flow_auto_save_enabled, web_extraction_enabled, metrics_content_type_enabled,
                                  notify_site_admins_on_throttle, authoring_enabled, custom_subscription_email_enabled,
                                  custom_subscription_email, custom_subscription_footer_enabled,
                                  custom_subscription_footer, ask_data_mode, named_sharing_enabled,
                                  mobile_biometrics_enabled, sheet_image_enabled, derived_permissions_enabled,
                                  user_visibility_mode, use_default_time_zone, time_zone, auto_suspend_refresh_enabled,
                                  auto_suspend_refresh_inactivity_window)
            all_site_items.append(site_item)
        return all_site_items

    @staticmethod
    def _parse_element(site_xml, ns):
        id = site_xml.get('id', None)
        name = site_xml.get('name', None)
        content_url = site_xml.get('contentUrl', None)
        status_reason = site_xml.get('statusReason', None)
        admin_mode = site_xml.get('adminMode', None)
        state = site_xml.get('state', None)
        subscribe_others_enabled = string_to_bool(site_xml.get('subscribeOthersEnabled', ''))
        disable_subscriptions = string_to_bool(site_xml.get('disableSubscriptions', ''))
        revision_history_enabled = string_to_bool(site_xml.get('revisionHistoryEnabled', ''))
        editing_flows_enabled = string_to_bool(site_xml.get('editingFlowsEnabled', ''))
        scheduling_flows_enabled = string_to_bool(site_xml.get('schedulingFlowsEnabled', ''))
        allow_subscription_attachments = string_to_bool(site_xml.get('allowSubscriptionAttachments', ''))
        guest_access_enabled = string_to_bool(site_xml.get('guestAccessEnabled', ''))
        cache_warmup_enabled = string_to_bool(site_xml.get('cacheWarmupEnabled', ''))
        commenting_enabled = string_to_bool(site_xml.get('commentingEnabled', ''))
        extract_encryption_mode = site_xml.get('extractEncryptionMode', None)
        request_access_enabled = string_to_bool(site_xml.get('requestAccessEnabled', ''))
        run_now_enabled = string_to_bool(site_xml.get('runNowEnabled', ''))
        tier_explorer_capacity = site_xml.get('tierExplorerCapacity', None)
        if tier_explorer_capacity:
            tier_explorer_capacity = int(tier_explorer_capacity)
        tier_creator_capacity = site_xml.get('tierCreatorCapacity', None)
        if tier_creator_capacity:
            tier_creator_capacity = int(tier_creator_capacity)
        tier_viewer_capacity = site_xml.get('tierViewerCapacity', None)
        if tier_viewer_capacity:
            tier_viewer_capacity = int(tier_viewer_capacity)
        data_alerts_enabled = string_to_bool(site_xml.get('dataAlertsEnabled', ''))
        commenting_mentions_enabled = string_to_bool(site_xml.get('commentingMentionsEnabled', ''))
        catalog_obfuscation_enabled = string_to_bool(site_xml.get('catalogObfuscationEnabled', ''))
        flow_auto_save_enabled = string_to_bool(site_xml.get('flowAutoSaveEnabled', ''))
        web_extraction_enabled = string_to_bool(site_xml.get('webExtractionEnabled', ''))
        metrics_content_type_enabled = string_to_bool(site_xml.get('metricsContentTypeEnabled', ''))
        notify_site_admins_on_throttle = string_to_bool(site_xml.get('notifySiteAdminsOnThrottle', ''))
        authoring_enabled = string_to_bool(site_xml.get('authoringEnabled', ''))
        custom_subscription_email_enabled = string_to_bool(site_xml.get('customSubscriptionEmailEnabled', ''))
        custom_subscription_email = site_xml.get('customSubscriptionEmail', None)
        custom_subscription_footer_enabled = string_to_bool(site_xml.get('customSubscriptionFooterEnabled', ''))
        custom_subscription_footer = site_xml.get('customSubscriptionFooter', None)
        ask_data_mode = site_xml.get('askDataMode', None)
        named_sharing_enabled = string_to_bool(site_xml.get('namedSharingEnabled', ''))
        mobile_biometrics_enabled = string_to_bool(site_xml.get('mobileBiometricsEnabled', ''))
        sheet_image_enabled = string_to_bool(site_xml.get('sheetImageEnabled', ''))
        derived_permissions_enabled = string_to_bool(site_xml.get('derivedPermissionsEnabled', ''))
        user_visibility_mode = site_xml.get('userVisibilityMode', '')
        use_default_time_zone = string_to_bool(site_xml.get('useDefaultTimeZone', ''))
        time_zone = site_xml.get('timeZone', None)
        auto_suspend_refresh_enabled = string_to_bool(site_xml.get('autoSuspendRefreshEnabled', ''))
        auto_suspend_refresh_inactivity_window = site_xml.get('autoSuspendRefreshInactivityWindow', None)
        if auto_suspend_refresh_inactivity_window:
            auto_suspend_refresh_inactivity_window = int(auto_suspend_refresh_inactivity_window)

        user_quota = site_xml.get('userQuota', None)
        if user_quota:
            user_quota = int(user_quota)

        storage_quota = site_xml.get('storageQuota', None)
        if storage_quota:
            storage_quota = int(storage_quota)

        revision_limit = site_xml.get('revisionLimit', None)
        if revision_limit:
            revision_limit = int(revision_limit)

        num_users = None
        storage = None
        usage_elem = site_xml.find('.//t:usage', namespaces=ns)
        if usage_elem is not None:
            num_users = usage_elem.get('numUsers', None)
            storage = usage_elem.get('storage', None)

        data_acceleration_mode = site_xml.get('dataAccelerationMode', '')

        flows_enabled = string_to_bool(site_xml.get('flowsEnabled', ''))
        cataloging_enabled = string_to_bool(site_xml.get('catalogingEnabled', ''))

        return id, name, content_url, status_reason, admin_mode, state, subscribe_others_enabled,\
            disable_subscriptions, revision_history_enabled, user_quota, storage_quota,\
            revision_limit, num_users, storage, data_acceleration_mode, flows_enabled, cataloging_enabled,\
            editing_flows_enabled, scheduling_flows_enabled, allow_subscription_attachments, guest_access_enabled,\
            cache_warmup_enabled, commenting_enabled, extract_encryption_mode, request_access_enabled, run_now_enabled,\
            tier_explorer_capacity, tier_creator_capacity, tier_viewer_capacity, data_alerts_enabled,\
            commenting_mentions_enabled, catalog_obfuscation_enabled, flow_auto_save_enabled, web_extraction_enabled,\
            metrics_content_type_enabled, notify_site_admins_on_throttle, authoring_enabled,\
            custom_subscription_email_enabled, custom_subscription_email, custom_subscription_footer_enabled,\
            custom_subscription_footer, ask_data_mode, named_sharing_enabled, mobile_biometrics_enabled,\
            sheet_image_enabled, derived_permissions_enabled, user_visibility_mode, use_default_time_zone, time_zone,\
            auto_suspend_refresh_enabled, auto_suspend_refresh_inactivity_window


# Used to convert string represented boolean to a boolean type
def string_to_bool(s):
    return s.lower() == 'true'

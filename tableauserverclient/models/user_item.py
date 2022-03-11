import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING

from defusedxml.ElementTree import fromstring

from .exceptions import UnpopulatedPropertyError
from .property_decorators import (
    property_is_enum,
    property_not_empty,
    property_not_nullable,
)
from .reference_item import ResourceReference
from ..datetime_helpers import parse_datetime

if TYPE_CHECKING:
    from ..server.pager import Pager


class UserItem(object):

    tag_name: str = "user"

    class Roles:
        Interactor = "Interactor"
        Publisher = "Publisher"
        ServerAdministrator = "ServerAdministrator"
        SiteAdministrator = "SiteAdministrator"
        Unlicensed = "Unlicensed"
        UnlicensedWithPublish = "UnlicensedWithPublish"
        Viewer = "Viewer"
        ViewerWithPublish = "ViewerWithPublish"
        Guest = "Guest"

        Creator = "Creator"
        Explorer = "Explorer"
        ExplorerCanPublish = "ExplorerCanPublish"
        ReadOnly = "ReadOnly"
        SiteAdministratorCreator = "SiteAdministratorCreator"
        SiteAdministratorExplorer = "SiteAdministratorExplorer"

        # Online only
        SupportUser = "SupportUser"

    class Auth:
        OpenID = "OpenID"
        SAML = "SAML"
        ServerDefault = "ServerDefault"

    def __init__(
        self, name: Optional[str] = None, site_role: Optional[str] = None, auth_setting: Optional[str] = None
    ) -> None:
        self._auth_setting: Optional[str] = None
        self._domain_name: Optional[str] = None
        self._external_auth_user_id: Optional[str] = None
        self._id: Optional[str] = None
        self._last_login: Optional[datetime] = None
        self._workbooks = None
        self._favorites: Optional[Dict[str, List]] = None
        self._groups = None
        self.email: Optional[str] = None
        self.fullname: Optional[str] = None
        self.name: Optional[str] = name
        self.site_role: Optional[str] = site_role
        self.auth_setting: Optional[str] = auth_setting

        return None

    @property
    def auth_setting(self) -> Optional[str]:
        return self._auth_setting

    @auth_setting.setter
    @property_is_enum(Auth)
    def auth_setting(self, value):
        self._auth_setting = value

    @property
    def domain_name(self) -> Optional[str]:
        return self._domain_name

    @property
    def external_auth_user_id(self) -> Optional[str]:
        return self._external_auth_user_id

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def last_login(self) -> Optional[datetime]:
        return self._last_login

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    @property_not_empty
    def name(self, value: str):
        self._name = value

    @property
    def site_role(self) -> Optional[str]:
        return self._site_role

    @site_role.setter
    @property_not_nullable
    @property_is_enum(Roles)
    def site_role(self, value):
        self._site_role = value

    @property
    def workbooks(self) -> "Pager":
        if self._workbooks is None:
            error = "User item must be populated with workbooks first."
            raise UnpopulatedPropertyError(error)
        return self._workbooks()

    @property
    def favorites(self) -> Dict[str, List]:
        if self._favorites is None:
            error = "User item must be populated with favorites first."
            raise UnpopulatedPropertyError(error)
        return self._favorites

    @property
    def groups(self) -> "Pager":
        if self._groups is None:
            error = "User item must be populated with groups first."
            raise UnpopulatedPropertyError(error)
        return self._groups()

    def to_reference(self) -> ResourceReference:
        return ResourceReference(id_=self.id, tag_name=self.tag_name)

    def _set_workbooks(self, workbooks) -> None:
        self._workbooks = workbooks

    def _set_groups(self, groups) -> None:
        self._groups = groups

    def _parse_common_tags(self, user_xml, ns) -> "UserItem":
        if not isinstance(user_xml, ET.Element):
            user_xml = fromstring(user_xml).find(".//t:user", namespaces=ns)
        if user_xml is not None:
            (
                _,
                _,
                site_role,
                _,
                _,
                fullname,
                email,
                auth_setting,
                _,
            ) = self._parse_element(user_xml, ns)
            self._set_values(None, None, site_role, None, None, fullname, email, auth_setting, None)
        return self

    def _set_values(
        self,
        id,
        name,
        site_role,
        last_login,
        external_auth_user_id,
        fullname,
        email,
        auth_setting,
        domain_name,
    ):
        if id is not None:
            self._id = id
        if name:
            self._name = name
        if site_role:
            self._site_role = site_role
        if last_login:
            self._last_login = last_login
        if external_auth_user_id:
            self._external_auth_user_id = external_auth_user_id
        if fullname:
            self.fullname = fullname
        if email:
            self.email = email
        if auth_setting:
            self._auth_setting = auth_setting
        if domain_name:
            self._domain_name = domain_name

    @classmethod
    def from_response(cls, resp, ns) -> List["UserItem"]:
        all_user_items = []
        parsed_response = fromstring(resp)
        all_user_xml = parsed_response.findall(".//t:user", namespaces=ns)
        for user_xml in all_user_xml:
            (
                id,
                name,
                site_role,
                last_login,
                external_auth_user_id,
                fullname,
                email,
                auth_setting,
                domain_name,
            ) = cls._parse_element(user_xml, ns)
            user_item = cls(name, site_role)
            user_item._set_values(
                id,
                name,
                site_role,
                last_login,
                external_auth_user_id,
                fullname,
                email,
                auth_setting,
                domain_name,
            )
            all_user_items.append(user_item)
        return all_user_items

    @staticmethod
    def as_reference(id_) -> ResourceReference:
        return ResourceReference(id_, UserItem.tag_name)

    @staticmethod
    def _parse_element(user_xml, ns):
        id = user_xml.get("id", None)
        name = user_xml.get("name", None)
        site_role = user_xml.get("siteRole", None)
        last_login = parse_datetime(user_xml.get("lastLogin", None))
        external_auth_user_id = user_xml.get("externalAuthUserId", None)
        fullname = user_xml.get("fullName", None)
        email = user_xml.get("email", None)
        auth_setting = user_xml.get("authSetting", None)

        domain_name = None
        domain_elem = user_xml.find(".//t:domain", namespaces=ns)
        if domain_elem is not None:
            domain_name = domain_elem.get("name", None)

        return (
            id,
            name,
            site_role,
            last_login,
            external_auth_user_id,
            fullname,
            email,
            auth_setting,
            domain_name,
        )

    def __repr__(self) -> str:
        return "<User {} name={} role={}>".format(self.id, self.name, self.site_role)

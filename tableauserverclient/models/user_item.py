import io
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from enum import IntEnum

from defusedxml.ElementTree import fromstring

from .exceptions import UnpopulatedPropertyError
from .property_decorators import (
    property_is_enum,
    property_not_empty,
)
from .reference_item import ResourceReference
from ..datetime_helpers import parse_datetime

from typing import Dict, List, Optional, TYPE_CHECKING

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
        str_site_role = self.site_role or "None"
        return "<User {} name={} role={}>".format(self.id, self.name, str_site_role)

    # valid values for each field
    CHOICES: List[List[str]] = [
        [],
        [],
        [],
        ["creator", "explorer", "viewer", "unlicensed"],  # license
        ["system", "site", "none", "no"],  # admin
        ["yes", "true", "1", "no", "false", "0"],  # publisher
        [],
        [Auth.SAML, Auth.OpenID, Auth.ServerDefault],  # auth
    ]

    class CSVImportFileItem(object):

        # CSV import file format
        # username, password, display_name, license, admin_level, publishing, email, auth type
        class Column(IntEnum):
            USERNAME = 0
            PASS = 1
            DISPLAY_NAME = 2
            LICENSE = 3  # aka site role
            ADMIN = 4
            PUBLISHER = 5
            EMAIL = 6
            AUTH = 7

            MAX = 7

        @staticmethod
        def _create_from_csv_line(line: str):
            if line is None or line is False or line == "\n" or line == "":
                return None
            line = line.strip().lower()
            values: List[str] = list(map(str.strip, line.split(",")))
            user = UserItem(values[UserItem.CSVImportFileItem.Column.USERNAME])
            if len(values) > 1:
                if len(values) > UserItem.CSVImportFileItem.Column.MAX:
                    raise ValueError("Too many attributes for user import")
                while len(values) <= UserItem.CSVImportFileItem.Column.MAX:
                    values.append("")
                site_role = UserItem.CSVImportFileItem.evaluate_site_role(
                    values[UserItem.CSVImportFileItem.Column.LICENSE],
                    values[UserItem.CSVImportFileItem.Column.ADMIN],
                    values[UserItem.CSVImportFileItem.Column.PUBLISHER],
                )

                user._set_values(
                    None,
                    values[UserItem.CSVImportFileItem.Column.USERNAME],
                    site_role,
                    None,
                    None,
                    values[UserItem.CSVImportFileItem.Column.DISPLAY_NAME],
                    values[UserItem.CSVImportFileItem.Column.EMAIL],
                    values[UserItem.CSVImportFileItem.Column.AUTH],
                    None,
                )
            return user

        @staticmethod
        def validate_file_for_import(csv_file: io.TextIOWrapper, logger) -> List[int]:
            num_errors = 0
            num_valid_lines = 0
            csv_file.seek(0)  # set to start of file in case it has been read earlier
            line: str = csv_file.readline()
            while line and line != "":
                try:
                    # do not print passwords
                    logger.info("Reading user {}".format(line[:4]))
                    UserItem.CSVImportFileItem._validate_imported_attributes_or_throw(line, logger)
                    num_valid_lines += 1
                except Exception as exc:
                    logger.info("Error parsing {}: {}".format(line[:4], exc))
                    num_errors += 1
                line = csv_file.readline()
            return [num_valid_lines, num_errors]

        # this might belong in the main User class
        # valid: username, domain/username, username@domain, domain/username@email
        @staticmethod
        def _validate_username_or_throw(username) -> None:
            if username is None or username == "" or username.strip(" ") == "":
                raise AttributeError("Username cannot be empty")
            if username.find(" ") >= 0:
                raise AttributeError("Username cannot contain spaces")
            at_symbol = username.find("@")
            if at_symbol >= 0:
                username = username[:at_symbol] + "X" + username[at_symbol + 1 :]
                if username.find("@") >= 0:
                    raise AttributeError("Username cannot repeat '@'")

        @staticmethod
        def _validate_imported_attributes_or_throw(incoming, logger) -> None:
            line = list(map(str.strip, incoming.split(",")))
            if len(line) > UserItem.CSVImportFileItem.Column.MAX:
                raise AttributeError("Too many attributes in line")
            username = line[UserItem.CSVImportFileItem.Column.USERNAME.value]
            logger.debug("> details - {}".format(username))
            UserItem.CSVImportFileItem._validate_username_or_throw(username)
            for i in range(1, len(line)):
                logger.debug("column {}: {}".format(UserItem.CSVImportFileItem.Column(i).name, line[i]))
                UserItem.CSVImportFileItem._validate_item(
                    line[i], UserItem.CHOICES[i], UserItem.CSVImportFileItem.Column(i)
                )

        @staticmethod
        def _validate_item(item: str, possible_values: List[str], column_type) -> None:
            if item is None or item == "":
                # value can be empty for any column except user, which is checked elsewhere
                return
            if item in possible_values or possible_values == []:
                return
            raise AttributeError("Invalid value {} for {}".format(item, column_type))

        # https://help.tableau.com/current/server/en-us/csvguidelines.htm#settings_and_site_roles
        @staticmethod
        def evaluate_site_role(license_level, admin_level, publisher):
            if not license_level or not admin_level or not publisher:
                return "Unlicensed"
            # ignore case everywhere
            license_level = license_level.lower()
            admin_level = admin_level.lower()
            publisher = publisher.lower()
            # don't need to check publisher for system/site admin
            if admin_level == "system":
                site_role = "SiteAdministrator"
            elif admin_level == "site":
                if license_level == "creator":
                    site_role = "SiteAdministratorCreator"
                elif license_level == "explorer":
                    site_role = "SiteAdministratorExplorer"
                else:
                    site_role = "SiteAdministratorExplorer"
            else:  # if it wasn't 'system' or 'site' then we can treat it as 'none'
                if publisher == "yes":
                    if license_level == "creator":
                        site_role = "Creator"
                    elif license_level == "explorer":
                        site_role = "ExplorerCanPublish"
                    else:
                        site_role = "Unlicensed"  # is this the expected outcome?
                else:  # publisher == 'no':
                    if license_level == "explorer" or license_level == "creator":
                        site_role = "Explorer"
                    elif license_level == "viewer":
                        site_role = "Viewer"
                    else:  # if license_level == 'unlicensed'
                        site_role = "Unlicensed"
            if site_role is None:
                site_role = "Unlicensed"
            return site_role

import io
import warnings
import xml.etree.ElementTree as ET
from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING

from defusedxml.ElementTree import fromstring
from typing_extensions import Self

from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.site_item import SiteAuthConfiguration
from .exceptions import UnpopulatedPropertyError
from .property_decorators import (
    property_is_enum,
    property_not_empty,
)
from .reference_item import ResourceReference

if TYPE_CHECKING:
    from tableauserverclient.server import Pager
    from tableauserverclient.models.favorites_item import FavoriteType


class UserItem:
    """
    The UserItem class contains the members or attributes for the view
    resources on Tableau Server. The UserItem class defines the information you
    can request or query from Tableau Server. The class attributes correspond
    to the attributes of a server request or response payload.


    Parameters
    ----------
    name: str
        The name of the user.

    site_role: str
        The role of the user on the site.

    auth_setting: str
        Required attribute for Tableau Cloud. How the user autenticates to the
        server.

    Attributes
    ----------
    domain_name: str | None
        The name of the Active Directory domain ("local" if local authentication
        is used).

    email: str | None
        The email address of the user.

    external_auth_user_id: str | None
        The unique identifier for the user in the external authentication system.

    id: str | None
        The unique identifier for the user.

    favorites: dict[str, list]
        The favorites of the user. Must be populated with a call to
        `populate_favorites()`.

    fullname: str | None
        The full name of the user.

    groups: Pager
        The groups the user belongs to. Must be populated with a call to
        `populate_groups()`.

    last_login: datetime | None
        The last time the user logged in.

    locale: str | None
        The locale of the user.

    language: str | None
        Language setting for the user.

    idp_configuration_id: str | None
        The ID of the identity provider configuration.

    workbooks: Pager
        The workbooks owned by the user. Must be populated with a call to
        `populate_workbooks()`.

    """

    tag_name: str = "user"

    class Roles:
        """
        The Roles class contains the possible roles for a user on Tableau
        Server.
        """

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
        """
        The Auth class contains the possible authentication settings for a user
        on Tableau Cloud.
        """

        OpenID = "OpenID"
        SAML = "SAML"
        TableauIDWithMFA = "TableauIDWithMFA"
        ServerDefault = "ServerDefault"

    def __init__(self, name: str | None = None, site_role: str | None = None, auth_setting: str | None = None) -> None:
        self._auth_setting: str | None = None
        self._domain_name: str | None = None
        self._external_auth_user_id: str | None = None
        self._id: str | None = None
        self._last_login: datetime | None = None
        self._workbooks = None
        self._favorites: "FavoriteType | None" = None
        self._groups = None
        self.email: str | None = None
        self.fullname: str | None = None
        self.name: str | None = name
        self.site_role: str | None = site_role
        self.auth_setting: str | None = auth_setting
        self._locale: str | None = None
        self._language: str | None = None
        self._idp_configuration_id: str | None = None

        return None

    def __str__(self) -> str:
        str_site_role = self.site_role or "None"
        return f"<User {self.id} name={self.name} role={str_site_role}>"

    def __repr__(self):
        return self.__str__() + "  { " + ", ".join(" % s: % s" % item for item in vars(self).items()) + "}"

    @property
    def auth_setting(self) -> str | None:
        return self._auth_setting

    @auth_setting.setter
    @property_is_enum(Auth)
    def auth_setting(self, value):
        self._auth_setting = value

    @property
    def domain_name(self) -> str | None:
        return self._domain_name

    @property
    def external_auth_user_id(self) -> str | None:
        return self._external_auth_user_id

    @property
    def id(self) -> str | None:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def last_login(self) -> datetime | None:
        return self._last_login

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str | None):
        self._name = value

    # valid: username, domain/username, username@domain, domain/username@email
    @staticmethod
    def validate_username_or_throw(username) -> None:
        if username is None or username == "" or username.strip(" ") == "":
            raise AttributeError("Username cannot be empty")
        if username.find(" ") >= 0:
            raise AttributeError("Username cannot contain spaces")
        at_symbol = username.find("@")
        if at_symbol >= 0:
            username = username[:at_symbol] + "X" + username[at_symbol + 1 :]
            if username.find("@") >= 0:
                raise AttributeError("Username cannot repeat '@'")

    @property
    def site_role(self) -> str | None:
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
    def favorites(self) -> "FavoriteType":
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

    @property
    def locale(self) -> str | None:
        return self._locale

    @property
    def language(self) -> str | None:
        return self._language

    @property
    def idp_configuration_id(self) -> str | None:
        """
        IDP configuration id for the user. This is only available on Tableau
        Cloud, 3.24 or later
        """
        return self._idp_configuration_id

    @idp_configuration_id.setter
    def idp_configuration_id(self, value: str) -> None:
        self._idp_configuration_id = value

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
                _,
                _,
                _,
            ) = self._parse_element(user_xml, ns)
            self._set_values(None, None, site_role, None, None, fullname, email, auth_setting, None, None, None, None)
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
        locale,
        language,
        idp_configuration_id,
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
            # Write directly to _auth_setting rather than going through the
            # @property_is_enum(Auth) setter. This method is called from both
            # CSV import and server response parsing (from_xml, populate, etc.);
            # if the server ever returns an auth type we don't yet know about
            # (a new Auth value in a future Tableau release), the enum guard
            # would raise ValueError during response parsing. CSV callers
            # already validate the auth string against CSVImport._AUTH_CANONICAL
            # before calling here, so this write is safe.
            self._auth_setting = auth_setting
        if domain_name:
            self._domain_name = domain_name
        if locale:
            self._locale = locale
        if language:
            self._language = language
        if idp_configuration_id:
            self._idp_configuration_id = idp_configuration_id

    @classmethod
    def from_response(cls, resp, ns) -> list["UserItem"]:
        element_name = ".//t:user"
        return cls._parse_xml(element_name, resp, ns)

    @classmethod
    def from_response_as_owner(cls, resp, ns) -> list["UserItem"]:
        element_name = ".//t:owner"
        return cls._parse_xml(element_name, resp, ns)

    @classmethod
    def from_xml(cls, xml: ET.Element, ns: dict | None = None) -> "UserItem":
        item = cls()
        item._set_values(*cls._parse_element(xml, ns))
        return item

    @classmethod
    def _parse_xml(cls, element_name, resp, ns):
        all_user_items = []
        parsed_response = fromstring(resp)
        all_user_xml = parsed_response.findall(element_name, namespaces=ns)
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
                locale,
                language,
                idp_configuration_id,
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
                locale,
                language,
                idp_configuration_id,
            )
            all_user_items.append(user_item)
        return all_user_items

    @staticmethod
    def as_reference(id_) -> ResourceReference:
        return ResourceReference(id_, UserItem.tag_name)

    def to_reference(self: Self) -> ResourceReference:
        if self.id is None:
            raise ValueError(f"{self.__class__.__qualname__} must have id to be converted to reference")
        return ResourceReference(self.id, self.tag_name)

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
        locale = user_xml.get("locale", None)
        language = user_xml.get("language", None)
        idp_configuration_id = user_xml.get("idpConfigurationId", None)

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
            locale,
            language,
            idp_configuration_id,
        )

    class CSVImport:
        """
        This class includes hardcoded options and logic for the CSV file format defined for user import
        https://help.tableau.com/current/server/en-us/users_import.htm
        """

        # username, password, display_name, license, admin_level, publishing, email, auth type
        class ColumnType(IntEnum):
            USERNAME = 0
            PASS = 1
            DISPLAY_NAME = 2
            LICENSE = 3  # aka site role
            ADMIN = 4
            PUBLISHER = 5
            EMAIL = 6
            AUTH = 7

        # Total number of columns supported by the import format. Held outside
        # the ColumnType enum so it can't be mistaken for a real column index.
        COLUMN_COUNT = 8

        # Lowercase -> canonical form mapping for the AUTH column. Class-level
        # so the dict isn't rebuilt on every call to create_user_from_line /
        # _validate_import_line_or_throw. The set of accepted values is derived
        # from this map (see _valid_attributes[AUTH]) so there's a single
        # source of truth.
        _AUTH_CANONICAL: dict[str, str] = {
            "saml": "SAML",
            "openid": "OpenID",
            "serverdefault": "ServerDefault",
            "tableauidwithmfa": "TableauIDWithMFA",
        }

        # Read a csv line and create a user item populated by the given attributes
        @staticmethod
        def create_user_from_line(line: str):
            if line is None or line is False or line == "\n" or line == "":
                return None
            values: list[str] = list(map(str.strip, line.strip().split(",")))
            if len(values) > UserItem.CSVImport.COLUMN_COUNT:
                raise ValueError("Too many attributes for user import")
            username = values[UserItem.CSVImport.ColumnType.USERNAME]
            user = UserItem(username)
            if len(values) > 1:
                while len(values) < UserItem.CSVImport.COLUMN_COUNT:
                    values.append("")
                site_role = UserItem.CSVImport._evaluate_site_role(
                    values[UserItem.CSVImport.ColumnType.LICENSE],
                    values[UserItem.CSVImport.ColumnType.ADMIN],
                    values[UserItem.CSVImport.ColumnType.PUBLISHER],
                )
                raw_auth = values[UserItem.CSVImport.ColumnType.AUTH]
                if raw_auth:
                    canonical = UserItem.CSVImport._AUTH_CANONICAL.get(raw_auth.lower())
                    if canonical is None:
                        # Unknown auth value: pass it through instead of raising.
                        # TSC's _AUTH_CANONICAL is a hardcoded list that will lag
                        # server-side additions; refusing to build the UserItem
                        # here would block CSV imports against newer servers as
                        # soon as Tableau ships a new auth type. If it is a
                        # typo, the server rejects the row when the request
                        # posts. Warn so the caller has a shot at noticing.
                        warnings.warn(
                            f"Unknown auth setting {raw_auth!r}; passing through unchanged. "
                            f"Known values: {sorted(UserItem.CSVImport._AUTH_CANONICAL.values())}",
                            stacklevel=2,
                        )
                        auth = raw_auth
                    else:
                        auth = canonical
                else:
                    auth = None
                user._set_values(
                    None,
                    username,
                    site_role,
                    None,
                    None,
                    values[UserItem.CSVImport.ColumnType.DISPLAY_NAME],
                    values[UserItem.CSVImport.ColumnType.EMAIL],
                    auth,
                    None,
                    None,
                    None,
                    None,
                )
            return user

        # Read through an entire CSV file meant for user import
        # Return the number of valid lines and a list of all the invalid lines
        @staticmethod
        def validate_file_for_import(csv_file: io.TextIOWrapper, logger) -> tuple[int, list[str]]:
            num_valid_lines = 0
            invalid_lines = []
            csv_file.seek(0)  # set to start of file in case it has been read earlier
            line: str = csv_file.readline()
            while line and line != "":
                try:
                    # do not print passwords
                    logger.info(f"Reading user {line[:4]}")
                    UserItem.CSVImport._validate_import_line_or_throw(line, logger)
                    num_valid_lines += 1
                except Exception as exc:
                    logger.info(f"Error parsing {line[:4]}: {exc}")
                    invalid_lines.append(line)
                line = csv_file.readline()
            return num_valid_lines, invalid_lines

        # Some fields in the import file are restricted to specific values
        # Iterate through each field and validate the given value against hardcoded constraints
        @staticmethod
        def _validate_import_line_or_throw(incoming, logger) -> None:
            # AUTH column's valid set is derived from _AUTH_CANONICAL so there's
            # one source of truth for the accepted values.
            _valid_attributes: list[list[str]] = [
                [],
                [],
                [],
                ["creator", "explorer", "viewer", "unlicensed"],  # license
                ["system", "site", "none", "no"],  # admin
                ["yes", "true", "1", "no", "false", "0"],  # publisher
                [],
                list(UserItem.CSVImport._AUTH_CANONICAL.values()),  # auth - normalized before comparison
            ]

            line = list(map(str.strip, incoming.split(",")))
            if len(line) > UserItem.CSVImport.COLUMN_COUNT:
                raise ValueError("Too many attributes for user import")
            username = line[UserItem.CSVImport.ColumnType.USERNAME.value]
            logger.debug(f"> details - {username}")
            UserItem.validate_username_or_throw(username)
            for i in range(1, len(line)):
                value = line[i]
                valid = _valid_attributes[i]
                column = UserItem.CSVImport.ColumnType(i)
                # normalize case for fields with a restricted value set
                skip_validation = False
                if valid:
                    if i == UserItem.CSVImport.ColumnType.AUTH:
                        canonical = UserItem.CSVImport._AUTH_CANONICAL.get(value.lower())
                        if canonical is not None:
                            value = canonical
                        elif value:
                            # Unknown auth value: warn and pass through instead
                            # of raising. TSC's _AUTH_CANONICAL is a hardcoded
                            # list that lags server-side additions; refusing
                            # would block CSV imports against newer servers as
                            # soon as Tableau ships a new auth type. Skip the
                            # allowlist check so the row still validates.
                            # Matches create_user_from_line's warn-and-pass.
                            warnings.warn(
                                f"Unknown auth setting {value!r}; passing through unchanged. "
                                f"Known values: {sorted(UserItem.CSVImport._AUTH_CANONICAL.values())}",
                                stacklevel=2,
                            )
                            skip_validation = True
                    else:
                        value = value.lower()
                # Mask the password column so it never reaches log handlers.
                safe_value = "***" if column == UserItem.CSVImport.ColumnType.PASS else value
                logger.debug(f"column {column.name}: {safe_value}")
                if not skip_validation:
                    UserItem.CSVImport._validate_attribute_value(value, valid, column)

        # Given a restricted set of possible values, confirm the item is in that set
        @staticmethod
        def _validate_attribute_value(item: str, possible_values: list[str], column_type) -> None:
            if item is None or item == "":
                # value can be empty for any column except user, which is checked elsewhere
                return
            if item in possible_values or possible_values == []:
                return
            raise ValueError(f"Invalid value {item} for {column_type}")

        # Inverse of _evaluate_site_role: decompose a site role back to (license, admin_level, publish)
        # for writing the CSV import format.
        @staticmethod
        def _decompose_site_role(site_role: str) -> tuple[str, str, str]:
            """Return (license, admin_level, publish) CSV column values for a given site role.

            Legacy `UserItem.Roles` values are handled in two ways depending on whether
            the server has a sensible modern equivalent:

            - **Mapped to modern equivalents** (row emitted, server accepts): the legacy
              roles `SiteAdministrator`, `Publisher`, `Interactor`, and `ReadOnly` each
              map to the current-model role that best matches their historical intent
              (SiteAdministratorExplorer, ExplorerCanPublish, Explorer, Viewer).
            - **Emitted as `license="Invalid"`** (row rejected server-side with
              USER_CSV_INVALID_LICENSE): the legacy roles `UnlicensedWithPublish`,
              `ViewerWithPublish`, `Guest`, and `SupportUser` have no equivalent in the
              current server model (`RestApiSiteRole` does not accept them on any code
              path). Emitting `"Invalid"` preserves the per-row error semantics callers
              of `bulk_add` had before this refactor, rather than silently coercing
              those users to a valid-but-wrong Unlicensed account.

            Round-trip note: `_evaluate_site_role(*_decompose_site_role(r)) == r` for
            every current-model role. Two label asymmetries: `ServerAdministrator`
            round-trips through the legacy label `SiteAdministrator` (that's the only
            label `_evaluate_site_role` emits for `admin="System"`), and the legacy
            roles above are folded into their modern equivalents by design.
            """
            _role_map: dict[str, tuple[str, str, str]] = {
                "ServerAdministrator": ("Creator", "System", "1"),
                "SiteAdministratorCreator": ("Creator", "Site", "1"),
                "SiteAdministratorExplorer": ("Explorer", "Site", "1"),
                "SiteAdministrator": ("Explorer", "Site", "1"),  # legacy, mapped to SiteAdministratorExplorer
                "Creator": ("Creator", "None", "1"),
                "ExplorerCanPublish": ("Explorer", "None", "1"),
                "Explorer": ("Explorer", "None", "0"),
                "Viewer": ("Viewer", "None", "0"),
                "Unlicensed": ("Unlicensed", "None", "0"),
                "ReadOnly": ("Viewer", "None", "0"),  # legacy, mapped to Viewer
                "Publisher": ("Explorer", "None", "1"),  # legacy, mapped to ExplorerCanPublish
                "Interactor": ("Explorer", "None", "0"),  # legacy, mapped to Explorer
            }
            return _role_map.get(site_role, ("Invalid", "None", "0"))

        # https://help.tableau.com/current/server/en-us/csvguidelines.htm#settings_and_site_roles
        # This logic is hardcoded to match the existing rules for import csv files
        @staticmethod
        def _evaluate_site_role(license_level, admin_level, publisher):
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
                if publisher in ("yes", "true", "1"):
                    if license_level == "creator":
                        site_role = "Creator"
                    elif license_level == "explorer":
                        site_role = "ExplorerCanPublish"
                    else:
                        site_role = "Unlicensed"  # is this the expected outcome?
                else:  # publisher is "no" / "false" / "0" / any other value:
                    if license_level == "explorer" or license_level == "creator":
                        site_role = "Explorer"
                    elif license_level == "viewer":
                        site_role = "Viewer"
                    else:  # if license_level == 'unlicensed'
                        site_role = "Unlicensed"
            if site_role is None:
                site_role = "Unlicensed"
            return site_role

from typing import Callable, Optional, TYPE_CHECKING

from defusedxml.ElementTree import fromstring

from .exceptions import UnpopulatedPropertyError
from .property_decorators import property_not_empty, property_is_enum
from .reference_item import ResourceReference
from .user_item import UserItem

if TYPE_CHECKING:
    from tableauserverclient.server import Pager


class GroupItem:
    tag_name: str = "group"

    class LicenseMode:
        onLogin: str = "onLogin"
        onSync: str = "onSync"

    def __init__(self, name=None, domain_name=None) -> None:
        self._id: Optional[str] = None
        self._license_mode: Optional[str] = None
        self._minimum_site_role: Optional[str] = None
        self._users: Optional[Callable[..., "Pager"]] = None
        self.name: Optional[str] = name
        self.domain_name: Optional[str] = domain_name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__!r})"

    @property
    def domain_name(self) -> Optional[str]:
        return self._domain_name

    @domain_name.setter
    def domain_name(self, value: str) -> None:
        self._domain_name = value

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def license_mode(self) -> Optional[str]:
        return self._license_mode

    @license_mode.setter
    @property_is_enum(LicenseMode)
    def license_mode(self, value: str) -> None:
        self._license_mode = value

    @property
    def minimum_site_role(self) -> Optional[str]:
        return self._minimum_site_role

    @minimum_site_role.setter
    @property_is_enum(UserItem.Roles)
    def minimum_site_role(self, value: str) -> None:
        self._minimum_site_role = value

    @property
    def users(self) -> "Pager":
        if self._users is None:
            error = "Group must be populated with users first."
            raise UnpopulatedPropertyError(error)
        #  Each call to `.users` should create a new pager, this just runs the callable
        return self._users()

    def _set_users(self, users: Callable[..., "Pager"]) -> None:
        self._users = users

    @classmethod
    def from_response(cls, resp, ns) -> list["GroupItem"]:
        all_group_items = list()
        parsed_response = fromstring(resp)
        all_group_xml = parsed_response.findall(".//t:group", namespaces=ns)
        for group_xml in all_group_xml:
            name = group_xml.get("name", None)
            group_item = cls(name)
            group_item._id = group_xml.get("id", None)

            # Domain name is returned in a domain element for some calls
            domain_elem = group_xml.find(".//t:domain", namespaces=ns)
            if domain_elem is not None:
                group_item.domain_name = domain_elem.get("name", None)

            # Import element is returned for both local and AD groups (2020.3+)
            import_elem = group_xml.find(".//t:import", namespaces=ns)
            if import_elem is not None:
                group_item.domain_name = import_elem.get("domainName", None)
                group_item.license_mode = import_elem.get("grantLicenseMode", None)
                group_item.minimum_site_role = import_elem.get("siteRole", None)

            all_group_items.append(group_item)
        return all_group_items

    @staticmethod
    def as_reference(id_: str) -> ResourceReference:
        return ResourceReference(id_, GroupItem.tag_name)

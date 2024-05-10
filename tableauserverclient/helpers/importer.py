from tableauserverclient.models.user_item import UserItem
from typing import List, Tuple
from enum import IntEnum



class UserCSVObject:
    def __init__(self):
        self.name = None
        self.password = None
        self.fullname = None
        self.license_level = None
        self.admin_level = None
        self.publisher = None
        self.email = None
        self.auth = None

    def populate(self, values: List[str]) -> None:
        n_values = len(values)
        self.name = values[0]
        if n_values >= 2:
            self.password = values[1]
        if n_values >= 3:
            self.fullname = values[2]
        if n_values >= 4:
            self.license_level = values[3]
        if n_values >= 5:
            self.admin_level = values[4]
        if n_values >= 6:
            self.publisher = values[5]
        if n_values >= 7:
            self.email = values[6]
        if n_values >= 8:
            self.auth = values[7]

    def to_tsc_user(self) -> UserItem:
        site_role = UserCSVImport.evaluate_site_role(self.license_level, self.admin_level, self.publisher)
        if not site_role:
            raise AttributeError("Site role is required")
        user = UserItem(self.name, site_role, self.auth)
        user.email = self.email
        user.fullname = self.fullname
        return user



class UserCSVImport(object):
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
        # version 3.25 and later
        IDP_NAME = 8
        IDP_ID = 9

        MAX = 7

    # maxColumns = v3.25+ ? 9 : 7

    # Take in a list of strings in expected order
    # and create a user item populated by the given attributes
    @staticmethod
    def create_user_model_from_line(line_values: List[str]) -> "UserItem":
        UserCSVImport._validate_import_line_or_throw(line_values)
        values: List[str] = list(map(lambda x: x.strip(), line_values))
        user = UserItem(values[UserCSVImport.ColumnType.USERNAME])
        if len(values) > 1:
            if len(values) > UserCSVImport.ColumnType.MAX:
                raise ValueError("Too many attributes for user import")
            while len(values) <= UserCSVImport.ColumnType.MAX:
                values.append("")
                
            site_role = UserCSVImport._evaluate_site_role(
                values[UserCSVImport.ColumnType.LICENSE],
                values[UserCSVImport.ColumnType.ADMIN],
                values[UserCSVImport.ColumnType.PUBLISHER],
            )
            if not site_role:
                raise AttributeError("Site role is required")

            user._set_values(
                None, # id 
                values[UserCSVImport.ColumnType.USERNAME],
                site_role,
                None, # last login
                None, # external auth provider id
                values[UserCSVImport.ColumnType.DISPLAY_NAME],
                values[UserCSVImport.ColumnType.EMAIL],
                values[UserCSVImport.ColumnType.AUTH],
                None, # domain name
            )
            if values[UserCSVImport.ColumnType.PASS] is not None:
                user.password = values[UserCSVImport.ColumnType.PASS]
                
            # TODO: implement IDP pools
        return user

    # helper method: validates an import file and if enabled, creates user models for each valid line
    # result: (users[], valid_lines[], (line, error)[])
    @staticmethod
    def process_file_for_import(filepath: str, validate_only=False) -> Tuple[List["UserItem"], List[str], List[Tuple[str, Exception]]]:
        n_failures_accepted = 3
        users: List[UserItem] = []
        failed: List[Tuple[str, Exception]] = []
        valid: List[str] = []
        if not filepath.find("csv"):
            raise ValueError("Only csv files are accepted")

        with open(filepath, encoding="utf-8-sig") as csv_file:
            for line in csv_file:
                if line == "":
                    continue
                
            
                # print only the username, because next value is password
                # logger.debug("> {}".format(line.split(",")))
                try:
                    UserCSVImport._validate_import_line_or_throw(line)
                    if not validate_only:
                        user: UserItem = UserCSVImport.create_user_model_from_line(line)
                        users.append(user)
                    valid.append(" ".join(line))
                except Exception as e:
                    failed.append((" ".join(line), e))
                    if len(failed) > n_failures_accepted and not validate_only:
                        raise ValueError(
                            "More than 3 lines have failed validation. Check the errors and fix your file."
                        )
        return users, valid, failed

    # valid: username, domain/username, username@domain, domain/username@email
    @staticmethod
    def _validate_username_or_throw(username) -> None:
        if username is None or username == "" or username.strip(" ") == "":
            raise AttributeError(_("user.input.name.err.empty"))
        if username.find(" ") >= 0:
            raise AttributeError(_("tabcmd.report.error.user.no_spaces_in_username"))
        at_symbol = username.find("@")

        # f a user name includes an @ character that represents anything other than a domain separator, 
        # you need to refer to the symbol using the hexadecimal format: \0x40
        if at_symbol >= 0:
            username = username[:at_symbol] + "X" + username[at_symbol + 1 :]
            if username.find("@") >= 0:
                raise AttributeError(_("tabcmd.report.error.user_csv.at_char"))
            
            
            
    # If Tableau Server is configured to use Active Directory authentication, there must be a Password column, 
    # but the column itself should be empty. If the server is using local authentication, you must provide passwords for new users. 
    # TODO: check any character/encoding limits for passwords
    @staticmethod
    def _validate_password_or_throw(password) -> None:
        isActiveDirectory = False # TODO: how to get this info?
        isLocalAuth = False # TODO: how to get this info?
        
        if isActiveDirectory and password is not None:
            raise AttributeError("Password must be empty for Active Directory accounts.")
        
        if isLocalAuth and password is None:
            raise AttributeError("Password must be provided for local authentication users.")
        

    # Note: The identifier is required if adding a user to an identity pool that uses Active Directory (or LDAP) identity store.
    # The identifier is optional if adding a user to an identity pool that uses the local identity store.
    @staticmethod
    def _validate_idp_identifier_or_throw(identifier) -> None:
        isActiveDirectory = False # TODO: how to get this info?
        if isActiveDirectory and identifier is not None:
            raise AttributeError("Identifier is required for Active Directory identity stores.")
        

    # Some fields in the import file are restricted to specific values
    # Iterate through each field and validate the given value against hardcoded constraints
    # Values in here are all CASE INSENSITIVE. So the values entered here are all lowercase
    # and all comparisons must force the input text to lowercase as well. 
    @staticmethod
    def _validate_import_line_or_throw(line: str) -> None:
        _valid_attributes: List[List[str]] = [
            [],
            [],
            [],
            ["creator", "explorer", "viewer", "unlicensed"],  # license
            ["system", "site", "none", "no"],  # admin
            ["yes", "true", "1", "no", "false", "0"],  # publisher
            [],
            [UserItem.Auth.SAML.lower(), 
             UserItem.Auth.OpenID.lower(), UserItem.Auth.TableauIDWithMFA.lower(), UserItem.Auth.ServerDefault.lower()],  # auth
            [],
            [],
        ]

        if line is None or line is False or len(line) == 0 or line == "":
            raise AttributeError("Empty line")
        values: List[str] = list(map(str.strip, line.split(",")))
        

        if len(values) > UserCSVImport.ColumnType.MAX:
            raise AttributeError("Too many attributes in line")
        # sometimes usernames are case sensitive
        username = values[UserCSVImport.ColumnType.USERNAME.value]
        # logger.debug("> details - {}".format(username))
        UserItem.validate_username_or_throw(username)
        if len(values) > UserCSVImport.ColumnType.PASS:
            password = values[UserCSVImport.ColumnType.PASS.value]
            UserCSVImport.validate_password_or_throw(password)
        if len(values) > UserCSVImport.ColumnType.IDP_ID:
            UserCSVImport._validate_idp_identifier_or_throw
        for i in range(2, len(values)):
            # logger.debug("column {}: {}".format(UserCSVImport.ColumnType(i).name, values[i]))
            UserCSVImport._validate_attribute_value(values[i], _valid_attributes[i], UserCSVImport.ColumnType(i).name)

    # Given a restricted set of possible values, confirm the item is in that set
    @staticmethod
    def _validate_attribute_value(item: str, possible_values: List[str], column_type) -> None:
        if item is None or item == "":
            # value can be empty for any column except user, which is checked elsewhere
            return
        item = item.strip()
        if item.lower() in possible_values or possible_values == []:
            return
        raise AttributeError(
            "Invalid value {} for {}. Valid values: {}".format(item, column_type, possible_values)
        )

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

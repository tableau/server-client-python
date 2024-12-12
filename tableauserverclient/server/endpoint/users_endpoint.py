import copy
import logging
from typing import Optional

from tableauserverclient.server.query import QuerySet

from .endpoint import QuerysetEndpoint, api
from .exceptions import MissingRequiredFieldError, ServerResponseError
from tableauserverclient.server import RequestFactory, RequestOptions
from tableauserverclient.models import UserItem, WorkbookItem, PaginationItem, GroupItem
from ..pager import Pager

from tableauserverclient.helpers.logging import logger


class Users(QuerysetEndpoint[UserItem]):
    """
    The user resources for Tableau Server are defined in the UserItem class.
    The class corresponds to the user resources you can access using the
    Tableau Server REST API. The user methods are based upon the endpoints for
    users in the REST API and operate on the UserItem class. Only server and
    site administrators can access the user resources.
    """

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/users"

    # Gets all users
    @api(version="2.0")
    def get(self, req_options: Optional[RequestOptions] = None) -> tuple[list[UserItem], PaginationItem]:
        """
        Query all users on the site. Request is paginated and returns a subset of users.
        By default, the request returns the first 100 users on the site.

        Parameters
        ----------
        req_options : Optional[RequestOptions]
            Optional request options to filter and sort the results.

        Returns
        -------
        tuple[list[UserItem], PaginationItem]
            Returns a tuple with a list of UserItem objects and a PaginationItem object.

        Raises
        ------
        ServerResponseError
            code: 400006
            summary: Invalid page number
            detail: The page number is not an integer, is less than one, or is
                greater than the final page number for users at the requested
                page size.

        ServerResponseError
            code: 400007
            summary: Invalid page size
            detail: The page size parameter is not an integer, is less than one.

        ServerResponseError
            code: 403014
            summary: Page size limit exceeded
            detail: The specified page size is larger than the maximum page size

        ServerResponseError
            code: 404000
            summary: Site not found
            detail: The site ID in the URI doesn't correspond to an existing site.

        ServerResponseError
            code: 405000
            summary: Invalid request method
            detail: Request type was not GET.

        Examples
        --------
        >>> import tableauserverclient as TSC
        >>> tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD')
        >>> server = TSC.Server('https://SERVERURL')

        >>> with server.auth.sign_in(tableau_auth):
        >>>     users_page, pagination_item = server.users.get()
        >>>     print("\nThere are {} user on site: ".format(pagination_item.total_available))
        >>>     print([user.name for user in users_page])
        """
        logger.info("Querying all users on site")

        if req_options is None:
            req_options = RequestOptions()
        req_options._all_fields = True

        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_user_items = UserItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_user_items, pagination_item

    # Gets 1 user by id
    @api(version="2.0")
    def get_by_id(self, user_id: str) -> UserItem:
        """
        Query a single user by ID.

        Parameters
        ----------
        user_id : str
            The ID of the user to query.

        Returns
        -------
        UserItem
            The user item that was queried.

        Raises
        ------
        ValueError
            If the user ID is not specified.

        ServerResponseError
            code: 404000
            summary: Site not found
            detail: The site ID in the URI doesn't correspond to an existing site.

        ServerResponseError
            code: 403133
            summary: Query user permissions forbidden
            detail: The user does not have permissions to query user information
                for other users

        ServerResponseError
            code: 404002
            summary: User not found
            detail: The user ID in the URI doesn't correspond to an existing user.

        ServerResponseError
            code: 405000
            summary: Invalid request method
            detail: Request type was not GET.

        Examples
        --------
        >>> user1 = server.users.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
        """
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        logger.info(f"Querying single user (ID: {user_id})")
        url = f"{self.baseurl}/{user_id}"
        server_response = self.get_request(url)
        return UserItem.from_response(server_response.content, self.parent_srv.namespace).pop()

    # Update user
    @api(version="2.0")
    def update(self, user_item: UserItem, password: Optional[str] = None) -> UserItem:
        """
        Modifies information about the specified user.

        If Tableau Server is configured to use local authentication, you can
        update the user's name, email address, password, or site role.

        If Tableau Server is configured to use Active Directory
        authentication, you can change the user's display name (full name),
        email address, and site role. However, if you synchronize the user with
        Active Directory, the display name and email address will be
        overwritten with the information that's in Active Directory.

        For Tableau Cloud, you can update the site role for a user, but you
        cannot update or change a user's password, user name (email address),
        or full name.

        Parameters
        ----------
        user_item : UserItem
            The user item to update.

        password : Optional[str]
            The new password for the user.

        Returns
        -------
        UserItem
            The user item that was updated.

        Raises
        ------
        MissingRequiredFieldError
            If the user item is missing an ID.

        Examples
        --------
        >>> user = server.users.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
        >>> user.fullname = 'New Full Name'
        >>> updated_user = server.users.update(user)

        """
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        url = f"{self.baseurl}/{user_item.id}"
        update_req = RequestFactory.User.update_req(user_item, password)
        server_response = self.put_request(url, update_req)
        logger.info(f"Updated user item (ID: {user_item.id})")
        updated_item = copy.copy(user_item)
        return updated_item._parse_common_tags(server_response.content, self.parent_srv.namespace)

    # Delete 1 user by id
    @api(version="2.0")
    def remove(self, user_id: str, map_assets_to: Optional[str] = None) -> None:
        """
        Removes a user from the site. You can also specify a user to map the
        assets to when you remove the user.

        Parameters
        ----------
        user_id : str
            The ID of the user to remove.

        map_assets_to : Optional[str]
            The ID of the user to map the assets to when you remove the user.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the user ID is not specified.

        Examples
        --------
        >>> server.users.remove('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
        """
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{user_id}"
        if map_assets_to is not None:
            url += f"?mapAssetsTo={map_assets_to}"
        self.delete_request(url)
        logger.info(f"Removed single user (ID: {user_id})")

    # Add new user to site
    @api(version="2.0")
    def add(self, user_item: UserItem) -> UserItem:
        """
        Adds the user to the site.

        To add a new user to the site you need to first create a new user_item
        (from UserItem class). When you create a new user, you specify the name
        of the user and their site role. For Tableau Cloud, you also specify
        the auth_setting attribute in your request. When you add user to
        Tableau Cloud, the name of the user must be the email address that is
        used to sign in to Tableau Cloud. After you add a user, Tableau Cloud
        sends the user an email invitation. The user can click the link in the
        invitation to sign in and update their full name and password.

        Parameters
        ----------
        user_item : UserItem
            The user item to add to the site.

        Returns
        -------
        UserItem
            The user item that was added to the site with attributes from the
            site populated.

        Raises
        ------
        ValueError
            If the user item is missing a name

        ValueError
            If the user item is missing a site role

        ServerResponseError
            code: 400000
            summary: Bad Request
            detail: The content of the request body is missing or incomplete, or
                contains malformed XML.

        ServerResponseError
            code: 400003
            summary: Bad Request
            detail: The user authentication setting ServerDefault is not
                supported for you site. Try again using TableauIDWithMFA instead.

        ServerResponseError
            code: 400013
            summary: Invalid site role
            detail: The value of the siteRole attribute must be Explorer,
                ExplorerCanPublish, SiteAdministratorCreator,
                SiteAdministratorExplorer, Unlicensed, or Viewer.

        ServerResponseError
            code: 404000
            summary: Site not found
            detail: The site ID in the URI doesn't correspond to an existing site.

        ServerResponseError
            code: 404002
            summary: User not found
            detail: The server is configured to use Active Directory for
                authentication, and the username specified in the request body
                doesn't match an existing user in Active Directory.

        ServerResponseError
            code: 405000
            summary: Invalid request method
            detail: Request type was not POST.

        ServerResponseError
            code: 409000
            summary: User conflict
            detail: The specified user already exists on the site.

        ServerResponseError
            code: 409005
            summary: Guest user conflict
            detail: The Tableau Server API doesn't allow adding a user with the
                guest role to a site.


        Examples
        --------
        >>> import tableauserverclient as TSC
        >>> server = TSC.Server('https://SERVERURL')
        >>> # Login to the server

        >>> new_user = TSC.UserItem(name='new_user', site_role=TSC.UserItem.Role.Unlicensed)
        >>> new_user = server.users.add(new_user)

        """
        url = self.baseurl
        logger.info(f"Add user {user_item.name}")
        add_req = RequestFactory.User.add_req(user_item)
        server_response = self.post_request(url, add_req)
        logger.info(server_response)
        new_user = UserItem.from_response(server_response.content, self.parent_srv.namespace).pop()
        logger.info(f"Added new user (ID: {new_user.id})")
        return new_user

    # Add new users to site. This does not actually perform a bulk action, it's syntactic sugar
    @api(version="2.0")
    def add_all(self, users: list[UserItem]):
        created = []
        failed = []
        for user in users:
            try:
                result = self.add(user)
                created.append(result)
            except Exception as e:
                failed.append(user)
        return created, failed

    # helping the user by parsing a file they could have used to add users through the UI
    # line format: Username [required], password, display name, license, admin, publish
    @api(version="2.0")
    def create_from_file(self, filepath: str) -> tuple[list[UserItem], list[tuple[UserItem, ServerResponseError]]]:
        created = []
        failed = []
        if not filepath.find("csv"):
            raise ValueError("Only csv files are accepted")

        with open(filepath) as csv_file:
            csv_file.seek(0)  # set to start of file in case it has been read earlier
            line: str = csv_file.readline()
            while line and line != "":
                user: UserItem = UserItem.CSVImport.create_user_from_line(line)
                try:
                    print(user)
                    result = self.add(user)
                    created.append(result)
                except ServerResponseError as serverError:
                    print("failed")
                    failed.append((user, serverError))
                line = csv_file.readline()
        return created, failed

    # Get workbooks for user
    @api(version="2.0")
    def populate_workbooks(self, user_item: UserItem, req_options: Optional[RequestOptions] = None) -> None:
        """
        Returns information about the workbooks that the specified user owns
        and has Read (view) permissions for.

        This method retrieves the workbook information for the specified user.
        The REST API is designed to return only the information you ask for
        explicitly. When you query for all the users, the workbook information
        for each user is not included. Use this method to retrieve information
        about the workbooks that the user owns or has Read (view) permissions.
        The method adds the list of workbooks to the user item object
        (user_item.workbooks).

        Parameters
        ----------
        user_item : UserItem
            The user item to populate workbooks for.

        req_options : Optional[RequestOptions]
            Optional request options to filter and sort the results.

        Returns
        -------
        None

        Raises
        ------
        MissingRequiredFieldError
            If the user item is missing an ID.

        Examples
        --------
        >>> user = server.users.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
        >>> server.users.populate_workbooks(user)
        >>> for wb in user.workbooks:
        >>>     print(wb.name)
        """
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        def wb_pager():
            return Pager(lambda options: self._get_wbs_for_user(user_item, options), req_options)

        user_item._set_workbooks(wb_pager)

    def _get_wbs_for_user(
        self, user_item: UserItem, req_options: Optional[RequestOptions] = None
    ) -> tuple[list[WorkbookItem], PaginationItem]:
        url = f"{self.baseurl}/{user_item.id}/workbooks"
        server_response = self.get_request(url, req_options)
        logger.info(f"Populated workbooks for user (ID: {user_item.id})")
        workbook_item = WorkbookItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        return workbook_item, pagination_item

    def populate_favorites(self, user_item: UserItem) -> None:
        """
        Populate the favorites for the user.

        Parameters
        ----------
        user_item : UserItem
            The user item to populate favorites for.

        Returns
        -------
        None

        Examples
        --------
        >>> import tableauserverclient as TSC
        >>> server = TSC.Server('https://SERVERURL')
        >>> # Login to the server

        >>> user = server.users.get_by_id('9f9e9d9c-8b8a-8f8e-7d7c-7b7a6f6d6e6d')
        >>> server.users.populate_favorites(user)
        >>> for obj_type, items in user.favorites.items():
        >>>     print(f"Favorites for {obj_type}:")
        >>>     for item in items:
        >>>         print(item.name)
        """
        self.parent_srv.favorites.get(user_item)

    # Get groups for user
    @api(version="3.7")
    def populate_groups(self, user_item: UserItem, req_options: Optional[RequestOptions] = None) -> None:
        """
        Populate the groups for the user.

        Parameters
        ----------
        user_item : UserItem
            The user item to populate groups for.

        req_options : Optional[RequestOptions]
            Optional request options to filter and sort the results.

        Returns
        -------
        None

        Raises
        ------
        MissingRequiredFieldError
            If the user item is missing an ID.

        Examples
        --------
        >>> server.users.populate_groups(user)
        >>> for group in user.groups:
        >>>     print(group.name)
        """
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        def groups_for_user_pager():
            return Pager(
                lambda options: self._get_groups_for_user(user_item, options),
                req_options,
            )

        user_item._set_groups(groups_for_user_pager)

    def _get_groups_for_user(
        self, user_item: UserItem, req_options: Optional[RequestOptions] = None
    ) -> tuple[list[GroupItem], PaginationItem]:
        url = f"{self.baseurl}/{user_item.id}/groups"
        server_response = self.get_request(url, req_options)
        logger.info(f"Populated groups for user (ID: {user_item.id})")
        group_item = GroupItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        return group_item, pagination_item

    def filter(self, *invalid, page_size: Optional[int] = None, **kwargs) -> QuerySet[UserItem]:
        """
        Queries the Tableau Server for items using the specified filters. Page
        size can be specified to limit the number of items returned in a single
        request. If not specified, the default page size is 100. Page size can
        be an integer between 1 and 1000.

        No positional arguments are allowed. All filters must be specified as
        keyword arguments. If you use the equality operator, you can specify it
        through <field_name>=<value>. If you want to use a different operator,
        you can specify it through <field_name>__<operator>=<value>. Field
        names can either be in snake_case or camelCase.

        This endpoint supports the following fields and operators:


        domain_name=...
        domain_name__in=...
        friendly_name=...
        friendly_name__in=...
        is_local=...
        last_login=...
        last_login__gt=...
        last_login__gte=...
        last_login__lt=...
        last_login__lte=...
        luid=...
        luid__in=...
        name__cieq=...
        name=...
        name__in=...
        site_role=...
        site_role__in=...
        """

        return super().filter(*invalid, page_size=page_size, **kwargs)

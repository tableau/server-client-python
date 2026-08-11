from functools import partial
import json
from pathlib import Path
from typing import TYPE_CHECKING
from collections.abc import Iterable

from tableauserverclient.models.connection_item import ConnectionItem
from tableauserverclient.models.pagination_item import PaginationItem
from tableauserverclient.models.permissions_item import PermissionsRule
from tableauserverclient.models.revision_item import RevisionItem
from tableauserverclient.models.virtual_connection_item import VirtualConnectionItem
from tableauserverclient.server.request_factory import RequestFactory
from tableauserverclient.server.request_options import RequestOptions
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api
from tableauserverclient.server.endpoint.permissions_endpoint import _PermissionsEndpoint
from tableauserverclient.server.endpoint.resource_tagger import TaggingMixin
from tableauserverclient.server.pager import Pager

if TYPE_CHECKING:
    from tableauserverclient.server import Server


class VirtualConnections(QuerysetEndpoint[VirtualConnectionItem], TaggingMixin):
    """Access virtual connection resources on Tableau Server.

    Using this endpoint you can list virtual connections on a site, retrieve
    a specific virtual connection's JSON content definition, publish new
    virtual connections, update metadata or the underlying database
    connection details, manage revisions, and control permissions and tags.

    The virtual connection resources are represented by the
    ``VirtualConnectionItem`` class in ``tableauserverclient.models``.

    REST API: `Virtual Connections Methods <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm>`_
    """

    def __init__(self, parent_srv: "Server") -> None:
        super().__init__(parent_srv)
        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/virtualConnections"

    @api(version="3.18")
    def get(self, req_options: RequestOptions | None = None) -> tuple[list[VirtualConnectionItem], PaginationItem]:
        """Return a list of virtual connections on the site.

        REST API: `List Virtual Connections <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm#list_virtual_connections>`_

        Parameters
        ----------
        req_options : RequestOptions, optional
            Request options such as page size and filters.

        Returns
        -------
        tuple[list[VirtualConnectionItem], PaginationItem]
            A pair of the page of virtual connections and pagination info.

        Examples
        --------
        >>> all_vcs, pagination = server.virtual_connections.get()
        >>> for vc in all_vcs:
        ...     print(vc.id, vc.name)
        """
        server_response = self.get_request(self.baseurl, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        virtual_connections = VirtualConnectionItem.from_response(server_response.content, self.parent_srv.namespace)
        return virtual_connections, pagination_item

    @api(version="3.18")
    def populate_connections(self, virtual_connection: VirtualConnectionItem) -> VirtualConnectionItem:
        """Populate the database connections for a virtual connection.

        After calling this method, iterate ``virtual_connection.connections``
        to access the underlying ``ConnectionItem`` objects.

        REST API: `List Virtual Connection Database Connections <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm#list_virtual_connection_database_connections>`_

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection to populate connections for.

        Returns
        -------
        VirtualConnectionItem
            The same item, with ``connections`` now available for iteration.

        Examples
        --------
        >>> server.virtual_connections.populate_connections(vc)
        >>> for conn in vc.connections:
        ...     print(conn.id, conn.server_address)
        """

        def _connection_fetcher():
            return Pager(partial(self._get_virtual_database_connections, virtual_connection))

        virtual_connection._connections = _connection_fetcher
        return virtual_connection

    def _get_virtual_database_connections(
        self, virtual_connection: VirtualConnectionItem, req_options: RequestOptions | None = None
    ) -> tuple[list[ConnectionItem], PaginationItem]:
        server_response = self.get_request(f"{self.baseurl}/{virtual_connection.id}/connections", req_options)
        connections = ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)

        return connections, pagination_item

    @api(version="3.18")
    def update_connection_db_connection(
        self, virtual_connection: str | VirtualConnectionItem, connection: ConnectionItem
    ) -> ConnectionItem:
        """Update the database connection details inside a virtual connection.

        REST API: `Update Virtual Connection Database Connection <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm#update_virtual_connection_database_connection>`_

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem or str
            The parent virtual connection, or its ID.

        connection : ConnectionItem
            The connection object with updated fields (server address, port,
            username, etc.). ``connection.id`` must be set.

        Returns
        -------
        ConnectionItem
            The updated connection as returned by the server.

        Examples
        --------
        >>> server.virtual_connections.populate_connections(vc)
        >>> conn = list(vc.connections)[0]
        >>> conn.server_address = 'new-db-server.example.com'
        >>> updated_conn = server.virtual_connections.update_connection_db_connection(vc, conn)
        """
        vconn_id = getattr(virtual_connection, "id", virtual_connection)
        url = f"{self.baseurl}/{vconn_id}/connections/{connection.id}/modify"
        xml_request = RequestFactory.VirtualConnection.update_db_connection(connection)
        server_response = self.put_request(url, xml_request)
        return ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.23")
    def get_by_id(self, virtual_connection: str | VirtualConnectionItem) -> VirtualConnectionItem:
        """Return the details of a specific virtual connection.

        The returned item has its ``content`` attribute populated with the
        virtual connection's JSON definition.

        REST API: `Get Virtual Connection <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm#get_virtual_connection>`_

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem or str
            The virtual connection, or its ID.

        Returns
        -------
        VirtualConnectionItem
            The virtual connection with ``content`` populated.

        Examples
        --------
        >>> vc = server.virtual_connections.get_by_id('1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d')
        >>> print(vc.name, vc.content)
        """
        if isinstance(virtual_connection, VirtualConnectionItem):
            vconn_id = virtual_connection.id or ""
        else:
            vconn_id = virtual_connection
        url = f"{self.baseurl}/{vconn_id}"
        server_response = self.get_request(url)
        result = VirtualConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        # The Get Virtual Connection response omits the `id` attribute on the
        # <virtualConnection> element (server-side response builder never calls
        # setId). Stamp it back from the request path so downstream calls that
        # need result.id (add_tags, delete_tags, update_tags) work.
        if result._id is None:
            result._id = vconn_id
        return result

    @api(version="3.23")
    def download(self, virtual_connection: str | VirtualConnectionItem) -> str:
        """Return the JSON definition of a virtual connection as a string.

        Convenience wrapper around ``get_by_id`` that returns just the
        serialized ``content``.

        REST API: `Get Virtual Connection <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm#get_virtual_connection>`_

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem or str
            The virtual connection, or its ID.

        Returns
        -------
        str
            The virtual connection JSON content, serialized.

        Examples
        --------
        >>> content_json = server.virtual_connections.download(vc)
        >>> with open('vc_backup.json', 'w') as f:
        ...     f.write(content_json)
        """
        v_conn = self.get_by_id(virtual_connection)
        return json.dumps(v_conn.content)

    @api(version="3.23")
    def update(self, virtual_connection: VirtualConnectionItem) -> VirtualConnectionItem:
        """Update virtual connection metadata (name, project, owner, certification, etc.).

        This does not modify the underlying JSON content of the virtual
        connection; use ``update_connection_db_connection`` for that.

        REST API: `Update Virtual Connection <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm#update_virtual_connection>`_

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection to update. Must have a valid ``id``.

        Returns
        -------
        VirtualConnectionItem
            The updated virtual connection as returned by the server.

        Examples
        --------
        >>> vc.is_certified = True
        >>> vc.certification_note = 'Approved by data team'
        >>> updated_vc = server.virtual_connections.update(vc)
        """
        url = f"{self.baseurl}/{virtual_connection.id}"
        xml_request = RequestFactory.VirtualConnection.update(virtual_connection)
        server_response = self.put_request(url, xml_request)
        return VirtualConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.23")
    def get_revisions(
        self, virtual_connection: VirtualConnectionItem, req_options: RequestOptions | None = None
    ) -> tuple[list[RevisionItem], PaginationItem]:
        """Return a list of revisions for a virtual connection.

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection whose revisions to retrieve.

        req_options : RequestOptions, optional
            Request options such as page size.

        Returns
        -------
        tuple[list[RevisionItem], PaginationItem]
            A pair of the page of revisions and pagination info.

        Examples
        --------
        >>> revisions, pagination = server.virtual_connections.get_revisions(vc)
        >>> for rev in revisions:
        ...     print(rev.revision_number, rev.created_at)
        """
        server_response = self.get_request(f"{self.baseurl}/{virtual_connection.id}/revisions", req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        revisions = RevisionItem.from_response(server_response.content, self.parent_srv.namespace, virtual_connection)
        return revisions, pagination_item

    @api(version="3.23")
    def download_revision(self, virtual_connection: VirtualConnectionItem, revision_number: int) -> str:
        """Return the JSON definition of a specific revision as a string.

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection whose revision to download.

        revision_number : int
            The revision number to download.

        Returns
        -------
        str
            The virtual connection JSON content at that revision, serialized.

        Examples
        --------
        >>> revisions, _ = server.virtual_connections.get_revisions(vc)
        >>> json_str = server.virtual_connections.download_revision(vc, revisions[0].revision_number)
        """
        url = f"{self.baseurl}/{virtual_connection.id}/revisions/{revision_number}"
        server_response = self.get_request(url)
        virtual_connection = VirtualConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return json.dumps(virtual_connection.content)

    @api(version="3.23")
    def delete(self, virtual_connection: VirtualConnectionItem | str) -> None:
        """Delete a virtual connection from the site.

        REST API: `Delete Virtual Connection <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm#delete_virtual_connection>`_

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem or str
            The virtual connection, or its ID.

        Returns
        -------
        None

        Examples
        --------
        >>> server.virtual_connections.delete(vc.id)
        """
        vconn_id = getattr(virtual_connection, "id", virtual_connection)
        self.delete_request(f"{self.baseurl}/{vconn_id}")

    @api(version="3.23")
    def publish(
        self,
        virtual_connection: VirtualConnectionItem,
        virtual_connection_content: str,
        mode: str = "CreateNew",
        publish_as_draft: bool = False,
    ) -> VirtualConnectionItem:
        """Publish a virtual connection to the server.

        For the virtual_connection object, name, project_id, and owner_id are
        required.

        The virtual_connection_content can be a json string or a file path to a
        json file.

        The mode can be "CreateNew" or "Overwrite". If mode is
        "Overwrite" and the virtual connection already exists, it will be
        overwritten.

        If publish_as_draft is True, the virtual connection will be published
        as a draft, and the id of the draft will be on the response object.

        REST API: `Publish Virtual Connection <https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_virtual_connections.htm#publish_virtual_connection>`_

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection to publish. Must have ``name``,
            ``project_id``, and ``owner_id`` set.

        virtual_connection_content : str
            The virtual connection JSON definition, either as a JSON string
            or as a path to a JSON file on disk.

        mode : str
            ``"CreateNew"`` (default) or ``"Overwrite"``. Use ``"Overwrite"``
            to replace an existing virtual connection.

        publish_as_draft : bool
            If ``True``, publish as a draft. The id on the returned item
            will be the draft's id. Default is ``False``.

        Returns
        -------
        VirtualConnectionItem
            The published virtual connection as returned by the server.

        Raises
        ------
        ValueError
            If ``mode`` is not ``"CreateNew"`` or ``"Overwrite"``.
        RuntimeError
            If ``virtual_connection_content`` is neither valid JSON nor a
            path to an existing file.

        Examples
        --------
        >>> new_vc = TSC.VirtualConnectionItem('My Virtual Connection')
        >>> new_vc.project_id = project.id
        >>> new_vc.owner_id = user.id
        >>> published = server.virtual_connections.publish(
        ...     new_vc, '/path/to/vc_definition.json', mode='CreateNew'
        ... )
        >>> print(published.id)
        """
        try:
            json.loads(virtual_connection_content)
        except json.JSONDecodeError:
            file = Path(virtual_connection_content)
            if not file.exists():
                raise RuntimeError(f"{virtual_connection_content} is not valid json nor an existing file path")
            content = file.read_text()
        else:
            content = virtual_connection_content

        if mode not in ["CreateNew", "Overwrite"]:
            raise ValueError(f"Invalid mode: {mode}")
        overwrite = mode == "Overwrite"

        url = f"{self.baseurl}?overwrite={str(overwrite).lower()}&publishAsDraft={str(publish_as_draft).lower()}"
        xml_request = RequestFactory.VirtualConnection.publish(virtual_connection, content)
        server_response = self.post_request(url, xml_request)
        return VirtualConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.22")
    def populate_permissions(self, virtual_connection: VirtualConnectionItem) -> None:
        """Populate the permissions for a virtual connection.

        After calling this method, iterate ``virtual_connection.permissions``
        to access the ``PermissionsRule`` objects.

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection to populate permissions for.

        Returns
        -------
        None
            Permissions are populated on ``virtual_connection.permissions``.

        Examples
        --------
        >>> server.virtual_connections.populate_permissions(vc)
        >>> for rule in vc.permissions:
        ...     print(rule)
        """
        self._permissions.populate(virtual_connection)

    @api(version="3.22")
    def add_permissions(
        self, virtual_connection: VirtualConnectionItem, rules: list[PermissionsRule]
    ) -> list[PermissionsRule]:
        """Add or update permissions on a virtual connection.

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection to update permissions on.

        rules : list[PermissionsRule]
            The permission rules to apply.

        Returns
        -------
        list[PermissionsRule]
            The updated list of permission rules as returned by the server.

        Examples
        --------
        >>> permission = TSC.PermissionsRule(
        ...     TSC.UserItem.as_reference(user.id),
        ...     {'Connect': 'Allow'}
        ... )
        >>> server.virtual_connections.add_permissions(vc, [permission])
        """
        return self._permissions.update(virtual_connection, rules)

    @api(version="3.22")
    def delete_permission(self, virtual_connection: VirtualConnectionItem, permission_rule: PermissionsRule) -> None:
        """Remove a specific permission from a virtual connection.

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection to remove the permission from.

        permission_rule : PermissionsRule
            The permission rule to remove.

        Returns
        -------
        None

        Examples
        --------
        >>> server.virtual_connections.delete_permission(vc, permission_rule)
        """
        return self._permissions.delete(virtual_connection, permission_rule)

    @api(version="3.23")
    def add_tags(self, virtual_connection: VirtualConnectionItem | str, tags: Iterable[str] | str) -> set[str]:
        """Add one or more tags to a virtual connection.

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem or str
            The virtual connection to tag, or its ID.

        tags : str or iterable of str
            A single tag or an iterable of tag strings.

        Returns
        -------
        set[str]
            The full tag set on the virtual connection after the add,
            as returned by the server.

        Examples
        --------
        >>> server.virtual_connections.add_tags(vc, ['finance', 'certified'])
        """
        return super().add_tags(virtual_connection, tags)

    @api(version="3.23")
    def delete_tags(self, virtual_connection: VirtualConnectionItem | str, tags: Iterable[str] | str) -> None:
        """Remove one or more tags from a virtual connection.

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem or str
            The virtual connection to remove tags from, or its ID.

        tags : str or iterable of str
            A single tag or an iterable of tag strings.

        Returns
        -------
        None

        Examples
        --------
        >>> server.virtual_connections.delete_tags(vc, 'finance')
        """
        return super().delete_tags(virtual_connection, tags)

    @api(version="3.30")
    def update_tags(self, virtual_connection: VirtualConnectionItem) -> None:
        """Push local tag edits to the server as add / delete calls.

        Computes the diff between ``virtual_connection.tags`` (mutated
        locally) and ``virtual_connection._initial_tags`` (captured at
        parse time), then issues `Add Tags to Virtual Connection` and
        `Delete Tag from Virtual Connection` calls to bring the server
        state in line.

        Requires Tableau Server 2026.2 / Cloud April 2026 or later (REST
        API 3.30+): earlier server versions do not populate tags on the
        response, so ``_initial_tags`` is empty and every tag on the item
        would be treated as new.

        Parameters
        ----------
        virtual_connection : VirtualConnectionItem
            The virtual connection whose tags to synchronize. Must have
            been fetched via `get` / `get_by_id` (which populates
            ``_initial_tags``) then edited via ``virtual_connection.tags``.

        Returns
        -------
        None

        Examples
        --------
        >>> vc = server.virtual_connections.get_by_id(vc_id)
        >>> vc.tags.add('finance')
        >>> vc.tags.discard('stale')
        >>> server.virtual_connections.update_tags(vc)
        """
        return super().update_tags(virtual_connection)

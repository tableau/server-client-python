"""Structural protocols for TSC item classes.

These protocols define the minimum interface shared across TSC resource items.
They use ``typing.Protocol`` (structural subtyping) rather than an ABC so that
existing classes do not need to modify their inheritance chain to satisfy the
contract.  Any class that exposes the required attributes satisfies the
protocol automatically -- no explicit inheritance is required or desired.
"""

from __future__ import annotations

import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class TableauItem(Protocol):
    """Structural interface satisfied by TSC resource item classes that carry an id and a name.

    Structurally satisfied by the primary content classes (WorkbookItem,
    DatasourceItem, ViewItem, FlowItem, MetricItem), user/group/project/schedule/
    site/webhook/custom-view/table/database/virtual-connection items, and any
    other class exposing ``id`` and ``name``. Items without a ``name`` attribute
    (e.g. TaskItem, DataAlertItem) do NOT satisfy this protocol.

    Notes
    -----
    ``id`` and ``name`` are declared as read-only ``@property`` so that concrete
    classes with narrower return types (e.g. ``name: str``) satisfy the protocol
    under mypy's covariant property checking. Plain writable instance attributes
    also satisfy a read-only property protocol.

    ``runtime_checkable`` enables ``isinstance(obj, TableauItem)`` checks at
    runtime, but these only verify attribute *presence*, not types or
    signatures. Full static checking requires a type checker such as mypy.
    ``issubclass`` is NOT supported for data-attribute Protocols and will raise
    ``TypeError`` -- use ``isinstance`` on an instance instead.

    ``from_response`` is intentionally excluded from this protocol because the
    primary content classes have divergent signatures (different ``resp``
    parameter types, extra parameters) that cannot be unified without widening
    to ``Any``.
    """

    @property
    def id(self) -> str | None: ...

    @property
    def name(self) -> str | None: ...


@runtime_checkable
class OwnedItem(TableauItem, Protocol):
    """Structural interface for TSC items that carry an owner reference.

    Structurally satisfied by WorkbookItem, DatasourceItem, ViewItem,
    FlowItem, ProjectItem, and MetricItem -- every item class that exposes
    an ``owner_id`` attribute.  Extends ``TableauItem``.

    No concrete class needs to explicitly inherit from OwnedItem.  Protocol
    structural subtyping means any class that exposes the required attribute
    satisfies the protocol implicitly.

    ``owner_id`` is declared as a read-only ``@property`` so that ViewItem
    (whose owner is determined by its parent workbook and is not independently
    writable) satisfies the protocol.  Plain writable instance attributes on
    other item classes also satisfy a read-only property protocol.
    """

    @property
    def owner_id(self) -> str | None: ...


@runtime_checkable
class TaggableItem(TableauItem, Protocol):
    """Structural interface for TSC items that carry a mutable tag set.

    Structurally satisfied by WorkbookItem, DatasourceItem, ViewItem,
    FlowItem, and MetricItem.  ProjectItem is intentionally excluded because
    it does not expose a ``tags`` attribute.
    """

    tags: set[str]


@runtime_checkable
class ContentItem(OwnedItem, TaggableItem, Protocol):
    """Extended interface for publishable content items.

    Composes OwnedItem (carries ``owner_id``), TaggableItem (carries ``tags``),
    and adds server-assigned timestamps.  Structurally satisfied by
    WorkbookItem, DatasourceItem, ViewItem, FlowItem, and MetricItem.

    No concrete class needs to explicitly inherit from ContentItem.  Protocol
    structural subtyping means any class that exposes all required attributes
    satisfies the protocol implicitly, avoiding mypy [override] errors that
    arise when a Protocol with plain writable annotations is explicitly
    subclassed by a class that implements them as read-only properties.
    """

    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None

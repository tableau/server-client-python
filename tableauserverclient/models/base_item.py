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
class BaseItem(Protocol):
    """Structural interface satisfied by all primary TSC resource item classes.

    Every TSC item class (WorkbookItem, DatasourceItem, ViewItem, FlowItem,
    UserItem, ProjectItem, ScheduleItem, GroupItem) exposes at minimum an ``id``
    attribute and a ``name`` attribute.  This protocol captures that minimal
    shared surface.

    ``id`` and ``name`` are declared as plain Protocol attributes (not
    ``@property``) so that concrete classes may implement them as either plain
    instance attributes or read-only properties.  Protocol structural subtyping
    means no concrete class needs to list ``BaseItem`` in its MRO -- any class
    with matching attributes satisfies the protocol implicitly.

    Notes
    -----
    ``runtime_checkable`` enables ``isinstance(obj, BaseItem)`` checks at
    runtime, but these only verify attribute *presence*, not types or
    signatures.  Full static checking requires a type checker such as mypy.

    ``from_response`` is intentionally excluded from this protocol because the
    four primary content classes have divergent signatures (different ``resp``
    parameter types, extra parameters) that cannot be unified without widening
    to ``Any``.
    """

    id: str | None
    name: str | None


@runtime_checkable
class OwnedItem(BaseItem, Protocol):
    """Structural interface for TSC items that carry an owner reference.

    Structurally satisfied by WorkbookItem, DatasourceItem, ViewItem,
    FlowItem, ProjectItem, and MetricItem -- every item class that exposes
    an ``owner_id`` attribute.

    No concrete class needs to explicitly inherit from OwnedItem.  Protocol
    structural subtyping means any class that exposes the required attribute
    satisfies the protocol implicitly.
    """

    owner_id: str | None


@runtime_checkable
class TaggableItem(BaseItem, Protocol):
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

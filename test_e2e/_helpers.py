"""Shared helpers for e2e tests."""

import uuid


def _unique(prefix: str) -> str:
    """Generate a name unique to this test run.

    Every user/group/project name used by an e2e test must be per-run to
    avoid 409 conflicts when: (a) two runs execute against the same site
    in parallel, or (b) a prior run crashed after `create` but before the
    `finally` block removed it.
    """
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

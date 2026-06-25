import zipfile
from pathlib import Path
import pytest

pytestmark = pytest.mark.packaging


def _find_wheel():
    wheels = list(Path("dist").glob("tableauserverclient-*.whl"))
    if not wheels:
        pytest.skip("No wheel in dist/ -- run 'python -m build --wheel' first")
    return max(wheels, key=lambda p: p.stat().st_mtime)


def test_wheel_only_tableauserverclient_at_root():
    with zipfile.ZipFile(_find_wheel()) as whl:
        top_dirs = {n.split("/")[0] for n in whl.namelist() if "/" in n}
    non_dist_info = {d for d in top_dirs if not d.endswith(".dist-info") and not d.endswith(".data")}
    assert non_dist_info == {"tableauserverclient"}, f"Unexpected top-level entries: {non_dist_info}"

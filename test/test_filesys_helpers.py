import os
from pathlib import Path
from io import BytesIO
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pytest

from tableauserverclient.filesys_helpers import get_file_object_size, get_file_type

TEST_ASSET_DIR = Path(__file__).parent / "assets"


def test_get_file_size_returns_correct_size() -> None:
    target_size = 1000  # bytes

    with BytesIO() as f:
        f.seek(target_size - 1)
        f.write(b"\0")
        file_size = get_file_object_size(f)

    assert file_size == target_size


def test_get_file_size_returns_zero_for_empty_file() -> None:
    with BytesIO() as f:
        file_size = get_file_object_size(f)

    assert file_size == 0


def test_get_file_size_coincides_with_built_in_method() -> None:
    asset_path = TEST_ASSET_DIR / "SampleWB.twbx"
    target_size = os.path.getsize(asset_path)
    with open(asset_path, "rb") as f:
        file_size = get_file_object_size(f)

    assert file_size == target_size


def test_get_file_type_identifies_a_zip_file() -> None:
    with BytesIO() as file_object:
        with ZipFile(file_object, "w") as zf:
            with BytesIO() as stream:
                stream.write(b"This is a zip file")
                zf.writestr("dummy_file", stream.getbuffer())
                file_object.seek(0)
                file_type = get_file_type(file_object)

    assert file_type == "zip"


def test_get_file_type_identifies_tdsx_as_zip_file() -> None:
    with open(TEST_ASSET_DIR / "World Indicators.tdsx", "rb") as file_object:
        file_type = get_file_type(file_object)
    assert file_type == "zip"


def test_get_file_type_identifies_twbx_as_zip_file() -> None:
    with open(TEST_ASSET_DIR / "SampleWB.twbx", "rb") as file_object:
        file_type = get_file_type(file_object)
    assert file_type == "zip"


def test_get_file_type_identifies_xml_file() -> None:
    root = ET.Element("root")
    child = ET.SubElement(root, "child")
    child.text = "This is a child element"
    etree = ET.ElementTree(root)

    with BytesIO() as file_object:
        etree.write(file_object, encoding="utf-8", xml_declaration=True)

        file_object.seek(0)
        file_type = get_file_type(file_object)

    assert file_type == "xml"


def test_get_file_type_identifies_tds_as_xml_file() -> None:
    with open(TEST_ASSET_DIR / "World Indicators.tds", "rb") as file_object:
        file_type = get_file_type(file_object)
    assert file_type == "xml"


def test_get_file_type_identifies_twb_as_xml_file() -> None:
    with open(TEST_ASSET_DIR / "RESTAPISample.twb", "rb") as file_object:
        file_type = get_file_type(file_object)
    assert file_type == "xml"


def test_get_file_type_identifies_hyper_file() -> None:
    with open(TEST_ASSET_DIR / "World Indicators.hyper", "rb") as file_object:
        file_type = get_file_type(file_object)
    assert file_type == "hyper"


def test_get_file_type_identifies_tde_file() -> None:
    asset_path = TEST_ASSET_DIR / "Data" / "Tableau Samples" / "World Indicators.tde"
    with open(asset_path, "rb") as file_object:
        file_type = get_file_type(file_object)
    assert file_type == "tde"


def test_get_file_type_handles_unknown_file_type() -> None:
    # Create a dummy png file
    with BytesIO() as file_object:
        png_signature = bytes.fromhex("89504E470D0A1A0A")
        file_object.write(png_signature)
        file_object.seek(0)

        with pytest.raises(ValueError):
            get_file_type(file_object)

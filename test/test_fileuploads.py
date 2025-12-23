import contextlib
import io
import os
from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.config import BYTES_PER_MB, config

TEST_ASSET_DIR = Path(__file__).parent / "assets"
FILEUPLOAD_INITIALIZE = TEST_ASSET_DIR / "fileupload_initialize.xml"
FILEUPLOAD_APPEND = TEST_ASSET_DIR / "fileupload_append.xml"
SAMPLE_WB = TEST_ASSET_DIR / "SampleWB.twbx"


@contextlib.contextmanager
def set_env(**environ):
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_read_chunks_file_path(server: TSC.Server) -> None:
    file_path = str(SAMPLE_WB)
    chunks = server.fileuploads._read_chunks(file_path)
    for chunk in chunks:
        assert chunk is not None


def test_read_chunks_file_object(server: TSC.Server) -> None:
    with SAMPLE_WB.open("rb") as f:
        chunks = server.fileuploads._read_chunks(f)
        for chunk in chunks:
            assert chunk is not None


def test_upload_chunks_file_path(server: TSC.Server) -> None:
    file_path = str(SAMPLE_WB)
    upload_id = "7720:170fe6b1c1c7422dadff20f944d58a52-1:0"

    initialize_response_xml = FILEUPLOAD_INITIALIZE.read_text()
    append_response_xml = FILEUPLOAD_APPEND.read_text()
    with requests_mock.mock() as m:
        m.post(server.fileuploads.baseurl, text=initialize_response_xml)
        m.put(f"{server.fileuploads.baseurl}/{upload_id}", text=append_response_xml)
        actual = server.fileuploads.upload(file_path)

    assert upload_id == actual


def test_upload_chunks_file_object(server: TSC.Server) -> None:
    upload_id = "7720:170fe6b1c1c7422dadff20f944d58a52-1:0"

    with SAMPLE_WB.open("rb") as file_content:
        initialize_response_xml = FILEUPLOAD_INITIALIZE.read_text()
        append_response_xml = FILEUPLOAD_APPEND.read_text()
        with requests_mock.mock() as m:
            m.post(server.fileuploads.baseurl, text=initialize_response_xml)
            m.put(f"{server.fileuploads.baseurl}/{upload_id}", text=append_response_xml)
            actual = server.fileuploads.upload(file_content)

    assert upload_id == actual


def test_upload_chunks_config(server: TSC.Server) -> None:
    data = io.BytesIO()
    data.write(b"1" * (config.CHUNK_SIZE_MB * BYTES_PER_MB + 1))
    data.seek(0)
    with set_env(TSC_CHUNK_SIZE_MB="1"):
        chunker = server.fileuploads._read_chunks(data)
        chunk = next(chunker)
        assert len(chunk) == config.CHUNK_SIZE_MB * BYTES_PER_MB
        data.seek(0)
        assert len(chunk) < len(data.read())

import contextlib
import io
import os
import unittest

import requests_mock

from tableauserverclient.config import BYTES_PER_MB, config
from tableauserverclient.server import Server
from ._utils import asset

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
FILEUPLOAD_INITIALIZE = os.path.join(TEST_ASSET_DIR, "fileupload_initialize.xml")
FILEUPLOAD_APPEND = os.path.join(TEST_ASSET_DIR, "fileupload_append.xml")


@contextlib.contextmanager
def set_env(**environ):
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


class FileuploadsTests(unittest.TestCase):
    def setUp(self):
        self.server = Server("http://test", False)

        # Fake sign in
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = f"{self.server.baseurl}/sites/{self.server.site_id}/fileUploads"

    def test_read_chunks_file_path(self):
        file_path = asset("SampleWB.twbx")
        chunks = self.server.fileuploads._read_chunks(file_path)
        for chunk in chunks:
            self.assertIsNotNone(chunk)

    def test_read_chunks_file_object(self):
        with open(asset("SampleWB.twbx"), "rb") as f:
            chunks = self.server.fileuploads._read_chunks(f)
            for chunk in chunks:
                self.assertIsNotNone(chunk)

    def test_upload_chunks_file_path(self):
        file_path = asset("SampleWB.twbx")
        upload_id = "7720:170fe6b1c1c7422dadff20f944d58a52-1:0"

        with open(FILEUPLOAD_INITIALIZE, "rb") as f:
            initialize_response_xml = f.read().decode("utf-8")
        with open(FILEUPLOAD_APPEND, "rb") as f:
            append_response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=initialize_response_xml)
            m.put(f"{self.baseurl}/{upload_id}", text=append_response_xml)
            actual = self.server.fileuploads.upload(file_path)

        self.assertEqual(upload_id, actual)

    def test_upload_chunks_file_object(self):
        upload_id = "7720:170fe6b1c1c7422dadff20f944d58a52-1:0"

        with open(asset("SampleWB.twbx"), "rb") as file_content:
            with open(FILEUPLOAD_INITIALIZE, "rb") as f:
                initialize_response_xml = f.read().decode("utf-8")
            with open(FILEUPLOAD_APPEND, "rb") as f:
                append_response_xml = f.read().decode("utf-8")
            with requests_mock.mock() as m:
                m.post(self.baseurl, text=initialize_response_xml)
                m.put(f"{self.baseurl}/{upload_id}", text=append_response_xml)
                actual = self.server.fileuploads.upload(file_content)

        self.assertEqual(upload_id, actual)

    def test_upload_chunks_config(self):
        data = io.BytesIO()
        data.write(b"1" * (config.CHUNK_SIZE_MB * BYTES_PER_MB + 1))
        data.seek(0)
        with set_env(TSC_CHUNK_SIZE_MB="1"):
            chunker = self.server.fileuploads._read_chunks(data)
            chunk = next(chunker)
            assert len(chunk) == config.CHUNK_SIZE_MB * BYTES_PER_MB
            data.seek(0)
            assert len(chunk) < len(data.read())

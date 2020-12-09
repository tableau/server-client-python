import os
import requests_mock
import unittest

from ._utils import asset
from tableauserverclient.server import Server
from tableauserverclient.server.endpoint.fileuploads_endpoint import Fileuploads

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
FILEUPLOAD_INITIALIZE = os.path.join(TEST_ASSET_DIR, 'fileupload_initialize.xml')
FILEUPLOAD_APPEND = os.path.join(TEST_ASSET_DIR, 'fileupload_append.xml')


class FileuploadsTests(unittest.TestCase):
    def setUp(self):
        self.server = Server('http://test')

        # Fake sign in
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = '{}/sites/{}/fileUploads'.format(self.server.baseurl, self.server.site_id)

    def test_read_chunks_file_path(self):
        fileuploads = Fileuploads(self.server)

        file_path = asset('SampleWB.twbx')
        chunks = fileuploads.read_chunks(file_path)
        for chunk in chunks:
            self.assertIsNotNone(chunk)

    def test_read_chunks_file_object(self):
        fileuploads = Fileuploads(self.server)

        with open(asset('SampleWB.twbx'), 'rb') as f:
            chunks = fileuploads.read_chunks(f)
            for chunk in chunks:
                self.assertIsNotNone(chunk)

    def test_upload_chunks_file_path(self):
        fileuploads = Fileuploads(self.server)
        file_path = asset('SampleWB.twbx')
        upload_id = '7720:170fe6b1c1c7422dadff20f944d58a52-1:0'

        with open(FILEUPLOAD_INITIALIZE, 'rb') as f:
            initialize_response_xml = f.read().decode('utf-8')
        with open(FILEUPLOAD_APPEND, 'rb') as f:
            append_response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=initialize_response_xml)
            m.put(self.baseurl + '/' + upload_id, text=append_response_xml)
            actual = fileuploads.upload_chunks(self.server, file_path)

        self.assertEqual(upload_id, actual)

    def test_upload_chunks_file_object(self):
        fileuploads = Fileuploads(self.server)
        upload_id = '7720:170fe6b1c1c7422dadff20f944d58a52-1:0'

        with open(asset('SampleWB.twbx'), 'rb') as file_content:
            with open(FILEUPLOAD_INITIALIZE, 'rb') as f:
                initialize_response_xml = f.read().decode('utf-8')
            with open(FILEUPLOAD_APPEND, 'rb') as f:
                append_response_xml = f.read().decode('utf-8')
            with requests_mock.mock() as m:
                m.post(self.baseurl, text=initialize_response_xml)
                m.put(self.baseurl + '/' + upload_id, text=append_response_xml)
                actual = fileuploads.upload_chunks(self.server, file_content)

        self.assertEqual(upload_id, actual)

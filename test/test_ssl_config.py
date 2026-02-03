import unittest
import ssl
from unittest.mock import patch, MagicMock
from tableauserverclient import Server
from tableauserverclient.server.endpoint import Endpoint
import logging


class TestSSLConfig(unittest.TestCase):
    @patch("requests.session")
    @patch("tableauserverclient.server.endpoint.Endpoint.set_parameters")
    def setUp(self, mock_set_parameters, mock_session):
        """Set up test fixtures with mocked session and request validation"""
        # Mock the session
        self.mock_session = MagicMock()
        mock_session.return_value = self.mock_session

        # Mock request preparation
        self.mock_request = MagicMock()
        self.mock_session.prepare_request.return_value = self.mock_request

        # Create server instance with mocked components
        self.server = Server("http://test")

    def test_default_ssl_config(self):
        """Test that by default, no custom SSL context is used"""
        self.assertIsNone(self.server._ssl_context)
        self.assertNotIn("verify", self.server.http_options)

    @patch("ssl.create_default_context")
    def test_weak_dh_config(self, mock_create_context):
        """Test that weak DH keys can be allowed when configured"""
        # Setup mock SSL context
        mock_context = MagicMock()
        mock_create_context.return_value = mock_context

        # Configure SSL with weak DH
        self.server.configure_ssl(allow_weak_dh=True)

        # Verify SSL context was created and configured correctly
        mock_create_context.assert_called_once()
        mock_context.set_dh_parameters.assert_called_once_with(min_key_bits=512)

        # Verify context was added to http options
        self.assertEqual(self.server.http_options["verify"], mock_context)

    @patch("ssl.create_default_context")
    def test_disable_weak_dh_config(self, mock_create_context):
        """Test that SSL config can be reset to defaults"""
        # Setup mock SSL context
        mock_context = MagicMock()
        mock_create_context.return_value = mock_context

        # First enable weak DH
        self.server.configure_ssl(allow_weak_dh=True)
        self.assertIsNotNone(self.server._ssl_context)
        self.assertIn("verify", self.server.http_options)

        # Then disable it
        self.server.configure_ssl(allow_weak_dh=False)
        self.assertIsNone(self.server._ssl_context)
        self.assertNotIn("verify", self.server.http_options)

    @patch("ssl.create_default_context")
    def test_warning_on_weak_dh(self, mock_create_context):
        """Test that a warning is logged when enabling weak DH keys"""
        logging.getLogger().setLevel(logging.WARNING)
        with self.assertLogs(level="WARNING") as log:
            self.server.configure_ssl(allow_weak_dh=True)
            self.assertTrue(
                any("WARNING: Allowing weak Diffie-Hellman keys" in record for record in log.output),
                "Expected warning about weak DH keys was not logged",
            )


if __name__ == "__main__":
    unittest.main()

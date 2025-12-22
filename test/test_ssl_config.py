import logging
from unittest.mock import MagicMock

import pytest

import tableauserverclient as TSC


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_default_ssl_config(server):
    """Test that by default, no custom SSL context is used"""
    assert server._ssl_context is None
    assert "verify" not in server.http_options


def test_weak_dh_config(server, monkeypatch):
    """Test that weak DH keys can be allowed when configured"""
    mock_context = MagicMock()
    mock_create_context = MagicMock(return_value=mock_context)
    monkeypatch.setattr("ssl.create_default_context", mock_create_context)

    server.configure_ssl(allow_weak_dh=True)

    mock_create_context.assert_called_once()
    mock_context.set_dh_parameters.assert_called_once_with(min_key_bits=512)
    assert server.http_options["verify"] == mock_context


def test_disable_weak_dh_config(server, monkeypatch):
    """Test that SSL config can be reset to defaults"""
    mock_context = MagicMock()
    mock_create_context = MagicMock(return_value=mock_context)
    monkeypatch.setattr("ssl.create_default_context", mock_create_context)

    # First enable weak DH
    server.configure_ssl(allow_weak_dh=True)
    assert server._ssl_context is not None
    assert "verify" in server.http_options

    # Then disable it
    server.configure_ssl(allow_weak_dh=False)
    assert server._ssl_context is None
    assert "verify" not in server.http_options


def test_warning_on_weak_dh(server, monkeypatch, caplog):
    """Test that a warning is logged when enabling weak DH keys"""
    mock_context = MagicMock()
    mock_create_context = MagicMock(return_value=mock_context)
    monkeypatch.setattr("ssl.create_default_context", mock_create_context)

    with caplog.at_level(logging.WARNING):
        server.configure_ssl(allow_weak_dh=True)

    assert any(
        "Allowing weak Diffie-Hellman keys" in record.getMessage() for record in caplog.records
    ), "Expected warning about weak DH keys was not logged"

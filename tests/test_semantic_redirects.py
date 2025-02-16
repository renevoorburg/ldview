import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

venv_lib = os.path.join(os.path.dirname(__file__), '..', 'venv', 'lib')
for folder in os.listdir(venv_lib):
    site_packages_path = os.path.join(venv_lib, folder, 'site-packages')
    if os.path.isdir(site_packages_path):
         sys.path.insert(0, site_packages_path)
         break

import pytest

from app import app
import config
from uri_utils import identity_uri_to_page_uri, page_uri_to_identity_uri


@pytest.fixture
def client():
    # Configure the app for testing
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_semantic_redirects_enabled(client, monkeypatch):
    """
    Test that when semantic redirects are enabled, the resolved identity URI in the response
    corresponds to the one returned by page_uri_to_identity_uri().
    """
    monkeypatch.setattr(config, "USE_SEMANTIC_REDIRECTS", True)
    monkeypatch.setattr(config, "BASE_URI", "http://example.org/")
    monkeypatch.setattr(config, "SEMANTIC_REDIRECT_URI_SEGMENTS", {
        'identification': '/id/',     # Pattern voor identificatie URIs
        'documentation': '/doc/'    # Pattern voor document URIs
    })

    test_uri = "http://example.org/id/test"
    
    response = client.get(test_uri, follow_redirects=False)
    redirect_url = response.headers.get("Location")
    expected_id_uri = identity_uri_to_page_uri(test_uri)

    assert expected_id_uri == redirect_url, f"Expected identity URI {expected_id_uri} does not match redirect URL {redirect_url}."


def test_semantic_redirects_disabled(client, monkeypatch):
    """
    Test that when semantic redirects are disabled, no redirect occurs, meaning the response does not have a Location header.
    """
    monkeypatch.setattr(config, "USE_SEMANTIC_REDIRECTS", False)
    monkeypatch.setattr(config, "BASE_URI", "http://example.org/")
    monkeypatch.setattr(config, "SEMANTIC_REDIRECT_URI_SEGMENTS", {
        'identification': '/id/',     # Pattern voor identificatie URIs
        'documentation': '/doc/'    # Pattern voor document URIs
    })
    test_uri = "http://example.org/id/"

    response = client.get(test_uri, follow_redirects=False)
    redirect_url = response.headers.get("Location")

    assert redirect_url is None, f"Response should not have a 'Location' header when semantic redirects are disabled."

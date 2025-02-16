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



def test_404_semantic_redirects_disabled(client, monkeypatch):
    """
    Test that when semantic redirects are disabled, no redirect occurs, meaning the response does not have a Location header.
    """
    monkeypatch.setattr(config, "USE_SEMANTIC_REDIRECTS", False)
    monkeypatch.setattr(config, "BASE_URI", "http://example.org/")
    monkeypatch.setattr(config, "SEMANTIC_REDIRECT_URI_SEGMENTS", {
        'identification': '/id/',     # Pattern voor identificatie URIs
        'documentation': '/doc/'    # Pattern voor document URIs
    })
    test_uri = "http://example.org/nosuch/"

    response = client.get(test_uri, follow_redirects=False)
    assert response.status_code == 404, f"Expected HTTP status code 404, got {response.status_code}."

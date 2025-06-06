from pathlib import Path

from dotenv import load_dotenv
import pytest
import os, certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables from .env file for all tests."""
    load_dotenv()

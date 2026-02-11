"""Shared fixtures for GUI tests."""

import pytest
import sys
import os
from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="module")
def qapp():
    """Create a QApplication instance for Qt widgets."""
    # Set QT platform to offscreen for headless environments
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

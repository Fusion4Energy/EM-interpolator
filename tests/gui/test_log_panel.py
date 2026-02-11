"""Tests for LogPanel class."""

import pytest

from em_interp.gui.log_panel import LogPanel


class TestLogPanel:
    """Tests for LogPanel class."""

    def test_init(self, qapp):
        """Test LogPanel initialization."""
        panel = LogPanel()
        assert panel is not None
        assert panel.log_text.isReadOnly()

    def test_append_log(self, qapp):
        """Test appending log messages."""
        panel = LogPanel()
        panel.append_log("Test message 1")
        panel.append_log("Test message 2")
        log_content = panel.log_text.toPlainText()
        assert "Test message 1" in log_content
        assert "Test message 2" in log_content

    def test_multiple_appends(self, qapp):
        """Test multiple log appends."""
        panel = LogPanel()
        messages = ["Message 1", "Message 2", "Message 3"]
        for msg in messages:
            panel.append_log(msg)
        log_content = panel.log_text.toPlainText()
        for msg in messages:
            assert msg in log_content

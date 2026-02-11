"""Tests for FilePanel class."""

import pytest
from unittest.mock import patch

from em_interp.gui.file_panel import FilePanel


class TestFilePanel:
    """Tests for FilePanel class."""

    def test_init(self, qapp):
        """Test FilePanel initialization."""
        panel = FilePanel()
        assert panel is not None
        assert panel.em_folder_path.text() == ""
        assert panel.mech_mesh_path.text() == ""
        assert panel.outdir_path.text() == ""
        assert panel.em_x_col_edit.text() == "0"
        assert panel.em_fx_col_edit.text() == "3"
        assert panel.mech_x_col_edit.text() == "1"
        assert panel.mech_node_id_col_edit.text() == "0"

    def test_set_em_folder_path(self, qapp):
        """Test setting EM folder path."""
        panel = FilePanel()
        test_path = "/test/em/folder"
        panel.em_folder_path.setText(test_path)
        assert panel.em_folder_path.text() == test_path

    def test_set_mech_mesh_path(self, qapp):
        """Test setting mechanical mesh path."""
        panel = FilePanel()
        test_path = "/test/mech/mesh.txt"
        panel.mech_mesh_path.setText(test_path)
        assert panel.mech_mesh_path.text() == test_path

    def test_set_outdir_path(self, qapp):
        """Test setting output directory path."""
        panel = FilePanel()
        test_path = "/test/output"
        panel.outdir_path.setText(test_path)
        assert panel.outdir_path.text() == test_path

    def test_column_edits(self, qapp):
        """Test column index edits."""
        panel = FilePanel()
        panel.em_x_col_edit.setText("5")
        panel.em_fx_col_edit.setText("8")
        panel.mech_x_col_edit.setText("2")
        panel.mech_node_id_col_edit.setText("1")
        assert panel.em_x_col_edit.text() == "5"
        assert panel.em_fx_col_edit.text() == "8"
        assert panel.mech_x_col_edit.text() == "2"
        assert panel.mech_node_id_col_edit.text() == "1"

    @patch("em_interp.gui.file_panel.QFileDialog.getExistingDirectory")
    def test_browse_em_folder(self, mock_dialog, qapp):
        """Test browsing EM folder."""
        panel = FilePanel()
        mock_dialog.return_value = "/test/em/path"
        panel.browse_em_folder()
        assert panel.em_folder_path.text() == "/test/em/path"

    @patch("em_interp.gui.file_panel.QFileDialog.getOpenFileName")
    def test_browse_mech_mesh(self, mock_dialog, qapp):
        """Test browsing mechanical mesh file."""
        panel = FilePanel()
        mock_dialog.return_value = ("/test/mech.txt", "")
        panel.browse_mech_mesh()
        assert panel.mech_mesh_path.text() == "/test/mech.txt"

    @patch("em_interp.gui.file_panel.QFileDialog.getExistingDirectory")
    def test_browse_outdir(self, mock_dialog, qapp):
        """Test browsing output directory."""
        panel = FilePanel()
        mock_dialog.return_value = "/test/output"
        panel.browse_outdir()
        assert panel.outdir_path.text() == "/test/output"

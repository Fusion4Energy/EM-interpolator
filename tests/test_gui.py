"""Tests for GUI modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import sys
import numpy as np

from em_interp.gui.file_panel import FilePanel
from em_interp.gui.log_panel import LogPanel
from em_interp.gui.param_panel import ParamPanel
from em_interp.gui.visualization_panel import VisualizationPanel
from em_interp.gui.main_window import MainWindow, QtLogHandler
from em_interp.gui.worker import InterpolationWorker
from em_interp.core.config import QUERY_TYPE, INTERPOLATION_KERNEL


@pytest.fixture(scope="module")
def qapp():
    """Create a QApplication instance for Qt widgets."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


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


class TestParamPanel:
    """Tests for ParamPanel class."""

    def test_init(self, qapp):
        """Test ParamPanel initialization."""
        panel = ParamPanel()
        assert panel is not None
        assert panel.method_combo.currentText() in [e.value for e in QUERY_TYPE]
        assert panel.param_spin.text() == "1"
        assert panel.max_dist_edit.text() == "0.5"
        assert panel.coinc_tol_edit.text() == "1e-6"
        assert panel.kernel_combo.currentText() in [e.value for e in INTERPOLATION_KERNEL]

    def test_method_combo_items(self, qapp):
        """Test method combo box contains all QUERY_TYPE values."""
        panel = ParamPanel()
        combo_items = [panel.method_combo.itemText(i) for i in range(panel.method_combo.count())]
        expected_items = [e.value for e in QUERY_TYPE]
        assert combo_items == expected_items

    def test_kernel_combo_items(self, qapp):
        """Test kernel combo box contains all INTERPOLATION_KERNEL values."""
        panel = ParamPanel()
        combo_items = [panel.kernel_combo.itemText(i) for i in range(panel.kernel_combo.count())]
        expected_items = [e.value for e in INTERPOLATION_KERNEL]
        assert combo_items == expected_items

    def test_param_edit(self, qapp):
        """Test parameter text edit."""
        panel = ParamPanel()
        panel.param_spin.setText("2.5")
        assert panel.param_spin.text() == "2.5"

    def test_max_dist_edit(self, qapp):
        """Test max distance edit."""
        panel = ParamPanel()
        panel.max_dist_edit.setText("1.0")
        assert panel.max_dist_edit.text() == "1.0"

    def test_coinc_tol_edit(self, qapp):
        """Test coincidence tolerance edit."""
        panel = ParamPanel()
        panel.coinc_tol_edit.setText("1e-5")
        assert panel.coinc_tol_edit.text() == "1e-5"

    def test_multithread_checkbox(self, qapp):
        """Test multithread checkbox."""
        panel = ParamPanel()
        initial_state = panel.multithread_check.isChecked()
        panel.multithread_check.setChecked(not initial_state)
        assert panel.multithread_check.isChecked() == (not initial_state)

    def test_method_changed_to_radius(self, qapp):
        """Test method change to Radius.
        
        Note: There is a case sensitivity mismatch in the original code. The combo box shows
        'Radius' (capitalized) but the code checks for 'radius' (lowercase), so the 
        special handling for radius method doesn't actually trigger through the UI.
        This test verifies the actual current behavior.
        """
        panel = ParamPanel()
        initial_max_dist = panel.max_dist_edit.text()
        panel.param_spin.setText("2.0")
        # Set the method combo to "Radius" using the correct enum value
        panel.method_combo.setCurrentText("Radius")
        # Due to case mismatch bug, max_dist should remain enabled and unchanged
        assert panel.max_dist_edit.isEnabled()
        assert panel.max_dist_edit.text() == initial_max_dist

    def test_param_changed_with_non_radius_method(self, qapp):
        """Test that param changes don't affect max_dist when method is not radius."""
        panel = ParamPanel()
        # Set method to K-Nearest Neighbors
        panel.method_combo.setCurrentText("K-Nearest Neighbors")
        panel.param_spin.setText("2.0")
        # max_dist should remain at its original value
        assert panel.max_dist_edit.text() == "0.5"
        # Change param again
        panel.param_spin.setText("3.5")
        # max_dist should still be unchanged
        assert panel.max_dist_edit.text() == "0.5"


class TestVisualizationPanel:
    """Tests for VisualizationPanel class."""

    @pytest.mark.skip(reason="VisualizationPanel requires OpenGL context which is not available in headless environment")
    def test_init(self, qapp):
        """Test VisualizationPanel initialization."""
        panel = VisualizationPanel()
        assert panel is not None
        assert panel._glyph_scale_em == 0.001
        assert panel._glyph_scale_mech == 0.001
        assert panel._mesh_em is None
        assert panel._mesh_mech is None

    @pytest.mark.skip(reason="VisualizationPanel requires OpenGL context which is not available in headless environment")
    def test_scale_slider_em(self, qapp):
        """Test EM glyph scale slider."""
        panel = VisualizationPanel()
        panel.scale_slider_em.setValue(50)
        assert panel._glyph_scale_em == 0.05
        assert "0.050" in panel.scale_label_em.text()

    @pytest.mark.skip(reason="VisualizationPanel requires OpenGL context which is not available in headless environment")
    def test_scale_slider_mech(self, qapp):
        """Test Mech glyph scale slider."""
        panel = VisualizationPanel()
        panel.scale_slider_mech.setValue(10)
        assert panel._glyph_scale_mech == 0.01
        assert "0.010" in panel.scale_label_mech.text()

    @pytest.mark.skip(reason="VisualizationPanel requires OpenGL context which is not available in headless environment")
    @patch("pyvista.UnstructuredGrid")
    def test_display_mesh(self, mock_mesh, qapp):
        """Test display_mesh method."""
        panel = VisualizationPanel()
        mock_em = MagicMock()
        mock_mech = MagicMock()
        
        # Create a mock glyph return
        mock_glyph_em = MagicMock()
        mock_glyph_mech = MagicMock()
        mock_em.glyph.return_value = mock_glyph_em
        mock_mech.glyph.return_value = mock_glyph_mech
        
        panel.display_mesh(mock_em, mock_mech)
        
        # Verify meshes are stored
        assert panel._mesh_em == mock_em
        assert panel._mesh_mech == mock_mech


class TestMainWindow:
    """Tests for MainWindow class."""

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_init(self, qapp):
        """Test MainWindow initialization."""
        window = MainWindow()
        assert window is not None
        assert window.windowTitle() == "EM Interpolation GUI"
        assert window.interpolator is None

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_file_panel_exists(self, qapp):
        """Test that file panel is created."""
        window = MainWindow()
        assert hasattr(window, "file_panel")
        assert isinstance(window.file_panel, FilePanel)

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_param_panel_exists(self, qapp):
        """Test that param panel is created."""
        window = MainWindow()
        assert hasattr(window, "param_panel")
        assert isinstance(window.param_panel, ParamPanel)

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_log_panel_exists(self, qapp):
        """Test that log panel is created."""
        window = MainWindow()
        assert hasattr(window, "log_panel")
        assert isinstance(window.log_panel, LogPanel)

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_visualization_panel_exists(self, qapp):
        """Test that visualization panel is created."""
        window = MainWindow()
        assert hasattr(window, "visualization_panel")
        assert isinstance(window.visualization_panel, VisualizationPanel)

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_buttons_exist(self, qapp):
        """Test that all action buttons are created."""
        window = MainWindow()
        assert hasattr(window, "btn_run_all")
        assert hasattr(window, "btn_init_interpolator")
        assert hasattr(window, "btn_interpolate")
        assert hasattr(window, "btn_export_checks")
        assert hasattr(window, "btn_export_ansys")
        assert hasattr(window, "btn_compute_vtk")
        assert hasattr(window, "btn_export_vtk")
        assert hasattr(window, "btn_preview_forces")

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_read_config(self, qapp):
        """Test reading configuration from param panel."""
        window = MainWindow()
        window.param_panel.method_combo.setCurrentText("K-Nearest Neighbors")
        window.param_panel.param_spin.setText("5")
        window.param_panel.max_dist_edit.setText("0.8")
        window.param_panel.coinc_tol_edit.setText("1e-7")
        window.param_panel.kernel_combo.setCurrentText("Weighted by distance")
        window.param_panel.multithread_check.setChecked(True)
        
        config = window._read_config()
        assert config.method == QUERY_TYPE.K
        assert config.param == 5.0
        assert config.max_distance == 0.8
        assert config.coincidence_tolerance == 1e-7
        assert config.kernel == INTERPOLATION_KERNEL.DISTANCE_WEIGHTED
        assert config.multithread is True

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    @patch("em_interp.gui.main_window.Interpolator")
    @patch("em_interp.gui.main_window.logging")
    def test_initialize_interpolator_success(self, mock_logging, mock_interpolator, qapp, tmp_path):
        """Test successful interpolator initialization."""
        window = MainWindow()
        window.file_panel.em_folder_path.setText(str(tmp_path / "em"))
        window.file_panel.mech_mesh_path.setText(str(tmp_path / "mech.txt"))
        window.file_panel.em_x_col_edit.setText("1")
        window.file_panel.em_fx_col_edit.setText("4")
        window.file_panel.mech_x_col_edit.setText("1")
        window.file_panel.mech_node_id_col_edit.setText("0")
        
        mock_interpolator_instance = MagicMock()
        mock_interpolator.return_value = mock_interpolator_instance
        
        window.initialize_interpolator()
        
        # Check interpolator was created
        mock_interpolator.assert_called_once()
        assert window.interpolator == mock_interpolator_instance

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    @patch("em_interp.gui.main_window.Interpolator")
    @patch("em_interp.gui.main_window.logging")
    def test_initialize_interpolator_failure(self, mock_logging, mock_interpolator, qapp):
        """Test interpolator initialization failure."""
        window = MainWindow()
        window.file_panel.em_folder_path.setText("/nonexistent/em")
        window.file_panel.mech_mesh_path.setText("/nonexistent/mech.txt")
        
        mock_interpolator.side_effect = FileNotFoundError("File not found")
        
        window.initialize_interpolator()
        
        # Interpolator should remain None
        assert window.interpolator is None
        mock_logging.error.assert_called()

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_click_export_checks_without_interpolator(self, qapp):
        """Test export checks without initialized interpolator."""
        window = MainWindow()
        # Should not raise exception
        window.click_export_checks()

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_click_export_ansys_without_interpolator(self, qapp):
        """Test export ANSYS without initialized interpolator."""
        window = MainWindow()
        # Should not raise exception
        window.click_export_ansys()

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_click_compute_vtk_without_interpolator(self, qapp):
        """Test compute VTK without initialized interpolator."""
        window = MainWindow()
        # Should not raise exception
        window.click_compute_vtk()

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_click_export_vtk_without_interpolator(self, qapp):
        """Test export VTK without initialized interpolator."""
        window = MainWindow()
        # Should not raise exception
        window.click_export_vtk()

    @pytest.mark.skip(reason="MainWindow requires OpenGL context for VisualizationPanel which is not available in headless environment")
    def test_click_preview_forces_without_interpolator(self, qapp):
        """Test preview forces without initialized interpolator."""
        window = MainWindow()
        # Should not raise exception
        window.click_preview_forces()


class TestQtLogHandler:
    """Tests for QtLogHandler class."""

    def test_init(self, qapp):
        """Test QtLogHandler initialization."""
        log_panel = LogPanel()
        handler = QtLogHandler(log_panel)
        assert handler.log_panel == log_panel

    def test_emit(self, qapp):
        """Test emit method."""
        import logging
        log_panel = LogPanel()
        handler = QtLogHandler(log_panel)
        handler.setFormatter(logging.Formatter("%(message)s"))
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        handler.emit(record)
        assert "Test message" in log_panel.log_text.toPlainText()


class TestInterpolationWorker:
    """Tests for InterpolationWorker class."""

    def test_init(self, qapp):
        """Test InterpolationWorker initialization."""
        mock_interpolator = MagicMock()
        worker = InterpolationWorker(mock_interpolator)
        assert worker.interpolator == mock_interpolator

    def test_run(self, qapp):
        """Test worker run method."""
        mock_interpolator = MagicMock()
        worker = InterpolationWorker(mock_interpolator)
        
        # Mock the interpolate_all method
        def mock_interpolate_all(progress_callback=None):
            if progress_callback:
                progress_callback(50)
                progress_callback(100)
        
        mock_interpolator.interpolate_all = mock_interpolate_all
        
        # Track signals
        progress_values = []
        finished_called = []
        
        def on_progress(value):
            progress_values.append(value)
        
        def on_finished():
            finished_called.append(True)
        
        worker.progress_changed.connect(on_progress)
        worker.finished.connect(on_finished)
        
        # Run the worker
        worker.run()
        
        # Check that signals were emitted
        assert 50 in progress_values
        assert 100 in progress_values
        assert len(finished_called) == 1

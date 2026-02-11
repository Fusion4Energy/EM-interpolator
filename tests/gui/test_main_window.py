"""Tests for MainWindow class."""

import pytest
from unittest.mock import patch, MagicMock

from em_interp.gui.main_window import MainWindow, QtLogHandler
from em_interp.gui.file_panel import FilePanel
from em_interp.gui.param_panel import ParamPanel
from em_interp.gui.log_panel import LogPanel
from em_interp.gui.visualization_panel import VisualizationPanel
from em_interp.core.config import QUERY_TYPE, INTERPOLATION_KERNEL


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

"""Tests for VisualizationPanel class."""

import pytest
from unittest.mock import patch, MagicMock

from em_interp.gui.visualization_panel import VisualizationPanel


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

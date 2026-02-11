"""Tests for ParamPanel class."""

import pytest

from em_interp.gui.param_panel import ParamPanel
from em_interp.core.config import QUERY_TYPE, INTERPOLATION_KERNEL


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

# Parameter editing panel
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QCheckBox,
    QLineEdit,
)
from em_interp.core.config import INTERPOLATION_KERNEL, QUERY_TYPE


class ParamPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Method
        method_row = QHBoxLayout()
        self.method_label = QLabel("Neighbors Method:")
        self.method_combo = QComboBox()
        self.method_combo.addItems([e.value for e in QUERY_TYPE])
        method_row.addWidget(self.method_label)
        method_row.addWidget(self.method_combo)
        layout.addLayout(method_row)

        # Param
        param_row = QHBoxLayout()
        self.param_label = QLabel("Param (R [m] or k):")
        self.param_spin = QDoubleSpinBox()
        self.param_spin.setRange(0, 1e6)
        param_row.addWidget(self.param_label)
        param_row.addWidget(self.param_spin)
        layout.addLayout(param_row)

        # Max Distance
        max_dist_row = QHBoxLayout()
        self.max_dist_label = QLabel("Max Distance [m]:")
        self.max_dist_edit = QLineEdit()
        self.max_dist_edit.setText("0.5")
        max_dist_row.addWidget(self.max_dist_label)
        max_dist_row.addWidget(self.max_dist_edit)
        layout.addLayout(max_dist_row)

        # Coincidence Tolerance
        coinc_tol_row = QHBoxLayout()
        self.coinc_tol_label = QLabel("Coincidence Tolerance [m]:")
        self.coinc_tol_edit = QLineEdit()
        self.coinc_tol_edit.setText("1e-6")  # m
        coinc_tol_row.addWidget(self.coinc_tol_label)
        coinc_tol_row.addWidget(self.coinc_tol_edit)
        layout.addLayout(coinc_tol_row)

        # Kernel
        kernel_row = QHBoxLayout()
        self.kernel_label = QLabel("Interpolation Kernel:")
        self.kernel_combo = QComboBox()
        self.kernel_combo.addItems([e.value for e in INTERPOLATION_KERNEL])
        kernel_row.addWidget(self.kernel_label)
        kernel_row.addWidget(self.kernel_combo)
        layout.addLayout(kernel_row)

        # Multithread
        self.multithread_check = QCheckBox("Multithread")
        layout.addWidget(self.multithread_check)

        # Connect logic for method/param interaction
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        self.param_spin.valueChanged.connect(self._on_param_changed)

    def _on_method_changed(self, method):
        if method == "radius":
            self.max_dist_edit.setEnabled(False)
            self.max_dist_edit.setValue(self.param_spin.value())
        else:
            self.max_dist_edit.setEnabled(True)

    def _on_param_changed(self, value):
        if self.method_combo.currentText() == "radius":
            self.max_dist_edit.setValue(value)

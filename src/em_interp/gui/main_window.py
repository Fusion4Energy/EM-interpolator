# Main window and layout for the interpolation GUI
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QSplitter,
    QLabel,
    QProgressDialog,
    QInputDialog,
)
from PyQt5.QtCore import Qt
from .file_panel import FilePanel
from .param_panel import ParamPanel
from .visualization_panel import VisualizationPanel
from .log_panel import LogPanel
import logging
from pathlib import Path
import os

from em_interp.core.interpolation import Interpolator
from em_interp.core.config import InterpolationConfig, INTERPOLATION_KERNEL, QUERY_TYPE
from em_interp.gui.worker import InterpolationWorker


class QtLogHandler(logging.Handler):
    def __init__(self, log_panel):
        super().__init__()
        self.log_panel = log_panel

    def emit(self, record):
        msg = self.format(record)
        self.log_panel.append_log(msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EM Interpolation GUI")
        self.resize(1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tabs
        tabs = QTabWidget()

        # Tab 1: File and parameter selection
        file_param_tab = QWidget()
        file_param_layout = QVBoxLayout(file_param_tab)
        self.file_panel = FilePanel()
        self.param_panel = ParamPanel()
        file_param_layout.addWidget(self.file_panel)
        file_param_layout.addWidget(self.param_panel, stretch=1)
        tabs.addTab(file_param_tab, "Input & Config")

        # Tab 2: Visualization and log

        vis_log_tab = QWidget()
        vis_log_layout = QVBoxLayout(vis_log_tab)

        # Top row of action buttons
        button_row = QHBoxLayout()
        self.btn_run_all = QPushButton("Run All")
        self.btn_run_all.setStyleSheet(
            "background-color: #0078d7; color: white; font-weight: bold;"
        )
        self.btn_init_interpolator = QPushButton("Initialize Interpolator")
        self.btn_interpolate = QPushButton("Interpolate")
        self.btn_export_checks = QPushButton("Export Checks")
        self.btn_export_ansys = QPushButton("Export ANSYS")
        self.btn_compute_vtk = QPushButton("Compute VTK")
        self.btn_export_vtk = QPushButton("Export VTK")
        self.btn_preview_forces = QPushButton("Preview Forces")
        button_row.addWidget(self.btn_run_all)
        button_row.addWidget(self.btn_init_interpolator)
        button_row.addWidget(self.btn_interpolate)
        button_row.addWidget(self.btn_export_checks)
        button_row.addWidget(self.btn_export_ansys)
        button_row.addWidget(self.btn_compute_vtk)
        button_row.addWidget(self.btn_export_vtk)
        button_row.addWidget(self.btn_preview_forces)
        vis_log_layout.addLayout(button_row)

        splitter = QSplitter()

        # Left: PyVista viewing pane with description
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        left_layout.addWidget(QLabel("3D Visualization 1: EM, 2: Mech"))
        self.visualization_panel = VisualizationPanel()
        left_layout.addWidget(self.visualization_panel)
        splitter.addWidget(left_widget)

        # Right: Logger with description
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2)
        right_layout.addWidget(QLabel("Log / Status Output:"))
        self.log_panel = LogPanel()
        right_layout.addWidget(self.log_panel)
        splitter.addWidget(right_widget)

        splitter.setSizes([800, 400])
        vis_log_layout.addWidget(splitter)
        tabs.addTab(vis_log_tab, "Interpolation")

        main_layout.addWidget(tabs)

        # Core logic: Interpolator instance
        self.interpolator = None
        self.btn_init_interpolator.clicked.connect(self.initialize_interpolator)
        self.btn_interpolate.clicked.connect(self.click_interpolate)
        self.btn_export_checks.clicked.connect(self.click_export_checks)
        self.btn_export_ansys.clicked.connect(self.click_export_ansys)
        self.btn_compute_vtk.clicked.connect(self.click_compute_vtk)
        self.btn_export_vtk.clicked.connect(self.click_export_vtk)
        self.btn_preview_forces.clicked.connect(self.click_preview_forces)
        self.btn_run_all.clicked.connect(self.click_run_all)

    def click_run_all(self):
        # 1. Initialize interpolator
        self.initialize_interpolator()
        if self.interpolator is None:
            return
        # 2. Interpolate (with progress bar)
        self._show_progress_dialog()
        self.worker = InterpolationWorker(self.interpolator)
        self.worker.progress_changed.connect(self._update_progress)

        def after_interpolation():
            self.progress_dialog.setLabelText("Exporting checks...")
            self.click_export_checks()
            self.progress_dialog.setLabelText("Exporting ANSYS files...")
            self.click_export_ansys()
            self.progress_dialog.setLabelText("Computing VTK...")
            self.click_compute_vtk()
            self.progress_dialog.setLabelText("Exporting VTK...")
            self.click_export_vtk()
            self.progress_dialog.close()

        self.worker.finished.connect(after_interpolation)
        self.worker.start()

        # Redirect Python logger to the log panel
        log_handler = QtLogHandler(self.log_panel)
        log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)
        logging.info("Application started. Ready for user input.")

    def initialize_interpolator(self):
        """Create the Interpolator instance using selected files and parameters."""

        em_folder = self.file_panel.em_folder_path.text()
        mech_mesh = self.file_panel.mech_mesh_path.text()
        config = self._read_config()

        # build the index files dictionary
        file_idx = {
            "mech_x": int(self.file_panel.mech_x_col_edit.text()),
            "mech_node_id": int(self.file_panel.mech_node_id_col_edit.text()),
            "em_x": int(self.file_panel.em_x_col_edit.text()),
            "em_f": int(self.file_panel.em_fx_col_edit.text()),
        }

        try:
            self.interpolator = Interpolator(
                path_to_em_folder=em_folder,
                path_to_mech_mesh=mech_mesh,
                config=config,
                file_idx=file_idx,
            )
        except (PermissionError, FileNotFoundError) as e:
            logging.error(f"Failed to initialize Interpolator: {e}")
            return
        logging.info("Interpolator initialized successfully.")

    def click_interpolate(self):
        if self.interpolator is None:
            logging.error("Interpolator not initialized. Cannot perform interpolation.")
            return
        self._show_progress_dialog()
        self.worker = InterpolationWorker(self.interpolator)
        self.worker.progress_changed.connect(self._update_progress)
        self.worker.finished.connect(self.progress_dialog.close)
        self.worker.start()

    def click_export_checks(self):
        if self.interpolator is None:
            logging.error("Interpolator not initialized. Cannot export checks.")
            return

        # create the outdir directory if it does not exist
        outfile = Path(self.file_panel.outdir_path.text(), "interpolation_checks.csv")

        # TODO: add possibility to select a different pole than 0,0,0
        self.interpolator.dump_interpolation_check(outfile, None)

    def click_export_ansys(self):
        if self.interpolator is None:
            logging.error("Interpolator not initialized. Cannot export ANSYS files.")
            return
        outdir = Path(self.file_panel.outdir_path.text(), "ansys_export")
        os.makedirs(outdir, exist_ok=True)
        self.interpolator.export_to_ansys(outdir)

    def click_compute_vtk(self):
        if self.interpolator is None:
            logging.error("Interpolator not initialized. Cannot compute VTK.")
            return
        self.interpolator.build_vtk_output()

    def click_export_vtk(self):
        if self.interpolator is None:
            logging.error("Interpolator not initialized. Cannot export VTK.")
            return
        outdir = Path(self.file_panel.outdir_path.text(), "vtk_export")
        os.makedirs(outdir, exist_ok=True)
        self.interpolator.export_forces_to_vtk(outdir)

    def click_preview_forces(self):
        if self.interpolator is None:
            logging.error("Interpolator not initialized. Cannot preview forces.")
            return

        # first pop up a dialog to select which mesh to preview
        mesh_names = list(self.interpolator.em_vtk.keys())
        if not mesh_names:
            logging.error("No mesh names available for preview.")
            return
        mesh_name, ok = QInputDialog.getItem(
            self, "Select Mesh", "Choose mesh to preview:", mesh_names, 0, False
        )
        if not ok or not mesh_name:
            logging.info("Mesh preview cancelled by user.")
            return
        self.visualization_panel.display_mesh(
            self.interpolator.em_vtk[mesh_name], self.interpolator.mech_vtk[mesh_name]
        )

    def _read_config(self) -> InterpolationConfig:
        config = InterpolationConfig(
            method=QUERY_TYPE(self.param_panel.method_combo.currentText()),
            param=float(self.param_panel.param_spin.text()),
            max_distance=float(self.param_panel.max_dist_edit.text()),
            coincidence_tolerance=float(self.param_panel.coinc_tol_edit.text()),
            kernel=INTERPOLATION_KERNEL(self.param_panel.kernel_combo.currentText()),
            multithread=self.param_panel.multithread_check.isChecked(),
        )
        return config

    def _show_progress_dialog(self):
        self.progress_dialog = QProgressDialog(
            "Interpolating...", "Cancel", 0, 100, self
        )
        self.progress_dialog.setWindowTitle("Progress")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()

    def _update_progress(self, value):
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.setValue(value)

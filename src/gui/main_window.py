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
)
from .file_panel import FilePanel
from .param_panel import ParamPanel
from .visualization_panel import VisualizationPanel
from .log_panel import LogPanel
from core.interpolation import Interpolator
from core.config import InterpolationConfig, INTERPOLATION_KERNEL, QUERY_TYPE
import logging
from PyQt5.QtWidgets import QInputDialog
from pathlib import Path
import os


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
        left_layout.addWidget(QLabel("3D Visualization (PyVista pane):"))
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
        tabs.addTab(vis_log_tab, "Visualization & Log")

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
        self.interpolator.interpolate_all()

    def click_export_checks(self):
        if self.interpolator is None:
            logging.error("Interpolator not initialized. Cannot export checks.")
            return

        # create the outdir directory if it does not exist
        outdir = Path(self.file_panel.outdir_path.text(), "interpolation_checks")
        os.makedirs(outdir, exist_ok=True)

        # TODO: add possibility to select a different pole than 0,0,0
        self.interpolator.dump_interpolation_check(outdir, None)

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
            param=self.param_panel.param_spin.value(),
            max_distance=float(self.param_panel.max_dist_edit.text()),
            coincidence_tolerance=float(self.param_panel.coinc_tol_edit.text()),
            kernel=INTERPOLATION_KERNEL(self.param_panel.kernel_combo.currentText()),
            multithread=self.param_panel.multithread_check.isChecked(),
        )
        return config

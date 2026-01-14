# File selection panel
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QHBoxLayout,
)


class FilePanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # EM Folder row
        self.em_folder_label = QLabel("EM Folder:")
        em_row = QHBoxLayout()
        self.em_folder_path = QLineEdit()
        self.em_folder_btn = QPushButton("Browse")
        self.em_folder_btn.clicked.connect(self.browse_em_folder)
        # x coord
        self.em_x_col_label = QLabel("Column X coord:")
        self.em_x_col_edit = QLineEdit()
        self.em_x_col_edit.setFixedWidth(40)
        self.em_x_col_edit.setText("0")
        # Fx coord
        self.em_fx_col_label = QLabel("Column Fx coord:")
        self.em_fx_col_edit = QLineEdit()
        self.em_fx_col_edit.setFixedWidth(40)
        self.em_fx_col_edit.setText("3")

        em_row.addWidget(self.em_folder_path)
        em_row.addWidget(self.em_folder_btn)
        em_row.addWidget(self.em_x_col_label)
        em_row.addWidget(self.em_x_col_edit)
        em_row.addWidget(self.em_fx_col_label)
        em_row.addWidget(self.em_fx_col_edit)
        layout.addWidget(self.em_folder_label)
        layout.addLayout(em_row)

        # Mechanical Mesh row
        self.mech_mesh_label = QLabel("Mechanical Mesh File:")
        mech_row = QHBoxLayout()
        self.mech_mesh_path = QLineEdit()
        self.mech_mesh_btn = QPushButton("Browse")
        self.mech_mesh_btn.clicked.connect(self.browse_mech_mesh)
        # x coord
        self.mech_x_col_label = QLabel("Column for X coord:")
        self.mech_x_col_edit = QLineEdit()
        self.mech_x_col_edit.setFixedWidth(40)
        self.mech_x_col_edit.setText("1")

        # nodeID
        self.mech_node_id_col_label = QLabel("Column for Node ID:")
        self.mech_node_id_col_edit = QLineEdit()
        self.mech_node_id_col_edit.setFixedWidth(40)
        self.mech_node_id_col_edit.setText("0")

        mech_row.addWidget(self.mech_mesh_path)
        mech_row.addWidget(self.mech_mesh_btn)
        mech_row.addWidget(self.mech_x_col_label)
        mech_row.addWidget(self.mech_x_col_edit)
        mech_row.addWidget(self.mech_node_id_col_label)
        mech_row.addWidget(self.mech_node_id_col_edit)
        layout.addWidget(self.mech_mesh_label)
        layout.addLayout(mech_row)

        # self.config_label = QLabel("Config File:")
        # self.config_path = QLineEdit()
        # self.config_btn = QPushButton("Browse")
        # self.config_btn.clicked.connect(self.browse_config)
        # layout.addWidget(self.config_label)
        # layout.addWidget(self.config_path)
        # layout.addWidget(self.config_btn)

        # output directory row
        self.outdir_label = QLabel("Output Directory:")
        outdir_row = QHBoxLayout()
        self.outdir_path = QLineEdit()
        self.outdir_btn = QPushButton("Browse")
        self.outdir_btn.clicked.connect(self.browse_outdir)
        layout.addWidget(self.outdir_label)
        outdir_row.addWidget(self.outdir_path)
        outdir_row.addWidget(self.outdir_btn)
        layout.addLayout(outdir_row)

    def browse_em_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select EM Folder")
        if folder:
            self.em_folder_path.setText(folder)

    def browse_mech_mesh(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Mechanical Mesh File")
        if file:
            self.mech_mesh_path.setText(file)

    # def browse_config(self):
    #     file, _ = QFileDialog.getOpenFileName(self, "Select Config File")
    #     if file:
    #         self.config_path.setText(file)

    def browse_outdir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.outdir_path.setText(folder)

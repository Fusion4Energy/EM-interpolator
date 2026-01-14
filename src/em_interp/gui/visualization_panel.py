# Visualization panel using PyVista
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt
import pyvista as pv
from pyvistaqt import QtInteractor


class VisualizationPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical)
        self.plotter_em = QtInteractor(self)
        self.plotter_mech = QtInteractor(self)
        splitter.addWidget(self.plotter_em.interactor)
        splitter.addWidget(self.plotter_mech.interactor)
        layout.addWidget(splitter)

    def display_mesh(
        self, mesh_em: pv.UnstructuredGrid, mesh_mech: pv.UnstructuredGrid
    ):
        self.plotter_em.clear()
        self.plotter_mech.clear()
        if mesh_em is not None:
            glyph_em = mesh_em.glyph(orient="vectors", scale="Force [N]", factor=0.1)
            self.plotter_em.add_mesh(glyph_em)
            self.plotter_em.reset_camera()
            self.plotter_em.render()
        if mesh_mech is not None:
            glyph_mech = mesh_mech.glyph(
                orient="vectors", scale="Force [N]", factor=0.1
            )
            self.plotter_mech.add_mesh(glyph_mech)
            self.plotter_mech.reset_camera()
            self.plotter_mech.render()

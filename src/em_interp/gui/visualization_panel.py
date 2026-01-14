# Visualization panel using PyVista
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QSlider,
    QLabel,
    QHBoxLayout,
)
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

        # Add two independent sliders for EM and Mech glyph scales
        slider_layout = QHBoxLayout()
        # EM slider
        self.scale_label_em = QLabel("EM Glyph Scale: 0.001")
        self.scale_slider_em = QSlider(Qt.Horizontal)
        self.scale_slider_em.setMinimum(1)  # 0.001
        self.scale_slider_em.setMaximum(100)  # 0.1
        self.scale_slider_em.setValue(1)
        self.scale_slider_em.setSingleStep(1)
        self.scale_slider_em.valueChanged.connect(self._on_scale_changed_em)
        slider_layout.addWidget(self.scale_label_em)
        slider_layout.addWidget(self.scale_slider_em)
        # Mech slider
        self.scale_label_mech = QLabel("Mech Glyph Scale: 0.001")
        self.scale_slider_mech = QSlider(Qt.Horizontal)
        self.scale_slider_mech.setMinimum(1)  # 0.001
        self.scale_slider_mech.setMaximum(100)  # 0.1
        self.scale_slider_mech.setValue(1)
        self.scale_slider_mech.setSingleStep(1)
        self.scale_slider_mech.valueChanged.connect(self._on_scale_changed_mech)
        slider_layout.addWidget(self.scale_label_mech)
        slider_layout.addWidget(self.scale_slider_mech)
        layout.addLayout(slider_layout)

        self._mesh_em = None
        self._mesh_mech = None
        self._glyph_scale_em = 0.001
        self._glyph_scale_mech = 0.001

    def display_mesh(
        self, mesh_em: pv.UnstructuredGrid, mesh_mech: pv.UnstructuredGrid
    ):
        self._mesh_em = mesh_em
        self._mesh_mech = mesh_mech
        self._update_glyphs_em()
        self._update_glyphs_mech()

    def _on_scale_changed_em(self, value):
        self._glyph_scale_em = 0.001 * value
        self.scale_label_em.setText(f"EM Glyph Scale: {self._glyph_scale_em:.3f}")
        self._update_glyphs_em()

    def _on_scale_changed_mech(self, value):
        self._glyph_scale_mech = 0.001 * value
        self.scale_label_mech.setText(f"Mech Glyph Scale: {self._glyph_scale_mech:.3f}")
        self._update_glyphs_mech()

    def _update_glyphs_em(self):
        self.plotter_em.clear()
        if self._mesh_em is not None:
            glyph_em = self._mesh_em.glyph(
                scale="Force [N]", orient=True, factor=self._glyph_scale_em
            )
            self.plotter_em.add_mesh(glyph_em)
            self.plotter_em.reset_camera()
            self.plotter_em.render()

    def _update_glyphs_mech(self):
        self.plotter_mech.clear()
        if self._mesh_mech is not None:
            glyph_mech = self._mesh_mech.glyph(
                scale="Force [N]", orient=True, factor=self._glyph_scale_mech
            )
            self.plotter_mech.add_mesh(glyph_mech)
            self.plotter_mech.reset_camera()
            self.plotter_mech.render()

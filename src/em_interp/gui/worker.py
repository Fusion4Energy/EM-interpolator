from PyQt5.QtCore import QThread, pyqtSignal


class InterpolationWorker(QThread):
    progress_changed = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, interpolator):
        super().__init__()
        self.interpolator = interpolator

    def run(self):
        # Example: Suppose interpolate_all accepts a callback for progress
        # If not, you may need to refactor interpolate_all to support progress reporting
        def progress_callback(percent):
            self.progress_changed.emit(percent)

        self.interpolator.interpolate_all(progress_callback=progress_callback)
        self.finished.emit()

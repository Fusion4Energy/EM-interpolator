"""Tests for InterpolationWorker class."""

import pytest
from unittest.mock import MagicMock

from em_interp.gui.worker import InterpolationWorker


class TestInterpolationWorker:
    """Tests for InterpolationWorker class."""

    def test_init(self, qapp):
        """Test InterpolationWorker initialization."""
        mock_interpolator = MagicMock()
        worker = InterpolationWorker(mock_interpolator)
        assert worker.interpolator == mock_interpolator

    def test_run(self, qapp):
        """Test worker run method."""
        mock_interpolator = MagicMock()
        worker = InterpolationWorker(mock_interpolator)
        
        # Mock the interpolate_all method
        def mock_interpolate_all(progress_callback=None):
            if progress_callback:
                progress_callback(50)
                progress_callback(100)
        
        mock_interpolator.interpolate_all = mock_interpolate_all
        
        # Track signals
        progress_values = []
        finished_called = []
        
        def on_progress(value):
            progress_values.append(value)
        
        def on_finished():
            finished_called.append(True)
        
        worker.progress_changed.connect(on_progress)
        worker.finished.connect(on_finished)
        
        # Run the worker
        worker.run()
        
        # Check that signals were emitted
        assert 50 in progress_values
        assert 100 in progress_values
        assert len(finished_called) == 1

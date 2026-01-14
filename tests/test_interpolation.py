import numpy as np
import pytest
from core.interpolation import MechTree
from core.config import InterpolationConfig, QUERY_TYPE, INTERPOLATION_KERNEL


class TestMechTree:
    @pytest.fixture
    def mechtree_data():
        X_Mech = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        X_EM = np.array(
            [
                [0.1, 0.0, 0.0],
                [0.0, 0.9, 0.0],
            ]
        )
        config = InterpolationConfig(
            method=QUERY_TYPE.RADIUS,
            param=1.0,
            kernel=INTERPOLATION_KERNEL.DISTANCE_WEIGHTED,
            max_distance=1.0,
            coincidence_tolerance=1e-6,
            multithread=False,
        )
        F_EM = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        )
        return X_Mech, X_EM, config, F_EM

    def test_kdtree_query_radius(self, mechtree_data):
        X_Mech, X_EM, config, F_EM = mechtree_data
        tree = MechTree(X_Mech, X_EM, config)
        idx = tree._run_query()
        assert len(idx) == X_EM.shape[0]
        for neighbors in idx:
            assert len(neighbors) > 0

    def test_interpolate(self, mechtree_data):
        X_Mech, X_EM, config, F_EM = mechtree_data
        tree = MechTree(X_Mech, X_EM, config)
        interpolated, unmapped = tree.interpolate(F_EM)
        assert interpolated.shape == (X_Mech.shape[0], 3)
        assert unmapped.shape == (1, 3)
        np.testing.assert_allclose(
            np.sum(interpolated, axis=0), np.sum(F_EM, axis=0), atol=1e-6
        )

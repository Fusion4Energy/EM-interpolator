import numpy as np
import pytest
from importlib.resources import files, as_file
from pathlib import Path

from em_interp.core.interpolation import MechTree, Interpolator
from em_interp.core.config import InterpolationConfig, QUERY_TYPE, INTERPOLATION_KERNEL

import tests.res.interpolation as res

RESOURCES = files(res)


class TestMechTree:
    @pytest.fixture
    def mechtree_data(self):
        X_Mech = np.array(
            [
                [-0.1, -0.1, -0.1],
                [1.5, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.5],
            ]
        )
        X_EM = np.array([[3.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0, 0, 0.7]])
        config = InterpolationConfig(
            method=QUERY_TYPE.RADIUS,
            param=1,
            kernel=INTERPOLATION_KERNEL.DISTANCE_WEIGHTED,
            max_distance=1,
            coincidence_tolerance=1e-6,
            multithread=False,
        )
        F_EM = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        return X_Mech, X_EM, config, F_EM

    def test_kdtree_query_radius(self, mechtree_data):
        X_Mech, X_EM, config, F_EM = mechtree_data
        tree = MechTree(X_Mech, X_EM, config)

        # test neighbours query
        assert tree.idx[0].tolist() == []
        assert tree.idx[1].tolist() == [2]

    def test_kdtree_query_knn(self, mechtree_data):
        X_Mech, X_EM, config, F_EM = mechtree_data
        config.method = QUERY_TYPE.K
        config.param = 2
        tree = MechTree(X_Mech, X_EM, config)

        # test neighbours query
        assert tree.idx[1].tolist() == [2, 0]

    def test_interpolate_distance(self, mechtree_data):
        X_Mech, X_EM, config, F_EM = mechtree_data
        tree = MechTree(X_Mech, X_EM, config)
        interpolated, unmapped = tree.interpolate(F_EM)

        assert np.linalg.norm(interpolated[1]) == 0.0  # no neighbours
        assert np.linalg.norm(interpolated[2]) == 1
        assert pytest.approx(np.linalg.norm(interpolated.sum(axis=0))) == 2 ** (1 / 2)
        assert np.linalg.norm(unmapped.sum()) == 1

    def test_interpolate_fem(self, mechtree_data):
        X_Mech, X_EM, config, F_EM = mechtree_data
        config.kernel = INTERPOLATION_KERNEL.FEM
        tree = MechTree(X_Mech, X_EM, config)
        interpolated, unmapped = tree.interpolate(F_EM)
        assert unmapped.sum() == 1


class TestInterpolator:
    @pytest.fixture
    def interpolator_fixture(self):
        config = InterpolationConfig(
            method=QUERY_TYPE.RADIUS,
            param=1,
            kernel=INTERPOLATION_KERNEL.DISTANCE_WEIGHTED,
            max_distance=1,
            coincidence_tolerance=1e-6,
            multithread=True,
        )
        file_idx = {"mech_node_id": 0, "mech_x": 1, "em_x": 1, "em_f": 4}

        with (
            as_file(RESOURCES.joinpath("mech_mesh.txt")) as mech_file,
            as_file(RESOURCES.joinpath("em")) as dummy_em_path,
        ):
            interpolator = Interpolator(
                dummy_em_path, mech_file, config, file_idx=file_idx
            )
        return interpolator

    def test_interpolate_all(self, interpolator_fixture):
        interpolator = interpolator_fixture
        interpolator.interpolate_all()

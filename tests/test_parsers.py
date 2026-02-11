from em_interp.core.parsers import parse_mech_mesh, parse_em_loads
import tests.res.parsers as res
from importlib.resources import files, as_file
import pytest

RES = files(res)


@pytest.mark.parametrize(
    ["mech_file", "X_col", "node_col"],
    [
        ["mech1.node", 1, 0],
    ],
)
def test_parse_mech_mesh(mech_file, X_col, node_col):
    with as_file(RES.joinpath(mech_file)) as file:
        X_Mech, Node_Number = parse_mech_mesh(file, X_col, node_col)


@pytest.mark.parametrize(
    ["em_file", "X_col", "F_col"],
    [
        ["em1.txt", 1, 4],
    ],
)
def test_parse_em_loads(em_file, X_col, F_col):
    with as_file(RES.joinpath(em_file)) as file:
        X_EM, F_EM = parse_em_loads(file, X_col, F_col)

from em_interp.core.config import INTERPOLATION_KERNEL, InterpolationConfig, QUERY_TYPE
from em_interp.core.interpolation import Interpolator
from pathlib import Path

# -------------------------
# --- User Input ----------
# -------------------------
CONFIG = InterpolationConfig(
    method=QUERY_TYPE.RADIUS,
    param=1,  # same unit as mesh coordinates if method is radius
    kernel=INTERPOLATION_KERNEL.DISTANCE_WEIGHTED,
    max_distance=1,  # same unit as mesh coordinates
    coincidence_tolerance=1e-6,  # same unit as mesh coordinates
    multithread=False,
)
# column indices for mech mesh and em loads files (starting from 0)
FILE_IDX = {"mech_node_id": 0, "mech_x": 1, "em_x": 1, "em_f": 4}

# all files to interpolate (mech mesh, em loads, output dir) - add as many as you want
TO_INTERPOLATE = [
    ("path/to/mech_mesh.node1", "path/to/em_loads1.txt", "path/to/output_dir1"),
    ("path/to/mech_mesh.node2", "path/to/em_loads2.txt", "path/to/output_dir2"),
]

BUILD_VTK = False  # set to True if you want to export forces to VTK (heavier)
# -------------------------
# --- End of user input ---
# -------------------------

# --- Code execution ---
for mech_path, em_path, output_dir in TO_INTERPOLATE:
    print(f"Interpolating on {mech_path}...")
    if not Path(output_dir).exists():
        Path(output_dir).mkdir(parents=True)
    interpolator = Interpolator(mech_path, em_path, CONFIG, FILE_IDX)
    interpolator.interpolate_all()
    interpolator.dump_interpolation_check(
        Path(output_dir, f"{Path(mech_path).stem}_checks.csv")
    )
    interpolator.export_to_ansys(Path(output_dir))
    if BUILD_VTK:
        interpolator.export_forces_to_vtk(Path(output_dir))  # a bit heavier
print("All done")

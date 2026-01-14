import numpy as np
import time
import logging
from sklearn.neighbors import KDTree
from sklearn.metrics.pairwise import euclidean_distances
import concurrent.futures
import os
from pathlib import Path
import pandas as pd
import pyvista as pv

from em_interp.core.parsers import parse_mech_mesh, parse_em_loads
from em_interp.core.config import InterpolationConfig, INTERPOLATION_KERNEL, QUERY_TYPE


class MechTree:
    def __init__(
        self, X_Mech: np.ndarray, X_EM: np.ndarray, config: InterpolationConfig
    ):
        """Intialize the KDTree for fast search in the mechanical nodes

        Parameters
        ----------
        X_Mech : np.ndarray
            point coordinates array of mechanical mesh nodes
        X_EM : np.ndarray
            point coordinates array of electromagnetic mesh centroids
        config : InterpolationConfig
            Configuration for the interpolation problem
        """
        logging.info("Building KDTree...")
        tic = time.perf_counter()
        self.tree = KDTree(X_Mech)
        toc = time.perf_counter()
        logging.info("Elapsed Time:")
        logging.info(toc - tic)

        self.X_Mech: np.ndarray = X_Mech
        self.X_EM: np.ndarray = X_EM
        self.config: InterpolationConfig = config
        self.idx = self._run_query()

    def _run_query(self):
        """run the requested query by config"""
        logging.info("Extracting nodes from KDTree...")
        tic = time.perf_counter()
        if self.config.method == QUERY_TYPE.RADIUS:
            idx = self.tree.query_radius(self.X_EM, r=self.config.param)
        elif self.config.method == QUERY_TYPE.K:
            # check for int already done in config
            idx = self.tree.query(self.X_EM, k=self.config.param)[1]

        toc = time.perf_counter()
        logging.info("Elapsed Time:")
        logging.info(toc - tic)

        return idx

    def interpolate(self, F_EM: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Perform the interpolation from EM to Mech nodes

        Parameters
        ----------
        F_EM : np.ndarray
            Nodal force array from EM analysis

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Interpolated forces on mechanical nodes and unmapped forces
        """
        logging.info("Performing interpolation...")
        tic = time.perf_counter()

        if self.config.multithread:
            num_threads = os.cpu_count() or 1
            block_size = int(np.ceil(self.X_EM.shape[0] / num_threads))
            blocks = [
                slice(i * block_size, min((i + 1) * block_size, self.X_EM.shape[0]))
                for i in range(num_threads)
            ]

            results = []
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=num_threads
            ) as executor:
                futures = [
                    executor.submit(
                        _interpolate_block,
                        self.X_EM,
                        self.X_Mech,
                        self.idx,
                        block,
                        F_EM,
                        self.config,
                    )
                    for block in blocks
                ]
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())

            interpolated = np.zeros([self.X_Mech.shape[0], 3])
            unmapped = np.zeros([1, 3])
            for interp, unm in results:
                interpolated += interp
                unmapped += unm
        else:
            interpolated, unmapped = _interpolate_block(
                self.X_EM,
                self.X_Mech,
                self.idx,
                slice(0, self.X_EM.shape[0]),
                F_EM,
                self.config,
            )

        toc = time.perf_counter()
        logging.info("Elapsed Time:")
        logging.info(toc - tic)

        return interpolated, unmapped


class Interpolator:
    def __init__(
        self,
        path_to_em_folder: str,
        path_to_mech_mesh: str,
        config: InterpolationConfig,
        file_idx: dict | None = None,
    ):
        """Class to handle the interpolation operations

        Parameters
        ----------
        path_to_em_folder : str
            path were the EM input forces are stored
        path_to_mech_mesh : str
            path to the mechanical mesh file
        config : InterpolationConfig
            configuration for the interpolation problem
        file_idx : dict | None, optional
            dictionary with file indices for parsing, by default None
        """
        # parse all necessary files
        if file_idx is None:
            self.mech_x, self.node_numbers = parse_mech_mesh(Path(path_to_mech_mesh))
        else:
            self.mech_x, self.node_numbers = parse_mech_mesh(
                Path(path_to_mech_mesh),
                col_mesh_nd=file_idx.get("mech_node_id", 0),
                col_mesh_x=file_idx.get("mech_x", 1),
            )
        self.config = config

        # parse all EM files to interpolate
        em_forces = {}

        # raise an error if folder does not exist or is empty
        if not os.path.exists(path_to_em_folder):
            raise FileNotFoundError(f"EM folder {path_to_em_folder} does not exist.")
        if len(os.listdir(path_to_em_folder)) == 0:
            raise FileNotFoundError(f"EM folder {path_to_em_folder} is empty.")

        for file in os.listdir(path_to_em_folder):
            file_path = Path(path_to_em_folder, file)
            name = file_path.stem
            if file_idx is None:
                em_x, em_f = parse_em_loads(file_path)
            else:
                em_x, em_f = parse_em_loads(
                    file_path,
                    col_em_x=file_idx.get("em_x", 0),
                    col_em_f=file_idx.get("em_f", 3),
                    vol_col=file_idx.get("em_vol", None),
                )
            em_forces[name] = em_f

        self.em_forces = em_forces

        # Intialize the KDtree and precompute the queries (assumption that em_x is the same)
        self.em_x = em_x
        self.mech_tree = MechTree(self.mech_x, em_x, self.config)
        self.interpolated_results = None
        self.mech_vtk = {}
        self.em_vtk = {}

    def interpolate_all(self):
        """Go through all em forces file and interpolate them"""
        interpolated_results = {}
        for name, F_EM in self.em_forces.items():
            interpolated, unmapped = self.mech_tree.interpolate(F_EM)
            interpolated_results[name] = {
                "interpolated": interpolated,
                "unmapped": unmapped,
            }
        self.interpolated_results = interpolated_results

    def dump_interpolation_check(self, outfile: Path, pole: np.ndarray | None = None):
        """Dump a csv file with the interpolation check results
        Parameters
        ----------
        outfile : Path
            output csv file path
        pole : np.ndarray | None, optional
            reference pole for moment calculation, by default None (0,0,0)
        """
        rows = []
        for name in self.em_forces.keys():
            row = self._compute_resultants(name, pole)
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(outfile, index=False)
        logging.info(f"Interpolation check dumped to {outfile}")

    def export_to_ansys(self, outdir: Path):
        """Export each interpolated result to an ANSYS format

        Parameters
        ----------
        outdir : Path
            output directory for the interpolated files

        """
        if self.interpolated_results is None:
            raise ValueError(
                "No interpolated results found. Run interpolate_all() first."
            )

        for name, result in self.interpolated_results.items():
            outfile = Path(outdir, f"interpolated_{name}.txt")
            df = pd.DataFrame(result["interpolated"], columns=["Fx", "Fy", "Fz"])
            df.index = self.node_numbers.astype(int)
            df.reset_index(inplace=True)
            df.to_csv(outfile, index=False, header=False)
        
        logging.info(f"ANSYS files exported to {outdir}")

    def _compute_resultants(self, name: str, pole: np.ndarray | None = None) -> dict:
        if pole is None:
            pole = np.array([0.0, 0.0, 0.0])

        F_EM = self.em_forces[name]
        if self.interpolated_results is None:
            raise ValueError(
                "No interpolated results found. Run interpolate_all() first."
            )
        F_Mech = self.interpolated_results[name]["interpolated"]

        R_F_EM = np.sum(F_EM, axis=0)
        R_F_Mech = np.sum(F_Mech, axis=0)

        M_EM = np.cross(self.em_x - pole, F_EM)
        M_Mech = np.cross(self.mech_x - pole, F_Mech)

        R_M_EM = np.sum(M_EM, axis=0)
        R_M_Mech = np.sum(M_Mech, axis=0)

        f_err_comp = np.divide(R_F_EM - R_F_Mech, R_F_EM)
        m_err_comp = np.divide(R_M_EM - R_M_Mech, R_M_EM)

        # give some warning if differences are very high
        if np.any(np.abs(f_err_comp) > 0.2):
            logging.warning(f"High difference in force resultant for {name}")
        if np.any(np.abs(m_err_comp) > 0.2):
            logging.warning(f"High difference in moment resultant for {name}")

        row = {
            "Name": name,
            "Fx [N]": R_F_EM[0],
            "Fy [N]": R_F_EM[1],
            "Fz [N]": R_F_EM[2],
            "Mx [Nm]": R_M_EM[0],
            "My [Nm]": R_M_EM[1],
            "Mz [Nm]": R_M_EM[2],
            "dFx [%]": f_err_comp[0] * 100,
            "dFy [%]": f_err_comp[1] * 100,
            "dFz [%]": f_err_comp[2] * 100,
            "dMx [%]": m_err_comp[0] * 100,
            "dMy [%]": m_err_comp[1] * 100,
            "dMz [%]": m_err_comp[2] * 100,
            "Unmapped_EM_Force [N]": np.linalg.norm(
                self.interpolated_results[name]["unmapped"]
            ),
        }

        return row

    def build_vtk_output(self):
        """Build the VTK output files for visualization

        Parameters
        ----------
        outdir : Path
            output directory for the interpolated files

        """
        if self.interpolated_results is None:
            raise ValueError(
                "No interpolated results found. Run interpolate_all() first."
            )
        # build and dump the vtks
        for name in self.em_forces.keys():
            # Mech
            pdata = pv.PolyData(self.mech_x)
            pdata["Fx [N]"] = self.interpolated_results[name]["interpolated"][:, 0]
            pdata["Fy [N]"] = self.interpolated_results[name]["interpolated"][:, 1]
            pdata["Fz [N]"] = self.interpolated_results[name]["interpolated"][:, 2]
            pdata["Force [N]"] = self.interpolated_results[name]["interpolated"]
            self.mech_vtk[name] = pdata

            # EM
            pdata_em = pv.PolyData(self.em_x)
            pdata_em["Fx [N]"] = self.em_forces[name][:, 0]
            pdata_em["Fy [N]"] = self.em_forces[name][:, 1]
            pdata_em["Fz [N]"] = self.em_forces[name][:, 2]
            pdata_em["Force [N]"] = self.em_forces[name]
            self.em_vtk[name] = pdata_em

    def export_forces_to_vtk(self, outdir: Path):
        """Export each interpolated result to a different VTK

        Parameters
        ----------
        outdir : Path
            output directory for the interpolated files

        """
        if self.interpolated_results is None:
            raise ValueError(
                "No interpolated results found. Run interpolate_all() first."
            )

        # dump the vtks
        # check first if vtk where built
        if not self.mech_vtk or not self.em_vtk:
            logging.warning("vtk were not built, building now...")
            self.build_vtk_output()

        for name in self.em_forces.keys():
            # Mech
            outfile = Path(outdir, f"{name}_interpolated.vtk")
            self.mech_vtk[name].save(outfile)

            # EM
            outfile_em = Path(outdir, f"{name}_EM.vtk")
            self.em_vtk[name].save(outfile_em)
        
        logging.info(f"VTK files exported to {outdir}")


def _interpolate_block(
    X_EM: np.ndarray,
    X_Mech: np.ndarray,
    idx_query: np.ndarray,
    EM_indices: slice,
    F_EM: np.ndarray,
    config: InterpolationConfig,
) -> tuple[np.ndarray, np.ndarray]:
    interpolated = np.zeros([X_Mech.shape[0], 3])
    unmapped = np.zeros([1, 3])

    i = EM_indices.start
    for em_node in X_EM[EM_indices]:
        mech_nodes_idx = idx_query[i]
        mapped = False

        # Ensure query is not empty
        if mech_nodes_idx.shape[0] > 0:
            distances = euclidean_distances(
                X_Mech[mech_nodes_idx], em_node.reshape(1, -1)
            )
            # clip the mech nodes based on max distance
            keep = distances.flatten() < config.max_distance
            distances = distances[keep]
            mech_nodes_idx = mech_nodes_idx[keep]

            # Ensure that after clipping something remains
            if mech_nodes_idx.shape[0] == 0:
                unmapped = unmapped + F_EM[i, :]
                i = i + 1
                continue

            # if coincident node found, assign directly
            if distances[0] < config.coincidence_tolerance:
                logging.debug(f"Coincident node found {X_EM[i, :]}")
                interpolated[mech_nodes_idx[0], :] = [
                    F_EM[i, 0],
                    F_EM[i, 1],
                    F_EM[i, 2],
                ]
                i = i + 1
                continue

            # If nothing above, perform the interpolation
            # This will adjourn the "interpolated" array
            if config.kernel == INTERPOLATION_KERNEL.DISTANCE_WEIGHTED:
                mapped = _dist_weight_kernel(
                    distances,
                    mech_nodes_idx,
                    i,
                    F_EM,
                    interpolated,
                )
            elif config.kernel == INTERPOLATION_KERNEL.FEM:
                mapped = _FEM_interpolation_kernel(
                    distances,
                    mech_nodes_idx,
                    i,
                    X_Mech,
                    X_EM,
                    F_EM,
                    interpolated,
                )
        if not mapped:
            unmapped = unmapped + F_EM[i, :]
        i += 1
    return interpolated, unmapped


# --- interpolation kernels ---
def _FEM_interpolation_kernel(
    Li: np.ndarray,
    mech_idx: np.ndarray,
    EM_index: int,
    X_Mech: np.ndarray,
    X_EM: np.ndarray,
    F_EM: np.ndarray,
    interpolated: np.ndarray,
) -> bool:
    roi = X_Mech[mech_idx] - X_EM[EM_index]
    vi = np.divide(roi, Li)

    if vi.shape[0] > 0:
        # Nt=idx[i].shape[0]
        Nt = vi.shape[0]
        A = np.zeros([3, 3])
        for j in range(0, vi.shape[0]):
            dist = Li[j][0]
            l = vi[j, 0]
            m = vi[j, 1]
            n = vi[j, 2]
            A[0, 0] += (1.0 / dist) * l**2.0
            A[0, 1] += (1.0 / dist) * l * m
            A[0, 2] += (1.0 / dist) * l * n

            A[1, 0] += (1.0 / dist) * l * m
            A[1, 1] += (1.0 / dist) * m**2.0
            A[1, 2] += (1.0 / dist) * m * n
            A[2, 0] += (1.0 / dist) * l * n
            A[2, 1] += (1.0 / dist) * m * n
            A[2, 2] += (1.0 / dist) * n**2.0

        F = np.zeros([3, 1])
        F[0] = F_EM[EM_index, 0]
        F[1] = F_EM[EM_index, 1]
        F[2] = F_EM[EM_index, 2]

        R = np.zeros([3 * vi.shape[0], 1])

        if abs(np.linalg.det(A)) > 1e-10:
            U = np.linalg.solve(A, F)

            for j in range(0, vi.shape[0]):
                dist = Li[j][0]
                l = vi[j, 0]
                m = vi[j, 1]
                n = vi[j, 2]
                A[0, 0] = (1.0 / dist) * l**2.0
                A[0, 1] = (1.0 / dist) * l * m
                A[0, 2] = (1.0 / dist) * l * n

                A[1, 0] = (1.0 / dist) * l * m
                A[1, 1] = (1.0 / dist) * m**2.0
                A[1, 2] = (1.0 / dist) * m * n
                A[2, 0] = (1.0 / dist) * l * n
                A[2, 1] = (1.0 / dist) * m * n
                A[2, 2] = (1.0 / dist) * n**2.0
                R[3 * j : 3 * j + 3] = np.dot(A, U)

        interpolated[mech_idx, :] += R.reshape(Nt, 3)
    else:
        return False  # not possible to map
    return True


def _dist_weight_kernel(
    Li: np.ndarray,
    mech_idx: np.ndarray,
    EM_index: int,
    F_EM: np.ndarray,
    interpolated: np.ndarray,
) -> bool:
    """simply distribute the EM force components proportionally to the inverse of the
    distance"""
    max_distance = np.max(Li)
    weights = 1 / (Li / max_distance)  # inverse distance weights
    weights /= np.sum(weights)  # normalize the weights so that they sum to 1
    interpolated[mech_idx, :] += weights * F_EM[EM_index]

    return True

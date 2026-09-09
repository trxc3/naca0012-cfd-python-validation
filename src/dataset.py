import os
import pandas as pd
from src.metrics import compute_cl_from_cp
from src.parser import extract_metadata_from_filename, parse_fluent_xy


class SimulationDataset:
    """Object representing a single CFD run, containing profiles, integrated metrics, and wall y+ checks."""

    def __init__(self, cp_file_path: str, yplus_file_path: str = None):
        self.cp_file_path = cp_file_path
        self.yplus_file_path = yplus_file_path

        # Extract metadata
        self.metadata = extract_metadata_from_filename(cp_file_path)
        self.mesh_level = self.metadata["mesh_level"]
        self.aoa = self.metadata["aoa"]

        # Parse CSV profiles into DataFrames
        self.df_cp = parse_fluent_xy(cp_file_path)
        self.df_yplus = (
            parse_fluent_xy(yplus_file_path) if yplus_file_path else None
        )

        # Compute key metrics
        self.cl_integrated = compute_cl_from_cp(self.df_cp)
        self.max_yplus = (
            float(self.df_yplus["value"].max())
            if self.df_yplus is not None
            else None
        )

    def summary(self) -> dict:
        """Returns a clean summary dictionary of the dataset metrics."""
        return {
            "mesh_level": self.mesh_level,
            "aoa": self.aoa,
            "cl_integrated": round(self.cl_integrated, 5),
            "max_yplus": (
                round(self.max_yplus, 3) if self.max_yplus is not None else "N/A"
            ),
        }
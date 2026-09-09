import pandas as pd
from src.dataset import SimulationDataset
from src.metrics import calculate_gci
from src.parser import load_nasa_benchmark
from src.visualization import (
    plot_cl_alpha_curve,
    plot_cp_comparison,
    plot_gci_uncertainty,
)

# Load CFD Fine Mesh Simulation
sim_fine = SimulationDataset(
    cp_file_path="data/raw/fluent_naca0012_mesh_fine_aoa4.csv",
    yplus_file_path="data/raw/fluent_naca0012_mesh_fine_yplus_aoa4.csv",
)

#Mock NASA Ladson Experimental Cl vs Alpha Data for context
#(Ladson Exp: Alpha = [-2, 0, 2, 4, 6, 8, 10], Cl ≈ [-0.2, 0.0, 0.21, 0.42, 0.63, 0.84, 1.02])
nasa_cl_data = pd.DataFrame(
    {
        "aoa": [-2, 0, 2, 4, 6, 8, 10],
        "cl": [-0.20, 0.00, 0.21, 0.42, 0.63, 0.84, 1.02],
    }
)

# Generate Cl vs Alpha Plot Overlaying CFD Point on NASA Curve
plot_cl_alpha_curve(
    cfd_aoa=[4],
    cfd_cl=[sim_fine.cl_integrated],
    nasa_cl_df=nasa_cl_data,
    save_path="reports/figures/cl_alpha_curve.png",
)
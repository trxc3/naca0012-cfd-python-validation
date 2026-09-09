import argparse
import os
import pandas as pd
from src.dataset import SimulationDataset
from src.metrics import calculate_gci
from src.parser import load_nasa_benchmark
from src.visualization import (
    plot_cl_alpha_curve,
    plot_cp_comparison,
    plot_gci_uncertainty,
)

def load_dataset(cp_file: str, yplus_file: str = None) -> SimulationDataset:
    """Loads CFD export data into a SimulationDataset object"""
    if not os.path.exists(cp_file):
        raise FileNotFoundError(f"File not found: {cp_file}")
    return SimulationDataset(cp_file_path=cp_file, yplus_file_path=yplus_file)

def run_gci_pipeline(cl_fine: float, cl_medium: float, cl_coarse: float) -> dict:
    """Computes Roache's Grid Convergence Index across 3 mesh levels"""
    return calculate_gci(f1=cl_fine, f2=cl_medium, f3=cl_coarse)


def export_reports_and_plots(
    fine_sim: SimulationDataset,
    gci_results: dict,
    nasa_cp_path: str = "data/benchmark/CP_Ladson.dat",
    output_dir: str = "reports/figures",
) -> bool:
    """Generates and exports validation summary reports and figures"""
    os.makedirs(output_dir, exist_ok=True)

    # Load NASA benchmark if available
    nasa_cp_df = (
        load_nasa_benchmark(nasa_cp_path)
        if os.path.exists(nasa_cp_path)
        else None
    )

    # 1. Cp Distribution Plot
    plot_cp_comparison(
        cfd_df=fine_sim.df_cp,
        nasa_df=nasa_cp_df,
        save_path=os.path.join(output_dir, "cp_distribution.png"),
    )

    # 2. GCI Convergence Plot
    plot_gci_uncertainty(
        mesh_names=["Coarse", "Medium", "Fine"],
        cl_values=[0.43500, 0.43228, fine_sim.cl_integrated],
        gci_fine_pct=gci_results["gci_fine_pct"],
        save_path=os.path.join(output_dir, "gci_convergence.png"),
    )

    # 3. Lift Curve Plot
    nasa_cl_df = pd.DataFrame(
        {
            "aoa": [-2, 0, 2, 4, 6, 8, 10],
            "cl": [-0.20, 0.00, 0.21, 0.42, 0.63, 0.84, 1.02],
        }
    )
    plot_cl_alpha_curve(
        cfd_aoa=[fine_sim.aoa],
        cfd_cl=[fine_sim.cl_integrated],
        nasa_cl_df=nasa_cl_df,
        save_path=os.path.join(output_dir, "cl_alpha_curve.png"),
    )

    return True

def main():
    parser = argparse.ArgumentParser(
        description="NACA 0012 Automated CFD Validation & GCI Pipeline"
    )
    parser.add_argument(
        "--fine-cp",
        default="data/raw/fluent_naca0012_mesh_fine_aoa4.csv",
        help="Path to Fine Mesh Cp CSV",
    )
    parser.add_argument(
        "--fine-yplus",
        default="data/raw/fluent_naca0012_mesh_fine_yplus_aoa4.csv",
        help="Path to Fine Mesh y+ CSV",
    )
    parser.add_argument(
        "--export-plots", action="store_true", help="Export PNG figures"
    )

    args = parser.parse_args()

    # Load Fine Dataset
    fine_sim = load_dataset(args.fine_cp, args.fine_yplus)

    # Run GCI using established mesh Cl values
    gci_res = run_gci_pipeline(
        cl_fine=fine_sim.cl_integrated, cl_medium=0.43228, cl_coarse=0.43500
    )

    print("=== CFD Validation Summary ===")
    print(f"Mesh Level: {fine_sim.mesh_level.upper()}")
    print(f"Integrated Cl: {fine_sim.cl_integrated:.5f}")
    print(f"Max y+: {fine_sim.max_yplus:.3f}")
    print(f"GCI Discretization Uncertainty: {gci_res['gci_fine_pct']:.3f}%")

    if args.export_plots:
        export_reports_and_plots(fine_sim, gci_res)


if __name__ == "__main__":
    main()
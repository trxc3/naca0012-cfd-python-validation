import os
import pytest
from project import export_reports_and_plots, load_dataset, run_gci_pipeline

def test_load_dataset():
    """Tests loading a valid CFD CSV file into SimulationDataset"""
    sim = load_dataset("data/raw/fluent_naca0012_mesh_fine_aoa4.csv")
    assert sim.mesh_level == "fine"
    assert sim.aoa == 4
    assert sim.cl_integrated == pytest.approx(0.40431, abs=1e-3)


def test_load_dataset_missing_file():
    """Tests exception handling for non-existent file paths"""
    with pytest.raises(FileNotFoundError):
        load_dataset("data/raw/non_existent_file.csv")


def test_run_gci_pipeline():
    """Tests GCI calculation math and p-order capping behavior"""
    gci = run_gci_pipeline(cl_fine=0.40431, cl_medium=0.43228, cl_coarse=0.43500)
    assert gci["order_p"] == 2.0
    assert gci["gci_fine_pct"] == pytest.approx(8.653, abs=1e-2)


def test_export_reports_and_plots(tmp_path):
    """Tests figure export pipeline writing files to directory"""
    sim = load_dataset("data/raw/fluent_naca0012_mesh_fine_aoa4.csv")
    gci = run_gci_pipeline(0.40431, 0.43228, 0.43500)

    out_dir = tmp_path / "figures"
    result = export_reports_and_plots(
        sim, gci, nasa_cp_path="data/benchmark/CP_Ladson.dat", output_dir=str(out_dir)
    )

    assert result is True
    assert os.path.exists(out_dir / "cp_distribution.png")
    assert os.path.exists(out_dir / "gci_convergence.png")
    assert os.path.exists(out_dir / "cl_alpha_curve.png")
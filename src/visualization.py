import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parse_ladson_dat(file_path: str):
    """Parses Tecplot-formatted Ladson CP_Ladson.dat benchmark file."""
    zones = {}
    current_zone = None
    data_lines = []

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("variables"):
                continue

            if line.startswith("zone"):
                if current_zone and data_lines:
                    zones[current_zone] = np.array(data_lines, dtype=float)
                    data_lines = []
                current_zone = line.split("t=")[-1].strip('"')
            else:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        data_lines.append([float(parts[0]), float(parts[1])])
                    except ValueError:
                        continue

    if current_zone and data_lines:
        zones[current_zone] = np.array(data_lines, dtype=float)

    return zones


def plot_cp_comparison(
    cfd_df: pd.DataFrame,
    nasa_df: pd.DataFrame = None,
    title: str = r"NACA 0012 Surface Pressure Distribution ($\alpha = 4^\circ$)",
    save_path: str = None,
):
    """Generates publication-grade Cp distribution plot with inverted Y-axis."""
    plt.figure(figsize=(8, 6), dpi=300)

    cp_col = "value" if "value" in cfd_df.columns else "cp"
    x_col = "x_c" if "x_c" in cfd_df.columns else "x"

    # Separate upper and lower CFD surfaces
    y_col = None
    for col in ["y_c", "y", "y-coordinate", "y_coordinate"]:
        if col in cfd_df.columns:
            y_col = col
            break

    if y_col is not None:
        upper = cfd_df[cfd_df[y_col] >= 0].sort_values(x_col)
        lower = cfd_df[cfd_df[y_col] < 0].sort_values(x_col)
    else:
        temp_df = cfd_df.copy().sort_values(x_col)
        temp_df["x_bin"] = pd.qcut(temp_df[x_col], q=min(len(temp_df) // 2, 100), duplicates="drop")
        upper = temp_df.groupby("x_bin", observed=True).apply(lambda g: g.loc[g[cp_col].idxmin()]).reset_index(drop=True)
        lower = temp_df.groupby("x_bin", observed=True).apply(lambda g: g.loc[g[cp_col].idxmax()]).reset_index(drop=True)

    plt.plot(upper[x_col], upper[cp_col], label=r"Ansys Fluent (Upper Surface)", color="#0055A5", linewidth=2)
    plt.plot(lower[x_col], lower[cp_col], label=r"Ansys Fluent (Lower Surface)", color="#0055A5", linestyle="--", linewidth=2)

    # Load and parse CP_Ladson.dat benchmark file
    benchmark_path = os.path.join("data", "benchmark", "CP_Ladson.dat")
    if os.path.exists(benchmark_path):
        zones = parse_ladson_dat(benchmark_path)
        
        # Interpolate Cp between alpha=0 deg and alpha=10 deg zones (Re=3M)
        z0_name = [z for z in zones if "Re=3 million" in z and "alpha=.0083" in z]
        z10_name = [z for z in zones if "Re=3 million" in z and "alpha=10.0130" in z]

        if z0_name and z10_name:
            arr0 = zones[z0_name[0]]
            arr10 = zones[z10_name[0]]
            
            # Linear interpolation for alpha = 4 degrees
            alpha_target = 4.0
            a0, a10 = 0.0083, 10.0130
            weight = (alpha_target - a0) / (a10 - a0)
            arr_interp_cp = arr0[:, 1] + weight * (arr10[:, 1] - arr0[:, 1])
            
            le_idx = np.argmin(arr0[:, 0])
            
            plt.scatter(
                arr0[: le_idx + 1, 0],
                arr_interp_cp[: le_idx + 1],
                label=r"NASA Exp Upper ($\alpha \approx 4^\circ$)",
                color="#D9534F",
                marker="o",
                facecolors="none",
                s=35,
                zorder=4,
            )
            plt.scatter(
                arr0[le_idx:, 0],
                arr_interp_cp[le_idx:],
                label=r"NASA Exp Lower ($\alpha \approx 4^\circ$)",
                color="#5CB85C",
                marker="s",
                facecolors="none",
                s=35,
                zorder=4,
            )

    plt.gca().invert_yaxis()
    plt.xlabel(r"Normalized Chord Location ($x/c$)", fontsize=12)
    plt.ylabel(r"Pressure Coefficient ($C_p$)", fontsize=12)
    plt.title(title, fontsize=13, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(frameon=True, loc="best")
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Plot saved to: {save_path}")

    plt.close()


def plot_gci_uncertainty(
    mesh_names: list,
    cl_values: list,
    gci_fine_pct: float,
    save_path: str = None,
):
    """Generates Lift Coefficient grid convergence plot with GCI error bars."""
    plt.figure(figsize=(7, 5), dpi=300)

    yerr = [0.0, 0.0, cl_values[2] * (gci_fine_pct / 100.0)]

    plt.errorbar(
        mesh_names,
        cl_values,
        yerr=yerr,
        fmt="-o",
        color="#2E4053",
        ecolor="#C0392B",
        capsize=5,
        capthick=1.5,
        linewidth=2,
        markersize=7,
        label=r"$C_L$ Convergence w/ Fine GCI Error",
    )

    plt.xlabel("Mesh Refinement Level", fontsize=12)
    plt.ylabel(r"Integrated Lift Coefficient ($C_L$)", fontsize=12)
    plt.title("Grid Convergence Index (GCI) Analysis", fontsize=13, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="best")
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Plot saved to: {save_path}")

    plt.close()


def plot_cl_alpha_curve(
    cfd_aoa: list,
    cfd_cl: list,
    nasa_cl_df: pd.DataFrame = None,
    save_path: str = None,
):
    """Plots Lift Coefficient vs Angle of Attack comparing CFD against NASA Experimental data and Thin Airfoil Theory."""
    plt.figure(figsize=(8, 6), dpi=300)

    if nasa_cl_df is not None:
        plt.plot(
            nasa_cl_df["aoa"],
            nasa_cl_df["cl"],
            "o--",
            color="#D9534F",
            label=r"NASA Ladson Exp ($Re=3\times 10^6$)",
            markersize=6,
            linewidth=1.5,
        )

    alpha_rad = np.radians(np.linspace(-2, 10, 50))
    cl_theoretical = 2 * np.pi * alpha_rad
    plt.plot(
        np.degrees(alpha_rad),
        cl_theoretical,
        ":",
        color="black",
        label=r"Thin Airfoil Theory ($2\pi / \text{rad}$)",
        alpha=0.7,
    )

    plt.scatter(
        cfd_aoa,
        cfd_cl,
        color="#0055A5",
        s=100,
        zorder=5,
        label=r"Ansys Fluent ($k$-$\omega$ SST) [$\alpha=4^\circ$]",
    )

    plt.xlabel(r"Angle of Attack $\alpha$ (degrees)", fontsize=12)
    plt.ylabel(r"Lift Coefficient ($C_L$)", fontsize=12)
    plt.title(
        r"NACA 0012 Lift Curve Validation ($Re = 3 \times 10^6$)",
        fontsize=13,
        fontweight="bold",
    )
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="best", frameon=True)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Plot saved to: {save_path}")

    plt.close()
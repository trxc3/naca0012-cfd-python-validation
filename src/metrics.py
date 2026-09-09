import numpy as np
import pandas as pd


def compute_cl_from_cp(df: pd.DataFrame) -> float:
    """Calculates Lift Coefficient (Cl) by integrating (Cp_lower - Cp_upper) over normalized chord x/c."""
    # Group by x/c to separate upper surface (min Cp) and lower surface (max Cp)
    grouped = df.groupby("x_c")["value"].agg(["min", "max"]).reset_index()

    x = grouped["x_c"].values
    cp_upper = grouped["min"].values  # Suction side
    cp_lower = grouped["max"].values  # Pressure side

    # Cl = ∫ (Cp_lower - Cp_upper) d(x/c)
    cl_integrated = np.trapezoid(cp_lower - cp_upper, x)
    return float(cl_integrated)


def calculate_gci(
    f1: float,
    f2: float,
    f3: float,
    r: float = 1.414,
    fs: float = 1.25,
    p_theoretical: float = 2.0,
) -> dict:
    """Computes Roache's Grid Convergence Index (GCI), capping p at theoretical order (2.0)."""
    e21 = (f2 - f1) / f1 if f1 != 0 else 0.0

    diff_21 = f2 - f1
    diff_32 = f3 - f2

    # Calculate apparent order p
    if diff_21 != 0 and diff_32 != 0 and (diff_32 / diff_21) > 0:
        p = np.abs(np.log(np.abs(diff_32 / diff_21)) / np.log(r))
        p = min(p, p_theoretical)  # Cap p at theoretical spatial scheme order
    else:
        p = p_theoretical

    denominator = (r**p) - 1.0
    gci_fine = (
        (fs * np.abs(e21)) / denominator * 100.0 if denominator != 0 else 0.0
    )

    return {
        "order_p": float(p),
        "relative_error_21_pct": float(np.abs(e21) * 100.0),
        "gci_fine_pct": float(gci_fine),
    }
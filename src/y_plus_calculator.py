import numpy as np

def calculate_first_cell_height(reynolds_num: float, chord_length: float = 1.0, target_y_plus: float = 1.0) -> float:
    """Calculates the required first cell height (m) for a given Re and target y+."""
    # Schlichting skin friction coefficient estimation
    c_f = (2.0 * np.log10(reynolds_num) - 0.65) ** (-2.3)
    
    # Friction velocity ratio u_tau / U_inf
    u_tau_ratio = np.sqrt(c_f / 2.0)
    
    # First cell height delta_y (meters)
    delta_y = (target_y_plus * chord_length) / (reynolds_num * u_tau_ratio)
    return delta_y


if __name__ == "__main__":
    Re = 3e6
    chord = 1.0  # meters
    y_plus = 1.0
    
    y_first = calculate_first_cell_height(Re, chord, y_plus)
    
    print("\n================ CFD Boundary Layer Result ================")
    print(f"Target y+                 : {y_plus}")
    print(f"Reynolds Number           : {Re:.1e}")
    print(f"Calculated First Cell Height: {y_first:.4e} m ({y_first*1e6:.2f} µm)")
    print("===========================================================\n")
import os
import numpy as np

def generate_naca0012_points(num_points: int = 150, chord: float = 1.0, sharp_te: bool = True):
#Generates NACA 0012 profile coordinates for Ansys SpaceClaim and DesignModeler.
  
    os.makedirs("data", exist_ok=True)
    
    # 1. Cosine Spacing (clusters points near LE and TE)
    beta = np.linspace(0, np.pi, num_points)
    x = 0.5 * chord * (1.0 - np.cos(beta))
    
    # 2. NACA 0012 Thickness Formula
    # Using -0.1036 forces exact zero thickness at trailing edge (sharp TE)
    a4 = -0.1036 if sharp_te else -0.1015
    
    yt = 5 * 0.12 * chord * (
        0.2969 * np.sqrt(x / chord) 
        - 0.1260 * (x / chord) 
        - 0.3516 * (x / chord)**2 
        + 0.2843 * (x / chord)**3 
        + a4 * (x / chord)**4
    )
    
    # 3. Create Continuous Closed Loop (TE -> LE -> TE)
    x_upper = x[::-1]
    y_upper = yt[::-1]
    
    x_lower = x[1:]
    y_lower = -yt[1:]
    
    x_coords = np.concatenate([x_upper, x_lower])
    y_coords = np.concatenate([y_upper, y_lower])
    
    # Force exact loop closure if endpoints differ slightly
    if not (np.isclose(x_coords[0], x_coords[-1]) and np.isclose(y_coords[0], y_coords[-1])):
        x_coords = np.append(x_coords, x_coords[0])
        y_coords = np.append(y_coords, y_coords[0])

    # 4. Clean up floating-point -0.0 artifacts
    x_coords = np.where(np.abs(x_coords) < 1e-12, 0.0, x_coords) + 0.0
    y_coords = np.where(np.abs(y_coords) < 1e-12, 0.0, y_coords) + 0.0

    # 5. Save SpaceClaim Format (Requires 3d=true header + SPACE delimiters)
    sc_path = os.path.join("data", "naca0012_spaceclaim.txt")
    with open(sc_path, "w") as f:
        f.write("3d=true\n")
        f.write("polyline=false\n")
        for px, py in zip(x_coords, y_coords):
            f.write(f"{px:.8f} {py:.8f} 0.00000000\n")
            
    # 6. Save DesignModeler Format (Group# Pt# X Y Z)
    dm_path = os.path.join("data", "naca0012_dm.txt")
    with open(dm_path, "w") as f:
        for idx, (px, py) in enumerate(zip(x_coords, y_coords), start=1):
            f.write(f"1\t{idx}\t{px:.8f}\t{py:.8f}\t0.00000000\n")

    print(f"\n[SUCCESS] Generated clean coordinate files:")
    print(f" - SpaceClaim     : {sc_path}")
    print(f" - DesignModeler  : {dm_path}\n")


if __name__ == "__main__":
    generate_naca0012_points()
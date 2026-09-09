import os
import re
import pandas as pd


def extract_metadata_from_filename(file_path: str) -> dict:
    """Extracts mesh level, angle of attack (AoA), and variable type from file naming conventions."""
    filename = os.path.basename(file_path)

    mesh_match = re.search(r"mesh_(coarse|medium|fine)", filename)
    aoa_match = re.search(r"aoa(\d+)", filename)
    var_match = re.search(r"mesh_(?:coarse|medium|fine)_([a-z]+)_aoa", filename)

    return {
        "mesh_level": mesh_match.group(1) if mesh_match else "unknown",
        "aoa": int(aoa_match.group(1)) if aoa_match else 0,
        "variable": var_match.group(1) if var_match else "cp",
    }


def parse_fluent_xy(file_path: str) -> pd.DataFrame:
    """Strips Ansys Fluent header metadata, extracts numbers, and normalizes chord coordinates x/c."""
    clean_rows = []

    with open(file_path, "r") as file:
        for line in file:
            line_str = line.strip()

            if (
                not line_str
                or line_str.startswith("(")
                or line_str.startswith('"')
            ):
                continue

            if re.match(r"^[+-]?\d", line_str):
                values = re.split(r"[\s,]+", line_str)
                if len(values) >= 2:
                    clean_rows.append([float(values[0]), float(values[1])])

    df = pd.DataFrame(clean_rows, columns=["x_raw", "value"])
    df["x_c"] = -df["x_raw"]

    metadata = extract_metadata_from_filename(file_path)
    df["mesh_level"] = metadata["mesh_level"]
    df["aoa"] = metadata["aoa"]

    return df.sort_values(by="x_c").reset_index(drop=True)


def load_nasa_benchmark(file_path: str) -> pd.DataFrame:
    """Loads NASA Ladson experimental Cp benchmark data into a clean DataFrame, ignoring text headers."""
    clean_rows = []

    with open(file_path, "r") as file:
        for line in file:
            line_str = line.strip()
            if (
                not line_str
                or line_str.startswith("#")
                or line_str.startswith("%")
            ):
                continue

            tokens = re.split(r"[\s,]+", line_str)

            # Extract numeric rows with at least 3 values (x/c, cp_upper, cp_lower)
            if len(tokens) >= 3:
                try:
                    row = [float(tokens[0]), float(tokens[1]), float(tokens[2])]
                    clean_rows.append(row)
                except ValueError:
                    # Skip header text lines containing words
                    continue

    df = pd.DataFrame(clean_rows, columns=["x_c", "cp_upper", "cp_lower"])
    return df.sort_values(by="x_c").reset_index(drop=True)
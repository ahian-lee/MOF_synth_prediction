#!/usr/bin/env python
"""
Simple CIF overlap-fix utility used before batch thermal prediction.
"""

import argparse
import shutil
import warnings
from pathlib import Path

import numpy as np
from ase.io import read, write
from scipy.spatial.distance import pdist, squareform

warnings.filterwarnings("ignore")


def optimize_cif(input_cif, output_cif, min_dist=1.5):
    atoms = read(input_cif)
    pos = atoms.get_positions()
    numbers = atoms.get_atomic_numbers()
    dist_matrix = squareform(pdist(pos))

    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            current_dist = dist_matrix[i, j]
            allowed = 2.0 if numbers[i] > 20 or numbers[j] > 20 else min_dist
            if 0 < current_dist < allowed:
                direction = pos[j] - pos[i]
                norm = np.linalg.norm(direction)
                if norm > 0.01:
                    pos[j] = pos[i] + (direction / norm) * allowed

    atoms.set_positions(pos)
    write(output_cif, atoms)


def batch_optimize(input_folder, output_folder, min_dist=1.5):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    if output_folder.exists():
        shutil.rmtree(output_folder)
    output_folder.mkdir(parents=True)

    results = []
    for cif_file in sorted(input_folder.glob("*.cif")):
        output_file = output_folder / cif_file.name
        try:
            optimize_cif(cif_file, output_file, min_dist=min_dist)
            results.append({"name": cif_file.name, "status": "SUCCESS"})
        except Exception as exc:
            results.append({"name": cif_file.name, "status": "FAILED", "reason": str(exc)})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-folder", required=True)
    parser.add_argument("--output-folder", required=True)
    parser.add_argument("--min-dist", type=float, default=1.5)
    args = parser.parse_args()
    results = batch_optimize(args.input_folder, args.output_folder, min_dist=args.min_dist)
    success = sum(1 for row in results if row["status"] == "SUCCESS")
    print(f"Optimized {success}/{len(results)} CIFs")


if __name__ == "__main__":
    main()

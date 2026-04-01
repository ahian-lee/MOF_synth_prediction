# MOFSimplify Extension Usage

This directory contains only my extension layer for batch thermal-stability prediction. It is not a redistribution of the original MOFSimplify web project.

## Upstream Dependency

Prepare a separate upstream `MOFSimplify` directory with:

- `model/thermal/ANN/final_model_T_few_epochs.h5`
- `model/thermal/ANN/train.csv`
- `zeo++-0.3/network`
- a working `molSimplify` Python environment

## Batch Thermal Prediction

```bash
python mofsimplify_extensions/batch_thermal_prediction.py \
  --mofsimplify-root /path/to/MOFSimplify \
  --cif-folder ./cifs \
  --output-dir ./thermal_results
```

Output CSV columns:

- `name`
- `status`
- `thermal_stability_C`
- `matched_features`

## Optional Preprocessing

If some generated CIFs contain overlapping atoms, run:

```bash
python mofsimplify_extensions/optimize_structures.py \
  --input-folder ./raw_cifs \
  --output-folder ./optimized_cifs \
  --min-dist 1.5
```

Then use `./optimized_cifs` as the input for thermal prediction.

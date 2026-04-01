# MOF Batch Stability and Synthesizability Toolkit

This repository packages two parts of my MOF workflow:

1. `mofsynth/`: a standalone MOF synthesizability prediction package based on PU-learning CGCNN.
2. `mofsimplify_extensions/`: my batch thermal-stability workflow built on top of the upstream `MOFSimplify` environment and model files.

This repository does not redistribute the original `MOFSimplify` web frontend or other upstream project code that I did not write. The thermal-stability extension here is intended to run against a separately prepared `MOFSimplify` installation.

## Repository Layout

```text
mof-tools-github/
├── mofsynth/
│   ├── predict_PU_learning.py
│   ├── generate_crystal_graph.py
│   ├── atom_init.json
│   ├── trained_models/
│   └── cgcnn/
├── mofsimplify_extensions/
│   ├── batch_thermal_prediction.py
│   └── optimize_structures.py
├── scripts/
│   ├── merge_predictions.py
│   └── run_combined_pipeline.sh
└── docs/
    └── mofsimplify_extension_usage.md
```

## Module Summary

### `mofsynth`

Predicts MOF synthesizability from CIF files.

- Input: a directory containing `.cif` files, `id_prop.csv`, and `atom_init.json`
- Step 1: generate crystal graphs
- Step 2: run ensemble prediction with 100 pretrained checkpoints
- Output: `test_results_ensemble_100models.csv`

Main commands:

```bash
python mofsynth/generate_crystal_graph.py \
  --cifs ./my_cifs \
  --n 12 \
  --r 8 \
  --f ./crystal_graph

python mofsynth/predict_PU_learning.py \
  --bag 100 \
  --graph ./crystal_graph \
  --cifs ./my_cifs \
  --modeldir ./mofsynth/trained_models
```

### `mofsimplify_extensions`

Runs batch thermal-stability prediction for many MOF CIF files using an existing `MOFSimplify` installation.

- Depends on upstream `MOFSimplify`, `molSimplify`, Zeo++, TensorFlow, and the upstream thermal model files
- Does not include the upstream frontend or web application
- Converts CIFs to geometric and RAC descriptors, applies the corrected feature mapping, then predicts thermal stability in Celsius

Main command:

```bash
python mofsimplify_extensions/batch_thermal_prediction.py \
  --mofsimplify-root /path/to/MOFSimplify \
  --cif-folder ./my_cifs \
  --output-dir ./thermal_results
```

## Thermal Model Dependency

The thermal prediction extension expects these files to exist under your upstream `MOFSimplify` checkout:

```text
model/thermal/ANN/final_model_T_few_epochs.h5
model/thermal/ANN/train.csv
zeo++-0.3/network
```

## Combined Workflow

If you want both predictions for the same CIF set:

1. Run `mofsynth` to get `CLscore`
2. Run `mofsimplify_extensions/batch_thermal_prediction.py` to get thermal stability
3. Merge results with `scripts/merge_predictions.py`

Example:

```bash
python scripts/merge_predictions.py \
  --synth-csv ./test_results_ensemble_100models.csv \
  --thermal-csv ./thermal_results/thermal_predictions.csv \
  --output ./combined_predictions.csv
```

## Notes

- `mofsynth` in this repository includes the packaged pretrained checkpoints.
- `mofsimplify_extensions` assumes you already have legal access to the upstream `MOFSimplify` installation and model assets.
- Generated CSV files, logs, crystal graphs, and temporary folders are ignored by git.

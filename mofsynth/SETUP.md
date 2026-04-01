# Synthesizability-PU-CGCNN Setup and Usage Guide

## Project Overview

This is a PU-learning based CGCNN model for predicting **CLscore** (crystal-likeness score), which quantifies the synthesizability of inorganic crystals, particularly MOFs.

## Project Structure

```
/opt/data/private/moffusion/mofsynth/prediction/
├── cgcnn/                           # CGCNN module
│   ├── data_PU_learning.py          # Data loading utilities
│   └── model_PU_learning.py         # Model architecture
├── trained_models/                   # 100 pre-trained models (bag_1 to bag_100)
├── CLscore_prediction_results/       # Pre-computed CLscore results
│   ├── MP_icsd_CLscore.csv
│   ├── MP_virtual_CLscore.csv
│   └── OQMD_virtual_CLscore.csv
├── cif_files/                       # Input directory (user provides CIF files)
│   ├── atom_init.json              # Element feature initialization (provided)
│   └── id_prop.csv                 # ID-property mapping (user creates)
├── saved_crystal_graph/             # Generated crystal graphs (auto-generated)
├── generate_crystal_graph.py        # Step 1: Generate crystal graphs
├── predict_PU_learning.py           # Step 2: Predict CLscore
└── main_PU_learning.py              # Training script (optional)

```

## Quick Start

### Step 1: Prepare Your CIF Files

Place your `.cif` files in the `cif_files/` directory:

```bash
# Copy your CIF files
cp /path/to/your/*.cif /opt/data/private/moffusion/mofsynth/prediction/cif_files/
```

### Step 2: Create id_prop.csv

Create `cif_files/id_prop.csv` with the following format:

```csv
crystal_id,synthesizable
your_structure_1,0
your_structure_2,0
your_structure_3,0
```

**Important:**
- `crystal_id`: Must match the CIF filename (without `.cif` extension)
- `synthesizable`: Use `0` for all structures (unlabeled data for prediction)

Example: If you have `my_mof.cif`, the csv entry should be:
```
my_mof,0
```

### Step 3: Generate Crystal Graphs

```bash
cd /opt/data/private/moffusion/mofsynth/prediction

python generate_crystal_graph.py \
    --cifs ./cif_files \
    --n 12 \
    --r 8 \
    --f ./saved_crystal_graph
```

**Parameters:**
- `--cifs`: Directory containing CIF files and id_prop.csv
- `--n`: Maximum number of neighbors (default: 12)
- `--r`: Cutoff radius in Angstroms (default: 8)
- `--f`: Output folder for crystal graph pickle files

### Step 4: Predict CLscore

```bash
python predict_PU_learning.py \
    --bag 100 \
    --graph ./saved_crystal_graph \
    --cifs ./cif_files \
    --modeldir ./trained_models
```

**Parameters:**
- `--bag`: Number of models for ensemble (use 100 for all pre-trained models)
- `--graph`: Directory containing pre-generated crystal graphs
- `--cifs`: Directory containing CIF files and id_prop.csv
- `--modeldir`: Directory containing pre-trained models

### Step 5: View Results

Results will be saved in `test_results_ensemble_100models.csv`:

```csv
crystal_id,CLscore
your_structure_1,0.7543
your_structure_2,0.3212
your_structure_3,0.8901
```

**CLscore Interpretation:**
- **Higher CLscore** (closer to 1) = More synthesizable
- **Lower CLscore** (closer to 0) = Less synthesizable

## Dependencies

Install required packages:

```bash
pip install numpy torch pymatgen tqdm
```

## Example Workflow

```bash
# 1. Navigate to project directory
cd /opt/data/private/moffusion/mofsynth/prediction

# 2. Copy your CIF files
cp /path/to/mofs/*.cif ./cif_files/

# 3. Update id_prop.csv with your structure IDs
# Edit ./cif_files/id_prop.csv manually

# 4. Generate crystal graphs
python generate_crystal_graph.py --cifs ./cif_files --n 12 --r 8 --f ./saved_crystal_graph

# 5. Predict CLscore
python predict_PU_learning.py --bag 100 --graph ./saved_crystal_graph --cifs ./cif_files --modeldir ./trained_models

# 6. Check results
cat test_results_ensemble_100models.csv
```

## Pre-computed Results

The `CLscore_prediction_results/` directory contains pre-computed CLscores for:
- **MP_icsd_CLscore.csv**: ICSD structures from Materials Project
- **MP_virtual_CLscore.csv**: Virtual structures from Materials Project
- **OQMD_virtual_CLscore.csv**: Virtual structures from OQMD

You can use these as reference or lookup tables.

## Troubleshooting

**Error: "atom_init.json does not exist!"**
- Ensure `atom_init.json` is in `cif_files/` directory

**Error: "id_prop.csv does not exist!"**
- Create `id_prop.csv` in `cif_files/` directory

**Error: "not find enough neighbors to build graph"**
- Increase the cutoff radius `--r` (e.g., from 8 to 10)

**Error: CIF file parsing errors**
- Verify your CIF files are in valid format
- Check that crystal IDs match filenames

## Reference

Jidon Jang, Geun Ho Gu, Juhwan Noh, Juhwan Kim, and Yousung Jung,
"Structure-Based Synthesizability Prediction of Crystals Using Partially Supervised Learning",
*Journal of the American Chemical Society*, 2020, 142, 44, 18836–18843
DOI: 10.1021/jacs.0c07384

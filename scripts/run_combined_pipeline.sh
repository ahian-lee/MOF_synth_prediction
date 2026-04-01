#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <mofsimplify_root> <cif_dir> <graph_dir> <output_dir>"
  exit 1
fi

MOFSIMPLIFY_ROOT="$1"
CIF_DIR="$2"
GRAPH_DIR="$3"
OUTPUT_DIR="$4"

mkdir -p "${OUTPUT_DIR}"

python mofsynth/generate_crystal_graph.py \
  --cifs "${CIF_DIR}" \
  --n 12 \
  --r 8 \
  --f "${GRAPH_DIR}"

python mofsynth/predict_PU_learning.py \
  --bag 100 \
  --graph "${GRAPH_DIR}" \
  --cifs "${CIF_DIR}" \
  --modeldir mofsynth/trained_models

python mofsimplify_extensions/batch_thermal_prediction.py \
  --mofsimplify-root "${MOFSIMPLIFY_ROOT}" \
  --cif-folder "${CIF_DIR}" \
  --output-dir "${OUTPUT_DIR}"

python scripts/merge_predictions.py \
  --synth-csv test_results_ensemble_100models.csv \
  --thermal-csv "${OUTPUT_DIR}/thermal_predictions.csv" \
  --output "${OUTPUT_DIR}/combined_predictions.csv"

echo "Combined results written to ${OUTPUT_DIR}/combined_predictions.csv"

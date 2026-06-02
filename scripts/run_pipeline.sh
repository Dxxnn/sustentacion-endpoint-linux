#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
IFOREST_CONTAMINATION="${IFOREST_CONTAMINATION:-0.05}"
cd "${ROOT_DIR}"

mkdir -p data/processed results

"${PYTHON}" scripts/parse_audit_log.py \
  --input data/raw/audit.log \
  --output data/processed/audit_events.csv

"${PYTHON}" scripts/build_features.py \
  --events data/processed/audit_events.csv \
  --labels data/raw/scenario_labels.csv \
  --output data/processed/features.csv

"${PYTHON}" scripts/rule_detector.py \
  --features data/processed/features.csv \
  --detections results/rule_detections.csv \
  --metrics results/rule_metrics.csv

"${PYTHON}" scripts/isolation_forest_baseline.py \
  --features data/processed/features.csv \
  --scores results/isolation_forest_scores.csv \
  --metrics results/isolation_forest_metrics.csv \
  --contamination "${IFOREST_CONTAMINATION}" \
  --model-output results/models/isolation_forest_pipeline.joblib

echo "[pipeline] Listo. Revisa data/processed y results."

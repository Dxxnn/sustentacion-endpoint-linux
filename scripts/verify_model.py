#!/usr/bin/env python3
"""Verifica que el artefacto entrenado pueda cargarse y usar el dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd


FEATURE_COLUMNS = [
    "interval_seconds",
    "chain_depth",
    "has_curl_wget",
    "chmod_event",
    "exec_from_tmp",
    "download_then_execute_window",
    "parent_process",
    "child_process",
    "user",
    "path",
]
NUMERIC_COLUMNS = FEATURE_COLUMNS[:6]
CATEGORICAL_COLUMNS = FEATURE_COLUMNS[6:]


def load_features(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path).fillna("")
    missing = sorted(set(FEATURE_COLUMNS + ["label", "scenario"]) - set(data.columns))
    if missing:
        raise SystemExit(f"Faltan columnas requeridas: {', '.join(missing)}")
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    for column in CATEGORICAL_COLUMNS:
        data[column] = data[column].astype(str).fillna("")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("results/models/isolation_forest_pipeline.joblib"),
    )
    parser.add_argument(
        "--features",
        type=Path,
        default=Path("data/processed/features.csv"),
    )
    args = parser.parse_args()

    model = joblib.load(args.model)
    data = load_features(args.features)
    predictions = model.predict(data[FEATURE_COLUMNS].head(25))

    print("Modelo cargado correctamente")
    print(f"Eventos procesados: {len(data)}")
    print(f"Predicciones de prueba: {len(predictions)}")
    print("\nEtiquetas:")
    print(data["label"].value_counts().to_string())
    print("\nEscenarios:")
    print(data["scenario"].value_counts().to_string())


if __name__ == "__main__":
    main()


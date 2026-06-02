#!/usr/bin/env python3
"""Modelo inicial de anomalías con Isolation Forest."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def metric_rows(y_true: list[int], y_pred: list[int]) -> list[dict[str, float | str]]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return [
        {"metric": "true_positives", "value": tp},
        {"metric": "false_positives", "value": fp},
        {"metric": "true_negatives", "value": tn},
        {"metric": "false_negatives", "value": fn},
        {"metric": "precision", "value": precision},
        {"metric": "recall_detection_rate", "value": recall},
        {"metric": "false_positive_rate", "value": fpr},
        {"metric": "f1_score", "value": f1},
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", required=True, type=Path)
    parser.add_argument("--scores", required=True, type=Path)
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--contamination", type=float, default=0.10)
    parser.add_argument("--model-output", type=Path)
    args = parser.parse_args()

    features = pd.read_csv(args.features).fillna("")
    if features.empty:
        raise SystemExit("No hay filas de variables para entrenar/evaluar.")

    numeric_features = [
        "interval_seconds",
        "chain_depth",
        "has_curl_wget",
        "chmod_event",
        "exec_from_tmp",
        "download_then_execute_window",
    ]
    categorical_features = ["parent_process", "child_process", "user", "path"]

    for col in numeric_features:
        features[col] = pd.to_numeric(features[col], errors="coerce").fillna(0)
    for col in categorical_features:
        features[col] = features[col].astype(str).fillna("")

    train = features[features["label"].eq("normal")].copy()
    if len(train) < 10:
        train = features.copy()
        training_note = "entrenado con todos los eventos por falta de linea base normal suficiente"
    else:
        training_note = "entrenado con eventos etiquetados como normales"

    preprocess = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=2), categorical_features),
        ]
    )
    model = IsolationForest(
        n_estimators=200,
        contamination=args.contamination,
        random_state=42,
    )
    pipeline = Pipeline(steps=[("preprocess", preprocess), ("model", model)])
    pipeline.fit(train[numeric_features + categorical_features])
    if args.model_output:
        args.model_output.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, args.model_output)

    predictions = pipeline.predict(features[numeric_features + categorical_features])
    scores = pipeline.decision_function(features[numeric_features + categorical_features])

    output = features.copy()
    output["iforest_prediction"] = predictions
    output["iforest_alert"] = (predictions == -1).astype(int)
    output["iforest_anomaly_score"] = -scores
    output["training_note"] = training_note

    args.scores.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.scores, index=False)

    labeled = output[output["label"].isin(["normal", "suspicious"])].copy()
    if labeled.empty:
        metrics = pd.DataFrame(
            [{"metric": "status", "value": "sin etiquetas suficientes; pendiente de validacion"}]
        )
    else:
        y_true = (labeled["label"] == "suspicious").astype(int).tolist()
        y_pred = labeled["iforest_alert"].astype(int).tolist()
        metrics = pd.DataFrame(metric_rows(y_true, y_pred))
        metrics.loc[len(metrics)] = {"metric": "training_note", "value": training_note}

    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.metrics, index=False)

    print(f"[iforest] Scores -> {args.scores}")
    print(f"[iforest] Metricas -> {args.metrics}")
    if args.model_output:
        print(f"[iforest] Modelo -> {args.model_output}")
    print(f"[iforest] Nota: {training_note}")


if __name__ == "__main__":
    main()

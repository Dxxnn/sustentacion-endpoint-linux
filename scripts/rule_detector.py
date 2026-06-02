#!/usr/bin/env python3
"""Detector inicial de reglas tipo SIEM sobre variables de auditd."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SHELLS = {"sh", "bash", "dash", "zsh"}
SUSPICIOUS_PARENTS = {"python", "python3", "awk", "find", "perl"}


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


def detect(features: pd.DataFrame) -> pd.DataFrame:
    data = features.copy()
    parent = data["parent_process"].fillna("").str.lower().str.split("/").str[-1]
    child = data["child_process"].fillna("").str.lower().str.split("/").str[-1]
    command = data["command"].fillna("").str.lower()
    path = data["path"].fillna("").str.lower()

    data["rule_unusual_parent_child"] = (
        parent.isin(SUSPICIOUS_PARENTS) & child.isin(SHELLS)
    ).astype(int)
    data["rule_download_tool"] = data["has_curl_wget"].fillna(0).astype(int)
    data["rule_permission_then_exec"] = (
        data["chmod_event"].fillna(0).astype(int).eq(1)
        | data["download_then_execute_window"].fillna(0).astype(int).eq(1)
    ).astype(int)
    data["rule_exec_from_lab_tmp"] = (
        data["exec_from_tmp"].fillna(0).astype(int).eq(1)
        & (command.str.contains("hello.sh") | path.str.contains("hello.sh"))
    ).astype(int)

    rule_cols = [
        "rule_unusual_parent_child",
        "rule_download_tool",
        "rule_permission_then_exec",
        "rule_exec_from_lab_tmp",
    ]
    data["rule_alert"] = data[rule_cols].max(axis=1)
    data["rule_reason"] = data[rule_cols].apply(
        lambda row: ";".join(col for col, value in row.items() if int(value) == 1),
        axis=1,
    )
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", required=True, type=Path)
    parser.add_argument("--detections", required=True, type=Path)
    parser.add_argument("--metrics", required=True, type=Path)
    args = parser.parse_args()

    features = pd.read_csv(args.features)
    detections = detect(features)

    args.detections.parent.mkdir(parents=True, exist_ok=True)
    detections.to_csv(args.detections, index=False)

    labeled = detections[detections["label"].isin(["normal", "suspicious"])].copy()
    if labeled.empty:
        metrics = pd.DataFrame(
            [{"metric": "status", "value": "sin etiquetas suficientes; pendiente de validacion"}]
        )
    else:
        y_true = (labeled["label"] == "suspicious").astype(int).tolist()
        y_pred = labeled["rule_alert"].astype(int).tolist()
        metrics = pd.DataFrame(metric_rows(y_true, y_pred))

    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.metrics, index=False)
    print(f"[rules] Detecciones -> {args.detections}")
    print(f"[rules] Metricas -> {args.metrics}")


if __name__ == "__main__":
    main()

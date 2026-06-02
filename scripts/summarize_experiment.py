#!/usr/bin/env python3
"""Genera tablas breves y un resumen Markdown de la corrida del laboratorio."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def read_metrics(path: Path) -> pd.Series:
    return pd.read_csv(path).set_index("metric")["value"]


def metric_value(metrics: pd.Series, name: str) -> float:
    return float(metrics[name])


def build_window_coverage(
    labels: pd.DataFrame,
    rules: pd.DataFrame,
    iforest: pd.DataFrame,
) -> pd.DataFrame:
    labels = labels.copy()
    labels["start"] = pd.to_datetime(labels["start_time_utc"], utc=True)
    labels["end"] = pd.to_datetime(labels["end_time_utc"], utc=True)
    rules = rules.copy()
    iforest = iforest.copy()
    rules["timestamp"] = pd.to_datetime(rules["timestamp_iso"], utc=True)
    iforest["timestamp"] = pd.to_datetime(iforest["timestamp_iso"], utc=True)

    rows: list[dict[str, object]] = []
    for _, row in labels.iterrows():
        rule_window = rules[(rules["timestamp"] >= row["start"]) & (rules["timestamp"] <= row["end"])]
        iforest_window = iforest[
            (iforest["timestamp"] >= row["start"]) & (iforest["timestamp"] <= row["end"])
        ]
        rows.append(
            {
                "run_id": row["run_id"],
                "scenario": row["scenario"],
                "expected_label": row["expected_label"],
                "start_time_utc": row["start_time_utc"],
                "end_time_utc": row["end_time_utc"],
                "event_count": len(rule_window),
                "rule_alert_count": int(rule_window["rule_alert"].astype(int).sum()),
                "rule_detected": int(rule_window["rule_alert"].astype(int).sum() > 0),
                "iforest_alert_count": int(iforest_window["iforest_alert"].astype(int).sum()),
                "iforest_detected": int(iforest_window["iforest_alert"].astype(int).sum() > 0),
            }
        )
    return pd.DataFrame(rows)


def build_sensitivity(sensitivity_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for path in sorted(sensitivity_dir.glob("isolation_forest_metrics_*.csv")):
        contamination = float(path.stem.rsplit("_", 1)[-1])
        metrics = read_metrics(path)
        rows.append(
            {
                "contamination": contamination,
                "precision": metric_value(metrics, "precision"),
                "recall_detection_rate": metric_value(metrics, "recall_detection_rate"),
                "false_positive_rate": metric_value(metrics, "false_positive_rate"),
                "f1_score": metric_value(metrics, "f1_score"),
                "true_positives": int(metric_value(metrics, "true_positives")),
                "false_positives": int(metric_value(metrics, "false_positives")),
                "true_negatives": int(metric_value(metrics, "true_negatives")),
                "false_negatives": int(metric_value(metrics, "false_negatives")),
            }
        )
    return pd.DataFrame(rows).sort_values("contamination").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=Path("data/processed/features.csv"))
    parser.add_argument("--labels", type=Path, default=Path("data/raw/scenario_labels.csv"))
    parser.add_argument("--rule-detections", type=Path, default=Path("results/rule_detections.csv"))
    parser.add_argument("--iforest-scores", type=Path, default=Path("results/isolation_forest_scores.csv"))
    parser.add_argument("--rule-metrics", type=Path, default=Path("results/rule_metrics.csv"))
    parser.add_argument("--iforest-metrics", type=Path, default=Path("results/isolation_forest_metrics.csv"))
    parser.add_argument("--sensitivity-dir", type=Path, default=Path("results/sensitivity"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--iforest-contamination", type=float, default=0.05)
    args = parser.parse_args()

    features = pd.read_csv(args.features).fillna("")
    labels = pd.read_csv(args.labels).fillna("")
    rules = pd.read_csv(args.rule_detections).fillna("")
    iforest = pd.read_csv(args.iforest_scores).fillna("")
    rule_metrics = read_metrics(args.rule_metrics)
    iforest_metrics = read_metrics(args.iforest_metrics)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    dataset_summary = pd.concat(
        [
            features["label"].value_counts().rename_axis("name").reset_index(name="count").assign(dimension="label"),
            features["scenario"].value_counts().rename_axis("name").reset_index(name="count").assign(dimension="scenario"),
        ],
        ignore_index=True,
    )[["dimension", "name", "count"]]
    coverage = build_window_coverage(labels, rules, iforest)
    sensitivity = build_sensitivity(args.sensitivity_dir)

    dataset_summary.to_csv(args.output_dir / "dataset_summary.csv", index=False)
    coverage.to_csv(args.output_dir / "scenario_window_coverage.csv", index=False)
    sensitivity.to_csv(args.output_dir / "isolation_forest_sensitivity.csv", index=False)

    suspicious = coverage[coverage["expected_label"] == "suspicious"]
    normal = coverage[coverage["expected_label"] == "normal"]
    retained_normal = normal[normal["event_count"] > 0]
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = f"""# Resumen de corrida del laboratorio

Generado en UTC: {generated_at}

## Conjunto de datos

- Eventos auditd procesados: {len(features)}
- Eventos normales etiquetados: {(features["label"] == "normal").sum()}
- Eventos sospechosos etiquetados: {(features["label"] == "suspicious").sum()}
- Eventos sin etiqueta: {(features["label"] == "unknown").sum()}

## Detector de reglas

- Precision por evento: {metric_value(rule_metrics, "precision"):.4f}
- Recall por evento: {metric_value(rule_metrics, "recall_detection_rate"):.4f}
- FPR por evento: {metric_value(rule_metrics, "false_positive_rate"):.4f}
- F1 por evento: {metric_value(rule_metrics, "f1_score"):.4f}
- Ventanas sospechosas detectadas: {int(suspicious["rule_detected"].sum())}/{len(suspicious)}
- Ventanas normales retenidas con eventos: {len(retained_normal)}/{len(normal)}
- Ventanas normales con alerta: {int(retained_normal["rule_detected"].sum())}/{len(retained_normal)}

## Isolation Forest

- Contaminacion configurada: {args.iforest_contamination:.4f}
- Precision por evento: {metric_value(iforest_metrics, "precision"):.4f}
- Recall por evento: {metric_value(iforest_metrics, "recall_detection_rate"):.4f}
- FPR por evento: {metric_value(iforest_metrics, "false_positive_rate"):.4f}
- F1 por evento: {metric_value(iforest_metrics, "f1_score"):.4f}
- Ventanas sospechosas detectadas: {int(suspicious["iforest_detected"].sum())}/{len(suspicious)}
- Ventanas normales retenidas con eventos: {len(retained_normal)}/{len(normal)}
- Ventanas normales con alerta: {int(retained_normal["iforest_detected"].sum())}/{len(retained_normal)}

## Nota metodologica

Isolation Forest se entreno con los eventos etiquetados como normales. Las metricas son una validacion
controlada del prototipo y no equivalen todavia a una evaluacion en produccion.
"""
    (args.output_dir / "experiment_summary.md").write_text(summary, encoding="utf-8")
    print(f"[summary] Archivos exportados en {args.output_dir}")


if __name__ == "__main__":
    main()

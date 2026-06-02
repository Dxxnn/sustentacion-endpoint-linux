#!/usr/bin/env python3
"""Construye variables de comportamiento a partir de eventos auditd parseados."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


LAB_DIR = "/tmp/project_audit_lab"


def basename(value: str) -> str:
    value = str(value or "")
    if not value:
        return ""
    return value.rstrip("/").split("/")[-1]


def to_int(value: object, default: int = -1) -> int:
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def approximate_depth(pid: int, pid_to_ppid: dict[int, int], max_depth: int = 12) -> int:
    depth = 0
    seen: set[int] = set()
    current = pid
    while current in pid_to_ppid and current not in seen and depth < max_depth:
        seen.add(current)
        parent = pid_to_ppid.get(current, 0)
        if parent <= 1 or parent == current:
            break
        depth += 1
        current = parent
    return depth


def assign_labels(events: pd.DataFrame, labels_path: Path, window_padding_seconds: int = 0) -> pd.DataFrame:
    events["scenario"] = "unlabeled"
    events["label"] = "unknown"
    if not labels_path.exists():
        return events

    labels = pd.read_csv(labels_path)
    if labels.empty:
        return events

    labels["start"] = pd.to_datetime(labels["start_time_utc"], utc=True, errors="coerce")
    labels["end"] = pd.to_datetime(labels["end_time_utc"], utc=True, errors="coerce")

    padding = pd.Timedelta(seconds=window_padding_seconds)
    for _, row in labels.dropna(subset=["start", "end"]).iterrows():
        start = row["start"] - padding
        end = row["end"] + padding
        mask = (events["timestamp"] >= start) & (events["timestamp"] <= end)
        events.loc[mask, "scenario"] = row.get("scenario", "unlabeled")
        events.loc[mask, "label"] = row.get("expected_label", "unknown")

    return events


def build_features(events_path: Path, labels_path: Path) -> pd.DataFrame:
    events = pd.read_csv(events_path, dtype=str).fillna("")
    if events.empty:
        return pd.DataFrame()

    events["timestamp"] = pd.to_datetime(events["timestamp_iso"], utc=True, errors="coerce")
    events = events.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    events["pid_int"] = events["pid"].apply(to_int)
    events["ppid_int"] = events["ppid"].apply(to_int)
    pid_to_comm = dict(zip(events["pid_int"], events["comm"].fillna("").astype(str)))
    pid_to_ppid = dict(zip(events["pid_int"], events["ppid_int"]))

    events["parent_process"] = events["ppid_int"].map(pid_to_comm).fillna("")
    events["child_process"] = events.apply(
        lambda row: basename(row["exe"]) or str(row["comm"] or ""),
        axis=1,
    )
    events["user"] = events["auid"].where(events["auid"].astype(str) != "", events["uid"])
    events["path"] = events["first_path"].where(events["first_path"].astype(str) != "", events["exe"])
    events["interval_seconds"] = events["timestamp"].diff().dt.total_seconds().fillna(0).clip(lower=0)
    events["chain_depth"] = events["pid_int"].apply(lambda pid: approximate_depth(pid, pid_to_ppid))

    text = (
        events["command"].astype(str)
        + " "
        + events["exe"].astype(str)
        + " "
        + events["comm"].astype(str)
        + " "
        + events["path"].astype(str)
    ).str.lower()

    events["has_curl_wget"] = text.str.contains(r"(?:^|\W)(?:curl|wget)(?:\W|$)", regex=True).astype(int)
    events["chmod_event"] = text.str.contains(r"(?:^|\W)chmod(?:\W|$)", regex=True).astype(int)
    events["exec_from_tmp"] = text.str.contains(LAB_DIR.lower(), regex=False).astype(int)

    last_download_time = None
    flags: list[int] = []
    for _, row in events.iterrows():
        if row["has_curl_wget"] == 1:
            last_download_time = row["timestamp"]
            flags.append(0)
            continue
        if last_download_time is not None:
            delta = (row["timestamp"] - last_download_time).total_seconds()
            flags.append(1 if 0 <= delta <= 120 and row["exec_from_tmp"] == 1 else 0)
        else:
            flags.append(0)
    events["download_then_execute_window"] = flags

    events = assign_labels(events, labels_path)

    columns = [
        "serial",
        "timestamp_iso",
        "pid",
        "ppid",
        "parent_process",
        "child_process",
        "user",
        "command",
        "path",
        "interval_seconds",
        "chain_depth",
        "has_curl_wget",
        "chmod_event",
        "exec_from_tmp",
        "download_then_execute_window",
        "scenario",
        "label",
    ]
    return events[columns]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True, type=Path)
    parser.add_argument("--labels", default=Path("data/raw/scenario_labels.csv"), type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.events.exists():
        raise SystemExit(f"No existe el archivo de eventos: {args.events}")

    features = build_features(args.events, args.labels)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(args.output, index=False)
    print(f"[features] Filas exportadas: {len(features)} -> {args.output}")


if __name__ == "__main__":
    main()

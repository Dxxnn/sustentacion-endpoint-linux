#!/usr/bin/env python3
"""Parsea /var/log/audit/audit.log en un CSV analitico.

El parser agrupa registros auditd por serial y reconstruye campos de SYSCALL,
EXECVE, CWD y PATH. No es un reemplazo de auditd; es una base reproducible para
el prototipo de investigacion.
"""

from __future__ import annotations

import argparse
import csv
import re
import shlex
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


MSG_RE = re.compile(r"msg=audit\((?P<ts>\d+(?:\.\d+)?):(?P<serial>\d+)\)")
TYPE_RE = re.compile(r"^type=(?P<type>\w+)")


ARG_RE = re.compile(r"^a\d+$")


def maybe_decode(event_type: str, key: str, value: str) -> str:
    value = value.strip()
    encoded_text = (
        (event_type == "EXECVE" and ARG_RE.fullmatch(key))
        or (event_type == "CWD" and key == "cwd")
        or (event_type == "PATH" and key == "name")
        or (event_type == "SYSCALL" and key in {"comm", "exe", "key"})
    )
    if encoded_text and len(value) >= 4 and len(value) % 2 == 0 and re.fullmatch(r"[0-9A-Fa-f]+", value):
        try:
            decoded = bytes.fromhex(value).decode("utf-8")
            if decoded and all(ch.isprintable() or ch.isspace() for ch in decoded):
                return decoded
        except (UnicodeDecodeError, ValueError):
            return value
    return value


def parse_kv(line: str, event_type: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    try:
        tokens = shlex.split(line, posix=True)
    except ValueError:
        tokens = line.split()
    for token in tokens:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        fields[key] = maybe_decode(event_type, key, value.strip('"'))
    return fields


def event_timestamp(ts: str) -> str:
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()


def parse_audit_log(input_path: Path) -> list[dict[str, str]]:
    grouped: dict[str, list[tuple[str, dict[str, str], str]]] = defaultdict(list)

    with input_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            msg = MSG_RE.search(line)
            typ = TYPE_RE.search(line)
            if not msg or not typ:
                continue
            serial = msg.group("serial")
            event_type = typ.group("type")
            fields = parse_kv(line, event_type)
            fields["_timestamp_epoch"] = msg.group("ts")
            fields["_serial"] = serial
            grouped[serial].append((event_type, fields, line))

    rows: list[dict[str, str]] = []
    for serial, records in sorted(grouped.items(), key=lambda item: int(item[0])):
        syscall = next((fields for typ, fields, _ in records if typ == "SYSCALL"), {})
        execve = [fields for typ, fields, _ in records if typ == "EXECVE"]
        cwd = next((fields for typ, fields, _ in records if typ == "CWD"), {})
        paths = [fields for typ, fields, _ in records if typ == "PATH"]

        if not syscall:
            continue

        argc = 0
        args: list[str] = []
        for fields in execve:
            try:
                argc = max(argc, int(fields.get("argc", "0")))
            except ValueError:
                argc = argc
            for index in range(0, 64):
                key = f"a{index}"
                if key in fields:
                    args.append(fields[key])

        path_values = [p.get("name", "") for p in paths if p.get("name")]
        timestamp_epoch = syscall.get("_timestamp_epoch", "0")
        row = {
            "serial": serial,
            "timestamp_epoch": timestamp_epoch,
            "timestamp_iso": event_timestamp(timestamp_epoch),
            "audit_key": syscall.get("key", ""),
            "syscall": syscall.get("syscall", ""),
            "success": syscall.get("success", ""),
            "exit": syscall.get("exit", ""),
            "pid": syscall.get("pid", ""),
            "ppid": syscall.get("ppid", ""),
            "uid": syscall.get("uid", ""),
            "auid": syscall.get("auid", ""),
            "gid": syscall.get("gid", ""),
            "comm": syscall.get("comm", ""),
            "exe": syscall.get("exe", ""),
            "cwd": cwd.get("cwd", ""),
            "argc": str(argc),
            "command": " ".join(args),
            "first_path": path_values[0] if path_values else "",
            "paths": "|".join(path_values),
            "raw_types": "|".join(typ for typ, _, _ in records),
        }
        rows.append(row)

    return rows


def write_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "serial",
        "timestamp_epoch",
        "timestamp_iso",
        "audit_key",
        "syscall",
        "success",
        "exit",
        "pid",
        "ppid",
        "uid",
        "auid",
        "gid",
        "comm",
        "exe",
        "cwd",
        "argc",
        "command",
        "first_path",
        "paths",
        "raw_types",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"No existe el archivo de entrada: {args.input}")

    rows = parse_audit_log(args.input)
    write_csv(rows, args.output)
    print(f"[parse] Eventos exportados: {len(rows)} -> {args.output}")


if __name__ == "__main__":
    main()

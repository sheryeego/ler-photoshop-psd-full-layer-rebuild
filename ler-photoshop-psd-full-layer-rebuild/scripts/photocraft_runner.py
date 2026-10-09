"""Portable PhotoCraft CLI adapter. No shell, installation, or persistent service."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def resolve_cli(supplied=None):
    candidate = supplied or os.environ.get("PHOTOCRAFT_CLI") or shutil.which("photocraft-cli")
    if not candidate:
        raise ValueError("Provide --cli, PHOTOCRAFT_CLI, or photocraft-cli on PATH.")
    resolved = Path(candidate).expanduser().resolve(strict=True)
    if not resolved.is_file():
        raise ValueError("PhotoCraft CLI must be a file.")
    return resolved


def call(cli, args, timeout=180):
    result = subprocess.run([str(cli), *map(str, args)], shell=False, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"PhotoCraft exit {result.returncode}: " + (result.stderr + result.stdout)[-6000:])
    return result.stdout


def info(cli, source):
    return json.loads(call(cli, ["info", Path(source).resolve(strict=True), "--compact"]))


def sha256(path):
    with Path(path).open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256") if hasattr(hashlib, "file_digest") else None
        if digest is None:
            digest = hashlib.sha256()
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def normalize_steps(steps):
    if not isinstance(steps, list):
        raise ValueError("Each batch must be a list of commands.")
    normalized = []
    for step in steps:
        if isinstance(step, str):
            command, params = step, {}
        elif isinstance(step, dict):
            command, params = step.get("command"), step.get("params", {})
        elif isinstance(step, list) and len(step) == 2:
            command, params = step
        else:
            raise ValueError("Use command strings, [command, params], or command/params objects.")
        if not isinstance(command, str) or not command.strip() or not isinstance(params, dict):
            raise ValueError("Commands require a nonempty string ID and object parameters.")
        normalized.append((command, params))
    return normalized


def load_batches(path):
    content = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(content, dict) and "batches" in content:
        batches = content["batches"]
        if not isinstance(batches, list) or not batches:
            raise ValueError("batches must be a nonempty list.")
    else:
        steps = content.get("steps", content.get("actions")) if isinstance(content, dict) else content
        batches = [steps]
    return [normalize_steps(batch) for batch in batches]


def command_args(source, steps, target):
    args = ["run", "--new", compact(source)] if isinstance(source, dict) else ["run", str(source)]
    for command, params in steps:
        args.extend(["--cmd", command, "--params", compact(params)])
    return [*args, "--out", str(target)]


def run_document(cli, source, batches, output, work_dir=None, timeout=180):
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Output exists; choose a new version: {output}")
    if not output.suffix:
        raise ValueError("Output requires a format extension such as .psd or .pcraft.")
    if not batches:
        raise ValueError("At least one batch is required.")
    if isinstance(source, dict):
        if not source:
            raise ValueError("New document specification is empty.")
    else:
        source = Path(source).expanduser().resolve(strict=True)
    work_root = Path(work_dir).resolve() if work_dir else output.parent / ".photocraft-work"
    # Preflight every batch before any action. Explicit batch boundaries preserve
    # selection/mask transactions rather than splitting them by a guessed size.
    probe_input = source if isinstance(source, dict) else work_root / ("x" * 40) / "checkpoint.pcraft"
    for batch in batches:
        argv = [str(cli), *command_args(probe_input, batch, work_root / ("x" * 40) / "checkpoint.pcraft")]
        units = len(subprocess.list2cmdline(argv).encode("utf-16-le")) // 2
        if units > 28000:
            raise ValueError("Batch exceeds safe Windows command-line size; split at complete operation boundaries.")
    output.parent.mkdir(parents=True, exist_ok=True)
    work_root.mkdir(parents=True, exist_ok=True)
    checkpoint_root = Path(tempfile.mkdtemp(prefix="run-", dir=work_root))
    all_results = []
    for index, batch in enumerate(batches):
        target = checkpoint_root / (f"checkpoint-{index + 1:03d}.pcraft")
        stdout = call(cli, command_args(source, batch, target), timeout=timeout)
        for line in stdout.splitlines():
            if line.lstrip().startswith("{"):
                result = json.loads(line)
                if "error" in result:
                    raise RuntimeError(f"Command failed: {compact(result)}")
                all_results.append(result)
        if not target.is_file():
            raise RuntimeError("PhotoCraft returned success without a checkpoint file.")
        source = target
    staged = checkpoint_root / ("final" + output.suffix)
    call(cli, ["convert", source, staged], timeout=timeout)
    # Exclusive creation prevents accidental replacement of an existing output.
    with staged.open("rb") as origin, output.open("xb") as destination:
        shutil.copyfileobj(origin, destination)
    return {"output": str(output), "sha256": sha256(output), "bytes": output.stat().st_size,
            "batchCount": len(batches), "commandCount": sum(map(len, batches)),
            "checkpointDirectory": str(checkpoint_root), "results": all_results}


def convert(cli, source, output):
    return run_document(cli, source, [[]], output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli")
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("probe")
    commands = sub.add_parser("commands")
    commands.add_argument("--filter", required=True)
    inspect = sub.add_parser("info")
    inspect.add_argument("source")
    inspect.add_argument("--full", action="store_true")
    export = sub.add_parser("convert")
    export.add_argument("source")
    export.add_argument("output")
    execute = sub.add_parser("run")
    source_group = execute.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--input")
    source_group.add_argument("--new")
    execute.add_argument("--actions", required=True)
    execute.add_argument("--out", required=True)
    execute.add_argument("--work-dir")
    execute.add_argument("--report")
    execute.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args()
    try:
        cli = resolve_cli(args.cli)
        if args.operation == "probe":
            result = {"cli": str(cli), "version": call(cli, ["--version"], timeout=20).strip(),
                      "transport": "local CLI", "applicationLaunched": False}
        elif args.operation == "commands":
            result = json.loads(call(cli, ["commands", "--json", "--filter", args.filter]))
        elif args.operation == "info":
            result = info(cli, args.source)
            if not args.full:
                result = {key: value for key, value in result.items() if key != "layers"}
        else:
            if args.operation == "convert":
                result = convert(cli, args.source, args.output)
            else:
                if args.report and Path(args.report).exists():
                    raise FileExistsError("Report exists; choose a new report path.")
                source = json.loads(args.new) if args.new else args.input
                if args.new and not isinstance(source, dict):
                    raise ValueError("--new requires a JSON object.")
                result = run_document(cli, source, load_batches(args.actions), args.out,
                                      args.work_dir, args.timeout)
                if args.report:
                    with Path(args.report).open("x", encoding="utf-8") as stream:
                        json.dump(result, stream, ensure_ascii=False, indent=2)
            result = {key: value for key, value in result.items() if key != "results"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

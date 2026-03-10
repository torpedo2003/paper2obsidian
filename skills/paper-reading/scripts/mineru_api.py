#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mineru_skill.cli import main


def build_args() -> list[str]:
    parser = argparse.ArgumentParser(description="Compatibility wrapper for the unified MinerU CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Remote PDF URL")
    group.add_argument("--file", help="Single local file")
    group.add_argument("--dir", help="Input directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--token", help="MinerU API token")
    parser.add_argument("--concurrency", type=int, default=5, help="Mapped to worker count")
    parser.add_argument("--poll-interval", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    forwarded = [
        "--output",
        args.output,
        "--workers",
        str(args.concurrency),
        "--poll-interval",
        str(args.poll_interval),
        "--timeout",
        str(args.timeout),
    ]
    for name in ("url", "file", "dir"):
        value = getattr(args, name)
        if value:
            forwarded.extend([f"--{name}", value])
    if args.token:
        forwarded.extend(["--token", args.token])
    if args.resume:
        forwarded.append("--resume")
    return forwarded


if __name__ == "__main__":
    raise SystemExit(main(build_args()))

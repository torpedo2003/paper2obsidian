from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional

from .core import (
    ParseOptions,
    gather_inputs,
    get_token,
    run_parse,
    run_parse_urls,
    summarize_results,
)

MODEL_CHOICES = ["pipeline", "vlm", "MinerU-HTML"]
LANGUAGE_CHOICES = ["auto", "en", "ch"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MinerU document parser")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", help="Input directory")
    group.add_argument("--file", help="Single file path")
    group.add_argument("--url", help="Reserved for future URL support")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--token", help="MinerU API token")
    parser.add_argument("--workers", "-w", type=int, default=5, help="Concurrent workers")
    parser.add_argument(
        "--mode",
        choices=["threaded", "stable"],
        default="threaded",
        help="Execution mode",
    )
    parser.add_argument("--resume", action="store_true", help="Skip files that already exist")
    parser.add_argument("--recursive", action="store_true", help="Walk subdirectories")
    parser.add_argument("--model", default="pipeline", choices=MODEL_CHOICES, help="Model version")
    parser.add_argument(
        "--language",
        default="auto",
        choices=LANGUAGE_CHOICES,
        help="Document language",
    )
    parser.add_argument("--poll-interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--timeout", type=int, default=600, help="Per-file timeout in seconds")
    parser.add_argument("--retries", type=int, default=5, help="Retries per file")
    parser.add_argument("--no-formula", action="store_true", help="Disable formula recognition")
    parser.add_argument("--no-table", action="store_true", help="Disable table extraction")
    return parser


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.mode == "stable":
        args.workers = 1
    return args


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    try:
        token = get_token(args.token)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    options = ParseOptions(
        model=args.model,
        language=args.language,
        enable_formula=not args.no_formula,
        enable_table=not args.no_table,
        poll_interval=args.poll_interval,
        timeout=args.timeout,
        retries=args.retries,
        resume=args.resume,
        workers=max(1, args.workers),
    )
    output_dir = Path(args.output)
    if args.url:
        results = run_parse_urls(token=token, urls=[args.url], output_dir=output_dir, options=options)
    else:
        input_files = gather_inputs(args.file, args.dir, recursive=args.recursive)
        results = run_parse(token=token, input_files=input_files, output_dir=output_dir, options=options)
    return summarize_results(results, output_dir)


if __name__ == "__main__":
    sys.exit(main())

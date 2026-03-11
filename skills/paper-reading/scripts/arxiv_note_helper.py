#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


ARXIV_RE = re.compile(r'(\d{4}\.\d{4,5})(v\d+)?')
DATE_PATTERNS = [
    re.compile(r'(?<!\d)(20\d{2}|19\d{2})[-_/.]?(0[1-9]|1[0-2])[-_/.]?(0[1-9]|[12]\d|3[01])(?!\d)'),
    re.compile(r'(?<!\d)(0[1-9]|1[0-2])[-_/.](0[1-9]|[12]\d|3[01])[-_/.](20\d{2}|19\d{2})(?!\d)'),
]


def extract_arxiv_id(value: str) -> str | None:
    value = value.strip()
    match = ARXIV_RE.search(value)
    if not match:
        return None
    return match.group(1)


def _normalize_datetime(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def _extract_date_components(text: str) -> tuple[int, int, int] | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        groups = match.groups()
        if len(groups[0]) == 4:
            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
        else:
            month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
        try:
            datetime(year, month, day)
        except ValueError:
            continue
        return year, month, day
    return None


def _candidate_texts(raw: str) -> list[str]:
    texts = [raw]
    parsed = urlparse(raw)
    if parsed.path:
        texts.append(unquote(parsed.path))
    if parsed.query:
        texts.append(unquote(parsed.query))
        for values in parse_qs(parsed.query).values():
            texts.extend(unquote(value) for value in values)
    return texts


def extract_source_date(value: str) -> datetime | None:
    raw = value.strip()
    for text in _candidate_texts(raw):
        parts = _extract_date_components(text)
        if parts:
            year, month, day = parts
            return datetime(year, month, day, 0, 0)
    return None


def build_pseudo_arxiv_id(value: str) -> str:
    raw = value.strip()
    now = datetime.now()
    time_code = int(now.strftime("%y%m%d%H%M%S")) * 1000 + now.microsecond // 1000
    pid = os.getpid()
    mix = f"{time_code}-{pid}"
    digest = hashlib.sha1(mix.encode("utf-8")).hexdigest()
    suffix_num = int(digest[:10], 16) % 100000
    if suffix_num == 0:
        suffix_num = (time_code + pid) % 100000 or 1
    return f"0000.{suffix_num:05d}"


def classify_source(value: str, is_arxiv: bool) -> str:
    if is_arxiv:
        return 'arxiv'
    raw = value.strip().lower()
    if raw.startswith(('http://', 'https://')):
        return 'pdf' if '.pdf' in raw else 'url'
    if raw.endswith('.pdf'):
        return 'pdf'
    return 'url'


def extract_paper_id(value: str) -> tuple[str, bool]:
    arxiv_id = extract_arxiv_id(value)
    if arxiv_id:
        return arxiv_id, True
    return build_pseudo_arxiv_id(value), False


def note_path(vault: Path, paper_id: str) -> Path:
    return vault / 'papers' / 'notes' / f'{paper_id}.md'


def pdf_path(vault: Path, paper_id: str) -> Path:
    return vault / 'assets' / 'pdfs' / f'{paper_id}.pdf'


def mineru_dir(vault: Path, paper_id: str) -> Path:
    return vault / 'assets' / 'mineru' / paper_id


def mineru_markdown(vault: Path, paper_id: str) -> Path | None:
    doc_dir = mineru_dir(vault, paper_id)
    candidates = [doc_dir / f'{paper_id}.md', doc_dir / 'full.md']
    for path in candidates:
        if path.exists() and path.stat().st_size > 0:
            return path
    return None


def cmd_paths(args: argparse.Namespace) -> int:
    vault = Path(args.vault)
    paper_id, is_arxiv = extract_paper_id(args.paper)
    src_type = classify_source(args.paper, is_arxiv)
    print(f'PAPER_ID={paper_id}')
    print(f'IS_ARXIV={1 if is_arxiv else 0}')
    print(f'ARXIV_ID={paper_id if is_arxiv else ""}')
    print(f'SOURCE_TYPE={src_type}')
    print(f'SOURCE_URL={args.paper if src_type in {"url", "pdf"} else ""}')
    print(f'NOTE_PATH={note_path(vault, paper_id)}')
    print(f'PDF_PATH={pdf_path(vault, paper_id)}')
    print(f'MINERU_DIR={mineru_dir(vault, paper_id)}')
    md = mineru_markdown(vault, paper_id)
    print(f'MINERU_MD={md if md else ""}')
    return 0


def cmd_exists(args: argparse.Namespace) -> int:
    vault = Path(args.vault)
    paper_id, _ = extract_paper_id(args.paper)
    path = note_path(vault, paper_id)
    print('1' if path.exists() else '0')
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Helpers for paper-reading skill')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_paths = sub.add_parser('paths')
    p_paths.add_argument('--vault', default=os.environ.get('OBSIDIAN_VAULT', ''))
    p_paths.add_argument('--paper', '--arxiv', dest='paper', required=True)
    p_paths.set_defaults(func=cmd_paths)

    p_exists = sub.add_parser('exists')
    p_exists.add_argument('--vault', default=os.environ.get('OBSIDIAN_VAULT', ''))
    p_exists.add_argument('--paper', '--arxiv', dest='paper', required=True)
    p_exists.set_defaults(func=cmd_exists)

    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, 'vault', None) and args.cmd in {'paths', 'exists'}:
        print('OBSIDIAN_VAULT is required', file=sys.stderr)
        sys.exit(1)
    sys.exit(args.func(args))

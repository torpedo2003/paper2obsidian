from __future__ import annotations

import os
import shutil
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse
from os.path import basename
import requests

API_BASE = "https://mineru.net/api/v4"
SUPPORTED_EXTS = {".pdf", ".docx", ".pptx", ".jpg", ".jpeg", ".png"}
DEFAULT_MODEL = "pipeline"
DEFAULT_LANGUAGE = "auto"
DEFAULT_TIMEOUT = 600
DEFAULT_POLL_INTERVAL = 5
DEFAULT_RETRIES = 5


@dataclass(frozen=True)
class ParseOptions:
    model: str = DEFAULT_MODEL
    language: str = DEFAULT_LANGUAGE
    enable_formula: bool = True
    enable_table: bool = True
    poll_interval: int = DEFAULT_POLL_INTERVAL
    timeout: int = DEFAULT_TIMEOUT
    retries: int = DEFAULT_RETRIES
    resume: bool = False
    workers: int = 5


@dataclass(frozen=True)
class ParseResult:
    ok: bool
    name: str
    detail: str = ""
    skipped: bool = False


def collect_files(path: Path, recursive: bool = False) -> List[Path]:
    iterator: Iterable[Path]
    iterator = path.rglob("*") if recursive else path.iterdir()
    return sorted(
        file_path
        for file_path in iterator
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTS
    )


def get_token(explicit_token: Optional[str]) -> str:
    token = explicit_token or os.environ.get("MINERU_TOKEN")
    if not token:
        raise ValueError(
            "No API token provided. Set MINERU_TOKEN or use --token. "
            "Get one at https://mineru.net/user-center/api-token"
        )
    return token


class MinerUClient:
    def __init__(self, token: str, timeout: int = DEFAULT_TIMEOUT):
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()

    def headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Accept": "*/*",
        }

    def create_batch_upload(
        self,
        filename: str,
        data_id: str,
        model: str,
        language: str,
        enable_formula: bool,
        enable_table: bool,
    ) -> Tuple[str, str]:
        payload = {
            "files": [{"name": filename, "data_id": data_id}],
            "model_version": model,
            "enable_formula": enable_formula,
            "enable_table": enable_table,
        }
        if language != DEFAULT_LANGUAGE:
            payload["language"] = language

        response = self.session.post(
            f"{API_BASE}/file-urls/batch",
            headers=self.headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        if result.get("code") != 0:
            raise RuntimeError(result.get("msg", "failed to create upload url"))

        data = result["data"]
        return data["batch_id"], data["file_urls"][0]

    def upload_file(self, upload_url: str, file_path: Path) -> None:
        with file_path.open("rb") as file_obj:
            response = self.session.put(upload_url, data=file_obj, timeout=300)
        if response.status_code not in (200, 203):
            raise RuntimeError(f"upload failed: {response.status_code}")

    def poll_result(
        self,
        batch_id: str,
        timeout: int,
        poll_interval: int,
    ) -> dict:
        start = time.time()
        while time.time() - start < timeout:
            response = self.session.get(
                f"{API_BASE}/extract-results/batch/{batch_id}",
                headers=self.headers(),
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            extract_results = result["data"]["extract_result"]
            if not extract_results:
                time.sleep(poll_interval)
                continue

            first = extract_results[0]
            state = first.get("state")
            if state == "done":
                return first
            if state == "failed":
                raise RuntimeError(first.get("err_msg", "parse failed"))
            time.sleep(poll_interval)

        raise TimeoutError(f"timed out waiting for batch {batch_id}")

    def create_url_task(
        self,
        src_url: str,
        data_id: str,
        model: str,
        enable_formula: bool,
        enable_table: bool,
    ) -> str:
        payload = {
            "url": src_url,
            "model_version": model,
            "enable_formula": enable_formula,
            "enable_table": enable_table,
            "data_id": data_id,
        }
        response = self.session.post(
            f"{API_BASE}/extract/task",
            headers=self.headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        if result.get("code") != 0:
            raise RuntimeError(result.get("msg", "failed to create task from url"))
        return result["data"]["task_id"]

    def poll_task(
        self,
        task_id: str,
        timeout: int,
        poll_interval: int,
    ) -> dict:
        start = time.time()
        while time.time() - start < timeout:
            response = self.session.get(
                f"{API_BASE}/extract/task/{task_id}",
                headers=self.headers(),
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("code") != 0:
                raise RuntimeError(result.get("msg", "failed to query task"))

            data = result["data"]
            state = data.get("state")
            if state == "done":
                return data
            if state == "failed":
                raise RuntimeError(data.get("err_msg", "parse failed"))
            time.sleep(poll_interval)

        raise TimeoutError(f"timed out waiting for task {task_id}")

    def download_and_extract(self, zip_url: str, output_dir: Path, stem: str) -> Path:
        zip_path = output_dir / f"{stem}.zip"
        response = self.session.get(zip_url, timeout=300)
        response.raise_for_status()
        zip_path.write_bytes(response.content)

        extract_dir = output_dir / stem
        images_dir = extract_dir / "images"
        extract_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue

                member_path = Path(member.filename)
                member_name = member_path.name

                if member_name == "full.md":
                    with archive.open(member) as src, (extract_dir / f"{stem}.md").open("wb") as dst:
                        shutil.copyfileobj(src, dst)
                    continue

                if "images" not in member_path.parts:
                    continue

                image_idx = member_path.parts.index("images")
                relative_path = Path(*member_path.parts[image_idx + 1 :])
                if not relative_path.parts:
                    continue

                target_path = images_dir / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as src, target_path.open("wb") as dst:
                    shutil.copyfileobj(src, dst)

        zip_path.unlink()
        
        return extract_dir


def process_file(
    client: MinerUClient,
    file_path: Path,
    output_dir: Path,
    options: ParseOptions,
    index: int,
    total: int,
) -> ParseResult:
    stem = file_path.stem
    if options.resume and (output_dir / stem).exists():
        print(f"  [{index}/{total}] skip {stem}")
        return ParseResult(ok=True, name=stem, skipped=True)

    print(f"  [{index}/{total}] upload {stem}", end="", flush=True)
    for attempt in range(1, options.retries + 1):
        try:
            batch_id, upload_url = client.create_batch_upload(
                filename=file_path.name,
                data_id=stem,
                model=options.model,
                language=options.language,
                enable_formula=options.enable_formula,
                enable_table=options.enable_table,
            )
            print(" -> parse", end="", flush=True)
            client.upload_file(upload_url, file_path)
            result = client.poll_result(
                batch_id=batch_id,
                timeout=options.timeout,
                poll_interval=options.poll_interval,
            )
            print(" -> download", end="", flush=True)
            client.download_and_extract(result["full_zip_url"], output_dir, stem)
            print(" -> ok")
            return ParseResult(ok=True, name=stem)
        except Exception as exc:  # noqa: BLE001
            if attempt == options.retries:
                print(f" -> fail ({exc})")
                return ParseResult(ok=False, name=stem, detail=str(exc))
            print(f" -> retry {attempt}", end="", flush=True)
            time.sleep(min(2 ** (attempt - 1), 8))

    return ParseResult(ok=False, name=stem, detail="unexpected failure")


def process_url(
    client: MinerUClient,
    src_url: str,
    output_dir: Path,
    options: ParseOptions,
    index: int,
    total: int,
) -> ParseResult:
    parsed = urlparse(src_url)
    raw_name = basename(parsed.path.rstrip('/'))
    stem = raw_name.replace('.pdf', '') if raw_name.lower().endswith('.pdf') else raw_name
    stem = stem or f"document_{index}"
    
    if options.resume and (output_dir / stem).exists():
        print(f"  [{index}/{total}] skip {stem}")
        return ParseResult(ok=True, name=stem, skipped=True)

    print(f"  [{index}/{total}] remote {stem}", end="", flush=True)
    for attempt in range(1, options.retries + 1):
        try:
            task_id = client.create_url_task(
                src_url=src_url,
                data_id=stem,
                model=options.model,
                enable_formula=options.enable_formula,
                enable_table=options.enable_table,
            )
            print(" -> parse", end="", flush=True)
            result = client.poll_task(
                task_id=task_id,
                timeout=options.timeout,
                poll_interval=options.poll_interval,
            )
            print(" -> download", end="", flush=True)
            client.download_and_extract(result["full_zip_url"], output_dir, stem)
            print(" -> ok")
            return ParseResult(ok=True, name=stem)
        except Exception as exc:  # noqa: BLE001
            if attempt == options.retries:
                print(f" -> fail ({exc})")
                return ParseResult(ok=False, name=stem, detail=str(exc))
            print(f" -> retry {attempt}", end="", flush=True)
            time.sleep(min(2 ** (attempt - 1), 8))

    return ParseResult(ok=False, name=stem, detail="unexpected failure")


def gather_inputs(file_path: Optional[str], dir_path: Optional[str], recursive: bool = False) -> List[Path]:
    if file_path:
        return [Path(file_path)]
    if not dir_path:
        raise ValueError("either --file or --dir is required")
    return collect_files(Path(dir_path), recursive=recursive)


def run_parse(
    token: str,
    input_files: Sequence[Path],
    output_dir: Path,
    options: ParseOptions,
) -> List[ParseResult]:
    output_dir.mkdir(parents=True, exist_ok=True)
    client = MinerUClient(token=token, timeout=options.timeout)
    total = len(input_files)
    if not total:
        return []

    print(
        f"Processing {total} file(s) with workers={options.workers}, "
        f"model={options.model}, language={options.language}"
    )

    if options.workers <= 1:
        return [
            process_file(client, file_path, output_dir, options, index, total)
            for index, file_path in enumerate(input_files, start=1)
        ]

    results: List[ParseResult] = []
    with ThreadPoolExecutor(max_workers=options.workers) as executor:
        futures = {
            executor.submit(process_file, client, file_path, output_dir, options, index, total): file_path
            for index, file_path in enumerate(input_files, start=1)
        }
        for future in as_completed(futures):
            results.append(future.result())
    return results


def run_parse_urls(
    token: str,
    urls: Sequence[str],
    output_dir: Path,
    options: ParseOptions,
) -> List[ParseResult]:
    output_dir.mkdir(parents=True, exist_ok=True)
    client = MinerUClient(token=token, timeout=options.timeout)
    total = len(urls)
    if not total:
        return []

    print(
        f"Processing {total} remote file(s) with workers={options.workers}, "
        f"model={options.model}, language={options.language}"
    )

    if options.workers <= 1:
        return [
            process_url(client, src_url, output_dir, options, index, total)
            for index, src_url in enumerate(urls, start=1)
        ]

    results: List[ParseResult] = []
    with ThreadPoolExecutor(max_workers=options.workers) as executor:
        futures = {
            executor.submit(process_url, client, src_url, output_dir, options, index, total): src_url
            for index, src_url in enumerate(urls, start=1)
        }
        for future in as_completed(futures):
            results.append(future.result())
    return results


def summarize_results(results: Sequence[ParseResult], output_dir: Path) -> int:
    if not results:
        print("No supported files found.")
        return 1

    success = sum(1 for item in results if item.ok and not item.skipped)
    skipped = sum(1 for item in results if item.skipped)
    failed = [item for item in results if not item.ok]

    print("=" * 50)
    print(f"success: {success}")
    print(f"skipped: {skipped}")
    print(f"failed: {len(failed)}")
    if failed:
        print("failed files:")
        for item in failed:
            print(f"  - {item.name}: {item.detail}")
    print(f"output: {output_dir}")
    return 0 if not failed else 1

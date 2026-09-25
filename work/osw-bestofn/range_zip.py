"""Range-only reader for the released OSWorld trajectory ZIPs.

Only callers' requested members are decompressed. This module never writes the ZIP,
screenshots, or trajectory text to the repository.
"""

from __future__ import annotations

import io
import json
import urllib.parse
import urllib.request
import zipfile
from pathlib import PurePosixPath
from typing import Iterable

UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
HF_API = "https://huggingface.co/api/datasets/xlangai/ubuntu_osworld_verified_trajs/tree/main?recursive=true&expand=false"
HF_RESOLVE = "https://huggingface.co/datasets/xlangai/ubuntu_osworld_verified_trajs/resolve/main/"


class HTTPRangeFile(io.RawIOBase):
    def __init__(self, url: str) -> None:
        self.url = url
        self.position = 0
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(request) as response:
            self.size = int(response.headers["Content-Length"])
        self.fetched_bytes = 0

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self.position = offset
        elif whence == 1:
            self.position += offset
        elif whence == 2:
            self.position = self.size + offset
        else:
            raise ValueError(f"unsupported seek mode: {whence}")
        return self.position

    def readinto(self, buffer: bytearray) -> int:
        if self.position >= self.size:
            return 0
        end = min(self.position + len(buffer), self.size) - 1
        request = urllib.request.Request(
            self.url,
            headers={"User-Agent": UA, "Range": f"bytes={self.position}-{end}"},
        )
        with urllib.request.urlopen(request) as response:
            data = response.read()
        buffer[: len(data)] = data
        self.position += len(data)
        self.fetched_bytes += len(data)
        return len(data)


def open_remote_zip(url: str) -> tuple[zipfile.ZipFile, HTTPRangeFile]:
    remote = HTTPRangeFile(url)
    archive = zipfile.ZipFile(io.BufferedReader(remote, buffer_size=1 << 20))
    return archive, remote


def list_root_archives() -> list[dict[str, object]]:
    request = urllib.request.Request(HF_API, headers={"User-Agent": UA})
    with urllib.request.urlopen(request) as response:
        rows = json.load(response)
    return [row for row in rows if row.get("path", "").endswith(".zip")]


def archive_url(filename: str) -> str:
    return HF_RESOLVE + urllib.parse.quote(filename, safe="/._-")


def result_members(archive: zipfile.ZipFile) -> list[str]:
    return sorted(name for name in archive.namelist() if name.endswith("result.txt"))


def task_key(member: str) -> str:
    parts = PurePosixPath(member).parts
    if len(parts) < 3 or parts[-1] != "result.txt":
        raise ValueError(f"unexpected result member: {member}")
    return "/".join(parts[-3:-1])


def read_result(archive: zipfile.ZipFile, member: str) -> int:
    value = archive.read(member).decode("utf-8", "replace").strip()
    try:
        numeric = float(value)
    except ValueError as exc:
        raise ValueError(
            f"{member}: expected official result 0/1, got {value!r}"
        ) from exc
    if numeric not in {0.0, 1.0}:
        raise ValueError(f"{member}: expected official result 0/1, got {value!r}")
    return int(numeric)


def archive_score(archive: zipfile.ZipFile) -> tuple[dict[str, int], int]:
    members = result_members(archive)
    rows = {task_key(member): read_result(archive, member) for member in members}
    return rows, sum(rows.values())

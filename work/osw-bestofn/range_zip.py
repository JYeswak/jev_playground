"""Range-only reader for the released OSWorld trajectory ZIPs.

Only callers' requested members are decompressed. This module never writes the ZIP,
screenshots, or trajectory text to the repository.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import io
import json
import urllib.parse
import urllib.request
import zipfile
import struct
import zlib
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
            self.url = response.geturl()
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

    def fetch_range(self, start: int, end: int) -> bytes:
        if start > end:
            return b""
        request = urllib.request.Request(
            self.url,
            headers={"User-Agent": UA, "Range": f"bytes={start}-{end}"},
        )
        with urllib.request.urlopen(request) as response:
            data = response.read()
        self.fetched_bytes += len(data)
        return data


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


def read_member_bytes(
    archive: zipfile.ZipFile, remote: HTTPRangeFile, member: str
) -> bytes:
    info = archive.getinfo(member)
    header = remote.fetch_range(info.header_offset, info.header_offset + 255)
    (
        signature,
        _v,
        _flags,
        _method,
        _time,
        _date,
        _crc,
        _csize,
        _usize,
        filename_len,
        extra_len,
    ) = struct.unpack_from("<4s5H3I2H", header)
    if signature != b"PK\x03\x04":
        raise ValueError(f"{member}: invalid local ZIP header")
    data_start = info.header_offset + 30 + filename_len + extra_len
    relative_start = 30 + filename_len + extra_len
    if relative_start + info.compress_size <= len(header):
        data = header[relative_start : relative_start + info.compress_size]
    else:
        data = remote.fetch_range(data_start, data_start + info.compress_size - 1)
    if info.compress_type == zipfile.ZIP_STORED:
        decoded = data
    elif info.compress_type == zipfile.ZIP_DEFLATED:
        decoded = zlib.decompress(data, -15)
    else:
        return archive.read(member)
    if len(decoded) != info.file_size:
        raise ValueError(
            f"{member}: range length={len(decoded)} expected={info.file_size}"
        )
    return decoded


def read_result(
    archive: zipfile.ZipFile, member: str, remote: HTTPRangeFile | None = None
) -> float:
    source = (
        read_member_bytes(archive, remote, member)
        if remote is not None
        else archive.read(member)
    )
    value = source.decode("utf-8", "replace").strip()
    try:
        numeric = float(value)
    except ValueError as exc:
        raise ValueError(
            f"{member}: expected official result in [0,1], got {value!r}"
        ) from exc
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{member}: expected official result in [0,1], got {value!r}")
    return numeric


def archive_score(
    archive: zipfile.ZipFile, remote: HTTPRangeFile | None = None
) -> tuple[dict[str, int], int]:
    members = result_members(archive)

    def read_one(member: str) -> tuple[str, int]:
        return task_key(member), read_result(archive, member, remote)

    with ThreadPoolExecutor(max_workers=32) as executor:
        rows = dict(executor.map(read_one, members))
    return rows, sum(rows.values())

"""Idempotent marked-block append/remove for shell rc files."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path


def block_begin(block_id: str) -> str:
    return f"# >> faah:{block_id}\n"


def block_end(block_id: str) -> str:
    return f"# << faah:{block_id}\n"


def has_block(content: str, block_id: str) -> bool:
    return f"# >> faah:{block_id}" in content


def remove_block_lines(content: str, block_id: str) -> str:
    begin = f"# >> faah:{block_id}"
    end = f"# << faah:{block_id}"
    lines = content.splitlines(keepends=True)
    out: list[str] = []
    skip = False
    for line in lines:
        if line.rstrip("\r\n") == begin.rstrip("\n"):
            skip = True
            continue
        if line.rstrip("\r\n") == end.rstrip("\n"):
            skip = False
            continue
        if not skip:
            out.append(line)
    return "".join(out)


def append_block(content: str, block_id: str, body: str) -> str:
    if has_block(content, block_id):
        return content
    sep = "" if content.endswith("\n") or not content else "\n"
    block = f"\n{block_begin(block_id)}{body}{block_end(block_id)}"
    return content + sep + block


def backup_if_exists(path: Path) -> Path | None:
    if not path.is_file():
        return None
    from datetime import datetime

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    bak = path.with_name(f"{path.name}.faahbak.{ts}")
    shutil.copy2(path, bak)
    return bak


def read_rc(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_rc(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@dataclass
class RcEditResult:
    path: Path
    changed: bool
    backup: Path | None


def ensure_block(
    rc_path: Path,
    block_id: str,
    body: str,
    *,
    backup: bool = True,
) -> RcEditResult:
    content = read_rc(rc_path)
    if has_block(content, block_id):
        return RcEditResult(rc_path, False, None)
    bkp = backup_if_exists(rc_path) if backup else None
    new_content = append_block(content, block_id, body)
    write_rc(rc_path, new_content)
    return RcEditResult(rc_path, True, bkp)


def remove_block_file(rc_path: Path, block_id: str, *, backup: bool = True) -> RcEditResult:
    if not rc_path.is_file():
        return RcEditResult(rc_path, False, None)
    content = read_rc(rc_path)
    if not has_block(content, block_id):
        return RcEditResult(rc_path, False, None)
    bkp = backup_if_exists(rc_path) if backup else None
    new_content = remove_block_lines(content, block_id)
    # Trim excessive blank lines at EOF
    new_content = re.sub(r"\n{3,}\Z", "\n\n", new_content)
    write_rc(rc_path, new_content)
    return RcEditResult(rc_path, True, bkp)

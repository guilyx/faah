"""Copy Cursor/VS Code helper fragments into the managed install directory."""

from __future__ import annotations

import shutil
from importlib.resources import as_file, files
from pathlib import Path


def install_editor_helpers(
    managed_root: Path,
    *,
    cursor: bool = False,
    vscode: bool = False,
) -> list[Path]:
    """Copy bundled cursor/ and vscode/ under managed_root/install/."""
    out: list[Path] = []
    data_trav = files("faah").joinpath("data")
    with as_file(data_trav) as data_path:
        data_path = Path(data_path)
        install_base = managed_root / "install"
        if cursor:
            src = data_path / "cursor"
            if src.is_dir():
                dst = install_base / "cursor"
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                out.append(dst)
        if vscode:
            src = data_path / "vscode"
            if src.is_dir():
                dst = install_base / "vscode"
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                out.append(dst)
    return out


def remove_editor_artifacts(managed_root: Path) -> None:
    install_base = managed_root / "install"
    for name in ("cursor", "vscode"):
        p = install_base / name
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
    if install_base.is_dir():
        try:
            install_base.rmdir()
        except OSError:
            pass

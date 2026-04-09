"""Install the built wheel into an isolated venv and run the real `faah` binary.

Uses a temporary HOME so install never touches the developer's ~/.zshrc.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from faah import __version__

REPO_ROOT = Path(__file__).resolve().parents[1]


def isolated_user_env(home: Path) -> dict[str, str]:
    """HOME and XDG_CONFIG_HOME so `~/.config/faah` resolves under `home`.

    CI often sets ``XDG_CONFIG_HOME``. If we only set ``HOME``, managed config
    still follows XDG and syncs outside the temp directory.
    """
    return {
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / ".config"),
    }


def _run(
    argv: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    base = {**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    if env:
        base.update(env)
    return subprocess.run(  # noqa: S603
        argv,
        cwd=cwd,
        env=base,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module")
def faah_wheel_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build one wheel for all tests in this module."""
    out = tmp_path_factory.mktemp("wheelhouse")
    proc = _run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(out)],
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    wheels = sorted(out.glob("faah-*.whl"))
    assert len(wheels) == 1, f"expected one wheel, got {list(out.iterdir())}"
    return wheels[0]


@pytest.fixture(scope="module")
def venv_with_wheel(
    tmp_path_factory: pytest.TempPathFactory,
    faah_wheel_path: Path,
) -> Path:
    """Single venv with the wheel installed once (shared across tests)."""
    root = tmp_path_factory.mktemp("packaging-venv")
    venv = root / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)  # noqa: S603
    pip = venv / "bin" / "pip"
    proc = _run([str(pip), "install", str(faah_wheel_path)])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return venv


@pytest.fixture()
def isolated_home(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    return home


def test_wheel_install_faah_version(venv_with_wheel: Path, isolated_home: Path) -> None:
    faah = venv_with_wheel / "bin" / "faah"
    proc = _run([str(faah), "--version"], env=isolated_user_env(isolated_home))
    assert proc.returncode == 0
    assert __version__ in (proc.stdout + proc.stderr)


def test_wheel_install_python_module_version(venv_with_wheel: Path, isolated_home: Path) -> None:
    py = venv_with_wheel / "bin" / "python"
    proc = _run(
        [str(py), "-m", "faah", "--version"],
        env=isolated_user_env(isolated_home),
    )
    assert proc.returncode == 0
    assert __version__ in (proc.stdout + proc.stderr)


def test_wheel_install_doctor_exits_zero(venv_with_wheel: Path, isolated_home: Path) -> None:
    faah = venv_with_wheel / "bin" / "faah"
    proc = _run([str(faah), "doctor"], env=isolated_user_env(isolated_home))
    assert proc.returncode == 0
    out = proc.stdout + proc.stderr
    assert "faah doctor" in out or "mpv" in out or "fzf" in out or "sound" in out.lower()


def test_wheel_install_syncs_data_without_rc(
    venv_with_wheel: Path,
    isolated_home: Path,
) -> None:
    """Non-interactive install with all shell/editor options off only syncs ~/.config/faah."""
    faah = venv_with_wheel / "bin" / "faah"
    env = isolated_user_env(isolated_home)
    proc = _run(
        [
            str(faah),
            "install",
            "--yes",
            "--no-zsh",
            "--no-bash",
            "--no-fzf",
            "--no-cursor",
            "--no-vscode",
        ],
        env=env,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    sound = isolated_home / ".config" / "faah" / "assets" / "sounds" / "fahhh.mp3"
    play = isolated_home / ".config" / "faah" / "scripts" / "play-faah.sh"
    assert sound.is_file()
    assert play.is_file()
    assert not (isolated_home / ".zshrc").exists()


def test_wheel_install_writes_zshrc_block(
    venv_with_wheel: Path,
    isolated_home: Path,
) -> None:
    faah = venv_with_wheel / "bin" / "faah"
    env = isolated_user_env(isolated_home)
    proc = _run(
        [
            str(faah),
            "install",
            "--yes",
            "--zsh",
            "--no-bash",
            "--no-fzf",
            "--no-cursor",
            "--no-vscode",
        ],
        env=env,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    zshrc = isolated_home / ".zshrc"
    assert zshrc.is_file()
    text = zshrc.read_text(encoding="utf-8")
    assert "# >> faah:zsh" in text
    assert "init/faah.zsh" in text
    assert "FAHH_DISABLE_MATRIX" not in text


def test_wheel_install_play_returns_expected_code(
    venv_with_wheel: Path,
    isolated_home: Path,
) -> None:
    """After sync, `faah play` runs; exit 0 if a player exists, else 1."""
    faah = venv_with_wheel / "bin" / "faah"
    env = isolated_user_env(isolated_home)
    _run(
        [
            str(faah),
            "install",
            "--yes",
            "--no-zsh",
            "--no-bash",
            "--no-fzf",
            "--no-cursor",
            "--no-vscode",
        ],
        env=env,
    )
    proc = _run([str(faah), "play"], env=env)
    assert proc.returncode in (0, 1)


def test_editable_install_faah_version(tmp_path: Path, isolated_home: Path) -> None:
    """Smoke-test `pip install -e .` from the repo (developer workflow)."""
    venv = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)  # noqa: S603
    pip = venv / "bin" / "pip"
    proc = _run([str(pip), "install", "-e", "."], cwd=REPO_ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    faah = venv / "bin" / "faah"
    proc2 = _run([str(faah), "--version"], env=isolated_user_env(isolated_home))
    assert proc2.returncode == 0
    assert __version__ in (proc2.stdout + proc2.stderr)

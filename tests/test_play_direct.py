"""`faah play` and `play_faah_sound`."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from faah.cli import app
from faah.sound import play_faah_sound, resolve_sound_path_for_play

runner = CliRunner()


def test_resolve_sound_path_after_sync(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    sp = resolve_sound_path_for_play()
    assert sp.is_file()
    assert sp.name == "fahhh.mp3"


def test_play_faah_sound_no_player_returns_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    resolve_sound_path_for_play()
    monkeypatch.setattr("faah.sound.shutil.which", lambda _: None)
    assert play_faah_sound() == 1


def test_faah_play_cli_exits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    r = runner.invoke(app, ["play"])
    assert r.exit_code in (0, 1)


def test_play_sound_mpv_argv_includes_no_window_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mp3 = tmp_path / "x.mp3"
    mp3.write_bytes(b"x")

    argv: list[str] | None = None

    def fake_which(cmd: str) -> str | None:
        return "/bin/mpv" if cmd == "mpv" else None

    def fake_run(cmd: list[str], **_kwargs: object) -> MagicMock:
        nonlocal argv
        argv = list(cmd)
        return MagicMock(returncode=0)

    monkeypatch.setattr("faah.sound.shutil.which", fake_which)
    monkeypatch.setattr("faah.sound.subprocess.run", fake_run)

    from faah.sound import play_sound

    assert play_sound(mp3, background=False) == 0
    assert argv is not None
    assert argv[0] == "/bin/mpv"
    assert "--no-terminal" in argv
    assert "--force-window=no" in argv
    assert "--no-video" in argv
    assert "--vo=null" in argv
    assert str(mp3) in argv


def test_play_sound_ffplay_includes_nodisp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mp3 = tmp_path / "x.mp3"
    mp3.write_bytes(b"x")

    argv: list[str] | None = None

    def fake_which(cmd: str) -> str | None:
        if cmd == "mpv":
            return None
        if cmd == "ffplay":
            return "/bin/ffplay"
        return None

    def fake_run(cmd: list[str], **_kwargs: object) -> MagicMock:
        nonlocal argv
        argv = list(cmd)
        return MagicMock(returncode=0)

    monkeypatch.setattr("faah.sound.shutil.which", fake_which)
    monkeypatch.setattr("faah.sound.subprocess.run", fake_run)

    from faah.sound import play_sound

    assert play_sound(mp3, background=False) == 0
    assert argv is not None
    assert "-nodisp" in argv
    assert str(mp3) in argv


def test_play_sound_paplay_includes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mp3 = tmp_path / "x.mp3"
    mp3.write_bytes(b"x")

    argv: list[str] | None = None

    def fake_which(cmd: str) -> str | None:
        if cmd in ("mpv", "ffplay"):
            return None
        if cmd == "paplay":
            return "/bin/paplay"
        return None

    def fake_run(cmd: list[str], **_kwargs: object) -> MagicMock:
        nonlocal argv
        argv = list(cmd)
        return MagicMock(returncode=0)

    monkeypatch.setattr("faah.sound.shutil.which", fake_which)
    monkeypatch.setattr("faah.sound.subprocess.run", fake_run)

    from faah.sound import play_sound

    assert play_sound(mp3, background=False) == 0
    assert argv == ["/bin/paplay", str(mp3)]

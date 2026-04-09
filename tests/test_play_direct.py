"""`faah play` and `play_faah_sound`."""

from pathlib import Path

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

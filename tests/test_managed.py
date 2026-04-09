"""Tests for managed config sync safety."""

from pathlib import Path

import pytest

from faah.installer.managed import sync_managed_config, unsafe_managed_dest_reason


def test_unsafe_when_resolved_path_is_faah_source_tree(tmp_path: Path) -> None:
    repo = tmp_path / "faah"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='faah'\n", encoding="utf-8")
    (repo / "src" / "faah").mkdir(parents=True)
    (repo / "src" / "faah" / "__init__.py").write_text('"""x"""\n', encoding="utf-8")

    assert unsafe_managed_dest_reason(repo) is not None
    with pytest.raises(ValueError, match="source|checkout|repository"):
        sync_managed_config(dest=repo)


def test_safe_under_dot_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    dest = tmp_path / ".config" / "faah"
    assert unsafe_managed_dest_reason(dest) is None
    sync_managed_config()
    assert (dest / "init" / "faah.zsh").is_file()

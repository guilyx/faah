"""Tests for rc block editing."""

from pathlib import Path

from faah.installer.rc import append_block, has_block, remove_block_lines


def test_append_idempotent() -> None:
    body = "echo hi\n"
    c1 = append_block("", "zsh", body)
    assert has_block(c1, "zsh")
    c2 = append_block(c1, "zsh", body)
    assert c1 == c2


def test_remove_block(tmp_path: Path) -> None:
    content = append_block("", "bash", "x\n")
    assert has_block(content, "bash")
    stripped = remove_block_lines(content, "bash")
    assert not has_block(stripped, "bash")


def test_backup_and_ensure(tmp_path: Path) -> None:
    from faah.installer.rc import ensure_block

    rc = tmp_path / ".zshrc"
    rc.write_text("# old\n", encoding="utf-8")
    r = ensure_block(rc, "zsh", "line\n", backup=True)
    assert r.changed
    assert r.backup is not None
    assert r.backup.is_file()
    r2 = ensure_block(rc, "zsh", "line\n", backup=True)
    assert not r2.changed

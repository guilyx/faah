# faah

Play a short sound when your interactive shell hits **“command not found” (127)** or **“not executable” (126)** by default — not for every failing command (`false`, `grep` miss, etc.), unless you opt in. Optional **fzf** defaults and **Cursor** / **VS Code** helper file copies.

## Install (PyPI / uv) — recommended

```bash
pip install faah
# or
uv tool install faah
```

Then run the interactive installer (requires a TTY):

```bash
faah
# same as:
faah install
```

This syncs bundled shell assets into **`~/.config/faah/`** and adds a **single marked block** to `~/.zshrc` and/or `~/.bashrc` that sources the managed `init/faah.{zsh,bash}` files.

Non-interactive (e.g. CI):

```bash
faah install --yes
```

Other commands:

| Command | Purpose |
|---------|---------|
| `faah doctor` | Check mpv/ffplay/paplay/aplay, fzf, sound file |
| `faah doctor --fix` | On Debian/Ubuntu with `apt-get`, install missing tools (sudo) |
| `faah play` | Play the sound once |
| `faah uninstall` | Remove faah blocks from rc files and `install/` helpers |
| `faah --version` | Package version |

Upgrade:

```bash
pip install -U faah
# or
uv tool upgrade faah
```

## Development (from this repo)

Uses **[uv](https://docs.astral.sh/uv/)** (see `pyproject.toml` and `uv.lock`).

```bash
uv sync --all-extras
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest -q
uv run ruff check src tests
uv run python -m build
```

Console entrypoint: `faah` → `faah.cli:main`.

## Layout

| Path | Role |
|------|------|
| [src/faah/](src/faah/) | Python package (CLI, installer, bundled `data/`) |
| [assets/sounds/fahhh.mp3](assets/sounds/fahhh.mp3) | Source copy of default sound (also shipped in the wheel under `faah/data/`) |
| [scripts/play-faah.sh](scripts/play-faah.sh) | Shell player script (bundled into `~/.config/faah/scripts/` by the installer) |
| [zsh/faah.zsh](zsh/faah.zsh), [bash/faah.bash](bash/faah.bash) | Hook sources (mirrored under `src/faah/data/`) |
| [fzf/](fzf/) | fzf defaults + integration |
| [cursor/](cursor/), [vscode/](vscode/) | Editor helper fragments (copied to `~/.config/faah/install/` when selected) |
| [.setup/](.setup/) | **Deprecated** wrappers; prefer `faah` CLI ([.setup/README.md](.setup/README.md)) |

## Environment variables

| Variable | Meaning |
|----------|---------|
| `FAHH_ROOT` | Managed config root (default: `~/.config/faah` when using installed snippets) |
| `FAHH_SOUND` | Path to sound file (default: `$FAHH_ROOT/assets/sounds/fahhh.mp3`) |
| `FAHH_DISABLED` | If non-empty, hooks do nothing |
| `FAHH_PLAY_ON_NONZERO` | If set and `FAHH_PLAY_EXIT_CODES` is unset: play on any non-zero exit |
| `FAHH_PLAY_EXIT_CODES` | Space-separated codes that trigger sound (default: `127 126`). Use `all` for any non-zero. |
| `FAHH_IGNORE_EXIT` | When mode is `all`: codes to never trigger sound (default: `130`) |

## Troubleshooting

- **No sound**: Install **mpv** or **ffplay**; run `faah doctor`.
- **Editors**: Integrated terminals must load your interactive shell rc. See [cursor/README.md](cursor/README.md) and [vscode/README.md](vscode/README.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Pre-commit (optional)

```bash
pre-commit install
pre-commit run -a
```

## License

Scripts and documentation: [MIT License](LICENSE) (`SPDX-License-Identifier: MIT`).

The bundled sound may be subject to separate rights; replace it with your own file if needed.

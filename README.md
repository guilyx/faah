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

## Repository layout

Everything user-facing after install lives under **`~/.config/faah/`**, populated from a **single bundled tree** in the Python package:

```text
src/faah/
├── __init__.py          # version
├── cli.py               # Typer CLI
├── sound.py             # play MP3 via mpv/ffplay/…
├── installer/           # rc blocks, sync bundled data, editor copies
└── data/                # only copy of shell assets (sdist/wheel)
    ├── assets/sounds/fahhh.mp3
    ├── scripts/play-faah.sh
    ├── zsh/  bash/  fzf/  init/
    ├── cursor/          # optional editor fragments (→ install/cursor when selected)
    └── vscode/
tests/                     # pytest
.github/workflows/         # CI + PyPI publish
```

| Path | Role |
|------|------|
| [src/faah/](src/faah/) | Python package; **`src/faah/data/`** is the bundled shell + sound + editor snippets |
| [src/faah/data/cursor/README.md](src/faah/data/cursor/README.md) | Cursor terminal notes |
| [src/faah/data/vscode/README.md](src/faah/data/vscode/README.md) | VS Code terminal notes |

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
- **Editors**: Integrated terminals must load your interactive shell rc. See [src/faah/data/cursor/README.md](src/faah/data/cursor/README.md) and [src/faah/data/vscode/README.md](src/faah/data/vscode/README.md).

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

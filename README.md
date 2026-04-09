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

Use **`faah help`** for usage (preferred over **`faah --help`**; both work).

This syncs bundled shell assets into **`~/.config/faah/`** (or **`$XDG_CONFIG_HOME/faah`** when `XDG_CONFIG_HOME` is set) and adds a **single marked block** to `~/.zshrc` and/or `~/.bashrc` that sources the managed `init/faah.{zsh,bash}` files.

Non-interactive (e.g. CI):

```bash
faah install --yes
```

During **`faah install`**, you can opt out of the usage-error banner with **`--no-fah-banner`** (adds **`export FAHH_FAH_BANNER=0`** to shell rc for the shells you install).

Other commands:

| Command | Purpose |
|---------|---------|
| `faah help` | Show CLI usage (preferred over **`faah --help`**) |
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

If you previously installed **`2.0.0rc1`**, upgrade with **`pip install -U faah`** (or **`uv tool upgrade faah`**) to get the current **2.0.x** line (**`2.0.1`** includes the mpv no-window fix for **`faah play`** / **`play-faah.sh`**).

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
| `XDG_CONFIG_HOME` | If set, managed config is **`$XDG_CONFIG_HOME/faah`** (must not point at a parent of your clone such that this path equals the repository root). If **unset**, faah uses **`~/.config/faah`** (i.e. `$HOME/.config/faah`). |
| `FAHH_ROOT` | Managed config root (default: `~/.config/faah` when using installed snippets) |
| `FAHH_SOUND` | Path to sound file (default: `$FAHH_ROOT/assets/sounds/fahhh.mp3`) |
| `FAHH_DISABLED` | If non-empty, hooks do nothing |
| `FAHH_PLAY_ON_NONZERO` | If set and `FAHH_PLAY_EXIT_CODES` is unset: play on any non-zero exit |
| `FAHH_PLAY_EXIT_CODES` | Space-separated codes that trigger sound (default: `127 126`). Use `all` for any non-zero. |
| `FAHH_IGNORE_EXIT` | When mode is `all`: codes to never trigger sound (default: `130`) |
| `FAHH_FAH_BANNER` | If **`0`**, **`false`**, **`no`**, or **`off`**, suppress the ASCII **FAAAAAAAAAAAAH** banner on CLI usage mistakes (Typer exit **2**). Default: enabled. Set via env or **`faah install --no-fah-banner`**. |

## Troubleshooting

- **No sound**: Install **mpv** or **ffplay**; run `faah doctor`.
- **A window opens when playing** (mpv/ffplay): faah passes **`--force-window=no`** and **`--no-video`** to **mpv**, and **`-nodisp`** to **ffplay**. Run **`faah install --yes`** to refresh **`~/.config/faah/scripts/play-faah.sh`**, or upgrade faah. If it persists, check **`mpv --version`** and your desktop session (Wayland/X11).
- **`faah install` runs the hook instead of the CLI** (e.g. you see **`faah:source:`** and the Python CLI never runs): Older rc snippets defined a **shell function** named **`faah`** that **shadowed** the real `faah` on your `PATH`. **Workaround:** run **`command faah install --yes`** once (zsh/bash: bypasses the function; same idea as **`\faah`** in zsh). After that, **`faah install`** updates the marked block to a one-liner that does **not** define `faah`, so the CLI works normally.
- **`source: no such file ... ~/.config/faah/init/faah.zsh`**: Your rc still runs the faah bootstrap, but **`~/.config/faah`** is missing or incomplete (removed by hand, failed install, etc.). **Fix:** run **`faah install --yes`** (or **`command faah install --yes`** if the function still shadows—see above), or remove the faah block from `~/.zshrc` / `~/.bashrc` (see **`faah uninstall`**). To edit rc without loading it: `zsh -f` then `nano ~/.zshrc`. The managed line is **`[[ -r ... ]] && source ...`** so a **missing top-level init file** does not error on startup.
- **Other errors from faah on startup**: The rc line only skips loading when that **main** `init/faah.{zsh,bash}` is absent or not readable. It does **not** silence failures from **`source`** itself (e.g. syntax error in that file) or from **nested** `source` lines inside managed files (e.g. a partial/corrupt tree). Those messages are intentional so you notice a broken install—run **`faah install --yes`** or **`faah doctor`**, or remove the faah block.
- **`assets/`, `bash/`, `zsh/`, … appeared at the root of your git clone** (with **`XDG_CONFIG_HOME` unset**): The intended location is **`~/.config/faah`**, not the repo. This usually means **`~/.config/faah` was a symlink** to your clone (or **`XDG_CONFIG_HOME`** used to be wrong so **`$XDG_CONFIG_HOME/faah`** was the clone). **Fix:** remove the symlink and use a real directory (`mkdir -p ~/.config/faah` after removing the link), delete stray copies from the clone (`git status`, then remove untracked `assets/`, `bash/`, … only if they are not part of `src/faah/data/`), run **`faah doctor`** — it reports **unsafe** if the resolved path still looks like a source checkout. Newer faah versions **refuse to sync** into a path that looks like the development repository.
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

# Roadmap

This document describes **directional goals** for faah after **2.1.0**. It is not a commitment to ship every item; [CHANGELOG.md](CHANGELOG.md) records what actually landed in each release.

## Plugin-style backends (printing / sounding)

**Motivation:** Today, **terminal-matrix** and **sound** are tightly coupled to concrete implementations (Python `terminal_matrix` + external players via `sound.py` / `play-faah.sh`). A small **plugin or entry-point layer** would let:

- **Visual hooks** (`faah` usage mistakes, shell hooks, optional `command_not_found` replacement) call a **stable interface** (e.g. “render a short effect for this context”) with **built-in default** = current matrix + flood.
- **Audio** use the same idea: **default** = mpv/ffplay/paplay path as today; optional packages expose **alternatives** (e.g. pipe to a user daemon, aplay-only minimal path, or a no-op for CI).

**Sketch:**

- Discover implementations via **`importlib.metadata` entry points** (e.g. `faah.visual`, `faah.sound`) or a thin **pluggy**-style registry, keeping **core** free of heavy optional deps.
- Document **stable contracts** (inputs: exit context, TTY vs non-TTY, duration hints; outputs: subprocess or no-op) so third-party packages can extend behavior without forking.

## Configuration beyond environment variables

- Optional **`~/.config/faah/faah.toml`** (or similar) for defaults that today require many **`FAHH_*`** exports, with **env still overriding** file for scripting and CI.

## Shell parity

- **fish**: hooks and install paths comparable to zsh/bash where demand exists.
- Optional **smoke tests** for generated snippets (static checks or scripted `fish -c` / `bash -c` / `zsh -c`) in CI.

## Observability and ergonomics

- **`faah doctor`**: structured sections for **visual backend**, **sound backend**, **PATH**, **managed tree**; room for **optional checks** registered by plugins later.
- **Single invocation** where possible: reduce repeated `faah` / `python -m faah` subprocess fan-out from hooks (performance and log noise).

## CI and portability

- Headless **matrix** / CLI smoke tests (duration caps, `FAHH_DISABLE_MATRIX` paths) already in motion; extend coverage for **packaging** and **shell refresh** flows.
- Clearer **WSL / Windows** notes when the stack is Python + POSIX shells only (document limitations; no false promises).

## Nice-to-haves

- **Locales / messages**: optional translation of user-facing strings (low priority).
- **Examples**: small “recipe” snippets for **tmux**, **remote SSH**, and **CI** (matrix off, sound on/off).

---

If you want to work on one of these, open an issue or draft a short design note so the approach matches the interfaces above.

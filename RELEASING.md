# Releasing `faah`

This project uses **SemVer**, **Keep a Changelog** (`CHANGELOG.md`), and a **Python package** built with **hatchling** (see `pyproject.toml`).

## Version source of truth

- **`src/faah/__init__.py`**: `__version__` (used by Hatch and `faah --version`).
- Optionally keep root **`VERSION`** in sync for humans/scripts; PyPI uses the Python version.

## Prepare a release

1. Update **`CHANGELOG.md`**: move `[Unreleased]` notes into a new `## [X.Y.Z] - YYYY-MM-DD` section; leave an empty `[Unreleased]` if needed.
2. Bump **`__version__`** in `src/faah/__init__.py`.
3. Commit on `main` (or a release branch), e.g. `chore(release): vX.Y.Z`.

## Tag

```bash
git tag -a "vX.Y.Z" -m "vX.Y.Z"
git push origin main --tags
```

## Publish to PyPI (GitHub Actions)

This repo includes [`.github/workflows/publish.yml`](.github/workflows/publish.yml), which builds with **uv** and publishes using **PyPI Trusted Publishing (OIDC)**.

1. In **PyPI** → your project → **Publishing**, add a **trusted publisher** for this GitHub repo (workflow: `publish.yml`, environment: `pypi` — adjust to match your PyPI settings).
2. In **GitHub** → **Settings → Environments**, create an environment named **`pypi`** if you use environment protection rules.
3. Create a **GitHub Release** (or run the workflow manually). The workflow uploads artifacts from `dist/` to PyPI.

Do **not** commit API tokens; OIDC is preferred.

## Local build sanity check

```bash
uv sync --all-extras
uv run python -m build
```

Artifacts appear under `dist/`.

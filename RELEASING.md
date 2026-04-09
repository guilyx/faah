# Releasing `faah`

This project uses **SemVer**, **Keep a Changelog** (`CHANGELOG.md`), and a **Python package** built with **hatchling** (see `pyproject.toml`).

## Version source of truth

- **`src/faah/__init__.py`**: `__version__` (used by Hatch, `faah --version`, and PyPI).

## Prepare a release

1. Update **`CHANGELOG.md`**: move `[Unreleased]` notes into a new `## [X.Y.Z] - YYYY-MM-DD` section; leave an empty `[Unreleased]` if needed.
2. Bump **`__version__`** in `src/faah/__init__.py`.
3. Commit on `main`, a feature/fix branch, or a dedicated **release branch** (e.g. **`release/2.0.0`** or **`release/2.0.0rc1`** for an RC), then open a PR into `main` as needed. Example message: `chore(release): 2.0.0`.

### Prep branches (e.g. **2.1.0**)

- Use a branch like **`release/2.1.0-prep`** to land changelog + version bumps before tagging.
- While preparing, **`__version__`** may stay on a **PEP 440** pre-release string (e.g. **`2.1.0dev0`**) until you are ready to publish; bump to **`2.1.0`** for the final commit that matches the Git tag and PyPI artifact.
- [ROADMAP.md](ROADMAP.md) holds forward-looking items that are **not** necessarily part of the tagged release; keep [CHANGELOG.md](CHANGELOG.md) aligned with what actually ships.

### Pre-releases (rc, alpha, beta)

Use **PEP 440** versions in **`__version__`** (e.g. **`2.0.0rc1`**, not `2.0.0-rc1` in the Python string—tools normalize for PyPI). Tag as **`v2.0.0rc1`** to match. Consumers install with **`pip install --pre faah`** or pin the exact version. Prefer pushing release prep on **`release/<version>`** so the GitHub Release / PyPI publish workflow targets a clear branch.

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

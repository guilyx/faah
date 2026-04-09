# Releasing `faah`

This repo follows **SemVer** (`MAJOR.MINOR.PATCH`) and **Keep a Changelog** in `CHANGELOG.md`.

## Prepare

- Update `CHANGELOG.md` under `[Unreleased]`
  - Keep entries short and user-facing.
- Decide the next version (SemVer).
- Update `VERSION`.

## Release

From a clean working tree on `main`:

```bash
git checkout main
git pull --ff-only

git add CHANGELOG.md VERSION
git commit -m "chore(release): vX.Y.Z"

git tag -a "vX.Y.Z" -m "vX.Y.Z"
git push origin main --tags
```

## Notes

- `./.setup/install.sh --version` prints the current `VERSION`.


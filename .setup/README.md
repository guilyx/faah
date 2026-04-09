# Setup (deprecated shell entrypoints)

**Prefer the PyPI CLI:** install with `pip install faah` or `uv tool install faah`, then run:

```bash
faah install
```

## Legacy scripts

| Script | Behavior |
|--------|----------|
| [install.sh](install.sh) | If `faah` is on `PATH`, forwards to it; otherwise prints install instructions. |
| [update.sh](update.sh) | Prints how to upgrade the PyPI package or `git pull` for source checkouts. |

For full options, run `faah --help` after installing the package.

# AGENTS.md

## Architecture

Single-file Python 3 CLI. All logic lives in `tch_cli.py` (300 lines). No modules, no packages, no tests.

## Commands

```bash
# Install deps (no version pins)
pip install -r requirements.txt

# Set token (required before download)
python tch_cli.py -t "YOUR_ACCESS_TOKEN"

# Download single textbook
python tch_cli.py -u "https://basic.smartedu.cn/tchMaterial/detail?contentId=xxx"

# Batch download
python tch_cli.py -f urls.txt -d ./output

# Lint (mirrors CI)
pip install flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Build standalone executable (PyInstaller)
pip install pyinstaller
pyi-makespec tch_cli.py --name tchMaterial-parser
pyinstaller ./tchMaterial-parser.spec
```

There are no test, typecheck, or format commands.

## Gotchas

- **`tchMaterial-parser.spec` is not in the repo.** CI references it in `build-release.yml` but the file does not exist. Generate it with `pyi-makespec tch_cli.py --name tchMaterial-parser` before running `pyinstaller`.
- **Token is stored as plain JSON** at `~/.config/tchMaterial-parser/data.json` despite the README claiming encryption. Do not treat this as secure storage.
- **No version pins in `requirements.txt`** — `requests` and `pypdf` resolve to latest. Be aware when debugging dependency issues.
- **The version string `v3.3.2-cli`** lives in `tch_cli.py:16`. There is also a numeric-only version in `version.txt` for PyInstaller on Windows. Keep both in sync on version bumps.
- **API URLs are hardcoded** throughout `tch_cli.py` (all under `ykt.cbern.com.cn`). If the platform migrates endpoints, these must be updated inline — there is no config abstraction.

## CI

- **Lint**: `python-app.yml` runs flake8 on push/PR to `main` (Python 3.14).
- **Build & Release**: `build-release.yml` builds PyInstaller artifacts (Windows x64, Linux x64, Linux ARM64, macOS ARM64) on release publish or manual `workflow_dispatch`.

#!/usr/bin/env bash
# Prepare the local Python environment before any project Python utility is run.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f "requirements-dev.txt" || ! -f "case-config.yaml" ]]; then
  echo "ERROR: run this script from a clone of the case-file framework." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: Git is required. Install Git and rerun this script." >&2
  exit 1
fi

PYTHON=()
if command -v python3 >/dev/null 2>&1; then
  PYTHON=(python3)
elif command -v python >/dev/null 2>&1; then
  PYTHON=(python)
elif command -v py >/dev/null 2>&1; then
  PYTHON=(py -3)
else
  echo "ERROR: Python 3 is required. Install Python 3 and rerun this script." >&2
  exit 1
fi

echo "Preparing the project virtual environment..."
if [[ ! -x ".venv/bin/python" && ! -x ".venv/Scripts/python.exe" ]]; then
  "${PYTHON[@]}" -m venv .venv
fi

if [[ -x ".venv/bin/python" ]]; then
  VENV_PYTHON=".venv/bin/python"
elif [[ -x ".venv/Scripts/python.exe" ]]; then
  VENV_PYTHON=".venv/Scripts/python.exe"
else
  echo "ERROR: virtual environment creation did not produce a usable Python interpreter." >&2
  exit 1
fi

echo "Installing declared setup dependencies..."
"$VENV_PYTHON" -m pip install -r requirements-dev.txt

echo "Verifying PyYAML is available in the project environment..."
"$VENV_PYTHON" -c 'import yaml; print("PyYAML", yaml.__version__, "ready")'

if command -v git-lfs >/dev/null 2>&1; then
  echo "Enabling Git LFS and fetching any objects tracked by this clone..."
  git lfs install
  git lfs pull
else
  tracked_lfs_files="$(git ls-files | grep -Ei '\.(pdf|docx?|xlsx?|mp4|mp3|wav|m4a|jpe?g|png|tiff?|zip|eml|msg)$' || true)"
  if [[ -n "$tracked_lfs_files" ]]; then
    echo "ERROR: this clone tracks Git LFS file types, but Git LFS is not installed." >&2
    echo "Install Git LFS, then rerun this script before pushing or hashing files." >&2
    exit 1
  fi
  echo "NOTICE: Git LFS is not installed. Install it before adding any binary files covered by .gitattributes."
fi

echo
echo "Setup environment ready."
echo "Use $VENV_PYTHON for all project Python commands."

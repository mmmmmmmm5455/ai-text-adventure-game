#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$PWD"
export PYTHONIOENCODING=UTF-8
exec python -m streamlit run frontend/app.py

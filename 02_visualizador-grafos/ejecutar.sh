#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ -x ../mi_entorno/bin/python ]; then
  PYTHON=../mi_entorno/bin/python
elif [ -x .venv/bin/python ]; then
  PYTHON=.venv/bin/python
else
  PYTHON=python3
fi

"$PYTHON" app.py

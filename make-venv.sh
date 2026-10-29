#!/usr/bin/env bash

set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
python=${PYSIM_VENV_PYTHON:-python3.14}
if [[ ! -x venv/bin/python ]]; then
    "$python" -m venv venv
elif [[ $(venv/bin/python -c 'import sys; print(sys.version_info[:2])') != \
        $("$python" -c 'import sys; print(sys.version_info[:2])') ]]; then
    printf 'Move the existing venv aside before rebuilding with %s.\n' "$python" >&2
    exit 1
fi
venv/bin/python -m pip install -r requirements.txt .
# cmd2 needs GNU readline for interactive editing and tab completion.
venv/bin/python -m pip install gnureadline
venv/bin/python -m pip check
venv/bin/python --version

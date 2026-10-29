#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec "${PYSIM_PYTHON:-$script_dir/venv/bin/python}" "$script_dir/pySim-isim.py" disable "$@"

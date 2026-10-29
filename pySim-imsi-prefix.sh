#!/usr/bin/env bash
# Replace an IMSI prefix using pySim-shell.py.
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: ./pySim-imsi-prefix.sh [-p READER] [--adm1 PIN] [--application usim|sim] [--dry-run] [--once] PREFIX

Read EF.IMSI, authenticate with ADM1, replace the first 5 or 6 digits,
and read back the result. Reader defaults to PC/SC 0; application to USIM.
Wait for a SIM, process it, then wait for removal and the next insertion.
Repeat until Ctrl+C. Use --once to process just one SIM.
ADM1 is requested for each SIM unless a shared PIN is supplied with --adm1.
ADM1 accepts 1-8 ASCII characters or 16 hexadecimal digits.

Examples:
  ./pySim-imsi-prefix.sh 26201 --dry-run
  ./pySim-imsi-prefix.sh 26201
  ./pySim-imsi-prefix.sh -p 1 --application sim 26201

Only the selected EF.IMSI is changed; EF.AD and PLMN/ISIM settings are unchanged.
EOF
}

die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

reader=0
application=usim
adm1=''
dry_run=false
once=false
prefix=''
while (($#)); do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        -p|--pcsc-device|--adm1|--application)
            (($# >= 2)) || die "Missing value for $1"
            case "$1" in
                -p|--pcsc-device) reader=$2 ;;
                --adm1) adm1=$2 ;;
                --application) application=$2 ;;
            esac
            shift 2 ;;
        --dry-run) dry_run=true; shift ;;
        --once) once=true; shift ;;
        -*) die "Unknown option: $1" ;;
        *) [[ -z $prefix ]] || die 'Supply exactly one prefix'; prefix=$1; shift ;;
    esac
done

[[ $prefix =~ ^[0-9]{5,6}$ ]] || die 'Prefix must contain 5 or 6 decimal digits'
[[ $reader =~ ^[0-9]+$ ]] || die 'Reader must be a nonnegative PC/SC reader number'
case "$application" in
    usim) imsi_path=MF/ADF.USIM/EF.IMSI ;;
    sim) imsi_path=MF/DF.GSM/EF.IMSI ;;
    *) die 'Application must be usim or sim' ;;
esac

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python=${PYSIM_PYTHON:-"$script_dir/venv/bin/python"}
if [[ ! -x $python ]]; then
    [[ -z ${PYSIM_PYTHON:-} ]] || die "Python executable not found: $python"
    python=python3
fi

trap 'exit 130' INT
trap 'exit 143' TERM

# Use pySim's existing pyscard dependency only to wait for hardware events.
# No connection or ADM verification is made while waiting.
wait_for_card() {
    "$python" - "$reader" "$1" <<'PY'
import sys
from smartcard.CardRequest import CardRequest
from smartcard.System import readers

try:
    available = readers()
    index = int(sys.argv[1])
    if index >= len(available):
        raise RuntimeError('No PC/SC reader found for number %d' % index)
    request = CardRequest(readers=[available[index]], timeout=None,
                          newcardonly=sys.argv[2] == 'true')
    try:
        request.waitforcard()
    finally:
        request.pcsccardrequest.release()
except KeyboardInterrupt:
    sys.exit(130)
except Exception as error:
    print('Error waiting for SIM: %s' % error, file=sys.stderr)
    sys.exit(1)
PY
}

read_imsi() {
    local json
    [[ -s $1 ]] || return 1
    json=$(tr -d '\r\n' < "$1")
    if [[ $json =~ \"imsi\"[[:space:]]*:[[:space:]]*\"([0-9]{6,15})\" ]]; then
        printf '%s' "${BASH_REMATCH[1]}"
    else
        return 1
    fi
}

process_card() (
# Run each card in a subshell, with fresh output files and a fresh prompted PIN.
# A failure exits only this card's processing and never retries its ADM1.
umask 077
work_dir=$(mktemp -d /tmp/pysim-imsi-prefix.XXXXXXXX) || die 'Could not create temporary directory'
trap 'rm -rf -- "$work_dir"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# pySim-shell can return zero even when individual commands fail. Require a
# valid decoded IMSI as well as a successful process status.
if ! "$python" "$script_dir/pySim-shell.py" -p "$reader" --noprompt \
        -e "select $imsi_path" \
        -e "read_binary_decoded > $work_dir/current.json" \
        > "$work_dir/read.log" 2>&1; then
    cat "$work_dir/read.log" >&2
    die 'Could not read the SIM'
fi
if ! current_imsi=$(read_imsi "$work_dir/current.json"); then
    cat "$work_dir/read.log" >&2
    die "Could not read $imsi_path (use --application sim for a classic SIM)"
fi
(( ${#current_imsi} > ${#prefix} )) || die 'IMSI must be longer than the prefix'
new_imsi="${prefix}${current_imsi:${#prefix}}"
printf 'Current IMSI: %s\nNew IMSI:     %s\n' "$current_imsi" "$new_imsi"

if [[ $current_imsi == "$new_imsi" ]]; then
    printf 'IMSI already has this prefix; no change needed.\n'
    exit 0
fi
if $dry_run; then
    printf 'Dry run: no authentication or write performed.\n'
    exit 0
fi

if [[ -z $adm1 ]]; then
    read -r -s -p 'ADM1: ' adm1 || die 'Could not read ADM1'
    printf '\n'
fi
if [[ $adm1 =~ ^[0-9a-fA-F]{16}$ ]]; then
    adm_args=(-A "$adm1")
else
    [[ -n $adm1 && ${#adm1} -le 8 && $adm1 != *[!\ -\~]* ]] || \
        die 'ADM1 must contain 1-8 printable ASCII characters or 16 hexadecimal digits'
    adm_args=(-a "$adm1")
fi

# Startup ADM authentication gates all -e commands: pySim-shell skips the
# write if verification fails. Do not use verify_adm followed by an unchecked
# write command, because command errors alone do not stop shell execution.
if ! "$python" "$script_dir/pySim-shell.py" -p "$reader" --noprompt \
        "${adm_args[@]}" \
        -e "select $imsi_path" \
        -e "update_binary_decoded '{\"imsi\":\"$new_imsi\"}'" \
        -e "read_binary_decoded > $work_dir/verified.json" \
        > "$work_dir/write.log" 2>&1; then
    die 'ADM1 authentication or IMSI update failed; no retry performed'
fi
# Authentication errors in pySim-shell can include the PIN. Keep its output
# private instead of echoing it on failure.
verified_imsi=$(read_imsi "$work_dir/verified.json") || die 'Could not read back the IMSI after the update'
[[ $verified_imsi == "$new_imsi" ]] || die "Verification failed: read back $verified_imsi"
printf 'Verified IMSI: %s\n' "$verified_imsi"
)

processed=0
failed=0
new_card_only=false
while true; do
    if $new_card_only; then
        printf '\nRemove the current SIM and insert the next one (Ctrl+C to stop).\n'
    else
        printf 'Waiting for a SIM in reader %s (Ctrl+C to stop)...\n' "$reader"
    fi
    wait_for_card "$new_card_only" || exit "$?"
    if process_card; then
        processed=$((processed + 1))
        result=0
    else
        result=$?
        [[ $result != 130 && $result != 143 ]] || exit "$result"
        failed=$((failed + 1))
        printf 'SIM failed; it will not be retried automatically.\n' >&2
    fi
    $once && exit "$result"
    printf 'Processed: %d; failed: %d\n' "$processed" "$failed"
    new_card_only=true
done

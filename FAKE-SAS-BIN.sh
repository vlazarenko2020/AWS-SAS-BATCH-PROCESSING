#!/bin/bash
#
# Fake/local stand-in for the real SAS binary (z_config.sas_bin), so the
# S3_Bucket_processing pipeline can be run end-to-end off the real SAS server.
#
# Emulates just enough of:
#   sas -work <dir> -log <dir_or_file> -print <dir_or_file> -sysin <file.sas> -nodms
# for ClassSASProgram.f_run_sas_program() to behave the same way the real sas
# binary does:
#   - When -log/-print are given a DIRECTORY (not a full file path), real SAS
#     defaults the output filename to <sysin-basename-without-.sas>.log / .lst
#     inside that directory - this script does the same. That's what lets
#     ClassSASProgram find f_file_log_with_path = "<log_dir>/<sas_stem>.log"
#     afterwards.
#   - It writes a SAS-log-shaped file (NOTE lines, the submitted source
#     echoed with line numbers) to that path.
#   - If the .sas source contains the literal marker FORCE_SAS_ERROR, an
#     "ERROR: " line is written to the log - ClassSASProgram greps logs for
#     "ERROR: " to decide SAS-ERROR vs SAS-SUCCESS, so this lets you exercise
#     both e-mail paths on demand without needing real SAS syntax errors.
#   - If -sysin is missing/unreadable, no log file is written at all - this
#     is what makes ClassSASProgram take its SAS-WARNING ("log file was
#     never created") path, same as if the real sas binary crashed early.
#
# NOT a SAS interpreter - it never executes any SAS statement, just echoes
# them into a fake log for pipeline testing.

set -euo pipefail

work_dir=""
log_target=""
print_target=""
sysin_file=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -work)  work_dir="$2";     shift 2 ;;
        -log)   log_target="$2";   shift 2 ;;
        -print) print_target="$2"; shift 2 ;;
        -sysin) sysin_file="$2";   shift 2 ;;
        -nodms) shift ;;
        *)      shift ;;
    esac
done

if [[ -z "${sysin_file}" || ! -f "${sysin_file}" ]]; then
    echo "FAKE-SAS-BIN.sh: -sysin file (${sysin_file}) not found. Not writing a log (emulating a crashed SAS run)." >&2
    exit 1
fi

sysin_basename="$(basename "${sysin_file}")"
sysin_stem="${sysin_basename%.sas}"

resolve_target() {
    local target="$1" ext="$2"
    if [[ -d "${target}" ]]; then
        echo "${target}/${sysin_stem}.${ext}"
    else
        echo "${target}"
    fi
}

log_file="$(resolve_target "${log_target}" 'log')"
print_file="$(resolve_target "${print_target}" 'lst')"

[[ -n "${work_dir}" ]] && mkdir -p "${work_dir}" 2>/dev/null || true

timestamp="$(date '+%d%b%Y:%H:%M:%S' | tr '[:lower:]' '[:upper:]')"

{
    echo "1                                                          The SAS System                            ${timestamp}"
    echo ""
    echo "NOTE: Copyright (c) 2016 by SAS Institute Inc., Cary, NC, USA. [EMULATED by FAKE-SAS-BIN.sh - not real SAS]"
    echo "NOTE: SAS (r) Proprietary Software 9.4 (TS1M6)"
    echo ""
    echo "NOTE: SAS initialization used:"
    echo "      real time           0.01 seconds"
    echo ""

    line_no=1
    while IFS= read -r line; do
        printf '%-4d %s\n' "${line_no}" "${line}"
        line_no=$((line_no + 1))
    done < "${sysin_file}"
    echo ""

    if grep -q 'FORCE_SAS_ERROR' "${sysin_file}"; then
        echo "ERROR: (emulated) FORCE_SAS_ERROR marker found in ${sysin_basename}."
        echo "NOTE: The SAS System stopped processing this step because of errors."
    else
        echo "NOTE: PROCEDURE (emulated) used (Total process time):"
        echo "      real time           0.02 seconds"
    fi

    echo ""
    echo "NOTE: SAS Institute Inc., SAS Campus Drive, Cary, NC USA 27513-2414"
    echo "NOTE: The SAS System used:"
    echo "      real time           0.05 seconds"
} > "${log_file}"

echo "(emulated listing output for ${sysin_basename})" > "${print_file}"

echo "FAKE-SAS-BIN.sh: wrote log (${log_file}) and listing (${print_file})."
exit 0

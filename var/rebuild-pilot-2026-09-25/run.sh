#!/bin/bash
# Pilot rebuild of the ten oracle countries with entries 186 and 189. Resumable: a country listed in
# done.txt is skipped, so running this again after an interruption picks up where it stopped.
cd "/Users/aadarsh/Documents/Visa Research Agent"
R=var/rebuild-pilot-2026-09-25
export R
build() {
  c=$1
  grep -qx "$c" "$R/done.txt" 2>/dev/null && { echo "$c skipped (done)"; return 0; }
  start=$(date -u +%FT%TZ)
  .venv/bin/visa-discover corpus --country "$c" > "$R/$c.log" 2>&1
  code=$?
  echo "$c exit=$code start=$start end=$(date -u +%FT%TZ)" >> "$R/results.txt"
  [ $code -eq 0 ] && echo "$c" >> "$R/done.txt"
}
export -f build
echo "started $(date -u +%FT%TZ)" >> "$R/results.txt"
printf '%s\n' JP GB CA DE NL FR SE SG AE US | xargs -P 2 -I{} bash -c 'build {}'
echo "ALL FINISHED $(date -u +%FT%TZ)" >> "$R/results.txt"

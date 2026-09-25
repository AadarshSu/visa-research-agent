#!/bin/bash
# Rebuild the SharePoint countries' stores after entry 215 (their page text had been stored empty) and
# Korea's after entry 219 (so an India mission page linking visaforkorea-ce.com can be recorded).
# Each country's corpus and text index are copied to var/_backup_before_2026-09-26/ first.
# Resumable: a country listed in done.txt is skipped. Run from the owner's terminal.
cd "/Users/aadarsh/Documents/Visa Research Agent"
R=var/rebuild-2026-09-26
B=var/_backup_before_2026-09-26
mkdir -p "$B/corpus" "$B/pagetext"
export R B
build() {
  c=$1
  grep -qx "$c" "$R/done.txt" 2>/dev/null && { echo "$c skipped (done)"; return 0; }
  [ -e "$B/corpus/$c.json" ] || cp -p "var/corpus/$c.json" "$B/corpus/$c.json"
  [ -e "$B/pagetext/$c.sqlite3" ] || cp -p "var/pagetext/$c.sqlite3" "$B/pagetext/$c.sqlite3"
  start=$(date -u +%FT%TZ)
  .venv/bin/visa-discover corpus --country "$c" > "$R/$c.log" 2>&1
  code=$?
  echo "$c exit=$code start=$start end=$(date -u +%FT%TZ)" | tee -a "$R/results.txt"
  [ $code -eq 0 ] && echo "$c" >> "$R/done.txt"
}
export -f build
echo "started $(date -u +%FT%TZ)" >> "$R/results.txt"
.venv/bin/visa-discover eu-store > "$R/eu-store.log" 2>&1
echo "eu-store exit=$? $(date -u +%FT%TZ)" | tee -a "$R/results.txt"
printf '%s\n' ES KR PT CA SA HR AT | xargs -P 2 -I{} bash -c 'build {}'
echo "ALL FINISHED $(date -u +%FT%TZ)" | tee -a "$R/results.txt"

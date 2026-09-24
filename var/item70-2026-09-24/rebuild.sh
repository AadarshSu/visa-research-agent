#!/bin/bash
# TODO item 70, step 5: rebuild only the stores the uploads-year fix changes, in batches.
#
# The fix changes what a build records wherever an authority files documents under a dated
# `uploads/<year>/` folder. The stores holding such entries are these 14 (every one dated 2025 or
# later, because the veto dropped the rest):
#   batch 1: MT                      — the one item-70 corridor that needs it
#   later:   AE CZ EE GR ID IE IT MY PH RO TH US ZA
#
# usage, from the repository root in the owner's terminal: rebuild.sh MT [CC ...]
# Resumable: a country in done.txt is skipped. Each country's corpus and text index are copied to
# var/_backup_before_item70_2026-09-24/ before its build, and a copy that already exists is kept.
cd "/Users/aadarsh/Documents/Visa Research Agent"
R="$(dirname "$0")/rebuild"
B=var/_backup_before_item70_2026-09-24
mkdir -p "$R" "$B/corpus" "$B/pagetext"
for c in "$@"; do
  grep -qx "$c" "$R/done.txt" 2>/dev/null && { echo "$c skipped (done)"; continue; }
  [ -e "$B/corpus/$c.json" ] || cp -p "var/corpus/$c.json" "$B/corpus/$c.json"
  [ -e "$B/pagetext/$c.sqlite3" ] || cp -p "var/pagetext/$c.sqlite3" "$B/pagetext/$c.sqlite3"
  start=$(date -u +%FT%TZ)
  .venv/bin/visa-discover corpus --country "$c" > "$R/$c.log" 2>&1
  code=$?
  echo "$c exit=$code start=$start end=$(date -u +%FT%TZ)" | tee -a "$R/results.txt"
  [ $code -eq 0 ] && echo "$c" >> "$R/done.txt"
done

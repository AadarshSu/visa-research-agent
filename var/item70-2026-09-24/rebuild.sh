#!/bin/bash
# Rebuild country stores, backing each up first. Written for TODO item 70's step 5 (Malta, entry 198)
# and used for the full rebuild of the 44 not yet rebuilt — see PROJECT_HANDOFF's *Next session*.
# Run `visa-discover eu-store` first. Brazil and Uruguay have no store to back up; the copy for them
# fails harmlessly and the build creates one.
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

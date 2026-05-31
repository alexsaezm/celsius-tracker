#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
changes="$(./track.py)"
[[ "$(jq '[.added, .removed] | map(length) | add' <<<"$changes")" -eq 0 ]] && exit 0
body="$(jq -r --arg date "$(date +%F)" '
  [$date]
  + (if (.added | length) > 0 then ["Added:"] + (.added | map("- " + .)) else [] end)
  + (if (.removed | length) > 0 then ["Removed:"] + (.removed | map("- " + .)) else [] end)
  | join("\n")
' <<<"$changes")"
apprise -c "$HOME/.config/apprise/apprise.yml" -g celsius -t "Celsius 232 author changes" -b "$body"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
authors="$(./track.py)"
[[ "$(jq length <<<"$authors")" -eq 0 ]] && exit 0
body="$(jq -r --arg date "$(date +%F)" '[$date] + map("- " + .) | join("\n")' <<<"$authors")"
apprise -c "$HOME/.config/apprise/apprise.yml" -g celsius -t "New Celsius 232 authors" -b "$body"

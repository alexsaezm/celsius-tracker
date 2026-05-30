# Celsius Author Tracker

Small tracker for `https://celsius232.es/autores-celsius/`.

This exists because the Celsius RSS feed appears to be empty, so this gives a
simple way to detect which authors are new.

`track.py` fetches the page, compares the current author list with `authors.json`,
updates `authors.json`, and prints new authors as a JSON array.

`notify.sh` runs `track.py` and sends an Apprise notification only when new
authors exist. The notification is sent to the `celsius` Apprise tag.

## Requirements

- Python 3
- `jq`
- `apprise`
- Apprise config at `~/.config/apprise/apprise.yml`
- A configured Apprise target tagged with `celsius`

## Apprise Config

Create or edit `~/.config/apprise/apprise.yml`.

Telegram example:

```yaml
version: 1
urls:
  - tgram://BOT_TOKEN/CHAT_ID:
      - tag: celsius
```

System notification example:

```yaml
version: 1
urls:
  - gnome://:
      - tag: celsius
```

You can keep multiple targets in the same file:

```yaml
version: 1
urls:
  - tgram://BOT_TOKEN/CHAT_ID:
      - tag: celsius
  - gnome://:
      - tag: celsius
```

Check that Apprise can see the `celsius` target:

```bash
apprise -c ~/.config/apprise/apprise.yml -g celsius --dry-run -t test -b test
```

## Manual Run

```bash
./track.py
./notify.sh
```

## Hourly Systemd User Timer

Create user systemd units from the project directory:

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/celsius-authors.service <<EOF
[Unit]
Description=Notify about new Celsius 232 authors

[Service]
Type=oneshot
WorkingDirectory=$(pwd)
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=$(pwd)/notify.sh
EOF

cat > ~/.config/systemd/user/celsius-authors.timer <<EOF
[Unit]
Description=Run Celsius 232 author notifications hourly

[Timer]
OnCalendar=hourly
Persistent=true
Unit=celsius-authors.service

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now celsius-authors.timer
```

Check the timer:

```bash
systemctl --user status celsius-authors.timer
systemctl --user list-timers celsius-authors.timer
```

Run once manually through systemd:

```bash
systemctl --user start celsius-authors.service
```

View logs:

```bash
journalctl --user -u celsius-authors.service
```

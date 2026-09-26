# GNOME Calendar Integration

An Omarchy bar widget showing the next event in the local GNOME Calendar. Left click opens GNOME Calendar; middle click refreshes the widget. It also includes a Codex skill and scripts to create, list, and delete events through Evolution Data Server.

## Requirements

- Linux desktop session with GNOME Calendar and Evolution Data Server
- Python 3 with PyGObject and the `ECal`, `EDataServer`, and `ICalGLib` GI typelibs
- Access to the user's session D-Bus
- Omarchy 4 for the bar widget

## Set up a new Omarchy device

Install the same integration used on the original device:

```bash
sudo pacman -S --needed gnome-calendar evolution-data-server python-gobject
gnome-calendar
omarchy plugin add https://github.com/Dornkimik/gnome-calendar-integration.git --enable
omarchy bar move dornkimik.gnome-calendar --section right --index 1
codex plugin marketplace add Dornkimik/gnome-calendar-integration
codex plugin add gnome-calendar-local@gnome-calendar-integration
```

Open a new Codex chat after installing the plugin. The Omarchy widget and the Codex plugin are separate installations. The Omarchy command places the widget immediately after the system tray, matching the original device. The included marketplace entry installs the entire repository as a Codex plugin, including all three Python scripts.

The widget reads the local Evolution Data Server calendar with UID `system-calendar` (usually **Personal**). Create or enable that calendar in GNOME Calendar and arrange for your appointments to appear there on the new device. This repository does not contain or transfer personal appointments, account credentials, or calendar data.

The widget needs the desktop user's session D-Bus. Test the local calendar reader with `/usr/bin/python scripts/next_event.py` from a clone of this repository if it says the calendar is unavailable. The Codex creation script defaults to `Europe/Berlin`; pass `--timezone` for another time zone.

## Omarchy widget

```bash
omarchy plugin add https://github.com/Dornkimik/gnome-calendar-integration.git --enable
```

The widget reads the `system-calendar` calendar every minute and displays the next current or future event. It runs `/usr/bin/python scripts/next_event.py` locally and does not send calendar data to a network service. Disable or remove it with `omarchy plugin disable dornkimik.gnome-calendar` or `omarchy plugin remove dornkimik.gnome-calendar`.

## Codex plugin and scripts

Install this repository as a Codex plugin, or run the scripts directly:

```bash
/usr/bin/python scripts/create_event.py --start 2026-09-28T15:00 --end 2026-09-28T16:00 --title Termin
/usr/bin/python scripts/manage_events.py list
/usr/bin/python scripts/manage_events.py delete --uid '<event-uid>' --expected-title 'Termin'
```

The default calendar UID is `system-calendar`. The create script uses `Europe/Berlin` by default; pass `--timezone` to choose another time zone. `create_event.py` requires both start and end times and reports `created` only after verifying the saved event. Repeating the same creation request reports `already_exists`.

The delete command checks the event title and refuses recurring events. List events first to find the exact UID.

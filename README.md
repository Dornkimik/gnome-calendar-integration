# GNOME Calendar (local) Codex plugin

Create, list, and delete events in a local GNOME Calendar through Evolution Data Server. The plugin includes a Codex skill and two Python scripts.

## Requirements

- Linux desktop session with GNOME Calendar and Evolution Data Server
- Python 3 with PyGObject and the `ECal`, `EDataServer`, and `ICalGLib` GI typelibs
- Access to the user's session D-Bus

## Usage

Install the plugin from this repository in Codex, or run the scripts directly:

```bash
/usr/bin/python scripts/create_event.py --start 2026-09-28T15:00 --end 2026-09-28T16:00 --title Termin
/usr/bin/python scripts/manage_events.py list
/usr/bin/python scripts/manage_events.py delete --uid '<event-uid>' --expected-title 'Termin'
```

The default calendar UID is `system-calendar`. The create script uses `Europe/Berlin` by default; pass `--timezone` to choose another time zone. `create_event.py` requires both start and end times and reports `created` only after verifying the saved event. Repeating the same creation request reports `already_exists`.

The delete command checks the event title and refuses recurring events. List events first to find the exact UID.

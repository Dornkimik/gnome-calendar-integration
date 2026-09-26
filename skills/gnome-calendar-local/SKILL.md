---
name: gnome-calendar-local
description: Create, list, or delete personal appointments in the user's local GNOME Calendar on this Linux machine. Use when the user asks to add, inspect, or remove local calendar events, unless they explicitly choose another calendar.
---

# GNOME Calendar Integration

Use the bundled `scripts/create_event.py` to create and verify appointments through Evolution Data Server. Resolve the script path relative to this `SKILL.md`: `../../scripts/create_event.py`. The default calendar UID is `system-calendar` (Personal), and the default time zone is `Europe/Berlin`; pass `--timezone` for another time zone.

Resolve relative dates using the user's current local date. Supply ISO local start and end times. Use the user's title when given; otherwise the script defaults to `Termin`. Example:

```bash
/usr/bin/python /path/to/gnome-calendar-local/scripts/create_event.py --start 2026-09-28T15:00 --end 2026-09-28T16:00 --title Termin
```

The calendar uses the session D-Bus. If sandbox execution reports `Operation not permitted` while connecting, retry the same command with `sandbox_permissions: "require_escalated"`; the user's request to create the appointment authorizes the calendar write. Report success only when the script prints `created` or `already_exists`. Do not create a duplicate when retrying after an unclear result.

## List and delete appointments

Use `scripts/manage_events.py` through Evolution Data Server. Resolve its path relative to this `SKILL.md`: `../../scripts/manage_events.py`. The default calendar is `system-calendar` (Personal). List events to identify their exact UID, title, and time:

```bash
/usr/bin/python /path/to/gnome-calendar-local/scripts/manage_events.py list
```

The script prints iCalendar times; a trailing `Z` means UTC. Convert these to the user's local time zone when presenting them. To delete one identified event, pass both its UID and its exact current title:

```bash
/usr/bin/python /path/to/gnome-calendar-local/scripts/manage_events.py delete --uid '<uid-from-list>' --expected-title '<exact-title-from-list>'
```

For multiple events, inspect the list and call `delete` separately for each selected UID. If the user's description could include legitimate events, ask which specific ones they mean before deleting. The script refuses recurring events for separate review. Report a deletion only when the command prints `"status": "deleted"`. If the session D-Bus is blocked by the sandbox, retry with `sandbox_permissions: "require_escalated"`; do not work around a rejection from automatic approval review.

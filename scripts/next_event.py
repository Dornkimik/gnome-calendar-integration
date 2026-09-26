#!/usr/bin/python
"""Print the next event in the local GNOME Calendar as JSON."""

import json
import sys
from datetime import datetime, timezone

import gi

gi.require_version('ECal', '2.0')
gi.require_version('EDataServer', '1.2')
gi.require_version('ICalGLib', '4.0')
from gi.repository import ECal, EDataServer


def event_time(value):
    """Parse UTC or floating iCalendar times returned by Evolution."""
    raw = value.as_ical_string()
    if len(raw) == 8:
        return datetime.strptime(raw, '%Y%m%d').astimezone()
    if raw.endswith('Z'):
        return datetime.strptime(raw, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc).astimezone()
    return datetime.strptime(raw, '%Y%m%dT%H%M%S').astimezone()


def main():
    registry = EDataServer.SourceRegistry.new_sync(None)
    source = registry.ref_source('system-calendar')
    if source is None or not source.get_enabled():
        raise RuntimeError('Personal calendar is unavailable')
    client = ECal.Client.connect_sync(source, ECal.ClientSourceType.EVENTS, 10, None)
    found, components = client.get_object_list_sync('#t', None)
    if not found:
        raise RuntimeError('Could not list calendar events')

    now = datetime.now().astimezone()
    upcoming = []
    for event in components:
        start_value = event.get_dtstart()
        if start_value is None:
            continue
        try:
            start = event_time(start_value)
            end_value = event.get_dtend()
            end = event_time(end_value) if end_value else start
        except (ValueError, TypeError):
            continue
        if end >= now:
            upcoming.append((start, event.get_summary() or '(Ohne Titel)'))

    if not upcoming:
        print(json.dumps({'status': 'empty'}))
        return
    start, title = min(upcoming, key=lambda item: item[0])
    print(json.dumps({'status': 'ok', 'title': title, 'start': start.isoformat()}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}), file=sys.stderr)
        sys.exit(1)

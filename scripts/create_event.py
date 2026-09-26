#!/usr/bin/python
"""Create and verify an event in the local GNOME Calendar (Evolution Data Server)."""
import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import gi

gi.require_version('ECal', '2.0')
gi.require_version('EDataServer', '1.2')
gi.require_version('ICalGLib', '4.0')
from gi.repository import ECal, EDataServer, ICalGLib


def local_datetime(value, zone):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=zone)
        if parsed.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None) != parsed.replace(tzinfo=None):
            raise ValueError(f'Invalid local time: {value}')
    return parsed.astimezone(zone)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--title', default='Termin')
    parser.add_argument('--start', required=True, help='ISO local date/time, e.g. 2026-09-28T15:00')
    parser.add_argument('--end', required=True, help='ISO local date/time, e.g. 2026-09-28T16:00')
    parser.add_argument('--timezone', default='Europe/Berlin')
    parser.add_argument('--calendar-uid', default='system-calendar')
    args = parser.parse_args()

    zone = ZoneInfo(args.timezone)
    start = local_datetime(args.start, zone)
    end = local_datetime(args.end, zone)
    if end <= start:
        parser.error('end must be after start')
    if any(c in args.title for c in '\r\n'):
        parser.error('title must be one line')

    registry = EDataServer.SourceRegistry.new_sync(None)
    source = registry.ref_source(args.calendar_uid)
    if source is None or not source.get_enabled():
        raise RuntimeError(f'Calendar is unavailable: {args.calendar_uid}')
    client = ECal.Client.connect_sync(source, ECal.ClientSourceType.EVENTS, 10, None)
    if client is None:
        raise RuntimeError('Could not connect to GNOME Calendar')

    stamp = lambda value: value.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    uid = str(uuid.uuid5(uuid.NAMESPACE_URL, '|'.join([args.calendar_uid, args.title, start.isoformat(), end.isoformat()]))) + '@codex-local'
    try:
        found, existing = client.get_object_sync(uid, None, None)
        if found:
            print(json.dumps({'status': 'already_exists', 'uid': uid, 'title': args.title, 'start': start.isoformat(), 'end': end.isoformat()}))
            return
    except Exception:
        pass

    ics = '\r\n'.join([
        'BEGIN:VEVENT',
        'UID:' + uid,
        'DTSTAMP:' + stamp(datetime.now(timezone.utc)),
        'DTSTART:' + stamp(start),
        'DTEND:' + stamp(end),
        'SUMMARY:' + args.title.replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;'),
        'END:VEVENT',
        '',
    ])
    component = ICalGLib.Component.new_from_string(ics)
    created, saved_uid = client.create_object_sync(component, ECal.OperationFlags.NONE, None)
    if not created:
        raise RuntimeError('GNOME Calendar did not create the event')
    verified, saved = client.get_object_sync(saved_uid, None, None)
    if not verified or saved is None:
        raise RuntimeError('Event was created but could not be verified')
    print(json.dumps({'status': 'created', 'uid': saved_uid, 'title': args.title, 'start': start.isoformat(), 'end': end.isoformat()}))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)

#!/usr/bin/python
"""List or delete appointments in a local GNOME Calendar via Evolution Data Server."""
import argparse
import json
import sys

import gi

gi.require_version('ECal', '2.0')
gi.require_version('EDataServer', '1.2')
gi.require_version('ICalGLib', '4.0')
from gi.repository import ECal, EDataServer, ICalGLib


def event_data(component):
    start = component.get_dtstart()
    end = component.get_dtend()
    return {
        'uid': component.get_uid(),
        'title': component.get_summary() or '',
        'start': start.as_ical_string() if start else None,
        'end': end.as_ical_string() if end else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--calendar-uid', default='system-calendar')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list', help='List events with IDs, titles and times')
    delete = commands.add_parser('delete', help='Delete exactly one event')
    delete.add_argument('--uid', required=True)
    delete.add_argument('--expected-title', required=True)
    args = parser.parse_args()

    registry = EDataServer.SourceRegistry.new_sync(None)
    source = registry.ref_source(args.calendar_uid)
    if source is None or not source.get_enabled():
        raise RuntimeError(f'Calendar is unavailable: {args.calendar_uid}')
    client = ECal.Client.connect_sync(source, ECal.ClientSourceType.EVENTS, 10, None)
    if client is None:
        raise RuntimeError('Could not connect to GNOME Calendar')

    if args.command == 'list':
        found, components = client.get_object_list_sync('#t', None)
        if not found:
            raise RuntimeError('Could not list calendar events')
        print(json.dumps({'status': 'listed', 'events': [event_data(c) for c in components]}, ensure_ascii=False))
        return

    found, component = client.get_object_sync(args.uid, None, None)
    if not found or component is None:
        raise RuntimeError(f'Event not found: {args.uid}')
    event = event_data(component)
    if event['title'] != args.expected_title:
        raise RuntimeError(f'Title mismatch: expected {args.expected_title!r}, found {event["title"]!r}')
    for kind in (ICalGLib.PropertyKind.RRULE_PROPERTY,
                 ICalGLib.PropertyKind.RDATE_PROPERTY,
                 ICalGLib.PropertyKind.RECURRENCEID_PROPERTY):
        if component.get_first_property(kind) is not None:
            raise RuntimeError('Recurring events require separate review')
    if not client.remove_object_sync(args.uid, None, ECal.ObjModType.THIS, ECal.OperationFlags.NONE, None):
        raise RuntimeError(f'Could not delete event: {args.uid}')
    print(json.dumps({'status': 'deleted', 'event': event}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)

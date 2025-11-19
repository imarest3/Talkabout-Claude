"""
Service for generating iCalendar (.ics) files compatible with Google Calendar.
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
import pytz


class ICalendarService:
    """
    Service to generate iCalendar format files for email invitations.
    Compatible with Google Calendar, Outlook, and other calendar applications.
    """

    @staticmethod
    def generate_ics(
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        location: str = "",
        organizer_email: str = "",
        organizer_name: str = "",
        attendee_email: str = "",
        attendee_name: str = "",
        uid: Optional[str] = None,
        url: Optional[str] = None,
        timezone: str = "UTC"
    ) -> str:
        """
        Generate an iCalendar (.ics) file content.

        Args:
            summary: Event title
            description: Event description
            start_time: Start datetime (timezone-aware)
            end_time: End datetime (timezone-aware)
            location: Event location or meeting URL
            organizer_email: Organizer's email
            organizer_name: Organizer's name
            attendee_email: Attendee's email
            attendee_name: Attendee's name
            uid: Unique identifier for the event
            url: URL for the event (meeting link)
            timezone: Timezone name (e.g., 'Europe/Madrid')

        Returns:
            String containing the iCalendar file content
        """
        # Generate unique ID if not provided
        if not uid:
            uid = str(uuid.uuid4())

        # Ensure times are in UTC for iCalendar
        if start_time.tzinfo is None:
            tz = pytz.timezone(timezone)
            start_time = tz.localize(start_time)

        if end_time.tzinfo is None:
            tz = pytz.timezone(timezone)
            end_time = tz.localize(end_time)

        # Convert to UTC
        start_utc = start_time.astimezone(pytz.UTC)
        end_utc = end_time.astimezone(pytz.UTC)

        # Format datetimes for iCalendar (YYYYMMDDTHHmmssZ)
        dtstart = start_utc.strftime('%Y%m%dT%H%M%SZ')
        dtend = end_utc.strftime('%Y%m%dT%H%M%SZ')
        dtstamp = datetime.now(pytz.UTC).strftime('%Y%m%dT%H%M%SZ')

        # Build iCalendar content
        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Talkabout//Event Invitation//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:REQUEST',
            'BEGIN:VEVENT',
            f'UID:{uid}',
            f'DTSTAMP:{dtstamp}',
            f'DTSTART:{dtstart}',
            f'DTEND:{dtend}',
            f'SUMMARY:{ICalendarService._escape_text(summary)}',
        ]

        # Add description if provided
        if description:
            lines.append(f'DESCRIPTION:{ICalendarService._escape_text(description)}')

        # Add location if provided
        if location:
            lines.append(f'LOCATION:{ICalendarService._escape_text(location)}')

        # Add URL if provided
        if url:
            lines.append(f'URL:{url}')

        # Add organizer if provided
        if organizer_email:
            org_line = f'ORGANIZER;CN={ICalendarService._escape_text(organizer_name)}:mailto:{organizer_email}'
            lines.append(org_line)

        # Add attendee if provided
        if attendee_email:
            att_line = f'ATTENDEE;CN={ICalendarService._escape_text(attendee_name)};RSVP=TRUE;'
            att_line += f'PARTSTAT=NEEDS-ACTION;ROLE=REQ-PARTICIPANT:mailto:{attendee_email}'
            lines.append(att_line)

        # Add alarms/reminders
        # Reminder 24 hours before
        lines.extend([
            'BEGIN:VALARM',
            'TRIGGER:-PT24H',
            'ACTION:DISPLAY',
            'DESCRIPTION:Reminder: Event tomorrow',
            'END:VALARM',
        ])

        # Reminder 1 hour before
        lines.extend([
            'BEGIN:VALARM',
            'TRIGGER:-PT1H',
            'ACTION:DISPLAY',
            'DESCRIPTION:Reminder: Event in 1 hour',
            'END:VALARM',
        ])

        # Close event and calendar
        lines.extend([
            'SEQUENCE:0',
            'STATUS:CONFIRMED',
            'TRANSP:OPAQUE',
            'END:VEVENT',
            'END:VCALENDAR'
        ])

        # Join lines with CRLF (required by RFC 5545)
        ics_content = '\r\n'.join(lines)

        return ics_content

    @staticmethod
    def generate_cancellation_ics(
        summary: str,
        start_time: datetime,
        end_time: datetime,
        uid: str,
        organizer_email: str = "",
        organizer_name: str = "",
        attendee_email: str = "",
        timezone: str = "UTC"
    ) -> str:
        """
        Generate an iCalendar cancellation.

        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            uid: Unique identifier for the event (must match original)
            organizer_email: Organizer's email
            organizer_name: Organizer's name
            attendee_email: Attendee's email
            timezone: Timezone name

        Returns:
            String containing the cancellation iCalendar content
        """
        # Ensure times are in UTC
        if start_time.tzinfo is None:
            tz = pytz.timezone(timezone)
            start_time = tz.localize(start_time)

        if end_time.tzinfo is None:
            tz = pytz.timezone(timezone)
            end_time = tz.localize(end_time)

        start_utc = start_time.astimezone(pytz.UTC)
        end_utc = end_time.astimezone(pytz.UTC)

        dtstart = start_utc.strftime('%Y%m%dT%H%M%SZ')
        dtend = end_utc.strftime('%Y%m%dT%H%M%SZ')
        dtstamp = datetime.now(pytz.UTC).strftime('%Y%m%dT%H%M%SZ')

        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Talkabout//Event Cancellation//EN',
            'METHOD:CANCEL',
            'BEGIN:VEVENT',
            f'UID:{uid}',
            f'DTSTAMP:{dtstamp}',
            f'DTSTART:{dtstart}',
            f'DTEND:{dtend}',
            f'SUMMARY:CANCELLED: {ICalendarService._escape_text(summary)}',
            'STATUS:CANCELLED',
        ]

        if organizer_email:
            lines.append(f'ORGANIZER;CN={organizer_name}:mailto:{organizer_email}')

        if attendee_email:
            lines.append(f'ATTENDEE:mailto:{attendee_email}')

        lines.extend([
            'SEQUENCE:1',
            'END:VEVENT',
            'END:VCALENDAR'
        ])

        return '\r\n'.join(lines)

    @staticmethod
    def _escape_text(text: str) -> str:
        """
        Escape special characters for iCalendar format.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        if not text:
            return ""

        # Replace special characters
        text = text.replace('\\', '\\\\')  # Backslash
        text = text.replace(';', '\\;')    # Semicolon
        text = text.replace(',', '\\,')    # Comma
        text = text.replace('\n', '\\n')   # Newline
        text = text.replace('\r', '')      # Remove carriage return

        return text

    @staticmethod
    def _fold_line(line: str, max_length: int = 75) -> str:
        """
        Fold long lines according to RFC 5545 (max 75 octets per line).

        Args:
            line: Line to fold
            max_length: Maximum line length

        Returns:
            Folded line
        """
        if len(line) <= max_length:
            return line

        folded = []
        while len(line) > max_length:
            folded.append(line[:max_length])
            line = ' ' + line[max_length:]  # Continuation lines start with space

        folded.append(line)
        return '\r\n'.join(folded)

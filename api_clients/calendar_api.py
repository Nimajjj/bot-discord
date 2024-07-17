import os
from typing import Generator
from icalendar import Calendar
from datetime import datetime, timedelta
from typing import Dict, List, Generator


def parse_ics_files(directory: str) -> Dict[datetime, List[str]]:
    availability: Dict[datetime, List[str]] = {}

    # for each file in CALENDAR_DIR
    for filename in os.listdir(directory):
        if not filename.endswith('.ics'):
            continue

        # open if .ics file
        with open(os.path.join(directory, filename), 'r') as f:
            calendar = Calendar.from_ical(f.read())

            # for each every events
            for component in calendar.walk():
                if component.name != "VEVENT":
                    continue

                # get date range
                start = component.get('dtstart').dt
                end = component.get('dtend').dt

                if isinstance(start, datetime) and isinstance(end, datetime):
                    for single_date in daterange(start, end):
                        if single_date not in availability:
                            availability[single_date] = []
                        availability[single_date].append(filename[:-4])
    return availability


def daterange(start_date: datetime, end_date: datetime) -> Generator[datetime, None, None]:
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

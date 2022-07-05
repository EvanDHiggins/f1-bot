from f1bot import command as cmd
from f1bot.mysql import ergast
from f1bot.data.schedule import Row as ScheduleRow

import pandas
import pytz
import attrs

import argparse
import datetime as dt


class Upcoming(cmd.Command):

    @classmethod
    def manifest(cls) -> cmd.Manifest:
        return cmd.Manifest(
            name="upcoming",
            description="Show the results for a session.",
        )

    def run(self, _args: argparse.Namespace) -> cmd.CommandValue:
        # The schedule is ordered by date
        schedule = ergast.get_schedule_as_structured(dt.date.today().year)

        # The first race we find that hasn't happened yet must be the next one.
        for event in schedule.rows:
            start_time = event.race
            has_happened = start_time < dt.datetime.now()
            if not has_happened:
                return format_event(event)

        raise cmd.CommandError(
            "Couldn't find an event that hasn't happened yet.")


def format_event(event: ScheduleRow) -> cmd.CommandValue:
    header = f"Round {event.round_num}: {event.race_name} -- {event.circuit}"

    body_columns = [
        "Event", "Date", "Time (PT)", "Time (MT)", "Time (CT)", "Time (ET)"]

    def fmt_date_row(event_time: dt.datetime) -> list[str]:
        dti = get_event_times(event_time)
        return [dti.date, dti.pt, dti.mt, dti.ct, dti.et]

    rows = [
        ["Race"] + fmt_date_row(event.race),
        ["Qualifying"] + fmt_date_row(event.qualifying),
        ["Sprint"] + fmt_date_row(event.sprint),
        ["FP3"] + fmt_date_row(event.fp3),
        ["FP2"] + fmt_date_row(event.fp2),
        ["FP1"] + fmt_date_row(event.fp1),
    ]

    body = pandas.DataFrame(data=rows, columns=body_columns)

    return [header, body]

@attrs.define()
class DateTimeInfo:
    date: str
    pt: str
    mt: str
    ct: str
    et: str

    @classmethod
    def none(cls) -> 'DateTimeInfo':
        return DateTimeInfo(date="N/A", pt="N/A", mt="N/A", ct="N/A", et="N/A")

def get_event_times(event_time: dt.datetime) -> DateTimeInfo:
    """Returns formatted timezone dates and times for the specified datetime."""

    if event_time is None or event_time is None:
        return DateTimeInfo.none()

    utc = event_time.replace(tzinfo=dt.timezone.utc)
    pt = utc.astimezone(tz=pytz.timezone("US/Pacific"))
    mt = utc.astimezone(tz=pytz.timezone("US/Mountain"))
    ct = utc.astimezone(tz=pytz.timezone("US/Central"))
    et = utc.astimezone(tz=pytz.timezone("US/Eastern"))

    time_format = "%-I:%M %p" # like "1:42 AM"

    return DateTimeInfo(
        date=pt.strftime("%b %-d"),
        pt=pt.strftime(time_format),
        mt=mt.strftime(time_format),
        ct=ct.strftime(time_format),
        et=et.strftime(time_format))

def build_datetime(date: dt.date, time: dt.timedelta) -> dt.datetime:
    return dt.datetime(year=date.year, month=date.month, day=date.day) + time

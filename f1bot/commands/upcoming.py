from f1bot import command as cmd
from f1bot.mysql import ergast

import pandas
import pytz

import argparse
import datetime as dt

from typing import Tuple

def format_event(event: pandas.Series) -> cmd.CommandValue:
    header = f"Round {event['round']}: {event['race_name']} -- {event['circuit_name']}"


    body_columns = [
        "Event", "Date", "Time (PT)", "Time (MT)", "Time (CT)", "Time (ET)"]

    def fmt_date(date: str, time: str) -> list[str]:
        return list(get_event_times(event[date], event[time]))

    rows = [
        ["Race"] + fmt_date("race_date", "race_time"),
        ["Qualifying"] + fmt_date("quali_date", "quali_time"),
        ["FP3"] + fmt_date("fp3_date", "fp3_time"),
        ["FP2"] + fmt_date("fp2_date", "fp2_time"),
        ["FP1"] + fmt_date("fp1_date", "fp1_time"),
    ]

    body = pandas.DataFrame(data=rows, columns=body_columns)

    return [header, body]

def get_event_times(
    date: dt.date, delta: dt.timedelta,
) -> Tuple[str, str, str, str, str]:

    utc = build_datetime(date, delta).replace(tzinfo=dt.timezone.utc)
    pt = utc.astimezone(tz=pytz.timezone("US/Pacific"))
    mt = utc.astimezone(tz=pytz.timezone("US/Mountain"))
    ct = utc.astimezone(tz=pytz.timezone("US/Central"))
    et = utc.astimezone(tz=pytz.timezone("US/Eastern"))

    time_format = "%-I:%M %p" # like "1:42 AM"

    return (
        pt.strftime("%b %-d"),
        pt.strftime(time_format),
        mt.strftime(time_format),
        ct.strftime(time_format),
        et.strftime(time_format))

def build_datetime(date: dt.date, time: dt.timedelta) -> dt.datetime:
    return dt.datetime(year=date.year, month=date.month, day=date.day) + time

class Upcoming(cmd.Command):

    @classmethod
    def manifest(cls) -> cmd.Manifest:
        return cmd.Manifest(
            name="upcoming",
            description="Show the results for a session.",
        )

    @classmethod
    def init_parser(cls, _parser: argparse.ArgumentParser):
        pass

    def run(self, _args: argparse.Namespace) -> cmd.CommandValue:
        # The schedule is ordered by date
        schedule = ergast.get_schedule(dt.date.today().year)

        # The first race we find that hasn't happened yet must be the next one.
        for _, event in schedule.iterrows():
            race_date: dt.date = event["race_date"]
            time: dt.timedelta = event["race_time"].to_pytimedelta()
            start_time = build_datetime(race_date, time)
            has_happened = start_time < dt.datetime.now()
            if not has_happened:
                return format_event(event)

        raise cmd.CommandError(
            "Couldn't find an event that hasn't happened yet.")

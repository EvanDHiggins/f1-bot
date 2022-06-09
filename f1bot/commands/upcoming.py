from f1bot import command as cmd
from f1bot.mysql import ergast

import f1bot
import pandas

import argparse
import datetime as dt

PARSER = f1bot.add_command_parser(
        'upcoming', description="Show the results for a session.")

def format_event(event: pandas.Series) -> cmd.CommandValue:
    header_columns = ["Name", "Round", "Circuit", "Location"]
    header = pandas.DataFrame(
        columns=header_columns,
        data=[[event["race_name"], event["round"], event["circuit_name"], event["location"]]])


    body_columns = ["Name", "Date", "Time (PT)", "Time (MT)", "Time (CT)", "Time (ET)"]
    rows = []
    rows.append(["Qualifying", event["quali_date"]] + get_times(event["quali_time"]))
    rows.append(["FP1", event["fp1_date"]] + get_times(event["fp1_time"]))
    rows.append(["FP2", event["fp2_date"]] + get_times(event["fp2_time"]))
    rows.append(["FP3", event["fp3_date"]] + get_times(event["fp3_time"]))

    body = pandas.DataFrame(data=rows, columns=body_columns)

    return [header, body]

def get_times(delta: dt.timedelta) -> list[str]:
    # TODO: Return the four values for timezones when delta is a time in UTC.
    return ["1", "2", "3", "4"]

def build_datetime(date: dt.date, time: dt.timedelta) -> dt.datetime:
    return dt.datetime(year=date.year, month=date.month, day=date.day) + time

class Upcoming:
    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        schedule = ergast.get_schedule(dt.date.today().year)
        for _, event in schedule.iterrows():
            race_date: dt.date = event["race_date"]
            time: dt.timedelta = event["race_time"].to_pytimedelta()
            start_time = build_datetime(race_date, time)
            has_happened = start_time < dt.datetime.now()
            if not has_happened:
                return format_event(event)


        # datetime.strptime()
        # print(schedule)
        return ""

UpcomingCommand = cmd.Command(name='upcoming', get=Upcoming)

from f1bot import command as cmd
from f1bot.lib import parsers
from f1bot.mysql import ergast

import f1bot

import argparse
import datetime as dt

PARSER = f1bot.add_command_parser(
        'upcoming', description="Show the results for a session.")

class Upcoming:
    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        schedule = ergast.get_schedule(dt.date.today().year)
        for _, event in schedule.iterrows():
            race_date: dt.date = event["Date"]
            time: dt.timedelta = event["Time"].to_pytimedelta()
            start_time = dt.datetime(year=race_date.year, month=race_date.month, day=race_date.day) + time
            print(start_time.strftime("%Y-%m-%d  %H:%M"))


        # datetime.strptime()
        # print(schedule)
        return ""

UpcomingCommand = cmd.Command(name='upcoming', get=Upcoming)

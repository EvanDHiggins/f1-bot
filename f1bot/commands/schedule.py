from f1bot import command as cmd
from f1bot.lib import parsers
from f1bot.mysql import ergast

import f1bot

import argparse

PARSER = f1bot.add_command_parser(
        'schedule', description="Show the results for a session.")
PARSER.add_argument('year', type=parsers.parse_year)

class Schedule:
    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        year: int = args.year
        return ergast.get_schedule(year)

ScheduleCommand = cmd.Command(name='schedule', get=Schedule)

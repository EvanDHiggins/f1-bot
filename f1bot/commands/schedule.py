from f1bot import command as cmd
from f1bot.lib import parsers
from f1bot.mysql import ergast

import f1bot

import argparse

PARSER = f1bot.add_command_parser(
        'schedule', description="Show the results for a session.")
PARSER.add_argument('year', type=parsers.parse_year)

class Schedule(cmd.Command):
    @classmethod
    def name(cls) -> str:
        return 'schedule'

    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        year: int = args.year
        schedule = ergast.get_schedule(year).drop(columns=["Time"])
        if schedule is not None:
            return schedule
        raise cmd.CommandError(
            'Something went wrong. Didn\'t get a DataFrame '
            'after dropping "Time" column.')

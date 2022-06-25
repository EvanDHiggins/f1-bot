from f1bot import command as cmd
from f1bot.lib import parsers
from f1bot.mysql import ergast

import argparse

class Schedule(cmd.Command):

    @classmethod
    def manifest(cls) -> cmd.Manifest:
        return cmd.Manifest(
            name='schedule',
            description="Show the results for a session.",
        )

    @classmethod
    def init_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument('year', type=parsers.parse_year)


    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        year: int = args.year
        schedule = ergast.get_schedule(year).drop(columns=[
            "quali_date", "quali_time",
            "fp1_date", "fp1_time",
            "fp2_date", "fp2_time",
            "fp3_date", "fp3_time", "race_time"])

        if schedule is not None:
            return schedule 

        raise cmd.CommandError(
            'Something went wrong. Didn\'t get a DataFrame '
            'after dropping "Time" column.')

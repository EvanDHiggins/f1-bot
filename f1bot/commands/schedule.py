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

        none_df_error = cmd.CommandError(
            'Something went wrong. Didn\'t get a DataFrame '
            'after dropping "Time" column.')


        schedule = ergast.get_schedule(year).to_dataframe()[[
            "Name", "Round", "Circuit", "Location", "Race"
        ]]

        if schedule is None:
            raise none_df_error

        schedule["Race"] = schedule["Race"].apply(lambda x: x.date())
        schedule.rename({"Race": "Date"}, inplace=True)

        return schedule


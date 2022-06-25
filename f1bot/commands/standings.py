import f1bot

from f1bot import command as cmd
from f1bot.lib import parsers

from f1bot.mysql import ergast

import argparse
import enum
import pandas

class StandingsType(enum.Enum):
    CONSTRUCTORS = 0
    DRIVERS = 1

def parse_standing_type(arg: str) -> StandingsType:
    arg = arg.lower()
    if "drivers".startswith(arg) or arg == "wdc":
        return StandingsType.DRIVERS
    elif "constructors".startswith(arg) or arg.lower() == 'wcc':
        return StandingsType.CONSTRUCTORS
    raise cmd.CommandError(f"Invalid argument: {arg}")

def standings_from_ergast(standings_type: StandingsType, year: int) -> pandas.DataFrame:
    if standings_type == StandingsType.DRIVERS:
        # TODO: This should merge the forename and surname column into one.
        return ergast.get_driver_standings(year)
    return ergast.get_constructor_standings(year)

class Standings(cmd.Command):

    @classmethod
    def manifest(cls) -> cmd.Manifest:
        return cmd.Manifest(
            name='standings',
            description="Returns the driver standings for the year.",
        )

    @classmethod
    def init_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            'standings_type',
            choices=['drivers', 'wdc', 'constructors', 'wcc'],
            default='drivers',
            help="Determines which type of standings to fetch")
        parser.add_argument('year', type=parsers.parse_year)

    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        standings_type = parse_standing_type(args.standings_type)

        year: int = args.year
        if standings_type == StandingsType.CONSTRUCTORS and year < 1958:
            raise cmd.CommandError(
                "The constructors championship was not awarded until 1958.")

        # TODO: Handle the current year differently. The database will usually
        # be a little stale, but for standings we want to always include the
        # most up to date information. Fastf1 doesn't seem to provide this,
        # so we'll probably want to get it from ergast.
        return standings_from_ergast(standings_type, year)

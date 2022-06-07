import f1bot

from f1bot import command as cmd
from f1bot.lib import parsers

from f1bot.mysql import ergast

import argparse
import enum

NAME = 'standings'

PARSER = f1bot.add_command_parser(
        NAME,
        description="Returns the driver standings for the year.",)
PARSER.add_argument(
        'standings_type', choices=['drivers', 'wdc', 'constructors', 'wcc'],
        default='drivers', help="Determines which type of standings to fetch")
PARSER.add_argument('year', type=parsers.parse_year)

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


class Standings:
    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        standings_type = parse_standing_type(args.standings_type)

        # TODO: Make it so that this defers to fastf1 if we're requesting the
        # current year. Ergast won't be as up to date as we'd like.
        year: int = args.year

        if standings_type == StandingsType.DRIVERS:
            # TODO: This should merge the forename and surname column into one.
            return ergast.get_driver_standings(year)

        if year < 1958:
            raise cmd.CommandError(
                "The constructors championship was not awarded until 1958.")
        return ergast.get_constructor_standings(year)


StandingsCommand = cmd.Command(name=NAME, get=Standings)

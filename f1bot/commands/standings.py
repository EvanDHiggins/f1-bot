import f1bot

from f1bot import command as cmd
from f1bot.lib.json import Compose, Extractor, JsonTableSchema
from f1bot.lib import parsers

from typing import Optional
from datetime import date

import requests
import pandas
import attrs
import fastf1
import argparse

PARSER = f1bot.add_command_parser(
        'standings',
        description="Returns the driver standings for the year.",)
PARSER.add_argument(
        'standings_type', choices=['drivers', 'constructors'],
        default='drivers', help="Determines which type of standings to fetch")
PARSER.add_argument('year', type=parsers.parse_year)

@attrs.define(frozen=True)
class StandingsSpec:
    url_component: str
    json_field: str
    table_schema: JsonTableSchema


NameExtractor = Compose(
    Extractor(['Driver', 'givenName']),
    Extractor(['Driver', 'familyName']),
    lambda x, y: " ".join([x, y]))


EventNumber = Extractor(
    ['MRData', 'StandingsTable', 'StandingsList', 'round'])


DRIVER = StandingsSpec(
    url_component='driverStandings',
    json_field='DriverStandings',
    table_schema=JsonTableSchema([
        ('Position', Extractor(['position'])),
        ('Driver', NameExtractor),
        ('Points', Extractor(['points'])),
        ('Team', Extractor(['Constructors', 0, 'name'])),
    ]))


CONSTRUCTOR = StandingsSpec(
    url_component='constructorStandings',
    json_field='ConstructorStandings',
    table_schema=JsonTableSchema([
        ('Team', Extractor(['Constructor', 'name'])),
        ('Position', Extractor(['position'])),
        ('Points', Extractor(['points'])),
        ('Wins', Extractor(['wins'])),
    ]))


def build_query_url(stype: StandingsSpec, year: Optional[int]) -> str:
    if year is None:
        yearStr = 'current'
    else:
        yearStr = str(year)
    return f'http://ergast.com/api/f1/{yearStr}/{stype.url_component}.json'


def get_standings(
    stype: StandingsSpec, year: Optional[int] = None
) -> cmd.CommandValue:
    query_url = build_query_url(stype, year)
    resp = requests.get(query_url)
    standings_list_json = (
        resp.json()['MRData']['StandingsTable']['StandingsLists'][0][
            stype.json_field])

    results = []

    if year is None:
        round_num = (
            resp.json()['MRData']['StandingsTable']['StandingsLists'][0]['round'])
        current_year = date.today().year
        event = fastf1.get_event(current_year, int(round_num))
        results.append(f"Standings as of: {event.EventName}")

    rows = [
        stype.table_schema.extract(js_obj)
        for js_obj in standings_list_json]
    results.append(pandas.DataFrame(
        columns=stype.table_schema.column_names(), data=rows))

    return results


def parse_standing_type(arg: str) -> StandingsSpec:
    arg = arg.lower()
    if "drivers".startswith(arg) or arg == "wdc":
        return DRIVER
    elif "constructors".startswith(arg) or arg.lower() == 'wcc':
        return CONSTRUCTOR
    raise cmd.CommandError(f"Invalid argument: {arg}")


class Standings:
    """Returns standings for the drivers or constructors championships."""
    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        standings_type = parse_standing_type(args.standings_type)
        year = args.year

        if standings_type is CONSTRUCTOR and year < 1958:
            raise cmd.CommandError(
                "The constructors championship was not awarded until 1958.")


        return get_standings(standings_type, year)


StandingsCommand = cmd.Command(name="standings", get=Standings)

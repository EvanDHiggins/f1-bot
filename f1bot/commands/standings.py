from f1bot.commands.command import CommandValue
from . import command as cmd
import fastf1
import requests
import enum
from typing import Optional, Any, Tuple, Union
import pandas
import attrs
import json

HELP_MSG="""standings $YEAR [$TYPE]

Where $Type: [drivers|constructors|wcc|wdc]
"""

@attrs.define(frozen=True)
class StandingsValue:
    url_component: str
    json_field: str
    row_extraction_map: list[Tuple[str, list[Union[str, int]]]]

class StandingsType(enum.Enum):
    DRIVER = StandingsValue(
        url_component='driverStandings',
        json_field='DriverStandings',
        row_extraction_map=[
            ('Position', ['position']),
            ('Driver', ['Driver', 'code']),
            ('Points', ['points']),
            ('Team', ['Constructors', 0, 'name']),
        ])
    CONSTRUCTOR = StandingsValue(
        url_component='constructorStandings',
        json_field='ConstructorStandings',
        row_extraction_map=[
            ('Team', ['Constructor', 'name']),
            ('Position', ['position']),
            ('Points', ['points']),
            ('Wins', ['wins']),
        ])

    def extract_row_from_json(self, js: dict[str, Any]) -> list[str]:
        row = []
        for extractor in self.value.row_extraction_map:
            value: Any = js
            for key in extractor[1]:
                value = value[key]
            if value is dict or value is list:
                raise ValueError(
                    "Incorrectly specified row extraction from ergast JSON response."
                    f"Used keys {extractor[1]} but resolved to {value} from object:\n\n{js}")
            row.append(value)
        return row

    def column_names(self) -> list[str]:
        return list(extractor[0] for extractor in self.value.row_extraction_map)

def build_query_url(stype: StandingsType, year: Optional[int]) -> str:
    if year is None:
        yearStr = 'current'
    else:
        yearStr = str(year)
    return f'http://ergast.com/api/f1/{yearStr}/{stype.value.url_component}.json'

def standings(stype: StandingsType, year: Optional[int] = None) -> pandas.DataFrame:
    query_url = build_query_url(stype, year)
    print(f'Calling {query_url}')
    resp = requests.get(query_url)
    standings_list_json = (
        resp.json()['MRData']['StandingsTable']['StandingsLists'][0][
            stype.value.json_field])

    rows = [
        stype.extract_row_from_json(js_obj)
        for js_obj in standings_list_json]
    return pandas.DataFrame(columns=stype.column_names(), data=rows)


def parse_standing_type(arg: str) -> StandingsType:
    arg = arg.lower()
    if "drivers".startswith(arg) or arg == "wdc":
        return StandingsType.DRIVER
    elif "constructors".startswith(arg) or arg.lower() == 'wcc':
        return StandingsType.CONSTRUCTOR
    raise cmd.CommandError(f"Invalid argument: {arg}")

class Standings:
    """Returns standings for the drivers or constructors championships."""
    def run(self, args: list[str]) -> CommandValue:
        standing_type = StandingsType.DRIVER
        year = None

        if len(args) >= 1:
            standing_type = parse_standing_type(args[0].lower())

        if len(args) >= 2:
            year = int(args[1])

        return standings(standing_type, year)


StandingsCommand = cmd.Command(
    name="standings",
    description="Returns the driver standings for the year.",
    help=HELP_MSG,
    get=Standings,
)

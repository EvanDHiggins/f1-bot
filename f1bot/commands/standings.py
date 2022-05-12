from f1bot.commands.command import CommandValue
from . import command as cmd
import requests
from typing import Optional, Any, Tuple, Union, Protocol, Callable
import pandas
import attrs
import fastf1
from datetime import date

HELP_MSG="""standings $YEAR [$TYPE]

Where $Type: [drivers|constructors|wcc|wdc]
"""

class JsonExtractor(Protocol):
    def extract(self, js: dict[str, Any]) -> str:
        raise NotImplementedError


@attrs.define()
class Compose:
    first: JsonExtractor
    second: JsonExtractor
    binary_op: Callable[[str, str], str]

    def extract(self, js: dict[str, Any]) -> str:
        return self.binary_op(self.first.extract(js), self.second.extract(js))


@attrs.define()
class Extractor:
    keys: list[Union[str, int]]

    def extract(self, js: dict[str, Any]) -> str:
        value: Any = js
        for key in self.keys:
            value = value[key]
        if value is dict or value is list:
            raise ValueError(
                "Incorrectly specified row extraction from ergast JSON response."
                f"Used keys {self.keys} but resolved to {value} from object:\n\n{js}")
        return value


@attrs.define()
class JsonTableSchema:
    columns: list[Tuple[str, JsonExtractor]]

    def extract(self, js: dict[str, Any]) -> list[str]:
        rows = []
        for column in self.columns:
            rows.append(column[1].extract(js))
        return rows

    def column_names(self) -> list[str]:
        return list(col[0] for col in self.columns)


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


def get_standings(stype: StandingsSpec, year: Optional[int] = None) -> CommandValue:
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
    def run(self, args: list[str]) -> CommandValue:
        standing_type = DRIVER
        year = None

        if len(args) >= 1:
            standing_type = parse_standing_type(args[0].lower())

        if len(args) >= 2:
            if not args[1].isdigit():
                raise cmd.CommandError(f"Could not parse {args[1]} as a year.")
            year = int(args[1])
            if year < 1950:
                raise cmd.CommandError("F1's first race was in 1950.")
            if year > date.today().year:
                raise cmd.CommandError("That year hasn't happened yet.")

        return get_standings(standing_type, year)


StandingsCommand = cmd.Command(
    name="standings",
    description="Returns the driver standings for the year.",
    help=HELP_MSG,
    get=Standings,
)

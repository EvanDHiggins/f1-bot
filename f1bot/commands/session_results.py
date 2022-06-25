from f1bot import command as cmd
from f1bot.lib import parsers
from f1bot.lib.sessions import SessionType
from f1bot.mysql import ergast
import argparse

class SessionResults(cmd.Command):
    """Returns the session results for a particular session."""

    @classmethod
    def manifest(cls) -> cmd.Manifest:
        return cmd.Manifest(
            name='results',
            description="Show the results for a session.",
        )

    @classmethod
    def init_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument('year', type=parsers.parse_year)
        parser.add_argument('weekend', type=str)
        parser.add_argument('session_type', type=SessionType.parse)

    def run(self, args: argparse.Namespace) -> cmd.CommandValue:
        year: int = args.year
        weekend: str = args.weekend
        session_type: SessionType = args.session_type
        race_id = ergast.resolve_fuzzy_race_query(year, weekend)
        if race_id is None:
            raise cmd.CommandError(
                f'Could not find race \'{weekend}\' in {year}.')
        if session_type == SessionType.RACE:
            return ergast.get_race_session(race_id)
        elif session_type == SessionType.QUALIFYING:
            return ergast.get_qualifying_session(race_id)
        elif session_type is None:
            raise cmd.CommandError("Unknown session type.")
        raise cmd.CommandError(
            "We don't support that command type yet.")

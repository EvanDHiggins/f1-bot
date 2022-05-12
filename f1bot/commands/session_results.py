from f1bot import command as cmd
from typing import Tuple
from fastf1.core import Session
from f1bot.lib.sessions import SessionType, SessionLoader
from f1bot.utils.fmt import format_lap_time
from f1bot.lib import parsers
import pandas

HELP_MSG="""results $YEAR $WEEKEND [Q|R|FPN]"""

class SessionResults:
    """Returns the session results for a particular session."""
    def run(self, args: list[str]) -> cmd.CommandValue:
        year, weekend, session_type = self.parse_args(args)
        return self.get_results(year, weekend, session_type)

    def get_results(
        self, year: int, weekend: str, session_type: SessionType
    ) -> cmd.CommandValue:
        session = SessionLoader(
                session_types=[session_type]
            ).load_for_weekend(year, weekend)[0]
        if session_type == SessionType.RACE:
            return self.format_race(session)
        elif session_type == SessionType.QUALIFYING:
            return self.format_qualifying(session)
        return self.format_practice(session)


    def format_race(self, session: Session) -> cmd.CommandValue:
        results = session.results[
            ['FullName', 'Position', 'TeamName', 'Status']
        ]
        results['Position'] = results['Position'].astype(int)
        return [session.event.EventName, results]

    def format_qualifying(self, session: Session) -> cmd.CommandValue:
        results = session.results[
            ['FullName', 'Position', 'TeamName', 'Q1', 'Q2', 'Q3']
        ]

        # Converts lap times into a readable format from Timedelta
        for q in ['Q1', 'Q2', 'Q3']:
            results[q] = results[q].apply(format_lap_time)

        results['Position'] = results['Position'].astype(int)
        return [session.event.EventName, results]

    def format_practice(self, session: Session) -> pandas.DataFrame:
        return session.results

    def parse_args(self, args: list[str]) -> Tuple[int, str, SessionType]:
        if len(args) != 3:
            raise cmd.CommandError(
                f"Not enough arguments. Expected 3, found {len(args)}.")

        year = parsers.parse_year(args[0])
        if year < 1950:
            raise cmd.CommandError("Formula 1 started in 1950...")

        session_type = SessionType.parse(args[2])
        if session_type is None:
            raise cmd.CommandError(
                f"Could not parse session string: {args[2]}")

        return year, args[1], session_type

SessionResultsCommand = cmd.Command(
    name="results",
    description="Returns the results for a session.",
    help=HELP_MSG,
    get=SessionResults,
)

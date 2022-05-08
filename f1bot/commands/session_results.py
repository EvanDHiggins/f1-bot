from . import command as cmd
from typing import Tuple
from fastf1.core import Session
from f1bot.lib.sessions import SessionType, SessionLoader

HELP_MSG="""results $YEAR $WEEKEND [Q|R|FPN]"""

class SessionResults:
    """Returns the session results for a particular session."""
    def run(self, args: list[str]) -> str:
        year, weekend, session_type = self.parse_args(args)
        return self.get_results(year, weekend, session_type)

    def get_results(
        self, year: int, weekend: str, session_type: SessionType
    ) -> str:
        session = SessionLoader(
                session_types=[session_type]
            ).load_for_weekend(year, weekend)[0]
        if session_type == SessionType.RACE:
            return self.format_race(session)
        elif session_type == SessionType.QUALIFYING:
            return self.format_qualifying(session)
        return self.format_practice(session)

    def format_race(self, session: Session) -> str:
        return ""

    def format_qualifying(self, session: Session) -> str:
        return ""

    def format_practice(self, session: Session) -> str:
        return ""

    def parse_args(self, args: list[str]) -> Tuple[int, str, SessionType]:
        if len(args) != 3:
            raise cmd.CommandError(
                f"Not enough arguments. Expected 3, found {len(args)}.")

        year = int(args[0])
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

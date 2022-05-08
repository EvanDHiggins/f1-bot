import fastf1

from attrs import define
from typing import Iterable
from fastf1.core import Session
import enum
from typing import Optional

class SessionType(enum.Enum):
    FREE_PRACTICE_1 = 'FP1'
    FREE_PRACTICE_2 = 'FP2'
    FREE_PRACTICE_3 = 'FP3'
    QUALIFYING = 'Q'
    RACE = 'R'

    @staticmethod
    def parse(s: str) -> Optional['SessionType']:
        for session_type in SessionType:
            if s.upper() == session_type.value:
                return session_type
        return None

@define
class SessionPredicate:
    name: str
    year: int
    session: SessionType

    def matches(self, session: Session) -> bool:
        return (self.name in session.event.EventName and
                self.year == session.date.year and
                self.session.value == session.name)


@define
class SessionLoader:
    # Values like 'R', 'Q', etc. that fastf1 accepts as valid session types.
    session_types: Iterable[SessionType]

    # Passed through to fastf1.core.Session.load
    laps: bool = False
    telemetry: bool = False
    weather: bool = False
    livedata: bool = False

    # Random sessions will have bad data which cause failures that are hard to
    # catch generically (e.g. a try/except), so this let's me selectively omit
    # races where I find issues.
    ignore: list[SessionPredicate] = []

    _corrupted_sessions: list[Session] = []
    _ignored_sessions: list[Session] = []

    def corrupted_sessions(self) -> list[Session]:
        return self._corrupted_sessions

    def ignored_sessions(self) -> list[Session]:
        return self._ignored_sessions

    def load_for_years(self, years: Iterable[int]) -> list[Session]:
        unloaded_sessions: list[Session] = []
        for year in years:
            unloaded_sessions.extend(
                    get_unloaded_sessions_for_year(year, self.session_types))
        
        return self._safe_load(unloaded_sessions)

    def load_for_weekend(self, year: int, weekend: str) -> list[Session]:
        unloaded_sessions: list[Session] = []
        for session_type in self.session_types:
            unloaded_sessions.append(
                fastf1.get_session(year, weekend, session_type.value))
        return self._safe_load(unloaded_sessions)


    def _safe_load(
        self, sessions: Iterable[Session]
    ) -> list[Session]:
        """Loads sessions and silences API errors that are encountered."""
        loaded_sessions = []
        for session in sessions:
            if any(pred.matches(session) for pred in self.ignore):
                self._ignored_sessions.append(session)
                continue

            # Sometimes sessions have bad data from Ergast. We'll keep going
            # and deal with them later.
            try:
                session.load(
                    laps=self.laps,
                    telemetry=self.telemetry,
                    weather=self.weather,
                    livedata=self.livedata
                )
            except ValueError:
                self._corrupted_sessions.append(session)
                continue
            loaded_sessions.append(session)
        return loaded_sessions

def get_unloaded_sessions_for_year(
    year: int, session_types: Iterable[SessionType]
) -> list[Session]:
    schedule = fastf1.get_event_schedule(year)
    sessions = []
    for round_num in schedule.RoundNumber.values:
        if round_num == 0:
            # Testing sessions have a number, but they cause the API to blow up.
            continue
        for session_type in session_types:
            sessions.append(fastf1.get_session(year, round_num, session_type.value))
    return sessions

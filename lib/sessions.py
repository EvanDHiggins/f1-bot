import fastf1

from attrs import define
from typing import Iterable
from fastf1.core import Session

@define
class SessionLoader:
    # Values like 'R', 'Q', etc. that fastf1 accepts as valid session types.
    session_types: Iterable[str]

    # Passed through to fastf1.core.Session.load
    laps: bool = False
    telemetry: bool = False
    weather: bool = False
    livedata: bool = False

    _session_load_err_count: int = 0
    _corrupted_sessions: list[Session] = []

    def err_count(self) -> int:
        return self._session_load_err_count

    def corrupted_sessions(self) -> list[Session]:
        return self._corrupted_sessions

    def load_for_years(self, years: Iterable[int]) -> list[Session]:
        unloaded_sessions: list[Session] = []
        for year in years:
            unloaded_sessions.extend(
                    get_unloaded_sessions_for_year(year, self.session_types))
        
        return self.safe_load(unloaded_sessions)

    def safe_load(
        self, sessions: Iterable[Session]
    ) -> list[Session]:
        """Loads sessions and silences API errors that are encountered."""
        loaded_sessions = []
        for session in sessions:
            # There's an error in a single session's ergast data that causes
            # fastf1 to barf. So we'll just catch the error and throw out that
            # race.
            try:
                session.load(
                    laps=self.laps,
                    telemetry=self.telemetry,
                    weather=self.weather,
                    livedata=self.livedata
                )
            except ValueError:
                self._session_load_err_count += 1
                self._corrupted_sessions.append(session)
                continue
            loaded_sessions.append(session)
        return loaded_sessions

def get_unloaded_sessions_for_year(
    year: int, session_types: Iterable[str]
) -> list[Session]:
    schedule = fastf1.get_event_schedule(year)
    sessions = []
    for round_num in schedule.RoundNumber.values:
        if round_num == 0:
            # Testing sessions have a number, but they cause the API to blow up.
            continue
        for session_type in session_types:
            sessions.append(fastf1.get_session(year, round_num, session_type))
    return sessions

import fastf1
from collections import defaultdict
from attrs import define
from typing import Optional

DriverAbbrev = str
DriverNum = str

def get_teammates(
    session_results: fastf1.core.SessionResults
) -> list[tuple[DriverNum, DriverNum]]:
    """Returns pairings of driver abbrevs who were teammates in this session.

    If a team ran only one driver (or >2) they'll be ommitted from the results.
    
    NOTE: Driver numbers are not stable across seasons, so this should only be
    used when considering data from a single session.
    """
    teams = defaultdict(lambda: [])
    for (driver_num, team_name) in session_results.TeamName.items():
        teams[team_name].append(driver_num)

    # Remove teams with fewer than 2 drivers (no teammates to consider)
    driver_count = {team: len(drivers) for team, drivers in teams.items()}
    for team_name, num_drivers in driver_count.items():
        if num_drivers != 2:
            teams.pop(team_name)

    return [tuple(drivers) for drivers in teams.values()]

@define
class DerivedDriverSessionData:
    number: str
    abbreviation: str
    finish_pos: int
    teammate_delta: Optional[int] = None


def compute_teammate_deltas(
    session_results: fastf1.core.SessionResults
) -> list[DerivedDriverSessionData]:
    """Converts session results to a numeric teammate delta map.

    Args:
        session_results: A session result for a single race.
    Returns:
        A mapping of driver number to the finishing delta to their teammate.
        A positive delta indicates they were ahead, a negative delta indicates
        they were behind.
    """
    def to_derived(driver_num: str) -> DerivedDriverSessionData:
        return DerivedDriverSessionData(
            number=driver_num,
            abbreviation=session_results.Abbreviation[driver_num],
            finish_pos=int(session_results.Position[driver_num]))

    teammates = [
        (to_derived(d1), to_derived(d2))
        for d1, d2 in get_teammates(session_results)
    ]
    for d1, d2 in teammates:
        d1.teammate_delta = d2.finish_pos - d1.finish_pos
        d2.teammate_delta = -d1.teammate_delta


    return [driver for drivers in teammates for driver in drivers]


def main():
    fastf1.Cache.enable_cache('../.f1-cache')
    session = fastf1.get_session(2022, 'Bahrain', 'R')
    session.load(laps=True,telemetry=False, weather=False, livedata=False)
    driver_session_data = compute_teammate_deltas(session.results)
    for data in driver_session_data:
        print(f'{data.abbreviation} -- {data.teammate_delta}')


if __name__ == "__main__":
    main()

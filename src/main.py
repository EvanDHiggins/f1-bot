import fastf1
from collections import defaultdict
from attrs import define
from typing import Optional

DriverAbbrev = str
DriverNum = str

@define
class DerivedDriverSessionData:
    """Collection of driver data.

    Some of this is pulled straight from fastf1.core.SessionResults, other
    pieces are derived.
    """

    # SessionResults keys drivers by the string repr of their number
    number: str

    # Driver abbreviation, e.g. VER, HAM, GAS
    abbreviation: str

    # The integer position they finished in.
    finish_pos: int

    # The number of positions that they are ahead of their teammate.
    # If driver A finishes 1st and driver B finishes 4th, their deltas are 3
    # and -3, respectively.
    teammate_delta: Optional[int] = None


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

def get_unloaded_sessions_for_year(year: int) -> list[fastf1.core.SessionResults]:
    schedule = fastf1.get_event_schedule(year)
    sessions = []
    for round_num in schedule.RoundNumber.values:
        if round_num == 0:
            # Testing sessions have a number, but they cause the API to blow up.
            continue
        sessions.append(fastf1.get_session(year, round_num, 'R'))
    return sessions

class Average:
    def __init__(self):
        self.total = 0
        self.count = 0

    def add(self, num: int):
        self.total += num
        self.count += 1

    def compute(self) -> float:
        return self.total / self.count

def compute_average_deltas_from_sessions(
    sessions: list[fastf1.core.SessionResults]
) -> dict[DriverAbbrev, float]:
    driver_data = [
        compute_teammate_deltas(session.results)
        for session in sessions
    ]

    # maps driver abbreviation to average
    delta_averages = defaultdict(lambda: Average())

    for race in driver_data:
        for driver in race:
            delta_averages[driver.abbreviation].add(driver.teammate_delta)

    average_deltas = {abbrev: avg.compute() for abbrev, avg in delta_averages.items()}
    return average_deltas


def main():
    fastf1.Cache.enable_cache('../.f1-cache')
    years_to_fetch = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    sessions = []
    for year in years_to_fetch:
        sessions.extend(get_unloaded_sessions_for_year(year))

    for session in sessions:
        session.load(laps=True, telemetry=False, weather=False, livedata=False)

    print(compute_average_deltas_from_sessions(sessions))

    # session = fastf1.get_session(2022, 'Bahrain', 'R')
    # session.load(laps=True,telemetry=False, weather=False, livedata=False)
    # driver_session_data = compute_teammate_deltas(session.results)
    # for data in driver_session_data:
        # print(f'{data.abbreviation} -- {data.teammate_delta}')


if __name__ == "__main__":
    main()

from f1bot import command as cmd

from f1bot.mysql import engine

from f1bot.data.standings import Standings
from f1bot.data.standings import Row as StandingsRow
from f1bot.data.schedule import Schedule
from f1bot.data.schedule import Row as ScheduleRow

import sqlalchemy as sql # type: ignore
import sqlalchemy.engine as sqlengine
import pandas
import attr

import datetime as dt

from typing import Optional

RaceId = int

def transform_to_dataframe(
    result: sqlengine.CursorResult, columns: list[str]
) -> pandas.DataFrame:
    return pandas.DataFrame(
        columns=columns, data=result.columns(*columns))

@engine.with_ergast
def get_qualifying_session(
    conn: sqlengine.Connection, race_id: RaceId
) -> cmd.CommandValue:
    result = conn.execute(sql.text(
        f"""
        SELECT *
        FROM qualifying q
        INNER JOIN drivers d
        ON q.driverId = d.driverId
        where raceId = :race_id
        """
    ), race_id=race_id)
    return transform_to_dataframe(
        result,
        ['number', 'forename', 'surname', 'position', 'q1', 'q2', 'q3'])


@engine.with_ergast
def get_race_session(
    conn: sqlengine.Connection, race_id: RaceId,
) -> cmd.CommandValue:
    result = conn.execute(sql.text(
        f"""
        SELECT *
        FROM results r
        INNER JOIN drivers d
        ON r.driverId = d.driverId
        INNER JOIN status s
        ON s.statusId = r.statusId
        WHERE r.raceId = :race_id
        """
    ), race_id=race_id)
    return transform_to_dataframe(
        result,
        ['number', 'forename', 'surname', 'position', 'time', 'status'])


@engine.with_ergast
def get_last_race_of_year(conn: sqlengine.Connection, year: int) -> RaceId:
    """Returns the raceId for the last year in a particular race calendar."""
    result = conn.execute(sql.text(
        # Uses a window query to rank all races against other races in the
        # same year against the "races.round" column and then selects the
        # largest 1st rank.
        f"""
        SELECT
            raceId, name
        FROM (
          SELECT
            raceId,
            name,
            year,
            ROW_NUMBER() OVER (PARTITION BY year ORDER BY round DESC) as rnk
          FROM races) r
        WHERE r.rnk = 1 AND r.year = {year}"""))
    if result.rowcount != 1:
        raise cmd.CommandError(
                f'Failed to find the last race of the year for {year}.'
                f'Expected 1 result, found {result.rowcount}')
    row = result.first()

    # We've already made sure this isn't possible.
    assert row is not None

    return row['raceId']

@attr.define
class Event:
    pass


s = """
Name, Date, Time (PT), Time (MT), Time (CT), Time (ET)

FP1, ...
FP2, ...
FP3, ...
Qualifying, ...
Azerbaijan GP, June 11th, PT, MT, CT, ET
"""

@engine.with_ergast
def get_schedule(conn: sqlengine.Connection, year: int) -> pandas.DataFrame:
    result = conn.execute(sql.text(
        f"""
        SELECT
            r.name as "race_name",
            r.round as "round",
            c.name as "circuit_name",
            c.location as "location",
            r.date as "race_date",
            r.time as "race_time",
            fp1_date, fp1_time,
            fp2_date, fp2_time,
            fp3_date, fp3_time,
            quali_date, quali_time,
            sprint_date, sprint_time
        FROM races r
            INNER JOIN circuits c
            ON r.circuitId = c.circuitId
        WHERE year = {year}
        ORDER BY round"""))

    def to_dt(s: sqlengine.Row, prefix: str) -> Optional[dt.datetime]:
        event_date = s[f"{prefix}_date"]
        if event_date is None:
            return None
        event_time = s[f"{prefix}_time"]
        return dt.datetime(
            year=event_date.year, month=event_date.month, day=event_date.day
        ) + event_time

    return Schedule(
        rows=[
            ScheduleRow(
                race_name=row['race_name'],
                round_num=row['round'],
                circuit=row['circuit_name'],
                location=row['location'],
                race=to_dt(row, 'race'),
                sprint=to_dt(row, 'sprint'),
                qualifying=to_dt(row, 'quali'),
                fp1=to_dt(row, 'fp1'),
                fp2=to_dt(row, 'fp2'),
                fp3=to_dt(row, 'fp3'),
            )
            for row in result.all()
        ]
    )


@engine.with_ergast
def resolve_fuzzy_race_query(
    conn: sqlengine.Connection, year: int, query: str
) -> Optional[RaceId]:
    match_by_race_name = conn.execute(sql.text(
        """
        SELECT *
        FROM races
        WHERE
            name LIKE CONCAT('%', :race_name, '%')
            AND year = :year
        """), race_name=query, year=year)
    if match_by_race_name.rowcount == 1:
        race = match_by_race_name.first()
        if race is None:
            raise ValueError(
                'Expected one result, found None?! For query '
                f'(year={year}, q={query})')
        return int(race['raceId'])

    match_by_track_name = conn.execute(sql.text(
        """
        SELECT *
        FROM races r
        INNER JOIN circuits c
        ON r.circuitId = c.circuitId
        WHERE
            c.name LIKE CONCAT('%', :race_name, '%')
            AND year = :year
        """), race_name=query, year=year)
    if match_by_track_name.rowcount == 1:
        race = match_by_track_name.first()
        if race is None:
            raise ValueError(
                'Expected one result, found None?! For query '
                f'(year={year}, q={query})')
        return int(race['raceId'])

    return None



@engine.with_ergast
def get_driver_standings(
    conn: sqlengine.Connection, year: int,
) -> Standings:
    last_race_id = get_last_race_of_year(year)
    result = conn.execute(sql.text(
        f"""
        SELECT *
        FROM driverStandings ds
        INNER JOIN drivers d
        ON ds.driverId = d.driverId
        WHERE raceId = {last_race_id}
        ORDER BY position
        """
    ))

    return Standings(
        rows=[
            StandingsRow(
                name=" ".join([row["forename"], row["surname"]]),
                position=row["position"],
                points=row["points"]
            )
            for row in result.all()
        ]
    )

@engine.with_ergast
def get_constructor_standings(
    conn: sqlengine.Connection, year: int,
) -> Standings:
    last_race_id = get_last_race_of_year(year)
    result = conn.execute(sql.text(
        f"""
        SELECT *
        FROM constructorStandings cs
        INNER JOIN constructors c
        ON cs.constructorId = c.constructorId
        WHERE raceId = {last_race_id}
        ORDER BY position
        """
    ))
    return Standings(
        rows=[
            StandingsRow(
                name=row["name"],
                position=row["position"],
                points=row["points"]
            )
            for row in result.all()
        ]
    )

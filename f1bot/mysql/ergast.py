from f1bot import command as cmd

import sqlalchemy as sql # type: ignore
import sqlalchemy.engine as sqlengine
import os
import attrs
import pandas

MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

ergast_engine = sql.create_engine(f"mysql+mysqldb://evanhiggins:{MYSQL_PASSWORD}@localhost/ergast")

RaceId = int

def transform_to_dataframe(
    result: sqlengine.CursorResult, columns: list[str]
) -> pandas.DataFrame:
    return pandas.DataFrame(
        columns=columns, data=result.columns(*columns))

def get_last_race_of_year(year: int) -> RaceId:
    """Returns the raceId for the last year in a particular race calendar."""
    with ergast_engine.connect() as conn:
        result = conn.execute(sql.text(
            # Uses a window query to rank all races against other races in the
            # same year against the "races.round" column and then selects the
            # largest 1st rank.
            f"""
            SELECT
                raceId, name
            FROM (
              SELECT
                raceId, name, year, ROW_NUMBER() OVER (PARTITION BY year ORDER BY round DESC) as rnk
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

def get_driver_standings(year: int) -> pandas.DataFrame:
    last_race_id = get_last_race_of_year(year)
    with ergast_engine.connect() as conn:
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
        return transform_to_dataframe(
                result, ["forename", "surname", "points", "position"])

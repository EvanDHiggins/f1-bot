import attr
import pandas
import datetime as dt

from typing import Optional

@attr.define()
class Row:
    race_name: str
    round_num: int
    circuit: str
    location: str
    race: dt.datetime
    sprint: Optional[dt.datetime]
    qualifying: Optional[dt.datetime]
    fp3: Optional[dt.datetime]
    fp2: Optional[dt.datetime]
    fp1: Optional[dt.datetime]

    @classmethod
    def keys(cls) -> list[str]:
        return [
            "Name",
            "Round",
            "Circuit",
            "Location",
            "Race",
            "Sprint",
            "Qualifying",
            "FP3",
            "FP2",
            "FP1"
        ]

    def to_series(self) -> pandas.Series:
        return pandas.Series(data={
            "Name": self.race_name,
            "Round": self.round_num,
            "Circuit": self.circuit,
            "Location": self.location,
            "Race": self.race,
            "Sprint": self.sprint,
            "Qualifying": self.qualifying,
            "FP3": self.fp3,
            "FP2": self.fp2,
            "FP1": self.fp1,
        })

@attr.define()
class Schedule:
    rows: list[Row]

    def to_dataframe(self) -> pandas.DataFrame:
        return pandas.DataFrame(
            columns=Row.keys(),
            data=(r.to_series() for r in self.rows)
        )

import attr
import pandas

@attr.define()
class Row:
    name: str
    position: int
    points: float

    @classmethod
    def keys(cls) -> list[str]:
        return ["Name", "Position", "Points"]

    def to_series(self) -> pandas.Series:
        return pandas.Series(data={
            "Name": self.name,
            "Position": self.position,
            "Points": self.points,
        })


@attr.define()
class Standings:
    rows: list[Row]

    def to_dataframe(self) -> pandas.DataFrame:
        return pandas.DataFrame(
            columns=Row.keys(),
            data=(r.to_series() for r in self.rows)
        )

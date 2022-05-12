from typing import Any, Tuple, Union, Protocol, Callable
import attrs

class JsonExtractor(Protocol):
    """Extracts a particular string value from json."""
    def extract(self, js: dict[str, Any]) -> str:
        raise NotImplementedError


@attrs.define()
class Compose:
    """Runs both extractors and combines their output with binary_op."""
    first: JsonExtractor
    second: JsonExtractor
    binary_op: Callable[[str, str], str]

    def extract(self, js: dict[str, Any]) -> str:
        return self.binary_op(self.first.extract(js), self.second.extract(js))


@attrs.define()
class Extractor:
    """Extracts a single value from the json object by iterating over keys."""
    keys: list[Union[str, int]]

    def extract(self, js: dict[str, Any]) -> str:
        value: Any = js
        for key in self.keys:
            value = value[key]
        if value is dict or value is list:
            raise ValueError(
                "Incorrectly specified row extraction from ergast JSON response."
                f"Used keys {self.keys} but resolved to {value} from object:\n\n{js}")
        return value


@attrs.define()
class JsonTableSchema:
    """Defines a way of extracting a table from a specific JSON object."""
    columns: list[Tuple[str, JsonExtractor]]

    def extract(self, js: dict[str, Any]) -> list[str]:
        rows = []
        for column in self.columns:
            rows.append(column[1].extract(js))
        return rows

    def column_names(self) -> list[str]:
        return list(col[0] for col in self.columns)

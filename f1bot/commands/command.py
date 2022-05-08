import attrs
from typing import Protocol, Type

class Runner(Protocol):
    def run(self, args: list[str]) -> str:
        raise NotImplementedError


@attrs.define(frozen=True)
class Command:
    name: str
    description: str
    help: str

    # Type constructor for a Runner
    get: Type[Runner]

    def run(self, args: list[str]) -> str:
        return self.get().run(args)

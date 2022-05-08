import attrs
from typing import Protocol, Type

class Runner(Protocol):
    def run(self, args: list[str]) -> str:
        raise NotImplementedError


class CommandError(Exception):
    """Describes an error running a command.

    Prefer to use this for "well-formed" errors like malformed input or a year
    that doesn't exist. Errors that aren't in the users control (e.g. API
    errors) should just raise any exception.
    """
    pass

@attrs.define(frozen=True)
class Command:
    name: str
    description: str
    help: str

    # Type constructor for a Runner
    get: Type[Runner]

    def run(self, args: list[str]) -> str:
        try:
            return self.get().run(args)
        except CommandError as e:
            return f"Failed to run command '{self.name}' with error:\n{str(e)}\n\n\n{self.help}"

        except Exception as e:
            return f"Internal error running command: {self.name}.\n\n{str(e)}"


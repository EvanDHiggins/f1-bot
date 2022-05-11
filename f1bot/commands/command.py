import attrs
from typing import Protocol, Type, Union
import pandas
import enum
import traceback

class CommandStatus(enum.Enum):
    OK = 0
    INTERNAL_ERROR = 1

CommandValue = Union[str, pandas.DataFrame]

@attrs.define(frozen=True)
class CommandResult:
    status: CommandStatus
    value: CommandValue

    @staticmethod
    def error(value: CommandValue) -> 'CommandResult':
        return CommandResult(status=CommandStatus.INTERNAL_ERROR, value=value)

    @staticmethod
    def ok(value: CommandValue) -> 'CommandResult':
        return CommandResult(status=CommandStatus.OK, value=value)

    def is_ok(self) -> bool:
        return self.status == CommandStatus.OK

    def is_error(self) -> bool:
        return self.status == CommandStatus.INTERNAL_ERROR


class Runner(Protocol):
    def run(self, args: list[str]) -> CommandValue:
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

    def run(self, args: list[str]) -> CommandResult:
        try:
            return CommandResult.ok(self.get().run(args))
        except CommandError as e:
            return CommandResult.error(
                f"Failed to run command '{self.name}' with error:\n"
                f"{str(e)}\n\n\n{self.help}"
            )

        except Exception as e:
            return CommandResult.error(
                f"Internal error running command: {self.name}.\n\n{str(e)}\n{traceback.format_exc()}")


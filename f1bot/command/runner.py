from .command_protocol import CommandValue
from .command_registry import REGISTRY
import attrs
import enum
import traceback

import f1bot.argparser as argparser

class CommandError(Exception):
    """Describes an error running a command.

    Prefer to use this for "well-formed" errors like malformed input or a year
    that doesn't exist. Errors that aren't in the users control (e.g. API
    errors) should just raise any exception.
    """
    pass

class CommandStatus(enum.Enum):
    OK = 0
    INTERNAL_ERROR = 1

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

def run_command(args: list[str]) -> CommandResult:
    try:
        return _run_command(args)
    except Exception as e:
        return CommandResult.error(str(e))

def _run_command(args: list[str]) -> CommandResult:
    """Looks up a command and runs it.

    Supports three forms:
        help: Prints the availabe commands and their descriptions.
        help $COMMAND: Prints the help text for $COMMAND.
        $COMMAND args...: Runs COMMAND with args.
    """

    parsed_args = argparser.get().parse_args(args)
    command = REGISTRY.get(parsed_args.command).command_constructor
    try:
        return CommandResult.ok(command().run(parsed_args))
    except CommandError as e:
        return CommandResult.error(
            f"Failed to run command '{command.manifest().name}' with error:"
            f"\n{str(e)}")

    except Exception as e:
        return CommandResult.error(
            f"Internal error running command: {command.manifest().name}.\n\n"
            f"{str(e)}\n{traceback.format_exc()}")

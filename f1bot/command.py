import attrs
from typing import Protocol, Type, Union, Any,  runtime_checkable
import pandas
import enum
import traceback
import argparse
import f1bot

CommandPrimitive = Union[str, pandas.DataFrame]
CommandValue = Union[CommandPrimitive, list[CommandPrimitive]]

_commands: dict[str, Type['Runnable']] = {}

def get_command_dict() -> dict[str, Type['Runnable']]:
    return _commands

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


@runtime_checkable
class Runnable(Protocol):
    @classmethod
    def name(cls) -> str:
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> CommandValue:
        raise NotImplementedError


class CommandError(Exception):
    """Describes an error running a command.

    Prefer to use this for "well-formed" errors like malformed input or a year
    that doesn't exist. Errors that aren't in the users control (e.g. API
    errors) should just raise any exception.
    """
    pass

class CommandRegistrar(type):
    def __init__(cls, name: str, bases: Any, clsdict: dict[str, Any]):
        super(CommandRegistrar, cls).__init__(name, bases, clsdict)

        # Ignore the first derived class. This will always be AutoCommand
        if len(cls.mro()) <= 2:
            if name != 'Command':
                raise ValueError(
                    'Only "Command" can use CommandRegistrar as its metaclass.')
            return

        if not issubclass(cls, Runnable):
            raise ValueError(
                "All classes with metaclass CommandRegistrar must implement "
                f"'Runnable'. Class '{name}' does not.")

        _commands[cls.name()] = cls

class Command(metaclass=CommandRegistrar):
    pass

def run_command(args: list[str]) -> CommandResult:
    """Looks up a command and runs it.

    Supports three forms:
        help: Prints the availabe commands and their descriptions.
        help $COMMAND: Prints the help text for $COMMAND.
        $COMMAND args...: Runs COMMAND with args.
    """
    parsed_args = f1bot.get().parse_args(args)
    command = get_command_dict()[parsed_args.command]
    try:
        return CommandResult.ok(command().run(parsed_args))
    except CommandError as e:
        return CommandResult.error(
            f"Failed to run command '{command.name}' with error:\n{str(e)}")

    except Exception as e:
        return CommandResult.error(
            f"Internal error running command: {command.name}.\n\n{str(e)}\n{traceback.format_exc()}")

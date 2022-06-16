from typing_extensions import TypeGuard
import attrs
from typing import Protocol, Type, Union, Any, get_type_hints, Optional, TypeVar, runtime_checkable
import pandas
import enum
import traceback
import argparse
import abc


class CommandStatus(enum.Enum):
    OK = 0
    INTERNAL_ERROR = 1

CommandPrimitive = Union[str, pandas.DataFrame]
CommandValue = Union[CommandPrimitive, list[CommandPrimitive]]

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
class Runner(Protocol):
    def run(self, args: argparse.Namespace) -> CommandValue:
        raise NotImplementedError

@runtime_checkable
class Runnable(Protocol):
    @classmethod
    def name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def description(cls) -> str:
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

T = TypeVar('T', bound='type')

commands: dict[str, Type[Runnable]] = {}

class CommandRegistrar(type):
    def __init__(cls, name: str, bases: Any, clsdict: dict[str, Any]):
        super(CommandRegistrar, cls).__init__(name, bases, clsdict)

        # Ignore the first derived class. This will always be AutoCommand
        if len(cls.mro()) <= 2:
            if name != 'AutoCommand':
                raise ValueError(
                    'Only "AutoCommand" can use CommandRegistrar as its metaclass.')
            return

        if not issubclass(cls, Runnable):
            raise ValueError(
                "All classes with metaclass CommandRegistrar must implement "
                f"'Runnable'. Class '{name}' does not. mro = {len(cls.mro())}")

        commands[cls.name()] = cls
        print(commands)

"""
TODO: Replace "'class Command' with 'class LegacyCommand'"
"""

class AutoCommand(metaclass=CommandRegistrar):
    pass

class FirstCommand(AutoCommand):
    @classmethod
    def name(cls) -> str:
        return "first"

    @classmethod
    def description(cls) -> str:
        return "Some stuff."

    def run(self, args: argparse.Namespace) -> CommandValue:
        return ""


@attrs.define(frozen=True)
class Command:
    name: str

    # Type constructor for a Runner
    get: Type[Runner]

    def run(self, args: argparse.Namespace) -> CommandResult:
        try:
            return CommandResult.ok(self.get().run(args))
        except CommandError as e:
            return CommandResult.error(
                f"Failed to run command '{self.name}' with error:\n{str(e)}")

        except Exception as e:
            return CommandResult.error(
                f"Internal error running command: {self.name}.\n\n{str(e)}\n{traceback.format_exc()}")


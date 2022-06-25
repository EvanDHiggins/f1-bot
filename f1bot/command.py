import f1bot

import attrs
import pandas
import enum
import traceback
import argparse

from typing import Protocol, Type, Union, Any,  runtime_checkable

CommandPrimitive = Union[str, pandas.DataFrame]
CommandValue = Union[CommandPrimitive, list[CommandPrimitive]]

_commands: dict[str, Type['Runnable']] = {}

@attrs.define()
class RegistryEntry:
    name: str
    parser: argparse.ArgumentParser
    command_constructor: Type['Runnable']

class CommandRegistry:
    def __init__(self):
        self._commands: dict[str, RegistryEntry] = {}

    def register(self, command: Type['Runnable']):
        manifest = command.manifest()
        parser = command.init_parser(
            f1bot.add_command_parser(
                manifest.name, description=manifest.description))

        self._commands[manifest.name] = RegistryEntry(
                name=manifest.name,
                parser=parser,
                command_constructor=command)

    def __contains__(self, name: str) -> bool:
        return name in self._commands

    def get(self, name: str) -> RegistryEntry:
        return self._commands[name]

REGISTRY = CommandRegistry()

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


@attrs.define()
class Manifest:
    name: str
    description: str

@runtime_checkable
class Runnable(Protocol):

    @classmethod
    def manifest(cls) -> Manifest:
        raise NotImplementedError

    @classmethod
    def init_parser(cls, parser: argparse.ArgumentParser):
        """Initializes the parser associated with this Runnable.

        init_parser will be called exactly once during registration to
        initialize the ArgumentParser for this command.

        Args:
            parser: A subparser for the main ArgumentParser constructed with
                this Runnable's name().
        """
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> CommandValue:
        """Implementation of the actual command."""
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

        REGISTRY.register(cls)

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

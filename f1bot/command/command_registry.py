from .command_protocol import CommandProtocol

import f1bot.argparser as argparser

import attrs
import argparse

from typing import Type, Any

@attrs.define()
class RegistryEntry:
    name: str
    parser: argparse.ArgumentParser
    command_constructor: Type[CommandProtocol]

class CommandRegistry:
    def __init__(self):
        self._commands: dict[str, RegistryEntry] = {}

    def register(self, command: Type[CommandProtocol]):
        manifest = command.manifest()
        if manifest.disabled:
            return

        parser = command.init_parser(
            argparser.add_command_parser(
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


class CommandRegistrar(type):
    def __init__(cls, name: str, bases: Any, clsdict: dict[str, Any]):
        super(CommandRegistrar, cls).__init__(name, bases, clsdict)

        # Ignore the first derived class. This will always be AutoCommand
        if len(cls.mro()) <= 2:
            if name != 'Command':
                raise ValueError(
                    'Only "Command" can use CommandRegistrar as its metaclass.')
            return

        if not issubclass(cls, CommandProtocol):
            raise ValueError(
                "All classes with metaclass CommandRegistrar must implement "
                f"'Runnable'. Class '{name}' does not.")

        REGISTRY.register(cls)

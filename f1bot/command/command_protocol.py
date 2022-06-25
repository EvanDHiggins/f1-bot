import attrs
import argparse
import pandas

from typing import Protocol, runtime_checkable, Union

CommandPrimitive = Union[str, pandas.DataFrame]
CommandValue = Union[CommandPrimitive, list[CommandPrimitive]]

@attrs.define()
class Manifest:
    name: str
    description: str

@runtime_checkable
class CommandProtocol(Protocol):

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

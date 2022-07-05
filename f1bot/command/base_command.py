from .command_registry import CommandRegistrar

import argparse

class Command(metaclass=CommandRegistrar):

    @classmethod
    def init_parser(cls, _parser: argparse.ArgumentParser):
        pass


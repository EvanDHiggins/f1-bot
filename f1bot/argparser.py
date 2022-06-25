import argparse
import f1bot.command as cmd

class F1ArgParser(argparse.ArgumentParser):
    def error(self, message: str):
        raise cmd.CommandError(message)

_ARG_PARSER = F1ArgParser('f1bot')
_SUBPARSERS = _ARG_PARSER.add_subparsers(title='commands', dest='command')

def add_command_parser(*args, **kwargs) -> argparse.ArgumentParser:
    return _SUBPARSERS.add_parser(*args, **kwargs)

def get() -> argparse.ArgumentParser:
    return _ARG_PARSER

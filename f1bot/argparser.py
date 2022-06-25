import argparse
import io

class ArgumentError(Exception):
    pass

class F1ArgParser(argparse.ArgumentParser):
    def error(self, message: str):
        raise ArgumentError(message)

    def exit(self):
        pass

_ARG_PARSER = F1ArgParser('\\f1', add_help=False)
_SUBPARSERS = _ARG_PARSER.add_subparsers(title='commands', dest='command')

def add_command_parser(*args, **kwargs) -> argparse.ArgumentParser:
    return _SUBPARSERS.add_parser(*args, add_help=False, **kwargs)

def get() -> argparse.ArgumentParser:
    return _ARG_PARSER

def get_usage(parser: argparse.ArgumentParser) -> str:
    string_buffer = io.StringIO()
    parser.print_help(string_buffer)
    return string_buffer.getvalue()

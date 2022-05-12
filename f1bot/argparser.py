import argparse

_ARG_PARSER = argparse.ArgumentParser('f1bot')
_SUBPARSERS = _ARG_PARSER.add_subparsers(title='commands', dest='command')

def add_command_parser(*args, **kwargs) -> argparse.ArgumentParser:
    return _SUBPARSERS.add_parser(*args, **kwargs)

def get() -> argparse.ArgumentParser:
    return _ARG_PARSER

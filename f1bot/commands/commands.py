from . import teammate_delta
from . import command
import fastf1

def register_commands(*commands: command.Command) -> dict[str, command.Command]:
    return {cmd.name: cmd for cmd in commands}

COMMAND_MAP = register_commands(teammate_delta.TeammateDeltaCommand)

def init_fastf1():
    fastf1.Cache.enable_cache('.f1-cache')

def execute(args: list[str]) -> str:
    if len(args) < 1:
        return "No arguments."

    command_name = args[0]

    if command_name == 'help':
        return help()

    command = COMMAND_MAP[args[0]]
    rest = args[1:]
    if len(rest) >= 1 and rest[0] == 'help':
        return command.help

    return command.run(rest)

def help() -> str:
    text = "Available commands:\n"
    commands = list(sorted(list(COMMAND_MAP.values()), key=lambda c: c.name))
    return text + "\n".join((f"{c.name} -- {c.description}") for c in commands)
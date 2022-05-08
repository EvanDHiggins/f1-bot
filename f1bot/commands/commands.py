from . import teammate_delta
from . import session_results
from . import command
import fastf1

def register_commands(*commands: command.Command) -> dict[str, command.Command]:
    return {cmd.name: cmd for cmd in commands}

COMMAND_MAP = register_commands(
    teammate_delta.TeammateDeltaCommand,
    session_results.SessionResultsCommand,
)

def init_fastf1():
    fastf1.Cache.enable_cache('.f1-cache')

def execute(args: list[str]) -> str:
    """Looks up a command and runs it.

    Supports three forms:
        help: Prints the availabe commands and their descriptions.
        help $COMMAND: Prints the help text for $COMMAND.
        $COMMAND args...: Runs COMMAND with args.
    """
    if len(args) < 1:
        return "No arguments."

    command_name = args[0]
    rest = args[1:]

    if command_name == 'help' and len(rest) >= 1:
        return COMMAND_MAP[rest[0]].help
    elif command_name == 'help':
        return help()

    command = COMMAND_MAP[args[0]]
    if len(rest) >= 1 and rest[0] == 'help':
        return command.help

    return command.run(rest)

def help() -> str:
    text = "Available commands:\n"
    commands = list(sorted(list(COMMAND_MAP.values()), key=lambda c: c.name))
    return text + "\n".join((f"{c.name} -- {c.description}") for c in commands)

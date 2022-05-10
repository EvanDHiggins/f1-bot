from f1bot.commands import standings, teammate_delta, session_results
from f1bot.commands.command import Command, CommandResult
import fastf1

def register_commands(*commands: Command) -> dict[str, Command]:
    return {cmd.name: cmd for cmd in commands}

COMMAND_MAP = register_commands(
    teammate_delta.TeammateDeltaCommand,
    session_results.SessionResultsCommand,
    standings.StandingsCommand,
)

def execute(args: list[str]) -> CommandResult:
    """Looks up a command and runs it.

    Supports three forms:
        help: Prints the availabe commands and their descriptions.
        help $COMMAND: Prints the help text for $COMMAND.
        $COMMAND args...: Runs COMMAND with args.
    """
    if len(args) < 1:
        return CommandResult.error("No arguments.")

    command_name = args[0]
    rest = args[1:]

    if command_name == 'help' and len(rest) >= 1:
        return CommandResult.ok(COMMAND_MAP[rest[0]].help)
    elif command_name == 'help':
        return CommandResult.ok(help())

    command = COMMAND_MAP[args[0]]
    if len(rest) >= 1 and rest[0] == 'help':
        return CommandResult.ok(command.help)

    return command.run(rest)

def help() -> str:
    text = "Available commands:\n"
    commands = list(sorted(list(COMMAND_MAP.values()), key=lambda c: c.name))
    return text + "\n".join((f"{c.name} -- {c.description}") for c in commands)

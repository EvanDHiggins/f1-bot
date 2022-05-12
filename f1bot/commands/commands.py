from f1bot.commands import standings, teammate_delta, session_results
from f1bot import command as cmd
import f1bot

def register_commands(*commands: cmd.Command) -> dict[str, cmd.Command]:
    return {cmd.name: cmd for cmd in commands}

COMMAND_MAP = register_commands(
    teammate_delta.TeammateDeltaCommand,
    session_results.SessionResultsCommand,
    standings.StandingsCommand,
)

def execute(args: list[str]) -> cmd.CommandResult:
    """Looks up a command and runs it.

    Supports three forms:
        help: Prints the availabe commands and their descriptions.
        help $COMMAND: Prints the help text for $COMMAND.
        $COMMAND args...: Runs COMMAND with args.
    """
    parsed_args = f1bot.get().parse_args(args)
    command = COMMAND_MAP[parsed_args.command]
    return command.run(parsed_args)

def help() -> str:
    text = "Available commands:\n"
    commands = list(sorted(list(COMMAND_MAP.values()), key=lambda c: c.name))
    return text + "\n".join((f"{c.name} -- {c.description}") for c in commands)

from . import command

class SessionResults:
    def run(self, args: list[str]) -> str:
        return ""

SessionResultsCommand = command.Command(
    name="results",
    description="Returns the results for a session.",
    help="TODO: How will this be run?",
    get=SessionResults,
)

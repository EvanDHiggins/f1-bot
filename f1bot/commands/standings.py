from f1bot.commands.command import CommandValue
from . import command as cmd
import fastf1

HELP_MSG="""standings $YEAR"""

class Standings:
    def run(self, args: list[str]) -> CommandValue:
        return fastf1.get_event_schedule(int(args[0]))

StandingsCommand = cmd.Command(
    name="standings",
    description="Returns the driver standings for the year.",
    help=HELP_MSG,
    get=Standings,
)

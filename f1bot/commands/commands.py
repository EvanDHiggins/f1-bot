from . import teammate_delta
import fastf1

COMMAND_MAP = {
    "teammate_delta": teammate_delta.run
}

def init_fastf1():
    fastf1.Cache.enable_cache('.f1-cache')

def execute(args: list[str]):
    COMMAND_MAP[args[0]](args[1:])

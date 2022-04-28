from lib import teammate_delta
import fastf1
import sys

COMMAND_MAP = {
    "teammate_delta": teammate_delta.run
}

def main():
    fastf1.Cache.enable_cache('.f1-cache')

    COMMAND_MAP[sys.argv[1]](sys.argv[2:])

if __name__ == "__main__":
    main()

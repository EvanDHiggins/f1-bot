import sys
import f1bot
from f1bot.commands import Schedule
from f1bot import command as cmd
import pandas as pd

def main():
    f1bot.init()
    resp = cmd.run_command(sys.argv[1:]).value
    respList = resp if isinstance(resp, list) else [resp]

    # By default pandas.DataFrame.__repr__ only prints out the first and last
    # few columns if the max is above a threshold. We want to alwasy see the
    # results, though.
    with pd.option_context(
        'display.max_rows', None,
        'display.max_columns', None, 
        'display.width', None,
    ):
        for idx, v in enumerate(respList):
            if isinstance(v, pd.DataFrame):
                print(v.to_string(index=False))
            else:
                print(v)

            # Print newlines between values if there are multiple.
            if idx + 1 < len(respList):
                print('')


if __name__ == "__main__":
    main()

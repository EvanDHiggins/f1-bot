import sys
from f1bot import commands
import f1bot
import pandas as pd

def main():
    f1bot.init()
    resp = commands.execute(sys.argv[1:]).value
    respList = resp if isinstance(resp, list) else [resp]

    # By default pandas.DataFrame.__repr__ only prints out the first and last
    # few columns if the max is above a threshold. We want to alwasy see the
    # results, though.
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
        for v in respList:
            print(v)

if __name__ == "__main__":
    main()

import sys
from f1bot import commands
import f1bot

def main():
    f1bot.init()
    resp = commands.execute(sys.argv[1:]).value
    respList = resp if isinstance(resp, list) else [resp]
    for v in respList:
        print(v)

if __name__ == "__main__":
    main()

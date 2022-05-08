import sys
from f1bot import commands
import f1bot

def main():
    f1bot.init()
    print(commands.execute(sys.argv[1:]).value)

if __name__ == "__main__":
    main()

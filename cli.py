import sys
from f1bot import commands

def main():
    commands.init_fastf1()
    print(commands.execute(sys.argv[1:]).value)

if __name__ == "__main__":
    main()

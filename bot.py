import f1bot
from f1bot import command as cmd
import f1bot.commands
import os
import tabulate
from discord.ext import commands
import pandas

TOKEN = os.getenv('F1_BOT_TOKEN')

bot = commands.Bot(command_prefix='\\')

@bot.command()
async def f1(ctx, *args: str):
    """Creates f1 command to interface with the underlying CLI.

    When connected to a discord guild, can be run like:
      -- '\f1 results 2016 spain r'

    Args are passed straight through to the underlying CLI.
    """
    result = f1bot.commands.execute(list(args))
    if result.is_error():
        await ctx.send(f'{result.status.name}: {result.value}')
        return

    results = result.value if isinstance(result.value, list) else [result.value]

    for v in results:
        await ctx.send(format_command_value(v))


def format_command_value(value: cmd.CommandValue) -> str:
    if isinstance(value, pandas.DataFrame):
        tabulated = tabulate.tabulate(value, headers='keys')
        return f"```{tabulated}```"
    elif isinstance(value, str):
        return f"```{value}```"
    else:
        return f"Error, unrecognized type: {type(value)}"


def main():
    f1bot.init()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()

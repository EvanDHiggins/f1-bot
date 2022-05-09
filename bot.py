import f1bot
import f1bot.commands
import os
import tabulate
from discord.ext import commands
import pandas

TOKEN = os.getenv('F1_BOT_TOKEN')
SERVER='Bot Test Server'

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

    if isinstance(result.value, pandas.DataFrame):
        tabulated = tabulate.tabulate(result.value, headers='keys')
        await ctx.send(f"```{tabulated}```")
    elif isinstance(result.value, str):
        await ctx.send(result.value)
    else:
        await ctx.send(f"Error, unrecognized type: {type(result.value)}")

def main():
    f1bot.init()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()

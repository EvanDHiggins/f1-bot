from datetime import date
from f1bot import command as cmd

def parse_year(s: str) -> int:
    if not s.isdigit():
        raise cmd.CommandError(f"Could not parse {s} as a year.")
    year = int(s)
    if year < 1950:
        raise cmd.CommandError("F1's first race was in 1950.")
    if year > date.today().year:
        raise cmd.CommandError("That year hasn't happened yet.")
    return year

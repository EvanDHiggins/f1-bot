import pandas

def strftime(tdelta: pandas.Timedelta, fmt: str) -> str:
    """Formats a pandas.Timedelta with minutes, seconds, and milliseconds."""
    fmt_args = {}
    fmt_args["minutes"], fmt_args["seconds"] = divmod(tdelta.seconds, 60)
    fmt_args["milliseconds"] = int(tdelta.microseconds / 1000)
    return fmt.format(**fmt_args)

def format_lap_time(tdelta: pandas.Timedelta) -> str:
    if pandas.isnull(tdelta):
        return "No Time"
    return strftime(tdelta, "{minutes:02}:{seconds:02}.{milliseconds:03}")

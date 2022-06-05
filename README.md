This repo exposes commands for interacting with F1 statistics. It
exposes a series of commands through a CLI and a Discord Bot.

## Ergast DB

[Ergast](https://ergast.com/mrd) provides the historic data backing most of
the bot's functionality, but it has pretty tight API usage restrictions. Luckily,
the helpfullly provide [database dumps](https://ergast.com/mrd/db/) that we can
use instead. For the most part we only use ergast for old data, but we can
refresh it periodically with `. env/bin/activate; python init-ergast-db.py`.
This will drop, download, and rebuild the tables from Ergast.


This repo exposes commands for interacting with F1 statistics. It
exposes a series of commands through a CLI and a Discord Bot.

## Ergast DB

[Ergast](https://ergast.com/mrd) provides the historic data backing most of
the bot's functionality, but it has pretty tight API usage restrictions. Luckily,
the helpfullly provide [database dumps](https://ergast.com/mrd/db/) that we can
use instead. For the most part we only use ergast for old data, but we can
refresh it periodically with `. env/bin/activate; python init-ergast-db.py`.
This will drop, download, and rebuild the tables from Ergast.

## Installation (Linux)

1. Install Mysql/MariaDB: `sudo apt install mariadb-server`
1. Clone the repo:

`git clone https://gitub.com/evandhiggins/f1-bot.git`

1. Install numpy dependency:

`sudo apt-get install libatlas-base-dev`

1. From the git directory, setup venv:

```
python3 -m pip install --user --upgrade pip
python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate

# --no-cache-dir is basically the only way I've gotten this to work on a pi.
# Without it the process tends to get killed because of OOMs.
python3 -m pip install -r requirements.txt --no-cache-dir
```

1. Create a mysql user 'evanhiggins' with password specified by $MYSQL_PASSWORD

1. Install ergast DB: `sudo env/bin/python init-ergast-db.py`

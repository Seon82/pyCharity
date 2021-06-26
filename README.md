# pyCharity

A python port of [Mikarific's Charity bot](https://github.com/Mikarific/Charity), a discord bot with information and progress for pxls.space factions.

## Installation

This bot requires python3 (3.8.8 recommended) as well as a mongodb database to run.
### Register your discord bot
See [discord.py's documentation](https://discordpy.readthedocs.io/en/stable/discord.html) on how to create a bot application.
* Make sure both `bot` and `application.commands` scopes are selected.
* Permissions should be set to at least `3154504784`.

### Fill out the .env file
Rename `env.dist` to `.env` and fill out your application id, secret token and mongodb uri.

### Install dependencies
Run `poetry install` to install dependencies.

### Start bot
Run `python src/main.py` to start the bot.

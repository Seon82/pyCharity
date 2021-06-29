# <img alt="pyCharity" src="./src/assets/profile.png" height="50" valign="middle"> pyCharity
[![Linter Actions Status](https://github.com/Seon82/pyCharity/actions/workflows/pipeline.yml//badge.svg?branch=master)](https://github.com/Seon82/pyCharity/actions)

A discord bot with information and template tracking for pxls.space. Inspired by [Mikarific's Charity bot](https://github.com/Mikarific/Charity).

## Installation

This bot can be started using docker-compose: simply clone the repo and run `docker-compose up`. 

### Requirements
* [python3](https://www.python.org/downloads/) (3.8.8 recommended)
* [poetry](https://github.com/python-poetry/poetry)
* [mongodb](https://docs.mongodb.com/manual/administration/install-community/)

### Register your discord bot
See [discord.py's documentation](https://discordpy.readthedocs.io/en/stable/discord.html) on how to create a bot application.
* Make sure both `bot` and `application.commands` scopes are selected.
* Permissions should be set to at least `3154504784`.


### Install dependencies
Run `poetry install` to install dependencies.

### Start bot
Run `python src/main.py` to start the bot.

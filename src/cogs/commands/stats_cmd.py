from datetime import datetime
from io import BytesIO
from typing import Union, Dict
import matplotlib
import matplotlib.pyplot as plt
import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from handlers.discord_utils import UserError, attach_image
from handlers.setup import GUILD_IDS, EMBED_COLOR, stats_manager, canvas


class StatsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.plot_colors = ("#7289DA", "#fa7a90")

    @cog_ext.cog_slash(
        name="stats",
        description="Dispaly a user's palcing actvity, or compare the activity of two users.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name=f"username_{i}",
                description="Username.",
                option_type=3,
                required=i == 0,
            )
            for i in range(2)
        ],
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _stats(self, ctx: SlashContext, **usernames):
        usernames = list(usernames.values())
        records = stats_manager.get_history(usernames, canvas.code)
        history = {username: {"dates": [], "pixels": []} for username in usernames}
        record = None
        async for record in records:
            for username in usernames:
                stats = record.get(username)
                if stats is not None:
                    history[username]["dates"].append(record.time)
                    history[username]["pixels"].append(stats["pixels"])
        if record is None:
            raise UserError("Username not found.")
        # TODO support the case where a user isn't
        # present in the final record (>1k)
        description = ""
        for username in usernames:
            if len(usernames) > 1:
                description += f"**{username}**\n"
            description += (
                f"Canvas pixels: {self.format(record.get(username)['pixels'])}\n"
            )
            description += f"Canvas ranking: {record.get(username)['place']}\n"
        if len(usernames) == 1:
            title = f"{usernames[0]}'s stats"
        else:
            title = "User stats"
        embed = discord.Embed(
            title=title,
            description=description,
            color=EMBED_COLOR,
        )
        buffer = self.plot(history)
        file = attach_image(buffer, embed)
        await ctx.send(embed=embed, file=file)

    @staticmethod
    def format(number: Union[int, str]) -> str:
        """
        Formats an integer using a space as the
        thousands separator.

        :param number: An integer or its string representation.
        """
        return format(int(number), "_").replace("_", " ")

    def plot(self, history=Dict[str, Dict[str, Union[int, datetime]]]) -> BytesIO:
        """
        Generate a pixel placing plot, render it and
        return the image binary data.
        """
        # Plot
        fig, ax = plt.subplots()
        for i, user_stats in enumerate(history.values()):
            dates, pixels = user_stats["dates"], user_stats["pixels"]
            ax.plot_date(dates, pixels, "-", color=self.plot_colors[i])
        usernames = history.keys()
        # Setup legend if necessary
        if len(usernames) > 1:
            legend = ax.legend(
                usernames,
                edgecolor=(0.18, 0.19, 0.21, 1.0),
                facecolor=(0.18, 0.19, 0.21, 1.0),
            )
            plt.setp(legend.get_texts(), color="white")
        # Plot styling
        fig.autofmt_xdate()
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, _: self.format(x))
        )
        ax.grid(axis="y", alpha=0.8)
        ax.spines["bottom"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.xaxis.label.set_color("white")
        ax.yaxis.set_tick_params(length=0)
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        buffer = BytesIO()
        plt.savefig(buffer, transparent=True)
        buffer.seek(0)
        return buffer


def setup(bot):
    bot.add_cog(StatsCommand(bot))

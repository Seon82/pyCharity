from io import BytesIO
from typing import Union
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

    @cog_ext.cog_slash(
        name="stats",
        description="See a user's placing stats.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="username",
                description="Username.",
                option_type=3,
                required=True,
            )
        ],
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _stats(self, ctx: SlashContext, username: str):
        history = stats_manager.get_history(username, canvas.code)
        dates, placed_pixels = [], []
        stats = None
        async for stats in history:
            placed_pixels.append(stats.get(username)["pixels"])
            dates.append(stats.time)
        if stats is None:
            raise UserError(f"`{username}` not found.")
        description = f"Canvas pixels: {self.format(stats.get(username)['pixels'])}\n"
        description += f"Canvas ranking: {stats.get(username)['place']}\n"
        embed = discord.Embed(
            title=f"{username}'s stats",
            description=description,
            color=EMBED_COLOR,
        )
        buffer = self.plot(dates, placed_pixels)
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

    def plot(self, dates: list, pixels: list) -> BytesIO:
        """
        Generate a pixel placing plot, render it and
        return the image binary data.
        """
        fig, ax = plt.subplots()
        ax.plot_date(dates, pixels, "-", color="#7289DA")
        fig.autofmt_xdate()
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, _: self.format(x))
        )
        ax.grid(axis="y")
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

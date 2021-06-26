import discord
from discord.ext import commands
from handlers.discord_utils import UserError


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready!")

    @commands.Cog.listener()
    async def on_slash_command_error(ctx, error):
        """Error message handler."""
        unexpected = False
        title = "❌ Error"
        if isinstance(error, UserError):
            description = error.args[0]
        elif isinstance(error, commands.errors.CommandOnCooldown):
            description = f"This command is on cooldown. Please try again in `{error.retry_after:.2f}s`."
        else:
            unexpected = True
            description = (
                "An unexpected error occured. Please contact the bot developer."
            )
        embed = discord.Embed(title=title, description=description, color=0xCC0000)
        await ctx.send(embed=embed)
        if unexpected:
            raise error


def setup(bot):
    bot.add_cog(Events(bot))

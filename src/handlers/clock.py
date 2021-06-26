from discord.ext import tasks, commands
from main import canvas


class Clock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_board.start()

    def cog_unload(self):
        self.update_board.cancel()

    @tasks.loop(minutes=2)
    async def update_board(self):
        try:
            canvas.board = await canvas.fetch_board()
            print("Board updated.")
        except Exception as e:
            print("Error while fetching board.", e)

    @update_board.before_loop
    async def before(self):
        print("Clock is waiting...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Clock(bot))

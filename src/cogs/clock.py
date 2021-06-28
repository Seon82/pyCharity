import logging
from discord.ext import tasks, commands
from handlers.setup import canvas, ws_client

logger = logging.getLogger("pyCharity." + __name__)


class Clock(commands.Cog):
    """
    A class used to manage background periodic tasks.
    Is used to update the canvas object periodically.
    """

    def __init__(self, bot):
        self.bot = bot
        self.update_board.start()

    def cog_unload(self):
        self.update_board.cancel()

    @tasks.loop(minutes=5)
    async def update_board(self):
        """Update the canvas info periodically."""
        try:
            await canvas.update_info()
            ws_client.pause()
            board = await canvas.fetch_board()
            canvas.board = board
            logger.debug("Board updated.")
            ws_client.resume()
        except Exception as e:
            logger.warning("Error while fetching board.", e)

    @update_board.before_loop
    async def before(self):
        logger.debug("Clock is waiting...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Clock(bot))

import logging
from discord.ext import tasks, commands
from handlers.pxls import compute_progress, Template, layer
from handlers.setup import canvas, ws_client, template_manager, base_url

logger = logging.getLogger("pyCharity." + __name__)


class Clock(commands.Cog):
    """
    A class used to manage background periodic tasks.
    Is used to update the canvas object periodically.
    """

    def __init__(self, bot):
        self.bot = bot
        # pylint: disable = no-member
        self.update_board.start()

    def cog_unload(self):
        # pylint: disable = no-member
        self.update_board.cancel()

    @tasks.loop(minutes=5)
    async def update_board(self):
        """Update the canvas info and template progress periodically."""
        # Update canvas
        try:
            await canvas.update_info()
            ws_client.pause()
            board = await canvas.fetch_board()
            canvas.board = board
            logger.debug("Board updated.")
            ws_client.resume()
        except Exception as error:
            logger.warning(f"Error while fetching board: {error}")
        # Update progress
        try:
            templates = template_manager.get_templates(
                canvas_code=canvas.info["canvasCode"]
            )
            async for template in templates:
                new_progress = await compute_progress(canvas, template)
                await template_manager.update_template(
                    template, data={"progress": new_progress.to_dict()}
                )
            logger.debug("Updated template progress.")
        except Exception as error:
            logger.warning(f"Error while updating template progress: {error}")
        # Generate combo
        try:
            combo, combo_exists = None, False
            templates = template_manager.get_templates(
                canvas_code=canvas.info["canvasCode"], scope={"$ne": "private"}
            )
            async for template in templates:
                if combo is None:
                    combo = template
                elif template.name == "combo":
                    combo_exists = True
                else:
                    combo = await layer(
                        canvas.board.width, canvas.board.height, combo, template
                    )
            if not combo is None:
                owner = self.bot.user.id
                combo = await Template.from_base(
                    base_template=combo,
                    name="combo",
                    url=base_url,
                    owner=owner,
                    canvas=canvas,
                    scope="global",
                )
                if combo_exists:
                    await template_manager.update_template(combo)
                else:
                    await template_manager.add_template(combo)
                logger.debug("Generated combo.")
        except Exception as error:
            logger.warning(f"Error while generating combo: {error}")

    @update_board.before_loop
    async def before(self):
        """Run before main loop is started."""
        logger.debug("Clock is waiting...")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Clock(bot))

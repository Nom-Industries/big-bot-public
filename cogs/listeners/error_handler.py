from cooldowns import CallableOnCooldown
import nextcord
import time
from nextcord.ext import commands
from nextcord.errors import Forbidden
from bot.bot import Bot

class Error_Handler(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_application_command_error(self, inter: nextcord.Interaction, error):
        error = getattr(error, "original", error)
        if isinstance(error, CallableOnCooldown):
            await inter.send(f"That command is on cooldown. You can use it again <t:{int(error.retry_after) + round(int(time.time()))}:R>")
        elif isinstance(error, Forbidden):
            await inter.send(f"I don't have permission to do that")
        else:
            raise error


def setup(client: Bot):
    client.add_cog(cog=Error_Handler(client=client))
from asyncio import tasks
from venv import create
import nextcord, pymysql
from nextcord.ext import commands
from bot.bot import Bot
from utils.utils import color_message
from views import List_Options
from constants import COOKIE, DBENDPOINT, DBPORT, DBUSER, DBPASS, DBNAME
from typing import List, Union
from utils import create_error_embed, create_success_embed


class WarningAppView(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Warn Member", timeout=None)

        self.reason = nextcord.ui.TextInput(
                label = "Reason",
                placeholder = "Reason for the warning",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=256,
                required=False
            )
        self.add_item(self.reason)

        self.evidence = nextcord.ui.TextInput(
                label = "Evidence",
                placeholder = "Evidence for the timeout",
                style=nextcord.TextInputStyle.paragraph,
                required=False
            )
        self.add_item(self.evidence)

    async def callback(self, interaction: nextcord.Interaction):
        self.reason = self.reason.value
        self.stop()
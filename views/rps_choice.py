import re
from typing import List
import nextcord
from nextcord import Interaction
from constants import NEXTCORD_PERM_LABELS, NEXTCORD_PERM_VALUES, BACKSLASH, RPS_CHOICES
from io import BytesIO
import json
import requests
from PIL import Image


class Rock_Paper_Scissors_Choice(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.values = []

    @nextcord.ui.select(placeholder="Make your choice", options=[nextcord.SelectOption(label=RPS_CHOICES[i], value=RPS_CHOICES[i]) for i in range(0, 3)], max_values=1)
    async def rps_choose(self, select: nextcord.ui.Select, interaction: Interaction):
        self.values.extend(select.values)
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green)
    async def submit(self, button: nextcord.ui.Button, interaction: Interaction):
        if len(self.values) == 0:
            await interaction.send("You need to select an option", ephemeral=True)
        else:
            self.values = [*set(self.values)]
            self.stop()
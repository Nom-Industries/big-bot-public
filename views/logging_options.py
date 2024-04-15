from typing import List
import nextcord
from nextcord import Interaction
from constants import LOGGING_TYPES_LABELS, LOGGING_TYPES_VALUES


class Toggle_Logs_View(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.values = []
        self.labels = []


    @nextcord.ui.select(placeholder="Toggle Logs", options=[nextcord.SelectOption(label=LOGGING_TYPES_LABELS[i], value=LOGGING_TYPES_VALUES[i]) for i in range(0, 7)], max_values=7)
    async def choose_logs(self, select: nextcord.ui.Select, interaction: Interaction):
        self.values.extend(select.values)
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green)
    async def submit(self, button: nextcord.ui.Button, interaction: Interaction):
        self.values = [*set(self.values)]
        self.stop()
    @nextcord.ui.button(label="Select All", style=nextcord.ButtonStyle.blurple)
    async def select_all(self, button: nextcord.ui.Button, interaction: Interaction):
        self.values=LOGGING_TYPES_VALUES
        self.stop()
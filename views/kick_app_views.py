import nextcord
from typing import List, Union


class KickAppView(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Kick Member", timeout=None)

        self.reason = nextcord.ui.TextInput(
                label = "Reason",
                placeholder = "Reason for the kick",
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
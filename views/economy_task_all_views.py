import nextcord
from utils import *
from typing import List, Union

class TaskButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = False

    @nextcord.ui.button(label = "Run next command", style = nextcord.ButtonStyle.blurple, disabled=False)
    async def run_cmd(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        self.stop()

        self.clear_items()
    
    @nextcord.ui.button(label="Skip Command", style=nextcord.ButtonStyle.grey, disabled=False)
    async def skip_cmd(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value=None
        self.stop()

        self.clear_items()

    @nextcord.ui.button(label="End task", style = nextcord.ButtonStyle.red, disabled=False)
    async def end_task(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        self.stop()

        self.clear_items()

    async def on_timeout(self):
        self.value=False
        self.stop()
        self.clear_items()

class RedoTask(nextcord.ui.View):
    def __init__(self, org_user:int):
        super().__init__(timeout=21600)
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Start task again", style = nextcord.ButtonStyle.blurple, disabled=False)
    async def redo_task(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value= True
        self.info = interaction
        self.stop()

        self.clear_items()

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True
    
    async def on_timeout(self):
        self.value=False
        self.stop()
        self.clear_items()

        
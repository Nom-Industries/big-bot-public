import nextcord

class FishEnabled(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=2)
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Catch!", style = nextcord.ButtonStyle.green, disabled=False)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        self.stop()
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.value=False
        self.stop()

class FishDisabled(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__()
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Catch!", style = nextcord.ButtonStyle.green, disabled=True)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        self.stop()

        self.clear_items()
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.stop()
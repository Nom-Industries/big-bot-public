import nextcord

class HigherOrLower(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=60)
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Lower", style = nextcord.ButtonStyle.blurple, disabled=False, row=1)
    async def higher(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "lower"
        self.stop()
    @nextcord.ui.button(label = "Spot On!", style = nextcord.ButtonStyle.blurple, disabled=False, row=1)
    async def spot_on(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "spot"
        self.stop()
    @nextcord.ui.button(label = "Higher", style = nextcord.ButtonStyle.blurple, disabled=False, row=1)
    async def lower(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "higher"
        self.stop()

    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.value=None
        self.stop()
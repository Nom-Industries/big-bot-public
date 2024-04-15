import nextcord

class Confirm(nextcord.ui.View):
    def __init__(self, org_user: int=0):
        super().__init__(timeout=600)
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Yes", emoji = "<:Check:779247977721495573>", style = nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        self.stop()

        self.clear_items()
    
    @nextcord.ui.button(label = "No", emoji = "<:Cross:779247977843523594>", style = nextcord.ButtonStyle.red)
    async def deny(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        self.stop()

        self.clear_items()
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.org_user == 0:
            return True
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.stop()
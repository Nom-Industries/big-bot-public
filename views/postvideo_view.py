import nextcord

class PostVideoChoice(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=60)
        self.value = "Not Given"
        self.org_user = org_user

    @nextcord.ui.button(label = "Gaming", style = nextcord.ButtonStyle.green, disabled=False)
    async def gaming(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Gaming"
        self.stop()
    @nextcord.ui.button(label = "Debate", style = nextcord.ButtonStyle.green, disabled=False)
    async def debate(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Debate"
        self.stop()
    @nextcord.ui.button(label = "Educational", style = nextcord.ButtonStyle.green, disabled=False)
    async def educational(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Educational"
        self.stop()
    @nextcord.ui.button(label = "Meme", style = nextcord.ButtonStyle.green, disabled=False)
    async def meme(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Meme"
        self.stop()
    @nextcord.ui.button(label = "Music", style = nextcord.ButtonStyle.green, disabled=False)
    async def music(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Music"
        self.stop()

    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.value="Not Given"
        self.stop()
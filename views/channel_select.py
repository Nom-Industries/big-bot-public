import nextcord

class ChannelList(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(custom_id="test", placeholder="Select a channel", min_values=0, max_values=25, channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.voice,nextcord.ChannelType.news])

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values = self.values
        self.view.stop()

class ChannelSelect(nextcord.ui.View):
    def __init__(self, org_user:int):
        super().__init__(timeout=30)
        self.add_item(ChannelList())
        self.values = []
        self.choice = None
        self.org_user = org_user

    @nextcord.ui.button(label="Finish", style=nextcord.ButtonStyle.green)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True
import nextcord

class MemberCount_View(nextcord.ui.View):

    def __init__(self, members, humans, bots):
        super().__init__()
        self.add_item(nextcord.ui.Button(label=f"Members: {members:,}", style = nextcord.ButtonStyle.blurple, disabled=False))
        self.add_item(nextcord.ui.Button(label=f"Humans: {humans:,}", style = nextcord.ButtonStyle.blurple, disabled=False))
        self.add_item(nextcord.ui.Button(label=f"Bots: {bots:,}", style = nextcord.ButtonStyle.blurple, disabled=False))
    
    @staticmethod
    async def callback(interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=False)
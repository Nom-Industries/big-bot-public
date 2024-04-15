import nextcord

class UnlockView(nextcord.ui.View):
    def __init__(self, channel, org_user:int):
        super().__init__()
        self.org_user = org_user
        self.channel = channel

    @nextcord.ui.button(label="Unlock Channel", style=nextcord.ButtonStyle.danger)
    async def unlock_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=False)
        channel = interaction.guild.get_channel(self.channel)
        role = interaction.guild.roles[0]
        await channel.set_permissions(role, send_messages=None)
        await interaction.edit_original_message(content=f"Successfully unlocked {channel.mention}", view=LockView(channel.id, self.org_user))

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

class LockView(nextcord.ui.View):
    def __init__(self, channel, org_user:int):
        super().__init__()
        self.org_user = org_user
        self.channel = channel

    @nextcord.ui.button(label="Lock Channel", style=nextcord.ButtonStyle.danger)
    async def unlock_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=False)
        channel = interaction.guild.get_channel(self.channel)
        role = interaction.guild.roles[0]
        await channel.set_permissions(role, send_messages=False)
        await interaction.edit_original_message(content=f"Successfully locked {channel.mention}", view=UnlockView(channel.id, self.org_user))

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

        
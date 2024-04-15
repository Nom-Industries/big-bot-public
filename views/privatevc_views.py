import nextcord
from typing import List, Union
from utils import create_error_embed, create_success_embed

class List_Select_Private_VCs(nextcord.ui.Select):
    def __init__(self, options: List[str], placeholder: str = "Select an option", max_values: int = 1):
        super().__init__(options=[nextcord.SelectOption(label=i, description=i) for i in options], placeholder=placeholder, max_values=max_values)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)

class List_Options_Private_VCs(nextcord.ui.View):
    def __init__(self, options: List[str], placeholder: str = "Select an option", max_values: int = 1):
        super().__init__(timeout=120)
        self.values = []
        for i in range(0, len(options), 25):
            self.add_item(List_Select_Private_VCs(options=options[i:i+25], placeholder=placeholder, max_values=max_values))
    
    @nextcord.ui.button(label="Complete", style=nextcord.ButtonStyle.green, row=1)
    async def complete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()

class RequestToJoinView(nextcord.ui.View):
    def __init__(self, channelid, memberid, ownerid, vcid):
        super().__init__(timeout=None)
        self.channelid = channelid
        self.memberid = memberid
        self.ownerid = ownerid
        self.vcid = vcid
        
    @nextcord.ui.button(label="Accept", style=nextcord.ButtonStyle.green, row=1)
    async def accept(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not interaction.user.id == int(self.ownerid):
            await interaction.response.defer(with_message=False)
        else:
            channel = interaction.guild.get_channel(int(self.channelid))
            member = interaction.guild.get_member(int(self.memberid))
            vc = interaction.guild.get_channel(int(self.vcid))
            try:
                if member in channel.members:
                    await member.move_to(vc)
                    await interaction.edit(embed=create_success_embed(title="Success!", description=f"I have successfully moved {member.mention} into the VC"), view=None)
                else:
                    await interaction.edit(embed=create_error_embed(title="Error!", description="Failed to move member to channel."), view=None)
            except:
                await interaction.edit(embed=create_error_embed(title="Error!", description="Failed to move member to channel."), view=None)
    @nextcord.ui.button(label="Deny", style=nextcord.ButtonStyle.green, row=1)
    async def deny(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not interaction.user.id == int(self.ownerid):
            await interaction.response.defer(with_message=False)
        else:
            channel = interaction.guild.get_channel(int(self.channelid))
            member = interaction.guild.get_member(int(self.memberid))
            vc = interaction.guild.get_channel(int(self.vcid))
            try:
                if member in channel.members:
                    await member.move_to(None)
            except:
                pass
            await interaction.edit(embed=create_success_embed(title="Success!", description=f"I have denied {member.mention}'s request to join your VC"), view=None)

    @nextcord.ui.button(label="Deny + Block", style=nextcord.ButtonStyle.green, row=1)
    async def deny_block(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not interaction.user.id == int(self.ownerid):
            await interaction.response.defer(with_message=False)
        else:
            channel = interaction.guild.get_channel(int(self.channelid))
            member = interaction.guild.get_member(int(self.memberid))
            vc = interaction.guild.get_channel(int(self.vcid))
            try:
                if member in channel.members:
                    await member.move_to(None)
            except:
                pass
            await channel.set_permissions(member, connect=False)
            await interaction.edit(embed=create_success_embed(title="Success!", description=f"I have denied {member.mention}'s request to join your VC"), view=None)

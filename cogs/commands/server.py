import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from constants import COLOUR_MAIN
from views.membercount_buttons import MemberCount_View
from bot import Bot
from utils import *

class Server(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @nextcord.slash_command(name="serverinfo", description="Gives information about the server")
    async def serverinfo(self, interaction: Interaction):
        await interaction.response.defer()

        embed = nextcord.Embed(colour=COLOUR_MAIN)
        embed.add_field(name="Owner", value=f"{interaction.guild.owner}")
        embed.add_field(name="Total Members", value=str(interaction.guild.member_count))
        embed.add_field(name="Creation Date", value=f"<t:{round(interaction.guild.created_at.timestamp())}>")
        role_list = interaction.guild.roles
        if len(interaction.guild.roles) > 25:
            role_list = interaction.guild.roles[-25:]
        embed.add_field(name=f"Roles ({len(interaction.guild.roles[1:])})", value=(', '.join([i.mention for i in role_list[:0:-1]]))[0:1000], inline=False)
        
        if interaction.guild.icon:
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
            embed.set_thumbnail(url=interaction.guild.icon)

        await interaction.send(embed=embed)


    @nextcord.slash_command(name="membercount", description="Find out the member count")
    async def membercount(self, interaction: Interaction):
        await interaction.response.defer()
        await interaction.send(view=MemberCount_View(len(interaction.guild.members), (len(interaction.guild.members)-len(interaction.guild.bots)), len(interaction.guild.bots)))

    

def setup(client):
    client.add_cog(cog=Server(client=client))
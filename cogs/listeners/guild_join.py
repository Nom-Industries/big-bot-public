import nextcord
from nextcord.ext import commands
from bot.bot import Bot
from constants import COLOUR_GOOD, COLOUR_BAD

class GuildJoin(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        supguild = self.client.get_guild(1015361041024155770)
        channel =  supguild.get_channel(1015364659299225713)
        embed = nextcord.Embed(title=f"Joined Guild", colour=COLOUR_GOOD)
        embed.add_field(name=f"Guild Name (ID)", value=f"{guild.name} ({guild.id})")
        embed.add_field(name=f"Guild Owner", value=f"{guild.owner} (<@{guild.owner.id}>)")
        embed.add_field(name=f"Guild Members", value=f"{len(guild.members)}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        supguild = self.client.get_guild(1015361041024155770)
        channel =  supguild.get_channel(1015364659299225713)
        embed = nextcord.Embed(title=f"Left Guild", colour=COLOUR_BAD)
        embed.add_field(name=f"Guild Name (ID)", value=f"{guild.name} ({guild.id})")
        embed.add_field(name=f"Guild Owner", value=f"{guild.owner} (<@{guild.owner.id}>)")
        embed.add_field(name=f"Guild Members", value=f"{len(guild.members)}")
        await channel.send(embed=embed)


def setup(client: Bot):
    client.add_cog(cog=GuildJoin(client=client))
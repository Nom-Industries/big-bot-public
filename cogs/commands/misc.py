import nextcord, asyncio
from nextcord import Interaction
from nextcord.ext import commands, tasks
from bot import Bot
from utils import *
import time
import cooldowns
import requests
from views import BotInfoLinkButton, PrivacyPolicyButton
from views.ping_view import PingView, PingRetry
from constants import COLOUR_MAIN, VOTELINK

class Misc(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="botinfo", description="Information about the bot")
    async def botinfo(self, interaction: Interaction):
        await interaction.response.defer()
        before = time.monotonic()
        msg = await interaction.send("Loading bot information")
        ping = (time.monotonic() - before) * 1000
        users = 0
        for guild in self.client.guilds:
            users+=guild.member_count
        embed = nextcord.Embed(title="Bot Infomation", description=f"""Ping: {round(ping)}ms
Server count: {str(len(self.client.guilds))}
User count: {users:,}
Support Server: [Need some support?](https://discord.gg/WjdMjUnBvJ)
Invite: [Invite Me](https://discord.com/api/oauth2/authorize?client_id=1016198853306884126&permissions=8&scope=applications.commands%20bot)
Vote: [Vote for me]({VOTELINK})
Privacy: [Privacy Policy](https://nomindustries.com/BigBot/privacy)""", colour=COLOUR_MAIN)
        await msg.edit(content = " ", embed=embed, view=BotInfoLinkButton())
    
    @nextcord.slash_command(name="ping", description="Get the bot's ping")
    async def ping(self, interaction: Interaction):
        msg = await interaction.send("Checking Ping")
        before = time.monotonic()
        await msg.edit("Checking Ping!")
        ping = round(((time.monotonic() - before) * 1000),2)
        await msg.edit(content=None, view=PingView(ping))
        await asyncio.sleep(5)
        await msg.edit(content=None, view=PingRetry(ping))

    @nextcord.slash_command(name="privacy", description=f"Get the link to our privacy policy")
    async def privacy_policy(self, ctx:Interaction):
        embed = nextcord.Embed(title="Privacy Policy", description="You can find our privacy policy here: \n\nhttps://nomindustries.com/BigBot/privacy", colour=COLOUR_MAIN)
        await ctx.send(embed=embed, view=PrivacyPolicyButton())


    @nextcord.slash_command(name=f"shardinfo", description=f"Get information on all shards")
    @cooldowns.cooldown(1, 30, bucket=cooldowns.SlashBucket.author)
    async def shardinfo(self, interaction:Interaction):
        await interaction.response.defer()
        description = ""
        for shard in self.client.shards:
            specshard = self.client.get_shard(shard)
            shard_servers = len([guild for guild in self.client.guilds if guild.shard_id == shard])
            description+=f"\n**Shard {shard+1}** has `{round(specshard.latency*100)}ms` latency with `{shard_servers} servers`"

        if not interaction.guild:
            await interaction.send(embed=nextcord.Embed(title=f"BigBot Shard Information", description=f"All current shards:\n {description}", colour=COLOUR_MAIN))
        else:
            guild_shard = interaction.guild.shard_id
            guildspecshard = self.client.get_shard(guild_shard)
            guild_shard_servers = len([guild for guild in self.client.guilds if guild.shard_id == guild_shard])
            await interaction.send(f"This server's shard is shard **{guild_shard+1}** with `{round(guildspecshard.latency*100)}ms` and `{guild_shard_servers} servers`", embed=nextcord.Embed(title=f"BigBot Shard Information", description=f"All current shards:\n {description}", colour=COLOUR_MAIN))


    @tasks.loop(minutes=5)
    async def topgg_update_loop(self):  
        r = requests.post(url="https://top.gg/api/bots/1016198853306884126/stats", json={"server_count": self.client.guilds, "shard_count":len(self.client.shards)}, headers={"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEwMTYxOTg4NTMzMDY4ODQxMjYiLCJib3QiOnRydWUsImlhdCI6MTY2NzY0NTQyMX0.DQtRABqXrcibGoQVkOo2IfWiHTaKfPzkD4mpLdMwOVc"})
        print(r)


def setup(client: Bot):
    client.add_cog(cog=Misc(client=client))

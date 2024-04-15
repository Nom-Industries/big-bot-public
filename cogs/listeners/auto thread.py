import nextcord
from nextcord.ext import commands
from bot.bot import Bot
from utils.utils import *
from db_handler.schemas import *
from typing import List, Union
from views import AutoThreadView, AutoThreadInfoView

class Threads(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="autothread", description="autothread base command")
    async def autothread(self, interaction: nextcord.Interaction):
        pass

    
    @autothread.subcommand(name="config", description="Configure your autothread settings")
    async def autothread_config(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        data: List[AutoThreadMain] = Bot.db.get_data(table="autothread", guild_id=interaction.guild.id)
        showedit = True
        showcreate = True
        if not data:
            content = "You don't currently have any autothreads on this server. Use the Add Autothread button to add one"
            showedit = False
        else:
            content = f"You currently have `{len(data)}` autothread(s)"
            if len(data) >= 3:
                showcreate = False
        embed=nextcord.Embed(title="Auto Thread", description=f"{content}", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=AutoThreadView(showcreate=showcreate, showedit=showedit, org_user=interaction.user.id, client=self.client))


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        data: List[AutoThreadMain] = Bot.db.get_data(table="autothread", guild_id=message.guild.id, channel_id=message.channel.id)
        if data:
            thread = await message.channel.create_thread(name=f"autothread-{message.author.name}", message=message, auto_archive_duration=10080)
            await thread.send(content=f"Automatically created thread.", view=AutoThreadInfoView())


def setup(client: Bot):
    client.add_cog(Threads(client))
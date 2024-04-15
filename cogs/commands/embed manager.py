from typing import List
import nextcord
import aiohttp
from nextcord import SlashOption
from nextcord.ext import commands
from nextcord.abc import GuildChannel
from bot.bot import Bot
from utils.utils import create_success_embed, create_warning_embed
from views import EmbedCreationForm
from constants import COLOUR_NEUTRAL

class EmbedManager(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="embed", description="Embed manager base")
    async def embed(self, interaction: nextcord.Interaction):
        pass
    @embed.subcommand(name="manager", description="Embed manager base")
    async def embed_manager(self, interaction: nextcord.Interaction):
        pass
    

    @embed_manager.subcommand(name="send", description="Send a custom embed to a channel")
    async def embed_manager_send(self,
        interaction: nextcord.Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="Channel to send the embed to",
            channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.news],
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        options = EmbedCreationForm(type=type)
        await interaction.response.send_modal(modal=options)
        await options.wait()
        embed = nextcord.Embed(description="Loading...", colour=COLOUR_NEUTRAL)
        msg = await interaction.send(embed=embed, ephemeral=True)
        embed = nextcord.Embed(title=options.embedtitle, description=options.embeddescription)
        if options.embedauthor:
            embed.set_author(name=options.embedauthor, icon_url=interaction.guild.icon.url if interaction.guild.icon else None, url=options.embedauthorurl if options.embedauthorurl else None)
        webhook = await channel.create_webhook(name=options.name, avatar=interaction.guild.icon if interaction.guild.icon else None, reason=f"Embed created by {interaction.user}")
        async with aiohttp.ClientSession() as session:
            webhookmsg = nextcord.Webhook.from_url(webhook.url, session=(session))
            await webhookmsg.send(embed=embed)
        await webhook.delete(reason=f"Embed created by {interaction.user}")
        await msg.edit(embed=create_success_embed(title="Success!", description=f"Successfully created embed and sent it to {channel.mention}"))
        

def setup(client: Bot):
    client.add_cog(EmbedManager(client))

from asyncio import tasks
import nextcord, asyncio
from nextcord.ext import commands, tasks
from nextcord import Interaction, SlashOption
from typing import List
from db_handler.schemas import *
from bot.bot import Bot
from utils.utils import create_success_embed, create_error_embed, create_warning_embed
from constants import COLOUR_MAIN

first = False

class ServerStatistics(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.update_stat_channels.start()

    @nextcord.slash_command(name="statistic", description="Statistic Channel base")
    async def statistic(self, interaction: Interaction):
        pass
    @statistic.subcommand(name="channel", description=f"Statistic Channel base")
    async def statistic_channel(self, interaction: Interaction):
        pass
    
    @statistic_channel.subcommand(name="possible", description="List of valid counter channels")
    async def statistic_channel_possible(self, interaction:Interaction):
        await interaction.send(embed=nextcord.Embed(title="Valid counter channels", description=f"Members (bots + humans)\nMembers (Humans Only)\nMembers (Bots Only)\nChannels (All excluding categories)\nChannels (Text only)\nChannels (Voice only)\nChannels (Categories only)\nRoles\nEmojis\nBoosts\nMembers (Online humans + bots)\nMembers (Online Humans)\nMembers (DND humans + bots)\nMembers (DND humans)\nMembers (idle humans + bots)\nMembers (idle humans)\nMembers (Offline humans + bots)\nMembers (Offline humans)", colour=COLOUR_MAIN))

    @statistic_channel.subcommand(name="create", description="Create a statistic counter channel")
    async def statistic_channel_create(self,
        interaction:Interaction,
        counter_type: str = SlashOption(
            name="type",
            description="The type of counter to create (Use /statistic channel list to see all available counter types)",
            required=True,
            choices={"Members (bots + humans)":"members_total", "Members (Humans Only)":"members_humans", "Members (Bots Only)":"members_bots", "Channels (All excluding categories)":"channels_all", "Channels (Text only)":"channels_text", "Channels (Voice only)":"channels_voice", "Channels (Categories only)":"channels_category", "Roles":"roles", "Emojis":"emojis", "Boosts":"boosts", "Members (Online humans + bots)":"members_online_total", "Members (Online Humans)":"members_online_humans", "Members (DND humans + bots)":"members_dnd_total", "Members (DND humans)":"members_dnd_humans", "Members (idle humans + bots)":"members_idle_total", "Members (idle humans)":"members_idle_humans", "Members (Offline humans + bots)":"members_offline_total", "Members (Offline humans)":"members_offline_humans"}
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        data: List[ServerstatsMain] = Bot.db.get_data(table="serverstats", guild_id=interaction.guild.id)
        if data:
            if len(data) == 5:
                await interaction.send(embed=create_error_embed(title="Max channels reached", description=f"You are only allowed a maximum of 5 statistic channels at one time. Use `/statistics channel remove` to remove some"))
                return
        await interaction.response.defer()
        channel = await interaction.guild.create_voice_channel("Loading...")
        Bot.db.create_data(table="serverstats", guild_id=interaction.guild.id, channel_id=channel.id, type=counter_type)
        await asyncio.sleep(0.5)
        if counter_type == "members_total":
            await channel.edit(name=f"All Members: {len(interaction.guild.members)}")
        elif counter_type == "members_humans":
            await channel.edit(name=f"All Humans: {len(interaction.guild.members) - len(interaction.guild.bots)}")
        elif counter_type == "members_bots":
            await channel.edit(name=f"All Bots: {len(interaction.guild.bots)}")
        elif counter_type == "channels_all":
            await channel.edit(name=f"All Channels: {len(interaction.guild.channels) - len(interaction.guild.categories)}")
        elif counter_type == "channels_text":
            await channel.edit(name=f"Text Channels: {len(interaction.guild.text_channels)}")
        elif counter_type == "channels_voice":
            await channel.edit(name=f"Voice Channels: {len(interaction.guild.voice_channels)}")
        elif counter_type == "channels_category":
            await channel.edit(name=f"Categories: {len(interaction.guild.categories)}")
        elif counter_type == "roles":
            await channel.edit(name=f"Roles: {len(interaction.guild.roles)}")
        elif counter_type == "emojis":
            await channel.edit(name=f"Emojis: {len(interaction.guild.emojis)}")
        elif counter_type == "boosts":
            await channel.edit(name=f"Boosts: {interaction.guild.premium_subscription_count}")
        elif counter_type == "members_online_total":
            amount = 0
            for member in interaction.guild.members:
                if member.status != "offline":
                    amount+=1
            await channel.edit(name=f"Online Members: {amount}")
        elif counter_type == "members_online_humans":
            amount = 0
            for member in interaction.guild.members:
                if member.status != "offline" and not member.bot:
                    amount+=1
            await channel.edit(name=f"Online Humans: {amount}")
        elif counter_type == "members_dnd_total":
            amount = 0
            for member in interaction.guild.members:
                if member.status.dnd:
                    amount+=1
            await channel.edit(name=f"DND Members: {amount}")
        elif counter_type == "members_dnd_humans":
            amount = 0
            for member in interaction.guild.members:
                if member.status.dnd and not member.bot:
                    amount+=1
            await channel.edit(name=f"DND Humans: {amount}")
        elif counter_type == "members_idle_total":
            amount = 0
            for member in interaction.guild.members:
                if member.status.idle:
                    amount+=1
            await channel.edit(name=f"Idle Members: {amount}")
        elif counter_type == "members_idle_humans":
            amount = 0
            for member in interaction.guild.members:
                if member.status.idle and not member.bot:
                    amount+=1
            await channel.edit(name=f"Idle Humans: {amount}")
        elif counter_type == "members_offline_total":
            amount = 0
            for member in interaction.guild.members:
                if member.status.offline:
                    amount+=1
            await channel.edit(name=f"Offline Members: {amount}")
        elif counter_type == "members_offline_humans":
            amount = 0
            for member in interaction.guild.members:
                if member.status.offline and not member.bot:
                    amount+=1
            await channel.edit(name=f"Offline Humans: {amount}")
        await interaction.send(embed=create_success_embed(title=f"Statistic Channel Created", description=f"I have created a statistic channel ({channel.mention})."))

    @statistic_channel.subcommand(name="remove", description="Remove a statistic counter channel")
    async def statistic_channel_remove(self,
        interaction:Interaction,
        channelid: str = SlashOption(
            name="channelid",
            description="The ID of the channel you want to remove. (You can get this via /statistic channel list)",
            required=True,
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer()
        data: List[ServerstatsMain] = Bot.db.get_data(table="serverstats", guild_id=interaction.guild.id, channel_id=channelid)
        if not data:
            await interaction.send(embed=create_error_embed(title=f"Not a statistic channel", description=f"That channel is not one of your statistic channel IDs. You can get a list of your current statistics channels with `/statistic channel list`."))
            return
        Bot.db.delete_data(table="serverstats", data=data[0])
        await interaction.send(embed=create_success_embed(title=f"Channel Removed", description=f"The channel has been removed as a statistic channel."))
        try:
            channel = interaction.guild.get_channel(int(channelid))
            await channel.delete()
        except:
            pass

    @statistic_channel.subcommand(name="list", description="List your current statistic counter channels")
    async def statistic_channel_list(self,
        interaction:Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer()
        data: List[ServerstatsMain] = Bot.db.get_data(table="serverstats", guild_id=interaction.guild.id)
        if not data:
            await interaction.send(embed=create_error_embed(title="No statistic counter channels", description=f"You don't currently have any statstic counter channels. You can create some using `/statistic channel create`"), ephemeral=True)
            return
        listofchannels = ""
        for channel in data:
            listofchannels += f"\n<#{channel.channel_id}> ({channel.channel_id})"
        embed = nextcord.Embed(title="Statistic Counter Channels", description=listofchannels, colour=COLOUR_MAIN)
        await interaction.send(embed=embed)

    @tasks.loop(minutes=10)
    async def update_stat_channels(self):
        await self.client.wait_until_ready()
        global first
        if first:
            first = False
            await asyncio.sleep(5)
        data: List[ServerstatsMain] = Bot.db.get_data(table="serverstats")
        for statchannel in data:
            try:
                guild = self.client.get_guild(int(statchannel[0]))
                channel = guild.get_channel(int(statchannel[1]))
                counter_type = statchannel[2]
                if counter_type == "members_total":
                    await channel.edit(name=f"All Members: {len(guild.members)}")
                elif counter_type == "members_humans":
                    await channel.edit(name=f"All Humans: {len(guild.members) - len(guild.bots)}")
                elif counter_type == "members_bots":
                    await channel.edit(name=f"All Bots: {len(guild.bots)}")
                elif counter_type == "channels_all":
                    await channel.edit(name=f"All Channels: {len(guild.channels) - len(guild.categories)}")
                elif counter_type == "channels_text":
                    await channel.edit(name=f"Text Channels: {len(guild.text_channels)}")
                elif counter_type == "channels_voice":
                    await channel.edit(name=f"Voice Channels: {len(guild.voice_channels)}")
                elif counter_type == "channels_category":
                    await channel.edit(name=f"Categories: {len(guild.categories)}")
                elif counter_type == "roles":
                    await channel.edit(name=f"Roles: {len(guild.roles)}")
                elif counter_type == "emojis":
                    await channel.edit(name=f"Emojis: {len(guild.emojis)}")
                elif counter_type == "boosts":
                    await channel.edit(name=f"Boosts: {guild.premium_subscription_count}")
                elif counter_type == "members_online_total":
                    amount = 0
                    for member in guild.members:
                        if member.status != "offline":
                            amount+=1
                    await channel.edit(name=f"Online Members: {amount}")
                elif counter_type == "members_online_humans":
                    amount = 0
                    for member in guild.members:
                        if member.status != "offline" and not member.bot:
                            amount+=1
                    await channel.edit(name=f"Online Humans: {amount}")
                elif counter_type == "members_dnd_total":
                    amount = 0
                    for member in guild.members:
                        if member.status.dnd:
                            amount+=1
                    await channel.edit(name=f"DND Members: {amount}")
                elif counter_type == "members_dnd_humans":
                    amount = 0
                    for member in guild.members:
                        if member.status.dnd and not member.bot:
                            amount+=1
                    await channel.edit(name=f"DND Humans: {amount}")
                elif counter_type == "members_idle_total":
                    amount = 0
                    for member in guild.members:
                        if member.status.idle:
                            amount+=1
                    await channel.edit(name=f"Idle Members: {amount}")
                elif counter_type == "members_idle_humans":
                    amount = 0
                    for member in guild.members:
                        if member.status.idle and not member.bot:
                            amount+=1
                    await channel.edit(name=f"Idle Humans: {amount}")
                elif counter_type == "members_offline_total":
                    amount = 0
                    for member in guild.members:
                        if member.status.offline:
                            amount+=1
                    await channel.edit(name=f"Offline Members: {amount}")
                elif counter_type == "members_offline_humans":
                    amount = 0
                    for member in guild.members:
                        if member.status.offline and not member.bot:
                            amount+=1
                    await channel.edit(name=f"Offline Humans: {amount}")
            except:
                pass
    
        

def setup(client: Bot):
    client.add_cog(cog=ServerStatistics(client=client))
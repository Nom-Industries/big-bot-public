import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from nextcord.abc import GuildChannel
from bot import Bot
from utils import *
from typing import List, Union
from views.autopublish_view import messageselectview
from views.confirm_deny import Confirm
from constants import COLOUR_MAIN
from nextcord.errors import *
from db_handler.schemas import Autopublish

class AutoPublish(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="autopublish", description=f"Autopublish Base")
    async def autopublish(self, interaction:Interaction):
        pass

    @autopublish.subcommand(name=f"add", description=f"Add an autopublish channel")
    async def autopublish_config(self,
    interaction: Interaction,
    channel: GuildChannel = SlashOption(
        name="channel", 
        description="Channel to automatically publish", 
        required=True, 
        channel_types=[nextcord.ChannelType.news]
    )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        
        await interaction.response.defer()
        data: List[Autopublish] = self.client.db.get_data(table="autopublish", guild_id=interaction.guild.id)
        if data and len(data) >= 3:
            await interaction.send(embed=create_error_embed(title=f"Max channels reached", description="You have reachd your maximum amount of autopublish channels (`3`). To add new ones you must remove an old one by using `/autopublish remove`"))
            return
        
        self.client.db.create_data(table="autopublish", guild_id=interaction.guild.id, channel_id=channel.id)

        await interaction.send(embed=create_success_embed(title=f"Autopublish channel added", description=f"I have successfully added {channel.mention} as an auto publish channel. Any messages sent in there will now automatically be published"))
            

    @autopublish.subcommand(name="remove", description="Remove an auto publish channel")
    async def autopublish_remove(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        
        data: List[Autopublish] = self.client.db.get_data(table="autopublish", guild_id=interaction.guild.id)
        if data:
            async def getoptions(data: List[Autopublish]):
                options: List[nextcord.SelectOption] = []
                message = f""
                for e in data:
                    try:
                        channel = await interaction.guild.fetch_channel(int(e.channel_id))
                        label = channel.name
                        description = channel.id
                        value = channel.id
                    except NotFound:
                        label = "Deleted Channel"
                        description = int(e.channel_id)
                        value = int(e.channel_id)
                    message += f"<#{int(e.channel_id)}> ({int(e.channel_id)})\n"
                    options.append(nextcord.SelectOption(label=label, description=description, value=value))
                return options, message
            
            options, message = await getoptions(data=data)
            embed = nextcord.Embed(title="Remove Auto Publish Channel", description=f"Select which autopublish channel to remove\nYou have `{len(data)}` autopublish channels out of a maximum of `3`\n", colour=COLOUR_MAIN)
            embed.set_footer(text="The select menu will expire after 30 seconds")
            options = messageselectview(selectoptions=options, userid=interaction.user.id)
            msg = await interaction.send(embed=embed, view=options, ephemeral=True)
            r = await options.wait()
            if r:
                embed.set_footer(text="The select menu has expired")
                await msg.edit(embed=embed, view=None)
                return
            selected = int(options.values[0])
            for e in data:
                if int(e.channel_id) == selected:
                    data = e
                    break
            try:
                channel = await interaction.guild.fetch_channel(int(data.channel_id))
                self.client.db.delete_data(table="autopublish", data=data)

                await interaction.edit_original_message(embed=create_success_embed(title=f"Auto publish channel removed", description=f"I have removed {channel.mention} as an autopublish channel"), view=None)
            
            except NotFound:
                embed = nextcord.Embed(title="Channel Not Found", description="I couldn't find that channel, do you want me to remove it as an autopublish channel?", colour=COLOUR_MAIN)
                view = Confirm(org_user=interaction.user.id)
                await interaction.edit_original_message(view=None)
                await interaction.edit_original_message(embed=embed, view=view)
                await view.wait()
                if view.value:
                    self.client.db.delete_data(table="autopublish", data=data)
                    embed = create_success_embed(title="Auto publish channel removed", description="The auto publish channel has been removed")
                    await interaction.edit_original_message(embed=embed, view=None)
                else:
                    embed = create_success_embed(title="Action Cancelled", description="The action has been cancelled")
                    await interaction.edit_original_message(embed=embed, view=None)
        else:
            await interaction.send(embed=create_error_embed(title=f"No autopublish channels", description="You don't currently have any auto publish channels. You can add some using `/autopublish add`"))

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.channel.is_news():
            data: List[Autopublish] = self.client.db.get_data(table="autopublish", channel_id=message.channel.id)

            if not data:
                return
            
            await message.publish()



def setup(client: Bot):
    client.add_cog(cog=AutoPublish(client=client))

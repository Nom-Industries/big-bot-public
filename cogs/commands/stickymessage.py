import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
from requests import options
from views.sticky_views import Message_Form, Sticky_Button, messageselectview, Option_Panel, Message_Type, Channel_Select
from views.confirm_deny import Confirm
from bot import Bot
from utils import *
from nextcord.abc import GuildChannel
import asyncio
from constants import COLOUR_MAIN
from typing import List, Union
from nextcord.errors import *
from db_handler.schemas import *

cooldown = []

class Stickymessage(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    
    @nextcord.slash_command(name="stickymessage", description="Base command")
    async def stickymessage(self, interaction: nextcord.Interaction):
        pass


    @stickymessage.subcommand(name="create", description="Create a new stickymessage")
    async def stickymessage_create(self,
        interaction: nextcord.Interaction,
        channel: GuildChannel = SlashOption(
            name="channel", 
            description="Channel to send stickymessage to", 
            required=True, 
            channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.news]
            ),
        type: str = SlashOption(
            name="type", 
            description="Type of message to send",
            required=True,
            choices={"Embed":"embed", "Message":"msg"}
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        try:
            data: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=interaction.guild.id, channel_id=channel.id)
            if data:
                await interaction.send(embed=create_warning_embed(title="Already Message", description=f"You already have a stickymessage for that channel, use `/stickymessage manage` to edit/remove it"), ephemeral=True)
                return
            
            data: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=interaction.guild.id)
            if data:
                if len(data) >= 3:
                    await interaction.send(embed=create_warning_embed(title="Max Messages Reached", description=f"You have reached the maximum amount of stickymessages in this server, use `/stickymessage manage` to edit/remove your existing messages"), ephemeral=True)
                    return
            
            if type == "embed":
                data: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=interaction.guild.id, type="embed")
                if data:
                    await interaction.send(embed=create_warning_embed(title="Max Embed Messages Reached", description=f"You have reached the maximum amount of embed stickymessages in this server, use `/stickymessage manage` to edit/remove your existing messages"), ephemeral=True)
                    return


            options = Message_Form(type=type)
            await interaction.response.send_modal(modal=options)
            await options.wait()
            if type == "msg":
                stickymsg = options.stickymessage

                message = await channel.send(content=stickymsg, view=Sticky_Button())
                stickymsg = stickymsg.replace("'", "&#39;")
                Bot.db.create_data(table="sticky", guild_id=interaction.guild.id, channel_id=channel.id, message_id=message.id, message=str(stickymsg), type="msg")

            elif type == "embed":
                description = options.embeddescription
                title = options.embedtitle
                embed = nextcord.Embed(title=title, description=description, colour=COLOUR_MAIN)
                message = await channel.send(embed=embed, view=Sticky_Button())
                title = title.replace("'", "&#39;")
                description = description.replace("'", "&#39;")
                Bot.db.create_data(table="sticky", guild_id=interaction.guild.id, channel_id=channel.id, message_id=message.id, title=str(title), description=str(description), type="embed")

            await interaction.send(embed=create_success_embed(title="Success", description=f"Successfully created and sent stickymessage to {channel.mention}"), ephemeral=True)
            

        except Exception as e:
            print(e)
            await interaction.send(embed=create_error_embed(title="Error", description=f"An error occurred while executing the command, please try again. \nJoin our [support server](https://discord.gg/WjdMjUnBvJ) if this issue persists"), ephemeral=True)
        
    
    @stickymessage.subcommand(name="manage", description="Edit or delete a sticky message")
    async def stickymessage_manage(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        data: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=interaction.guild.id)
        dataa: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=interaction.guild.id, type="embed")
        if data:
            #if len(data) == 1:
                #pass
            #else:
                async def getoptions(data):
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
                embed_messages = len(dataa) if dataa else 0
                embed = nextcord.Embed(title="Manage Stickymessage", description=f"Select which stickymessage to edit\nYou have `{len(data)}` stickymessages out of a maximum of `3`\nYou have `{embed_messages}` embed stickymessages out of a maximum of `1`\n{message}", colour=COLOUR_MAIN)
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
                    embed = nextcord.Embed(title="Select a option", description=f"Select an option to edit the stickymessage. \nEditing the stickymessage in: {channel.mention}", colour=COLOUR_MAIN)
                    await msg.edit(embed=embed, view=Option_Panel(userid=interaction.user.id, data=data, org_iter=interaction))
                except NotFound:
                    embed = nextcord.Embed(title="Channel Not Found", description="I couldn't find that channel, do you want me to delete the stickymessage?", colour=COLOUR_MAIN)
                    view = Confirm(org_user=interaction.user.id)
                    await msg.edit(embed=embed, view=view)
                    await view.wait()
                    if view.value:
                        Bot.db.delete_data(table="sticky", data=data)
                        embed = create_success_embed(title="Sticky Message Deleted", description="The stickymessage has been deleted")
                        await msg.edit(embed=embed, view=None)
                    else:
                        embed = create_success_embed(title="Action Cancelled", description="The action has been cancelled")
                        await msg.edit(embed=embed, view=None)
        else:
            await interaction.send(embed=create_warning_embed(title="No Messages", description="Your dont have any sticky messages setup, use `/stickymessage create` to create one"), ephemeral=True)


    @stickymessage.subcommand(name="setup", description="Interactive stickymessage setup")
    async def stickymessage_setup(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        try:
            data: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=interaction.guild.id)
            if data:
                if len(data) >= 3:
                    await interaction.send(embed=create_warning_embed(title="Max Messages Reached", description=f"You have reached the maximum amount of stickymessages in this server, use `/stickymessage manage` to edit/remove your existing messages"), ephemeral=True)
                    return
            
            mchannel = Channel_Select()
            embed = nextcord.Embed(title="Select Channel", description="Which channel do you want to setup a sticky message in?", colour=COLOUR_MAIN)
            msg = await interaction.send(embed=embed, view=mchannel, ephemeral=True)
            await mchannel.wait()
            if not mchannel.rchannel:
                return
            data: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=interaction.guild.id, channel_id=mchannel.rchannel.id)
            if data:
                await msg.edit(embed=create_warning_embed(title="Already Message", description=f"You already have a stickymessage for that channel, use `/stickymessage manage` to edit/remove it"), view=None)
                return

            embed = nextcord.Embed(title="Select Type", description="What type of sticky message do you want to create?", colour=COLOUR_MAIN)
            mtype = Message_Type(msg=msg)
            await msg.edit(embed=embed, view=mtype)
            await mtype.wait()
            if not mtype.value:
                return
            elif mtype.value == "embed":
                if (not mtype.rdescription) or (not mtype.rtitle):
                    return
                embed = nextcord.Embed(title=mtype.rtitle, description=mtype.rdescription)
                rmsg = None
            else:
                rmsg = mtype.rmsg
                embed = None

            rmsg = await mchannel.rchannel.send(content=rmsg, embed=embed)
            if mtype.value == "embed":
                description = mtype.rdescription.replace("'", "&#39;")
                title = mtype.rtitle.replace("'", "&#39;")
                smsg = "N/A NOM"
            else:
                smsg = mtype.rmsg.replace("'", "&#39;")
                description = "N/A NOM"
                title = "N/A NOM"
            Bot.db.create_data(table="sticky", guild_id=interaction.guild.id, channel_id=mchannel.rchannel.id, message_id=rmsg.id, message=str(smsg), title=str(title), description=str(description), type=mtype.value)
            
            await msg.edit(embed=create_success_embed(title="Success", description=f"Successfully created and sent stickymessage to {mchannel.rchannel.mention}"), view=None)
            
            

            

        except Exception as e:
            print(e)
            await interaction.send(embed=create_error_embed(title="Error", description=f"An error occurred while executing the command, please try again. \nJoin our [support server](https://discord.gg/WjdMjUnBvJ) if this issue persists"), ephemeral=True)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        if message.channel.id in cooldown:
            return
        cooldown.append(message.channel.id)
        data: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=message.guild.id, channel_id=message.channel.id)
        if data:
            data = data[0]
            try:
                oldmsg = await message.channel.fetch_message(int(data.message_id))
                await oldmsg.delete()
            except:
                pass
            try:
                if data.type == "msg":
                    stickymsg = data.message.replace("&#39;", "'")
                    msg = await message.channel.send(content=stickymsg, view=Sticky_Button())
                elif data.type == "embed":
                    title = data.title.replace("&#39;", "'")
                    description = data.description.replace("&#39;", "'")
                    embed = nextcord.Embed(title=title, description=description, colour=COLOUR_MAIN)
                    msg = await message.channel.send(embed=embed, view=Sticky_Button())
            except:
                pass
            
            data.message_id = msg.id
            Bot.db.update_data(table="sticky", data=data)
            await asyncio.sleep(2)
        index = cooldown.index(message.channel.id)
        del cooldown[index]

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        data: List[StickyMain] = Bot.db.get_data(table="sticky", channel_id=channel.id)
        if data:
            Bot.db.delete_data(table="sticky", data=data[0])


def setup(client):
    client.add_cog(cog=Stickymessage(client=client))
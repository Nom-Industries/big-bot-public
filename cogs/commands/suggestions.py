from typing import List
import nextcord, random
from nextcord.ext import commands
from bot.bot import Bot
from utils.utils import color_message, create_warning_embed
from views import SuggestionView, AutoThreadJoin, VotingView
from constants import COLOUR_MAIN, COLOUR_NEUTRAL
from string import ascii_letters, digits
from db_handler.schemas import *

class Suggestions(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="suggestion", description="Suggestions base")
    async def suggestions(self, interaction: nextcord.Interaction):
        pass

    @suggestions.subcommand(name="config", description="Configure your suggestion channels")
    async def suggestions_config(self,
        interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        
        data: List[SuggestionsMain] = Bot.db.get_data(table="suggestions", guild_id=interaction.guild.id)
        
        if not data:
            content = "You don't currently have any suggestion channels on this server. Use the Add Suggestion Channel button to add one"

        else:
            content = f"You currently have `{len(data)}` Suggestion Channel(s):\n" + '\n'.join(f"<#{i.channel_id}> - `{i.channel_id}`" for i in data)
            
        embed = nextcord.Embed(title="Suggestion Channel", description=f"{content}", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=SuggestionView(user=interaction.user, data=data if data else []))

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        data: List[SuggestionsMain] = self.client.db.get_data("suggestions", guild_id=message.guild.id, channel_id=message.channel.id)
        if data and data[0]:
            if data[0].type == "simple":
                await message.add_reaction("✅")
                await message.add_reaction("❎")
                if data[0].autothread:
                    thread = await message.channel.create_thread(name=f"suggestion-{message.author.name}", message=message, auto_archive_duration=10080)
                    await thread.send("Thread Automatically Created.", view=AutoThreadJoin())

            elif data[0].type == "embedded":
                embed = nextcord.Embed(title="Suggestion", description=f"{message.content}", colour=COLOUR_MAIN)
                embed.set_author(name=f"{message.author}", icon_url=message.author.avatar.url if message.author.avatar else None)
                embed.set_footer(text=f"User ID: {message.author.id}")
                pic_ext = ['.jpg','.png','.jpeg']
                if len(message.attachments) > 0:
                    for ext in pic_ext:
                        if message.attachments[0].filename.endswith(ext):
                            embed.set_image(message.attachments[0])

                await message.delete()
                msg = await message.channel.send(embed=embed)
                await msg.add_reaction("✅")
                await msg.add_reaction("❎")
                if data[0].autothread:
                    thread = await msg.channel.create_thread(name=f"suggestion-{message.author.name}", message=msg, auto_archive_duration=10080)
                    await thread.send("Thread Automatically Created.", view=AutoThreadJoin())
                    if len(message.attachments) > 1:
                        content = "Other images in message:\n"
                        for i in message.attachments:
                            if i.url == message.attachments[0].url:
                                pass
                            else:
                                for ext in pic_ext:
                                    if i.filename.endswith(ext):
                                        content+=f"\n{i.url}"
                        
                        if content == "Other images in message:\n":
                            return
                        
                        await thread.send(content)
            else:
                embed = nextcord.Embed(title="Suggestion", description=f"{message.content}", colour=COLOUR_NEUTRAL)
                embed.set_author(name=f"{message.author}", icon_url=message.author.avatar.url if message.author.avatar else None)
                embed.add_field(name=f"Status", value=f"Pending")
                try:
                    await message.delete()
                except:
                    pass

                uniqueID = False
                while not uniqueID:
                    suggID = ''.join([random.choice(ascii_letters+digits+"_") for i in range(8)])
                    infodata = Bot.db.get_data("suggestions_info", suggestion_id=suggID)
                    if not infodata:
                        uniqueID = True

                embed.set_footer(text=f"Suggestion ID: {suggID} | 0 - 0")
                pic_ext = ['.jpg','.png','.jpeg']
                if len(message.attachments) > 0:
                    for ext in pic_ext:
                        if message.attachments[0].filename.endswith(ext):
                            embed.set_image(message.attachments[0])

                msg = await message.channel.send(embed=embed)
                Bot.db.create_data("suggestions_info", suggestion_id=suggID, guild_id=message.guild.id, channel_id=message.channel.id, message_id=msg.id, user_id=message.author.id, status="pending", upvotes=[], downvotes=[])
                await msg.edit(view=VotingView())
                if data[0].autothread:
                    thread = await msg.channel.create_thread(name=f"suggestion-{message.author.name}", message=msg, auto_archive_duration=10080)
                    await thread.send("Thread Automatically Created.", view=AutoThreadJoin())
                    if len(message.attachments) > 1:
                        content = "Other images in message:\n"
                        for i in message.attachments:
                            if i.url == message.attachments[0].url:
                                pass
                            else:
                                for ext in pic_ext:
                                    if i.filename.endswith(ext):
                                        content+=f"\n{i.url}"
                        if content == "Other images in message:\n":
                            return
                        
                        await thread.send(content)


    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.client.add_view(AutoThreadJoin())
            print(color_message(message="Loaded AutoThreadJoin view", color="blue"))
        except Exception as e:
            print(e)
            print(color_message(message="Failed to load AutoThreadJoin view", color="yellow"))
        try:
            self.client.add_view(VotingView())
            print(color_message(message="Loaded Voting view", color="blue"))
        except Exception as e:
            print(e)
            print(color_message(message="Failed to load Voting view", color="yellow"))




def setup(client: Bot):
    client.add_cog(Suggestions(client))
    
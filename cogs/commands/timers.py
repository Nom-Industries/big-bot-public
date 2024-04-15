
import nextcord, time
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from bot.bot import Bot
from constants import COLOUR_MAIN
from utils.utils import create_warning_embed, create_error_embed, create_success_embed, generate_random_string
from typing import List, Union
from db_handler.schemas import *

class Timers(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @nextcord.slash_command(name=f"reminder", description=f"Reminders base")
    async def reminders(self, interaction:nextcord.Interaction):
        pass

    
    @reminders.subcommand(name=f"create", description=f"Create a new reminder")
    async def reminders_create(self,
        interaction:nextcord.Interaction,
        durationinput:str=SlashOption(
            name=f"duration",
            description=f"How long should this reminder be?",
            required=True
        ),
        message:str=SlashOption(
            name=f"message",
            description=f"The message to display when the reminder ends.",
            required=False,
            default=""
        )):
        message = message[:500]

        await interaction.response.defer(ephemeral=True)

        if durationinput[-1].lower() == "s":
            duration=int(int(durationinput[:-1]))
        elif durationinput[-1] == "m":
            duration = int(int(durationinput[:-1])*60)
        elif durationinput[-1].lower() == "h":
            duration = int(int(durationinput[:-1])*3600)
        elif durationinput[-1].lower() == "d":
            duration = int(int(durationinput[:-1])*86400)
        elif durationinput[-1] == "M":
            duration = int(int(durationinput[:-1])*2629746)
        elif durationinput[-1].lower() == "y":
            duration = int(int(durationinput[:-1])*31536000)
        else:
            await interaction.send(embed=create_error_embed(title="Invalid Duration", description=f"You provided an invalid duration. For help on durations, please read our [knowledgebase article](https://nomindustries.com/help/knowledgebase.php?article=1) on it."))
            return
        if duration > 43200000:
            await interaction.send("Duration must be less than 500 days")
            return
        
        userdata: List[RemindersBase] = Bot.db.get_data(table="reminders", user_id=interaction.user.id)
        max_reminders = 25

        if userdata:
            if len(userdata) >= max_reminders:
                await interaction.send(embed=create_warning_embed(title=f"Max reminders reached", description=f"You have reached the maximum numder of allowed reminders (`{max_reminders}`). You can manage your reminders with the `/reminder list` and `/reminder delete` commands."))
                return

        uniqueID = False
        while not uniqueID:
            reminder_id = generate_random_string(length=6)
            id_data: List[RemindersBase] = Bot.db.get_data(table="reminders", reminder_id=reminder_id)
            if not id_data:
                uniqueID=True

        if interaction.channel.type == nextcord.ChannelType.private:
            data: List[RemindersBase] = Bot.db.create_data(table=f"reminders", reminder_id=reminder_id, guild_id=interaction.user.id, channel_id=interaction.user.id, user_id=interaction.user.id, message=message, time=(time.time()+duration), completed=False)
        else:
            data: List[RemindersBase] = Bot.db.create_data(table=f"reminders", reminder_id=reminder_id, guild_id=interaction.guild.id, channel_id=interaction.channel.id, user_id=interaction.user.id, message=message, time=(time.time()+duration), completed=False)
        await interaction.send(embed=create_success_embed(title=f"Reminder created [`{reminder_id}`]", description=f"I have setup a reminder which will be sent <t:{round(time.time())+duration}:R>" + (F"with the message: `{message}`" if not message=="" else ".")))


    @reminders.subcommand(name=f"list", description=f"List all your current reminders.")
    async def reminders_list(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        data: List[RemindersBase] = Bot.db.get_data(table="reminders", user_id=interaction.user.id)
        if not data:
            await interaction.send(embed=create_error_embed(title=f"No reminders", description=f"You don't have any active reminders. You can create one using `/reminder create`"))
            return
        
        embed=nextcord.Embed(title=f"Current reminders", description=f"Below is a list of your current reminders:\n\n", colour=COLOUR_MAIN)
        for reminder in data:
            embed.description+=f"`{reminder.reminder_id}` - <#{reminder.channel_id}> - <t:{reminder.time}:R>" + (f" - {reminder.message[:100]}" if not reminder.message == '' else '') + "\n"
        
        await interaction.send(embed=embed)

    @reminders.subcommand(name=f"remove", description=f"Remove a reminder")
    async def reminders_remove(self,
        interaction: Interaction,
        reminderid: str = SlashOption(
            name=f"reminder-id",
            description=f"The ID of the reminder you want to remove",
            required=True
        )):
        await interaction.response.defer(ephemeral=True)
        data: List[RemindersBase] = Bot.db.get_data(table="reminders", user_id=interaction.user.id, reminder_id=reminderid)
        if not data:
            await interaction.send(embed=create_warning_embed(title=f"No reminder", description=f"We couldn't find any reminder belonging to you with that ID. Make sure the ID is case-specific and try again later."))
            return
        Bot.db.delete_data(table="reminders", data=data[0])
        await interaction.send(embed=create_success_embed(title=f"Reminder removed", description=f"I have successfully removed the reminder with ID `{reminderid}`."))



    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 1080236533426180188 and "NOTIFICATION:" in message.content:
            content = message.content.replace("NOTIFICATION: ", "")
            ids = content.split(" ")
            reminder_id = ids[0]
            guild_id = ids[1]
            channel_id = ids[2]
            user_id = ids[3]
            try:
                user = await self.client.fetch_user(int(user_id))
                if guild_id == channel_id and user_id == guild_id and user_id == channel_id:
                    print(content)
                    await user.send(f"{user.mention} reminder `{reminder_id}`" + (f": `{content.split(f'{user_id} ')[3]}`" if not ids[4] == "None" else ""))
                else:
                    try:
                        guild = self.client.get_guild(int(guild_id))
                        channel = guild.get_channel(int(channel_id))
                        await channel.send(f"{user.mention} reminder `{reminder_id}`" + (f": `{content.split(f'{user_id} ')[1].replace('`', '')}`" if not ids[4] == "None" else ""))
                    except:
                        await user.send(f"{user.mention} reminder `{reminder_id}`" + (f": {ids[4]}." if not ids[4] == "None" else ""))
            except Exception as e:
                pass
            data: List[RemindersBase] = Bot.db.get_data(table="reminders", reminder_id=reminder_id)
            Bot.db.delete_data(table="reminders", data=data[0])


def setup(client: commands.Bot):
    client.add_cog(Timers(client))
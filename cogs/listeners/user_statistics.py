from asyncio import tasks
from nextcord.ext import commands, tasks
from datetime import datetime
from bot.bot import Bot
from utils import *
from typing import List
from db_handler.schemas import *
from constants import COLOUR_GOOD, COLOUR_MAIN, COLOUR_NEUTRAL, DBENDPOINT, DBPORT, DBUSER, DBPASS, DBNAME
import pymysql
import nextcord
from nextcord import Interaction, SlashOption

class UserStatistics(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.reset_daily_messages.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        userstats: List[UserStatisticsBase] = Bot.db.get_data(table="user_statistics", unique_id=f"{message.guild.id}-{message.author.id}")
        if not userstats:
            userstats: UserStatisticsBase = Bot.db.create_data(table="user_statistics", unique_id=f"{message.guild.id}-{message.author.id}", user_id=message.author.id, guild_id=message.guild.id, total_msgs=0, last_daily_msgs=0, last_weekly_msgs=0, last_monthly_msgs=0)
        else:
            userstats = userstats[0]
        
        userstats.total_msgs += 1

        Bot.db.update_data(table="user_statistics", data=userstats)
    
    @nextcord.slash_command(name="messages", description="View the number of messages someone has sent")
    async def view_messages(self,
                            interaction:Interaction,
                            user: nextcord.Member = SlashOption(
                                name="user",
                                description="The user who's message count you want to see",
                                required=False
    )):
        user = interaction.user if not user else user
        data: List[UserStatisticsBase] = Bot.db.get_data(table="user_statistics", unique_id=f"{interaction.guild.id}-{user.id}")
        if not data:
            await interaction.send(embed=create_warning_embed(title="User has no message count", description=f"{user.mention} has not sent any messages."), ephemeral=True)
            return
        data = data[0]
        embed = nextcord.Embed(title=f"{get_user_name(user)}'s messages", description=f"Today: {(int(data.total_msgs)-int(data.last_daily_msgs)):,}\nTotal: {(int(data.total_msgs)):,}", colour=COLOUR_MAIN)
        embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
        await interaction.send(embed=embed)

    @tasks.loop(seconds=60)
    async def reset_daily_messages(self):
        await self.client.wait_until_ready()
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        if current_time == "23:59":
            conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
            cur = conn.cursor()
            cur.execute("UPDATE user_statistics SET last_daily_msgs = total_msgs")
            conn.commit()

def setup(client: Bot):
    client.add_cog(UserStatistics(client))
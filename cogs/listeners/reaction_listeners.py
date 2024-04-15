import nextcord, pickle, base64
from bot.bot import Bot
from nextcord.ext import commands
from utils import *
from constants import DBENDPOINT, DBNAME, DBUSER, DBPASS
import pymysql


class reactions_listeners(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        conn = pymysql.connect(host=DBENDPOINT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM `reaction_emojis` WHERE msg_id = %s AND emoji_id = %s", (payload.message_id, payload.emoji.id if payload.emoji.is_custom_emoji() else base64.b64encode(pickle.dumps(payload.emoji.name)).decode("utf-8")))
        data = cur.fetchall()
        if data:
            roleid = data[0][4]
            guild = await self.client.fetch_guild(payload.guild_id)
            role = guild.get_role(int(roleid))
            if role not in payload.member.roles:
                await payload.member.add_roles(role)
                try:
                    await payload.member.send(embed=create_success_embed(title="Success", description=f"Successfully **added** the **{role.name}** role to you"))
                except:
                    pass

    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.client.user.id:
            await payload.message.add_reaction(payload.emoji)
            return
        
        guild = await self.client.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        if member.bot:
            return
        
        conn = pymysql.connect(host=DBENDPOINT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM `reaction_emojis` WHERE msg_id = %s AND emoji_id = %s", (payload.message_id, payload.emoji.id if payload.emoji.is_custom_emoji() else base64.b64encode(pickle.dumps(payload.emoji.name)).decode("utf-8")))
        data = cur.fetchall()
        if data:
            roleid = data[0][4]
            role = guild.get_role(int(roleid))
            if role in member.roles:
                await member.remove_roles(role)
                try:
                    await member.send(embed=create_success_embed(title="Success", description=f"Successfully **removed** the **{role.name}** role from you"))
                except:
                    pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        conn = pymysql.connect(host=DBENDPOINT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM `reaction_main` WHERE message_id = %s", message.id)
        cur.execute("DELETE FROM `reaction_emojis` WHERE msg_id = %s", message.id)
        conn.commit()
    
def setup(client: Bot):
    client.add_cog(reactions_listeners(client=client))
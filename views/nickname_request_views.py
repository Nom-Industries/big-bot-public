import nextcord, pymysql
from constants import DBENDPOINT, DBPORT, DBUSER, DBPASS, DBNAME
from utils.utils import create_warning_embed, create_error_embed, create_success_embed

class NicknameRequestManagement(nextcord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client

    @nextcord.ui.button(label="Accept", style=nextcord.ButtonStyle.green, custom_id="nick_request_accept")
    async def accept_request(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM nickname_main WHERE guild_id=%s", interaction.guild.id)
        data = cur.fetchall()
        if not data:
            await interaction.send(embed=create_error_embed(title="System Error", description=f"This system has not yet been configured by the server administrators. Please contact them if you believe this is an error"), ephemeral=True)
            return
        cur.execute("SELECT * FROM nickname_requests WHERE guild=%s AND message_id=%s", (interaction.guild.id, interaction.message.id))
        requestdata = cur.fetchall()
        if not requestdata:
            await interaction.send(embed=create_error_embed(title="Invalid Member", description=f"This user doesn't currently have a nickname request outgoing"))
            return
        modroleid = data[0][2]
        role = interaction.guild.get_role(int(modroleid))
        if interaction.user.guild_permissions.administrator or role in interaction.user.roles:
            try:
                try:
                    member = interaction.guild.get_member(int(requestdata[0][2]))
                    await member.edit(nick=str(requestdata[0][1]))
                except:
                    pass
                await interaction.send(embed=create_success_embed(title=f"Nickname request accepted", description=f"I have successfully changed {member.mention}'s nickname."), ephemeral=True)
                cur.execute("DELETE FROM nickname_requests WHERE guild=%s AND user=%s", (interaction.guild.id, member.id))
                conn.commit()
                try:
                    channel = interaction.guild.get_channel(int(requestdata[0][4]))
                    message = await channel.fetch_message(int(requestdata[0][3]))
                    await message.delete()
                except:
                    pass
                try:
                    member = interaction.guild.get_member(int(requestdata[0][2]))
                    await member.send(f"Your nickname request in **{interaction.guild.name}** for the nickname `{requestdata[0][1]}` has been accepted!")
                except:
                    pass
            except:
                cur.execute("DELETE FROM nickname_requests WHERE guild=%s AND user=%s", (interaction.guild.id, member.id))
                conn.commit()
                await interaction.send(embed=create_error_embed(title="Invalid Member", description=f"I couldn't find that member. Perhaps they left the guild?"), ephemeral=True)
                channel = interaction.guild.get_channel(int(requestdata[0][4]))
                message = await channel.fetch_message(int(requestdata[0][3]))
                await message.delete()
        else:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description=f"You are lacking {role.mention} so cannot use this. Contact the server administrators if you believe this is an error"), ephemeral=True)

    @nextcord.ui.button(label="Deny", style=nextcord.ButtonStyle.danger, custom_id="nick_request_deny")
    async def deny_request(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM nickname_main WHERE guild_id=%s", interaction.guild.id)
        data = cur.fetchall()
        if not data:
            await interaction.send(embed=create_error_embed(title="System Error", description=f"This system has not yet been configured by the server administrators. Please contact them if you believe this is an error"), ephemeral=True)
            return
        cur.execute("SELECT * FROM nickname_requests WHERE guild=%s AND message_id=%s", (interaction.guild.id, interaction.message.id))
        requestdata = cur.fetchall()
        if not requestdata:
            await interaction.send(embed=create_error_embed(title="Invalid Member", description=f"This user doesn't currently have a nickname request outgoing"))
            return
        modroleid = data[0][2]
        role = interaction.guild.get_role(int(modroleid))
        if interaction.user.guild_permissions.administrator or role in interaction.user.roles:
            try:
                member = interaction.guild.get_member(int(requestdata[0][2]))
                await interaction.send(embed=create_success_embed(title=f"Nickname request denied", description=f"I have successfully denied {member.mention}'s nickname request."), ephemeral=True)
                cur.execute("DELETE FROM nickname_requests WHERE guild=%s AND user=%s", (interaction.guild.id, member.id))
                conn.commit()
                try:
                    channel = interaction.guild.get_channel(int(requestdata[0][4]))
                    message = await channel.fetch_message(int(requestdata[0][3]))
                    await message.delete()
                except:
                    pass
                try:
                    await member.send(f"Your nickname request in **{interaction.guild.name}** for the nickname `{requestdata[0][1]}` has been denied.")
                except:
                    pass
            except:
                cur.execute("DELETE FROM nickname_requests WHERE guild=%s AND user=%s", (interaction.guild.id, member.id))
                conn.commit()
                await interaction.send(embed=create_error_embed(title="Invalid Member", description=f"I couldn't find that member. Perhaps they left the guild?"), ephemeral=True)
                channel = interaction.guild.get_channel(int(requestdata[0][4]))
                message = await channel.fetch_message(int(requestdata[0][3]))
                await message.delete()
        else:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description=f"You are lacking {role.mention} so cannot use this. Contact the server administrators if you believe this is an error"), ephemeral=True)
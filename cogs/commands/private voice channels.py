import nextcord, asyncio
from nextcord import SlashOption
from nextcord.ext import commands
from nextcord.abc import GuildChannel
from bot.bot import Bot
from utils.utils import create_error_embed, create_success_embed
from constants import COLOUR_GOOD, COLOUR_MAIN, COLOUR_NEUTRAL, DBENDPOINT, DBPORT, DBUSER, DBPASS, DBNAME
import pymysql, random
from views import List_Options_Private_VCs, RequestToJoinView

guild_slowmode = []

class PrivateVoiceChannels(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="privatevc", description="Private Voice Channels Base")
    async def privatevc(self, interaction: nextcord.Interaction):
        pass


    @privatevc.subcommand(name="create", description="Create a private voice channel")
    async def privatevc_create(self,
        interaction: nextcord.Interaction,
        name: str = SlashOption(
            name="name",
            description="Name of the voice call",
            required=True
        ),
        category: GuildChannel = SlashOption(
            name="category",
            description="Category for the voice call",
            required=True,
            channel_types=[nextcord.ChannelType.category]
        ),
        logchannel: GuildChannel = SlashOption(
            name="logchannel",
            description="Channel that voice call logs will be sent to",
            required=True,
            channel_types=[nextcord.ChannelType.text]
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM voice_channels_main WHERE guild_id = %s", interaction.guild.id)
        data = cur.fetchall()
        if len(data) >= 3:
            await interaction.send("You have reached the maximum amount of private voice channels (3). You can remove some to make space for new ones using `/privatevc remove`", ephemeral=True)
            conn.commit()
            return
        channel = await interaction.guild.create_voice_channel(name=name, category=category)
        cur.execute("INSERT INTO voice_channels_main (guild_id, channel_id, name, logchannel) VALUES (%s, %s, %s, %s)", (interaction.guild.id, channel.id, name, logchannel.id))
        conn.commit()
        embed=nextcord.Embed(title="Voice Channel Created", description=f"I have successfully created a private voice channel {channel.mention} in {category.mention} category. When people join this channel a private voice call we be made for them", colour=COLOUR_GOOD)
        await interaction.send(embed=embed)
    
    @privatevc.subcommand(name="remove", description="Delete a private voice channel")
    async def privatevc_remove(self,
        interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM voice_channels_main WHERE guild_id = %s", interaction.guild.id)
        data = cur.fetchall()
        if not data:
            await interaction.send("You have no private voice channels on this server.")
            conn.commit()
            return
        optiontext = ""
        options = []
        for i in range(len(data)):
            optiontext = optiontext + f"{i+1}: `Name` {data[i][2]} - `Channel ID` {data[0][1]}\n"
            options.append(str(i+1))
        embed = nextcord.Embed(title="Delete private voice channels", description=f"Choose which channel you want to delete from the list below:\n\n {optiontext}", colour=COLOUR_MAIN)
        chosenoption = List_Options_Private_VCs(options)
        msg = await interaction.send(embed=embed, view=chosenoption)
        await chosenoption.wait()
        option = data[(int(chosenoption.values[0])-1)][1]
        cur.execute("DELETE FROM voice_channels_main WHERE channel_id=%s", (option))
        conn.commit()
        embed = nextcord.Embed(title="Delete private voice channels", description=f"I have successfully removed the selected channel from the database. You will need to manually delete the channel from the discord server", colour=COLOUR_GOOD)
        await interaction.edit_original_message(embed=embed, view=None)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before, after):
        if after.channel:
            conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
            cur = conn.cursor()
            cur.execute("SELECT * FROM voice_channels_main WHERE guild_id = %s AND channel_id = %s", (after.channel.guild.id, after.channel.id))
            data = cur.fetchall()
            if not data:
                cur.execute("SELECT * FROM voice_channels WHERE guild_id = %s AND channel_id = %s", (after.channel.guild.id, after.channel.id))
                data1 = cur.fetchall()
                if not data1:
                    cur.execute("SELECT * FROM voice_channels WHERE guild_id = %s AND request_join_id = %s", (after.channel.guild.id, after.channel.id))
                    data1 = cur.fetchall()
                    if not data1:
                        conn.commit()
                        pass
                    else:
                        conn.commit()
                        channelid = data1[0][5]
                        channel = after.channel.guild.get_channel(int(channelid))
                        textchannelid = data1[0][6]
                        textchannel = after.channel.guild.get_channel(int(textchannelid))
                        ownerid = data1[0][1]
                        vcid = data1[0][3]
                        embed = nextcord.Embed(title="Request to join", description=f"""<@{ownerid}>, {member.mention} is requesting to join your private VC. You can choose 1 of the following actions:

1. Accept them and give them access to your channel
2. Deny them and remove them from your request to join channel
3. Deny them and block them from your request to join channel""", colour=COLOUR_NEUTRAL)
                        await textchannel.send(f"<@{ownerid}> | {member.mention}", embed=embed, view=RequestToJoinView(channelid=after.channel.id, memberid=member.id, ownerid=ownerid, vcid=vcid))
                else:
                    base = data1[0][4]
                    cur.execute("SELECT * FROM voice_channels_main WHERE channel_id=%s", base)
                    data = cur.fetchall()
                    conn.commit()
                    logchannelid = data[0][3]
                    if len(str(logchannelid)) > 7:
                        logchannel = after.channel.guild.get_channel(int(logchannelid))
                        if before.channel:
                            if after.channel.id == before.channel.id:
                                pass
                            else:
                                await logchannel.send(f"``{member}`` (``{member.id}``) Joined ``{after.channel.name}`` (``{after.channel.id}``)")
                        else:
                            await logchannel.send(f"``{member}`` (``{member.id}``) Joined ``{after.channel.name}`` (``{after.channel.id}``)")
            else:
                cur.execute(f"SELECT * FROM voice_channels WHERE guild_id = %s AND owner_id = %s", (after.channel.guild.id, member.id))
                data1 = cur.fetchall()
                if data1:
                    channel = after.channel.guild.get_channel(int(data1[0][3]))
                    await member.move_to(channel)
                    conn.commit()
                    pass
                else:
                    while after.channel.guild.id in guild_slowmode:
                        await asyncio.sleep(1)
                    guild_slowmode.append(after.channel.guild.id)
                    try:
                        channel = await after.channel.clone(name=f"{member.name}'s channel")
                        everyone = after.channel.guild.roles[0]
                        await channel.set_permissions(everyone, connect=False)
                        cur.execute("INSERT INTO voice_channels (guild_id, owner_id, private, channel_id, base_call_id) VALUES (%s, %s, %s, %s, %s)", (after.channel.guild.id, member.id, "yes", channel.id, after.channel.id))
                        logchannelid = data[0][3]
                        if len(str(logchannelid)) > 7:
                            logchannel = after.channel.guild.get_channel(int(logchannelid))
                            await logchannel.send(f"``{channel.name}`` (``{channel.id}``) Was Created.")
                        conn.commit()
                        await member.move_to(channel)
                        await channel.set_permissions(member, connect=True, use_voice_activation=True)
                        await asyncio.sleep(2)
                        index = guild_slowmode.index(after.channel.guild.id)
                        del guild_slowmode[index]
                    except:
                        await asyncio.sleep(2)
                        index = guild_slowmode.index(after.channel.guild.id)
                        del guild_slowmode[index]
        if before.channel:
            conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
            cur = conn.cursor()
            cur.execute("SELECT * FROM voice_channels WHERE guild_id = %s AND channel_id = %s", (before.channel.guild.id, before.channel.id))
            data = cur.fetchall()
            if not data:
                conn.commit()
                return
            if len(before.channel.members) == 0:
                while before.channel.guild.id in guild_slowmode:
                    await asyncio.sleep(1)
                guild_slowmode.append(before.channel.guild.id)
                try:
                    base = data[0][4]
                    cur.execute("DELETE FROM voice_channels WHERE channel_id=%s", before.channel.id)
                    cur.execute("SELECT * FROM voice_channels_main WHERE channel_id=%s", base)
                    data1 = cur.fetchall()
                    logchannelid = data1[0][3]
                    requestchannelid = data[0][5]
                    if len(str(logchannelid)) > 7:
                        logchannel = before.channel.guild.get_channel(int(logchannelid))
                        await logchannel.send(f"``{member}`` (``{member.id}``) Left ``{before.channel.name}`` (``{before.channel.id}``)")
                        await logchannel.send(f"``{before.channel.name}`` (``{before.channel.id}``) Was Deleted.")
                    conn.commit()
                    if len(str(requestchannelid)) > 7:
                        requestchannel = before.channel.guild.get_channel(int(requestchannelid))
                        await requestchannel.delete()
                    await before.channel.delete()
                    await asyncio.sleep(2)
                    index = guild_slowmode.index(
before.channel.guild.id)
                    del guild_slowmode[index]
                except:
                    await asyncio.sleep(2)
                    index = guild_slowmode.index(after.channel.guild.id)
                    del guild_slowmode[index]

            else:
                base = data[0][4]
                cur.execute("SELECT * FROM voice_channels_main WHERE channel_id=%s", base)
                data1 = cur.fetchall()
                conn.commit()
                logchannelid = data1[0][3]
                if logchannelid:
                    logchannel = before.channel.guild.get_channel(int(logchannelid))
                    if after.channel:
                        if after.channel.id == before.channel.id:
                            pass
                        else:
                            await logchannel.send(f"``{member}`` (``{member.id}``) Left ``{before.channel.name}`` (``{before.channel.id}``)")
                    else:
                        await logchannel.send(f"``{member}`` (``{member.id}``) Left ``{before.channel.name}`` (``{before.channel.id}``)")

    @privatevc.subcommand(name="invite", description="Invite a user to your voice channel")
    async def privatevc_invite(self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Who do you want to invite to your voice call?",
            required=True
        )):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM voice_channels WHERE guild_id = %s AND owner_id = %s", (interaction.guild.id, interaction.user.id))
        data = cur.fetchall()
        if not data:
            await interaction.send(embed=create_error_embed(title="Error!", description="You are not the owner of any VC."))
            conn.commit()
            return
        channelid = data[0][3]
        base = int(data[0][4])
        channel = interaction.guild.get_channel(int(channelid))
        await channel.set_permissions(member, connect=True, view_channel=True, use_voice_activation=True)
        await interaction.send(embed=create_success_embed(title="Success!", description=f"You have successfully added {member.mention} to {channel.mention}"), ephemeral=True)
        chance = random.randint(1, 10)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
        cur.execute("SELECT * FROM voice_channels_main WHERE guild_id = %s AND channel_id = %s", (interaction.guild.id, base))
        data = cur.fetchall()
        conn.commit()
        basechannel = data[0][3]
        if len(str(basechannel)) > 7:
            logchannel = interaction.guild.get_channel(int(basechannel))
            await logchannel.send(f"``{member}`` (``{member.id}``) Was Invited To ``{channel.name}`` (``{channel.id}``)")

    @privatevc.subcommand(name="block", description="Block a user from your voice channel")
    async def privatevc_block(self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Who do you want to block from your voice call?",
            required=True
        )):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM voice_channels WHERE guild_id = %s AND owner_id = %s", (interaction.guild.id, interaction.user.id))
        data = cur.fetchall()
        if not data:
            await interaction.send(embed=create_error_embed(title="Error!", description="You are not the owner of any VC."))
            conn.commit()
            return
        channelid = data[0][3]
        base = int(data[0][4])
        channel = interaction.guild.get_channel(int(channelid))
        await channel.set_permissions(member, connect=False, view_channel=False, use_voice_activation=False)
        if member in channel.members:
            await member.move_to(None)
        await interaction.send(embed=create_success_embed(title="Success!", description=f"You have successfully blocked {member.mention} from {channel.mention}"), ephemeral=True)
        chance = random.randint(1, 10)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
        cur.execute("SELECT * FROM voice_channels_main WHERE guild_id = %s AND channel_id = %s", (interaction.guild.id, base))
        data = cur.fetchall()
        conn.commit()
        basechannel = data[0][3]
        if len(str(basechannel)) > 7:
            logchannel = interaction.guild.get_channel(int(basechannel))
            await logchannel.send(f"``{member}`` (``{member.id}``) Was Blocked From ``{channel.name}`` (``{channel.id}``)")


    @privatevc.subcommand(name="public", description="Creates a \"request to join\" channel for other members")
    async def privatevc_public(self,
        interaction: nextcord.Interaction):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM voice_channels WHERE guild_id = %s AND owner_id = %s", (interaction.guild.id, interaction.user.id))
        data = cur.fetchall()
        channelid = data[0][3]
        base = int(data[0][4])
        if not data:
            await interaction.send(embed=create_error_embed(title="Error!", description="You are not the owner of any VC."))
            conn.commit()
            return
        if data[0][5]:
            await interaction.send(embed=create_error_embed(title="Error!", description="Your call is already public"), ephemeral=True)
            conn.commit()
            return
        cur.execute("SELECT * FROM voice_channels_main WHERE guild_id = %s AND channel_id = %s", (interaction.guild.id, base))
        data = cur.fetchall()
        channel = interaction.guild.get_channel(int(channelid))
        basechannel = interaction.guild.get_channel(int(base))
        joinchannel = await basechannel.clone(name=f"Join {interaction.user.name}")
        await joinchannel.edit(position=0 if channel.position == 0 else channel.position)
        cur.execute("UPDATE voice_channels SET request_join_id = %s, request_join_text_id = %s WHERE channel_id = %s", (joinchannel.id, interaction.channel.id, channel.id))
        conn.commit()
        await interaction.send(embed=create_success_embed(title="Success!", description=f"You have successfully created a \"Request to join\" channel. Users can join the channel if they want to join your main channel and you can accept/deny them"), ephemeral=True)
        chance = random.randint(1, 10)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @privatevc.subcommand(name="transfer", description="Transfer your voice channel to someone else")
    async def privatevc_transfer(self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Who do you want to transfer your channel to?",
            required=True
        )):
        if member == interaction.user:
            await interaction.send(embed=create_error_embed(title="Error!", description="You cannot transfer your channel to yourself"), ephemeral=True)
            return
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM voice_channels WHERE guild_id = %s AND owner_id = %s", (interaction.guild.id, interaction.user.id))
        data = cur.fetchall()
        if not data:
            await interaction.send(embed=create_error_embed(title="Error!", description="You are not the owner of any VC."))
            conn.commit()
            return
        cur.execute("UPDATE voice_channels SET owner_id = %s WHERE channel_id = %s AND owner_id = %s", (member.id, int(data[0][3]), interaction.user.id))
        conn.commit()
        await interaction.send(embed=create_success_embed(title="Success!", description=f"You have successfully transfered your voice call to {member.mention}"))
        chance = random.randint(1, 10)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")



            
            
        

def setup(client: Bot):
    client.add_cog(PrivateVoiceChannels(client))
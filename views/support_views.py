import nextcord, asyncio
from constants import COLOUR_GOOD, COLOUR_MAIN, COLOUR_NEUTRAL, DBENDPOINT, DBNAME, DBUSER, DBPASS, DBPORT
import pymysql, os, time
from utils import *

creation_cooldown = []


class Ticket_Open(nextcord.ui.View):
    def __init__(self, client):
        self.client = client
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Open Ticket", style=nextcord.ButtonStyle.blurple, custom_id="ticketopen")
    async def ticket_open(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id in creation_cooldown:
            await interaction.send("You are currently on cooldown. Try again later.", ephemeral=True)
            return
        creation_cooldown.append(interaction.user.id)
        await interaction.response.defer(with_message=True, ephemeral=True)
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        while not self.client.is_ready():
            await asyncio.sleep(1)
        try:
            cur.execute(f"SELECT * FROM current_tickets WHERE originmessage_id = {interaction.message.id} AND author_id = {interaction.user.id}")
            data = cur.fetchall()
            if len(data) > 0:
                data = data[0]
                e = interaction.guild.get_channel(int(data[0]))
                if e:
                    await e.set_permissions(interaction.user, read_messages=True, send_messages=True, embed_links=True, attach_files=True)
                    await interaction.send(embed=create_warning_embed(title="Ticket Open", description=f"You already have a ticket open, please use that channel for support. \n\n{e.mention}"))
                    conn.commit()
                    index = creation_cooldown.index(interaction.user.id)
                    del creation_cooldown[index]
                    return
                else:
                    cur.execute(f"DELETE FROM `current_tickets` WHERE channel_id={int(data[0])}")
                    conn.commit()
        except Exception as e:
            print(e)
            await interaction.send(embed=create_error_embed(title="Error", description="There was an error contacting the database, please try again later"))
            conn.commit()
            index = creation_cooldown.index(interaction.user.id)
            del creation_cooldown[index]
            return
        try:
            cur.execute(f"SELECT * FROM ticket_blacklists WHERE member=%s AND guild=%s", (interaction.user.id, interaction.guild.id))
            data = cur.fetchall()
            if data:
                await interaction.send(embed=create_warning_embed(title="Blacklisted", description=f"You have been blacklisted from creating new tickets in this server."))
                index = creation_cooldown.index(interaction.user.id)
                del creation_cooldown[index]
                return
            cur.execute(f"SELECT * FROM support_main WHERE message_id = {interaction.message.id} AND guild_id={interaction.guild.id}")
            data = cur.fetchall()
            cur.execute(f"SELECT * FROM support_main WHERE guild_id={interaction.guild.id}")
            overdata = cur.fetchall()
            if data:
                data = data[0]
                if int(data[3]) == 0:
                    category = None
                else:
                    category = await interaction.guild.fetch_channel(int(data[3]))
                channel = await interaction.guild.create_text_channel(
                    name=f"{str(data[8]).replace('{num}', str(data[9])).replace('{user_name}', str(interaction.user.name)).replace('{user_id}', str(interaction.user.id))}",
                    category=category,
                    overwrites={
                        interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                        interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True)
                        }
                    )
                await channel.set_permissions(interaction.user,
                                                read_messages=True,
                                                send_messages=True,
                                                embed_links=True,
                                                attach_files=True
                                                )
                open_message = data[4]
                while "{$" in open_message:
                    loc = open_message.find("{$user}")
                    open_message = open_message[:loc] + interaction.user.mention + open_message[loc+7:]
                embed = nextcord.Embed(title=channel.name.replace('-', ' '), description=open_message, colour=COLOUR_MAIN)
                if int(data[2]) != 0:
                    supportrole = interaction.guild.get_role(int(data[2]))
                    await channel.set_permissions(supportrole,
                                                read_messages=True,
                                                send_messages=True,
                                                embed_links=True,
                                                attach_files=True
                                                )
                if int(data[5]) != 0:
                    pingrole = interaction.guild.get_role(int(data[5]))
                    openmsg = await channel.send(f"{interaction.user.mention}, {pingrole.mention}", embed=embed, view=Ticket_Close(self.client))
                else:
                    openmsg = await channel.send(f"{interaction.user.mention}", embed=embed, view=Ticket_Close(self.client))
                await openmsg.pin()
                
                cur.execute("UPDATE support_main SET number = %s WHERE message_id = %s AND guild_id=%s", (str(int(data[9])+1), interaction.message.id, interaction.guild.id))

                cur.execute(f"INSERT INTO current_tickets (channel_id, author_id, originmessage_id) VALUES ({channel.id}, {interaction.user.id}, {data[1]})")
                conn.commit()
                index = creation_cooldown.index(interaction.user.id)
                del creation_cooldown[index]

                await interaction.send(embed=create_success_embed(title="Success", description=f"Ticket created in {channel.mention}!"), ephemeral=True)
                try:
                    logchannelid = data[6]
                    logchannel = interaction.guild.get_channel(int(logchannelid))
                    embed = nextcord.Embed(title="Ticket Created", description=f"""
**Panel**: {interaction.channel.mention} ([Message]({interaction.message.jump_url}))
**Ticket**: {channel.mention} ({channel.id})
**Created By**: {interaction.user.mention} ({interaction.user.id})""", colour=COLOUR_MAIN)
                    await logchannel.send(embed=embed)
                except:
                    pass
            
            else:
                await interaction.send(embed=create_warning_embed(title="Config Error", description=f"There is a issue with the config, please contact the server administrators to fix it."), ephemeral=True)
                conn.commit()
                index = creation_cooldown.index(interaction.user.id)
                del creation_cooldown[index]
    
        except Exception as e:
            print(e)
            conn.commit()
            try:
                await interaction.send(embed=create_error_embed(title="Error", description=f"An error occurred, please try again. \nIf the issue persists contact the server administrators for assistance"), ephemeral=True)
            except:
                pass
            index = creation_cooldown.index(interaction.user.id)
            del creation_cooldown[index]
            

class Ticket_Close(nextcord.ui.View):
    def __init__(self, client):
        self.client = client
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Close Ticket", style=nextcord.ButtonStyle.red, custom_id="ticketclose")
    async def ticket_close(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM `current_tickets` WHERE channel_id = %s", (interaction.channel.id))
        data1 = cur.fetchall()
        if not data1:
            await interaction.send("Error fetching ticket from database")
            conn.commit()
            return
        ownerid = data1[0][1]
        cur.execute("SELECT * FROM `support_main` WHERE `message_id` = %s", (data1[0][2]))
        data = cur.fetchall()
        if not data:
            await interaction.send("Error fetching panel from database")
            conn.commit()
            return
        await interaction.message.edit(view=None)
        embed = nextcord.Embed(title="Ticket closing log", colour=COLOUR_MAIN)
        embed1=nextcord.Embed(title="", description="Removing ticket from database", colour=COLOUR_NEUTRAL)
        msg = await interaction.channel.send(embeds=[embed, embed1])
        if data[0][6] != 0:
            logchannelid = data[0][6]
            logchannel = interaction.guild.get_channel(int(logchannelid))
        cur.execute("DELETE FROM `current_tickets` WHERE channel_id=%s", (interaction.channel.id))
        conn.commit()
        embed2=nextcord.Embed(title="", description="Ticket removed from database", colour=COLOUR_GOOD)
        embed3=nextcord.Embed(title="", description="Generating ticket transcript", colour=COLOUR_NEUTRAL)
        await msg.edit(embeds=[embed, embed2, embed3])
        f = open(f"ticket-transcript-{interaction.channel.id}.txt", "a")
        async for message in interaction.channel.history(oldest_first = True):
            f.writelines(f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.author}: {message.content}\n")

        message = await interaction.channel.history().flatten()
        f.close()
        embed4=nextcord.Embed(title="", description="Ticket transcript created", colour=COLOUR_GOOD)
        embed5=nextcord.Embed(title="", description="Sending transcript", colour=COLOUR_NEUTRAL)
        await msg.edit(embeds=[embed, embed2, embed4, embed5])
        if int(data[0][6]) != 0:
            log_embed=nextcord.Embed(title="Ticket closed", description=f"""
            
Ticket: {interaction.channel.name} ({interaction.channel.id})
Closed By: {interaction.user.mention} ({interaction.user.id})
Created By: <@{ownerid}> ({ownerid})""", colour=COLOUR_MAIN)
            await logchannel.send(embed=log_embed, file=nextcord.File(f"ticket-transcript-{interaction.channel.id}.txt"))
        try:
            if int(data[0][7]) != 0:
                member = interaction.guild.get_member(int(ownerid))
                member_embed=nextcord.Embed(title="Ticket closed", description=f"Your ticket has been closed. The transcript is attached above", colour=COLOUR_MAIN)
                await member.send(embed=member_embed, file=nextcord.File(f"ticket-transcript-{interaction.channel.id}.txt"))
        except Exception as e:
            print(e)
            pass
        os.remove(f"ticket-transcript-{interaction.channel.id}.txt")
        embed6=nextcord.Embed(title="", description="Transcript sent", colour=COLOUR_GOOD)
        embed7=nextcord.Embed(title="", description=f"This channel will be deleted <t:{round(time.time())+11}:R>", colour=COLOUR_NEUTRAL)
        await msg.edit(embeds=[embed, embed2, embed4, embed6, embed7])
        await asyncio.sleep(10)
        await interaction.channel.delete()

class SupportConfigForm(nextcord.ui.Modal):
    def __init__(self, welcomemsg:bool, paneltitle:bool, panelmsg:bool, channel, name_template):
        super().__init__(title="Ticket Panel Options", timeout=None)
        self.application_channel = channel
        self.chosewelcomemsg = welcomemsg
        self.chosepaneltitle = paneltitle
        self.chosepanelmsg = panelmsg
        self.name_template = name_template

        if welcomemsg:
            self.welcomemsg = nextcord.ui.TextInput(
                label = "What is your welcome message?",
                placeholder = "Example: Welcome to your ticket {$user}",
                style=nextcord.TextInputStyle.paragraph,
                min_length=1,
                max_length=3000,
                required=True
            )
            self.add_item(self.welcomemsg)
        
        if paneltitle:
            self.paneltitle = nextcord.ui.TextInput(
                label = "What is your panel title?",
                placeholder = "Example: Create a ticket!",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=255,
                required=True
            )
            self.add_item(self.paneltitle)
        
        if panelmsg:
            self.panelmsg = nextcord.ui.TextInput(
                label = "What is your panel message?",
                placeholder = "Example: Click the button to create a ticket!",
                style=nextcord.TextInputStyle.paragraph,
                min_length=1,
                max_length=3000,
                required=True
            )
            self.add_item(self.panelmsg)
        if name_template:
            self.name_template = nextcord.ui.TextInput(
                label="What is your name template?",
                placeholder="Variables: {num}, {user_name}, {user_id}",
                style=nextcord.TextInputStyle.short,
                min_length=3,
                max_length=24,
                required=True
            )
            self.add_item(self.name_template)

    async def callback(self, interaction: nextcord.Interaction):
        if self.chosewelcomemsg:
            self.chosewelcomemsg = self.welcomemsg.value
        if self.chosepaneltitle:
            self.chosepaneltitle = self.paneltitle.value
        if self.chosepanelmsg:
            self.chosepanelmsg = self.panelmsg.value
        if self.name_template:
            self.chosetemplate = self.name_template.value[:32]
        self.stop()


class channelselect(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(placeholder="Select a channel", min_values=1, max_values=1, channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.news])

    async def callback(self, interaction: nextcord.Interaction):
        self.view.rchannel = self.values[0]
        self.view.stop()

class Channel_Select(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        self.add_item(channelselect())
        self.rchannel = None

class categoryselect(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(placeholder="Select a category", min_values=1, max_values=1, channel_types=[nextcord.ChannelType.category])

    async def callback(self, interaction: nextcord.Interaction):
        self.view.rcategory = self.values[0]
        self.view.stop()

class Category_Select(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        self.add_item(categoryselect())
        self.rcategory = None

class roleselect(nextcord.ui.RoleSelect):
    def __init__(self):
        super().__init__(placeholder="Select a role", min_values=1, max_values=1)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.rrole = self.values[0]
        self.view.stop()

class Role_Select(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        self.add_item(roleselect())
        self.rrole = None

class Form_Button(nextcord.ui.View):
    def __init__(self, welcomemsg, paneltitle, panelmsg, channel):
        super().__init__(timeout=600)
        self.application_channel = channel
        self.chosewelcomemsg = welcomemsg
        self.chosepaneltitle = paneltitle
        self.chosepanelmsg = panelmsg

    @nextcord.ui.button(label="Input", style=nextcord.ButtonStyle.blurple, disabled=False)
    async def input(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        options = SupportConfigForm(welcomemsg=self.chosewelcomemsg, paneltitle=self.chosepaneltitle, panelmsg=self.chosepaneltitle, channel=self.application_channel, name_template=False)
        await interaction.response.send_modal(modal=options)
        await options.wait()
        if self.chosewelcomemsg:
            self.welcomemsg = options.chosewelcomemsg
        else:
            self.panelmsg = options.chosepanelmsg
            self.paneltitle = options.chosepaneltitle
        self.stop()

async def reset_cooldown_loop():
    global creation_cooldown
    creation_cooldown = []
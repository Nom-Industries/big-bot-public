import nextcord, time, asyncio
from bot.bot import Bot
from nextcord import Interaction, SlashOption
from nextcord.ext import commands, tasks
from nextcord.abc import GuildChannel
from utils import *
from views.support_views import Ticket_Open, Ticket_Close, SupportConfigForm, Channel_Select, Category_Select, Role_Select, Form_Button, reset_cooldown_loop
from views import Confirm
from constants import COLOUR_GOOD, COLOUR_MAIN, COLOUR_NEUTRAL, DBENDPOINT, DBNAME, DBUSER, DBPASS, DBPORT
import pymysql

class Support(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.reset_cooldown_list.start()

    @nextcord.slash_command(name="supportpanel", description="Support Commands")
    async def panel(self, interaction: nextcord.Interaction):
        pass

    @panel.subcommand(name="create", description="Create a support pannel")
    async def panel_create(self, 
                        interaction: nextcord.Interaction, 
                        channel: GuildChannel = SlashOption(
                            name="channel", 
                            description="Channel to send panel to",
                            required=True,
                            channel_types=[nextcord.ChannelType.text]
                            ),
                        category: nextcord.CategoryChannel = SlashOption(
                            name="category",
                            description="Category to open tickets in",
                            required=False,
                            channel_types=[nextcord.ChannelType.category]
                            ),
                        supportrole: nextcord.Role = SlashOption(
                            name="supportrole",
                            description="The role that will have access to tickets",
                            required=False
                            ),
                        logchannel: GuildChannel = SlashOption(
                            name="logchannel",
                            description="The channel where ticket logs will be sent",
                            required=False,
                            channel_types=[nextcord.ChannelType.text]
                            ),
                        pingrole: nextcord.Role = SlashOption(
                            name="pingrole",
                            description="The role that will be pinged when a ticket is created",
                            required=False
                            ),
                        name_template: bool = SlashOption(
                            name=f"template",
                            description="Whether to use a custom name template on tickets",
                            required=False,
                            default=False
                            ),
                        dmonclose: bool = SlashOption(
                            name="dmonclose",
                            description="Whether to dm the ticket creator a transcript of the ticket",
                            required=False,
                            default=False,
                            ),
                        customwelcomemessage: bool = SlashOption(
                            name="customwelcomemessage",
                            description="Wheter you want to use a custom welcome message",
                            required=False,
                            default=False,
                            ),
                        custompaneltitle: bool = SlashOption(
                            name="custompaneltitle",
                            description="Wheter you want to use a custom title for the panel",
                            required=False,
                            default=False,
                            ),
                        custompanelmessage: bool = SlashOption(
                            name="custompanelmessage",
                            description="Wheter you want to use a custom message for the panel",
                            required=False,
                            default=False,
                            )
                        ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return

        if customwelcomemessage or custompaneltitle or custompanelmessage or name_template:
            options = SupportConfigForm(customwelcomemessage, custompaneltitle, custompanelmessage, channel, name_template)
            await interaction.response.send_modal(modal=options)
            await options.wait()
            if customwelcomemessage:
                customwelcomemessage = options.chosewelcomemsg
            if custompaneltitle:
                custompaneltitle = options.chosepaneltitle
            if custompanelmessage:
                custompanelmessage = options.chosepanelmsg
            if name_template:
                name_template = options.chosetemplate


        if not customwelcomemessage:
            customwelcomemessage = "Welcome to the ticket {$user}. \n\nExplain your issue in this channel and a member of the support team will help you out shortly"
        if not custompaneltitle:
            custompaneltitle = "Support"
        if not custompanelmessage:
            custompanelmessage = "Click the button below to speak to the servers support team"
        if not name_template:
            name_template = "ticket-{num}"
        if not category:
            category = 0
        else:
            category = category.id
        if not supportrole:
            supportrole = 0
        else:
            supportrole = supportrole.id
        if not logchannel:
            logchannel = 0
        else:
            logchannel = logchannel.id
        if not pingrole:
            pingrole = 0
        else:
            pingrole = pingrole.id
        if not dmonclose:
            dmonclose = 0
        else:
            dmonclose = 1
        embed = nextcord.Embed(title=f"{custompaneltitle}", description=f"{custompanelmessage}", colour=COLOUR_MAIN)
        message = await channel.send(embed=embed, view=Ticket_Open(self.client))
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO support_main (guild_id, message_id, supportrole_id, supportcategory_id, creation_message, pingrole_id, logchannel_id, dmonclose, name_template) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (interaction.guild.id, message.id, supportrole, category, customwelcomemessage, pingrole, logchannel, dmonclose, name_template))
        conn.commit()

        await interaction.send(embed=create_success_embed(title="Success", description=f"Successfully created and sent panel to {channel.mention}"), ephemeral=True)

    @nextcord.slash_command("add", description="Add a member to a ticket")
    async def support_add(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to add to the ticket",
            required=True
        )):
        await interaction.response.defer()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM current_tickets WHERE channel_id = %s", interaction.channel.id)
        data = cur.fetchall()
        if data:
            await interaction.channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True, read_message_history=True)
            await interaction.send(f"Successfully added **{member}** to the ticket")
            try:
                cur.execute("SELECT * FROM support_main WHERE message_id=%s", data[0][2])
                data = cur.fetchall()
                logchannelid = data[0][6]
                logchannel = interaction.guild.get_channel(int(logchannelid))
                embed = nextcord.Embed(title="Member Added to Ticket", description=f"""
Ticket: {interaction.channel.mention} ({interaction.channel.id})
Member Added: {member.mention} ({member.id})
Member Added By: {interaction.user.id} ({interaction.user.id})""", colour=COLOUR_MAIN)
                await logchannel.send(embed=embed)
            except Exception as e:
                print(e)
                pass
        else:
            await interaction.send("This channel is not a ticket.")


    @panel.subcommand(name="setup", description="Interactive support panel setup")
    async def supportpanel_setup(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return

        mchannel = Channel_Select()
        embed = nextcord.Embed(title="Select Channel", description="Which channel do you want to setup a support pannel in?")
        msg = await interaction.send(embed=embed, view=mchannel, ephemeral=True)
        await mchannel.wait()
        if not mchannel.rchannel:
            return

        choice = Confirm()
        embed = nextcord.Embed(title="Category", description="Do you want your tickets to be created in a category?")
        await msg.edit(embed=embed, view=choice)
        await choice.wait()
        if choice.value:
            tcategory = Category_Select()
            embed = nextcord.Embed(title="Category", description="Which category do you want to create tickets in?")
            await msg.edit(embed=embed, view=tcategory)
            await tcategory.wait()
            if not tcategory.rcategory:
                return
            rtcategory = tcategory.rcategory.id
        else:
            rtcategory = 0

        choice2 = Confirm()
        embed = nextcord.Embed(title="Support Role", description="Do you want to add a support role?")
        await msg.edit(embed=embed, view=choice2)
        await choice2.wait()
        if choice2.value:
            srole = Role_Select()
            embed = nextcord.Embed(title="Support Role", description="What role do you want to set as the support role?")
            await msg.edit(embed=embed, view=srole)
            await srole.wait()
            if not srole.rrole:
                return
            rsrole = srole.rrole.id
        
        else:
            rsrole = 0

        choice3 = Confirm()
        embed = nextcord.Embed(title="Log Channel", description="Do you want to setup a log channel?")
        await msg.edit(embed=embed, view=choice3)
        await choice3.wait()
        if choice3.value:
            lchannel = Channel_Select()
            embed = nextcord.Embed(title="Log Channel", description="Which channel do you want to setup logging in?")
            await msg.edit(embed=embed, view=lchannel)
            await lchannel.wait()
            if not lchannel.rchannel:
                return
            rlchannel = lchannel.rchannel.id

        else:
            rlchannel = 0

        choice4 = Confirm()
        embed = nextcord.Embed(title="Ping Role", description="Do you want a role to be pinged when tickets are opened?")
        await msg.edit(embed=embed, view=choice4)
        await choice4.wait()
        if choice4.value:
            prole = Role_Select()
            embed = nextcord.Embed(title="Ping Role", description="What role do you want to be pinged?")
            await msg.edit(embed=embed, view=prole)
            await prole.wait()
            if not prole.rrole:
                return
            rprole = prole.rrole.id
        
        else:
            rprole = 0

        choice5 = Confirm()
        embed = nextcord.Embed(title="Dm on close", description="Do you want to dm a user a copy of the transcript when a ticket is closed?")
        await msg.edit(embed=embed, view=choice5)
        await choice5.wait()
        if choice5.value:
            dmonclose = 1
        else:
            dmonclose = 0

        choice6 = Confirm()
        embed = nextcord.Embed(title="Custom Embed", description="Do you want to create a custom embed for the support pannel?")
        await msg.edit(embed=embed, view=choice6)
        await choice6.wait()
        if choice6.value:
            embed = nextcord.Embed(title="Custom Embed", description="Press the button below to create a custom embed")
            custompannelbutton = Form_Button(welcomemsg=False, paneltitle=True, panelmsg=True, channel=mchannel.rchannel)
            await msg.edit(embed=embed, view=custompannelbutton)
            await custompannelbutton.wait()
            if (not custompannelbutton.panelmsg) or (not custompannelbutton.paneltitle):
                return
            custompaneltitle = custompannelbutton.paneltitle
            custompanelmessage = custompannelbutton.panelmsg
        else:
            custompaneltitle = "Support"
            custompanelmessage = "Click the button below to speak to the servers support team"
        
        choice7 = Confirm()
        embed = nextcord.Embed(title="Custom Welcome Message", description="Do you want to create a custom welcome message for when a ticket is created?")
        await msg.edit(embed=embed, view=choice7)
        await choice7.wait()
        if choice7.value:
            embed = nextcord.Embed(title="Custom Welcome Message", description="Press the button below to create a custom welcome message")
            customwelcomemessagebutton = Form_Button(welcomemsg=True, paneltitle=False, panelmsg=False, channel=mchannel.rchannel)
            await msg.edit(embed=embed, view=customwelcomemessagebutton)
            await customwelcomemessagebutton.wait()
            if not customwelcomemessagebutton.welcomemsg:
                return
            customwelcomemessage = customwelcomemessagebutton.welcomemsg
        else:
            customwelcomemessage = "Welcome to the ticket {$user}. \n\nExplain your issue in this channel and a member of the support team will help you out shortly"

        channel = mchannel.rchannel
        
        embed = nextcord.Embed(title=f"{custompaneltitle}", description=f"{custompanelmessage}", colour=COLOUR_MAIN)
        message = await channel.send(embed=embed, view=Ticket_Open(self.client))
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"INSERT INTO support_main (guild_id, message_id, supportrole_id, supportcategory_id, creation_message, pingrole_id, logchannel_id, dmonclose) VALUES ({interaction.guild.id}, {message.id}, {rsrole}, {rtcategory}, '{customwelcomemessage}', {rprole}, {rlchannel}, {dmonclose})")
        conn.commit()

        await msg.edit(embed=create_success_embed(title="Success", description=f"Successfully created and sent panel to {channel.mention}"), view=None)

    @nextcord.slash_command("ticket-blacklist", description="Blacklist a user from creating any new tickets in the server")
    async def support_ticket_blacklist(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to blacklist from creating tickets",
            required=True
        ),
        reason: str = SlashOption(
            name="reason",
            description="The reason for blacklisting the user from creating tickets",
            required=False,
            default="Not Given"
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `moderator_members` permission, contact the server administrators if you believe this is an error"))
            return
        if member.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description=f"That member cannot be blacklisted since they have `manage_members` permission."))
            return
        await interaction.response.defer()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM ticket_blacklists WHERE guild=%s AND member=%s", (interaction.guild.id, member.id))
        data = cur.fetchall()
        if data:
            conn.commit()
            await interaction.send(f"**{member}** is already blacklisted from creating tickets. Use `/ticket-unblacklist` to remove them from the blacklist.")
            return
        cur.execute(f"INSERT INTO ticket_blacklists (member, guild, moderator, reason, given) VALUES (%s, %s, %s, %s, %s)", (member.id, interaction.guild.id, interaction.user.id, reason[:350], (round(time.time()))))
        conn.commit()
        embed = nextcord.Embed(title=f"Ticket Blacklist", description=f"{member.mention} has been added to the ticket blacklist with reason: {reason[:350]}", colour=COLOUR_GOOD)
        embed.set_footer(text=f"User ID: {member.id} | Moderator ID: {interaction.user.id}")
        await interaction.send(embed=embed)

    @nextcord.slash_command("ticket-unblacklist", description="Remove a blacklist from a user, allowing them to create new tickets in the server")
    async def support_ticket_unblacklist(self,
        interaction: Interaction,
        member : nextcord.Member = SlashOption(
            name="member",
            description="Member to remove blacklist from",
            required=True
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `moderator_members` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM ticket_blacklists WHERE guild=%s AND member=%s", (interaction.guild.id, member.id))
        data = cur.fetchall()
        if not data:
            conn.commit()
            await interaction.send(f"**{member}** is not currently blacklisted from creating tickets. Use `/ticket-blacklist` to blacklist them")
            return
        embed = nextcord.Embed(title="Confirmation", description=f"""Are you sure you want to delete the following blacklist:

Member: <@{data[0][0]}>
Moderator: <@{data[0][2]}>
Reason: ``{data[0][3]}``
Given: <t:{data[0][4]}> (<t:{data[0][4]}:R>)""", colour=COLOUR_NEUTRAL)
        confirmation = Confirm(org_user=interaction.user.id)
        await interaction.send(embed=embed, view=confirmation)
        await confirmation.wait()
        decision = confirmation.value
        if not decision:
            embed = nextcord.Embed(title="Confirmation", description="Action cancelled.", colour=COLOUR_NEUTRAL)
            await interaction.edit_original_message(embed=embed, view=None)
            return
        cur.execute(f"DELETE FROM `ticket_blacklists` WHERE guild=%s AND member=%s", (interaction.guild.id, member.id))
        conn.commit()
        embed = nextcord.Embed(title=f"Ticket Unblacklist", description=f"{member.mention} has been removed from the ticket blacklist.", colour=COLOUR_GOOD)
        embed.set_footer(text=f"User ID: {member.id} | Moderator ID: {interaction.user.id}")
        await interaction.edit_original_message(embed=embed, view=None)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        if message.author == self.client.user:
            cur.execute(f"SELECT * FROM support_main WHERE message_id = {message.id}")
            data = cur.fetchall()
            if data:
                cur.execute(f"DELETE FROM support_main WHERE message_id = {message.id}")
                conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.type is nextcord.MessageType.pins_add and message.author.id == self.client.user.id:
            await message.delete()


    @tasks.loop(minutes=1)
    async def reset_cooldown_list(self):
        await self.client.wait_until_ready()
        await reset_cooldown_loop()

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.client.add_view(Ticket_Open(self.client))
            print(color_message(message="Loaded Ticket_Open view", color="blue"))
        except Exception as e:
            print(e)
            print(color_message(message="Failed to load Ticket_Open view", color="yellow"))
        try:
            self.client.add_view(Ticket_Close(self.client))
            print(color_message(message="Loaded Ticket_Close view", color="blue"))
        except Exception as e:
            print(e)
            print(color_message(message="Failed to load Ticket_Close view", color="yellow"))

def setup(client: Bot):
    client.add_cog(cog=Support(client=client))
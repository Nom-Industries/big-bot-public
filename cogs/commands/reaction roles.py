import nextcord, asyncio, pickle, base64
from bot.bot import Bot
from nextcord.ext import commands
from utils import *
from constants import COLOUR_MAIN, DBENDPOINT, DBNAME, DBUSER, DBPASS, DBPORT
import pymysql
from views.reaction_views import Options,  Channel_Select, Options2, Role_Select, Button_View, Dropdown_View, Message_Id, Open_Form, Colour_Choice, Select_Type
from views.confirm_deny import Confirm
from typing import List
from nextcord.errors import *

class Reactionroles(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @nextcord.slash_command(name="reactionroles", description="Reaction role commands")
    async def reactionroles(self, interaction: nextcord.Interaction):
        pass

    @reactionroles.subcommand(name="create", description="Interactive creation of a reaction message")
    async def reactionroles_create(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"), ephemeral=True)
            return
        view = Options(interaction.user.id)
        embed = nextcord.Embed(title="Message Type", description="What type of message do you want to use?", colour=COLOUR_MAIN)
        msg = await interaction.send(embed=embed, view=view, ephemeral=False)
        await view.wait()
        if view.choice is None:
            return
        
        elif view.choice in ("msg", "embed"):
            type = Options2(interaction.user.id)
            embed = nextcord.Embed(title="Reaction Type", description="Choose how members will interact with the pannel", colour=COLOUR_MAIN)
            await msg.edit(embed=embed, view=type)
            await type.wait()
            if type.type is None:
                return

            elif type.type in ("button", "dropdown"):
                channelview = Channel_Select(interaction.user.id)
                embed = nextcord.Embed(title="Select Channel", description="Which channel do you want to send the reaction role message to?", colour=COLOUR_MAIN)
                await msg.edit(embed=embed, view=channelview)
                await channelview.wait()
                if channelview.rchannel is None:
                    return
                roleview = Role_Select(interaction.user.id)
                embed = nextcord.Embed(title="Select Roles", description="Which roles do you want to be on the reaction role panel?", colour=COLOUR_MAIN)
                await msg.edit(embed=embed, view=roleview)
                await roleview.wait()
                if roleview.roles:
                    if type.type == "button":
                        emojis = []
                        info = []
                        rlist = []
                        msgg = await msg.fetch()
                        def check(reaction, member):
                            return  reaction.message.channel == interaction.channel and member == interaction.user
                        for role in roleview.roles:
                            i = []
                            embed = nextcord.Embed(title="Custom Name", description=f"Do you want to give the button a custom name for {role.mention} ({role.id})?", colour=COLOUR_MAIN)
                            confirm = Confirm(org_user=interaction.user.id)
                            await msg.edit(embed=embed, view=confirm)
                            await confirm.wait()
                            if confirm.value:
                                embed = nextcord.Embed(title="Open Form", description=f"Press the button below to enter the name you want the button name to be for {role.mention} ({role.id})", colour=COLOUR_MAIN)
                                b = Open_Form(org_user=interaction.user.id, type="button")
                                await msg.edit(embed=embed, view=b)
                                await b.wait()
                                i.append(b.name)
                            else:
                                i.append(role.name)
                            embed = nextcord.Embed(title="Custom Emoji", description=f"Do you want to give the button a custom emoji for {role.mention} ({role.id})?", colour=COLOUR_MAIN)
                            confirm2 = Confirm(org_user=interaction.user.id)
                            await msg.edit(embed=embed, view=confirm2)
                            await confirm2.wait()
                            if confirm2.value:
                                embed = nextcord.Embed(title="Chose emoji", description=f"React to this message with the emoji you want to use for {role.mention} ({role.id})", colour=COLOUR_MAIN)
                                await msg.edit(embed=embed, view=None)
                                do = True
                                while do is True:
                                    try:
                                        reaction, e = await self.client.wait_for('reaction_add', timeout=600, check=check)
                                    except asyncio.TimeoutError:
                                        embed = create_error_embed(title="Timed out", description="This interaction has timed out.")
                                        await msg.edit(embed=embed)
                                        return
                                    await msgg.clear_reactions()
                                    if reaction.emoji in emojis:
                                        await msgg.reply("You can't use the same emoji more than once! React with another emoji you wish to use.", delete_after=5)
                                    else:
                                        emojis.append(reaction.emoji)
                                        i.append(reaction.emoji)
                                        do = False
                            else:
                                i.append(None)
                            embed = nextcord.Embed(title="Button Colour", description=f"Select the button colour you want to use for {role.mention} ({role.id})?", colour=COLOUR_MAIN)
                            colour = Colour_Choice(org_user=interaction.user.id)
                            await msg.edit(embed=embed, view=colour)
                            await colour.wait()
                            if not colour.colour:
                                return
                            i.append(colour.colour)
                            rlist.append(role.id)
                            info.append(i)
                        reactionroleview = Button_View(info=info)
                        if view.choice == "embed":
                            embed = nextcord.Embed(title=f"{view.rtitle}", description=f"{view.rdescription}", colour=COLOUR_MAIN)
                            content = None
                        elif view.choice == "msg":
                            content = view.rmsg
                            embed = None
                        rmsg = await channelview.rchannel.send(content=content, embed=embed, view=reactionroleview)
                        
                        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                        cur = conn.cursor()
                        cur.execute(f"INSERT INTO `reaction_main` (guild_id, message_id, channel_id, reaction_type, message_type, roles) VALUES ({interaction.guild.id}, {rmsg.id}, {channelview.rchannel.id}, '{type.type}', '{view.choice}', '{rlist}')")
                        conn.commit()
                        await msg.edit(embed=create_success_embed(title="Success", description=f"Sucessfully created panel and sent it to {channelview.rchannel.mention}"), view=None)
                    
                    else:
                        info = []
                        rlist = []
                        emojis = []
                        embed = nextcord.Embed(title="Dropdown Type", description="Do you want member to be able to select a **single** role or **multiple roles** from this menu at a time?", colour=COLOUR_MAIN)
                        t = Select_Type(org_user=interaction.user.id)
                        await msg.edit(embed=embed, view=t)
                        await t.wait()
                        if not t.t:
                            return
                        
                        msgg = await msg.fetch()
                        def check(reaction, member):
                            return  reaction.message.channel == interaction.channel and member == interaction.user
                        for role in roleview.roles:
                            i = []
                            embed = nextcord.Embed(title="Custom Name", description=f"Do you want to give the select option a custom name for {role.mention} ({role.id})?", colour=COLOUR_MAIN)
                            confirm = Confirm(org_user=interaction.user.id)
                            await msg.edit(embed=embed, view=confirm)
                            await confirm.wait()
                            if confirm.value:
                                embed = nextcord.Embed(title="Open Form", description=f"Press the button below to enter the name you want the select name to be for {role.mention} ({role.id})", colour=COLOUR_MAIN)
                                b = Open_Form(org_user=interaction.user.id, type="select name")
                                await msg.edit(embed=embed, view=b)
                                await b.wait()
                                i.append(b.name)
                            else:
                                i.append(role.name)
                            embed = nextcord.Embed(title="Custom Description", description=f"Do you want to give the select option a custom description for {role.mention} ({role.id})?", colour=COLOUR_MAIN)
                            confirm3 = Confirm(org_user=interaction.user.id)
                            await msg.edit(embed=embed, view=confirm3)
                            await confirm3.wait()
                            if confirm3.value:
                                embed = nextcord.Embed(title="Open Form", description=f"Press the button below to enter the description you want for {role.mention} ({role.id})", colour=COLOUR_MAIN)
                                c = Open_Form(org_user=interaction.user.id, type="select desc")
                                await msg.edit(embed=embed, view=c)
                                await c.wait()
                                i.append(c.description)
                            else:
                                i.append(None)
                            embed = nextcord.Embed(title="Custom Emoji", description=f"Do you want to give the select option a custom emoji for {role.mention} ({role.id})?", colour=COLOUR_MAIN)
                            confirm2 = Confirm(org_user=interaction.user.id)
                            await msg.edit(embed=embed, view=confirm2)
                            await confirm2.wait()
                            if confirm2.value:
                                embed = nextcord.Embed(title="Chose emoji", description=f"React to this message with the emoji you want to use for {role.mention} ({role.id})", colour=COLOUR_MAIN)
                                await msg.edit(embed=embed, view=None)
                                do = True
                                while do is True:
                                    try:
                                        reaction, e = await self.client.wait_for('reaction_add', timeout=600, check=check)
                                    except asyncio.TimeoutError:
                                        embed = create_error_embed(title="Timed out", description="This interaction has timed out.")
                                        await msg.edit(embed=embed)
                                        return
                                    await msgg.clear_reactions()
                                    if reaction.emoji in emojis:
                                        await msgg.reply("You can't use the same emoji more than once! React with another emoji you wish to use.", delete_after=5)
                                    else:
                                        emojis.append(reaction.emoji)
                                        i.append(reaction.emoji)
                                        do = False
                            else:
                                i.append(None)
                            i.append(role.id)
                            rlist.append(role.id)
                            info.append(i)

                        async def getoptions(info) -> List[nextcord.SelectOption]:
                            options: List[nextcord.SelectOption] = []
                            for i in info:
                                label = i[0] # role.name
                                description = i[1] # role.id
                                emoji = i[2]
                                value = i[3]
                                options.append(nextcord.SelectOption(label=label, value=value, description=description, emoji=emoji))
                            return options
                        selectoptions = await getoptions(info=info)
                        select = Dropdown_View(selectoptions=selectoptions)
                        if view.choice == "embed":
                            embed = nextcord.Embed(title=f"{view.rtitle}", description=f"{view.rdescription}", colour=COLOUR_MAIN)
                            content = None
                        elif view.choice == "msg":
                            content = view.rmsg
                            embed = None
                        rmsg = await channelview.rchannel.send(content=content, embed=embed, view=select)

                        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                        cur = conn.cursor()
                        cur.execute(f"INSERT INTO `reaction_main` (guild_id, message_id, channel_id, reaction_type, message_type, roles, select_type) VALUES ({interaction.guild.id}, {rmsg.id}, {channelview.rchannel.id}, '{type.type}', '{view.choice}', '{rlist}', '{t.t}')")
                        conn.commit()
                        await msg.edit(embed=create_success_embed(title="Success", description=f"Sucessfully created panel and sent it to {channelview.rchannel.mention}"), view=None)

            elif type.type == "reaction":
                channelview = Channel_Select(org_user=interaction.user.id)
                embed = nextcord.Embed(title="Select Channel", description="Which channel do you want to send the reaction role message to?", colour=COLOUR_MAIN)
                await msg.edit(embed=embed, view=channelview)
                await channelview.wait()
                if channelview.rchannel is None:
                    return
                roleview = Role_Select(org_user=interaction.user.id)
                embed = nextcord.Embed(title="Select Roles", description="Which roles do you want to be on the reaction role panel?", colour=COLOUR_MAIN)
                await msg.edit(embed=embed, view=roleview)
                await roleview.wait()
                if roleview.roles:
                    emojis = []
                    info = []
                    msgg = await msg.fetch()
                    def check(reaction, member):
                        return  reaction.message.channel == interaction.channel and member == interaction.user
                    if roleview.roles:
                        for role in roleview.roles:
                            embed = nextcord.Embed(title="Chose emoji", description=f"React to this message with the emoji you want to use for {role.mention} ({role.id})", colour=COLOUR_MAIN)
                            await msg.edit(embed=embed, view=None)
                            do = True
                            while do is True:
                                try:
                                    reaction, e = await self.client.wait_for('reaction_add', timeout=600, check=check)
                                except asyncio.TimeoutError:
                                    embed = create_error_embed(title="Timed out", description="This interaction has timed out.")
                                    await msg.edit(embed=embed)
                                    return
                                await msgg.clear_reactions()
                                if reaction.emoji in emojis:
                                    await msgg.reply("You can't use the same emoji more than once! React with another emoji you wish to use.", delete_after=5)
                                else:
                                    emojis.append(reaction.emoji)
                                    if isinstance(reaction.emoji, str):
                                        info.append([base64.b64encode(pickle.dumps(reaction.emoji)).decode("utf-8"), role.id])
                                    else:
                                        info.append([reaction.emoji.id, role.id])
                                    do = False
                        
                        if view.choice == "embed":
                            embed = nextcord.Embed(title=f"{view.rtitle}", description=f"{view.rdescription}", colour=COLOUR_MAIN)
                            content = None
                        elif view.choice == "msg":
                            content = view.rmsg
                            embed = None
                        rmsg = await channelview.rchannel.send(content=content, embed=embed)

                        for emoji in emojis:
                            await rmsg.add_reaction(emoji)

                        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                        cur = conn.cursor()
                        for i in info:
                            cur.execute("INSERT INTO `reaction_emojis` (guild_id, channel_id, msg_id, emoji_id, role_id) VALUES (%s, %s, %s, %s, %s)", (interaction.guild.id, channelview.rchannel.id, rmsg.id, i[0], i[1]))

                        conn.commit()
                        await msg.edit(embed=create_success_embed(title="Success", description=f"Successfully created and sent role reeaction message to {channelview.rchannel.mention}"))

        elif view.choice == "ownmsg":
            channelview = Channel_Select(org_user=interaction.user.id)
            embed = nextcord.Embed(title="Select Channel", description="Which channel is your message in?", colour=COLOUR_MAIN)
            await msg.edit(embed=embed, view=channelview)
            await channelview.wait()
            if channelview.rchannel is None:
                return
            messageidview = Message_Id(org_user=interaction.user.id)
            embed = nextcord.Embed(title="Get message id", description="Copy the messages id and then press the button below", colour=COLOUR_MAIN)
            await msg.edit(embed=embed, view=messageidview)
            await messageidview.wait()
            if messageidview.msgid is None:
                return
            
            conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM `reaction_emojis` WHERE msg_id = {messageidview.msgid}")
            data = cur.fetchall()
            conn.commit()
            if data:
                await msg.edit(embed=create_error_embed(title="Error", description="That message already has a reaction role panel on it!"), view=None)
                return
            
            try:
                ownmsg = await channelview.rchannel.fetch_message(int(messageidview.msgid))
            except NotFound:
                embed = create_error_embed(title="Error", description="Unable to find that message, ensure you enter the correct channel and message id and try again")
                await msg.edit(embed=embed, view=None)
                return
            roleview = Role_Select(org_user=interaction.user.id)
            embed = nextcord.Embed(title="Select Roles", description="Which roles do you want to be on the reaction role panel?", colour=COLOUR_MAIN)
            await msg.edit(embed=embed, view=roleview)
            await roleview.wait()
            emojis = []
            msgg = await msg.fetch()
            def check(reaction, member):
                return  reaction.message.channel == interaction.channel and member == interaction.user
            if roleview.roles:
                conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                cur = conn.cursor()
                for role in roleview.roles:
                    embed = nextcord.Embed(title="Chose emoji", description=f"React to this message with the emoji you want to use for {role.mention} ({role.id})", colour=COLOUR_MAIN)
                    await msg.edit(embed=embed, view=None)
                    do = True
                    while do is True:
                        try:
                            reaction, e = await self.client.wait_for('reaction_add', timeout=600, check=check)
                        except asyncio.TimeoutError:
                            embed = create_error_embed(title="Timed out", description="This interaction has timed out.")
                            await msg.edit(embed=embed)
                            return
                        await msgg.clear_reactions()
                        if reaction.emoji in emojis:
                            await msgg.reply("You can't use the same emoji more than once! React with another emoji you wish to use.", delete_after=5)
                        else:
                            cur.execute("INSERT INTO `reaction_emojis` (guild_id, channel_id, msg_id, emoji_id, role_id) VALUES (%s, %s, %s, %s, %s)", (interaction.guild.id, channelview.rchannel.id, ownmsg.id, reaction.emoji.id if not isinstance(reaction.emoji, str) else base64.b64encode(pickle.dumps(reaction.emoji)).decode("utf-8"), role.id))
                            emojis.append(reaction.emoji)
                            do = False
                conn.commit()
                
                await ownmsg.clear_reactions()

                for emoji in emojis:
                    await ownmsg.add_reaction(emoji)
                
                await msg.edit(embed=create_success_embed(title="Success", description=f"Successfully created reaction role menu on selected message in {channelview.rchannel.mention}"))

        
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.client.add_view(Button_View(startup=True))
            print(color_message(message="Loaded Button_View view", color="blue"))
        except Exception as e:
            print(e)
            print(color_message(message="Failed to load Button_View view", color="yellow"))
        try:
            self.client.add_view(Dropdown_View(startup=True))
            print(color_message(message="Loaded Dropdown_View view", color="blue"))
        except Exception as e:
            print(e)
            print(color_message(message="Failed to load Dropdown_View view", color="yellow"))


def setup(client: Bot):
    client.add_cog(cog=Reactionroles(client=client))
import nextcord
from utils import *
import pymysql
from constants import DBENDPOINT, DBNAME, DBUSER, DBPASS, DBPORT
from typing import List, Union

class channelselect(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(placeholder="Select a channel", min_values=1, max_values=1, channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.news])

    async def callback(self, interaction: nextcord.Interaction):
        self.view.rchannel = self.values[0]
        self.view.stop()

class Channel_Select(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=600)
        self.add_item(channelselect())
        self.rchannel = None
        self.org_user = org_user

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't use this!", ephemeral=True)
            return False
        
        return True

class roleselect(nextcord.ui.RoleSelect):
    def __init__(self):
        super().__init__(placeholder="Select a role", min_values=1, max_values=20)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.roles.extend(self.values)
        self.view.stop()

class Role_Select(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=600)
        self.add_item(roleselect())
        self.roles = []
        self.org_user = org_user

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't use this!", ephemeral=True)
            return False
        
        return True

class Msgform(nextcord.ui.Modal):
    def __init__(self, type: str):
        super().__init__(title="Create Message", timeout=None)
        self.type = type

        if type == "msg":
            self.msg = nextcord.ui.TextInput(
                label = "What is your message?",
                placeholder = "Tip: To mention roles do <@&roleid> (e.g. <@&777102282218536990>)",
                style=nextcord.TextInputStyle.paragraph,
                min_length=1,
                max_length=2000,
                required=True
            )
            self.add_item(self.msg)

        elif type == "embed":

            self.embedtitle = nextcord.ui.TextInput(
                  label = "What do you want the title to be?",
                  placeholder = "Tip: Up to 256 characters!",
                  style=nextcord.TextInputStyle.short,
                  min_length=1,
                  max_length=256,
                  required=True
            )
            self.add_item(self.embedtitle)

            self.embeddescription = nextcord.ui.TextInput(
                  label = "What do you want the description to be?",
                  placeholder = "Tip: To mention roles do <@&roleid> (e.g. <@&777102282218536990>)",
                  style=nextcord.TextInputStyle.paragraph,
                  min_length=1,
                  max_length=4000,
                  required=True
            )
            self.add_item(self.embeddescription)

    async def callback(self, interaction: nextcord.Interaction):
        if self.type == "msg":
            self.rmsg = self.msg.value
        elif self.type == "embed":
            self.rtitle = self.embedtitle.value
            self.rdescription = self.embeddescription.value
        self.stop()

class Options(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=None)
        self.choice = None
        self.org_user = org_user

    @nextcord.ui.button(label="Embed message", style=nextcord.ButtonStyle.blurple)
    async def embed(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.choice = "embed"
        modal = Msgform(type="embed")
        await interaction.response.send_modal(modal=modal)
        await modal.wait()
        if (not modal.rtitle is None) and (not modal.rdescription is None):
            self.rtitle = modal.rtitle
            self.rdescription = modal.rdescription
            self.stop()
        else:
            self.choice = None

    @nextcord.ui.button(label="Text message", style=nextcord.ButtonStyle.blurple)
    async def msg(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.choice = "msg"
        modal = Msgform(type="msg")
        await interaction.response.send_modal(modal=modal)
        await modal.wait()
        if not modal.rmsg is None:
            self.rmsg = modal.rmsg
            self.stop()
        else:
            self.choice = None

    @nextcord.ui.button(label="Pre-exisiting message", style=nextcord.ButtonStyle.blurple, disabled=False)
    async def own_msg(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.choice = "ownmsg"
        self.stop()

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't use this!", ephemeral=True)
            return False
        
        return True

class Options2(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=600)
        self.type = None
        self.org_user = org_user

    @nextcord.ui.button(label="Reactions", style=nextcord.ButtonStyle.blurple, disabled=False)
    async def reaction(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.type = "reaction"
        self.stop()

    @nextcord.ui.button(label="Buttons", style=nextcord.ButtonStyle.blurple)
    async def buttons(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.type = "button"
        self.stop()

    @nextcord.ui.button(label="Dropdown", style=nextcord.ButtonStyle.blurple)
    async def dropdown(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.type = "dropdown"
        self.stop()

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't use this!", ephemeral=True)
            return False
        
        return True

class Button(nextcord.ui.Button):
    def __init__(self, button_num: int, role=None, emoji=None, colour=nextcord.ButtonStyle.blurple):
        if role:
            super().__init__(style=colour, custom_id=f"{button_num}", label=role, emoji=emoji)
        else:
            super().__init__(style=colour, custom_id=f"{button_num}", label="startup")

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True, with_message=True)
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `reaction_main` WHERE message_id = {interaction.message.id}")
        data = cur.fetchall()
        data = data[0][5]
        roleids = data.replace("[", "").replace("]", "").replace(",", "").split(" ")
        role = interaction.guild.get_role(int(roleids[int(self.custom_id)]))
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.send(embed=create_success_embed(title="Success!", description=f"Successfully removed {role.mention} from you"), ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.send(embed=create_success_embed(title="Success!", description=f"Successfully added {role.mention} to you"), ephemeral=True)
        conn.commit()
        
class Button_View(nextcord.ui.View):
    def __init__(self, info=None, startup=False):
        if info is None:
            info = []
        super().__init__(timeout=None)
        button_num = 0
        for i in info:
            self.add_item(Button(role=i[0], emoji=i[1],button_num=button_num, colour=i[2]))
            button_num += 1

        if startup:
            while button_num < 21:
                self.add_item(Button(button_num=button_num))
                button_num += 1

class Dropdown(nextcord.ui.Select):
    def __init__(self, selectoptions: List[nextcord.SelectOption]):
        super().__init__(placeholder="Select a role", custom_id="rselect", options=selectoptions)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)
        role = interaction.guild.get_role(int(self.values[0]))
        if role:
            try:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.send(embed=create_success_embed(title="Success!", description=f"Successfully removed {role.mention} from you"), ephemeral=True)
                else:
                    conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM `reaction_main` WHERE message_id = %s", interaction.message.id)
                    data = cur.fetchall()
                    conn.commit()
                    user_role_ids = [str(role.id) for role in interaction.user.roles]
                    if data[0][6] == "single":
                        data = data[0][5]
                        roleids = data.replace("[", "").replace("]", "").replace(",", "").split(" ")
                        common_roles = list(set(user_role_ids) & set(roleids))
                        for rolezid in common_roles:
                            rolez = interaction.guild.get_role(int(rolezid))
                            await interaction.user.remove_roles(rolez)
                    await interaction.user.add_roles(role)
                    await interaction.send(embed=create_success_embed(title="Success!", description=f"Successfully added {role.mention} to you"), ephemeral=True)
            except Exception as e:
                print(e)
                await interaction.send(embed=create_error_embed(title=f"Invalid Permissions", description=f"I do not have permission to give you this role. Please inform the server administrators of this issue."), ephemeral=True)

class Dropdown_View(nextcord.ui.View):
    def __init__(self, selectoptions: List[nextcord.SelectOption] = None, startup: bool = False):
        if selectoptions is None:
            selectoptions = []
        super().__init__(timeout=None)
        if startup:
            selectoptions.append(nextcord.SelectOption(label="startup", value=0))
        self.add_item(Dropdown(selectoptions=selectoptions))


class MessageIdModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Message Id", timeout=None)

        self.question = nextcord.ui.TextInput(
            label = "What is the message id?",
            placeholder = "Paste the message id here",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=30,
            required=True
        )
        self.add_item(self.question)

    async def callback(self, interaction: nextcord.Interaction):
        self.msgid = self.question.value
        self.stop()
        

class Message_Id(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=None)
        self.msgid = None
        self.org_user = org_user

    @nextcord.ui.button(label="Input", style=nextcord.ButtonStyle.blurple)
    async def reaction(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = MessageIdModal()
        await interaction.response.send_modal(modal=modal)
        await modal.wait()
        if not modal.msgid is None:
            self.msgid = modal.msgid
            self.stop()
        else:
            self.choice = None

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't use this!", ephemeral=True)
            return False
        
        return True
    
class Customisation(nextcord.ui.Modal):
    def __init__(self, type: str):
        super().__init__(title="Customize your panel", timeout=None)
        self.type = type
        self.name = None
        self.description = None

        if type == "button":
            self.question = nextcord.ui.TextInput(
                label = "What do you want the button message to be?",
                placeholder = "Enter your message here",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=30,
                required=True
            )
            self.add_item(self.question)
        
        if type == "select name":
            self.q = nextcord.ui.TextInput(
                label = "What do you want the name to be",
                placeholder = "Enter your message here",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=30,
                required=True
            )
            self.add_item(self.q)

        if type == "select desc":

            self.z = nextcord.ui.TextInput(
                label = "What do you want the description to be?",
                placeholder = "Enter your message here",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=50,
                required=True
            )
            self.add_item(self.z)

    async def callback(self, interaction: nextcord.Interaction):
        if self.type == "button":
            self.name = self.question.value
        elif self.type == "select name":
            self.name = self.q.value
        elif self.type == "select desc":
            self.description = self.z.value
        self.stop()

class Open_Form(nextcord.ui.View):
    def __init__(self, org_user:int, type: str):
        super().__init__(timeout=None)
        self.type = type
        self.org_user = org_user
        self.name = None
        self.description = None

    @nextcord.ui.button(label="Open Form", style=nextcord.ButtonStyle.blurple)
    async def embed(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = Customisation(type=self.type)
        await interaction.response.send_modal(modal=modal)
        await modal.wait()
        if (self.type == "button") and (modal.name is not None):
            self.name = modal.name
            self.stop()
        elif (self.type == "select name") and (modal.name is not None):
            self.name = modal.name
            self.stop()
        elif (self.type == "select desc") and (modal.description is not None):
            self.description = modal.description
            self.stop()

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't use this!", ephemeral=True)
            return False
        
        return True
    
class Colour_Choice(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=None)
        self.colour = None
        self.org_user = org_user

    @nextcord.ui.button(label="Blurple", style=nextcord.ButtonStyle.blurple)
    async def b(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.colour = nextcord.ButtonStyle.blurple
        self.stop()
    
    @nextcord.ui.button(label="Grey", style=nextcord.ButtonStyle.grey)
    async def g(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.colour = nextcord.ButtonStyle.grey
        self.stop()

    @nextcord.ui.button(label="Green", style=nextcord.ButtonStyle.green)
    async def gr(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.colour = nextcord.ButtonStyle.green
        self.stop()

    @nextcord.ui.button(label="Red", style=nextcord.ButtonStyle.red)
    async def r(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.colour = nextcord.ButtonStyle.red
        self.stop()

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't use this!", ephemeral=True)
            return False
        
        return True
    
class Select_Type(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=None)
        self.t = None
        self.org_user = org_user

    @nextcord.ui.button(label="Single", style=nextcord.ButtonStyle.blurple)
    async def single(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.t = "single"
        self.stop()
    
    @nextcord.ui.button(label="Multiple", style=nextcord.ButtonStyle.grey)
    async def g(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.t = "multiple"
        self.stop()
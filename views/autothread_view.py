import nextcord
from bot.bot import Bot
from db_handler.schemas import *
from typing import List, Union
from constants import COLOUR_MAIN
from utils import create_error_embed, create_success_embed

class AutoThreadView(nextcord.ui.View):
    def __init__(self, showcreate:bool, showedit:bool, org_user:int, client):
        super().__init__()
        self.showcreate = showcreate
        self.showedit = showedit
        self.org_user = org_user
        self.client = client

    @nextcord.ui.button(label = "Create new autothread", style = nextcord.ButtonStyle.green)
    async def create_autothread(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.showcreate:
            data: List[AutoThreadMain] = Bot.db.get_data(table="autothread", guild_id=interaction.guild.id)
            channelarray = Options(org_user=interaction.user.id)
            embed=nextcord.Embed(title="Autothread Create", description=f"Choose what channel you want to have autothread enabled by selecting it below.", colour=COLOUR_MAIN)
            await interaction.edit(embed=embed, view=channelarray)
            await channelarray.wait()
            channel = channelarray.values[0]
            data: List[AutoThreadMain] = Bot.db.get_data(table="autothread", guild_id=interaction.guild.id, channel_id=channel.id)
            if data:
                await interaction.edit_original_message(embed=create_error_embed(title="Error!", description=f"{channel.mention} is already an autothread channel."), view=None)
                return
            data: List[AutoThreadMain] = Bot.db.create_data(table="autothread", guild_id=interaction.guild.id, channel_id=channel.id)
            await interaction.edit_original_message(embed=create_success_embed(title="Autothread Channel", description=f"{channel.mention} has been set as an autothread channel. I will now create a thread for every new message sent in this channel."), view=None)
        else:
            await interaction.send(embed=create_error_embed(title="Error!", description="You have reached the maximum amount of autothread channels (**3**)"))
    
    @nextcord.ui.button(label = "Delete an existing autothread", style = nextcord.ButtonStyle.red)
    async def edit_autothread(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.showedit:
            data: List[AutoThreadMain] = Bot.db.get_data(table="autothread", guild_id=interaction.guild.id)
            optiontext = ""
            options = []
            for i in range(len(data)):
                optiontext = optiontext + f"{i+1}: `Channel ID` {data[i].channel_id}\n"
                options.append(str(i+1))
            embed = nextcord.Embed(title="Delete autothread", description=f"Choose which autothread you want to delete from the list below:\n\n {optiontext}", colour=COLOUR_MAIN)
            chosenoption = List_Options_AutoThread(self.org_user, options)
            msg = await interaction.send(embed=embed, view=chosenoption)
            await chosenoption.wait()
            option = data[(int(chosenoption.values[0])-1)]
            Bot.db.delete_data(table="autothread", data=option)
            await interaction.edit_original_message(embed=create_success_embed(title="Success!", description="I have deleted the selected autothread. I will no longer create threads for messages sent in that channel"), view=None)
        else:
            await interaction.send("You don't have an exisiting autothread to edit.", ephemeral=True)


    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True


class List_Select_AutoThread(nextcord.ui.Select):
    def __init__(self, options: List[str], placeholder: str = "Select an option", max_values: int = 1):
        super().__init__(options=[nextcord.SelectOption(label=i, description=i) for i in options], placeholder=placeholder, max_values=max_values)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)

class List_Options_AutoThread(nextcord.ui.View):
    def __init__(self, org_user:int, options: List[str], placeholder: str = "Select an option", max_values: int = 1):
        super().__init__(timeout=120)
        self.values = []
        self.org_user = org_user
        for i in range(0, len(options), 25):
            self.add_item(List_Select_AutoThread(options=options[i:i+25], placeholder=placeholder, max_values=max_values))

    @nextcord.ui.button(label="Complete", style=nextcord.ButtonStyle.green)
    async def complete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

class AutoThreadInfoView(nextcord.ui.View):

    def __init__(self):
        super().__init__()
        self.add_item(nextcord.ui.Button(label=f"Auto Thread Configured By Server Administrators", style = nextcord.ButtonStyle.grey, disabled=True))


class ChannelList(nextcord.ui.ChannelSelect):
      def __init__(self):
        super().__init__(custom_id="test", placeholder="Select a channel", min_values=1, max_values=1, channel_types=[nextcord.ChannelType.text])

      async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)
        self.view.stop()

class Options(nextcord.ui.View):
    def __init__(self, org_user:int):
        super().__init__(timeout=30)
        self.add_item(ChannelList())
        self.values = []
        self.choice = None
        self.org_user = org_user

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True
import nextcord
from nextcord import Interaction
from constants import COLOUR_MAIN
from bot.bot import Bot
from typing import List, Union
from db_handler.schemas import *



class Default_View(nextcord.ui.View):
    def __init__(self, org_user: int, timeout: int = 600):
        super().__init__(timeout=timeout)
        self.org_user = org_user

    async def on_timeout(self):
        self.stop()
        self.clear_items()

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True


class ModerationConfigView(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=120)
        self.org_user = org_user
        
    @nextcord.ui.button(label="Set muted role", style=nextcord.ButtonStyle.blurple, disabled=False)
    async def set_muted_role(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.defer(with_message=False)
        select_role = Role_Select(org_user = self.org_user)
        await interaction.message.edit(embed=nextcord.Embed(title=f"Set muted role", description=f"Use the menu below to choose your muted role or remove your current one.", colour=COLOUR_MAIN), view=select_role)
        await select_role.wait()
        data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=interaction.guild.id)
        data = data[0]
        if select_role.value is None:
            data.muted_role = None
            role = None
            Bot.db.update_data("moderation_main", data=data)
        else:
            role = interaction.guild.get_role(int(select_role.value))
            data.muted_role = role.id
            Bot.db.update_data("moderation_main", data=data)

        config_view = ModerationConfigView(org_user=interaction.user.id)
        embed=nextcord.Embed(title=f"Moderation Config", description=f"You can edit your moderation configuration using the buttons below.\n\nMuted Role: {f'<@&{data.muted_role}>' if not data.muted_role is None else 'None'}\nModeration Log Channel: {f'<#{data.mod_log_channel}>' if not data.mod_log_channel is None else 'None'}", colour=COLOUR_MAIN)
        await interaction.message.edit(embed=embed, view=config_view)
    
    @nextcord.ui.button(label="Set moderation log channel", style=nextcord.ButtonStyle.blurple)
    async def right_arrow(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.defer(with_message=False)
        select_channel = Channel_Select(org_user = self.org_user)
        await interaction.message.edit(embed=nextcord.Embed(title=f"Set moderation log channel", description=f"Use the menu below to choose your moderation log channel or remove your current one.", colour=COLOUR_MAIN), view=select_channel)
        await select_channel.wait()
        data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=interaction.guild.id)
        data = data[0]
        if select_channel.value is None:
            data.mod_log_channel = None
            channel = None
            Bot.db.update_data("moderation_main", data=data)
        else:
            channel = interaction.guild.get_channel(int(select_channel.value))
            data.mod_log_channel = channel.id
            Bot.db.update_data("moderation_main", data=data)

        config_view = ModerationConfigView(org_user=interaction.user.id)
        embed=nextcord.Embed(title=f"Moderation Config", description=f"You can edit your moderation configuration using the buttons below.\n\nMuted Role: {f'<@&{data.muted_role}>' if not data.muted_role is None else 'None'}\nModeration Log Channel: {f'<#{data.mod_log_channel}>' if not data.mod_log_channel is None else 'None'}", colour=COLOUR_MAIN)
        await interaction.message.edit(embed=embed, view=config_view)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        return True
        
            

class Channel_Select(Default_View):
    def __init__(self, org_user: int):
        super().__init__(timeout=120, org_user=org_user)
        self.add_item(ChannelList())
        self.value = None
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()
        self.clear_items()
    @nextcord.ui.button(label=f"Clear moderation log channel", style=nextcord.ButtonStyle.grey, row=0)
    async def clear_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = None
        self.stop()
        self.clear_items()

class ChannelList(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(custom_id="channel_list", placeholder="Select channel", min_values=1, max_values=1, row=1)
    async def callback(self, interaction: nextcord.Interaction):
        self.view.value = self.values[0].id

class Role_Select(Default_View):
    def __init__(self, org_user: int):
        super().__init__(timeout=120, org_user=org_user)
        self.add_item(RoleList())
        self.value = None
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()
        self.clear_items()
    @nextcord.ui.button(label=f"Clear muted role", style=nextcord.ButtonStyle.grey, row=0)
    async def clear_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = None
        self.stop()
        self.clear_items()  

class RoleList(nextcord.ui.RoleSelect):
    def __init__(self):
        super().__init__(custom_id="role_list", placeholder="Select role", min_values=1, max_values=1, row=1)
    async def callback(self, interaction: nextcord.Interaction):
        self.view.value = self.values[0].id
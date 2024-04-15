import nextcord, re, ast
from bot.bot import Bot
from constants import COLOUR_MAIN
from typing import List, Union
from utils import create_error_embed, create_success_embed
import numpy as np
from db_handler.schemas import *

class LevelConfig(nextcord.ui.View):
    def __init__(self, user: nextcord.User, client):
        super().__init__()
        self.user = user
        self.client = client


    @nextcord.ui.button(label = "Enabled", style = nextcord.ButtonStyle.blurple)
    async def levelling_config_enabled(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.enabled:
            maindata.enabled = False
            await interaction.send(embed=create_success_embed(title=f"Levelling Disabled", description=f"I have disabled levelling for this guild"), ephemeral=True)
        else:
            maindata.enabled = True
            await interaction.send(embed=create_success_embed(title=f"Levelling Enabled", description=f"I have enabled levelling for this guild"), ephemeral=True)

        Bot.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Change minimum XP", style=nextcord.ButtonStyle.blurple, row=1)
    async def levelling_config_min_xp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        changemodal = xp_min_change()
        await interaction.response.send_modal(changemodal)
        await changemodal.wait()
        newxp = changemodal.xp
        try:
            newxp = int(newxp)
        except ValueError:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum XP must be an integer"), ephemeral=True)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.max_xp < newxp:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum XP cannot be greater than the maximum XP"), ephemeral=True)
            return
        elif newxp < 1:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum XP must be at least `1`"), ephemeral=True)
            return
        elif newxp > 100:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum XP cannot be more than `100`"), ephemeral=True)
            return
        else:
            maindata.min_xp = newxp
            await interaction.send(embed=create_success_embed(title=f"Minimum XP Set", description=f"I have set the minimum XP to `{newxp}`"), ephemeral=True)
            Bot.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Change maximum XP", style=nextcord.ButtonStyle.blurple, row=1)
    async def levelling_config_max_vc_xp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        changemodal = xp_max_change()
        await interaction.response.send_modal(changemodal)
        await changemodal.wait()
        newxp = changemodal.xp
        try:
            newxp = int(newxp)
        except ValueError:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum XP must be an integer"), ephemeral=True)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.min_xp > newxp:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum XP cannot be less than the minimum XP"), ephemeral=True)
            return
        elif newxp < 1:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum XP must be at least `1`"), ephemeral=True)
            return
        elif newxp > 150:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum XP cannot be more than `150`"), ephemeral=True)
            return
        else:
            maindata.max_xp = newxp
            await interaction.send(embed=create_success_embed(title=f"Maximum XP Set", description=f"I have set the maximum XP to `{newxp}`"), ephemeral=True)
            Bot.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Change Chat XP Cooldown", style=nextcord.ButtonStyle.blurple, row=1)
    async def levelling_config_cooldown(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        changemodal = cooldown()
        await interaction.response.send_modal(changemodal)
        await changemodal.wait()
        newcd = changemodal.cooldown
        try:
            newcd = int(newcd)
        except ValueError:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The cooldown must be a number"), ephemeral=True)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if newcd < 10:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum cooldown must be at least 10 seconds"), ephemeral=True)
            return
        elif newcd > 120:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum cooldown cannot be above 120 seconds"), ephemeral=True)
            return
        else:
            maindata.cooldown = newcd
            await interaction.send(embed=create_success_embed(title=f"Chat XP Cooldown Set", description=f"I have set the new chat xp gain cooldown `{newcd}`"), ephemeral=True)
            Bot.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Change minimum voice XP", style=nextcord.ButtonStyle.blurple, row=2)
    async def levelling_config_min_vc_xp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        changemodal = xp_min_change()
        await interaction.response.send_modal(changemodal)
        await changemodal.wait()
        newxp = changemodal.xp
        try:
            newxp = int(newxp)
        except ValueError:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum voice XP must be an integer"), ephemeral=True)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.max_vc_xp < newxp:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum voice XP cannot be greater than the maximum XP"), ephemeral=True)
            return
        elif newxp < 1:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum voice XP must be at least `1`"), ephemeral=True)
            return
        elif newxp > 100:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The minimum voice XP cannot be more than `100`"), ephemeral=True)
            return
        else:
            maindata.min_vc_xp = newxp
            await interaction.send(embed=create_success_embed(title=f"Minimum Voice XP Set", description=f"I have set the minimum voice XP to `{newxp}`"), ephemeral=True)
            Bot.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Change maximum voice XP", style=nextcord.ButtonStyle.blurple, row=2)
    async def levelling_config_max_voice_xp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        changemodal = xp_max_change()
        await interaction.response.send_modal(changemodal)
        await changemodal.wait()
        newxp = changemodal.xp
        try:
            newxp = int(newxp)
        except ValueError:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum voice XP must be an integer"), ephemeral=True)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.min_vc_xp > newxp:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum voice XP cannot be less than the minimum XP"), ephemeral=True)
            return
        elif newxp < 1:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum voice XP must be at least `1`"), ephemeral=True)
            return
        elif newxp > 150:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The maximum voice XP cannot be more than `150`"), ephemeral=True)
            return
        else:
            maindata.max_vc_xp = newxp
            await interaction.send(embed=create_success_embed(title=f"Maximum Voice XP Set", description=f"I have set the maximum voice XP to `{newxp}`"), ephemeral=True)
            Bot.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label = "Levels System (Mee6/BigBot)", style = nextcord.ButtonStyle.blurple, row=2)
    async def levelling_config_mee6(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.mee6_levels:
            maindata.mee6_levels = False
            await interaction.send(embed=create_success_embed(title="Levels system changed", description="I have changed the levels system from Mee6 to BigBot (default)."), ephemeral=True)
        else:
            maindata.mee6_levels = True
            await interaction.send(embed=create_success_embed(title="Levels system changed", description="I have changed the levels system from BigBot (default) to Mee6."), ephemeral=True)

        Bot.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Change the reward earned message", style=nextcord.ButtonStyle.blurple, row=3)
    async def levelling_config_reward_earned_message(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        changemodal = reward_earned_message_change()
        await interaction.response.send_modal(changemodal)
        await changemodal.wait()
        newmsg = changemodal.newmsg
        maindata: List[LevelMain] = self.client.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        maindata.reward_message = newmsg
        self.client.db.update_data(table="level_main", data=maindata)
        await interaction.send(embed=create_success_embed(title=f"Reward earned message set", description=f"I have set the reward up message to ``{newmsg}``"), ephemeral=True)

        
        maindata: List[LevelMain] = self.client.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Change the level up message", style=nextcord.ButtonStyle.blurple, row=3)
    async def levelling_config_level_up_message(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        changemodal = level_up_message_change()
        await interaction.response.send_modal(changemodal)
        await changemodal.wait()
        newmsg = changemodal.newmsg
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        maindata.level_up_message = newmsg
        Bot.db.update_data(table="level_main", data=maindata)
        await interaction.send(embed=create_success_embed(title=f"Level up message set", description=f"I have set the level up message to ``{newmsg}``"), ephemeral=True)

        
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Change the level up channel", style=nextcord.ButtonStyle.blurple, row=3)
    async def levelling_config_level_up_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        channel_selected = Channel_Select(interaction.user.id)
        embed = nextcord.Embed(title="Select channel to send", description="Select channel to send level up messages to. Click only submit to not send any messages and click the Currently typing channel button to send the level up message to the channel the user is typing in", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=channel_selected, ephemeral=True)
        await channel_selected.wait()
        selected_channel = channel_selected.values[0]
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if not selected_channel:
            maindata.level_up_channel = None
            channeltext = None
        elif selected_channel == "current":
            maindata.level_up_channel = "current"
            channeltext = "Currently typing channel"
        else:
            channeltext = selected_channel.mention
            maindata.level_up_channel = selected_channel.id
        Bot.db.update_data(table="level_main", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"Level up channel set", description=f"I have set the level up channel to {channeltext}"), view=None)

        
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label = "Drops Enabled", style = nextcord.ButtonStyle.blurple, row=0)
    async def levelling_config_drops_enabled(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.drops:
            maindata.drops = False
            await interaction.send(embed=create_success_embed(title=f"Drops Disabled", description=f"I have disabled XP drops for this guild"), ephemeral=True)
        else:
            maindata.drops = True
            await interaction.send(embed=create_success_embed(title=f"Drops Enabled", description=f"I have enabled XP drops for this guild"), ephemeral=True)

        Bot.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        if maindata.mee6_levels:
            level_system = "Mee6"
        else:
            level_system = "BigBot (Default)"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\nLevels System: {level_system}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label = "Stackable Rewards", style = nextcord.ButtonStyle.blurple, row=3)
    async def stackable_rewards_enabled(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = self.client.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.stackable_rewards:
            maindata.stackable_rewards = False
            await interaction.send(embed=create_success_embed(title=f"Stackable Rewards Disabled", description=f"I have disabled Stackable Rewards for this guild"), ephemeral=True)
        else:
            maindata.stackable_rewards = True
            await interaction.send(embed=create_success_embed(title=f"Stackable Rewards Enabled", description=f"I have enabled Stackable Rewards for this guild"), ephemeral=True)

        self.client.db.update_data(table="level_main", data=maindata)

        maindata: List[LevelMain] = self.client.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label = "Customise card settings", style = nextcord.ButtonStyle.grey, row=4)
    async def card_config_settings(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        embed = nextcord.Embed(title=f"{interaction.guild.name} card config settings", colour=COLOUR_MAIN)
        embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
        embed.set_footer(text="Click the 'settings info' button to see what each option changes")
        await interaction.edit(embed=embed, view=CardConfig(self.user, self.client))

    @nextcord.ui.button(label = "Manage no XP channels", style = nextcord.ButtonStyle.grey, row=4)
    async def manage_no_xp_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        noxpchannelstext = ""
        if maindata.no_xp_channels:
            for channel in np.asarray(np.matrix(maindata.no_xp_channels))[0]:
                noxpchannelstext+=f"\n- <#{channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} XP Channel Management", description=f"Current No XP channels:\n\n{noxpchannelstext}", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=NoXPChannelsConfig(self.user, self.client))

    @nextcord.ui.button(label = "Manage no XP roles", style = nextcord.ButtonStyle.grey, row=4)
    async def manage_no_xp_roles(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        noxpchannelstext = ""
        if maindata.no_xp_roles:
            for channel in np.asarray(np.matrix(maindata.no_xp_roles))[0]:
                noxpchannelstext+=f"\n- <@&{channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} XP Roles Management", description=f"Current No XP roles:\n\n{noxpchannelstext}", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=NoXPRolesConfig(self.user, self.client))
        

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self.user.id == interaction.user.id
    


    

class xp_min_change(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Change minimum XP", timeout=None)
        self.xp = nextcord.ui.TextInput(
            label = "What is the new minimum XP",
            placeholder = "This can't be more than the maximum XP!",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=10,
            required=True
        )
        self.add_item(self.xp)


    async def callback(self, interaction: nextcord.Interaction):
        self.xp = self.xp.value
        self.stop()

class xp_max_change(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Change maximum XP", timeout=None)
        self.xp = nextcord.ui.TextInput(
            label = "What is the new maximum XP",
            placeholder = "This can't be less than the minimum XP!",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=10,
            required=True
        )
        self.add_item(self.xp)


    async def callback(self, interaction: nextcord.Interaction):
        self.xp = self.xp.value
        self.stop()

class cooldown(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Change Chat XP Cooldown", timeout=None)
        self.cooldown = nextcord.ui.TextInput(
            label = "What is the new chat xp cooldown",
            placeholder = "Needs to be at least 10 seconds, maximum 120 seconds",
            style=nextcord.TextInputStyle.short,
            min_length=2,
            max_length=3,
            required=True
        )
        self.add_item(self.cooldown)


    async def callback(self, interaction: nextcord.Interaction):
        self.cooldown = self.cooldown.value
        self.stop()

class level_up_message_change(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Change level up message", timeout=None)
        self.newmsg = nextcord.ui.TextInput(
            label = "What is the new level up message?",
            placeholder = "{$user} = user who leveled up\n{$new_level} = The users new level\n{$old_level} = The users old level",
            style=nextcord.TextInputStyle.paragraph,
            min_length=1,
            max_length=1000,
            required=True
        )
        self.add_item(self.newmsg)


    async def callback(self, interaction: nextcord.Interaction):
        self.newmsg = self.newmsg.value
        self.stop()

class reward_earned_message_change(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Change reward earned message", timeout=None)
        self.newmsg = nextcord.ui.TextInput(
            label = "What is the new reward earned message?",
            placeholder = "{$role} = Role earned\n{$user} = User\n{$new} = User's new level\n{$old} = User's old level",
            style=nextcord.TextInputStyle.paragraph,
            min_length=1,
            max_length=1000,
            required=True
        )
        self.add_item(self.newmsg)


    async def callback(self, interaction: nextcord.Interaction):
        self.newmsg = self.newmsg.value
        self.stop()


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

class Channel_Select(Default_View):
    def __init__(self, org_user: int):
        super().__init__(timeout=120, org_user=org_user)
        self.add_item(ChannelList())
        self.values = []
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.values:
            self.values = [False]
            self.stop()
            self.clear_items()
    
        self.stop()
        self.clear_items()
    @nextcord.ui.button(label=f"Currently typing channel", style=nextcord.ButtonStyle.green, row=0)
    async def current_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.values = ["current"]
        self.stop()
        self.clear_items()

class ChannelList(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(custom_id="channel_list", placeholder="Select channel", min_values=1, max_values=1, row=1)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values = self.values


class CardConfig(nextcord.ui.View):
    def __init__(self, user: nextcord.User, client):
        super().__init__()
        self.user = user
        self.client = client


    @nextcord.ui.button(label = "Set background colour", style = nextcord.ButtonStyle.blurple)
    async def levelling_card_background(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        embed = nextcord.Embed(title=f"Set card background colour", description=f"Using the dropdown below, select what colour you want your card background to be. Click the default button to set it to default", colour=COLOUR_MAIN)
        cardselect = CardBackgroundConfig(self.user, self.client, maindata.background_color)
        await interaction.edit(embed=embed, view=cardselect)
        await cardselect.wait()
        cardselected = cardselect.chosen
        maindata.background_color = cardselected
        newdata = Bot.db.update_data(table="level_main", data=maindata)
        embed = nextcord.Embed(title=f"{interaction.guild.name} card config settings", colour=COLOUR_MAIN)
        embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
        embed.set_footer(text="Click the 'settings info' button to see what each option changes")
        await interaction.edit(embed=embed, view=CardConfig(self.user, self.client))

    @nextcord.ui.button(label = "Set main colour", style = nextcord.ButtonStyle.blurple)
    async def main_colour(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        colourselect = SetColour()
        await interaction.response.send_modal(colourselect)
        await colourselect.wait()
        colourvalid = colourselect.match
        colour_hex = colourselect.hex_code
        if not colourvalid:
            await interaction.send(embed=create_error_embed(title=f"Invalid hex code", description=f"That was an invalid hex code. Use https://colorpicker.me/ to get the hex code for a colour you like!"), ephemeral=True)
            embed = nextcord.Embed(title=f"{interaction.guild.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfig(self.user, self.client))
        else:
            if colour_hex == "default":
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/43a1e8/100x100", ephemeral=True)
            else:
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/{colour_hex.replace('#', '')}/100x100", ephemeral=True)
            maindata.main_color = colour_hex
            newdata = Bot.db.update_data(table="level_main", data=maindata)
            embed = nextcord.Embed(title=f"{interaction.guild.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfig(self.user, self.client))
    @nextcord.ui.button(label = "Set primary font colour", style = nextcord.ButtonStyle.blurple)
    async def primary_font_colour(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        colourselect = SetColour()
        await interaction.response.send_modal(colourselect)
        await colourselect.wait()
        colourvalid = colourselect.match
        colour_hex = colourselect.hex_code
        if not colourvalid:
            await interaction.send(embed=create_error_embed(title=f"Invalid hex code", description=f"That was an invalid hex code. Use https://colorpicker.me/ to get the hex code for a colour you like!"), ephemeral=True)
            embed = nextcord.Embed(title=f"{interaction.guild.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfig(self.user, self.client))
        else:
            if colour_hex == "default":
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/ffffff/100x100", ephemeral=True)
            else:
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/{colour_hex.replace('#', '')}/100x100", ephemeral=True)
            maindata.primary_font_color = colour_hex
            newdata = Bot.db.update_data(table="level_main", data=maindata)
            embed = nextcord.Embed(title=f"{interaction.guild.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfig(self.user, self.client))
    @nextcord.ui.button(label = "Set secondary font colour", style = nextcord.ButtonStyle.blurple)
    async def secondary_font_colour(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        colourselect = SetColour()
        await interaction.response.send_modal(colourselect)
        await colourselect.wait()
        colourvalid = colourselect.match
        colour_hex = colourselect.hex_code
        if not colourvalid:
            await interaction.send(embed=create_error_embed(title=f"Invalid hex code", description=f"That was an invalid hex code. Use https://colorpicker.me/ to get the hex code for a colour you like!"), ephemeral=True)
            embed = nextcord.Embed(title=f"{interaction.guild.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfig(self.user, self.client))
        else:
            if colour_hex == "default":
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/727175/100x100", ephemeral=True)
            else:
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/{colour_hex.replace('#', '')}/100x100", ephemeral=True)
            maindata.secondary_font_color = colour_hex
            newdata = Bot.db.update_data(table="level_main", data=maindata)
            embed = nextcord.Embed(title=f"{interaction.guild.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfig(self.user, self.client))

    @nextcord.ui.button(label="Settings info", style = nextcord.ButtonStyle.grey, row=3)
    async def settings_info(self, button, interaction:nextcord.Interaction):
        embed = nextcord.Embed(title=f"Card settings info", description=(f"\n\nBackground colour: The colour of the lines on the background image\n\nMain colour: The colour used for the XP bar and for the level text\n\nPrimary font colour: The colour used for your rank, name and your current XP\n\nSecondary font colour: The colour used for your discriminator and the current Xp threshold"), colour=COLOUR_MAIN)
        await interaction.send(embed=embed, ephemeral=True)


    @nextcord.ui.button(label="Go to main settings", style = nextcord.ButtonStyle.grey, row=4)
    async def go_to_main_settings(self, button, interaction:nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=LevelConfig(self.user, self.client))




    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self.user.id == interaction.user.id


class CardBackgroundConfig(nextcord.ui.View):
    def __init__(self, user: nextcord.User, client, already_chosen):
        super().__init__()
        self.user = user
        self.client = client
        self.chosen = "default"
        self.already_chosen = already_chosen

    @nextcord.ui.button(label="Set Default", style=nextcord.ButtonStyle.blurple)
    async def card_background_default(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.chosen = "default"
        await interaction.send(file = nextcord.File(f"./big-bot/assets/images/level/default.png", f"card.png"), ephemeral=True)

    @nextcord.ui.button(label="Complete", style=nextcord.ButtonStyle.green)
    async def complete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()

    @nextcord.ui.select(options=[nextcord.SelectOption(label="Apricot", value=f"apricot"), nextcord.SelectOption(label="Beige", value=f"beige"), nextcord.SelectOption(label="Black", value=f"black"), nextcord.SelectOption(label="Blue", value=f"blue"), nextcord.SelectOption(label="Brown", value=f"brown"), nextcord.SelectOption(label="Cyan", value=f"cyan"), nextcord.SelectOption(label="Dark purple", value=f"dark purple"), nextcord.SelectOption(label="Default", value=f"default"), nextcord.SelectOption(label="Gray", value=f"gray"), nextcord.SelectOption(label="Green", value=f"green"), nextcord.SelectOption(label="Lavender", value=f"lavender"), nextcord.SelectOption(label="Lime", value=f"lime"), nextcord.SelectOption(label="Magenta", value=f"magenta"), nextcord.SelectOption(label="Maroon", value=f"maroon"), nextcord.SelectOption(label="Mint", value=f"mint"), nextcord.SelectOption(label="Navy", value=f"navy"), nextcord.SelectOption(label="Olive", value=f"olive"), nextcord.SelectOption(label="Orange", value=f"orange"), nextcord.SelectOption(label="Pink", value=f"pink"), nextcord.SelectOption(label="Purple", value=f"purple"), nextcord.SelectOption(label="Red", value=f"red"), nextcord.SelectOption(label="Teal", value=f"teal"), nextcord.SelectOption(label="White", value=f"white"), nextcord.SelectOption(label="Yellow", value=f"yellow")], placeholder="Select a colour", max_values=1)
    async def options_card(self, select, interaction: nextcord.Interaction):
        self.chosen = select.values[0]
        await interaction.send("Preview of chosen background:", file = nextcord.File(f"assets/images/level/{select.values[0]}.png", f"card.png"), ephemeral=True)


class SetColour(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Set colour", timeout=None)
        self.hex_code = nextcord.ui.TextInput(
            label = "What is the new colour?",
            placeholder = "Must be a hex colour code (e.g. #43a1e8). Type 'default' to set to the default colour",
            style=nextcord.TextInputStyle.short,
            min_length=7,
            max_length=7,
            required=True
        )
        self.add_item(self.hex_code)


    async def callback(self, interaction: nextcord.Interaction):
        if self.hex_code.value.lower() == "default":
            self.match = True
            self.hex_code = "default"
        else:
            self.match = re.search('^#(?:[0-9a-fA-F]{3}){1,2}$', self.hex_code.value)
            self.hex_code = self.hex_code.value
        self.stop()



class CardConfigUser(nextcord.ui.View):
    def __init__(self, user: nextcord.User, client):
        super().__init__()
        self.user = user
        self.client = client


    @nextcord.ui.button(label = "Set background colour", style = nextcord.ButtonStyle.blurple)
    async def levelling_card_background_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelUsers] = Bot.db.get_data(table="level_users", unique_id=f"{interaction.guild.id}-{interaction.user.id}")
        maindata = maindata[0]
        embed = nextcord.Embed(title=f"Set card background colour", description=f"Using the dropdown below, select what colour you want your card background to be. Click the default button to set it to default", colour=COLOUR_MAIN)
        cardselect = CardBackgroundConfigUser(self.user, self.client, maindata.background_color)
        await interaction.edit(embed=embed, view=cardselect)
        await cardselect.wait()
        cardselected = cardselect.chosen
        maindata.background_color = cardselected
        newdata = Bot.db.update_data(table="level_users", data=maindata)
        embed = nextcord.Embed(title=f"{interaction.user.name} card config settings", colour=COLOUR_MAIN)
        embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
        embed.set_footer(text="Click the 'settings info' button to see what each option changes")
        await interaction.edit(embed=embed, view=CardConfigUser(self.user, self.client))

    @nextcord.ui.button(label = "Set main colour", style = nextcord.ButtonStyle.blurple)
    async def main_colour_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelUsers] = Bot.db.get_data(table="level_users", unique_id=f"{interaction.guild.id}-{interaction.user.id}")
        maindata = maindata[0]
        colourselect = SetColourUser()
        await interaction.response.send_modal(colourselect)
        await colourselect.wait()
        colourvalid = colourselect.match
        colour_hex = colourselect.hex_code
        if not colourvalid:
            await interaction.send(embed=create_error_embed(title=f"Invalid hex code", description=f"That was an invalid hex code. Use https://colorpicker.me/ to get the hex code for a colour you like!"), ephemeral=True)
            embed = nextcord.Embed(title=f"{interaction.user.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfigUser(self.user, self.client))
        else:
            if colour_hex == "default":
                colour_hex = None
            else:
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/{colour_hex.replace('#', '')}/100x100", ephemeral=True)
            maindata.main_color = colour_hex
            newdata = Bot.db.update_data(table="level_users", data=maindata)
            embed = nextcord.Embed(title=f"{interaction.user.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfigUser(self.user, self.client))
    @nextcord.ui.button(label = "Set primary font colour", style = nextcord.ButtonStyle.blurple)
    async def primary_font_colour_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelUsers] = Bot.db.get_data(table="level_users", unique_id=f"{interaction.guild.id}-{interaction.user.id}")
        maindata = maindata[0]
        colourselect = SetColourUser()
        await interaction.response.send_modal(colourselect)
        await colourselect.wait()
        colourvalid = colourselect.match
        colour_hex = colourselect.hex_code
        if not colourvalid:
            await interaction.send(embed=create_error_embed(title=f"Invalid hex code", description=f"That was an invalid hex code. Use https://colorpicker.me/ to get the hex code for a colour you like!"), ephemeral=True)
            embed = nextcord.Embed(title=f"{interaction.user.name} card config", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfigUser(self.user, self.client))
        else:
            if colour_hex == "default":
                colour_hex = None
            else:
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/{colour_hex.replace('#', '')}/100x100", ephemeral=True)
            maindata.primary_font_color = colour_hex
            newdata = Bot.db.update_data(table="level_users", data=maindata)
            embed = nextcord.Embed(title=f"{interaction.user.name} card config", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfigUser(self.user, self.client))
    @nextcord.ui.button(label = "Set secondary font colour", style = nextcord.ButtonStyle.blurple)
    async def secondary_font_colour_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        maindata: List[LevelUsers] = Bot.db.get_data(table="level_users", unique_id=f"{interaction.guild.id}-{interaction.user.id}")
        maindata = maindata[0]
        colourselect = SetColourUser()
        await interaction.response.send_modal(colourselect)
        await colourselect.wait()
        colourvalid = colourselect.match
        colour_hex = colourselect.hex_code
        if not colourvalid:
            await interaction.send(embed=create_error_embed(title=f"Invalid hex code", description=f"That was an invalid hex code. Use https://colorpicker.me/ to get the hex code for a colour you like!"), ephemeral=True)
            embed = nextcord.Embed(title=f"{interaction.user.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfigUser(self.user, self.client))
        else:
            if colour_hex == "default":
                colour_hex = None
            else:
                await interaction.send(f"Preview of chosen colour: https://singlecolorimage.com/get/{colour_hex.replace('#', '')}/100x100", ephemeral=True)
            maindata.secondary_font_color = colour_hex
            newdata = Bot.db.update_data(table="level_users", data=maindata)
            embed = nextcord.Embed(title=f"{interaction.user.name} card config settings", colour=COLOUR_MAIN)
            embed.description = f"""\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}"""
            embed.set_footer(text="Click the 'settings info' button to see what each option changes")
            await interaction.edit(embed=embed, view=CardConfigUser(self.user, self.client))

    @nextcord.ui.button(label="Settings info", style = nextcord.ButtonStyle.grey, row=3)
    async def settings_info_user(self, button, interaction:nextcord.Interaction):
        embed = nextcord.Embed(title=f"Card settings info", description=(f"\n\nBackground colour: The colour of the lines on the background image\n\nMain colour: The colour used for the XP bar and for the level text\n\nPrimary font colour: The colour used for your rank, name and your current XP\n\nSecondary font colour: The colour used for your discriminator and the current Xp threshold"), colour=COLOUR_MAIN)
        await interaction.send(embed=embed, ephemeral=True)




    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self.user.id == interaction.user.id


class CardBackgroundConfigUser(nextcord.ui.View):
    def __init__(self, user: nextcord.User, client, already_chosen):
        super().__init__()
        self.user = user 
        self.client = client
        self.chosen = None
        self.already_chosen = already_chosen

    @nextcord.ui.button(label="Set Default", style=nextcord.ButtonStyle.blurple)
    async def card_background_default_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.chosen = None

    @nextcord.ui.button(label="Complete", style=nextcord.ButtonStyle.green)
    async def complete_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()

    @nextcord.ui.select(options=[nextcord.SelectOption(label="Apricot", value=f"apricot"), nextcord.SelectOption(label="Beige", value=f"beige"), nextcord.SelectOption(label="Black", value=f"black"), nextcord.SelectOption(label="Blue", value=f"blue"), nextcord.SelectOption(label="Brown", value=f"brown"), nextcord.SelectOption(label="Cyan", value=f"cyan"), nextcord.SelectOption(label="Dark purple", value=f"dark purple"), nextcord.SelectOption(label="Default", value=f"default"), nextcord.SelectOption(label="Gray", value=f"gray"), nextcord.SelectOption(label="Green", value=f"green"), nextcord.SelectOption(label="Lavender", value=f"lavender"), nextcord.SelectOption(label="Lime", value=f"lime"), nextcord.SelectOption(label="Magenta", value=f"magenta"), nextcord.SelectOption(label="Maroon", value=f"maroon"), nextcord.SelectOption(label="Mint", value=f"mint"), nextcord.SelectOption(label="Navy", value=f"navy"), nextcord.SelectOption(label="Olive", value=f"olive"), nextcord.SelectOption(label="Orange", value=f"orange"), nextcord.SelectOption(label="Pink", value=f"pink"), nextcord.SelectOption(label="Purple", value=f"purple"), nextcord.SelectOption(label="Red", value=f"red"), nextcord.SelectOption(label="Teal", value=f"teal"), nextcord.SelectOption(label="White", value=f"white"), nextcord.SelectOption(label="Yellow", value=f"yellow")], placeholder="Select a colour", max_values=1)
    async def options_card_user(self, select, interaction: nextcord.Interaction):
        self.chosen = select.values[0]
        await interaction.send("Preview of chosen background:", file = nextcord.File(f"./big-bot/assets/images/level/{select.values[0]}.png", f"card.png"), ephemeral=True)


class SetColourUser(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Set colour", timeout=None)
        self.hex_code = nextcord.ui.TextInput(
            label = "What is the new colour?",
            placeholder = "Type 'default' to set to the guild's default colour",
            style=nextcord.TextInputStyle.short,
            min_length=7,
            max_length=7,
            required=True
        )
        self.add_item(self.hex_code)


    async def callback(self, interaction: nextcord.Interaction):
        if self.hex_code.value.lower() == "default":
            self.match = True
            self.hex_code = "default"
        else:
            self.match = re.search('^#(?:[0-9a-fA-F]{3}){1,2}$', self.hex_code.value)
            self.hex_code = self.hex_code.value
        self.stop()


class NoXPChannelsConfig(nextcord.ui.View):
    def __init__(self, user: nextcord.User, client):
        super().__init__()
        self.user = user
        self.client = client


    @nextcord.ui.button(label = "Add no XP channels", style = nextcord.ButtonStyle.blurple)
    async def add_no_xp_channels(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.no_xp_channels is None:
            maindata.no_xp_channels = []
        elif not "[" in maindata.no_xp_channels:
            maindata.no_xp_channels = []
        else:
            maindata.no_xp_channels = ast.literal_eval(maindata.no_xp_channels)
        for channelid in maindata.no_xp_channels:
            try:
                channel = await interaction.guild.fetch_channel(int(channelid))
            except nextcord.errors.NotFound:
                index = maindata.no_xp_channels.index(channelid)
                del maindata.no_xp_channels[index]
        channel_selected = Channel_Select_XP(interaction.user.id, len(interaction.guild.channels))
        embed = nextcord.Embed(title="Select channels to add", description="Select any channels you want to add as no XP channels. ", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=channel_selected, ephemeral=True)
        await channel_selected.wait()
        selected_channel = channel_selected.values
        for channel in selected_channel:
            if channel.id in maindata.no_xp_channels:
                pass
            else:
                if channel.type == nextcord.ChannelType.category:
                    for tchannel in channel.channels:
                        if not tchannel.id in maindata.no_xp_channels:
                            maindata.no_xp_channels.append(tchannel.id)
                else:
                    maindata.no_xp_channels.append(channel.id)
        Bot.db.update_data(table="level_main", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"No XP channels added", description=f"I have add the following channels to the no xp channels list {', '.join([channel.mention for channel in selected_channel])}"), view=None)
        noxpchannelstext = ""
        for channel in np.asarray(np.matrix(maindata.no_xp_channels))[0]:
            noxpchannelstext+=f"\n- <#{channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} XP Channel Management", description=f"Current No XP channels:\n\n{noxpchannelstext}", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)


    @nextcord.ui.button(label = "Remove no XP channels", style = nextcord.ButtonStyle.blurple)
    async def remove_no_xp_channels(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.no_xp_channels is None:
            maindata.no_xp_channels = []
        elif not "[" in maindata.no_xp_channels:
            maindata.no_xp_channels = []
        else:
            maindata.no_xp_channels = ast.literal_eval(maindata.no_xp_channels)
        for channelid in maindata.no_xp_channels:
            try:
                channel = await interaction.guild.fetch_channel(int(channelid))
            except nextcord.errors.NotFound:
                index = maindata.no_xp_channels.index(channelid)
                del maindata.no_xp_channels[index]
        channel_selected = Channel_Select_XP(interaction.user.id, len(interaction.guild.channels))
        embed = nextcord.Embed(title="Select channels to remove", description="Select any channels you want to remove as no XP channels. ", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=channel_selected, ephemeral=True)
        await channel_selected.wait()
        selected_channel = channel_selected.values
        for channel in selected_channel:
            if channel.type == nextcord.ChannelType.category:
                    for tchannel in channel.channels:
                        if tchannel.id in maindata.no_xp_channels:
                            index = maindata.no_xp_channels.index(tchannel.id)
                            del maindata.no_xp_channels[index]
            else:
                if channel.id in maindata.no_xp_channels:
                    if channel.type == nextcord.ChannelType.category:
                        for tchannel in channel.channels:
                            index = maindata.no_xp_channels.index(tchannel.id)
                            del maindata.no_xp_channels[index]
                    else:
                        index = maindata.no_xp_channels.index(channel.id)
                        del maindata.no_xp_channels[index]
                else:
                    pass
        Bot.db.update_data(table="level_main", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"No XP channels removed", description=f"I removed the following channels as no XP channels {', '.join([channel.mention for channel in selected_channel])}"), view=None)
        noxpchannelstext = ""
        for channel in np.asarray(np.matrix(maindata.no_xp_channels))[0]:
            noxpchannelstext+=f"\n- <#{channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} XP Channel Management", description=f"Current No XP channels:\n\n{noxpchannelstext}", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Go to main settings", style = nextcord.ButtonStyle.grey, row=4)
    async def go_to_main_settings(self, button, interaction:nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=LevelConfig(self.user, self.client))



    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self.user.id == interaction.user.id
    

class Channel_Select_XP(Default_View):
    def __init__(self, org_user: int, channel_len):
        super().__init__(timeout=120, org_user=org_user)
        self.add_item(ChannelListXP())
        self.values = []
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.values:
            self.values = []
            self.stop()
            self.clear_items()
    
        self.stop()
        self.clear_items()

class ChannelListXP(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(custom_id="channel_list_xp", placeholder="Select channel", min_values=1, max_values=25, row=1)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values = self.values#
        

class NoXPRolesConfig(nextcord.ui.View):
    def __init__(self, user: nextcord.User, client):
        super().__init__()
        self.user = user
        self.client = client


    @nextcord.ui.button(label = "Add no XP roles", style = nextcord.ButtonStyle.blurple)
    async def add_no_xp_channels(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.no_xp_roles is None:
            maindata.no_xp_roles = []
        elif not "[" in maindata.no_xp_roles:
            maindata.no_xp_roles = []
        else:
            maindata.no_xp_roles = ast.literal_eval(maindata.no_xp_roles)
        guildroles = await interaction.guild.fetch_roles()
        for channelid in maindata.no_xp_roles:
            if channelid in guildroles:
                pass
            else:
                index = maindata.no_xp_roles.index(channelid)
                del maindata.no_xp_roles[index]
        channel_selected = Role_Select_XP(interaction.user.id, len(interaction.guild.channels))
        embed = nextcord.Embed(title="Select roles to add", description="Select any roles you want to add as no XP roles." , colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=channel_selected, ephemeral=True)
        await channel_selected.wait()
        selected_channel = channel_selected.values
        for channel in selected_channel:
            if channel.id in maindata.no_xp_roles:
                pass
            else:
                maindata.no_xp_roles.append(channel.id)
        Bot.db.update_data(table="level_main", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"No XP roles added", description=f"I have added the following roles to the no xp roles list {', '.join([channel.mention for channel in selected_channel])}"), view=None)
        noxpchannelstext = ""
        for channel in np.asarray(np.matrix(maindata.no_xp_roles))[0]:
            noxpchannelstext+=f"\n- <@&{channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} XP Role Management", description=f"Current No XP roles:\n\n{noxpchannelstext}", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)


    @nextcord.ui.button(label = "Remove no XP roles", style = nextcord.ButtonStyle.blurple)
    async def remove_no_xp_channels(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.no_xp_roles is None:
            maindata.no_xp_roles = []
        elif not "[" in maindata.no_xp_roles:
            maindata.no_xp_roles = []
        else:
            maindata.no_xp_roles = ast.literal_eval(maindata.no_xp_roles)
        guildroles = await interaction.guild.fetch_roles()
        for channelid in maindata.no_xp_roles:
            if channelid in guildroles:
                pass
            else:
                index = maindata.no_xp_roles.index(channelid)
                del maindata.no_xp_roles[index]
        channel_selected = Role_Select_XP(interaction.user.id, len(interaction.guild.channels))
        embed = nextcord.Embed(title="Select roles to remove", description="Select any roles you want to remove as no XP roles." , colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=channel_selected, ephemeral=True)
        await channel_selected.wait()
        selected_channel = channel_selected.values
        for channel in selected_channel:
            if channel.id in maindata.no_xp_roles:
                index = maindata.no_xp_roles.index(channel.id)
                del maindata.no_xp_roles[index]
            else:
                pass
        Bot.db.update_data(table="level_main", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"No XP roles removed", description=f"I have removed the following roles to the no xp roles list {', '.join([channel.mention for channel in selected_channel])}"), view=None)
        noxpchannelstext = ""
        for channel in np.asarray(np.matrix(maindata.no_xp_roles))[0]:
            noxpchannelstext+=f"\n- <@&{channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} XP Role Management", description=f"Current No XP roles:\n\n{noxpchannelstext}", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Go to main settings", style = nextcord.ButtonStyle.grey, row=4)
    async def go_to_main_settings(self, button, interaction:nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=LevelConfig(self.user, self.client))



    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self.user.id == interaction.user.id
    def __init__(self, user: nextcord.User, client):
        super().__init__()
        self.user = user
        self.client = client


    @nextcord.ui.button(label = "Remove no XP roles", style = nextcord.ButtonStyle.blurple)
    async def remove_no_xp_channels(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True, ephemeral=True)
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        maindata = maindata[0]
        if maindata.no_xp_roles is None:
            maindata.no_xp_roles = []
        elif not "[" in maindata.no_xp_roles:
            maindata.no_xp_roles = []
        else:
            maindata.no_xp_roles = ast.literal_eval(maindata.no_xp_roles)
        guildroles = await interaction.guild.fetch_roles()
        for channelid in maindata.no_xp_roles:
            if channelid in guildroles:
                pass
            else:
                index = maindata.no_xp_roles.index(channelid)
                del maindata.no_xp_roles[index]
        channel_selected = Role_Select_XP(interaction.user.id, len(interaction.guild.channels))
        embed = nextcord.Embed(title="Select roles to remove", description="Select any roles you want to remove as no XP roles." , colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=channel_selected, ephemeral=True)
        await channel_selected.wait()
        selected_channel = channel_selected.values
        for channel in selected_channel:
            if channel.id in maindata.no_xp_roles:
                index = maindata.no_xp_roles.index(channel.id)
                del maindata.no_xp_roles[index]
            else:
                pass
        Bot.db.update_data(table="level_main", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"No XP roles removed", description=f"I have removed the following roles to the no xp roles list {', '.join([channel.mention for channel in selected_channel])}"), view=None)
        noxpchannelstext = ""
        for channel in np.asarray(np.matrix(maindata.no_xp_roles))[0]:
            noxpchannelstext+=f"\n- <@&{channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} XP Role Management", description=f"Current No XP roles:\n\n{noxpchannelstext}", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)

    @nextcord.ui.button(label="Go to main settings", style = nextcord.ButtonStyle.grey, row=4)
    async def go_to_main_settings(self, button, interaction:nextcord.Interaction):
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=0)
        else:
            maindata = maindata[0]
        if maindata.level_up_channel == "current":
            levelupchannel = "Channel they are typing in"
        elif maindata.level_up_channel is None:
            levelupchannel = None
        else:
            levelupchannel = f"<#{maindata.level_up_channel}>"
        embed = nextcord.Embed(title=f"{interaction.guild.name} Levelling Settings", description=(f"\n\nEnabled: {maindata.enabled}\n\nMinimum XP: {maindata.min_xp}\nMaximum XP: {maindata.max_xp}\nChat XP Cooldown: {maindata.cooldown if not maindata.cooldown is None else 30}s\n\nMinimum voice XP: {maindata.min_vc_xp}\nMaximum voice XP {maindata.max_vc_xp}\n\nReward earned message: {maindata.reward_message}\nLevel up message: {maindata.level_up_message}\nLevel up channel: {levelupchannel}\nStackable rewards: {maindata.stackable_rewards}\n\n XP Drops Enabled: {maindata.drops}"), colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=LevelConfig(self.user, self.client))



    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self.user.id == interaction.user.id
        

class Role_Select_XP(Default_View):
    def __init__(self, org_user: int, channel_len):
        super().__init__(timeout=120, org_user=org_user)
        self.add_item(RoleListXP())
        self.values = []
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.values:
            self.values = []
            self.stop()
            self.clear_items()
    
        self.stop()
        self.clear_items()

class RoleListXP(nextcord.ui.RoleSelect):
    def __init__(self):
        super().__init__(custom_id="channel_list_xp", placeholder="Select role", min_values=1, max_values=25, row=1)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values = self.values





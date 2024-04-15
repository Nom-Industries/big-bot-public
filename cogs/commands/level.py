import nextcord, io
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from bot import Bot
from utils import *
import aiohttp
from typing import List, Union
from PIL import Image, ImageFont, ImageDraw
from views import LevelConfig, CardConfigUser,  Confirm
from db_handler.schemas import *
from nextcord.abc import GuildChannel
from constants import COLOUR_MAIN, COLOUR_BAD

class Level(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name=f"level", description=f"View your level in the server")
    async def level(self,
        interaction: Interaction,
        member: nextcord.Member=SlashOption(
            name=f"member",
            description=f"Member to check level of",
            required=False
        )):
        if not member:
            member = interaction.user
        await interaction.response.defer()
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=False)
            await interaction.send("Levelling is disabled in this guild.")
            return 
        else:
            maindata = maindata[0]
            if not maindata.enabled:
                await interaction.send("Levelling is disabled in this guild.")
                return
        def get_info(total_xp, maindata):
            if maindata.mee6_levels:
                return utils.mee_totalxp_to_level(total_xp)
            else:
                return totalxp_to_level(total_xp)
        data: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id, user_id=member.id)
        if not data:
            data = Bot.db.create_data(table="level_users", unique_id=f"{interaction.guild.id}-{member.id}", guild_id=interaction.guild.id, user_id=member.id, total_xp=0)
            total_xp = 0
            level, threshold, xp = get_info(total_xp, maindata)
        else:
            data = data[0]
            total_xp = data.total_xp
            level, threshold, xp = get_info(data.total_xp, maindata)

        lb: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id)
        lb = sorted(lb, key=lambda x: x.total_xp, reverse=True)
        rank = ([i for i in range(len(lb)) if int(lb[i].user_id) == member.id][0]) + 1

        background_color, main_color, prim_color, secondary_color = data.background_color, data.main_color, data.primary_font_color, data.secondary_font_color
        if not data.background_color:
            background_color = maindata.background_color
        if not data.main_color:
            main_color = maindata.main_color
        if not data.primary_font_color:
            prim_color = maindata.primary_font_color
        if not data.secondary_font_color:
            secondary_color = maindata.secondary_font_color

        bytes = await generate_level_image(member, interaction.guild, rank, level, xp, threshold, background_color, main_color, prim_color, secondary_color)
        await interaction.send(file=nextcord.File(bytes, "card.png"))
    

    @nextcord.slash_command(name=f"rank", description=f"View your rank in the server")
    async def rank(self,
        interaction: Interaction,
        member: nextcord.Member=SlashOption(
            name=f"member",
            description=f"Member to check level of",
            required=False
        )):
        if not member:
            member = interaction.user
        await interaction.response.defer()
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=False)
            await interaction.send("Levelling is disabled in this guild.")
            return
        else:
            maindata = maindata[0]
            if not maindata.enabled:
                await interaction.send("Levelling is disabled in this guild.")
                return
        def get_info(total_xp, maindata):
            if maindata.mee6_levels:
                return utils.mee_totalxp_to_level(total_xp)
            else:
                return totalxp_to_level(total_xp)
        data: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id, user_id=member.id)
        if not data:
            data = Bot.db.create_data(table="level_users", unique_id=f"{interaction.guild.id}-{member.id}", guild_id=interaction.guild.id, user_id=member.id, total_xp=0)
            total_xp = 0
            level, threshold, xp = get_info(total_xp, maindata)
        else:
            data = data[0]
            total_xp = data.total_xp
            level, threshold, xp = get_info(data.total_xp, maindata)

        lb: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id)
        lb = sorted(lb, key=lambda x: x.total_xp, reverse=True)
        rank = ([i for i in range(len(lb)) if int(lb[i].user_id) == member.id][0]) + 1

        background_color, main_color, prim_color, secondary_color = data.background_color, data.main_color, data.primary_font_color, data.secondary_font_color
        if not data.background_color:
            background_color = maindata.background_color
        if not data.main_color:
            main_color = maindata.main_color
        if not data.primary_font_color:
            prim_color = maindata.primary_font_color
        if not data.secondary_font_color:
            secondary_color = maindata.secondary_font_color

        bytes = await generate_level_image(member, interaction.guild, rank, level, xp, threshold, background_color, main_color, prim_color, secondary_color)
        await interaction.send(file=nextcord.File(bytes, "card.png"))
    
    @nextcord.user_command(name=f"view level")
    async def view_level(self,
        interaction: Interaction,
        member: nextcord.Member):
        await interaction.response.defer()
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=False)
            await interaction.send("Levelling is disabled in this guild.")
            return 
        else:
            maindata = maindata[0]
            if not maindata.enabled:
                await interaction.send("Levelling is disabled in this guild.")
                return
        def get_info(total_xp, maindata):
            if maindata.mee6_levels:
                return utils.mee_totalxp_to_level(total_xp)
            else:
                return totalxp_to_level(total_xp)
        data: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id, user_id=member.id)
        if not data:
            data = Bot.db.create_data(table="level_users", unique_id=f"{interaction.guild.id}-{member.id}", guild_id=interaction.guild.id, user_id=member.id, total_xp=0)
            total_xp = 0
            level, threshold, xp = get_info(total_xp, maindata)
        else:
            data = data[0]
            total_xp = data.total_xp
            level, threshold, xp = get_info(data.total_xp, maindata)

        lb: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id)
        lb = sorted(lb, key=lambda x: x.total_xp, reverse=True)
        rank = ([i for i in range(len(lb)) if int(lb[i].user_id) == member.id][0]) + 1
        background_color, main_color, prim_color, secondary_color = data.background_color, data.main_color, data.primary_font_color, data.secondary_font_color
        if not data.background_color:
            background_color = maindata.background_color
        if not data.main_color:
            main_color = maindata.main_color
        if not data.primary_font_color:
            prim_color = maindata.primary_font_color
        if not data.secondary_font_color:
            secondary_color = maindata.secondary_font_color

        bytes = await generate_level_image(member, interaction.guild, rank, level, xp, threshold, background_color, main_color, prim_color, secondary_color)
        await interaction.send(file=nextcord.File(bytes, "card.png"))

    @nextcord.slash_command(name=f"levels", description=f"levelling base")
    async def levelling(self, interaction: Interaction):
        pass

    @levelling.subcommand(name=f"config", description=f"config base")
    async def levelling_config(self, interaction: Interaction):
        pass

    @levelling_config.subcommand(name=f"user", description=f"Customise your user levelling configuration")
    async def levelling_config_user(self, interaction: Interaction):
        maindata: List[LevelUsers] = Bot.db.get_data(table="level_users", unique_id=f"{interaction.guild.id}-{interaction.user.id}")
        if not maindata:
            maindata = Bot.db.create_data(table="level_users", unique_id=f"{interaction.guild.id}-{interaction.user.id}", guild_id=interaction.guild.id, user_id=interaction.user.id, total_xp=0)
        else:
            maindata = maindata[0]
        embed = nextcord.Embed(title=f"{interaction.user.name} card config settings", description=f"\n\nBackground Colour: {str(maindata.background_color).capitalize()}\nMain Colour: {str(maindata.main_color).capitalize()}\nPrimary Font Colour: {str(maindata.primary_font_color).capitalize()}\nSecondary Font Colour: {str(maindata.secondary_font_color).capitalize()}", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=CardConfigUser(interaction.user, self.client))

    @levelling_config.subcommand(name=f"server", description=f"Customise your servers levelling configuration")
    async def levelling_config_server(self, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(f"You are not allowed to use this command")
            return
        
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
        await interaction.send(embed=embed, view=LevelConfig(interaction.user, self.client))

    @levelling.subcommand(name=f"boostroles", description=f"boosted roles")
    async def boosted_exp_roles(self, interaction: nextcord.Interaction):
        pass

    @boosted_exp_roles.subcommand(name=f"add", description=f"Add a boosted xp role")
    async def boosted_exp_roles_add(self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = SlashOption(
            name=f"role",
            description=f"Role to grant a boost to",
            required=True
        ),
        boost_percentage: int = SlashOption(
            name=f"boost",
            description=f"Boost the role should receive as a percentage between 1 and 500",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        if boost_percentage < 1:
            boost_percentage = 1
        elif boost_percentage > 500:
            boost_percentage = 500
        roledata: List[LevelBonusRoles] = Bot.db.get_data(table="level_bonus_roles", guild_id=interaction.guild.id, role_id=role.id)
        if roledata:
            roledata.role_id = role.id
            roledata.boost = boost_percentage
            Bot.db.update_data(table="level_bonus_roles", data=roledata)
            await interaction.send(embed=create_success_embed(title=f"Role XP Boost Updated", description=f"Successfully granted {role.mention} a boosted XP of {boost_percentage}%"))
        else:
            roledata: List[LevelBonusRoles] = Bot.db.create_data(table="level_bonus_roles", guild_id=interaction.guild.id, role_id=role.id, boost=boost_percentage)
            await interaction.send(embed=create_success_embed(title=f"Role XP Boost Added", description=f"Successfully granted {role.mention} a boosted XP of {boost_percentage}%"))

    @boosted_exp_roles.subcommand(name=f"remove", description=f"Remove a boosted xp role")
    async def boosted_exp_roles_remove(self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = SlashOption(
            name=f"role",
            description=f"Role to remove the boost from",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        roledata: List[LevelBonusRoles] = Bot.db.get_data(table="level_bonus_roles", guild_id=interaction.guild.id, role_id=role.id)
        if roledata:
            Bot.db.delete_data(table="level_bonus_roles", data=roledata[0])
            await interaction.send(embed=create_success_embed(title=f"Role XP Boost Removed", description=f"Successfully removed the XP boost from {role.mention}"))
        else:
            await interaction.send(embed=create_error_embed(title="Error!", description=f"{role.mention} does not have an XP Boost!"))

    @boosted_exp_roles.subcommand(name=f"list", description=f"List all XP Boosted Roles")
    async def boosted_exp_roles_list(self,
        interaction: nextcord.Interaction,
        ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        roledata: List[LevelBonusRoles] = Bot.db.get_data(table="level_bonus_roles", guild_id=interaction.guild.id)
        if roledata:
            boosted_xp_role_msg = ""
            guild_roles = await interaction.guild.fetch_roles()
            guild_role_ids = []
            for role in guild_roles:
                guild_role_ids.append(role.id)
            for role in roledata:
                if role.role_id in guild_role_ids:
                    boosted_xp_role_msg += f"\n- <@&{role.role_id}> - {role.boost}%"
                else:
                    Bot.db.delete_data(table="level_bonus_roles", data=role)
            await interaction.send(embed=create_success_embed(title=f"Roles with XP Boost", description=f"{boosted_xp_role_msg}"))
        else:
            await interaction.send(embed=create_error_embed(title="Error!", description=f"Your server does not have any xp boosted roles!"))

    @levelling.subcommand(name=f"boostchannels", description=f"boosted channels")
    async def boosted_exp_channels(self, interaction: nextcord.Interaction):
        pass

    @boosted_exp_channels.subcommand(name=f"add", description=f"Add a boosted xp channel")
    async def boosted_exp_channels_add(self,
        interaction: nextcord.Interaction,
        channel: GuildChannel = SlashOption(
            name="channel", 
            description=f"Boost the channel should receive as a percentage between 1 and 999",
            required=True, 
            channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.news, nextcord.ChannelType.voice]
        ),
        boost_percentage: int = SlashOption(
            name=f"boost",
            description=f"Boost the role should receive as a percentage",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        if boost_percentage < 1:
            boost_percentage = 1
        elif boost_percentage > 500:
            boost_percentage = 500
        channeldata: List[LevelBonusChannels] = Bot.db.get_data(table="level_bonus_channels", guild_id=interaction.guild.id, channel_id=channel.id)
        if channeldata:
            channeldata.channel_id = channel.id
            channeldata.boost = boost_percentage
            Bot.db.update_data(table="level_bonus_channels", data=channeldata)
            await interaction.send(embed=create_success_embed(title=f"Channel XP Boost Updated", description=f"Successfully granted {channel.mention} a boosted XP of {boost_percentage}%"))
        else:
            channeldata: List[LevelBonusChannels] = Bot.db.create_data(table="level_bonus_channels", guild_id=interaction.guild.id, channel_id=channel.id, boost=boost_percentage)
            await interaction.send(embed=create_success_embed(title=f"Channel XP Boost Added", description=f"Successfully granted {channel.mention} a boosted XP of {boost_percentage}%"))

    @boosted_exp_channels.subcommand(name=f"remove", description=f"Remove a boosted xp channels")
    async def boosted_exp_channels_remove(self,
        interaction: nextcord.Interaction,
        channel: GuildChannel = SlashOption(
            name="channel", 
            description="Channel to remove boost exp from", 
            required=True, 
            channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.news, nextcord.ChannelType.voice]
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        channeldata: List[LevelBonusChannels] = Bot.db.get_data(table="level_bonus_channels", guild_id=interaction.guild.id, channel_id=channel.id)
        if channeldata:
            Bot.db.delete_data(table="level_bonus_channels", data=channeldata[0])
            await interaction.send(embed=create_success_embed(title=f"Channel XP Boost Removed", description=f"Successfully removed the XP boost from {channel.mention}"))
        else:
            await interaction.send(embed=create_error_embed(title="Error!", description=f"{channel.mention} does not have an XP Boost!"))

    @boosted_exp_channels.subcommand(name=f"list", description=f"List all XP Boosted Channels")
    async def boosted_exp_channels_list(self,
        interaction: nextcord.Interaction,
        ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        channeldata: List[LevelBonusChannels] = Bot.db.get_data(table="level_bonus_channels", guild_id=interaction.guild.id)
        if channeldata:
            boosted_xp_channel_msg = ""
            guild_channels = await interaction.guild.fetch_channels()
            guild_channel_ids = []
            for channel in guild_channels:
                guild_channel_ids.append(channel.id)
            for channel in channeldata:
                if channel.channel_id in guild_channel_ids:
                    boosted_xp_channel_msg += f"\n- <#{channel.channel_id}> - {channel.boost}%"
                else:
                    Bot.db.delete_data(table="level_bonus_channels", data=channel)
            await interaction.send(embed=create_success_embed(title=f"Channels with XP Boost", description=f"{boosted_xp_channel_msg}"))
        else:
            await interaction.send(embed=create_error_embed(title="Error!", description=f"Your server does not have any xp boosted channels!"))

    @levelling.subcommand(name=f"rewards", description=f"rewards base")
    async def levelling_rewards(self, interaction: nextcord.Interaction):
        pass

    @levelling_rewards.subcommand(name=f"add", description=f"Add a levelling reward")
    async def levelling_rewards_add(self,
        interaction: nextcord.Interaction,
        level: int = SlashOption(
            name=f"level",
            description=f"Level to add the role at",
            required=True
        ),
        role: nextcord.Role = SlashOption(
            name=f"role",
            description=f"Role to add to users when they reach the level",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        roledata: List[LevelRoles] = Bot.db.get_data(table="level_roles", guild_id=interaction.guild.id, level=level)
        if roledata:
            roledata.role_id = role.id
            Bot.db.update_data(table="level_main", data=roledata)
        else:
            roledata: List[LevelRoles] = Bot.db.create_data(table="level_roles", guild_id=interaction.guild.id, level=level, role_id=role.id)
        await interaction.send(embed=create_success_embed(title=f"Role reward added", description=f"Successfully added {role.mention} as the reward for reaching level {level}"))

    @levelling_rewards.subcommand(name=f"remove", description=f"Remove a levelling reward")
    async def levelling_rewards_remove(self,
        interaction: nextcord.Interaction,
        level: int = SlashOption(
            name=f"level",
            description=f"Level to remove the role for",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        roledata: List[LevelRoles] = Bot.db.get_data(table="level_roles", guild_id=interaction.guild.id, level=level)
        if roledata:
            Bot.db.delete_data(table="level_roles", data=roledata[0])
        await interaction.send(embed=create_success_embed(title=f"Role reward removed", description=f"Successfully removed any level rewards for reaching level {level}"))

    @levelling_rewards.subcommand(name=f"list", description=f"List all levelling rewards")
    async def levelling_rewards_list(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        await interaction.response.defer()
        roledata: List[LevelRoles] = Bot.db.get_data(table="level_roles", guild_id=interaction.guild.id)
        if not roledata:
            await interaction.send("There are no level rewards setup.", ephemeral=True)
            return
        text = ""
        for reward in roledata:
            text+=f"\n{reward.level} - <@&{reward.role_id}>"
        await interaction.send(embed=create_success_embed(title=f"Role rewards", description=text))


    @nextcord.slash_command(name=f"setlevel", description=f"Set a user's level")
    async def setlevel(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name=f"member",
            description=f"The member to change the level of",
            required= True
        ),
        level: int = SlashOption(
            name=f"level",
            description="Level to set the user to",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You require `administrator` permission to run this command!"))
            return
        if level > 500:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The level must be less than 500"))
            return
        await interaction.response.defer()
        serverdata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not serverdata:
            serverdata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=False)
            await interaction.send("Levelling is disabled in this guild.")
            return
        else:
            serverdata = serverdata[0]
            if not serverdata.enabled:
                await interaction.send("Levelling is disabled in this guild.")
                return
        
        maindata: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id, user_id=member.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_users", unique_id=f"{interaction.guild.id}-{member.id}", guild_id=interaction.guild.id, user_id=member.id, total_xp=0)
        else:
            maindata = maindata[0]
        
        def get_info(lvl, maindata):
            if maindata.mee6_levels:
                return utils.mee_lvl_to_xp(lvl)
            else:
                return level_to_totalxp(lvl)

        confirmation = Confirm(interaction.user.id)
        embed = create_warning_embed(title=f"Are you sure?", description=f"Are you sure you want to set {member.mention}'s level to `{level}`")
        await interaction.send(embed=embed, view=confirmation)
        await confirmation.wait()
        if not confirmation.value:
            embed=nextcord.Embed(title=f"Action Cancelled", description=f"The action has been cancelled.", colour=COLOUR_BAD)
            await interaction.edit_original_message(embed=embed, view=None)
            return

        maindata.total_xp = get_info(level, serverdata)
        Bot.db.update_data(table="level_users", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"User level set", description=f"I have set {member.mention}'s level to `{level}`"), view=None)

    @nextcord.slash_command(name=f"removexp", description=f"Remove XP from a user")
    async def removexp(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name=f"member",
            description=f"The member to remove xp from",
            required= True
        ),
        xp: int = SlashOption(
            name=f"xp",
            description="Amount of XP to remove from the user",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You require `administrator` permission to run this command!"))
            return

        if xp > 12525000:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The xp must be less than {12525000:,}"))
            return
        await interaction.response.defer()
        maindata: List[LevelUsers] = self.client.db.get_data(table="level_users", guild_id=interaction.guild.id, user_id=member.id)
        if not maindata:
            maindata = self.client.db.create_data(table="level_users", unique_id=f"{interaction.guild.id}-{member.id}", guild_id=interaction.guild.id, user_id=member.id, total_xp=0)
        else:
            maindata = maindata[0]

        confirmation = Confirm(interaction.user.id)
        embed = create_warning_embed(title=f"Are you sure?", description=f"Are you sure you want to remove `{xp:,}` XP from {member.mention}")
        await interaction.send(embed=embed, view=confirmation)
        await confirmation.wait()
        if not confirmation.value:
            embed=nextcord.Embed(title=f"Action Cancelled", description=f"The action has been cancelled.", colour=COLOUR_BAD)
            await interaction.edit_original_message(embed=embed, view=None)
            return
        if maindata.total_xp - xp < 0:
            maindata.total_xp = 0
        else:
            maindata.total_xp -= xp
        self.client.db.update_data(table="level_users", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"User xp removed", description=f"I have removed `{xp:,}` XP from  {member.mention}"), view=None)

    
    @nextcord.slash_command(name=f"addxp", description=f"Add XP to a user")
    async def addxp(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name=f"member",
            description=f"The member to add xp to",
            required= True
        ),
        xp: int = SlashOption(
            name=f"xp",
            description="Amount of XP to add to the user",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You require `administrator` permission to run this command!"))
            return

        if xp > 12525000:
            await interaction.send(embed=create_error_embed(title=f"Invalid Value", description=f"The xp must be less than {12525000:,}"))
            return
        await interaction.response.defer()
        maindata: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id, user_id=member.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_users", unique_id=f"{interaction.guild.id}-{member.id}", guild_id=interaction.guild.id, user_id=member.id, total_xp=0)
        else:
            maindata = maindata[0]

        if maindata.total_xp + xp > 10000000:
            await interaction.send(embed=create_error_embed(title=f"Error!", description=f"You cannot add more than 10,000,000 exp at once!"))
            return
        confirmation = Confirm(interaction.user.id)
        embed = create_warning_embed(title=f"Are you sure?", description=f"Are you sure you want to add `{xp:,}` XP to {member.mention}")
        await interaction.send(embed=embed, view=confirmation)
        await confirmation.wait()
        if not confirmation.value:
            embed=nextcord.Embed(title=f"Action Cancelled", description=f"The action has been cancelled.", colour=COLOUR_BAD)
            await interaction.edit_original_message(embed=embed, view=None)
            return
        maindata.total_xp += xp
        Bot.db.update_data(table="level_users", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"User xp added", description=f"I have added `{xp:,}` XP to  {member.mention}"), view=None)

    @nextcord.slash_command(name=f"resetlevel", description=f"Reset a users level.")
    async def resetlevel(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name=f"member",
            description=f"The member who's level you wish to reset",
            required= True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You require `administrator` permission to run this command!"))
            return
        await interaction.response.defer()
        maindata: List[LevelUsers] = self.client.db.get_data(table="level_users", guild_id=interaction.guild.id, user_id=member.id)
        if not maindata:
            maindata = self.client.db.create_data(table="level_users", unique_id=f"{interaction.guild.id}-{member.id}", guild_id=interaction.guild.id, user_id=member.id, total_xp=0)
        else:
            maindata = maindata[0]
        confirmation = Confirm(interaction.user.id)
        embed = create_warning_embed(title=f"Are you sure?", description=f"Are you sure you want to reset {member.mention}'s level")
        await interaction.send(embed=embed, view=confirmation)
        await confirmation.wait()
        if not confirmation.value:
            embed=nextcord.Embed(title=f"Action Cancelled", description=f"The action has been cancelled.", colour=COLOUR_BAD)
            await interaction.edit_original_message(embed=embed, view=None)
            return
        maindata.total_xp = 0
        self.client.db.update_data(table="level_users", data=maindata)
        await interaction.edit_original_message(embed=create_success_embed(title=f"User level reset", description=f"I have reset {member.mention}'s level"), view=None)


    

def get_colour(rank):
    if rank == 0:
        return "#ffd700"
        
    elif rank == 1:
        return "#c0c0c0"
        
    elif rank == 2:
        return "#cd7f32"
    
    else:
        return "#808080"
    
async def generate_level_image(member, guild, rank, level, xp, threshold, bg_colour, main_colour, prim_colour, second_colour):
    user_avatar_image = str(member.display_avatar.with_size(512).url)
    async with aiohttp.ClientSession() as session:
        async with session.get(user_avatar_image) as resp:
            avatar_bytes = io.BytesIO(await resp.read())

    if main_colour in ("default", None):
        main_colour = "#43a1e8"
    if prim_colour in ("default", None):
        prim_colour = "#ffffff"
    if second_colour in ("default", None):
        second_colour = "#727175"


    if bg_colour is None:
        bg_colour = "default"
    img = Image.open(f"./big-bot/assets/images/level/{bg_colour}.png")
    logo = Image.open(avatar_bytes).resize((200, 200)).convert("RGBA")
    # Stack overflow helps :)
    bigsize = (logo.size[0] * 3, logo.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(logo.size, Image.ANTIALIAS)
    logo.putalpha(mask)
    ##############################
    img.paste(logo, (20, 20), mask=logo)

    # Black Circle
    draw = ImageDraw.Draw(img)
    draw.ellipse((152, 152, 208, 208), fill='#000')

    # Placing offline or Online Status
    if str(member.status) == "online":
        draw.ellipse((155, 155, 205, 205), fill='#3BA55B')
    elif str(member.status) == "idle":
        draw.ellipse((155, 155, 205, 205), fill='#F9A61A')
    elif str(member.status) == "dnd":
        draw.ellipse((155, 155, 205, 205), fill='#EC4245')
    else:
        draw.ellipse((155, 155, 205, 205), fill='#737F8D')
    ##################################

    # Working with fonts
    big_font = ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf', 60)
    medium_font = ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf', 40)
    small_font = ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf', 30)
    extra_small_front=ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf',10)
    # Placing Level text (right-upper part)
    text_size = draw.textsize(f"{level}", font=big_font)
    offset_x = 1000 - 15 - text_size[0]
    offset_y = 5
    draw.text((offset_x, offset_y), f"{level}", font=big_font, fill=main_colour)
    text_size = draw.textsize('LEVEL', font=small_font)

    offset_x -= 5 + text_size[0]
    offset_y = 35
    draw.text((offset_x, offset_y), "LEVEL", font=small_font, fill=main_colour)
    #totalxp field



    # Placing Rank Text (right upper part)
    text_size = draw.textsize(f"{rank}", font=big_font)
    offset_x -= 15 + text_size[0]
    offset_y = 5
    draw.text((offset_x, offset_y), f"{rank}", font=big_font, fill=prim_colour)

    text_size = draw.textsize("RANK", font=small_font)
    offset_x -= 5 + text_size[0]
    offset_y = 35
    draw.text((offset_x, offset_y), "RANK", font=small_font, fill=prim_colour)

    # Placing Progress Bar
    # Background Bar
    bar_offset_x = logo.size[0] + 20 + 100
    bar_offset_y = 160
    bar_offset_x_1 = 1000 - 50
    bar_offset_y_1 = 200
    circle_size = bar_offset_y_1 - bar_offset_y

    # Progress bar rect greyier one
    draw.rectangle((bar_offset_x, bar_offset_y, bar_offset_x_1, bar_offset_y_1), fill="#727175")
    # Placing circle in progress bar

    # Left circle
    draw.ellipse((bar_offset_x - circle_size // 2, bar_offset_y, bar_offset_x + circle_size // 2,
                    bar_offset_y + circle_size), fill="#727175")

    # Right Circle
    draw.ellipse(
        (bar_offset_x_1 - circle_size // 2, bar_offset_y, bar_offset_x_1 + circle_size // 2, bar_offset_y_1),
        fill="#727175")

    # Filling Progress Bar

    bar_length = bar_offset_x_1 - bar_offset_x
    # Calculating of length
    # Bar Percentage (final_xp - current_xp)/final_xp

    # Some variables
    progress = (threshold - xp) * 100 / threshold
    progress = 100 - progress
    progress_bar_length = round(bar_length * progress / 100)
    pbar_offset_x_1 = bar_offset_x + progress_bar_length

    # Drawing Rectangle 
    draw.rectangle((bar_offset_x, bar_offset_y, pbar_offset_x_1, bar_offset_y_1), fill=main_colour)
    # Left circle
    draw.ellipse((bar_offset_x - circle_size // 2, bar_offset_y, bar_offset_x + circle_size // 2,
                    bar_offset_y + circle_size), fill=main_colour)
    # Right Circle
    draw.ellipse(
        (pbar_offset_x_1 - circle_size // 2, bar_offset_y, pbar_offset_x_1 + circle_size // 2, bar_offset_y_1),
        fill=main_colour)

    def convert_int(integer):
        if integer>=1000:
            integer = round(integer / 1000, 2)
            return f'{integer}K'
        else:
            return integer

    # Drawing Xp Text
    text = f"/ {convert_int(threshold)} XP"
    xp_text_size = draw.textsize(text, font=small_font)
    xp_offset_x = bar_offset_x_1 - xp_text_size[0]
    xp_offset_y = bar_offset_y - xp_text_size[1] - 10
    draw.text((xp_offset_x, xp_offset_y), text, font=small_font, fill=second_colour)

    text = f'{convert_int(xp)} '
    xp_text_size = draw.textsize(text, font=small_font)
    xp_offset_x -= xp_text_size[0]
    draw.text((xp_offset_x, xp_offset_y), text, font=small_font, fill=prim_colour)

    # Placing User Name
    text = member.name
    text_size = draw.textsize(text, font=medium_font)
    text_offset_x = bar_offset_x - 10
    text_offset_y = bar_offset_y - text_size[1] - 10
    if "g" in member.name or "q" in member.name or "p" in member.name or "y" in member.name:
        text_offset_y+=5
    draw.text((text_offset_x, text_offset_y), text, font=medium_font, fill=prim_colour)


    # Placing Discriminator
    if not str(member.discriminator) == "0":
        text = f'#{member.discriminator}'
        text_offset_x += text_size[0] + 10
        text_size = draw.textsize(text, font=medium_font)
        if "g" in member.name or "q" in member.name or "p" in member.name or "y" in member.name:
            text_offset_y+=5
        draw.text((text_offset_x-10, text_offset_y), text, font=medium_font, fill=second_colour)

    bytes = io.BytesIO()
    img.save(bytes, 'PNG')
    bytes.seek(0)
    return bytes

async def generate_level_up_image(member, guild, oldlevel, newlevel, bg_colour, main_colour, prim_colour, second_colour):
    user_avatar_image = str(member.display_avatar.with_size(64).url)
    async with aiohttp.ClientSession() as session:
        async with session.get(user_avatar_image) as resp:
            avatar_bytes = io.BytesIO(await resp.read())

    if main_colour in ("default", None):
        main_colour = "#43a1e8"
    if prim_colour in ("default", None):
        prim_colour = "#ffffff"
    if second_colour in ("default", None):
        second_colour = "#727175"
    if bg_colour is None:
        bg_colour = "default"

    img = Image.open(f"./big-bot/./big-bot/assets/images/levelup/{bg_colour}.png")
    logo = Image.open(avatar_bytes).resize((64, 64)).convert("RGBA")
    # Stack overflow helps :)
    bigsize = (logo.size[0] * 3, logo.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(logo.size, Image.ANTIALIAS)
    logo.putalpha(mask)
    ##############################
    img.paste(logo, (5, 5), mask=logo)

    draw = ImageDraw.Draw(img)

    # Working with fonts
    medium_font = ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf', 34)
    arrow_font=ImageFont.FreeTypeFont('./big-bot/assets/fonts/levelupfont.ttf',30)


    def convert_int(integer):
        if integer>=1000:
            integer = round(integer / 1000, 2)
            return f'{integer}K'
        else:
            return integer

    # Placing Level Up Text
    text = f'Level Up!'
    text_size = draw.textsize(text, font=medium_font)
    offset_x = 250 - 20 - text_size[0]
    offset_y = -5
    draw.text((offset_x,offset_y),text,font=medium_font, fill='#ffffff')

    #Placing Level Text
    text = f'{oldlevel} → {newlevel}'
    text_size = draw.textsize(text, font=arrow_font)
    offset_x = 160
    offset_y = 65
    draw.text((offset_x,offset_y),text,font=arrow_font, fill='#ffffff', anchor='ms')

    bytes = io.BytesIO()
    img.save(bytes, 'PNG')
    bytes.seek(0)
    return bytes


def setup(client: Bot):
    client.add_cog(cog=Level(client=client))

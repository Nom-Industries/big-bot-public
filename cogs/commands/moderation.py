from asyncio import tasks
import random
import nextcord, asyncio, time, datetime, pymysql
from nextcord import Interaction, SlashOption
from nextcord.ext import commands, tasks
from nextcord.abc import GuildChannel
from bot.bot import Bot
from constants import COLOUR_BAD, COLOUR_GOOD, COLOUR_MAIN, COLOUR_NEUTRAL, DBENDPOINT, DBPORT, DBUSER, DBPASS, DBNAME
from utils.utils import color_message, create_warning_embed, create_error_embed, create_success_embed
from views import PurgeView, LockView, UnlockView, Modlogs_Information_View, Punishment_Edit, NicknameRequestManagement, Confirm, ModerationConfigView, TimeoutAppView, WarningAppView, Modlogs_Information_View_Non_Pagified
from string import ascii_letters, digits
from typing import List, Union
from db_handler.schemas import *
from dateutil import parser

unraiding = []

class Moderation(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.unban_loop.start()
        self.unmute_loop.start()

    @staticmethod
    async def get_log_webhook(guild):
        data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=guild.id)
        if not data:
            data = Bot.db.create_data("moderation_main", guild=guild.id)
        else:
            data = data[0]
        return data.mod_log_channel
    

    async def log_moderation(self, guild, embed):
        logchannelid = await self.get_log_webhook(guild)
        try:
            logchannel = guild.get_channel(logchannelid)
            await logchannel.send(embed=embed)
        except:
            pass

    @staticmethod
    async def create_punishment_id():
        uniqueID = False
        while not uniqueID:
            punishmentID = ''.join([random.choice(ascii_letters+digits+"_") for i in range(8)])
            data: List[GuildMod] = Bot.db.get_data("guild_mod", punishment_id=punishmentID)
            if not data:
                uniqueID = True
        return punishmentID

    @staticmethod
    async def duration_input_to_text(durationinput):
        try:
            if durationinput[-1] == "s":
                duration=int(int(durationinput[:-1]))
                durationsuffix = "second(s)"
            elif durationinput[-1] == "m" and "perm" not in durationinput.lower():
                duration = int(int(durationinput[:-1])*60)
                durationsuffix = "min(s)"
            elif durationinput[-1] == "h":
                duration = int(int(durationinput[:-1])*3600)
                durationsuffix = "hour(s)"
            elif durationinput[-1] == "d":
                duration = int(int(durationinput[:-1])*86400)
                durationsuffix = "day(s)"
            elif durationinput[-1] == "M" and "perm" not in durationinput.lower():
                duration = int(int(durationinput[:-1])*2629746)
                durationsuffix = "month(s)"
            elif durationinput[-2] =="mo":
                duration = int(int(durationinput[:-2])*2629746)
                durationsuffix = "month(s)"
            elif durationinput[-1] == "y":
                duration=int(int(durationinput[:-1])*31556952)
                durationsuffix = "year(s)"
            elif durationinput.lower() == "permanent" or durationinput.lower() == "perm":
                duration = "Permanent"
                durationsuffix = ""
            else:
                duration = "ERROR"
                durationsuffix = create_error_embed(title=f"Invalid duration", description=f"You provided an invalid duration.")
        except:
            duration = "ERROR"
            durationsuffix = create_error_embed(title=f"Invalid duration", description=f"You provided an invalid duration.")
        return duration, durationsuffix

    @staticmethod
    async def create_punishment_log_embed(punishment, punishment_id, member, moderator, reason="Not Given", duration=None, expires=None, colour=COLOUR_BAD, evidence="Not Given"):
        embed = nextcord.Embed(title=str(punishment).capitalize(), description=f"**Member**: {member.mention} ({member.id})\n**Responsible Moderator**: {moderator.mention} ({moderator.id})\n**Reason**: `{reason[:300] if reason else 'Not Given'}`\n**Evidence**: {evidence}", colour=colour)
        valid_perms = ["per", "perm", "permanent"]
        if not duration:
            pass
        elif str(duration.replace(" ", "")).lower() in valid_perms:
            embed.description += "\n**Duration**: Permanent\n**Expires**: Never"
        else:
            embed.description += f"\n**Duration**: {duration}\n**Expires**: <t:{expires}> (<t:{expires}:R>)"
        embed.set_footer(text=f"Punishment ID: {punishment_id}")
        return embed
    
    async def log_punishment_in_database(self, guild_id, member_id, mod_id, type, duration, expires, reason="Not Given", evidence="None"):
        pun_id = await self.create_punishment_id()
        data = Bot.db.create_data("guild_mod", guild_id=guild_id, punishment_id=pun_id, member_id=member_id, mod_id=mod_id, type=type, reason=reason if reason else "Not Given", duration=duration, expires=expires, given=round(time.time()), expired="no", evidence=evidence)
        return data

    async def timeout_user(self, guild, moderator, member, duration, duration_input, reason="Not Given", evidence="None"):
        timeout_time = nextcord.utils.utcnow()+datetime.timedelta(seconds=duration)
        await member.timeout(timeout=timeout_time, reason=reason)
        data = await self.log_punishment_in_database(guild.id, member.id, moderator.id, type="timeout", duration=duration, expires=round(timeout_time.timestamp()), reason=reason, evidence=evidence)
        await self.log_moderation(guild=guild, embed=await self.create_punishment_log_embed("timeout", data.punishment_id, member, moderator, reason, duration_input, data.expires, evidence=evidence))

    async def warn_user(self, guild, moderator, member, duration, duration_input, reason="Not Given", evidence="None"):
        data = await self.log_punishment_in_database(guild.id, member.id, moderator.id, type="warning", duration=duration, expires="None", reason=reason, evidence=evidence)
        await self.log_moderation(guild=guild, embed=await self.create_punishment_log_embed("warning", data.punishment_id, member, moderator, reason, evidence=evidence))
    
    async def kick_user(self, guild, moderator, member, duration, duration_input, reason="Not Given", evidence="None"):
        await member.kick(reason=reason)
        data = await self.log_punishment_in_database(guild.id, member.id, moderator.id, type="kick", duration=duration, expires="None", reason=reason, evidence=evidence)
        await self.log_moderation(guild=guild, embed=await self.create_punishment_log_embed("kick", data.punishment_id, member, moderator, reason, evidence=evidence))

    async def ban_user(self, guild, moderator, member, duration, duration_input, reason="Not Given", evidence="None"):
        await guild.ban(member, reason=reason)
        data: List[GuildMod] = Bot.db.get_data("guild_mod", guild_id=guild.id, member_id=member.id, type="ban")
        if data:
            for log in data:
                log.expired = "yes"
                log.expires = round(time.time())
                log.evidence = evidence
                Bot.db.update_data("guild_mod", data=log)
        data = await self.log_punishment_in_database(guild.id, member.id, moderator.id, type="ban", duration=duration, expires=(round(time.time())+duration) if not duration == "Permanent" else "Never", reason=reason, evidence=evidence)
        await self.log_moderation(guild=guild, embed=await self.create_punishment_log_embed("ban", data.punishment_id, member, moderator, reason, duration_input, data.expires, evidence=evidence))
    
    async def mute_user(self, guild, moderator, member, duration, duration_input, reason="Not Given", evidence="None"):
        data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=guild.id)
        if not data:
            return "ERROR - NO ROLE"
        data = data[0]
        try:
            muted_role = guild.get_role(data.muted_role)
            await member.add_roles(muted_role)
        except:
            return "ERROR - NO ROLE"
        data: List[GuildMod] = Bot.db.get_data("guild_mod", guild_id=guild.id, member_id=member.id, type="mute", expired="no")
        if data:
            for log in data:
                if not log.expired == "yes":
                    log.expired = "yes"
                    log.expires = round(time.time())
                    log.evidence = evidence
                    Bot.db.update_data("guild_mod", data=log)
        data = await self.log_punishment_in_database(guild.id, member.id, moderator.id, type="mute", duration=duration, expires=(round(time.time())+duration) if not duration == "Permanent" else "Never", reason=reason, evidence=evidence)
        await self.log_moderation(guild=guild, embed=await self.create_punishment_log_embed("mute", data.punishment_id, member, moderator, reason, duration_input, data.expires, evidence=evidence))
    
    async def untimeout_user(self, guild, moderator, member, duration, duration_input, reason="Not Given"):
        await member.timeout(timeout=None, reason=reason)
        data: List[GuildMod] = Bot.db.get_data("guild_mod", guild_id=guild.id, member_id=member.id, type="timeout")
        if data:
            for log in data:
                log.expired = "yes"
                log.expires = round(time.time())
                Bot.db.update_data("guild_mod", data=log)
        data = await self.log_punishment_in_database(guild.id, member.id, moderator.id, type="untimeout", duration=duration, expires="None", reason=reason)
        await self.log_moderation(guild=guild, embed=await self.create_punishment_log_embed("untimeout", data.punishment_id, member, moderator, reason, colour=COLOUR_GOOD))

    async def unmute_user(self, guild, moderator, member, duration, duration_input, reason="Not Given"):
        data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=guild.id)
        if not data:
            return "ERROR - NO ROLE"
        data = data[0]
        try:
            muted_role = guild.get_role(data.muted_role)
            if not muted_role in member.roles:
                return "ERROR - DONT HAVE ROLE"
            await member.remove_roles(muted_role)
        except:
            return "ERROR - NO ROLE"
        data: List[GuildMod] = Bot.db.get_data("guild_mod", guild_id=guild.id, member_id=member.id, type="mute", expired="no")
        if data: 
            for log in data:
                if not log.expired == "yes":
                    log.expires = round(time.time())
                    log.expired = "yes"
                    Bot.db.update_data("guild_mod", data=log)
        data = await self.log_punishment_in_database(guild.id, member.id, moderator.id, type="unmute", duration=duration, expires="None", reason=reason)
        await self.log_moderation(guild=guild, embed=await self.create_punishment_log_embed("unmute", data.punishment_id, member, moderator, reason, colour=COLOUR_GOOD))

    
    async def unban_user(self, guild, moderator, member, duration, duration_input, reason="Not Given"):
        try:
            await guild.unban(user=member, reason=reason)
        except Exception as e:
            return "ERROR - NOT BANNED"
        data: List[GuildMod] = Bot.db.get_data("guild_mod", guild_id=guild.id, member_id=member.id, type="ban", expired="no")
        if data: 
            for log in data:
                if not log.expired == "yes":
                    log.expires = round(time.time())
                    log.expired = "yes"
                    Bot.db.update_data("guild_mod", data=log)
        data = await self.log_punishment_in_database(guild.id, member.id, moderator.id, type="unban", duration=duration, expires="None", reason=reason)
        await self.log_moderation(guild=guild, embed=await self.create_punishment_log_embed("unban", data.punishment_id, member, moderator, reason, colour=COLOUR_GOOD))

    @staticmethod
    async def check_user_mute(guild, member):
        data: List[GuildMod] = Bot.db.get_data("guild_mod", guild_id=guild.id, member_id=member.id, type="mute", expired="no")
        if data:
            return True
        return False
            
    
    @nextcord.slash_command(name=f"timeout", description=f"Timeout a user")
    async def timeout(self,
        interaction: Interaction,
        member : nextcord.Member = SlashOption(
            name="member",
            description=f"Member to timeout",
            required=True
        ),
        duration_input: str = SlashOption(
            name=f"duration",
            description=f"Duration to timeout user for",
            required=True
        ),
        reason: str = SlashOption(
            name=f"reason",
            description=f"Reason for the timeout",
            required=False
        ),
        evidence: str = SlashOption(
            name="evidence",
            description="Evidence for punishment",
            required=False
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        await interaction.response.defer()
        duration, durationsuffix = await self.duration_input_to_text(duration_input)
        if duration == "ERROR":
            await interaction.send(embed=durationsuffix)
            return
        if duration > 2419200:
            if duration_input[:-1] + durationsuffix == "1month(s)":
                duration = 2419200
            else:
                await interaction.send(embed=create_warning_embed(title=f"Invalid duration", description=f"All timeouts must have a duration under 28 days. This a restriction put in place by discord. If you would like to bypass this restriction, please use the `/mute` command instead of `/timeout`."))
                return
        await self.timeout_user(interaction.guild, interaction.user, member, duration, (duration_input[:-1] + " " + durationsuffix), reason=reason, evidence=evidence)
        embed = nextcord.Embed(title=f"Member timed out", description=f"I have successfully timed out {member.mention} for {duration_input[:-1] + ' ' + durationsuffix} with reason: `{reason if reason else 'Not Given'}`.\n\nIt will expire in <t:{round(time.time())+duration}:R>", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        try:
            await member.send(embed=nextcord.Embed(title=f"Timeout", description=f"You have been timed out in **{interaction.guild.name}** until <t:{round(time.time())+duration}:R> with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_BAD))
        except:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this punishment.", colour=COLOUR_BAD)])

    @nextcord.user_command(name=f"Timeout user")
    async def user_timeout(self, interaction: Interaction, member: nextcord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"), ephemeral=True)
            return
        modal_options = TimeoutAppView()
        await interaction.response.send_modal(modal_options)
        await modal_options.wait()
        duration_input = modal_options.duration_input
        reason = modal_options.reason
        evidence = modal_options.evidence
        duration, durationsuffix = await self.duration_input_to_text(duration_input)
        if duration == "ERROR":
            await interaction.send(embed=durationsuffix)
            return
        if duration > 2419200:
            if duration_input[:-1] + durationsuffix == "1month(s)":
                duration = 2419200
            else:
                await interaction.send(embed=create_warning_embed(title=f"Invalid duration", description=f"All timeouts must have a duration under 28 days. This a restriction put in place by discord. If you would like to bypass this restriction, please use the `/mute` command instead of `/timeout`."), ephemeral=True)
                return
        await self.timeout_user(interaction.guild, interaction.user, member, duration, (duration_input[:-1] + " " + durationsuffix), reason=reason, evidence=evidence)
        embed = nextcord.Embed(title=f"Member timed out", description=f"I have successfully timed out {member.mention} for {duration_input[:-1] + ' ' + durationsuffix} with reason: `{reason if reason else 'Not Given'}`.\n\nIt will expire in <t:{round(time.time())+duration}:R>", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        try:
            await member.send(embed=nextcord.Embed(title=f"Timeout", description=f"You have been timed out in **{interaction.guild.name}** until <t:{round(time.time())+duration}:R> with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_BAD))
        except:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this punishment.", colour=COLOUR_BAD)])

    @nextcord.slash_command(name=f"warn", description=f"Warn a user")
    async def warn(self,
        interaction: Interaction,
        member : nextcord.Member = SlashOption(
            name="member",
            description=f"Member to warn",
            required=True
        ),
        reason: str = SlashOption(
            name=f"reason",
            description=f"Reason for the warning",
            required=False
        ),
        evidence: str = SlashOption(
            name="evidence",
            description="Evidence for punishment",
            required=False
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        await interaction.response.defer()
        await self.warn_user(interaction.guild, interaction.user, member, "None", "None", reason=reason, evidence=evidence)
        embed = nextcord.Embed(title=f"Member warned", description=f"I have successfully warned {member.mention} with reason: `{reason if reason else 'Not Given'}`.", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        try:
            await member.send(embed=nextcord.Embed(title=f"Warning", description=f"You have been warned in **{interaction.guild.name}** with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_NEUTRAL))
        except:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this punishment.", colour=COLOUR_BAD)])

    @nextcord.user_command(name=f"Warn user")
    async def user_warn(self,interaction: Interaction,member : nextcord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        modal_options = WarningAppView()
        await interaction.response.send_modal(modal_options)
        await modal_options.wait()
        reason = modal_options.reason
        evidence = modal_options.evidence
        await self.warn_user(interaction.guild, interaction.user, member, "None", "None", reason=reason, evidence=evidence)
        embed = nextcord.Embed(title=f"Member warned", description=f"I have successfully warned {member.mention} with reason: `{reason if reason else 'Not Given'}`.", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        try:
            await member.send(embed=nextcord.Embed(title=f"Warning", description=f"You have been warned in **{interaction.guild.name}** with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_NEUTRAL))
        except:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this punishment.", colour=COLOUR_BAD)])

    @nextcord.slash_command(name=f"kick", description=f"Kick a user")
    async def kick(self,
        interaction: Interaction,
        member : nextcord.Member = SlashOption(
            name="member",
            description=f"Member to kick",
            required=True
        ),
        reason: str = SlashOption(
            name=f"reason",
            description=f"Reason for the kick",
            required=False
        ),
        evidence: str = SlashOption(
            name="evidence",
            description="Evidence for punishment",
            required=False
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        await interaction.response.defer()
        messaged = True
        try:
            await member.send(embed=nextcord.Embed(title=f"Kick", description=f"You were kicked from **{interaction.guild.name}** with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_BAD))
        except:
            messaged = False
        await self.kick_user(interaction.guild, interaction.user, member, "None", "None", reason=reason, evidence=evidence)
        embed = nextcord.Embed(title=f"Member kicked", description=f"I have successfully kicked {member.mention} with reason: `{reason if reason else 'Not Given'}`.", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        if not messaged:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this punishment.", colour=COLOUR_BAD)])
    @nextcord.user_command(name=f"Kick user")
    async def user_kick(self,interaction: Interaction,member : nextcord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        modal_options = WarningAppView()
        await interaction.response.send_modal(modal_options)
        await modal_options.wait()
        reason = modal_options.reason
        evidence = modal_options.evidence
        messaged = True
        try:
            await member.send(embed=nextcord.Embed(title=f"Kick", description=f"You were kicked from **{interaction.guild.name}** with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_BAD))
        except:
            messaged = False
        await self.kick_user(interaction.guild, interaction.user, member, "None", "None", reason=reason, evidence=evidence)
        embed = nextcord.Embed(title=f"Member kicked", description=f"I have successfully kicked {member.mention} with reason: `{reason if reason else 'Not Given'}`.", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        if not messaged:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this punishment.", colour=COLOUR_BAD)])

    @nextcord.slash_command(name=f"ban", description=f"Ban a user")
    async def ban(self,
        interaction: Interaction,
        member : nextcord.Member = SlashOption(
            name="member",
            description=f"Member to ban",
            required=True
        ),
        duration_input: str = SlashOption(
            name=f"duration",
            description=f"Duration to ban user for",
            required=True
        ),
        reason: str = SlashOption(
            name=f"reason",
            description=f"Reason for the ban",
            required=False
        ),
        evidence: str = SlashOption(
            name="evidence",
            description="Evidence for punishment",
            required=False
        )):
        if not interaction.user.guild_permissions.moderate_members or not interaction.user.guild_permissions.ban_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` and `ban_members` permission to run this command"), ephemeral=True)
            return
        if member in interaction.guild.members and member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        await interaction.response.defer()
        duration, durationsuffix = await self.duration_input_to_text(duration_input)
        if duration == "ERROR":
            await interaction.send(embed=durationsuffix)
            return
        if not duration == "Permanent" and duration > 3155695200:
            duration = 3155695200
        messaged = True
        try:
            await member.send(embed=nextcord.Embed(title=f"Banned", description=f"You have been banned in **{interaction.guild.name}** until <t:{round(time.time())+duration}:R> with reason: `{reason if reason else 'Not Given'}`" if not duration == "Permanent" else f"You have been permanently banned in **{interaction.guild.name}** with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_BAD))
        except:
            messaged = False
        await self.ban_user(interaction.guild, interaction.user, member, duration, (duration_input[:-1] + " " + durationsuffix), reason=reason, evidence=evidence)
        embed = nextcord.Embed(title=f"Member banned", description=f"I have successfully banned {member.mention} for {duration_input[:-1] + ' ' + durationsuffix} with reason: `{reason if reason else 'Not Given'}`.\n\nIt will expire <t:{round(time.time())+duration}:R>" if duration != "Permanent" else f"I have successfully banned {member.mention} permanently with reason: `{reason if reason else 'Not Given'}`.\n\nIt will never expire", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        if not messaged:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this punishment.", colour=COLOUR_BAD)])

    
    @nextcord.slash_command(name=f"mute", description=f"Mute a user")
    async def mute(self,
        interaction: Interaction,
        member : nextcord.Member = SlashOption(
            name="member",
            description=f"Member to mute",
            required=True
        ),
        duration_input: str = SlashOption(
            name=f"duration",
            description=f"Duration to mute user for",
            required=True
        ),
        reason: str = SlashOption(
            name=f"reason",
            description=f"Reason for the mute",
            required=False
        ),
        evidence: str = SlashOption(
            name="evidence",
            description="Evidence for punishment",
            required=False
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        await interaction.response.defer()
        duration, durationsuffix = await self.duration_input_to_text(duration_input)
        if duration == "ERROR":
            await interaction.send(embed=durationsuffix)
            return
        if not duration == "Permanent" and duration > 3155695200:
            duration = 3155695200
        status = await self.mute_user(interaction.guild, interaction.user, member, duration, (duration_input[:-1] + " " + durationsuffix), reason=reason, evidence=evidence)
        if status == "ERROR - NO ROLE":
            await interaction.send(embed=create_error_embed(title=f"No muted role", description=f"You don't have a valid muted role set. If you have a muted role set, please follow [this guide](https://nomindustries.com/help/knowledgebase.php?article=2) to make sure I can add it to people"))
            return
        embed = nextcord.Embed(title=f"Member muted", description=f"I have successfully muted {member.mention} for {duration_input[:-1] + ' ' + durationsuffix} with reason: `{reason if reason else 'Not Given'}`.\n\nIt will expire <t:{round(time.time())+duration}:R>" if duration != "Permanent" else f"I have successfully muted {member.mention} permanently with reason: `{reason if reason else 'Not Given'}`.\n\nIt will never expire", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        try:
            await member.send(embed=nextcord.Embed(title=f"Muted", description=f"You have been muted in **{interaction.guild.name}** until <t:{round(time.time())+duration}:R> with reason: `{reason if reason else 'Not Given'}`" if not duration == "Permanent" else f"You have been permanently muted in **{interaction.guild.name}** with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_BAD))
        except:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this punishment.", colour=COLOUR_BAD)])

    @nextcord.slash_command(name=f"untimeout", description=f"Remove a timeout from a user")
    async def untimeout(self,
        interaction: Interaction,
        member : nextcord.Member = SlashOption(
            name="member",
            description=f"Member to untimeout",
            required=True
        ),
        reason: str = SlashOption(
            name=f"reason",
            description=f"Reason for the removal of the timeout",
            required=False
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        if not member._timeout:
            await interaction.send(embed=create_warning_embed(title="Member not timed out!", description=f"{member.mention} is not currently timed out!"))
            return
        await interaction.response.defer()
        await self.untimeout_user(interaction.guild, interaction.user, member, "None", "None", reason=reason)
        embed = nextcord.Embed(title=f"Member timeout removed", description=f"I have successfully removed the timeout from {member.mention} with reason: `{reason if reason else 'Not Given'}`.", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        try:
            await member.send(embed=nextcord.Embed(title=f"Timeout removed", description=f"Your timeout in **{interaction.guild.name}** has been removed with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_GOOD))
        except:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this removal.", colour=COLOUR_BAD)])

    @nextcord.slash_command(name=f"unmute", description=f"Remove a mute from a user")
    async def unmute(self,
        interaction: Interaction,
        member : nextcord.Member = SlashOption(
            name="member",
            description=f"Member to unmute",
            required=True
        ),
        reason: str = SlashOption(
            name=f"reason",
            description=f"Reason for the removal of the mute",
            required=False
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` permission to run this command"), ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot punish member", description=f"That member has a higher or the same rank as you so you cannot punish them"))
            return
        await interaction.response.defer()
        status = await self.unmute_user(interaction.guild, interaction.user, member, "None", "None", reason=reason)
        if status == "ERROR - NO ROLE":
            await interaction.send(embed=create_error_embed(title=f"No muted role", description=f"You don't have a valid muted role set. If you have a muted role set, please follow [this guide](https://nomindustries.com/help/knowledgebase.php?article=2) to make sure I can add it to people"))
            return
        elif status == "ERROR - DONT HAVE ROLE":
            await interaction.send(embed=create_error_embed(title=f"Member doesn't have role", description=f"That member doesn't have the muted role so I cannot remove it. To mute a user use `/mute`."))
            return
        embed = nextcord.Embed(title=f"Member mute removed", description=f"I have successfully removed the mute from {member.mention} with reason: `{reason if reason else 'Not Given'}`.", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        try:
            await member.send(embed=nextcord.Embed(title=f"Mute removed", description=f"Your mute in **{interaction.guild.name}** has been removed with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_GOOD))
        except:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this removal.", colour=COLOUR_BAD)])

    @nextcord.slash_command(name=f"unban", description=f"Remove a ban from a user")
    async def unban(self,
        interaction: Interaction,
        memberid: str = SlashOption(
            name=f"member-id",
            description=f"The ID of the user you would like to unban",
            required=True
        ),
        reason: str = SlashOption(
            name=f"reason",
            description=f"Reason for the removal of the ban",
            required=False,
            default="Not Given"

        )):
        if not interaction.user.guild_permissions.moderate_members or not interaction.user.guild_permissions.ban_members:
            await interaction.send(embed=create_warning_embed(title=f"Invalid Permissions", description=f"You require the `moderate_members` and `ban_members` permission to run this command"), ephemeral=True)
            return
        
        await interaction.response.defer()
        try:
            member = await self.client.fetch_user(int(memberid))
        except Exception as e:
            await interaction.send(embed=create_error_embed(title="Invalid Member", description=f"That is not a valid member ID"))
            return
        status = await self.unban_user(interaction.guild, interaction.user, member, "None", "None", reason=reason)
        if status == "ERROR - NOT BANNED":
            await interaction.send(embed=create_error_embed(title="Member not banned", description=f"That member is not banned."))
            return
        embed = nextcord.Embed(title=f"Member ban removed", description=f"I have successfully removed the ban from {member.mention} with reason: `{reason if reason else 'Not Given'}`.", colour=COLOUR_GOOD)
        msg = await interaction.send(embed=embed)
        try:
            await member.send(embed=nextcord.Embed(title=f"Ban removed", description=f"Your ban in **{interaction.guild.name}** has been removed with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_GOOD))
        except:
            await msg.edit(embeds=[(embed), nextcord.Embed(description=f"I was unable to message {member.mention} to inform them of this removal.", colour=COLOUR_BAD)])


    @commands.Cog.listener()
    async def on_guild_audit_log_entry_create(self, entry):
        if entry.user == self.client.user:
            return
        if entry.user.bot:
            return
        if entry.action == nextcord.AuditLogAction.member_role_update:
            data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=entry.guild.id)
            if not data:
                return
            try:
                muted_role = entry.guild.get_role(int(data[0].muted_role))
                if not muted_role in entry.before.roles and muted_role in entry.after.roles:
                    status = await self.mute_user(entry.guild, entry.user, entry.target, "Permanent", "Permanent", reason=entry.reason if entry.reason else "Not Given")
                if muted_role in entry.before.roles and not muted_role in entry.after.roles:
                    data: List[GuildMod] = Bot.db.get_data("guild_mod", guild_id=entry.guild.id, member_id=entry.target.id, type="mute", expired="no")
                    if data: 
                        for log in data:
                            if not log.expired == "yes":
                                log.expires = round(time.time())
                                log.expired = "yes"
                                Bot.db.update_data("guild_mod", data=log)
                    print("1")
                    data = await self.log_punishment_in_database(entry.guild.id, entry.target.id, entry.user.id, type="unmute", duration="None", expires="None", reason=entry.reason if entry.reason else "Not Given")
                    print("2")
                    await self.log_moderation(guild=entry.guild, embed=await self.create_punishment_log_embed("unmute", data.punishment_id, entry.target, entry.user, entry.reason, colour=COLOUR_GOOD))
            except:
                pass
        if entry.action == nextcord.AuditLogAction.member_update:
            if not entry.after.communication_disabled_until is None:
                timeout_time = entry.after.communication_disabled_until
                expires = round(parser.parse(timeout_time).timestamp())
                duration = expires - round(time.time())
                td = datetime.timedelta(seconds=duration)
                duration_input = f"{td.days}d {td.seconds//3600}h {(td.seconds//60)%60}m {td.seconds%60}s"
                data = await self.log_punishment_in_database(entry.guild.id, entry.target.id, entry.user.id, type="timeout", duration=duration, expires=expires, reason=entry.reason if entry.reason else "Not Given")
                await self.log_moderation(guild=entry.guild, embed=await self.create_punishment_log_embed("timeout", data.punishment_id, entry.target, entry.user, entry.reason if entry.reason else "Not Given", duration_input, data.expires))
            if not entry.before.communication_disabled_until is None and entry.after.communication_disabled_until is None:
                data: List[GuildMod] = Bot.db.get_data("guild_mod", guild_id=entry.guild.id, member_id=entry.target.id, type="timeout")
                if data:
                    for log in data:
                        log.expired = "yes"
                        log.expires = round(time.time())
                        Bot.db.update_data("guild_mod", data=log)
                data = await self.log_punishment_in_database(entry.guild.id, entry.target.id, entry.user.id, type="untimeout", duration="None", expires="None", reason=entry.reason if entry.reason else "Not Given")
                await self.log_moderation(guild=entry.guild, embed=await self.create_punishment_log_embed("untimeout", data.punishment_id, entry.target, entry.user, entry.reason if entry.reason else "Not Given", colour=COLOUR_GOOD))
    
    @nextcord.slash_command(name="purge", description="clear some messages from the chat")
    async def purge(self,
        interaction: Interaction,
        amount: int = SlashOption(
            name="amount",
            description="Amount of messages to purge",
            required=True
        ),
        member: nextcord.Member = SlashOption(
            name="member",
            description=f"Member to purge messages of",
            required=False
        )):
        if amount < 0 or amount > 100:
            await interaction.send("Amount of messages must be > 0 and < 100")
            return
        if interaction.user.guild_permissions.manage_messages:
            await interaction.response.defer(ephemeral=True)
            embed = nextcord.Embed(title=f"Purging...", description=f"Please wait...", colour=COLOUR_MAIN)
            msg = await interaction.send(embed=embed, ephemeral=True)
            if member:
                msgs = []
                async for m in interaction.channel.history():
                    if len(msgs) == amount:
                        break
                    if m.author == member:
                        msgs.append(m)
                await interaction.channel.delete_messages(msgs)
                await msg.delete()
                await interaction.channel.send(embed=nextcord.Embed(title=f"Purged messages", description=f"{interaction.user.mention}, I have successfully purged {len(msgs)} {('of ' + member.mention + ' ') if member else ''}messages", colour=COLOUR_MAIN), view=PurgeView(), delete_after=10)
            else:
                msgs = []
                async for m in interaction.channel.history():
                    if len(msgs) == amount:
                        break
                    msgs.append(m)
                await interaction.channel.delete_messages(msgs)
                await msg.delete()
                await interaction.channel.send(embed=nextcord.Embed(title=f"Purged messages", description=f"{interaction.user.mention}, I have successfully purged {len(msgs)} messages", colour=COLOUR_MAIN), view=PurgeView(), delete_after=10)

    @nextcord.slash_command(name="lock", description="lock a channel")
    async def lock(self,
        interaction: Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="Channel to lock",
            channel_types=[nextcord.ChannelType.text],
            required=True
        )):
        if interaction.user.guild_permissions.manage_channels:
            await interaction.response.defer()
            role = interaction.guild.roles[0]
            overwrites = channel.overwrites_for(role)
            read_messages = overwrites.read_messages
            await channel.set_permissions(role, send_messages=False, read_messages=read_messages)
            await interaction.send(f"Successfully locked {channel.mention}", view=UnlockView(channel.id, org_user=interaction.user.id))

    @nextcord.slash_command(name="unlock", description="unlock a channel")
    async def unlock(self,
        interaction: Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="Channel to lock",
            channel_types=[nextcord.ChannelType.text],
            required=True
        )):
        if interaction.user.guild_permissions.manage_channels:
            await interaction.response.defer()
            role = interaction.guild.roles[0]
            overwrites = channel.overwrites_for(role)
            read_messages = overwrites.read_messages
            await channel.set_permissions(role, send_messages=None, read_messages=read_messages)
            await interaction.send(f"Successfully unlocked {channel.mention}", view=LockView(channel.id, org_user=interaction.user.id))


    @nextcord.slash_command(name=f"setnick", description=f"Set a user's nickname")
    async def setnick(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name=f"member",
            description=f"Member to change nick of",
            required=True
        ),
        nick: str = SlashOption(
            name=f"nickname",
            description=f"What to change the users nick to",
            required=True
        )):
        if not interaction.user.guild_permissions.manage_nicknames:
            await interaction.send(f"You require `manage nicknames` permission to run this command")
            return
        if member.top_role >= interaction.user.top_role and not interaction.user == interaction.guild.owner:
            await interaction.send(embed=create_warning_embed(title="Cannot change members nickname", description=f"That member has a higher or the same rank as you so you cannot change their nick"))
            return
        await interaction.response.defer()
        await member.edit(nick=nick)
        await interaction.send(embed=create_success_embed(title=f"Change nickname", description=f"I have changed **{member.name}**'s nickname to `{nick}`"))


    @nextcord.slash_command(name="modlogs", description="Get the moderation history for a member")
    async def modlogs(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to get modlogs of",
            required=True
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(f"You are not allowed to use this command")
            return
        await interaction.response.defer()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM guild_mod WHERE member_id = %s AND guild_id = %s", (member.id, interaction.guild.id))
        data = cur.fetchall()
        cur.execute("SELECT * FROM guild_mod WHERE member_id = %s AND guild_id = %s AND type IN ('mute', 'ban', 'timeout', 'kick', 'warning')", (member.id, interaction.guild.id))
        data2 = cur.fetchall()
        conn.commit()
        if not data:
            await interaction.send(embed=nextcord.Embed(description=f"No mod logs found for {member.mention} ({member.id})", colour=COLOUR_NEUTRAL))
            return

        embed = nextcord.Embed(title=f"Member Modlogs ({(len(data))})", color=COLOUR_MAIN)
        pages = {}
        member = await self.client.fetch_user(int(data[0][2]))
        for i in range(0, len(data), 10):
            embed = nextcord.Embed(title=f"Member Modlogs ({(len(data))})", color=COLOUR_MAIN)
            for j in data[i:i+10]:
                moderator = False
                if len(data) < 7:
                    moderator = await self.client.fetch_user(int(j[3]))          
                duration = j[6]
                durationtext = ""
                if not duration == "None":
                    if not duration == "Permanent":
                        duration=int(duration)
                        td = datetime.timedelta(seconds=duration)
                        durationtext = f"{td.days}d {td.seconds//3600}h {(td.seconds//60)%60}m {td.seconds%60}s"
                    else:
                        durationtext = duration 
                embed.add_field(name=f"Punishment `{j[1]}`", value=f"""**Member**: {member} ({member.id})
**Responsible Moderator**: <@{j[3]}>
**Punishment Type**: {str(j[4]).capitalize()} {f'- {durationtext}' if not duration == "None" else ""}
**Reason**: {(str(j[5]))[:50]} - <t:{j[8]}>
**Evidence**: {(str(j[10]))[:50]}""", inline=False)
            embed.set_footer(text=f"Page: {i//10+1} | Use `/punishment info <punishmentId>` to get more information on a specific punishment.")
            
            pages[i//10] = embed
        neg_pages = {}
        member = await self.client.fetch_user(int(data[0][2]))
        for i in range(0, len(data2), 10):
            embed = nextcord.Embed(title=f"Member Modlogs ({(len(data2))})", color=COLOUR_MAIN)
            for j in data2[i:i+10]:
                moderator = False
                if len(data) < 7:
                    moderator = await self.client.fetch_user(int(j[3]))          
                duration = j[6]
                durationtext = ""
                if not duration == "None":
                    if not duration == "Permanent":
                        duration=int(duration)
                        td = datetime.timedelta(seconds=duration)
                        durationtext = f"{td.days}d {td.seconds//3600}h {(td.seconds//60)%60}m {td.seconds%60}s"
                    else:
                        durationtext = duration 
                embed.add_field(name=f"Punishment `{j[1]}`", value=f"""**Member**: {member} ({member.id})
**Responsible Moderator**: <@{j[3]}>
**Punishment Type**: {str(j[4]).capitalize()} {f'- {durationtext}' if not duration == "None" else ""}
**Reason**: {(str(j[5]))[:50]} - <t:{j[8]}>
**Evidence**: {(str(j[10]))[:50]}""", inline=False)
            embed.set_footer(text=f"Page: {i//10+1} | Use `/punishment info <punishmentId>` to get more information on a specific punishment.")
            
            neg_pages[i//10] = embed
        modlog_menu = Modlogs_Information_View(pages=pages, neg_pages=neg_pages)
        non_pagified_modlog_menu = Modlogs_Information_View_Non_Pagified(pages=pages, neg_pages=neg_pages)
        await interaction.edit_original_message(content="", attachments=[], embed=neg_pages[0], view=modlog_menu if len(pages) > 1 else non_pagified_modlog_menu)
        await modlog_menu.wait()

    @nextcord.slash_command(name="warnings", description="Get the warning history for a member")
    async def warnings(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to get modlogs of",
            required=True
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(f"You are not allowed to use this command")
            return
        await interaction.response.defer()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM guild_mod WHERE member_id = %s AND guild_id = %s AND type=%s", (member.id, interaction.guild.id, "warning"))
        data = cur.fetchall()
        conn.commit()
        if not data:
            await interaction.send(embed=nextcord.Embed(description=f"No warnings found for {member.mention} ({member.id})", colour=COLOUR_NEUTRAL))
            return

        embed = nextcord.Embed(title=f"Member Warnings ({(len(data))})", color=COLOUR_MAIN)
        pages = {}
        member = await self.client.fetch_user(int(data[0][2]))
        for i in range(0, len(data), 10):
            embed = nextcord.Embed(title=f"Member Warnings ({(len(data))})", color=COLOUR_MAIN)
            for j in data[i:i+10]:
                moderator = False
                if len(data) < 7:
                    moderator = await self.client.fetch_user(int(j[3]))           
                embed.add_field(name=f"Punishment `{j[1]}`", value=f"""**Member**: {member} ({member.id})
**Responsible Moderator{" ID" if not moderator else ""}**: {(f"{moderator} ({moderator.id})") if moderator else int(j[3])}
**Punishment Type**: {str(j[4]).capitalize()}
**Reason**: {(str(j[5]))[:50]} - <t:{j[8]}>
***Evidence**: {(str(j[10]))[:50]}""", inline=False)
            embed.set_footer(text=f"Page: {i//10+1} | Use `/punishment info <punishmentId>` to get more information on a specific punishment.")
            
            pages[i//10] = embed

        modlog_menu = Modlogs_Information_View(pages=pages)
        await interaction.edit_original_message(content="", attachments=[], embed=pages[0], view=modlog_menu if len(pages) > 1 else None)
        await modlog_menu.wait()

    @nextcord.slash_command("slowmode", description=f"Set a channels slowmode")
    async def slowmode(self,
        interaction:Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="What channel do you want to change the slowmode of",
            required=False,
            channel_types=[nextcord.ChannelType.text]
        ),
        durationinput:str=SlashOption(
            name="time",
            description=f"The time you want to set as the channel slowmode",
            required=False,
            default="0s"
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(f"You are not allowed to use this command")
            return
        if not channel:
            channel = interaction.channel
        if durationinput[-1] == "s":
            duration=int(int(durationinput[:-1]))
            durationsuffix = "second(s)"
        elif durationinput[-1] == "m":
            duration = int(int(durationinput[:-1])*60)
            durationsuffix = "min(s)"
        elif durationinput[-1] == "h":
            duration = int(int(durationinput[:-1])*3600)
            durationsuffix = "hour(s)"
        else:
            await interaction.send(embed=create_error_embed(title="Invalid Duration", description=f"You provided an invalid duration."))
            return
        if duration > 21600:
            await interaction.send("Duration must be < 6 hours")
            return

        await channel.edit(slowmode_delay=duration)
        await interaction.send(embed=create_success_embed(title=f"Slowmode added", description=f"{channel.mention} now has a slowmode of {durationinput[:-1]} {durationsuffix}"))
        

        

    @nextcord.slash_command(name="punishment", description="Punishment commands")
    async def punishment(self, interaction: nextcord.Interaction):
        pass
        

    @punishment.subcommand(name="info", description="Get the information on a specific punishment")
    async def punishment_info(self,
        interaction: Interaction,
        punishmentId: str = SlashOption(
            name="punishment-id",
            description="The punishment ID of the punishment you want to check (case-sensitive)",
            required=True
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(f"You are not allowed to use this command")
            return
        await interaction.response.defer()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM guild_mod WHERE punishment_id = %s AND guild_id = %s", (punishmentId, interaction.guild.id))
        data = cur.fetchall()
        conn.commit()
        if not data:
            await interaction.send(embed=create_error_embed(title="Error!", description="I couldn't find a punishment from this server with that ID"))
            return
        embed=nextcord.Embed(title=f"`{punishmentId}` punishment info", colour=COLOUR_MAIN)
        try:
            member = await self.client.fetch_user(int(data[0][2]))
            embed.add_field(name="Member", value=f"{member} ({member.id})")
        except:
            pass
        try:
            moderator = await self.client.fetch_user(int(data[0][3]))
            embed.add_field(name="Responsible Moderator", value=f"{moderator} ({moderator.id})")
        except:
            pass
        punishmenttype=data[0][4]
        embed.add_field(name=f"Punishment Type", value=f"{punishmenttype}")
        reason = data[0][5]
        embed.add_field(name=f"Reason", value=f"``{reason[0:500]}``")
        duration = data[0][6]
        evidence = data[0][10]
        if not duration == "None":
            if not duration == "Permanent":
                duration=int(duration)
                td = datetime.timedelta(seconds=duration)
                durationtext = f"{td.days}d {td.seconds//3600}h {(td.seconds//60)%60}m {td.seconds%60}s"
            else:
                durationtext = duration
            embed.add_field(name="Duration", value=f"{durationtext}")
        if not duration == "None":
            expires = data[0][7]
            if not expires == "Never":
                embed.add_field(name="Expires" if int(expires) > round(time.time()) else "Expired", value=f"<t:{expires}> (<t:{expires}:R>)")
            else:
                embed.add_field(name="Expires", value=f"Never")
        given = data[0][8]
        embed.add_field(name="Given", value=f"<t:{given}>")
        embed.add_field(name="Evidence", value=evidence)

        await interaction.send(embed=embed)

    @punishment.subcommand(name="edit", description="Edit the information of a punishment")
    async def punishment_edit(self,
        interaction: Interaction,
        punishmentId: str = SlashOption(
            name="punishment-id",
            description="The punishment ID for the punishment you want to edit",
            required=True
        )):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.send(f"You are not allowed to use this command")
            return
        await interaction.response.defer()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `guild_mod` WHERE punishment_id = %s AND guild_id = %s", (punishmentId, interaction.guild.id))
        data = cur.fetchall()
        conn.commit()
        if not data:
            await interaction.send(embed=create_error_embed(title="Error!", description="I couldn't find a punishment from this server with that ID"))
            return
        duration = data[0][6]
        if not duration == "None":
            if not duration == "Permanent":
                duration=int(duration)
                td = datetime.timedelta(seconds=duration)
                durationtext = ""
                durationtext += f"{td.days}d" if td.days != 0 else ""
                durationtext += f"{td.seconds//3600}h" if td.seconds//3600 != 0 else ""
                durationtext += f"{(td.seconds//60)%60}m" if (td.seconds//60)%60 != 0 else ""
                durationtext += f"{td.seconds%60}s" if td.seconds%60 != 0 else ""

            else:
                durationtext = duration
        else:
            durationtext = "N/A"

        embed=nextcord.Embed(title="Punishment Edit", description=f"""Punishment Information:
        
``Member ID: {data[0][2]}
Moderator ID: {data[0][3]}
Punishment Type: {str(data[0][4]).capitalize()}
Duration: {durationtext}
Reason: {str(data[0][5])[:1500]}
Evidence: {str(data[0][10])[:300]}``

Please select what you want to do next using the buttons below""", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=Punishment_Edit(data, interaction.user))

    @nextcord.slash_command(name=f"unraid", description=f"Ban or kick all members who meet specific checks")
    async def unraid(self,
        interaction:Interaction,
        duration:str=SlashOption(
            name=f"duration",
            description=f"How long the users must have been in the guild to remove",
            required=True,
            choices={"10 minutes": "600", "30 minutes": "1800", "1 hour": "3600", "6 hours": "21600", "12 hours": "43200", "1 day": "86400"}
        ),
        text:str=SlashOption(
            name=f"text",
            description=f"The text all the users must have in their name",
            required=False,
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(f"You are not allowed to use this command")
            return
        await interaction.response.defer()
        if interaction.guild.id in unraiding:
            await interaction.send(embed=create_error_embed(title=f"Already unraiding", description=f"You are already running the unraid command. Please wait for that to finish before running it again"))
        unraiding.append(interaction.guild.id)
        members_to_kick=[]
        for member in interaction.guild.members:
            now = datetime.datetime.now(datetime.timezone.utc)
            secs = (now - member.joined_at).total_seconds()
            if not secs > int(duration):
                if text:
                    if text.lower() in member.name.lower():
                        members_to_kick.append(member)
                else:
                    members_to_kick.append(member)
        if len(members_to_kick) == 0:
            index = unraiding.index(interaction.guild.id)
            del unraiding[index]
            await interaction.send(embed=create_error_embed(title=f"No members found", description=f"We couldn't find any members that met the given requirements "))
            return
        confirmmenu = Confirm(org_user=interaction.user.id)
        embed = nextcord.Embed(title="Please Confirm", description=f"Are you sure you want to ban {len(members_to_kick)} members\n\n**THIS ACTION CANNOT BE UNDONE**", colour=COLOUR_NEUTRAL)
        cm = await interaction.send(embed=embed, view=confirmmenu)
        r = await confirmmenu.wait()
        if r:
            await cm.delete()
        chosen = confirmmenu.value
        if chosen:
            await interaction.edit_original_message(embed=nextcord.Embed(description=f"Banning {len(members_to_kick)} members. This will take approximately {len(members_to_kick)} seconds.", colour=COLOUR_MAIN), view=None)
            for member in members_to_kick:
                try:
                    await member.ban(reason=f"Unraid run by {interaction.user}")
                    await asyncio.sleep(0.6)
                except Exception as e:
                    pass
            index = unraiding.index(interaction.guild.id)
            del unraiding[index]
            await interaction.edit_original_message(embed=nextcord.Embed(description=f"Successfully banned {len(members_to_kick)} members", colour=COLOUR_GOOD))
        else:
            index = unraiding.index(interaction.guild.id)
            del unraiding[index]
            await interaction.edit_original_message(embed=nextcord.Embed(title=f"Cancelled", description=f"You successfully cancelled the action.", colour=COLOUR_BAD), view=None)



#Nickname requests

    @nextcord.slash_command(name="nickname", description="nickname base")
    async def nickname(self, interaction: Interaction):
        pass

    @nickname.subcommand(name="request", description="nickname request base")
    async def nickname_request(self, interaction: Interaction):
        pass

    @nickname_request.subcommand(name="disable", description="Disable the nickname request system")
    async def nickname_request_disable(self, interaction:Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM nickname_main WHERE guild_id=%s", (interaction.guild.id))
        cur.execute("DELETE FROM nickname_requests WHERE guild=%s", (interaction.guild.id))
        conn.commit()
        await interaction.send(embed=create_success_embed(title="Success!", description=f"Successfully disabled the nickname requests system."))
    @nickname_request.subcommand(name="logchannel", description="Channel to send nickname requests to")
    async def nickname_request_logchannel(self,
        interaction: Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="channel to send nickname request logs to",
            channel_types=[nextcord.ChannelType.text],
            required=True
        ),
        modrole: nextcord.Role = SlashOption(
            name="modrole",
            description="Role that need to accept nickname requests",
            required=True
        ),
        requiredrole: nextcord.Role = SlashOption(
            name="required-role",
            description="Role that you need to send nickname requests",
            required=False,
            default=None
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM nickname_main WHERE guild_id=%s", interaction.guild.id)
        data = cur.fetchall()
        if requiredrole:
                requiredrole = requiredrole.id
        if not data:
            cur.execute("INSERT INTO nickname_main (guild_id, channel_id, mod_role_id, required_role) VALUES (%s, %s, %s, %s)", (interaction.guild.id, channel.id, modrole.id, requiredrole))
        else:
            cur.execute("UPDATE nickname_main SET guild_id=%s AND channel_id=%s AND mod_role_id=%s AND required_role=%s WHERE guild_id=%s", (interaction.guild.id, channel.id, modrole.id, requiredrole, interaction.guild.id))
        conn.commit()
        await interaction.send(embed=create_success_embed(title="Success!", description=f"Successfully setup nickname requests in {channel.mention}"))

    @nickname_request.subcommand(name="submit", description="Submit a nickname change request")
    async def nickname_request_submit(self,
        interaction: Interaction,
        new_nickname: str = SlashOption(
            name="nickname",
            description="The nickname you want to change to",
            required=True
        )):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM nickname_main WHERE guild_id=%s", interaction.guild.id)
        data = cur.fetchall()
        if len(new_nickname) < 2 or len(new_nickname) > 32:
            await interaction.send("The length of your requested nickname must be > 2 and < 32", ephemeral=True)
            return
        if not data:
            await interaction.send(embed=create_error_embed(title="No request channel", description="The server administrators have not setup this system yet."))
            return
        if data[0][3]:
            allowed=False
            for i in interaction.user.roles:
                if i.id == int(data[0][3]):
                    allowed=True
            if not allowed:
                await interaction.send(embed=create_error_embed(title="No permission", description=f"You require the <@&{data[0][3]}> role to request a nickname change"))
                return
        cur.execute("SELECT * FROM nickname_requests WHERE guild=%s AND user=%s", (interaction.guild.id, interaction.user.id))
        userdata = cur.fetchall()
        if userdata:
            await interaction.send(embed=create_error_embed(title="Request already outgoing", description="You already have an outgoing nickname request in this server. Wait for that request to recieve a verdict or do `/nickname request cancel` to cancel you last request"))
            return
        embed = nextcord.Embed(title="Nickname Request", colour=COLOUR_NEUTRAL)
        embed.set_author(name=f"{interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.add_field(name="User", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        embed.add_field(name="Request Name", value=f"{new_nickname}")
        channel = interaction.guild.get_channel(int(data[0][1]))
        msg = await channel.send(embed=embed, view=NicknameRequestManagement(self.client))
        await interaction.send("Nickname request sent!", ephemeral=True)
        cur.execute("INSERT INTO nickname_requests (guild, requested_nick, user, message_id, channel_sent_id) VALUES (%s, %s, %s, %s, %s)", (interaction.guild.id, new_nickname, interaction.user.id, msg.id, data[0][1]))
        conn.commit()

    @nickname_request.subcommand(name="accept", description="Accept a nickname request")
    async def nickname_request_accept(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to accept nick request for",
            required=True
        )):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM nickname_main WHERE guild_id=%s", interaction.guild.id)
        data = cur.fetchall()
        if not data:
            await interaction.send(embed=create_error_embed(title="System Error", description=f"This system has not yet been configured by the server administrators. Please contact them if you believe this is an error"), ephemeral=True)
            return
        cur.execute("SELECT * FROM nickname_requests WHERE guild=%s AND user=%s", (interaction.guild.id, member.id))
        requestdata = cur.fetchall()
        if not requestdata:
            await interaction.send(embed=create_error_embed(title="Invalid Member", description=f"This user doesn't currently have a nickname request outgoing"))
            return
        modroleid = data[0][2]
        role = interaction.guild.get_role(int(modroleid))
        if interaction.user.guild_permissions.administrator or role in interaction.user.roles:
            try:
                try:
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
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description=f"You are lacking {role.mention} so cannot use this command. Contact the server administrators if you believe this is an error"))
        

    @nickname_request.subcommand(name="deny", description="Deny a nickname request")
    async def nickname_request_deny(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to deny nick request for",
            required=True
        )):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM nickname_main WHERE guild_id=%s", interaction.guild.id)
        data = cur.fetchall()
        if not data:
            await interaction.send(embed=create_error_embed(title="System Error", description=f"This system has not yet been configured by the server administrators. Please contact them if you believe this is an error"), ephemeral=True)
            return
        cur.execute("SELECT * FROM nickname_requests WHERE guild=%s AND user=%s", (interaction.guild.id, member.id))
        requestdata = cur.fetchall()
        if not requestdata:
            await interaction.send(embed=create_error_embed(title="Invalid Member", description=f"This user doesn't currently have a nickname request outgoing"))
            return
        modroleid = data[0][2]
        role = interaction.guild.get_role(int(modroleid))
        if interaction.user.guild_permissions.administrator or role in interaction.user.roles:
            try:
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
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description=f"You are lacking {role.mention} so cannot use this command. Contact the server administrators if you believe this is an error"))

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.client.add_view(NicknameRequestManagement(self.client))
            print(color_message(message="Loaded NicknameRequestManagement view", color="blue"))
        except Exception as e:
            print(e)
            print(color_message(message="Failed to load NicknameRequestManagement view", color="yellow"))

    @commands.Cog.listener()
    async def on_member_unban(self, guild: nextcord.Guild, member: nextcord.Member):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM guild_mod WHERE guild_id=%s AND member_id=%s AND type='ban' AND expired='no'", (guild.id, member.id))
        data = cur.fetchall()
        if data:
            for i in data:
                if i[7] == "Never" or int(i[7]) > round(time.time()):
                    cur.execute("UPDATE guild_mod SET expires=%s, expired=%s WHERE punishment_id=%s", (round(time.time()), "yes", i[1]))
        conn.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        muted = await self.check_user_mute(member.guild, member)
        if not muted:
            return
        data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=member.guild.id)
        data = data[0]
        muted_role = member.guild.get_role(data.muted_role)
        await member.add_roles(muted_role)
        embed = nextcord.Embed(title="Member muted", description=f"I have successfully muted {member.mention} with reason: `Continued Mute`.", colour=COLOUR_GOOD)
        embed.set_footer(text=f"This means the user left the server when being muted and has now rejoined. Since the user is still muted I have re-added the **{muted_role.name}** role to them.")
        await self.log_moderation(guild=member.guild, embed=embed)

    @tasks.loop(seconds=10)
    async def unban_loop(self):
        await self.client.wait_until_ready()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM guild_mod WHERE expires < {round(time.time())} AND expired='no' AND type='ban' AND expires != 'Never'")
        data=cur.fetchall()
        if data:
            for i in data:
                if i[7] is None or i[7] == "Never":
                    pass
                else:
                    conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                    cur = conn.cursor()
                    cur.execute("UPDATE guild_mod SET expires=%s, expired=%s WHERE punishment_id=%s", (round(time.time()), "yes", i[1]))

                    try:
                        guild = self.client.get_guild(int(i[0]))
                        user = await self.client.fetch_user(int(i[2]))
                        await guild.unban(user=user, reason="Automatic Unban")
                    except Exception as e:
                        cur.execute("UPDATE guild_mod SET expires=%s, expired=%s WHERE punishment_id=%s", (round(time.time()), "yes", i[1]))
                        conn.commit()
                        cur.execute(f"SELECT * FROM guild_mod WHERE expires < {round(time.time())} AND expired='no' AND type='ban'")
                        data=cur.fetchall()
                        return
                    reason = "Automatic Unban"
                    uniqueID = False
                    conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                    cur = conn.cursor()
                    while not uniqueID:
                        punishmentId = ''.join([random.choice(ascii_letters+digits+"_") for i in range(8)])
                        cur.execute("SELECT * FROM guild_mod WHERE punishment_id = %s", punishmentId)
                        data = cur.fetchall()
                        if not data:
                            uniqueID = True
                    cur.execute("UPDATE guild_mod SET expires=%s, expired=%s WHERE punishment_id=%s", (round(time.time()), "yes", i[1]))
                    conn.commit()
                    conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                    cur = conn.cursor()
                    cur.execute(f"INSERT INTO `guild_mod` (guild_id, punishment_id, member_id, mod_id, type, reason, duration, expires, given) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (guild.id, punishmentId, user.id, 1016198853306884126, "unban", reason if reason else "Not Given", "None", "None", round(time.time())))
                    conn.commit()
                    embed = nextcord.Embed(title="Unban", description=f"""
**Member**: {user.mention} ({user.id})
**Responsible Moderator**: <@{1016198853306884126}> ({1016198853306884126})
**Reason**: `{str(reason)[:300]}`""", colour=COLOUR_NEUTRAL)
                    embed.set_footer(text=f"Punishment ID: {punishmentId}")
                    await self.log_moderation(guild=guild, embed=embed)
                    cur.execute(f"SELECT * FROM guild_mod WHERE expires < {round(time.time())} AND expired='no' AND type='ban'")
                    data=cur.fetchall()


    # ------------------------- Moderation Configuration -------------------------


    @nextcord.slash_command(name=f"moderation", description=f"Moderation base.")
    async def moderation(self, interaction:Interaction):
        pass

    @moderation.subcommand(name=f"config", description=f"Configure your servers moderation settings")
    async def moderation_config(self, interaction:Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"), ephemeral=True)
            return
        await interaction.response.defer()
        data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=interaction.guild.id)
        if not data:
            data = Bot.db.create_data("moderation_main", guild=interaction.guild.id)
        else:
            data = data[0]

        config_view = ModerationConfigView(org_user=interaction.user.id)
        embed=nextcord.Embed(title=f"Moderation Config", description=f"You can edit your moderation configuration using the buttons below.\n\nMuted Role: {f'<@&{data.muted_role}>' if not data.muted_role is None else 'None'}\nModeration Log Channel: {f'<#{data.mod_log_channel}>' if not data.mod_log_channel is None else 'None'}", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=config_view)


                
    @tasks.loop(seconds=10)
    async def unmute_loop(self):
        await self.client.wait_until_ready()
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM guild_mod WHERE expires < {round(time.time())} AND expired='no' AND type='mute' AND expires != 'Never'")
        mdata=cur.fetchall()
        print(mdata)
        if mdata:
            for i in mdata:
                if i[7] is None or i[7] == "Never":
                    pass
                else:
                    conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                    cur = conn.cursor()
                    cur.execute("UPDATE guild_mod SET expires=%s, expired=%s WHERE punishment_id=%s", (round(time.time()), "yes", i[1]))
                    conn.commit()
                    data: List[ModerationMain] = Bot.db.get_data("moderation_main", guild=int(i[0]))
                    
                    if data:
                        if data[0].muted_role is not None:
                            mutedroleid = data[0].muted_role
                            try:
                                guild = self.client.get_guild(int(i[0]))
                                user = await self.client.fetch_user(int(i[2]))
                                mutedrole = guild.get_role(int(mutedroleid))
                                member = guild.get_member(user.id)
                                await member.remove_roles(mutedrole)
                            except Exception as e:
                                pass

                            reason = "Automatic Unmute"
                            uniqueID = False
                            conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
                            cur = conn.cursor()
                            while not uniqueID:
                                punishmentId = ''.join([random.choice(ascii_letters+digits+"_") for i in range(8)])
                                cur.execute("SELECT * FROM guild_mod WHERE punishment_id = %s", punishmentId)
                                udata = cur.fetchall()
                                if not udata:
                                    uniqueID = True
                            cur.execute(f"INSERT INTO `guild_mod` (guild_id, punishment_id, member_id, mod_id, type, reason, duration, expires, given) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (guild.id, punishmentId, user.id, 1016198853306884126, "unmute", reason if reason else "Not Given", "None", "None", round(time.time())))
                            conn.commit()
                            try:
                                embed = nextcord.Embed(title="Unmute", description=f"""**Member**: {member.mention} ({member.id}) \n**Responsible Moderator**: {guild.me.mention} ({guild.me.id}) \n**Reason**: `{str(reason)[:300]}`""", colour=COLOUR_GOOD)
                                embed.set_footer(text=f"Punishment ID: {punishmentId}")
                                await self.log_moderation(guild=guild, embed=embed)
                                try:
                                    await member.send(embed=nextcord.Embed(title=f"Mute removed", description=f"Your mute in **{guild.name}** has been removed with reason: `{reason if reason else 'Not Given'}`", colour=COLOUR_GOOD))
                                except:
                                    return
                            except Exception as e:
                                pass
                        else:
                            return


def setup(client: Bot):
    client.add_cog(Moderation(client))
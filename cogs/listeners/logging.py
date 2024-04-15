import io
from typing import List
import nextcord
import datetime, time, random, os, aiohttp
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from nextcord.abc import GuildChannel
from bot.bot import Bot
from utils.utils import create_warning_embed, create_error_embed, create_success_embed, get_user_name
from constants import COLOUR_BAD, COLOUR_GOOD, COLOUR_MAIN, COLOUR_NEUTRAL, NEXTCORD_PERM_LABELS, NEXTCORD_PERM_VALUES, LOGGING_TYPES_LABELS, LOGGING_TYPES_VALUES
from views.logging_options import Toggle_Logs_View
from views.channel_select import ChannelSelect
from db_handler.schemas import *
import calendar

class Logging(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @staticmethod
    async def get_log_webhook(**query):
        data: List[LoggingMain] = Bot.db.get_data(table="logging", **query)

        if not data:
            return False
            
        return data

    @staticmethod
    async def check_log_enabled(guild, channel, type_of_pun:str):
        data: List[LoggingMain] = Bot.db.get_data(table="logging", guild_id=guild.id, channel_id=channel)
        if not data:
            return False
        return True if int(data[0].__dict__[type_of_pun]) == 1 else False

    

    # Message Logging
    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        logpanels = await self.get_log_webhook(guild_id=message.guild.id, message=1)
        if not logpanels:
            return
        
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if message.channel.id in logpanel.channel_channel_blacklist:
                    continue
                
            if not message.author.bot and not logchannel is None:
                embed=nextcord.Embed(title="Message Deleted", timestamp=message.created_at, colour=COLOUR_BAD)
                embed.add_field(name="Message Content", value=message.content[:1000])
                embed.add_field(name="Message Channel", value=message.channel.mention)
                embed.set_author(name=f"{get_user_name(message.author)}", icon_url=message.author.avatar.url if message.author.avatar else None)
                embed.set_footer(text=f"{message.author.id} | Message Created")
                if len(message.content) > 0:
                    async with aiohttp.ClientSession() as session:
                        webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                        await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)
                if len(message.attachments) > 0:
                    embeds_to_send = []
                    pic_ext = ['.jpg','.png','.jpeg']
                    for file in message.attachments:
                        for ext in pic_ext:
                            if file.filename.endswith(ext):
                                embed = nextcord.Embed(title=f"Image deleted", colour=COLOUR_BAD)
                                embed.add_field(name="Message Channel", value=message.channel.mention)
                                embed.set_author(name=f"{message.author}", icon_url=message.author.avatar.url if message.author.avatar else None)
                                embed.set_image(file)
                                embeds_to_send.append(embed)
                    if len(embeds_to_send) > 0:
                        async with aiohttp.ClientSession() as session:
                            webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                            await webhook.send(embeds=embeds_to_send, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        logpanels = await self.get_log_webhook(guild_id=before.guild.id, message=1)
        if not logpanels:
            return
        
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if before.channel.id in logpanel.channel_channel_blacklist:
                    continue

            if not before.author.bot:
                if before.content == after.content:
                    return
                embed=nextcord.Embed(title="Message Edited", description=f"[Jump to message]({after.jump_url})", timestamp=before.created_at, colour=COLOUR_NEUTRAL)
                embed.add_field(name="Original Content", value=before.content[:1000])
                embed.add_field(name="Edited Content", value=after.content[:1000])
                embed.add_field(name="Message Channel", value=after.channel.mention)
                embed.set_author(name=f"{get_user_name(after.author)}", icon_url=after.author.avatar.url if after.author.avatar else None)
                embed.set_footer(text=f"{after.author.id} | Message Created")
                async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: List[nextcord.Message]):
        msg1 = messages[0]
        logpanels = await self.get_log_webhook(guild_id=msg1.guild.id, message=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if msg1.channel.id in logpanel.channel_channel_blacklist:
                    continue
                
            embed=nextcord.Embed(title="Bulk Message Delete", description=f"``{len(messages)}`` messages have been deleted from {msg1.channel.mention} ({msg1.channel.id})", colour=COLOUR_BAD)
            embed.set_author(name=f"{msg1.guild.name}", icon_url=msg1.guild.icon.url if msg1.guild.icon else None)
            embed.set_footer(text=f"Messages Deleted")
            num = random.randint(1,5555555)
            delete_messages = ""
            for message in messages:
                    delete_messages+=(f"{message.author if message.author else None}: {message.content if message.content else None}\n")
            f = io.StringIO(delete_messages)
            f.seek(0)
            try:
                async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, file=nextcord.File(f, f"deleted-messages.txt"), avatar_url=self.client.user.avatar.url)
            except Exception as e:
                print(e)
    
    #Member Logs
    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        logpanels = await self.get_log_webhook(guild_id=member.guild.id, member=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            embed=nextcord.Embed(title="Member Joined", description=f"**:warning: :warning: :warning: YOUNG ACCOUNT WARNING - {member.created_at.strftime('%B %d %Y @ %H:%M:%S %p')}** \n\n{member.mention} ({member.id})" if (datetime.datetime.now(datetime.timezone.utc)-member.created_at).days < 3 else f"{member.mention} ({member.id})" ,timestamp=member.created_at, colour=COLOUR_GOOD)
            
            if member.avatar:
                embed.set_author(name=f"{get_user_name(member)}", icon_url=member.avatar.url if member.avatar else None)
            
            embed.set_footer(text=f"Account Created")
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        logpanels = await self.get_log_webhook(guild_id=member.guild.id, member=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link

            try:
                ban = await member.guild.fetch_ban(member)
                ban_reason = ban.reason
                embed=nextcord.Embed(title="Member Banned", description=f"{member.mention} ({member.id})\n\nReason: ``{ban_reason}``", timestamp=member.created_at, colour=COLOUR_BAD)
            except nextcord.NotFound:
                embed=nextcord.Embed(title="Member Left", description=f"{member.mention} ({member.id})", timestamp=member.created_at, colour=COLOUR_BAD)
            
            if member.avatar:
                embed.set_author(name=f"{get_user_name(member)}", icon_url=member.avatar.url if member.avatar else None)
            
            embed.set_footer(text=f"Account Created")
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)


    # @commands.Cog.listener()
    # async def on_guild_audit_log_entry_create(self, entry):
    #     if entry.action == nextcord.AuditLogAction.kick:
    #         target = await self.client.fetch_user(entry._target_id)
    #         logpanels = await self.get_log_webhook(entry.guild.id)
    #         if not logpanels:
    #             return
    #         for logpanel in logpanels:
    #             dolog = True
    #             logchannel = logpanel.webhook_link
    #             enabled = await self.check_log_enabled(entry.guild, logpanel.channel_id, "member")
    #             if not enabled:
    #                 dolog=False
    #             if dolog:
    #                 embed=nextcord.Embed(title="Member Kicked", description=f"{target.mention} ({target.id})\n\nReason: ``{entry.reason}``", timestamp=target.created_at, colour=COLOUR_BAD)
    #                 if target.avatar:
    #                     embed.set_author(name=f"{target}", icon_url=target.avatar.url if target.avatar else None)
    #                 embed.set_footer(text=f"Account Created")
    #                 logchannel = await self.get_log_webhook(entry.guild)
    #                 async with aiohttp.ClientSession() as session:
    #                     webhook = nextcord.Webhook.from_url(logchannel, session=(session))
    #                     await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: nextcord.Guild, member: nextcord.Member):
        logpanels = await self.get_log_webhook(guild_id=guild.id, member=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link

            embed=nextcord.Embed(title="Member Unbanned", description=f"{member.mention} ({member.id})", timestamp=member.created_at, colour=COLOUR_GOOD)
            embed.set_author(name=f"{get_user_name(member)}", icon_url=member.avatar.url if member.avatar else None)
            embed.set_footer(text=f"Account Created")
            async with aiohttp.ClientSession() as session:
                webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        logpanels = await self.get_log_webhook(guild_id=after.guild.id, member=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link

            embed = nextcord.Embed(title="Member Updated", description=f"{after.mention}", colour=COLOUR_NEUTRAL, timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.set_author(name=f"{get_user_name(after)}", icon_url=after.avatar.url if after.avatar else None)
            embed.set_footer(text=f"Member ID: {after.id}")

            try:
                if before.discriminator != after.discriminator:
                    embed.add_field(name="Member Discriminator Updated", value=f"{before.discriminator} ==> {after.discriminator}")

                if before.nick != after.nick:
                    embed.add_field(name="Member Nick Updated", value=f"{before.nick} ==> {after.nick}")

                if before.name != after.name:
                    embed.add_field(name="Member Name Updated", value=f"{before.name} ==> {after.name}")

                if before.communication_disabled_until != after.communication_disabled_until:
                    if before.communication_disabled_until is None:
                        endtime = calendar.timegm(after.communication_disabled_until.timetuple())
                        message = f"Member timeout added, expires <t:{endtime}:R>"
                    elif after.communication_disabled_until is None:
                        message = f"Member timeout removed"
                    else:
                        endtime = calendar.timegm(after.communication_disabled_until.timetuple())
                        message = f"Member timeout length updated, expires <t:{endtime}:R>"
                    embed.add_field(name="Member Timeout Updated", value=f"{message}")
            
            except Exception as e:
                print(e)
                pass

            try:
                if before.roles != after.roles:
                    roles = ""
                    for role in before.roles:
                        if role not in after.roles:
                            roles += f"Member was removed from the `{role.name}` role\n"
                    
                    for role in after.roles:
                        if role not in before.roles:
                            roles += f"Member was granted the `{role.name}` role\n"

                    embed.add_field(name="Member Roles Updated", value=f"{roles}")

            except:
                pass

            if len(embed.fields) > 0:
                try:
                    async with aiohttp.ClientSession() as session:
                        webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                        await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)
                except:
                    pass


    #Channel logs
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        logpanels = await self.get_log_webhook(guild_id=channel.guild.id, channel=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if channel.id in logpanel.channel_channel_blacklist:
                    continue 
            
            embed=nextcord.Embed(title="Channel Created", timestamp=channel.created_at, colour=COLOUR_GOOD)
            embed.add_field(name="Channel", value=f"{channel.mention} ({channel.id})", inline=False)
            embed.add_field(name="Category", value=f"{channel.category}")
            embed.set_author(name=channel.name)
            embed.set_footer(text="Channel Created")
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        logpanels = await self.get_log_webhook(guild_id=channel.guild.id, channel=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if channel.id in logpanel.channel_channel_blacklist:
                    continue
            
            embed=nextcord.Embed(title="Channel Deleted", timestamp=datetime.datetime.now(datetime.timezone.utc), colour=COLOUR_BAD)
            embed.add_field(name="Channel", value=f"{channel.name} ({channel.id})", inline=False)
            embed.add_field(name="Category", value=f"{channel.category}")
            embed.set_author(name=channel.name)
            embed.set_footer(text="Channel Deleted")
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        logpanels = await self.get_log_webhook(guild_id=after.guild.id, channel=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if before.id in logpanel.channel_channel_blacklist:
                    continue
                
            embed = nextcord.Embed(title="Channel Updated", description=f"{after.mention}", colour=COLOUR_NEUTRAL)
            if before.name != after.name:
                embed.add_field(name="Channel name updated", value=f"`{before.name}` ==> `{after.name}`")
            try:
                if before.topic != after.topic:
                    embed.add_field(name="Channel topic updated", value=f"`{before.topic}` ==> `{after.topic}`")
                if before.slowmode_delay != after.slowmode_delay:
                    embed.add_field(name="Channel slowmode updated", value=f"`{before.slowmode_delay} seconds` ==> `{after.slowmode_delay} seconds`")
                if before.nsfw != after.nsfw:
                    embed.add_field(name="Channel NSFW status updated", value=f"`{before.nsfw}` ==> `{after.nsfw}`")
                if before.is_news() != after.is_news():
                    embed.add_field(name="Channel news status updated", value=f"`{before.is_news()}` ==> `{after.is_news()}`")
            except:
                pass
            try:
                if before.bitrate != after.bitrate:
                    embed.add_field(name="Channel bitrate updated", value=f"`{before.bitrate:,}` ==> `{after.bitrate:,}`")
                if before.user_limit != after.user_limit:
                    embed.add_field(name="Channel user limit updated", value=f"`{before.user_limit}` ==> `{after.user_limit}`")
                if before.nsfw != after.nsfw:
                    embed.add_field(name="Channel NSFW status updated", value=f"`{before.nsfw}` ==> `{after.nsfw}`")  
            except:
                pass
            
            try:
                for role in before.changed_roles:
                    if role in after.changed_roles:
                        if list(before.overwrites_for(role).__iter__()) != list(after.overwrites_for(role).__iter__()):
                            perms = ""
                            for j in list(before.overwrites_for(role).__iter__()):
                                i = list(before.overwrites_for(role).__iter__()).index(j)
                                if j != list(after.overwrites_for(role).__iter__())[i]:
                                    k = list(after.overwrites_for(role).__iter__())[i]
                                    index = NEXTCORD_PERM_VALUES.index(j[0])
                                    rolename = NEXTCORD_PERM_LABELS[index]
                                    perms += f"**{rolename}**: {j[1]} ==> {k[1]}\n"
                            embed.add_field(name=f"{role.name}", value=f"{perms}")

                    else:
                        embed.add_field(name="Role Overwrites Removed", value=f"{role.mention} overwrites was removed")
                
                for role in after.changed_roles:
                    if role not in before.changed_roles:
                        embed.add_field(name="Role Overwrites Added", value=f"{role.mention} overwrites were added")
            except:
                pass

            if len(embed.fields) > 0:
                try:
                    async with aiohttp.ClientSession() as session:
                        webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                        await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)
                except:
                    pass

    #VC Logging
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before, after):
        if after.channel:
            checker = after
        elif before.channel:
            checker = before
        else:
            return
        logpanels = await self.get_log_webhook(guild_id=member.guild.id, voice=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if checker.channel.id in logpanel.channel_channel_blacklist:
                    continue
                
            if not before.channel and after.channel:
                embed=nextcord.Embed(title=f"Member Joined VC", description=f"{member.mention} joined {after.channel.mention}", colour=COLOUR_GOOD)
            if before.channel and after.channel:
                if before.channel == after.channel:
                    return
                embed=nextcord.Embed(title=f"Member Switched VC", description=f"{member.mention} switched VC's from {before.channel.mention} to {after.channel.mention}", colour=COLOUR_NEUTRAL)
            if not after.channel and before.channel:
                embed=nextcord.Embed(title=f"Member Left VC", description=f"{member.mention} left {before.channel.mention}", colour=COLOUR_BAD)
            embed.set_author(name=f"{get_user_name(member)}", icon_url=member.avatar.url if member.avatar else None)
            embed.set_footer(text=f"Member ID | {member.id}")
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    #Invite Logging
    @commands.Cog.listener()
    async def on_invite_create(self, invite: nextcord.Invite):
        logpanels = await self.get_log_webhook(guild_id=invite.guild.id, invite=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if invite.channel.id in logpanel.channel_channel_blacklist:
                    continue
                
            embed=nextcord.Embed(title="Invite Created", colour=COLOUR_GOOD)
            embed.add_field(name="Expires", value=f"<t:{round(time.time())+invite.max_age}>" if invite.max_age != 0 else f"Permanently")
            embed.add_field(name="Code", value=f"{invite.code}")
            embed.add_field(name="Grants Temporary Membership", value=f"{invite.temporary}")
            embed.add_field(name="Uses", value=f"{invite.max_uses}" if invite.max_uses != 0 else f"Unlimited")
            embed.add_field(name="Invite Channel", value=f"{invite.channel.mention}")
            embed.set_author(name=f"{get_user_name(invite.inviter)}", icon_url=invite.inviter.avatar.url if invite.inviter.avatar else None, url=invite.url)
            embed.set_footer(text=f"Creator ID | {invite.inviter.id}")
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite: nextcord.Invite):
        logpanels = await self.get_log_webhook(guild_id=invite.guild.id, invite=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if invite.channel.id in logpanel.channel_channel_blacklist:
                    continue
            
            embed=nextcord.Embed(title="Invite Deleted", colour=COLOUR_BAD)
            embed.add_field(name="Code", value=f"{invite.code}")
            embed.add_field(name="Invite Channel", value=f"{invite.channel.mention}")
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    # Role Logging
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: nextcord.Role):
        logpanels = await self.get_log_webhook(guild_id=role.guild.id, role=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if role.id in logpanel.role_role_blacklist:
                    continue
                
            embed=nextcord.Embed(title="Role Created", description=f"{role.mention}", colour=role.colour, timestamp=role.created_at)
            embed.set_footer(text=f"Role ID: {role.id}")
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: nextcord.Role):
        logpanels = await self.get_log_webhook(guild_id=role.guild.id, role=1)
        if not logpanels:
            return
        
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if role.id in logpanel.role_role_blacklist:
                    continue
                    
            embed=nextcord.Embed(title="Role Deleted", description=f" ", colour=role.colour, timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.set_footer(text=f"Role ID: {role.id}")
            embed.set_author(name=role.name)
            async with aiohttp.ClientSession() as session:
                    webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                    await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        logpanels = await self.get_log_webhook(guild_id=after.guild.id, role=1)
        if not logpanels:
            return
        for logpanel in logpanels:
            logchannel = logpanel.webhook_link
            if logpanel.channel_channel_blacklist:
                if after.id in logpanel.role_role_blacklist:
                    continue
                    
            embed=nextcord.Embed(title="Role Updated", description=f"{after.mention}", colour=after.colour, timestamp=datetime.datetime.now(datetime.timezone.utc))
            embed.set_author(name=after.name)
            embed.set_footer(text=f"Role ID: {after.id}")
            try:
                if before.name != after.name:
                    embed.add_field(name="Role Name Updated", value=f"{before.name} ==> {after.name}")

                if before.colour != after.colour:
                    embed.add_field(name="Role Colour Updated", value=f"{before.colour} ==> {after.colour}")
                
                if before.hoist != after.hoist:
                    embed.add_field(name="Role Hoisting Updated", value=f"{before.hoist} ==> {after.hoist}")

                if before.mentionable != after.mentionable:
                    embed.add_field(name="Role Mentionable Updated", value=f"{before.mentionable} ==> {after.mentionable}")
            
            except:
                pass
            
            try:
                if list(before.permissions.__iter__()) != list(after.permissions.__iter__()):
                    perms = ""
                    for i in list(before.permissions.__iter__()):
                        index = list(before.permissions.__iter__()).index(i)
                        j = list(after.permissions.__iter__())[index]
                        if i != j:
                            perms += f"**{i[0]}**: {i[1]} ==> {j[1]}\n"
                    embed.add_field(name="Role Permissions Updated", value=f"{perms}")
            except:
                pass


            if len(embed.fields) > 0:
                try:
                    async with aiohttp.ClientSession() as session:
                        webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                        await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)
                except:
                    pass

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        for guild in after.mutual_guilds:
            try:
                logpanels = await self.get_log_webhook(guild_id=guild.id, user=1)
                if not logpanels:
                    return
                for logpanel in logpanels:
                    logchannel = logpanel.webhook_link
                        
                    embed = nextcord.Embed(title="User Updated", description=f"{after.mention}", colour=COLOUR_NEUTRAL, timestamp=datetime.datetime.now(datetime.timezone.utc))
                    embed.set_author(name=f"{get_user_name(after)}", icon_url=after.avatar.url if after.avatar else None)
                    embed.set_footer(text=f"Member ID: {after.id}")
                    if not before.name == after.name:
                        embed.add_field(name=f"Username Updated", value=f"`{before.name}` ==> `{after.name}`")
                    if not before.discriminator == after.discriminator:
                        embed.add_field(name=f"Discriminator Updated", value=f"`{before.discriminator}` ==> `{after.discriminator}`")

                    if len(embed.fields) > 0:
                        try:
                            async with aiohttp.ClientSession() as session:
                                webhook = nextcord.Webhook.from_url(logchannel, session=(session))
                                await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)
                        except:
                            pass
            except:
                pass




    # Config Command
    @nextcord.slash_command(name="logging", description="Logging Commands")
    async def logging(self, interaction: Interaction):
        pass
    

    @logging.subcommand(name="add", description="Add a log channel")
    async def logging_config(self,
        interaction: Interaction,
        logchannel: GuildChannel = SlashOption(
            name="logchannel",
            description="The channel logs will get sent to",
            required=True,
            channel_types=[nextcord.ChannelType.text]
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer()
        data: List[LoggingMain] = Bot.db.get_data(table="logging", guild_id=interaction.guild.id, channel_id=logchannel.id)
        if data:
            await interaction.send(embed=create_error_embed(title=f"Channel already a log channel", description="This channel is already a log channel. To add a new logging config to it you must remove the old one by using `/logging remove`"))
            return
        data: List[LoggingMain] = Bot.db.get_data(table="logging", guild_id=interaction.guild.id)
        if data and len(data) >= 3:
            await interaction.send(embed=create_error_embed(title=f"Max channels reached", description="You have reachd your maximum amount of logging channels (`3`). To add new ones you must remove an old one by using `/logging remove`"))
            return
        embed=nextcord.Embed(title=f"Toggle Logs", description=f"Toggle the logs you want enabled or click the select all button to enable them all.", colour=COLOUR_MAIN)
        toggleview = Toggle_Logs_View()
        await interaction.send(embed=embed, view=toggleview, ephemeral=True)
        await toggleview.wait()
        togglevalues = toggleview.values
        if len(togglevalues) == 0:
            await interaction.edit_original_message(embed=create_error_embed(title=f"No logs selected", description=f"You must select at least one log."))
            return

        blacklist_channels = ChannelSelect(org_user=interaction.user.id)
        embed = nextcord.Embed(title="Select Blacklist Channels", description="Select any channels that you do not want to trigger logs", colour=COLOUR_MAIN)
        await interaction.edit_original_message(embed=embed, view=blacklist_channels)
        await blacklist_channels.wait()

        webhook = await logchannel.create_webhook(name="BigBot Logging", avatar=self.client.user.avatar)
        data = Bot.db.create_data(table="logging", guild_id=interaction.guild.id, message=("message" in togglevalues), role=("role" in togglevalues), member=("member" in togglevalues), voice=int("voice" in togglevalues), channel=int("channel" in togglevalues), invite=("invite" in togglevalues), user=("user" in togglevalues), webhook_link=webhook.url, channel_id=logchannel.id, channel_channel_blacklist=[i.id for i in blacklist_channels.values] if blacklist_channels.values else None)
        embed=nextcord.Embed(title="Logging Updated", colour=COLOUR_GOOD)
        embed.add_field(name="Log Channel", value=f"{logchannel.mention} ({logchannel.id})")
        enabled_logs =""
        for i in togglevalues:
            enabled_logs += str(LOGGING_TYPES_LABELS[LOGGING_TYPES_VALUES.index(i)]) + ", "
        embed.add_field(name=f"Enabled Logs", value=f"{enabled_logs[:-2]}")
        await interaction.edit_original_message(embed=embed, view=None)
        embed.set_footer(text=f"Changed by {interaction.user}")
        async with aiohttp.ClientSession() as session:
            webhook = nextcord.Webhook.from_url(webhook.url, session=(session))
            await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)

    @logging.subcommand(name="list", description="Get a list of all your log channels")
    async def logging_list(self, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer(ephemeral=True)
        data: List[LoggingMain] = Bot.db.get_data(table="logging", guild_id=interaction.guild.id)
        if not data:
            await interaction.send(embed=create_warning_embed(title=f"No log channels", description=f"You don't have any log channels. Use `/logging add` to add one."))
            return
        embed = nextcord.Embed(title=f"{interaction.guild.name} Log Channels", description=f"", colour=COLOUR_MAIN)
        for chan in data:
            embed.description = embed.description + f"\n\n<#{chan.channel_id}> ({chan.channel_id})({chan.webhook_link})"
        await interaction.send(embed=embed)

    @logging.subcommand(name="remove", description="Remove a channel from your logging list")
    async def logging_remove(self,
        interaction: Interaction,
        channel: str = SlashOption(
            name=f"channel-id",
            description=f"The channel ID of the channel you want to stop logs in (You can get this by doing /logging list)",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer()
        data: List[LoggingMain] = Bot.db.get_data(table="logging", guild_id=interaction.guild.id, channel_id=channel)
        if not data:
            await interaction.send(embed=create_warning_embed(title=f"No log channel", description=f"That channel is not currently being used for logging"))
            return
        Bot.db.delete_data(table="logging", data=data[0])
        await interaction.send(embed=create_success_embed(title=f"Channel Removed", description=f"I will stop sending logs to <#{channel}>."))

    @logging.subcommand(name="edit", description="Edit a log channel")
    async def logging_edit(self,
        interaction: Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="The logging channel you want to edit",
            required=True,
            channel_types=[nextcord.ChannelType.text]
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer()
        data: List[LoggingMain] = Bot.db.get_data(table="logging", guild_id=interaction.guild.id, channel_id=channel.id)
        if not data:
            await interaction.send(embed=create_warning_embed(title="No log channel", description="That channel is not currently being used for logging"))
            return
        
        embed=nextcord.Embed(title="Toggle Logs", description="Toggle the logs you want enabled or click the select all button to enable them all.", colour=COLOUR_MAIN)
        toggleview = Toggle_Logs_View()
        await interaction.send(embed=embed, view=toggleview, ephemeral=True)
        await toggleview.wait()
        togglevalues = toggleview.values
        if len(togglevalues) == 0:
            await interaction.edit_original_message(embed=create_error_embed(title="No logs selected", description="You must select at least one log."))
            return
        
        webhook = data[0].webhook_link
        
        blacklist_channels = ChannelSelect(org_user=interaction.user.id)
        embed = nextcord.Embed(title="Select Blacklist Channels", description="Select any channels that you do not want to trigger logs", colour=COLOUR_MAIN)
        await interaction.edit_original_message(embed=embed, view=blacklist_channels)
        await blacklist_channels.wait()

        Bot.db.delete_data(table="logging", data=data[0])
        data = Bot.db.create_data(table="logging", guild_id=interaction.guild.id, message=("message" in togglevalues), role=("role" in togglevalues), member=("member" in togglevalues), voice=int("voice" in togglevalues), channel=int("channel" in togglevalues), invite=("invite" in togglevalues), user=("user" in togglevalues), webhook_link=webhook, channel_id=channel.id, channel_channel_blacklist=[i.id for i in blacklist_channels.values] if blacklist_channels.values else None)

        embed=nextcord.Embed(title="Log channel updated", colour=COLOUR_GOOD)
        embed.add_field(name="Log Channel", value=f"{channel.mention} ({channel.id})")
        enabled_logs =""
        for i in togglevalues:
            enabled_logs += str(LOGGING_TYPES_LABELS[LOGGING_TYPES_VALUES.index(i)]) + ", "
        embed.add_field(name="Enabled Logs", value=f"{enabled_logs[:-2]}")
        await interaction.edit_original_message(embed=embed, view=None)
        embed.set_footer(text=f"Changed by {interaction.user}")

        async with aiohttp.ClientSession() as session:
            webhook = nextcord.Webhook.from_url(webhook, session=(session))
            await webhook.send(embed=embed, avatar_url=self.client.user.avatar.url)


def setup(client: Bot):
    client.add_cog(cog=Logging(client=client))

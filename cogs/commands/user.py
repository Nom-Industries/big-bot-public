import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from constants import COLOUR_MAIN
from bot import Bot
from utils import *
import time

class User(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @nextcord.slash_command(name="user", description="User commands")
    async def user_cmds(self, interaction: Interaction):
        pass

    @user_cmds.subcommand(name="id", description="Get the ID of a user")
    async def user_cmds_id(self,
        interaction: Interaction,
        member: nextcord.User = SlashOption(
            name="user",
            description="User to get ID of",
            required=True
        )):
        await interaction.send(f"**{member.id}**")

    @user_cmds.subcommand(name="info", description="Shows user info")
    async def user_cmds_info(self,
        interaction: Interaction,
        member: nextcord.User = SlashOption(
            name="user",
            description="User to get info of",
            required=False
        )):
        if not member:
            member = interaction.user
        embed=nextcord.Embed(colour=member.roles[-1].colour if len(member.roles) > 1 else None)
        embed.add_field(name="Name", value=member if not str(member.discriminator) == "0" else member.name)
        embed.add_field(name="ID", value=member.id)
        if member.nick:
            embed.add_field(name="Nickname", value=member.nick)
        embed.add_field(name=f"Mention", value=member.mention)
        embed.add_field(name="Bot", value="Yes" if member.bot else "No")
        role_list = member.roles
        if len(member.roles) > 10:
            role_list = member.roles[-11:]
        embed.add_field(name=f"Roles ({len(member.roles[1:])}) (Shows 10 max)", value=(((', '.join([i.mention for i in role_list[:0:-1]]))[0:1000]) + (" ..." if len(member.roles[1:]) > 10 else "")))
        embed.add_field(name="Joined Server", value=("<t:" + str(int(time.mktime(time.strptime(str(member.joined_at)[:19],"%Y-%m-%d %H:%M:%S")))) + "> (<t:" + str(int(time.mktime(time.strptime(str(member.joined_at)[:19],"%Y-%m-%d %H:%M:%S")))) + ":R>)"), inline=False)
        embed.add_field(name="Joined Discord", value=("<t:" + str(int(time.mktime(time.strptime(str(member.created_at)[:19],"%Y-%m-%d %H:%M:%S")))) + "> (<t:" + str(int(time.mktime(time.strptime(str(member.created_at)[:19],"%Y-%m-%d %H:%M:%S")))) + ":R>)"))
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        await interaction.send(embed=embed)

    @nextcord.user_command(name="user info")
    async def user_info_user(self, interaction, member):
        embed=nextcord.Embed(colour=member.roles[-1].colour if len(member.roles) > 1 else None)
        embed.add_field(name="Name", value=member if not str(member.discriminator) == "0" else member.name)
        embed.add_field(name="ID", value=member.id)
        if member.nick:
            embed.add_field(name="Nickname", value=member.nick)
        embed.add_field(name=f"Mention", value=member.mention)
        embed.add_field(name="Bot", value="Yes" if member.bot else "No")
        role_list = member.roles
        if len(member.roles) > 10:
            role_list = member.roles[-11:]
        embed.add_field(name=f"Roles ({len(member.roles[1:])}) (Shows 10 max)", value=(((', '.join([i.mention for i in role_list[:0:-1]]))[0:1000]) + (" ..." if len(member.roles[1:]) > 10 else "")))
        embed.add_field(name="Joined Server", value=("<t:" + str(int(time.mktime(time.strptime(str(member.joined_at)[:19],"%Y-%m-%d %H:%M:%S")))) + "> (<t:" + str(int(time.mktime(time.strptime(str(member.joined_at)[:19],"%Y-%m-%d %H:%M:%S")))) + ":R>)"), inline=False)
        embed.add_field(name="Joined Discord", value=("<t:" + str(int(time.mktime(time.strptime(str(member.created_at)[:19],"%Y-%m-%d %H:%M:%S")))) + "> (<t:" + str(int(time.mktime(time.strptime(str(member.created_at)[:19],"%Y-%m-%d %H:%M:%S")))) + ":R>)"))
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        await interaction.send(embed=embed)

    @user_cmds.subcommand("avatar", description="Shows a users avatar")
    async def user_cmds_avatar(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="member to get avatar of",
            required=False
        )):
        if not member:
            member = interaction.user
        embed=nextcord.Embed(description=f"[Avatar URL]({member.display_avatar.url})", colour=COLOUR_MAIN)
        embed.set_image(url=member.display_avatar.url)
        await interaction.send(embed=embed)



    

def setup(client):
    client.add_cog(cog=User(client=client))
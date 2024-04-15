import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from bot.bot import Bot
from constants import COLOUR_MAIN
from utils.utils import create_error_embed, create_success_embed, create_warning_embed
from views.list_options import List_Options
from db_handler.schemas import *
from typing import List

class Autoroles(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @nextcord.slash_command(name="autorole", description="Autorole commands")
    async def autorole(self, interaction: Interaction):
        pass
    
    @autorole.subcommand(name="add", description="Add autoroles")
    async def add(self, interaction: Interaction, role: nextcord.Role = SlashOption(name="role", description="Role to add (leave blank to select multiple)", required=True)):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return

        guild_data: List[GuildMain] = Bot.db.get_data(table="guild_main", guild_id=interaction.guild.id)
        if not guild_data:
            guild_data = Bot.db.create_data(table="guild_main", guild_id=interaction.guild.id)
        
        else:
            guild_data: GuildMain = guild_data[0]
        
        if guild_data.autorole_ids and len(guild_data.autorole_ids) >= 10:
            await interaction.send(embed=create_warning_embed(title="Max autoroles!", description=f"This server has the max number of autoroles (10)!"), ephemeral=True)
            return
        
        if not guild_data.autorole_ids:
            guild_data.autorole_ids = []

        if role:
            if role.id in guild_data.autorole_ids:
                await interaction.send(embed=create_warning_embed(title="Role is already an autorole!", description=f"{role.mention} is already an autorole!"), ephemeral=True)
                return
            
            else:
                guild_data.autorole_ids.append(role.id)
                Bot.db.update_data(table="guild_main", data=guild_data)
                await interaction.send(embed=create_success_embed(title="Success!", description=f"{role.mention} will now be given whenever a member joins this server!"), ephemeral=True)
                return
        
        role_options = List_Options(options=[i for i in interaction.guild.roles if i.is_assignable()], max_values=10-len(guild_data.autorole_ids), placeholder="Select role(s)")
        await interaction.send("Select the roles", view=role_options, ephemeral=True)
        await role_options.wait()

        roles_selected = [nextcord.utils.find(lambda r: r.name == i, interaction.guild.roles).id for i in role_options.values]

        await interaction.edit_original_message(content="", embed=create_success_embed(title="Success!", description="The following roles are now autoroles:\n" + '\n'.join([f'<@&{i}>' for i in list(set(guild_data.autorole_ids).symmetric_difference(set(roles_selected))) if i in roles_selected]) + "\n(Some roles you selected may not have showed up as they are already autoroles)"), view=None)

        guild_data.autorole_ids.extend([i for i in roles_selected if i not in guild_data.autorole_ids])
        Bot.db.update_data(table="guild_main", data=guild_data)

    @autorole.subcommand(name="remove", description="Remove autoroles")
    async def remove(self, interaction: Interaction, role: nextcord.Role = SlashOption(name="role", description="Role to remove (leave blank to select multiple)", required=True)):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return

        guild_data: List[GuildMain] = Bot.db.get_data(table="guild_main", guild_id=interaction.guild.id)
        if not guild_data or len(guild_data[0].autorole_ids) == 0:
            await interaction.send(embed=create_warning_embed(title="No autoroles!", description="This server does not have any autoroles!"), ephemeral=True)
            return
        
        guild_data: GuildMain = guild_data[0]

        if role:
            if role.id not in guild_data.autorole_ids:
                await interaction.send(embed=create_warning_embed(title="Role is not an autorole!", description=f"{role.mention} is not an autorole!"), ephemeral=True)
                return
            
            else:
                guild_data.autorole_ids.remove(role.id)
                Bot.db.update_data(table="guild_main", data=guild_data)
                await interaction.send(embed=create_success_embed(title="Success!", description=f"{role.mention} has been removed as an autorole!"), ephemeral=True)
                return
        
        role_options = List_Options(options=[interaction.guild.get_role(i) for i in guild_data.autorole_ids], max_values=len(guild_data.autorole_ids), placeholder="Select role(s)")
        await interaction.send("Select the roles", view=role_options, ephemeral=True)
        await role_options.wait()

        roles_selected = [nextcord.utils.find(lambda r: r.name == i, interaction.guild.roles).id for i in role_options.values]

        guild_data.autorole_ids = [i for i in guild_data.autorole_ids if i not in roles_selected]
        Bot.db.update_data(table="guild_main", data=guild_data)
        
        await interaction.edit_original_message(content="", embed=create_success_embed(title="Success!", description="The following roles are removed from autoroles:\n" + '\n'.join([f'<@&{i}>' for i in roles_selected]) + "\n(Some roles you selected may not have showed up as they are not autoroles)"), view=None)

    @autorole.subcommand(name="list", description="Show all autoroles")
    async def list_autoroles(self, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return

        guild_data: List[GuildMain] = Bot.db.get_data(table="guild_main", guild_id=interaction.guild.id)
        if not guild_data or len(guild_data[0].autorole_ids) == 0:
            await interaction.send(embed=create_warning_embed(title="No autoroles!", description="This server does not have any autoroles!"), ephemeral=True)
            return
        
        embed = nextcord.Embed(title=f"Autoroles for {interaction.guild.name}", colour=COLOUR_MAIN)
        embed.description = '\n'.join([interaction.guild.get_role(i).mention for i in guild_data[0].autorole_ids])
        await interaction.send(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        # Check whether they have this on from database
        # Get roles from database
        # database = [1022883217340108810, 1022886952367816794]
        # roles = []
        # for roleid in database:
        #     roles.append(member.guild.get_role(roleid))
        # await member.add_roles(*roles)

        guild_data: List[GuildMain] = Bot.db.get_data(table="guild_main", guild_id=member.guild.id)

        if not guild_data or not guild_data[0].autorole_ids:
            return
        
        for i in guild_data[0].autorole_ids:
            try:
                await member.add_roles(member.guild.get_role(i))

            except:
                pass

def setup(client: Bot):
    client.add_cog(cog=Autoroles(client=client))

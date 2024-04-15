from typing import List
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from bot import Bot
from utils import *
from views.confirm_deny import Confirm
from views.role_create import ColorPicker, Role_Maker, Role_Perm_View, Role_Position_Change
import requests, random
from PIL import Image
from io import BytesIO
from constants import COLOUR_MAIN, COLOUR_NEUTRAL

class Role(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="role", description="Role commands")
    async def role(self, interaction: Interaction):
        pass

    @role.subcommand(name="id", description="Gives you the ID of a role")
    async def role_id(self,
        interaction: Interaction,
        role: nextcord.Role = SlashOption(
            name="role",
            description="Role to get ID of",
            required=True
        )):
        await interaction.send(f"**{role.id}**")

    @role.subcommand(name="info", description="Shows role info")
    async def info(
        self,
        interaction: Interaction,
        role: nextcord.Role = SlashOption(
            name="role",
            description="Name of role",
            required=True
        )
    ):
        embed = nextcord.Embed(color=role.color)
        embed.add_field(name="Name", value=role.name)
        embed.add_field(name="ID", value=str(role.id))
        embed.add_field(name="Colour", value=str(role.color))
        embed.add_field(name="Members With Role", value=str(len(role.members)))
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No")
        embed.add_field(name="Can I give the role?", value="Yes" if role.is_assignable() else "No")
        embed.add_field(name="Permissions", value=', '.join([' '.join([i.capitalize() for i in i[0].split("_")]) for i in role.permissions.__iter__() if i[1]]) if any(i[1] for i in role.permissions.__iter__()) else 'None')
        embed.set_footer(text=f"Date Created: {role.created_at.strftime('%d/%m/%Y')}")

        await interaction.send(embed=embed)
        chance = random.randint(1, 10)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @role.subcommand(name="add", description="Adds role to user")
    async def add(
        self,
        interaction: Interaction,
        role: nextcord.Role = SlashOption(
            name="role",
            description="Name of role",
            required=True
        ),
        member: nextcord.Member = SlashOption(
            name="member",
            description="Name of member (Leave empty to add role to yourself)",
            required=False
        )
    ):
        if not member:
            member = interaction.user
        
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title=f"You do not have permission!", description="You lack the permission, `MANAGE_ROLES`. If you think this is an error, contact your server admins to resolve it. If the issue persists, join our discord server below!"), ephemeral=True)
            return
        
        if interaction.user.roles[-1].position <= role.position:
            await interaction.send(embed=create_error_embed(title=f"You do not have permission to add this role!", description=f"The role, {role.mention}, is higher than your highest role, {interaction.user.roles[-1].mention}. If you think this is an error, contact your server admins to resolve it. If the issue persists, join our discord server below!"), ephemeral=True)
            return

        try:
            if role in member.roles:
                await interaction.send(embed=create_warning_embed(title="User already has role!", description=f"{member.mention} already has the role {role.mention}!"), ephemeral=True)
                return

            await member.add_roles(role, reason=f"{interaction.user.name + '#' + interaction.user.discriminator} added role, {role.name}, to {member.name + '#' + member.discriminator}")
            await interaction.send(embed=create_success_embed(title="Success", description=f"Added {role.mention} to {member.mention}!"), ephemeral=True)

        except:
            await interaction.send(embed=create_error_embed(title="Error!", description=f"Sorry I lack the permissions to add the role {role.mention}. Please check to make sure my role is above this role"), ephemeral=True)

    @role.subcommand(name="remove", description="Removes role from user")
    async def remove(
        self,
        interaction: Interaction,
        role: nextcord.Role = SlashOption(
            name="role",
            description="Name of role",
            required=True
        ),
        member: nextcord.Member = SlashOption(
            name="member",
            description="Name of member (Leave empty to add role to yourself)",
            required=False
        )
    ):
        if not member:
            member = interaction.user
        
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title=f"You do not have permission!", description="You lack the permission, `MANAGE_ROLES`. If you think this is an error, contact your server admins to resolve it. If the issue persists, join our discord server below!"), ephemeral=True)
            return
        
        if interaction.user.roles[-1].position <= role.position:
            await interaction.send(embed=create_error_embed(title=f"You do not have permission to add this role!", description=f"The role, {role.mention}, is higher than your highest role, {interaction.user.roles[-1].mention}. If you think this is an error, contact your server admins to resolve it. If the issue persists, join our discord server below!"), ephemeral=True)
            return
        
        try:
            if role not in member.roles:
                await interaction.send(embed=create_warning_embed(title="User does not have role!", description=f"{member.mention} does not have the role {role.mention}!"), ephemeral=True)
                return

            await member.remove_roles(role, reason=f"{interaction.user.name + '#' + interaction.user.discriminator} removed role, {role.name}, from {member.name + '#' + member.discriminator} using the /role remove command")
            await interaction.send(embed=create_success_embed(title="Success", description=f"Removed {role.mention} from {member.mention}!"), ephemeral=True)

        except:
            await interaction.send(embed=create_error_embed(title="Error!", description=f"Sorry I lack the permissions to remove the role {role.mention}. Please check to make sure my role is above this role"), ephemeral=True)

    @role.subcommand(name="create", description="Create a role")
    async def create(self, interaction: Interaction, name: str = SlashOption(name="name", description="Name of role", required=True)):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"), ephemeral=True)
            return
        
        if not interaction.app_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title="Error!", description="Sorry I lack the permission to manage roles. Please edit my permissions to use this command"), ephemeral=True)
            return

        embed = nextcord.Embed(title="Pick permissions!", description="Click on the select menus below to pick the permissions. Once you are finished, click submit!", colour=COLOUR_MAIN)
        role_perms = Role_Perm_View()

        await interaction.send(embed=embed, view=role_perms, ephemeral=True)
        await role_perms.wait()

        img_data = requests.get("https://singlecolorimage.com/get/000000/100x100").content
        image_binary = Image.open(BytesIO(img_data))
        byte_io = BytesIO()
        image_binary.save(byte_io, "png")
        byte_io.seek(0)
        color_picker = ColorPicker()
        await interaction.edit_original_message(content="Use the buttons below to create a color or click the `Custom` button to put your own rgb or hex color code!", embed=None, file=nextcord.File(byte_io, "image.png"), view=color_picker)
        await color_picker.wait()

        permissions = nextcord.Permissions()
        for i in role_perms.values:
            permissions.__setattr__(i, True)

        roles: List[nextcord.Role] = [i for i in interaction.guild.roles if (interaction.user.roles[-1].position > i.position and i.name != "@everyone")]

        role = await interaction.guild.create_role(name=name, color=nextcord.Color.from_rgb(color_picker.r, color_picker.g, color_picker.b), permissions=permissions, reason=f"{interaction.user.name + '#' + interaction.user.discriminator} created role, {name}, using the /role create command")

        embed = nextcord.Embed(title="Role Placement", colour=COLOUR_MAIN)
        for i in range(10):
            embed.add_field(name="\u200b", value=f"{i+1}. {roles[i].mention} " + f"{'`Your role`' if roles[i] == role else ''}", inline=False)

        role_postion_change = Role_Position_Change(role, roles)
        await interaction.edit_original_message(content="", attachments=[], embed=embed, view=role_postion_change)
        await role_postion_change.wait()

        embed = nextcord.Embed(title="Hoist Role", description=f"Would you like hoist (keep above) the role, {role.mention}?", colour=COLOUR_MAIN)
        role_hoist = Confirm(interaction.user.id)
        await interaction.edit_original_message(content="", embed=embed, view=role_hoist)
        await role_hoist.wait()

        if role_hoist.value:
            await role.edit(hoist=True)

        await interaction.edit_original_message(embed=create_success_embed(title="Success!", description=f"The role, {role.mention}, has been created.\nPermissions: {', '.join([' '.join([i.capitalize() for i in i[0].split('_')]) for i in role.permissions.__iter__() if i[1]]) if any(i[1] for i in role.permissions.__iter__()) else 'None'}\nColor: ({color_picker.r}, {color_picker.g}, {color_picker.b})\nHoisted: {'Yes' if role_hoist.value else 'No'}"), view=None)

    @role.subcommand(name="edit", description="Edit a role")
    async def edit(self, interaction: Interaction, role: nextcord.Role = SlashOption(name="role", description="Name of role", required=True)):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title="Error", description="You do not have permission to run this command!"), ephemeral=True)
            return
        
        if not interaction.app_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title="Error!", description="Sorry I lack the permission to manage roles. Please edit my permissions to use this command"), ephemeral=True)
            return
        
        embed = nextcord.Embed(title="Edit Role!", description=f"Use the following buttons below to edit the role {role.mention}!", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=Role_Maker(role=role, org_inter=interaction), ephemeral=True)

        # embed = nextcord.Embed(title="Permissions!", description=f"The first two select menus will allow you to pick permissions to add and the bottom two menus will let you remove. Use them to select the correct permissions and click the submit button. Currently, {role.mention} has the following permissions: \n\n{'- ' + f'{BACKSLASH}- '.join([' '.join([i.capitalize() for i in i[0].split('_')]) for i in role.permissions.__iter__() if i[1]]) if any([i[1] for i in role.permissions.__iter__()]) else 'None'}")
        # role_perm_changes = Role_Perm_Edit(role=role, perms=[i[0] for i in role.permissions.__iter__() if i[1]])
        # await interaction.send(embed=embed, view=role_perm_changes, ephemeral=True)
        # await role_perm_changes.wait()

        # img_data = requests.get(f"https://singlecolorimage.com/get/{'%02x%02x%02x' % (role.color.r, role.color.g, role.color.b)}/100x100").content
        # image_binary = Image.open(BytesIO(img_data))
        # byte_io = BytesIO()
        # image_binary.save(byte_io, "png")
        # byte_io.seek(0)
        # color_picker = ColorPicker(r=role.color.r, g=role.color.g, b=role.color.b)
        # await interaction.edit_original_message(content="Use the buttons below to create a color or click the `Custom` button to put your own rgb or hex color code!", embed=None, file=nextcord.File(byte_io, "image.png"), view=color_picker)
        # await color_picker.wait()

        # roles: List[nextcord.Role] = [i for i in interaction.guild.roles if (interaction.user.roles[-1].position > i.position and i.name != "@everyone")]


        # role_postion_change = Role_Position_Change(role, roles)
        # await interaction.edit_original_message(content="", attachments=[], embed=embed, view=role_postion_change)
        # await role_postion_change.wait()

        # embed = nextcord.Embed(title="Hoist Role", description=f"Would you like hoist (keep above) the role, {role.mention}?")
        # role_hoist = Confirm(interaction.user.id)
        # await interaction.edit_original_message(content="", embed=embed, view=role_hoist)
        # await role_hoist.wait()


        # if role_hoist.value:
        #     await role.edit(permissions=permissions, color=nextcord.Color.from_rgb(color_picker.r, color_picker.g, color_picker.b), position=role_postion_change.role_pos+1, hoist=True, reason=f"{interaction.user.name + '#' + interaction.user.discriminator} edited role, {role.name}, using the /role edit command")
        
        # else:
        #     await role.edit(permissions=permissions, color=nextcord.Color.from_rgb(color_picker.r, color_picker.g, color_picker.b), position=role_postion_change.role_pos+1, hoist=False, reason=f"{interaction.user.name + '#' + interaction.user.discriminator} edited role, {role.name}, using the /role edit command")

        # await interaction.edit_original_message(embed=create_success_embed(title="Success!", description=f"The role, {role.mention}, has been edited.\nPermissions: {', '.join([' '.join([i.capitalize() for i in i[0].split('_')]) for i in role.permissions.__iter__() if i[1]]) if any([i[1] for i in role.permissions.__iter__()]) else 'None'}\nColor: ({color_picker.r}, {color_picker.g}, {color_picker.b})\nHoisted: {'Yes' if role_hoist.value else 'No'}"), view=None)

    @role.subcommand(name="delete", description="Remove a role")
    async def delete(self, interaction: Interaction, role: nextcord.Role = SlashOption(name="role", description="Name of role", required=True)):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title="Error", description="You do not have permission to run this command!"), ephemeral=True)
            return
        
        if not interaction.app_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title="Error!", description="Sorry I lack the permission to manage roles. Please edit my permissions to use this command"), ephemeral=True)
            return
        
        embed = nextcord.Embed(title="Confirm", description=f"Are you sure that you would like to delete the role, {role.mention}, and remove it from `{len(role.members)}` {'people' if len(role.members) - 1 != 0 else 'person'}?", colour=COLOUR_NEUTRAL)
        confirm = Confirm(interaction.user.id)
        await interaction.send(embed=embed, view=confirm, ephemeral=True)
        await confirm.wait()

        if not confirm.value:
            await interaction.edit_original_message(embed=create_warning_embed(title="Action Canceled", description=f"You have successfully canceled the action of deleting the role {role.mention}"), view=None)
            return

        try:
            rolename = role.name
            await role.delete(reason=f"{interaction.user.name + '#' + interaction.user.discriminator} deleted role, {rolename}, using the /role delete command")
            await interaction.edit_original_message(embed=create_success_embed(title="Role deleted", description=f"The role, {rolename}, has been deleted"), view=None)

        except:
            await interaction.edit_original_message(embed=create_error_embed(title="Error!", description=f"An error has occurred while deleting the role, {role.mention}. Please check to make sure I have the proper permissions"), view=None)

    @role.subcommand(name="menu", description="Create a role menu/reaction roles")
    async def menu(self, interaction: Interaction):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.send(embed=create_error_embed(title="Error", description="You do not have permission to run this command!"), ephemeral=True)
            return
        
        await interaction.send("Type in the name of the role or mention the role to add to the role menu")

        message = ""

        while message.lower() != "finish":
            await interaction.edit_original_message(content="")

def setup(client: Bot):
    client.add_cog(cog=Role(client=client))
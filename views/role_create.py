import re
from typing import List, Tuple
import nextcord
from nextcord import Interaction
from constants import COLOUR_MAIN, NEXTCORD_PERM_LABELS, NEXTCORD_PERM_VALUES, BACKSLASH
from io import BytesIO
import json
import requests
from PIL import Image

from utils.utils import create_success_embed

class Role_Name_Change(nextcord.ui.Modal):
    def __init__(self, view: nextcord.ui.View):
        super().__init__(title="Role Name Change")
        self.view = view
        self.name = nextcord.ui.TextInput(label="Enter the name for the role", placeholder="Role name", default_value=self.view.role_name)
        self.add_item(self.name)
    
    async def callback(self, interaction: Interaction):
        self.view.role_name = self.name.value
        await interaction.response.send_message(f"Name changed!\nName: {self.name.value}", ephemeral=True)

class Role_Maker(nextcord.ui.View):
    def __init__(self, role: nextcord.Role, org_inter: Interaction):
        super().__init__(timeout=120)
        self.role = role
        self.role_name = self.role.name
        self.role_perms = [i[0] for i in role.permissions.__iter__() if i[1]]
        self.color = role.color.to_rgb()
        self.role_pos = role.position
        self.role_hoist = role.hoist
        self.org_inter = org_inter
    
    @nextcord.ui.button(label="Change Name", style=nextcord.ButtonStyle.blurple)
    async def name_change(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        form = Role_Name_Change(view=self)
        await interaction.response.send_modal(modal=form)
        await form.wait()
    
    @nextcord.ui.button(label="Permissions", style=nextcord.ButtonStyle.blurple)
    async def permission_edit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Permissions!", description=f"The first two select menus will allow you to pick permissions to add and the bottom two menus will let you remove. Use them to select the correct permissions and click the submit button. Currently, {self.role.mention} has the following permissions: \n\n{'- ' + f'{BACKSLASH}- '.join([' '.join([j.capitalize() for j in i.split('_')]) for i in self.role_perms]) if len(self.role_perms) > 0 else 'None'}", colour=COLOUR_MAIN)
        role_perms = Role_Perm_Edit(role=self.role, perms=self.role_perms)
        await interaction.send(embed=embed, view=role_perms, content="", ephemeral=True)
        await role_perms.wait()

        self.role_perms = role_perms.perms

        await interaction.edit_original_message(content=f"Edited permissions!\nPermissions: {', '.join([NEXTCORD_PERM_LABELS[NEXTCORD_PERM_VALUES.index(i)] for i in role_perms.perms]) if len(role_perms.perms) > 0 else 'None'}", embed=None, view=None)
    
    @nextcord.ui.button(label="Colour", style=nextcord.ButtonStyle.blurple)
    async def color_change(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        img_data = requests.get(f"https://singlecolorimage.com/get/{'%02x%02x%02x' % (self.role.color.r, self.role.color.g, self.role.color.b)}/100x100").content
        image_binary = Image.open(BytesIO(img_data))
        byte_io = BytesIO()
        image_binary.save(byte_io, "png")
        byte_io.seek(0)
        color_picker = ColorPicker(r=self.role.color.r, g=self.role.color.g, b=self.role.color.b) if self.color else ColorPicker()
        await interaction.send(content="Use the buttons below to create a color or click the `Custom` button to put your own rgb or hex color code!", file=nextcord.File(byte_io, "image.png"), view=color_picker, ephemeral=True)
        await color_picker.wait()
        
        self.color = (color_picker.r, color_picker.g, color_picker.b)

        await interaction.edit_original_message(content=f"Edited color!\nRGB: {self.color}", view=None)

    @nextcord.ui.button(label="Placement", style=nextcord.ButtonStyle.blurple)
    async def role_change(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        roles: List[nextcord.Role] = [i for i in interaction.guild.roles if (interaction.user.roles[-1].position > i.position and i.name != "@everyone")]

        embed = nextcord.Embed(title="Role Placement", color=COLOUR_MAIN)
        for i in range(10):
            embed.add_field(name="\u200b", value=f"{i+1}. {roles[i].mention} " + f"{'`Your role`' if roles[i] == self.role else ''}", inline=False)

        role_postion_change = Role_Position_Change(self.role, roles)
        await interaction.send(content="", embed=embed, view=role_postion_change, ephemeral=True)
        await role_postion_change.wait()
        self.role_pos = role_postion_change.role_pos

        await interaction.edit_original_message(content=f"Edited role position!\nPosition: {role_postion_change.role_pos}", embed=None, view=None)
    
    @nextcord.ui.button(label="Hoist", style=nextcord.ButtonStyle.blurple)
    async def hoisting(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("Role is now hoisted" if not self.role_hoist else "Role is now not hoisted", ephemeral=True)
        self.role_hoist = not self.role_hoist

    @nextcord.ui.button(label="Finish", style=nextcord.ButtonStyle.green, row=1)
    async def complete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        permissions = nextcord.Permissions.none()
        for i in self.role_perms:
            permissions.__setattr__(i, True)
        
        await self.role.edit(name=self.role_name, permissions=permissions, color=nextcord.Color.from_rgb(self.color[0], self.color[1], self.color[2]), position=self.role_pos+1, hoist=self.role_hoist, reason=f"{interaction.user.name + '#' + interaction.user.discriminator} edited role, {self.role.name}, using the /role edit command")

        await self.org_inter.edit_original_message(embed=create_success_embed(title="Success!", description=f"The role, {self.role.mention}, has been edited.\nPermissions: {', '.join([' '.join([i.capitalize() for i in i[0].split('_')]) for i in self.role.permissions.__iter__() if i[1]]) if any(i[1] for i in self.role.permissions.__iter__()) else 'None'}\nColor: ({self.color[0]}, {self.color[1]}, {self.color[2]})\nHoisted: {'Yes' if self.role_hoist else 'No'}"), view=None, attachments=[])

class Role_Edit_Clear(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.value = None
    
    @nextcord.ui.button(label="Save", style=nextcord.ButtonStyle.green)
    async def save(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = True
        self.stop()

    @nextcord.ui.button(label="Clear", style=nextcord.ButtonStyle.red)
    async def clear(self, button: nextcord.ui.Button, interaction: Interaction):
        self.value = False
        self.stop()
    
class Role_Perm_Edit(nextcord.ui.View):
    def __init__(self, role: nextcord.Role, perms: list):
        super().__init__(timeout=120)
        self.role = role
        self.perms = perms
    
    @nextcord.ui.select(placeholder="Pick permissions", options=[nextcord.SelectOption(label=NEXTCORD_PERM_LABELS[i], value=NEXTCORD_PERM_VALUES[i]) for i in range(0, 25)], max_values=25)
    async def choose_perm_1(self, select: nextcord.ui.Select, interaction: Interaction):
        self.perms.extend(select.values)
        self.perms = [*set(self.perms)]

        await self.update_embed(interaction)
    
    @nextcord.ui.select(placeholder="Pick permissions", options=[nextcord.SelectOption(label=NEXTCORD_PERM_LABELS[i], value=NEXTCORD_PERM_VALUES[i]) for i in range(25, 41)], max_values=16)
    async def choose_perm_2(self, select: nextcord.ui.Select, interaction: Interaction):
        self.perms.extend(select.values)
        self.perms = [*set(self.perms)]

        await self.update_embed(interaction)
    
    @nextcord.ui.select(placeholder="Remove permissions", options=[nextcord.SelectOption(label=NEXTCORD_PERM_LABELS[i], value=NEXTCORD_PERM_VALUES[i]) for i in range(0, 25)], max_values=25)
    async def remove_perm_1(self, select: nextcord.ui.Select, interaction: Interaction):
        for i in select.values:
            try:
                self.perms.remove(i)

            except:
                pass

        self.perms = [*set(self.perms)]

        await self.update_embed(interaction)
    
    @nextcord.ui.select(placeholder="Remove permissions", options=[nextcord.SelectOption(label=NEXTCORD_PERM_LABELS[i], value=NEXTCORD_PERM_VALUES[i]) for i in range(25, 41)], max_values=16)
    async def remove_perm_2(self, select: nextcord.ui.Select, interaction: Interaction):
        for i in select.values:
            try:
                self.perms.remove(i)

            except:
                pass

        self.perms = [*set(self.perms)]

        await self.update_embed(interaction)
    
    @nextcord.ui.button(label="All", style=nextcord.ButtonStyle.gray)
    async def all(self, button: nextcord.ui.Button, interaction: Interaction):
        self.perms = NEXTCORD_PERM_VALUES

        await self.update_embed(interaction)
    
    @nextcord.ui.button(label="Clear", style=nextcord.ButtonStyle.gray)
    async def clear(self, button: nextcord.ui.Button, interaction: Interaction):
        self.perms = []

        await self.update_embed(interaction)
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green)
    async def submit(self, button: nextcord.ui.Button, interaction: Interaction):
        self.stop()
    
    async def update_embed(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Permissions!", description=f"The first two select menus will allow you to pick permissions to add and the bottom two menus will let you remove. Use them to select the correct permissions and click the submit button. Currently, {self.role.mention} has the following permissions: \n\n{'- ' + f'{BACKSLASH}- '.join([' '.join([j.capitalize() for j in i.split('_')]) for i in self.perms]) if len(self.perms) > 0 else 'None'}", colour=COLOUR_MAIN)
        await interaction.response.edit_message(embed=embed)

class Role_Perm_View(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.values = []
    
    @nextcord.ui.select(placeholder="Pick the permissions", options=[nextcord.SelectOption(label=NEXTCORD_PERM_LABELS[i], value=NEXTCORD_PERM_VALUES[i]) for i in range(0, 25)], max_values=25)
    async def select_perm_1(self, select: nextcord.ui.Select, interaction: Interaction):
        self.values.extend(select.values)
    
    @nextcord.ui.select(placeholder="Pick the permissions", options=[nextcord.SelectOption(label=NEXTCORD_PERM_LABELS[i], value=NEXTCORD_PERM_VALUES[i]) for i in range(25, 41)], max_values=16)
    async def select_perm_2(self, select: nextcord.ui.Select, interaction: Interaction):
        self.values.extend(select.values)

    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green)
    async def submit(self, button: nextcord.ui.Button, interaction: Interaction):
        self.values = [*set(self.values)]
        self.stop()

class ColorButton(nextcord.ui.Button):
    def __init__(self, value_button, style, type_of = 0, row = 0, label = "", emoji = "", disabled = False):
        super().__init__(style=style, label=label if label else None, emoji=emoji if emoji else None, row=row, disabled=disabled)
        self.type_of = type_of
        self.value_button = value_button

    async def callback(self, interaction: nextcord.Interaction):
        if self.style == nextcord.ButtonStyle.gray:
            form = CustomColor(self.view.r, self.value_button[0], self.view.g, self.value_button[1], self.view.b, self.value_button[2], self.view)
            await interaction.response.send_modal(modal=form)
            await form.wait()

        else:
            if self.style == nextcord.ButtonStyle.red:
                self.view.r = self.view.r + self.type_of if (self.view.r + self.type_of >= 0 and self.view.r + self.type_of <= 255) else self.view.r
                self.value_button.label = self.view.r
            
            elif self.style == nextcord.ButtonStyle.green:
                self.view.g = self.view.g + self.type_of if (self.view.g + self.type_of >= 0 and self.view.g + self.type_of <= 255) else self.view.g
                self.value_button.label = self.view.g
            
            elif self.style == nextcord.ButtonStyle.blurple:
                self.view.b = self.view.b + self.type_of if (self.view.b + self.type_of >= 0 and self.view.b + self.type_of <= 255) else self.view.b
                self.value_button.label = self.view.b

            new_color = '%02x%02x%02x' % (self.view.r, self.view.g, self.view.b)
        
            img_data = requests.get(f"https://singlecolorimage.com/get/{new_color}/100x100").content
            image_binary = Image.open(BytesIO(img_data))
            byte_io = BytesIO()
            image_binary.save(byte_io, "png")
            byte_io.seek(0)

            await interaction.edit(view=self.view)
            await interaction.edit_original_message(file=nextcord.File(byte_io, "image.png"), attachments=[])
        
class ColorPicker(nextcord.ui.View):
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        super().__init__()
        self.r = r
        self.g = g
        self.b = b

        self.display_r = nextcord.ui.Button(style=nextcord.ButtonStyle.red, label=str(self.r), row=0, disabled=True)
        self.display_g = nextcord.ui.Button(style=nextcord.ButtonStyle.green, label=str(self.g), row=1, disabled=True)
        self.display_b = nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label=str(self.b), row=2, disabled=True)
        
        self.add_item(ColorButton(type_of=-5, value_button=self.display_r, style=nextcord.ButtonStyle.red, label="<-x5"))
        self.add_item(ColorButton(type_of=-1, value_button=self.display_r, style=nextcord.ButtonStyle.red, emoji="<:left_arrow:1049429857488093275>"))
        self.add_item(self.display_r)
        self.add_item(ColorButton(type_of=1, value_button=self.display_r, style=nextcord.ButtonStyle.red, emoji="<:right_arrow:1049430086257999882>"))
        self.add_item(ColorButton(type_of=5, value_button=self.display_r, style=nextcord.ButtonStyle.red, label="5x->"))

        self.add_item(ColorButton(type_of=-5, value_button=self.display_g, style=nextcord.ButtonStyle.green, label="<-x5", row=1))
        self.add_item(ColorButton(type_of=-1, value_button=self.display_g, style=nextcord.ButtonStyle.green, emoji="<:left_arrow:1049429857488093275>", row=1))
        self.add_item(self.display_g)
        self.add_item(ColorButton(type_of=1, value_button=self.display_g, style=nextcord.ButtonStyle.green, emoji="<:right_arrow:1049430086257999882>", row=1))
        self.add_item(ColorButton(type_of=5, value_button=self.display_g, style=nextcord.ButtonStyle.green, label="5x->", row=1))

        self.add_item(ColorButton(type_of=-5, value_button=self.display_b, style=nextcord.ButtonStyle.blurple, label="<-x5", row=2))
        self.add_item(ColorButton(type_of=-1, value_button=self.display_b, style=nextcord.ButtonStyle.blurple, emoji="<:left_arrow:1049429857488093275>", row=2))
        self.add_item(self.display_b)
        self.add_item(ColorButton(type_of=1, value_button=self.display_b, style=nextcord.ButtonStyle.blurple, emoji="<:right_arrow:1049430086257999882>", row=2))
        self.add_item(ColorButton(type_of=5, value_button=self.display_b, style=nextcord.ButtonStyle.blurple, label="5x->", row=2))

        self.add_item(ColorButton(style=nextcord.ButtonStyle.gray, label="Custom", value_button=(self.display_r, self.display_g, self.display_b), row=3))

    @nextcord.ui.button(label="Done", style=nextcord.ButtonStyle.success, row=4)
    async def done_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()
  
class CustomColor(nextcord.ui.Modal):
    def __init__(self, r_val, r_button, g_val, g_button, b_val, b_button, view):
        super().__init__(title="Custom Color!")

        self.r_val = r_val
        self.r_button = r_button
        self.g_val = g_val
        self.g_button = g_button
        self.b_val = b_val
        self.b_button = b_button
        self.view = view

        self.color_name = nextcord.ui.TextInput(
            label="Color (RGB or Hex)",
            placeholder="(43, 56, 100) or #000000",
            max_length=15
        )

        self.add_item(self.color_name)
    
    async def callback(self, interaction: nextcord.Interaction):
        if self.color_name.value:
            is_rgb = False
            if ("(" in self.color_name.value or ")" in self.color_name.value or "," in self.color_name.value) and "#" in self.color_name.value:
                color_name = (0, 0, 0)
                first_color_name = "000000"

            elif "(" in self.color_name.value or ")" in self.color_name.value or "," in self.color_name.value:
                is_rgb = True
                color_name = self.color_name.value.replace("(", "").replace(")", "").replace(" ", "").split(",")
                
                if len(color_name) != 3:
                    color_name = [0, 0, 0]

                color_name = tuple(int(i) if int(i) <= 255 else 255 for i in color_name)
            
            else:
                first_color_name = ''.join(i if (i.isdigit() or i.isalpha()) else '' for i in self.color_name.value) if ((len(self.color_name.value) == 7 and "#" in self.color_name.value) or (len(self.color_name.value) == 6 and "#" not in self.color_name.value)) else '000000'
                try:
                    color_name = tuple(int(first_color_name[i:i+len(first_color_name)//3], 16) for i in range(0, len(first_color_name), len(first_color_name)//3))

                except:
                    color_name = (0, 0, 0)
                    first_color_name = "000000"

            self.view.r = int(color_name[0])
            self.r_button.label = color_name[0]
            self.view.g = int(color_name[1])
            self.g_button.label = color_name[1]
            self.view.b = int(color_name[2])
            self.b_button.label = color_name[2]

            color_name = '%02x%02x%02x' % color_name if is_rgb else first_color_name.replace("#", "")

            img_data = requests.get(f"https://singlecolorimage.com/get/{color_name}/100x100").content
            image_binary = Image.open(BytesIO(img_data))
            byte_io = BytesIO()
            image_binary.save(byte_io, "png")
            byte_io.seek(0)

            await interaction.edit(view=self.view)
            await interaction.edit_original_message(file=nextcord.File(byte_io, "image.png"), attachments=[])
                
        return False

class Role_Position_Modal(nextcord.ui.Modal):
    def __init__(self, role: nextcord.Role, view: nextcord.ui.View, data: dict, interaction: Interaction):
        super().__init__(title="Role Position")
        
        self.data = data
        self.view = view
        self.role = role
        self.inter = interaction

        self.position = nextcord.ui.TextInput(label="Position", required=True, placeholder="Ex: 1")
        self.add_item(self.position)
    
    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        value = int(re.sub("\D", "", self.position.value)) - 1

        if value // 10 in self.data and value % 10 <= len(self.data[value//10]):
            self.view.role_pos = value

            self.view.pages = {}
            
            roles = [i for i in interaction.guild.roles if (interaction.user.roles[-1].position > i.position and i.name != "@everyone" and i.name != self.role.name)]
            roles.insert(self.view.role_pos, self.role)

            for i in range(0, len(roles), 10):
                embed = nextcord.Embed(title="Role Placement", color=COLOUR_MAIN)
                for j in roles[i:i+10]:                
                    embed.add_field(name="\u200b", value=f"{roles.index(j)+1}. {j.mention} " + f"{'`Your role`' if j == self.role else ''}", inline=False)
                
                self.view.pages[i//10] = embed
            
            self.view.cur = 0

            await self.inter.edit_original_message(embed=self.view.pages[0])
            
            await interaction.send("Edited position!", ephemeral=True)
        
        else:
            await interaction.send("The position you entered is invalid", ephemeral=True)

class Role_Position_Change(nextcord.ui.View):
    def __init__(self, role: nextcord.Role, roles: List[nextcord.Role]):
        super().__init__(timeout=120)
        self.cur = 0
        self.pages = {}
        self.role = role
        self.role_pos = role.position
        for i in range(0, len(roles), 10):
            embed = nextcord.Embed(title="Role Placement", color=COLOUR_MAIN)
            for j in roles[i:i+10]:                
                embed.add_field(name="\u200b", value=f"{roles.index(j)+1}. {j.mention} " + f"{'`Your role`' if j == role else ''}", inline=False)
            
            self.pages[i//10] = embed
        
    @nextcord.ui.button(emoji="⬅️", style=nextcord.ButtonStyle.blurple)
    async def left_arrow(self, button: nextcord.ui.Button, interaction: Interaction):
        if self.cur == 0:
            return
        
        self.cur -= 1
        await interaction.response.edit_message(embed=self.pages[self.cur])
    
    @nextcord.ui.button(emoji="➡️", style=nextcord.ButtonStyle.blurple)
    async def right_arrow(self, button: nextcord.ui.Button, interaction: Interaction):
        if self.cur == len(self.pages):
            return
        
        self.cur += 1
        await interaction.response.edit_message(embed=self.pages[self.cur])
    
    @nextcord.ui.button(label="Edit Position", style=nextcord.ButtonStyle.gray)
    async def edit_pos(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.response.send_modal(modal=Role_Position_Modal(self.role, self, self.pages, interaction))
    
    @nextcord.ui.button(label="Refresh", style=nextcord.ButtonStyle.gray)
    async def refresh_embed(self, button: nextcord.ui.Button, interaction: Interaction):
        roles = [i for i in interaction.guild.roles if (interaction.user.roles[-1].position > i.position and i.name != "@everyone" and i.name != self.role.name)]
        roles.insert(self.role_pos, self.role)

        for i in range(0, len(roles), 10):
            embed = nextcord.Embed(title="Role Placement", color=COLOUR_MAIN)
            for j in roles[i:i+10]:                
                embed.add_field(name="\u200b", value=f"{roles.index(j)+1}. {j.mention} " + f"{'`Your role`' if j == self.role else ''}", inline=False)
            
            self.pages[i//10] = embed
        
        self.cur = 0

        await interaction.response.edit_message(embed=self.pages[0])

        await interaction.send("Refreshed!", ephemeral=True)
    
    @nextcord.ui.button(label="Finish", style=nextcord.ButtonStyle.green)
    async def finish(self, button: nextcord.ui.Button, interaction: Interaction):
        await interaction.guild.edit_role_positions({self.role: self.role_pos+1 if self.role_pos < 3 else self.role_pos+2})

        self.stop()

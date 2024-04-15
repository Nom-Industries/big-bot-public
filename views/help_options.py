from typing import Dict, List
import nextcord
from constants import COLOUR_MAIN, VOTELINK, HELP_COMMAND_USER, HELP_COMMAND_MOD, HELP_COMMAND_ADMIN
    
class HelpCommandSelectAll(nextcord.ui.Select):
    def __init__(self, data: Dict[str, str]):
        super().__init__(options=[nextcord.SelectOption(label=i) for i in data], placeholder="Select a category")
        self.data = data
    
    async def callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title=self.values[0], description="Key: <> = Required | [] = Optional", colour=COLOUR_MAIN)
        for i in self.data[self.values[0]]:
            embed.add_field(name=f"{i['name']}", value=f'''
            Description: {i['description']}
            Usage: `{i['usage'][:-1]}`
            ''', inline=False)
        
        if self.view.org_inter != interaction.user.id:
            await interaction.send(embed=embed, ephemeral=True, view=HelpCommandOptionsAll(org_inter=interaction, options=self.data))
            return
        
        await interaction.edit(embed=embed)

class HelpCommandOptionsAll(nextcord.ui.View):
    def __init__(self, org_inter: int, options: dict):
        super().__init__(timeout=21600)
        self.org_inter = org_inter
        self.options = options
        self.add_item(HelpCommandSelectAll(data=self.options))
        self.add_item(nextcord.ui.Button(label="Support Server", url="https://discord.gg/WjdMjUnBvJ"))
        self.add_item(nextcord.ui.Button(label="Invite", url="https://discord.com/api/oauth2/authorize?client_id=1016198853306884126&permissions=8&scope=applications.commands%20bot"))
        self.add_item(nextcord.ui.Button(label="Vote", url=VOTELINK))
    
    @nextcord.ui.button(label="Home", style=nextcord.ButtonStyle.blurple, row=1)
    async def menu(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Help", description='''
Welcome to the help command! The categories are

= General user Commands
= Moderator Commands
= Administrator Commands
= All Commands''', colour=COLOUR_MAIN)

        if interaction.user.id == self.org_inter:
            await interaction.edit(embed=embed, view=HelpCommandOptionsMenu(org_inter=interaction.user.id, options=self.options))
        else:
            await interaction.send(embed=embed, view=HelpCommandOptionsMenu(org_inter=interaction.user.id, options=self.options), ephemeral=True)
    
    @nextcord.ui.button(label="Back", style=nextcord.ButtonStyle.blurple, row=1)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="User/General Commands", description="The user command categories are:\n\n- " + "\n- ".join(list(self.options)), colour=COLOUR_MAIN)

        if interaction.user.id == self.org_inter:
            await interaction.edit(embed=embed, view=HelpCommandOptionsAll(org_inter=interaction.user.id, options=self.options))
        else:
            await interaction.send(embed=embed, view=HelpCommandOptionsAll(org_inter=interaction.user.id, options=self.options), ephemeral=True)

class HelpCommandOptionsMenu(nextcord.ui.View):
    def __init__(self, org_inter: int, options: dict):
        super().__init__(timeout=21600)
        self.org_inter = org_inter
        self.options = options
        self.add_item(nextcord.ui.Button(label="Support Server", url="https://discord.gg/WjdMjUnBvJ"))
    @nextcord.ui.button(label = "Home", style = nextcord.ButtonStyle.blurple, disabled=False)
    async def home(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Help", description='''
Welcome to the help command! The categories are

= General user Commands
= Moderator Commands
= Administrator Commands
= All Commands''', colour=COLOUR_MAIN)

        if interaction.user.id == self.org_inter:
            await interaction.edit(embed=embed, view=HelpCommandOptionsMenu(org_inter=interaction.user.id, options=self.options))
        else:
            await interaction.send(embed=embed, view=HelpCommandOptionsMenu(org_inter=interaction.user.id, options=self.options), ephemeral=True)


    @nextcord.ui.button(label = "General User Commands", style = nextcord.ButtonStyle.green, disabled=False)
    async def gen_user_commands(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="User/General Commands", description="The user command categories are:\n\n- " + "\n- ".join(list(HELP_COMMAND_USER)), colour=COLOUR_MAIN)

        if interaction.user.id == self.org_inter:
            await interaction.edit(embed=embed, view=HelpCommandOptionsAll(org_inter=interaction.user.id, options=HELP_COMMAND_USER))
        else:
            await interaction.send(embed=embed, view=HelpCommandOptionsAll(org_inter=interaction.user.id, options=HELP_COMMAND_USER), ephemeral=True)
        
    @nextcord.ui.button(label = "Moderator Commands", style = nextcord.ButtonStyle.blurple, disabled=False)
    async def mod_commands(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Moderator Commands", description="The moderator command categories are:\n\n- " + "\n- ".join(list(HELP_COMMAND_MOD)), colour=COLOUR_MAIN)

        if interaction.user.id == self.org_inter:
            await interaction.edit(embed=embed, view=HelpCommandOptionsAll(org_inter=interaction.user.id, options=HELP_COMMAND_MOD))
        else:
            await interaction.send(embed=embed, view=HelpCommandOptionsAll(org_inter=interaction.user.id, options=HELP_COMMAND_MOD), ephemeral=True)
        
    @nextcord.ui.button(label = "Administrator Commands", style = nextcord.ButtonStyle.red, disabled=False)
    async def admin_commands(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Admin Commands", description="The admin command categories are:\n\n- " + "\n- ".join(list(HELP_COMMAND_ADMIN)), colour=COLOUR_MAIN)

        if interaction.user.id == self.org_inter:
            await interaction.edit(embed=embed, view=HelpCommandOptionsAll(org_inter=interaction.user.id, options=HELP_COMMAND_ADMIN))
        else:
            await interaction.send(embed=embed, view=HelpCommandOptionsAll(org_inter=interaction.user.id, options=HELP_COMMAND_ADMIN), ephemeral=True)
import nextcord
from nextcord.ext import commands
from bot.bot import Bot
from views import HelpCommandOptionsMenu
from constants import COLOUR_MAIN, HELP_COMMAND_USER

class Help(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="help", description="help command")
    async def help(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Help", description='''
Welcome to the help command! The categories are

= General user Commands
= Moderator Commands
= Administrator Commands
= All Commands''', colour=COLOUR_MAIN)

        await interaction.send(embed=embed, view=HelpCommandOptionsMenu(org_inter=interaction.user.id, options=HELP_COMMAND_USER))

    """@nextcord.slash_command(name="faq", description=f"Get the FAQ's for the bot")
    async def faq(self, interaction:nextcord.Interaction):
        embed=nextcord.Embed(title="FAQ", description=f"Here are the FAQ categories for the bot:\n\n- Economy\n- Support Panel\n- Reaction Roles\n- Private Voice Channels\n- Sticky Messages\n- Server Statistics Channels", colour=COLOUR_MAIN)"""
        
def setup(client: Bot):
    client.add_cog(Help(client))
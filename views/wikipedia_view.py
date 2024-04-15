from asyncio import tasks
from cmath import e
from operator import itemgetter
import nextcord, random, requests, wikipediaapi, asyncio
from io import BytesIO
from nextcord.ext import commands
from bot.bot import Bot
from utils.utils import color_message, create_success_embed, create_error_embed
from views import Economy_Help_View, Confirm
from quickchart import QuickChart
from constants import COLOUR_MAIN, COOKIE, DBENDPOINT, DBPORT, DBUSER, DBPASS, DBNAME
import cooldowns, pymysql, time

class Wikipedia_Research(nextcord.ui.View):
    def __init__(self, org_user:nextcord.Member, org_link=None):
        super().__init__()
        self.org_user = org_user
        if not org_link is None:
            self.add_item(nextcord.ui.Button(label="View on wikipedia", url=org_link))


    @nextcord.ui.button(label="Search a different query", style=nextcord.ButtonStyle.blurple)
    async def wikipedia_research(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        options = WikipediaResearchModal()
        await interaction.response.send_modal(modal=options)
        await options.wait()
        query = options.newqueryanswer
        wiki_wiki = wikipediaapi.Wikipedia("en")
        page_py = wiki_wiki.page(query)
        if page_py.exists():
            embed = nextcord.Embed(title=str(page_py.title)[0:250], description=f"[Wikipedia Page]({page_py.fullurl})\n\n {page_py.summary[0:3000]}", colour=COLOUR_MAIN)
            if interaction.user.id == self.org_user.id:
                await interaction.edit(embed=embed, view=Wikipedia_Research(org_user=self.org_user, org_link=page_py.fullurl))
            else:
                await interaction.send(embed=embed, view=Wikipedia_Research(org_user=self.org_user, org_link=page_py.fullurl), ephemeral=True)
        else:
            if interaction.user.id == self.org_user.id:
                await interaction.edit(embed=create_error_embed(title="Invalid Query", description="We couldn't find that query in wikipedia."), view=Wikipedia_Research(org_user=self.org_user))
            else:
                await interaction.send(embed=create_error_embed(title="Invalid Query", description="We couldn't find that query in wikipedia."), view=Wikipedia_Research(org_user=self.org_user), ephemeral=True)




class WikipediaResearchModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Wikipedia Search", timeout=None)
        self.newquery = nextcord.ui.TextInput(
            label = "What is your query?",
            placeholder = "Example: L'Hôpital's rule",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=150,
            required=True
        )
        self.add_item(self.newquery)
        

    async def callback(self, interaction: nextcord.Interaction):
        self.newqueryanswer = self.newquery.value
        self.stop()

import nextcord
from constants import COLOUR_MAIN, COOKIE

class Economy_Help_View(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(nextcord.ui.Button(label="Support Server", url="https://discord.gg/WjdMjUnBvJ"))



    @nextcord.ui.button(label="General Info", style=nextcord.ButtonStyle.blurple)
    async def economy_help_general(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Economy Help", description=f"""Welcome to the BigBot economy.
        
**__General Economy Information__**

The currency of the economy is cookies {COOKIE}
You need to nom cookies to get more {COOKIE}'s
Every 24 hours you can get your daily cookie allowance of anywhere between 75-100

Use the buttons below to get more detailed information about commands and what you can do with the cookies you nom.""", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)


    @nextcord.ui.button(label="Commands", style=nextcord.ButtonStyle.blurple)
    async def economy_help_commands(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Economy Command List", description=f"""`/balance` - Shows you your current cookie balance
`/nom` - Noms cookies and adds them to your balance
`/daily` - Gives you your daily cookie allowance
`/pray` - Pray to the nom Gods to get cookies
`/leaderboard` - Get the global leaderboard""", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed)
from typing import List
import nextcord, requests
from io import BytesIO
from quickchart import QuickChart
from constants import COLOUR_MAIN
from db_handler.schemas import EconomyMain

class Economy_Leaderboard_Graph(nextcord.ui.View):
    def __init__(self, leaderboard: List[EconomyMain], lb_text: str):
        super().__init__()
        self.leaderboard = leaderboard
        self.lb_text = lb_text
        self.graph = None

    @nextcord.ui.button(label="Show Leaderboard Graph", style=nextcord.ButtonStyle.blurple)
    async def economy_leaderboard_graph(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):        
        if not self.graph:
            members = []
            cookies = []
            for i in range(15):
                cookies.append(str(self.leaderboard[i].balance))
                members.append(str(self.leaderboard[i].user_id))

            qc = QuickChart()
            qc.width = 500
            qc.height = 300
            qc.device_pixel_ratio = 2.0
            qc.config = {"type": "bar","data": {"labels": members,"datasets": [{"label": "Cookies","data": cookies}]}}
            imageurl: requests.Response = requests.get(str(qc.get_url())).content
            self.graph = imageurl

        await interaction.edit(file = nextcord.File(BytesIO(self.graph), "lb.png"), content=None, embed=None, view=Economy_Leaderboard_Embed(self.leaderboard, self.lb_text))

class Economy_Leaderboard_Embed(nextcord.ui.View):
    def __init__(self, leaderboard: List[EconomyMain], lb_text: str):
        super().__init__()
        self.leaderboard = leaderboard
        self.lb_text = lb_text

    @nextcord.ui.button(label="Show Leaderboard Embed", style=nextcord.ButtonStyle.blurple)
    async def economy_leaderboard_graph(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Leaderboard", description=self.lb_text, colour=COLOUR_MAIN)
        
        await interaction.edit(embed=embed, view=Economy_Leaderboard_Graph(self.leaderboard, self.lb_text), attachments=[])
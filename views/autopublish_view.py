import nextcord
from utils import *
from typing import List, Union



class messageselect(nextcord.ui.Select):
      def __init__(self, selectoptions: List[nextcord.SelectOption]):
        super().__init__(placeholder="Select a message", min_values=1, max_values=1, options=selectoptions, disabled=False)

      async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=False)
        self.view.values.extend(self.values)
        self.view.stop()

class messageselectview(nextcord.ui.View):
      def __init__(self,  selectoptions: List[nextcord.SelectOption], userid):
        super().__init__(timeout=30)
        self.add_item(messageselect(selectoptions=selectoptions))
        self.userid = userid
        self.values = []

      async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self.userid == interaction.user.id
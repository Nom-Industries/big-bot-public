import nextcord
from typing import List, Union

class List_Select(nextcord.ui.Select):
    def __init__(self, options: List[Union[nextcord.Role, nextcord.TextChannel, nextcord.VoiceChannel]], placeholder: str = "Select an option", max_values: int = 1):
        super().__init__(options=[nextcord.SelectOption(label=i.name, description=i.id, value=i.id) for i in options], placeholder=placeholder, max_values=max_values)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)

class List_Options(nextcord.ui.View):
    def __init__(self, options: List[Union[nextcord.Role, nextcord.TextChannel, nextcord.VoiceChannel]], placeholder: str = "Select an option", max_values: int = 1):
        super().__init__(timeout=120)
        self.values = []
        for i in range(0, len(options), 25):
            self.add_item(List_Select(options=options[i:i+25], placeholder=placeholder, max_values=max_values))
    
    @nextcord.ui.button(label="Complete", style=nextcord.ButtonStyle.green)
    async def complete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()
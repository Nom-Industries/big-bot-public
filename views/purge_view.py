import nextcord

class PurgeView(nextcord.ui.View):

    def __init__(self):
        super().__init__()
        self.add_item(nextcord.ui.Button(label=f"This message will be deleted in 10 seconds", style = nextcord.ButtonStyle.grey, disabled=True))
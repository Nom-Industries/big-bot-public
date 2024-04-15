import nextcord

class WorkTriviaButton(nextcord.ui.Button):
    def __init__(self, label: str, style, disabled):
        super().__init__(label=label, style=style, disabled=disabled)
    
    async def callback(self, interaction: nextcord.Interaction):
        self.view.value = self.label
        self.view.stop()

class WorkTriviaView(nextcord.ui.View):
    def __init__(self, org_user: int, answers, selected_answer = None, correct = None):
        super().__init__(timeout=60)
        self.value = None
        self.org_user = org_user

        for i in range(len(answers)):
            if selected_answer:
                if answers[i] == correct:
                    style = nextcord.ButtonStyle.green
                            
                else:
                    style = nextcord.ButtonStyle.grey
            
            else:
                style = nextcord.ButtonStyle.blurple

            self.add_item(WorkTriviaButton(label=str(i+1), style=style, disabled=False if style == nextcord.ButtonStyle.blurple else True))

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.value = None
        self.stop()
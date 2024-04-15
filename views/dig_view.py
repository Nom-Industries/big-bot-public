import nextcord

class DigSpade(nextcord.ui.View):
    def __init__(self, org_user: int, drill_disable:bool=True):
        super().__init__(timeout=60)
        self.value = "Not Given"
        self.org_user = org_user
        self.drill_disable = drill_disable

    @nextcord.ui.button(label = "Indium Mine", style = nextcord.ButtonStyle.green, disabled=False, row=1)
    async def indium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Indium"
        self.stop()
    @nextcord.ui.button(label = "Silver Mine", style = nextcord.ButtonStyle.green, disabled=False, row=1)
    async def silver(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Silver"
        self.stop()
    @nextcord.ui.button(label = "Osmium Mine", style = nextcord.ButtonStyle.green, disabled=False, row=1)
    async def osmium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Osmium"
        self.stop()
    @nextcord.ui.button(label = "Platinum Mine", style = nextcord.ButtonStyle.green, disabled=False, row=1)
    async def platinum(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Platinum"
        self.stop()
    @nextcord.ui.button(label = "Gold Mine", style = nextcord.ButtonStyle.green, disabled=True, row=2)
    async def gold(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Gold"
        self.stop()
    @nextcord.ui.button(label = "Rhenium Mine", style = nextcord.ButtonStyle.green, disabled=True, row=2)
    async def rhenium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Rhenium"
        self.stop()
    @nextcord.ui.button(label = "Palladium Mine", style = nextcord.ButtonStyle.green, disabled=True, row=2)
    async def palladium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Palladium"
        self.stop()
    @nextcord.ui.button(label = "Rhodium Mine", style = nextcord.ButtonStyle.green, disabled=True, row=2)
    async def rhodium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Rhodium"
        self.stop()

    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.value="Not Given"
        self.stop()

class DigDrill(nextcord.ui.View):
    def __init__(self, org_user: int, drill_disable:bool=True):
        super().__init__(timeout=60)
        self.value = "Not Given"
        self.org_user = org_user
        self.drill_disable = drill_disable

    @nextcord.ui.button(label = "Indium Mine", style = nextcord.ButtonStyle.green, disabled=False, row=1)
    async def indium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Indium"
        self.stop()
    @nextcord.ui.button(label = "Silver Mine", style = nextcord.ButtonStyle.green, disabled=False, row=1)
    async def silver(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Silver"
        self.stop()
    @nextcord.ui.button(label = "Osmium Mine", style = nextcord.ButtonStyle.green, disabled=False, row=1)
    async def osmium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Osmium"
        self.stop()
    @nextcord.ui.button(label = "Platinum Mine", style = nextcord.ButtonStyle.green, disabled=False, row=1)
    async def platinum(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Platinum"
        self.stop()
    @nextcord.ui.button(label = "Gold Mine", style = nextcord.ButtonStyle.green, disabled=False, row=2)
    async def gold(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Gold"
        self.stop()
    @nextcord.ui.button(label = "Rhenium Mine", style = nextcord.ButtonStyle.green, disabled=False, row=2)
    async def rhenium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Rhenium"
        self.stop()
    @nextcord.ui.button(label = "Palladium Mine", style = nextcord.ButtonStyle.green, disabled=False, row=2)
    async def palladium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Palladium"
        self.stop()
    @nextcord.ui.button(label = "Rhodium Mine", style = nextcord.ButtonStyle.green, disabled=False, row=2)
    async def rhodium(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "Rhodium"
        self.stop()

    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.value="Not Given"
        self.stop()
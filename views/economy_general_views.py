import nextcord


class EconomyPurchaseAmount(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Amount to buy", timeout=None)
        self.amounttobuy = nextcord.ui.TextInput(
            label = "How many items do you want to buy?",
            placeholder = "Example: 7",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=5,
            required=True
        )
        self.add_item(self.amounttobuy)
        

    async def callback(self, interaction: nextcord.Interaction):
        self.amount = self.amounttobuy.value
        self.stop()
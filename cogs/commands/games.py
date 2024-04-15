import nextcord, random, asyncio
from nextcord import SlashOption
from nextcord.ext import commands
from constants import COLOUR_MAIN, RPS_CHOICES
from bot.bot import Bot
from views.rps_choice import Rock_Paper_Scissors_Choice
from views.tictactoe import TicTacToeView

class Games(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="coinflip", description="Do a coin flip")
    async def coin_flip(self, interaction: nextcord.Interaction):    
        msg = await interaction.send(f"Your coin landed on")
        await asyncio.sleep(0.185)
        for i in range(3):
            await msg.edit("Your coin landed on " + ''.join('.' for _ in range(i+1)))
            await asyncio.sleep(0.185)         
        choice = random.choice(["Heads", "Tails"])
        await msg.edit(f"Your coin landed on ... ||**{choice}**||")
    
    @nextcord.slash_command(name="rps", description="Play rock paper scissors")
    async def rps(self,
        interaction: nextcord.Interaction,
        choice: str = SlashOption(
            name="choice",
            description="Your choice",
            choices=RPS_CHOICES,
            required=False
        )):
        bot_choice = random.choice(RPS_CHOICES)
        msg = False
        if not choice:
            rps_choice = Rock_Paper_Scissors_Choice()

            msg = await interaction.send("Make your choice:", view=rps_choice, ephemeral=True)
            await rps_choice.wait()
            choice = rps_choice.values[0]
        if choice == bot_choice:
            if msg:
                await msg.edit("You drew.", view=None)
            else:
                await interaction.send("You drew.", ephemeral=True)
        elif (choice == "Rock" and bot_choice == "Scissors") or (choice == "Paper" and bot_choice == "Rock") or (choice == "Scissors" and bot_choice == "Paper"):
            if msg:
                await msg.edit(f"You won! The bot chose {bot_choice}", view=None)
            else:
                await interaction.send(f"You won! The bot chose {bot_choice}", ephemeral=True)
        else:
            if msg:
                await msg.edit(f"You lost! The bot chose {bot_choice}", view=None)
            else:
                await interaction.send(f"You lost! The bot chose {bot_choice}", ephemeral=True)

    @nextcord.slash_command(name="tictactoe", description="Play tictactoe against an opponent")
    async def tictactoe(self,
        interaction: nextcord.Interaction,
        opponent: nextcord.User = SlashOption(
            name="opponent",
            description="Who will be your opponent?",
            required=True
        )):
        if opponent.id == interaction.user.id:
            await interaction.send("You can't play against yourself", ephemeral=True)
            return
        embed=nextcord.Embed(title="Tic Tac Toe", description=f"{interaction.user.mention} starts!\n\nX = {interaction.user.mention}\nO ={opponent.mention}", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=TicTacToeView(interaction.user.id, opponent.id))

    """@nextcord.slash_command(name="hangman", description="Play hangman against an opponent")
    async def hangman(self,
        interaction: nextcord.Interaction,
        opponent: nextcord.User = SlashOption(
            name="opponent",
            description="Who will be your opponent?",
            required=True
        )):
        pass"""

    

def setup(client: Bot):
    client.add_cog(Games(client))

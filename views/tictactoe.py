from typing import List
import nextcord
from nextcord import Interaction
import random
from constants import NEXTCORD_PERM_LABELS, NEXTCORD_PERM_VALUES, BACKSLASH, RPS_CHOICES, COLOUR_MAIN, COLOUR_NEUTRAL, COLOUR_GOOD


class TicTacToeView(nextcord.ui.View):
    def __init__(self, user1id, user2id):
        super().__init__()
        self.user1id = user1id
        self.user2id = user2id
        self.current_user = user1id
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(row=x, x=x, y=y))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.user1id, self.board
            elif value == -3:
                return self.user2id, self.board
        for line in range(3):
            value = self.board[0][line] + \
                self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.user1id, self.board
            elif value == -3:
                return self.user2id, self.board
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.user1id, self.board
        elif diag == -3:
            return self.user2id, self.board
        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.user1id, self.board
        elif diag == -3:
            return self.user2id, self.board
        if all(i != 0 for row in self.board for i in row):
            return "Tie", None
        return None, None


class TicTacToeButton(nextcord.ui.Button):
    def __init__(self, row, x, y):
        super().__init__(label="\u200b", style=nextcord.ButtonStyle.grey, disabled=False, row=row)
        self.x = x
        self.y = y

    async def callback(self, interaction: nextcord.Interaction):
        if interaction.user.id == self.view.user1id and interaction.user.id == self.view.current_user:
            self.label = "X"
            self.disabled = True
            self.style = nextcord.ButtonStyle.green
            await interaction.message.edit(view=self.view)
            self.view.current_user = self.view.user2id
            self.view.board[self.x][self.y] = 1
            content = f"It is now <@{self.view.user2id}>'s go"
        elif interaction.user.id == self.view.user2id and interaction.user.id == self.view.current_user:
            self.label = "O"
            self.disabled = True
            self.style = nextcord.ButtonStyle.red
            await interaction.message.edit(view=self.view)
            self.view.current_user = self.view.user1id
            self.view.board[self.x][self.y] = -1
            content = f"It is now <@{self.view.user1id}>'s go"
        else:
            return
        winner, disable = self.view.check_board_winner()
        if winner is not None:
            if winner == self.view.user1id:
                winnermem = interaction.guild.get_member(self.view.user1id)
                embed = nextcord.Embed(title=f"{winnermem} has won!", colour=COLOUR_GOOD)
                embed.set_thumbnail(url=winnermem.avatar.url if winnermem.avatar else None)
            elif winner == self.view.user2id:
                winnermem = interaction.guild.get_member(self.view.user2id)
                embed = nextcord.Embed(title=f"{winnermem} has won!", colour=COLOUR_GOOD)
                embed.set_thumbnail(url=winnermem.avatar.url if winnermem.avatar else None)
            else:
                embed = nextcord.Embed(title=f"Its a tie!", colour=COLOUR_NEUTRAL)
            for child in self.view.children:
                child.disabled = True
            if winner in (self.view.user1id, self.view.user2id):
                diag = disable[0][0] + disable[1][1] + disable[2][2]
                if diag in (3, -3):
                    self.view.children[0].disabled = False
                    self.view.children[4].disabled = False
                    self.view.children[8].disabled = False
                diag = disable[0][2] + disable[1][1] + disable[2][0]
                if diag in (3, -3):
                    self.view.children[2].disabled = False
                    self.view.children[4].disabled = False
                    self.view.children[6].disabled = False
                if (disable[0][0] + disable[0][1] + disable[0][2]) == 3 or (disable[0][0] + disable[0][1] + disable[0][2]) == -3:
                    self.view.children[0].disabled = False
                    self.view.children[1].disabled = False
                    self.view.children[2].disabled = False
                if (disable[1][0] + disable[1][1] + disable[1][2]) == 3 or (disable[1][0] + disable[1][1] + disable[1][2]) == -3:
                    self.view.children[3].disabled = False
                    self.view.children[4].disabled = False
                    self.view.children[5].disabled = False
                if (disable[2][0] + disable[2][1] + disable[2][2]) == 3 or (disable[2][0] + disable[2][1] + disable[2][2]) == -3:
                    self.view.children[6].disabled = False
                    self.view.children[7].disabled = False
                    self.view.children[8].disabled = False
                if (disable[0][0] + disable[1][0] + disable[2][0]) == 3 or (disable[0][0] + disable[1][0] + disable[2][0]) == -3:
                    self.view.children[0].disabled = False
                    self.view.children[3].disabled = False
                    self.view.children[6].disabled = False
                if (disable[0][1] + disable[1][1] + disable[2][1]) == 3 or (disable[0][1] + disable[1][1] + disable[2][1]) == -3:
                    self.view.children[1].disabled = False
                    self.view.children[4].disabled = False
                    self.view.children[7].disabled = False
                if (disable[0][2] + disable[1][2] + disable[2][2]) == 3 or (disable[0][2] + disable[1][2] + disable[2][2]) == -3:
                    self.view.children[2].disabled = False
                    self.view.children[5].disabled = False
                    self.view.children[8].disabled = False
            self.view.stop()
            await interaction.message.edit(embed=embed, view=self.view)
            chance = random.randint(1, 10)
            if chance == 1:
                await interaction.message.edit(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
        else:
            embed = nextcord.Embed(title="Tic Tac Toe", description=f"{content}\n\nX = <@{self.view.user1id}>\nO =<@{self.view.user2id}>",colour=COLOUR_MAIN if not content == "It's a tie!" else COLOUR_NEUTRAL)
            await interaction.message.edit(embed=embed, view=self.view)

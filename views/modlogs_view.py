from typing import List, Tuple
import nextcord
from nextcord import Interaction


class Modlogs_Information_View(nextcord.ui.View):
    def __init__(self, pages, neg_pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.neg_pages = neg_pages
        self.cur = 1
        self.show_neg = True
        
    @nextcord.ui.button(emoji="⬅️", style=nextcord.ButtonStyle.blurple, disabled=True)
    async def left_arrow(self, button: nextcord.ui.Button, interaction: Interaction):
        if not self.show_neg:
            self.cur -= 1
            if self.cur == 1:
                self.left_arrow.disabled = True
            if not self.cur == len(self.pages):
                self.right_arrow.disabled = False

            
            await interaction.response.edit_message(embed=self.pages[self.cur-1], view=self)
        else:
            self.cur -= 1
            if self.cur == 1:
                self.left_arrow.disabled = True
            if not self.cur == len(self.neg_pages):
                self.right_arrow.disabled = False

            
            await interaction.response.edit_message(embed=self.neg_pages[self.cur-1], view=self)

    @nextcord.ui.button(label="Show positive modlogs", style=nextcord.ButtonStyle.grey, disabled=False)
    async def show_positive_modlogs(self, button: nextcord.ui.Button, interaction: Interaction):
        self.cur = 1
        if self.show_neg:
            self.show_neg = False
            button.label = "Hide positive modlogs"
            self.left_arrow.disabled = True
            self.right_arrow.disabled = True if len(self.pages) <=1 else False
            await interaction.response.edit_message(embed=self.pages[0], view=self)
        else:
            self.show_neg = True
            button.label = "Show positive modlogs"
            self.left_arrow.disabled = True
            self.right_arrow.disabled = True if len(self.neg_pages) <=1 else False
            await interaction.response.edit_message(embed=self.neg_pages[0], view=self)
    
    @nextcord.ui.button(emoji="➡️", style=nextcord.ButtonStyle.blurple)
    async def right_arrow(self, button: nextcord.ui.Button, interaction: Interaction):
        if not self.show_neg:
            self.cur += 1
            if self.cur == len(self.pages):
                self.right_arrow.disabled = True
            else:
                self.right_arrow.disabled = False
            if not self.cur == 1:
                self.left_arrow.disabled = False
            
            await interaction.response.edit_message(embed=self.pages[self.cur-1], view=self)
        else:
            self.cur += 1
            if self.cur == len(self.neg_pages):
                self.right_arrow.disabled = True
            else:
                self.right_arrow.disabled = False
            if not self.cur == 1:
                self.left_arrow.disabled = False
            
            await interaction.response.edit_message(embed=self.neg_pages[self.cur-1], view=self)


class Modlogs_Information_View_Non_Pagified(nextcord.ui.View):
    def __init__(self, pages, neg_pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.neg_pages = neg_pages
        self.show_neg = True

    @nextcord.ui.button(label="Show positive modlogs", style=nextcord.ButtonStyle.grey, disabled=False)
    async def show_positive_modlogs(self, button: nextcord.ui.Button, interaction: Interaction):
        if self.show_neg:
            self.show_neg = False
            button.label = "Hide positive modlogs"
            await interaction.response.edit_message(embed=self.pages[0], view=self)
        else:
            self.show_neg = True
            button.label = "Show positive modlogs"
            await interaction.response.edit_message(embed=self.neg_pages[0], view=self)
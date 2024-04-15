from typing import List
import nextcord
from nextcord import Interaction
from constants import COLOUR_GOOD, COLOUR_BAD
import time
from utils import create_error_embed

class BanDurationChoice(nextcord.ui.View):
    def __init__(self, org_user: nextcord.Member, member, reason, punishmentId):
        super().__init__(timeout=30)
        self.org_user = org_user
        self.member = member
        self.reason = reason if reason else "Not Given"
        self.duration = 0
        self.add_item(BanDurationButton(member=self.member, reason=self.reason, durationinput="60 seconds", punishmentId=punishmentId))
        self.add_item(BanDurationButton(member=self.member, reason=self.reason, durationinput="10 minutes", punishmentId=punishmentId))
        self.add_item(BanDurationButton(member=self.member, reason=self.reason, durationinput="1 hour", punishmentId=punishmentId))
        self.add_item(BanDurationButton(member=self.member, reason=self.reason, durationinput="1 day", punishmentId=punishmentId))
        self.add_item(BanDurationButton(member=self.member, reason=self.reason, durationinput="1 week", punishmentId=punishmentId))
        self.add_item(BanDurationButton(member=self.member, reason=self.reason, durationinput="2 weeks", punishmentId=punishmentId))
        self.add_item(BanDurationButton(member=self.member, reason=self.reason, durationinput="1 month", punishmentId=punishmentId))

    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.org_user != interaction.user.id:
            await interaction.send("You cannot click this button!", ephemeral=True)
            return False
        
        return True

class BanDurationButton(nextcord.ui.Button):
    def __init__(self, member: int, reason: str, durationinput: str, punishmentId):
        super().__init__(style=nextcord.ButtonStyle.blurple, label=durationinput)
        self.member = member
        self.reason = reason
        self.punishmentId = punishmentId
    
    async def callback(self, interaction: Interaction):
        if "Permanent" in self.label:
            duration = "Permanent"
        elif "second" in self.label.split(" ")[1]:
            duration=int(int(self.label.split(" ")[0]))

        elif "minute" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*60)

        elif "hour" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*3600)

        elif "day" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*86400)
        
        elif "week" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*604800)
        elif "month" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*604800)
        member = interaction.guild.get_member(self.member)
        try:
            try:
                if not str(duration) == "Permanent":
                    embed=nextcord.Embed(title="Ban", description=f"You have been banned in **{interaction.guild.name}** till <t:{round(time.time())+duration}> with reason: **{str(self.reason)[:1500]}**", colour=COLOUR_BAD)
                else:
                    embed=nextcord.Embed(title="Ban", description=f"You have been banned in **{interaction.guild.name}** permanently with reason: **{str(self.reason)[:1500]}**", colour=COLOUR_BAD)
            
                await member.send(embed=embed)
            except Exception as e:
                pass
            await member.ban(reason=self.reason)
            if not self.label == "Permanent":
                embed=nextcord.Embed(title="Ban", description=f"I have successfully banned {member.mention} for `{self.label}` with reason `{self.reason}`", colour=COLOUR_GOOD)
            else:
                embed=nextcord.Embed(title="Ban", description=f"I have successfully banned {member.mention} `permanently` with reason `{self.reason}`", colour=COLOUR_GOOD)
            embed.set_footer(text=f"Punishment ID: {self.punishmentId}")
            await interaction.edit(embed=embed, view=None)
            if not self.label == "Permanent":
                self.view.duration = int(duration)
            else:
                self.view.duration = "Permanent"
            self.view.stop()
        except Exception as e:
            print(e)
            await interaction.edit(embed=create_error_embed(title="Missing Permissions", description=f"I don't have permissions to ban **{member}**."), view=None)
            return
    
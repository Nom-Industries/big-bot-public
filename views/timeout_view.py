from typing import List
import nextcord
from nextcord import Interaction
from constants import COLOUR_GOOD, NEXTCORD_PERM_LABELS, NEXTCORD_PERM_VALUES, BACKSLASH, RPS_CHOICES
from io import BytesIO
import json
import requests, datetime
from utils import create_error_embed
from PIL import Image

class TimeoutDurationChoice(nextcord.ui.View):
    def __init__(self, org_user: nextcord.Member, member, reason, punishmentId):
        super().__init__(timeout=30)
        self.org_user = org_user
        self.member = member
        self.reason = reason if reason else "Not Given"
        self.duration = 0
        self.add_item(TimeoutDurationButton(member=self.member, reason=self.reason, durationinput="5 seconds", punishmentId=punishmentId))
        self.add_item(TimeoutDurationButton(member=self.member, reason=self.reason, durationinput="60 seconds", punishmentId=punishmentId))
        self.add_item(TimeoutDurationButton(member=self.member, reason=self.reason, durationinput="5 minutes", punishmentId=punishmentId))
        self.add_item(TimeoutDurationButton(member=self.member, reason=self.reason, durationinput="10 minutes", punishmentId=punishmentId))
        self.add_item(TimeoutDurationButton(member=self.member, reason=self.reason, durationinput="1 hour", punishmentId=punishmentId))
        self.add_item(TimeoutDurationButton(member=self.member, reason=self.reason, durationinput="1 day", punishmentId=punishmentId))
        self.add_item(TimeoutDurationButton(member=self.member, reason=self.reason, durationinput="1 week", punishmentId=punishmentId))
        self.add_item(TimeoutDurationButton(member=self.member, reason=self.reason, durationinput="2 weeks", punishmentId=punishmentId))
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.org_user != interaction.user.id:
            await interaction.send("You cannot click this button!", ephemeral=True)
            return False
        
        return True

class TimeoutDurationButton(nextcord.ui.Button):
    def __init__(self, member: int, reason: str, durationinput: str, punishmentId):
        super().__init__(style=nextcord.ButtonStyle.blurple, label=durationinput)
        self.member = member
        self.reason = reason
        self.punishmentId = punishmentId
    
    async def callback(self, interaction: Interaction):
        if "second" in self.label.split(" ")[1]:
            duration=int(int(self.label.split(" ")[0]))

        elif "minute" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*60)

        elif "hour" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*3600)

        elif "day" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*86400)
        
        elif "week" in self.label.split(" ")[1]:
            duration = int(int(self.label.split(" ")[0])*604800)
        member = interaction.guild.get_member(self.member)
        try:
            await member.timeout(timeout=(nextcord.utils.utcnow()+datetime.timedelta(seconds=int(duration))), reason=self.reason)
            embed=nextcord.Embed(title="Timeout", description=f"I have successfully timedout {member.mention} for `{self.label}` with reason `{self.reason}`", colour=COLOUR_GOOD)
            embed.set_footer(text=f"Punishment ID: {self.punishmentId}")
            await interaction.edit(embed=embed, view=None)
            self.view.duration = int(duration)
            self.view.stop()
        except:
            await interaction.edit(embed=create_error_embed(title="Missing Permissions", description=f"I don't have permissions to timeout **{member.name}**."), view=None)
            return
    
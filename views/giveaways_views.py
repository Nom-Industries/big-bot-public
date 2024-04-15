import nextcord
from utils import *
from typing import List, Union
from views import Confirm
from db_handler.schemas import *
from bot.bot import Bot
from constants import COLOUR_BAD, COLOUR_NEUTRAL, COLOUR_GOOD, COLOUR_MAIN

class Giveaway_List_Select(nextcord.ui.RoleSelect):
    def __init__(self):
        super().__init__(custom_id="test", placeholder="Select some roles", min_values=1, max_values=10)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)
        self.view.stop()

class Giveaway_List_Options(nextcord.ui.View):
    def __init__(self, org_user:int):
        super().__init__(timeout=300)
        self.add_item(Giveaway_List_Select())
        self.values = []
        self.choice = None
        self.org_user = org_user

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True
    

class Bypass_Giveaway_List_Select(nextcord.ui.RoleSelect):
    def __init__(self):
        super().__init__(custom_id="test1", placeholder="Select some roles", min_values=1, max_values=1)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)
        self.view.stop()

class Bypass_Giveaway_List_Options(nextcord.ui.View):
    def __init__(self, org_user:int):
        super().__init__(timeout=300)
        self.add_item(Bypass_Giveaway_List_Select())
        self.values = []
        self.choice = None
        self.org_user = org_user

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True
    
    
class Giveaway_Boost_Roles_Boosts_Button(nextcord.ui.Button):
    def __init__(self, label: str, style, disabled):
        super().__init__(label=label, style=style, disabled=disabled)
    
    async def callback(self, interaction: nextcord.Interaction):
        self.view.value = self.label
        self.view.stop()

class Giveaway_Boost_Roles_Boosts(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=300)
        self.value = None
        self.org_user = org_user
        for i in range(15):
            self.add_item(Giveaway_Boost_Roles_Boosts_Button(label=str(i+2), style=nextcord.ButtonStyle.blurple, disabled=False))

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.value = None
        self.stop()

class MinMessagesView(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Minimum messages", timeout=None)

        self.min_messages = nextcord.ui.TextInput(
                label = "What is the minimum message requirement?",
                placeholder = "Max: 99999",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=5,
                required=True
            )
        self.add_item(self.min_messages)

    async def callback(self, interaction: nextcord.Interaction):
        self.min_messages = self.min_messages.value
        self.stop()

class RequirementConfirm(nextcord.ui.View):
    def __init__(self, org_user: int=0):
        super().__init__(timeout=600)
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Yes", emoji = "<:Check:779247977721495573>", style = nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        min_messages = MinMessagesView()
        await interaction.response.send_modal(min_messages)
        await min_messages.wait()
        self.value = min_messages.min_messages
        self.stop()

        self.clear_items()
    
    @nextcord.ui.button(label = "No", emoji = "<:Cross:779247977843523594>", style = nextcord.ButtonStyle.red)
    async def deny(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 0
        self.stop()

        self.clear_items()
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.org_user == 0:
            return False
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.stop()

class ViewParticipants(nextcord.ui.View):
    def __init__(self, pages, entrants):
        super().__init__(timeout=120)
        self.pages = pages
        self.entrants = entrants
        self.cur = 1
        
    @nextcord.ui.button(emoji="⬅️", style=nextcord.ButtonStyle.blurple, disabled=True)
    async def left_arrow(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.cur -= 1
        if self.cur == 1:
            self.left_arrow.disabled = True
        if not self.cur == len(self.pages):
            self.right_arrow.disabled = False

        embed_desc = "\n".join(f"- <@{str(self.pages[self.cur-1][i-1])}> ({str(self.entrants.count(self.pages[self.cur-1][i-1]))} entries)" for i in range(len(self.pages[self.cur-1])))
        embed = nextcord.Embed(title=f"Participants ({self.cur}/{len(self.pages)})", description=f"{embed_desc}", colour=COLOUR_MAIN)

        await interaction.response.edit_message(embed=embed, view=self)

    
    @nextcord.ui.button(emoji="➡️", style=nextcord.ButtonStyle.blurple)
    async def right_arrow(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.cur += 1
        if self.cur == len(self.pages):
            self.right_arrow.disabled = True
        else:
            self.right_arrow.disabled = False
        if not self.cur == 1:
            self.left_arrow.disabled = False

        embed_desc = "\n".join(f"- <@{str(self.pages[self.cur-1][i-1])}> ({str(self.entrants.count(self.pages[self.cur-1][i-1]))} entries)" for i in range(len(self.pages[self.cur-1])))
        embed = nextcord.Embed(title=f"Participants ({self.cur}/{len(self.pages)})", description=f"{embed_desc}", colour=COLOUR_MAIN)

        await interaction.response.edit_message(embed=embed, view=self)



class EnterGiveaway(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="0 (0)", emoji="🎉", style=nextcord.ButtonStyle.blurple, custom_id="enter_giveaway")
    async def enter_giveaway(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        msg = await interaction.send(embed=nextcord.Embed(title="Please Wait...", colour=COLOUR_NEUTRAL), ephemeral=True)
        giveawaydata: List[GiveawayMain] = Bot.db.get_data(table="giveaway", message_id=interaction.message.id)
        entrants = giveawaydata[0].entrants
        entrants = [] if not entrants else entrants
        if interaction.user.id in entrants:
            confirm_button = Confirm(org_user=interaction.user.id)
            await msg.edit(embed=nextcord.Embed(title="Confirm entry removal", description="Are you sure you want to leave the giveaway?", colour=COLOUR_NEUTRAL), view=confirm_button)
            await confirm_button.wait()
            if confirm_button.value == True:
                giveawaydata[0].entrants = list(filter((interaction.user.id).__ne__, entrants))
                giveaway: List[GiveawayMain] = Bot.db.update_data(table="giveaway", data=giveawaydata[0])
                button.label = f"{str(len(list(set(giveaway.entrants))))} ({str(len(giveaway.entrants))})"
                await interaction.message.edit(view=self)
                await msg.edit(embed=nextcord.Embed(title="Left giveaway", description=f"Your entry to **{giveawaydata[0].item}** giveaway has been removed.", colour=COLOUR_BAD), view=None)
                return
            else:
                await msg.edit(embed=nextcord.Embed(title="Giveaway leaving cancelled", description=f"Successfully cancelled removing your entry for **{giveawaydata[0].item}** giveaway", colour=COLOUR_GOOD), view=None)
                return
        user_stats_data: List[UserStatisticsBase] = Bot.db.get_data(table="user_statistics", unique_id=f"{interaction.guild.id}-{interaction.user.id}")
        if not user_stats_data:
            user_stats_data: UserStatisticsBase = Bot.db.create_data(table="user_statistics", unique_id=f"{interaction.guild.id}-{interaction.user.id}", user_id=interaction.user.id, guild_id=interaction.guild.id, total_msgs=0, last_daily_msgs=0, last_weekly_msgs=0, last_monthly_msgs=0)
        else:
            user_stats_data = user_stats_data[0]


        # ROLE REQUIREMENTS
        if giveawaydata[0].allowedroles:
            has_allowed_role = False
            for role_id in giveawaydata[0].allowedroles:
                try:
                    role = interaction.guild.get_role(int(role_id))
                    if role in interaction.user.roles:
                        has_allowed_role = True
                except:
                    pass

            if not has_allowed_role:
                await msg.edit(embed=nextcord.Embed(title="Entry denied", description="You don't have any of the required roles for this giveaway.", colour=COLOUR_BAD))
                return
        
        if giveawaydata[0].blockedroles:
            has_blocked_role = False
            for role_id in giveawaydata[0].blockedroles:
                try:
                    role = interaction.guild.get_role(int(role_id))
                    if role in interaction.user.roles:
                        has_blocked_role = True
                except:
                    pass

            if has_blocked_role:
                await msg.edit(embed=nextcord.Embed(title="Entry denied", description="You have one of the blocked roles for this giveaway.", colour=COLOUR_BAD))
                return
        
        bypass = False
        if giveawaydata[0].bypassroles:
            for roleid in giveawaydata[0].bypassroles:
                try:
                    role = interaction.guild.get_role(int(roleid))
                    if role in interaction.user.roles:
                        bypass = True
                except:
                    pass

        # MESSAGE REQUIREMENTS
        if giveawaydata[0].min_daily_msgs and int(giveawaydata[0].min_daily_msgs) > 0 and bypass is False:
            if not int(user_stats_data.total_msgs)-int(user_stats_data.last_daily_msgs) >= giveawaydata[0].min_daily_msgs:
                await msg.edit(embed=nextcord.Embed(title="Entry denied", description=f"You only have {int(user_stats_data.total_msgs)-int(user_stats_data.last_daily_msgs)} out of the required {giveawaydata[0].min_daily_msgs} daily messages.", colour=COLOUR_BAD))
                return
        
        if giveawaydata[0].min_total_msgs and giveawaydata[0].min_total_msgs > 0 and bypass is False:
            if not int(user_stats_data.total_msgs) >=giveawaydata[0].min_total_msgs:
                await msg.edit(embed=nextcord.Embed(title="Entry denied", description=f"You only have {int(user_stats_data.total_msgs)} out of the required {giveawaydata[0].min_total_msgs} total messages.", colour=COLOUR_BAD))
                return
            
        # ENTER GIVEAWAY

        # CHECK BOOSTS
        boostdata: List[GiveawayTempBoosterBase] =  Bot.db.get_data(table="giveaway_temp_boosters", message_id=interaction.message.id)
        stackboost = giveawaydata[0].stackboostedroles
        boosts = []
        entries = 1
        if boostdata:
            for boost in boostdata:
                boostrole = interaction.guild.get_role(int(boost.boost_role_id))
                if boostrole in interaction.user.roles:
                    boosts.append(int(boost.boost_amount))
            if len(boosts) > 0:
                if not stackboost:
                    entries = max(boosts)
                else:
                    entries = 0
                    for amnt in boosts:
                        entries += amnt
        
        giveawaydata: List[GiveawayMain] = Bot.db.get_data(table="giveaway", message_id=interaction.message.id)
        entrants = giveawaydata[0].entrants if giveawaydata[0].entrants else []
        for i in range(entries):
            entrants.append(interaction.user.id)
        giveawaydata[0].entrants = entrants
        giveaway: List[GiveawayMain] = Bot.db.update_data(table="giveaway", data=giveawaydata[0])
        button.label = f"{str(len(list(set(giveaway.entrants))))} ({str(len(giveaway.entrants))})"
        await interaction.message.edit(view=self)
        await msg.edit(embed=nextcord.Embed(title="Entry confirmed", description=f"Your entry for **{giveawaydata[0].item}** giveaway has been confirmed.", colour=COLOUR_GOOD))


    @nextcord.ui.button(label="Participants", style=nextcord.ButtonStyle.grey, custom_id="view_participants")
    async def get_participants(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        msg = await interaction.send(embed=nextcord.Embed(title="Please Wait...", colour=COLOUR_MAIN), ephemeral=True)
        giveawaydata: List[GiveawayMain] = Bot.db.get_data(table="giveaway", message_id=interaction.message.id)
        entrants = giveawaydata[0].entrants
        if len(entrants) == 0:
            await msg.edit(embed=nextcord.Embed(title="Nobody has entered this giveaway", colour=COLOUR_NEUTRAL))
            return
        non_duplicate_entrants = list(set(entrants))
        entry_list = []
        for i in range(0, len(non_duplicate_entrants), 15):
            entry_list_temp = []
            for j in non_duplicate_entrants[i:i+15]:
                entry_list_temp.append(int(j))
            entry_list.append(entry_list_temp)
        embed_desc = "\n".join(f"- <@{str(entry_list[0][i-1])}> ({str(entrants.count(entry_list[0][i-1]))} entries)" for i in range(len(entry_list[0])))
        embed = nextcord.Embed(title=f"Participants (1/{len(entry_list)})", description=f"{embed_desc}", colour=COLOUR_MAIN)
        print(entry_list)
        if len(entry_list) == 1:
            await msg.edit(embed=embed)
        else:
            participants_view = ViewParticipants(pages = entry_list, entrants=entrants)
            await msg.edit(embed=embed, view=participants_view)


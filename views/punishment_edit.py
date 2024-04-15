import nextcord, pymysql, datetime
from nextcord import Interaction
from constants import COLOUR_GOOD, COLOUR_MAIN, COLOUR_NEUTRAL, DBENDPOINT, DBPORT, DBUSER, DBPASS, DBNAME
from utils.utils import create_error_embed
from views import Confirm


class Punishment_Edit(nextcord.ui.View):
    def __init__(self, punishment, org_user:nextcord.Member):
        super().__init__()
        self.punishment = punishment
        self.punishment_id = punishment[0][1]
        self.member_id = punishment[0][2]
        self.mod_id = punishment[0][3]
        self.punishment_type = punishment[0][4]
        self.reason = punishment[0][5]
        self.duration = punishment[0][6]
        self.expires = punishment[0][7]
        self.given = punishment[0][8]
        self.evidence = punishment[0][10]
        self.org_user = org_user.id


    @staticmethod
    async def duration_input_to_text(durationinput):
        try:
            if durationinput[-1] == "s":
                duration=int(int(durationinput[:-1]))
                durationsuffix = "second(s)"
            elif durationinput[-1] == "m" and "perm" not in durationinput:
                duration = int(int(durationinput[:-1])*60)
                durationsuffix = "min(s)"
            elif durationinput[-1] == "h":
                duration = int(int(durationinput[:-1])*3600)
                durationsuffix = "hour(s)"
            elif durationinput[-1] == "d":
                duration = int(int(durationinput[:-1])*86400)
                durationsuffix = "day(s)"
            elif durationinput[-1] == "M" and "perm" not in durationinput:
                duration = int(int(durationinput[:-1])*2629746)
                durationsuffix = "month(s)"
            elif durationinput[-2] =="mo":
                duration = int(int(durationinput[:-2])*2629746)
                durationsuffix = "month(s)"
            elif durationinput[-1] == "y":
                duration=int(int(durationinput[:-1])*31556952)
                durationsuffix = "year(s)"
            elif durationinput.lower() == "permanent" or durationinput.lower() == "perm":
                duration = "Permanent"
                durationsuffix = ""
            else:
                duration = "ERROR"
                durationsuffix = create_error_embed(title=f"Invalid duration", description=f"You provided an invalid duration.")
        except:
            duration = "ERROR"
            durationsuffix = create_error_embed(title=f"Invalid duration", description=f"You provided an invalid duration.")
        return duration, durationsuffix

    @nextcord.ui.button(label="Edit Reason", style=nextcord.ButtonStyle.blurple)
    async def punishment_edit_reason(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `guild_mod` WHERE punishment_id = %s AND guild_id = %s", (self.punishment_id, interaction.guild.id))
        data = cur.fetchall()
        conn.commit()
        if not data:
            await interaction.edit(embed=create_error_embed(title="Error!", description="I couldn't find a punishment from this server with that ID"), view=None, content=None)
            return
        options = Punishment_Edit_Reason()
        await interaction.response.send_modal(modal=options)
        await options.wait()
        cur.execute(f"UPDATE `guild_mod` SET `reason` = %s WHERE punishment_id = %s And guild_id = %s", (str(options.reasonanswer), self.punishment_id, interaction.guild.id))
        conn.commit()
        await interaction.edit(content=f"Punishment reason updated to ``{str(options.reasonanswer)}``", embed=await self.update_embed(interaction.guild.id))
    
    @nextcord.ui.button(label="Edit Duration", style=nextcord.ButtonStyle.blurple)
    async def punishment_edit_duration(self, button: nextcord.ui.Button, interaction: Interaction):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `guild_mod` WHERE punishment_id = %s AND guild_id = %s", (self.punishment_id, interaction.guild.id))
        data = cur.fetchall()
        conn.commit()
        if not data:
            await interaction.edit(embed=create_error_embed(title="Error!", description="I couldn't find a punishment from this server with that ID"), view=None, content=None)
            return
        new_duration = Punishment_Edit_Duration()
        await interaction.response.send_modal(modal=new_duration)
        await new_duration.wait()
        duration, durationsuffix = await self.duration_input_to_text(new_duration.duration)
        if duration == "ERROR":
            await interaction.send(embed=durationsuffix)
            return
        if not duration == "Permanent" and duration > 3155695200:
            duration = 3155695200
        expires = int(self.given) + duration
        cur.execute(f"UPDATE `guild_mod` SET `expires` = %s, `duration` = %s WHERE punishment_id = %s And guild_id = %s", (str(expires), str(duration), self.punishment_id, interaction.guild.id))
        conn.commit()
        await interaction.edit(content=f"Punishment duration updated to end at <t:{expires}>", embed=await self.update_embed(interaction.guild.id))

    @nextcord.ui.button(label="Edit Evidence", style=nextcord.ButtonStyle.blurple)
    async def punishment_edit_evidence(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `guild_mod` WHERE punishment_id = %s AND guild_id = %s", (self.punishment_id, interaction.guild.id))
        data = cur.fetchall()
        conn.commit()
        if not data:
            await interaction.edit(embed=create_error_embed(title="Error!", description="I couldn't find a punishment from this server with that ID"), view=None, content=None)
            return
        options = Punishment_Edit_Evidence()
        await interaction.response.send_modal(modal=options)
        await options.wait()
        cur.execute(f"UPDATE `guild_mod` SET `evidence` = %s WHERE punishment_id = %s And guild_id = %s", (str(options.evidence), self.punishment_id, interaction.guild.id))
        conn.commit()
        await interaction.edit(content=f"Punishment evidence updated to ``{str(options.evidence)}``", embed=await self.update_embed(interaction.guild.id))

    @nextcord.ui.button(label="Delete Punishment", style=nextcord.ButtonStyle.red)
    async def punishment_edit_delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `guild_mod` WHERE punishment_id = %s AND guild_id = %s", (self.punishment_id, interaction.guild.id))
        data = cur.fetchall()
        conn.commit()
        if not data:
            await interaction.edit(embed=create_error_embed(title="Error!", description="I couldn't find a punishment from this server with that ID"), view=None, content=None)
            return
        embed = nextcord.Embed(title="Confirmation", description="Are you sure you want to **__PERMANENTLY__** delete this punishment\n\n**THIS ACTION CANNOT BE UNDONE**", colour=COLOUR_NEUTRAL)
        confirmation = Confirm(org_user=self.org_user)
        await interaction.edit(embed=embed, view=confirmation)
        await confirmation.wait()
        decision = confirmation.value
        if not decision:
            await interaction.edit_original_message(embed=await self.update_embed(interaction.guild.id), view=Punishment_Edit(self.punishment, interaction.user))
        else:
            cur.execute(f"DELETE FROM `guild_mod` WHERE punishment_id=%s", self.punishment_id)
            conn.commit()
            await interaction.edit(embed=nextcord.Embed(description="Successfully deleted punishment", colour=COLOUR_GOOD), view=None)

    async def update_values(self, punishment_id, guild_id):
        conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `guild_mod` WHERE punishment_id = %s AND guild_id = %s", (punishment_id, guild_id))
        punishment = cur.fetchall()
        conn.commit()
        self.punishment_id = punishment[0][1]
        self.member_id = punishment[0][2]
        self.mod_id = punishment[0][3]
        self.punishment_type = punishment[0][4]
        self.reason = punishment[0][5]
        self.duration = punishment[0][6]
        self.expires = punishment[0][7]
        self.given = punishment[0][8]
        self.evidence = punishment[0][10]


    async def update_embed(self, guild):
        await self.update_values(self.punishment_id, guild)
        duration = self.duration
        if not duration == "None":
            if not duration == "Permanent":
                duration=int(duration)
                td = datetime.timedelta(seconds=duration)
                durationtext = ""
                durationtext += f"{td.days}d" if td.days != 0 else ""
                durationtext += f"{td.seconds//3600}h" if td.seconds//3600 != 0 else ""
                durationtext += f"{(td.seconds//60)%60}m" if (td.seconds//60)%60 != 0 else ""
                durationtext += f"{td.seconds%60}s" if td.seconds%60 != 0 else ""

            else:
                durationtext = duration
        else:
            durationtext = "N/A"
        embed = nextcord.Embed(title="Punishment Edit", description=f"""Punishment Information:
        
``Member ID: {self.member_id}
Moderator ID: {self.mod_id}
Punishment Type: {str(self.punishment_type).capitalize()}
Duration: {durationtext}
Reason: {str(self.reason)[:1500]}
Evidence: {str(self.evidence)[:300]}``

Please select what you want to do next using the buttons below""", colour=COLOUR_MAIN)
        return embed

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.org_user != interaction.user.id:
            await interaction.send("You cannot click this button!", ephemeral=True)
            return False
        
        return True

        

class Punishment_Edit_Reason(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Change Punishment Reason", timeout=None)
        self.newreason = nextcord.ui.TextInput(
            label = "What is your new reason?",
            placeholder = "Example: Spamming",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=150,
            required=True
        )
        self.add_item(self.newreason)
        

    async def callback(self, interaction: nextcord.Interaction):
        self.reasonanswer = self.newreason.value
        self.stop()

class Punishment_Edit_Evidence(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Change Punishment Evidence", timeout=None)
        self.evidence = nextcord.ui.TextInput(
            label = "What is your new evidence?",
            placeholder = "Example: He cheated",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=150,
            required=True
        )
        self.add_item(self.evidence)
        

    async def callback(self, interaction: nextcord.Interaction):
        self.evidence = self.evidence.value
        self.stop()


class Punishment_Edit_Duration(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Change Punishment Duration", timeout=None)
        self.newduration = nextcord.ui.TextInput(
            label = "What is your new duration?",
            placeholder = "Please Note: This will be changed from when the original punishment was given.",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=150,
            required=True
        )
        self.add_item(self.newduration)
        

    async def callback(self, interaction: nextcord.Interaction):
        self.duration = self.newduration.value
        self.stop()
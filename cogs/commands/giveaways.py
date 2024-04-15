import nextcord, time, random
from asyncio import tasks
from nextcord import SlashOption, Interaction
from nextcord.ext import commands, tasks
from bot import Bot
from utils import *
from nextcord.abc import GuildChannel
import pymysql
from constants import COLOUR_BAD, COLOUR_GOOD, COLOUR_MAIN, DBENDPOINT, DBNAME, DBUSER, DBPASS, DBPORT
from db_handler.schemas import *
from typing import List, Union
from views import Giveaway_List_Options, Confirm, Giveaway_Boost_Roles_Boosts, RequirementConfirm, EnterGiveaway, Bypass_Giveaway_List_Options



class Giveaways(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
        self.end_giveaways.start()

    @nextcord.slash_command(name="giveaway", description="giveaway base")
    async def giveaway(self, interaction:Interaction):
        pass

    @giveaway.subcommand(name="create", description="Create a new giveaway")
    async def giveaway_create(self,
        interaction: Interaction,
        channel: GuildChannel = SlashOption(
            name="channel",
            description="The channel to send the giveaway message to",
            required=True,
            channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.news]
        ),
        item: str = SlashOption(
            name="item",
            description="The item you are giving away",
            required=True
        ),
        duration: str = SlashOption(
            name="duration",
            description="How long the giveaway should last (e.g. 1d, 6h)",
            required=True
        ),
        winners: int = SlashOption(
            name="winners",
            description="The amount of people who will win the item",
            required=False,
            default=1
        ),
        host: nextcord.Member = SlashOption(
            name="host",
            description="The person hosting the giveaway",
            required=False,
            default=None
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer()
        giveaway_embed=nextcord.Embed(title=f"{item[:256]}", description="Click the button below to enter the giveaway.", colour=COLOUR_MAIN)
        giveaway_embed.add_field(name="Giveaway Info", value="e", inline=False)
        ends_at = utils.duration_input_to_text(duration)
        print(ends_at)
        if ends_at == "ERROR":
            await interaction.send(embed=create_error_embed(title="Invalid Duration", description="The duration you inputted is invalid."))
            return
        required_roles_ids = []
        blacklisted_roles_ids = []

        confirm_view = Confirm(org_user=interaction.user.id)
        await interaction.send(embed=nextcord.Embed(title="Do you want to add required roles to this giveaway?", colour=COLOUR_MAIN), view=confirm_view)
        await confirm_view.wait()
        if confirm_view.value:
            role_menu=Giveaway_List_Options(org_user=interaction.user.id)
            await interaction.edit_original_message(embed=nextcord.Embed(title="Select the required roles for this giveaway", description="Click the dropdown on this message to select the roles you want", colour=COLOUR_MAIN), view=role_menu)
            await role_menu.wait()
            required_roles=role_menu.values
            giveaway_embed.add_field(name="Required Roles", value=f"{','.join([role.mention for role in required_roles])}", inline=False)
            required_roles_ids = [role.id for role in required_roles]
        
        confirm_view = Confirm(org_user=interaction.user.id)
        await interaction.edit_original_message(embed=nextcord.Embed(title="Do you want to add blacklisted roles to this giveaway?", colour=COLOUR_MAIN), view=confirm_view)
        await confirm_view.wait()
        if confirm_view.value:
            role_menu=Giveaway_List_Options(org_user=interaction.user.id)
            await interaction.edit_original_message(embed=nextcord.Embed(title="Select the blacklisted roles for this giveaway", description="Click the dropdown on this message to select the roles you want", colour=COLOUR_MAIN), view=role_menu)
            await role_menu.wait()
            blacklisted_roles=role_menu.values
            giveaway_embed.add_field(name="Blacklisted Roles", value=f"{','.join([role.mention for role in blacklisted_roles])}", inline=False)
            blacklisted_roles_ids = [role.id for role in blacklisted_roles]

        stackboosts = False
        boosts = []

        confirm_view = Confirm(org_user=interaction.user.id)
        await interaction.edit_original_message(embed=nextcord.Embed(title="Do you want to give some roles a boost in entries?", colour=COLOUR_MAIN), view=confirm_view)
        await confirm_view.wait()
        if confirm_view.value:
            role_menu=Giveaway_List_Options(org_user=interaction.user.id)
            await interaction.edit_original_message(embed=nextcord.Embed(title="Select which roles you would like to give a boost to", description="Click the dropdown on this message to select the roles you want", colour=COLOUR_MAIN), view=role_menu)
            await role_menu.wait()
            boosted_roles=role_menu.values
            boosts = []
            boost_desc = ""
            for role in boosted_roles:
                embed=nextcord.Embed(title="Setup boosted roles", description=f"What boost do you want to give to {role.mention}", colour=COLOUR_MAIN)
                boost_selection = Giveaway_Boost_Roles_Boosts(org_user=interaction.user.id)
                await interaction.edit_original_message(embed=embed, view=boost_selection)
                await boost_selection.wait()
                boosts.append(boost_selection.value)
                boost_desc+=f"{role.mention} - **{boost_selection.value}x**\n"
            giveaway_embed.add_field(name="Boosted Roles", value=boost_desc, inline=False)
            confirm_view = Confirm(org_user=interaction.user.id)
            await interaction.edit_original_message(embed=nextcord.Embed(title="Should roles boosted entries stack?", colour=COLOUR_MAIN), view=confirm_view)
            await confirm_view.wait()
            stackboosts = confirm_view.value

        requirements_desc =""    
        
        confirm_view = RequirementConfirm(org_user=interaction.user.id)
        await interaction.edit_original_message(embed=nextcord.Embed(title="Do you want to add a minimum daily message requirement?", colour=COLOUR_MAIN), view=confirm_view)
        await confirm_view.wait()
        min_daily_messages = confirm_view.value
        try:
            min_daily_messages = int(min_daily_messages)
        except:
            min_daily_messages = 0
        requirements_desc += f"{confirm_view.value} messages sent today\n" if int(min_daily_messages) > 0 else ""

        # confirm_view = RequirementConfirm(org_user=interaction.user.id)
        # await interaction.edit_original_message(embed=nextcord.Embed(title=f"Do you want to add a minimum weekly message requirement?", colour=COLOUR_MAIN), view=confirm_view)
        # await confirm_view.wait()
        # min_weekly_messages = confirm_view.value
        # requirements_desc += f"{confirm_view.value} messages sent this week" if (not min_daily_messages == True or not min_daily_messages == False or not min_daily_messages == None) else ""

        # confirm_view = RequirementConfirm(org_user=interaction.user.id)
        # await interaction.edit_original_message(embed=nextcord.Embed(title=f"Do you want to add a minimum monthly message requirement?", colour=COLOUR_MAIN), view=confirm_view)
        # await confirm_view.wait()
        # min_monthly_messages = confirm_view.value
        # requirements_desc += f"{confirm_view.value} messages sent this month" if (not min_daily_messages == True or not min_daily_messages == False or not min_daily_messages == None) else ""

        confirm_view = RequirementConfirm(org_user=interaction.user.id)
        await interaction.edit_original_message(embed=nextcord.Embed(title="Do you want to add a minimum total message requirement?", colour=COLOUR_MAIN), view=confirm_view)
        await confirm_view.wait()
        min_total_messages = confirm_view.value
        try:
            min_total_messages = int(min_total_messages)
        except:
            min_total_messages = 0
        requirements_desc += f"{confirm_view.value} messages sent total\n" if int(min_total_messages) >0 else ""

        if requirements_desc != "":
            giveaway_embed.add_field(name="Requirements", value=requirements_desc)

        bypass_roles_ids = []
        if not min_total_messages == 0 or not min_daily_messages == 0:

            confirm_view = Confirm(org_user=interaction.user.id)
            await interaction.edit_original_message(embed=nextcord.Embed(title="Do you want to add a requirement bypass role to this giveaway?", colour=COLOUR_MAIN), view=confirm_view)
            await confirm_view.wait()
            if confirm_view.value:
                role_menu=Bypass_Giveaway_List_Options(org_user=interaction.user.id)
                await interaction.edit_original_message(embed=nextcord.Embed(title="Select the requirement bypass role for this giveaway", description="Click the dropdown on this message to select the role you want", colour=COLOUR_MAIN), view=role_menu)
                await role_menu.wait()
                bypass_roles=role_menu.values
                giveaway_embed.add_field(name="Requirement Bypass Role", value=f"{','.join([role.mention for role in bypass_roles])}", inline=False)
                bypass_roles_ids = [role.id for role in bypass_roles]

        giveaway_embed.set_field_at(index=0, name="Giveaway Info", value=(f"Duration: <t:{int(round(time.time()))+ends_at}> (Ends: <t:{int(round(time.time()))+ends_at}:R>)\nWinners: {winners}\n" + (f"Host: {host.mention}" if host else "")), inline=False)
        gw_msg = await channel.send(embed=giveaway_embed, view=EnterGiveaway())
        giveawaydata: List[GiveawayMain] = Bot.db.create_data(table="giveaway", guild_id=interaction.guild.id, channel_id=channel.id, message_id=gw_msg.id, winners=winners, item=item, ends=int(round(time.time()))+ends_at, allowedroles=required_roles_ids, blockedroles=blacklisted_roles_ids, stackboostedroles=stackboosts, min_daily_msgs = min_daily_messages if min_daily_messages else 0, min_total_msgs = min_total_messages if min_total_messages else 0, bypassroles=bypass_roles_ids)
        if not boosts == []:
            i = 0
            for role in boosted_roles:
                boostdata: List[GiveawayTempBoosterBase] = Bot.db.create_data(table="giveaway_temp_boosters", message_id=gw_msg.id, boost_role_id=role.id, boost_amount=boosts[i])
                i+=1
        await interaction.edit_original_message(embed=create_success_embed(title="Giveaway created", description=f"Your giveaway has been created and set up in {channel.mention}"), view=None)

    @giveaway.subcommand(name="reroll", description="Reroll a giveaway")
    async def giveaway_reroll(self,
                            interaction:Interaction,
                            giveaway_id: str = SlashOption(
                                name="message-id",
                                description="The message ID of the giveaway you want to reroll",
                                required=True)
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        data: List[GiveawayMain] = Bot.db.get_data("giveaway", guild_id=interaction.guild.id, message_id=int(giveaway_id))
        if not data:
            await interaction.send(embed=create_error_embed(title="Invalid message ID", description="The message ID provided is not a valid giveaway message ID."))
            return
        data = data[0]
        if not int(data.ends) == 1:
            await interaction.send(embed=create_error_embed(title="Giveaway not finished", description="The giveaway provided has not finished so cannot be rerolled."))
            return
        channel = interaction.guild.get_channel(int(data.channel_id))
        message = await channel.fetch_message(int(data.message_id))

        entrants = data.entrants
        entries = data.entrants

        if len(list(set(entrants))) < data.winners:
            embed = nextcord.Embed(title=f"{data.item[0:255]}", description="Nobody won this giveaway as there was not enough entries.", colour=COLOUR_BAD)
            await interaction.send(embed=embed, ephemeral=True)
            return

        winners = []
        winner = random.choice(entrants)
        member = interaction.guild.get_member(winner)
        winners.append(member)
        entrants = list(filter((winner).__ne__, entrants))

        await interaction.send(f"The new giveaway winner for **{data.item[0:255]}** is: {winners[0].mention}")

    @giveaway.subcommand(name="end", description="End a currently running giveaway")
    async def giveaway_end(self,
                            interaction:Interaction,
                            giveaway_id: str = SlashOption(
                                name="message-id",
                                description="The message ID of the giveaway you want to reroll",
                                required=True)
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_warning_embed(title="Lacking Permissions", description="You are lacking the `administrator` permission, contact the server administrators if you believe this is an error"))
            return
        await interaction.response.defer(ephemeral=True)
        giveaway: List[GiveawayMain] = Bot.db.get_data("giveaway", guild_id=interaction.guild.id, message_id=int(giveaway_id))
        if not giveaway:
            await interaction.send(embed=create_error_embed(title="Invalid message ID", description="The message ID provided is not a valid giveaway message ID."))
            return
        giveaway = giveaway[0]
        if int(giveaway.ends) == 1:
            await interaction.send(embed=create_error_embed(title="Giveaway already finished", description="The giveaway provided has already finished so cannot be ended."))
            return

        channel = interaction.guild.get_channel(int(giveaway.channel_id))
        message = await channel.fetch_message(int(giveaway.message_id))
        await message.edit(view=None)

        entrants = giveaway.entrants
        entries = giveaway.entrants
        if len(list(set(entrants))) < giveaway.winners:
            embed = nextcord.Embed(title=f"{giveaway.item[0:255]}", description="Nobody won this giveaway as there was not enough entries.", colour=COLOUR_BAD)
            await message.edit(embed=embed)
            embed = nextcord.Embed(title="Giveaway Ended", description="Nobody won this giveaway as there was not enough entries.", colour=COLOUR_BAD)
            await message.reply(embed=embed)
            giveaway.ends = 1
            Bot.db.update_data(table="giveaway", data=giveaway)
            return

        winners = []
        for i in range(int(giveaway.winners)):
            winner = random.choice(entrants)
            member = interaction.guild.get_member(winner)
            winners.append(member)
            entrants = list(filter((winner).__ne__, entrants))

        giveaway.ends = 1
        Bot.db.update_data(table="giveaway", data=giveaway)
        embed = nextcord.Embed(title=f"{giveaway.item[0:255]}", description=f"Entries: {len(list(set(entries)))}\nWinner(s): {','.join(winner.mention for winner in winners)}", colour=COLOUR_BAD)
        embed.set_footer(text="This giveaway has ended.")
        await message.edit(embed=embed)
        embed = nextcord.Embed(title="Giveaway Ended", description=f"Entries: {len(list(set(entries)))}\nWinner(s): {','.join(winner.mention for winner in winners)}", colour=COLOUR_GOOD)
        await message.reply(','.join(winner.mention for winner in winners), embed=embed)
        await interaction.send("Giveaway successfully ended.")
        try:
            await message.edit(view=None)
        except:
            return


    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.client.add_view(EnterGiveaway())
            print(color_message(message="Loaded EnterGiveaway view", color="blue"))
        except Exception as e:
            print(e)
            print(color_message(message="Failed to load EnterGiveaway view", color="yellow"))


    @tasks.loop(seconds=5)
    async def end_giveaways(self):
        try:
            await self.client.wait_until_ready()
            conn = pymysql.connect(host=DBENDPOINT, port=DBPORT, user=DBUSER, password=DBPASS, db=DBNAME)
            cur = conn.cursor()
            cur.execute("SELECT * FROM giveaway_main WHERE ends < %s AND ends != '1'", round(time.time()))
            data = cur.fetchall()
            for giveaway in data:
                try:
                    giveaway: List[GiveawayMain] = Bot.db.get_data(table="giveaway", message_id=giveaway[2])
                    giveaway = giveaway[0]
                    if not giveaway.ends < round(time.time()) or giveaway.ends == 1:
                        return
                    guild = self.client.get_guild(int(giveaway.guild_id))
                    channel = guild.get_channel(int(giveaway.channel_id))
                    message = await channel.fetch_message(int(giveaway.message_id))
                    await message.edit(view=None)

                    entrants = giveaway.entrants
                    entries = giveaway.entrants
                    if len(list(set(entrants))) < giveaway.winners:
                        embed = nextcord.Embed(title=f"{giveaway.item[0:255]}", description="Nobody won this giveaway as there was not enough entries.", colour=COLOUR_BAD)
                        await message.edit(embed=embed)
                        embed = nextcord.Embed(title="Giveaway Ended", description="Nobody won this giveaway as there was not enough entries.", colour=COLOUR_BAD)
                        await message.reply(embed=embed)
                        giveaway.ends = 1
                        Bot.db.update_data(table="giveaway", data=giveaway)
                        continue

                    winners = []
                    for i in range(int(giveaway.winners)):
                        winner = random.choice(entrants)
                        member = guild.get_member(winner)
                        winners.append(member)
                        entrants = list(filter((winner).__ne__, entrants))

                    giveaway.ends = 1
                    Bot.db.update_data(table="giveaway", data=giveaway)
                    embed = nextcord.Embed(title=f"{giveaway.item[0:255]}", description=f"Entries: {len(list(set(entries)))}\nWinner(s): {','.join(winner.mention for winner in winners)}", colour=COLOUR_BAD)
                    embed.set_footer(text="This giveaway has ended.")
                    await message.edit(embed=embed)
                    embed = nextcord.Embed(title="Giveaway Ended", description=f"Entries: {len(list(set(entries)))}\nWinner(s): {','.join(winner.mention for winner in winners)}", colour=COLOUR_GOOD)
                    await message.reply(','.join(winner.mention for winner in winners), embed=embed)
                    try:
                        await message.edit(view=None)
                    except:
                        return
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)




def setup(client: Bot):
    client.add_cog(Giveaways(client))
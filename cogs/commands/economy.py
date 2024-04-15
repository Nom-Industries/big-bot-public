from typing import Union
import nextcord, random, aiohttp, asyncio, requests
from nextcord.ext import commands
from bot.bot import Bot
from utils.utils import create_success_embed, create_error_embed
from views import Confirm, EconomyPurchaseAmount, FishEnabled, FishDisabled, PostVideoChoice, TaskButton, RedoTask, DigSpade, DigDrill, HigherOrLower, WorkTriviaView
from constants import COOKIE, SHOPITEMINFO, HUNTWINITEMS, HUNTWINOPTIONS, FISHWINITEMS, FISHINGWINOPTIONS, POSSIBLEITEMS, POSSIBLEITEMSINFO, SHOPITEMS, COLOUR_MAIN, COLOUR_GOOD, COLOUR_NEUTRAL, COLOUR_BAD, DIGPROFIT, DIGCHANCES, ECONOMY_TIPS
import cooldowns, time, math
from db_handler.schemas import *

class Economy(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    async def end_tasks(self, message: nextcord.Message, interaction: nextcord.Interaction):
        chance = random.randint(1,15)
        if chance == 1:
            data: List[Economy_User_Settings] = self.client.db.get_data(table="economy_user_settings", user=interaction.user.id)
            if not data or data[0].tips is True:
                tip = random.choice(ECONOMY_TIPS)
                await message.channel(tip + f" {interaction.user.mention}")
                
        if chance in (2, 3):
            await message.edit(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @staticmethod
    async def get_user(guild, user, create_if_not_exist = True):
        data: List[EconomyMain] = Bot.db.get_data(table="economy", guild_id=guild, user_id=user)
        if not data:
            if create_if_not_exist:
                data = [Bot.db.create_data(table="economy", guild_id=guild, user_id=user, balance=0, daily=round(time.time()), weekly=round(time.time()), monthly=round(time.time()))]

            else:
                return False

        return data
    
    @staticmethod
    async def update_user(user: EconomyMain):
        data = Bot.db.update_data(table="economy", data=user)
        return data

    async def daily_check_reset(self, user: int, guild: Union[str, int]):
        data: List[EconomyMain] = await self.get_user(guild, user)
        if round(time.time()) > data[0].daily:
            data[0].balance += round(100)
            data[0].daily = round(time.time()) + 86400
            data: EconomyMain = await self.update_user(data[0])
            return data, round(100)
        
        return data[0].daily
    
    async def weekly_check_reset(self, user: int, guild: Union[str, int]):
        data: List[EconomyMain] = await self.get_user(guild, user)
        if round(time.time()) > data[0].weekly:
            data[0].balance += round(1000)
            data[0].weekly = round(time.time()) + 604800
            data: EconomyMain = await self.update_user(data[0])
            return data, round(1000)
        
        return data[0].weekly
    
    async def monthly_check_reset(self, user: int, guild: Union[str, int]):
        data: List[EconomyMain] = await self.get_user(guild, user)
        if round(time.time()) > data[0].monthly:
            data[0].balance += round(10000)
            data[0].monthly = round(time.time()) + 2629800
            data: EconomyMain = await self.update_user(data[0])
            return data, round(10000)
        
        return data[0].monthly

    @nextcord.slash_command(name="inventory", description="View your inventory items")
    @cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author)
    async def inventory(self,
        interaction:nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="User to view eventory of",
            required=False
        )):
        await interaction.response.defer()
        if not user:
            user = interaction.user

        data: EconomyMain = await self.get_user(guild="global", user=user.id)
        description=f"Here is a list of the items **{user}** currently has in their inventory:\n\n"
        for i in POSSIBLEITEMS:
            itemname = POSSIBLEITEMSINFO[i]["name"]
            itemamount = data[0].__dict__[i]
            if itemamount != 0:
                description+=f"{itemname} - {itemamount}\n"
        
        if description==f"Here is a list of the items **{user}** currently has in their inventory:\n\n":
            await interaction.send(f"**{user}** doesn't have any items in their inventory")
            return
        
        embed = nextcord.Embed(description=description, colour=COLOUR_MAIN)
        embed.set_footer(text=f"Run by {interaction.user.name}")

        await interaction.send(embed=nextcord.Embed(description=description, colour=COLOUR_MAIN))

    @nextcord.slash_command(name="work", description="Work to nom some cookies")
    @cooldowns.cooldown(1, 900, bucket=cooldowns.SlashBucket.author)
    async def work(self, interaction: nextcord.Interaction):
        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel.id == interaction.channel.id
            
        winnings = random.randint(50,250)
        data = await self.get_user(guild="global", user=interaction.user.id)
        energyUsed = False
        if int(data[0].energy) > 0:
            data[0].energy -= 1
            energyUsed=True
            winnings = random.randint(150, 350)

        activity = random.randint(1, 4)
        if activity == 1:
            num1=random.randint(1,10)
            num2=random.randint(10,50)
            if num1 <=5:
                embed = nextcord.Embed(title="Work", description=f"What is {num1}+{num2}", colour=COLOUR_MAIN)
                embed.set_footer(text=f"Run by {interaction.user.name}")
                msgsent = await interaction.send(embed=embed)
                try:
                    answer = await self.client.wait_for('message', check=check, timeout=120)
                    if str(answer.content) == str(num1+num2):
                        data[0].balance += round(winnings*float(data[0].current_boost))
                        embed = nextcord.Embed(title="Work", description=f"Correct! You got {round(winnings*float(data[0].current_boost))} {COOKIE}'s ({data[0].current_boost}x boost) for your work\n\nYou now have {data[0].balance} {COOKIE}'s", colour=COLOUR_GOOD)
                        embed.set_footer(text=f"Run by {interaction.user.name}")
                        await msgsent.edit(embed=embed)
                    else:
                        embed.set_footer(text=f"Run by {interaction.user.name}")
                        await msgsent.edit(embed=nextcord.Embed(title="Work", description=f"Incorrect. You got nothing LLLLLL!", colour=COLOUR_BAD))
                except asyncio.TimeoutError:
                    await msgsent.delete()
                    await interaction.send(f"{interaction.user.mention} You took too long to answer.")
            else:
                msgsent=await interaction.send(embed=nextcord.Embed(title="Work", description=f"What is {num2}-{num1}", colour=COLOUR_MAIN))
                try:
                    answer = await self.client.wait_for('message', check=check, timeout=120)
                    if str(answer.content) == str(num2-num1):
                        data[0].balance += round(winnings*float(data[0].current_boost))
                        await msgsent.edit(embed=nextcord.Embed(title="Work", description=f"Correct! You got {round(winnings*float(data[0].current_boost))} {COOKIE}'s ({data[0].current_boost}x boost) for your work\n\nYou now have {data[0].balance} {COOKIE}'s", colour=COLOUR_GOOD))
                    else:
                        await msgsent.edit(embed=nextcord.Embed(title="Work", description=f"Incorrect. You got nothing LLLLLL!", colour=COLOUR_BAD))
                    await self.end_tasks(msgsent, interaction)
                except asyncio.TimeoutError:
                    await msgsent.delete()
                    await interaction.send(f"{interaction.user.mention} You took too long to answer.")
            try:
                await answer.delete()
            except Exception as e:
                pass

        elif activity == 2:
            embed = nextcord.Embed(title="Work", description=f"Remember the order of these colour squares", colour=COLOUR_MAIN)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            msgsent = await interaction.send(embed=embed)
            await asyncio.sleep(3)
            colours = ["purple", "yellow", "green", "red", "blue", "brown", "orange", "white", "black"]
            colourschosen = []
            for i in range(6):
                chosen=random.choice(colours)
                if not chosen == "white" and not chosen=="black":
                    await msgsent.edit(embed=None, content=f"{i+1}. :{chosen}_square:")
                else:
                    await msgsent.edit(embed=None, content=f"{i+1}. :{chosen}_large_square:")
                colourschosen.append(chosen)
                await asyncio.sleep(1)
            num1 = random.randint(1, 5)
            embed = nextcord.Embed(title="Work", description=f"What was the colour of sqaure number {num1}", colour=COLOUR_MAIN)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            await msgsent.edit(content=None, embed=embed)
            try:
                answer = await self.client.wait_for('message', check=check, timeout=120)
                if str(answer.content.lower()) == str(colourschosen[num1-1]):
                    data[0].balance += round(winnings*float(data[0].current_boost))
                    embed = nextcord.Embed(title="Work", description=f"Correct! You got {round(winnings*float(data[0].current_boost))} {COOKIE}'s ({data[0].current_boost}x boost) for your work\n\nYou now have {data[0].balance} {COOKIE}'s", colour=COLOUR_GOOD)
                    embed.set_footer(text=f"Run by {interaction.user.name}")
                    await msgsent.edit(embed=embed)
                else:
                    embed = nextcord.Embed(title="Work", description=f"Incorrect. You got nothing LLLLLL!", colour=COLOUR_BAD)
                    embed.set_footer(text=f"Run by {interaction.user.name}")
                    await msgsent.edit(embed=embed)
                await self.end_tasks(msgsent, interaction)
            except asyncio.TimeoutError:
                await msgsent.delete()
                await interaction.send(f"{interaction.user.mention} You took too long to answer.")
            try:
                await answer.delete()
            except Exception as e:
                pass

        elif activity in (3, 4):
            difficulty = random.choice(["easy", "medium", "hard"])
            winnings_values = {"easy": random.randint(50, 150), "medium": random.randint(150, 350), "hard": random.randint(350, 500)}
            winnings = round(winnings_values[difficulty.lower()] * float(data[0].current_boost))
            if energyUsed:
                winnings = round((winnings_values[difficulty] + 50)  * float(data[0].current_boost))

            res = requests.get(f"https://the-trivia-api.com/api/questions?categories=history,science,food_and_drink,general_knowledge,geography,film_and_tv,arts_and_literature,music,society_and_culture,sport_and_leisure&limit=1&difficulty={difficulty}").json()[0]
            question = res["question"]
            category = res["category"]
            questionid = res["id"]
            answer = res["correctAnswer"]
            incorrectanswers = res["incorrectAnswers"]
            answers = [answer]
            answers.extend(incorrectanswers)
            random.shuffle(answers) 
            answertext = "\n".join(f'{i+1}. {answers[i]}' for i in range(len(answers)))
            embedcolours = {"easy": COLOUR_GOOD, "medium": COLOUR_NEUTRAL, "hard": COLOUR_BAD}
            embed = nextcord.Embed(title=f"{category} Trivia Question ({difficulty.capitalize()})", description=f"{question}\n\n**Answers:**\n\n{answertext}", colour=embedcolours[difficulty])
            embed.set_footer(text=f"Run by {interaction.user.name} | {questionid}")
            workview = WorkTriviaView(org_user=interaction.user.id, answers=answers)
            msg = await interaction.send(embed=embed, view=workview)
            await workview.wait()

            view = WorkTriviaView(org_user=interaction.user.id, answers=answers, selected_answer=answers[int(workview.value)-1], correct=answer)

            if answers[int(workview.value)-1] == answer:
                embed = nextcord.Embed(title="Correct!", description=f"You correctly answered the trivia question! You earned {winnings} {COOKIE}'s ({data[0].current_boost}x boost)\n\nYou now have {data[0].balance} {COOKIE}'s", colour=COLOUR_GOOD)
                data[0].balance += winnings

            else:
                embed = nextcord.Embed(title=f"Incorrect", description=f"You got the answer wrong! LLLLLL\n\nThe correct answer was `{answer}`", colour=COLOUR_BAD)

            embed.set_footer(text=f"Run by {interaction.user.name} | {questionid}")
            await msg.edit(embed=embed, view=view)

        await self.update_user(data[0])
    
    @nextcord.slash_command(name="nom", description="Nom some cookies")
    @cooldowns.cooldown(1, 30, bucket=cooldowns.SlashBucket.author)
    async def nom(self, interaction: nextcord.Interaction):
        amount = random.randint(40,60)
        data = await self.get_user(guild="global", user=interaction.user.id)
        if int(data[0].yeast) > 0:
            data[0].yeast -= 1
            amount = random.randint(47,67)
    
        data[0].balance += round(amount*float(data[0].current_boost))
        await self.update_user(data[0])
        embed=nextcord.Embed(title="Nom", description=(f"You nommed {round(amount*float(data[0].current_boost))} {COOKIE} ({data[0].current_boost}x boost)\n\n You now have {data[0].balance} {COOKIE}."), colour=COLOUR_GOOD)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        msgsent=await interaction.send(embed=embed)
        await self.end_tasks(msgsent, interaction)

    @nextcord.slash_command(name="balance", description="View your or another user's cookie balance")
    @cooldowns.cooldown(1, 3, bucket=cooldowns.SlashBucket.author)
    async def balance(self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            name="member",
            description="Member to check the balance of",
            required=False
        )):
        if not member:
            member = interaction.user
        
        data = await self.get_user(guild="global", user=member.id, create_if_not_exist=False)
        if not data:
            await interaction.send("That member is not registered with our economy system.", ephemeral=True)
            return

        cookies = data[0].balance
        await interaction.send(content=f"**You** have {int(cookies):,} {COOKIE}'s" if member.id == interaction.user.id else f"**{member.name}** has {int(cookies):,} {COOKIE}'s")
    
    @nextcord.slash_command(name="daily", description="Get your daily cookies")
    async def daily(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        check = await self.daily_check_reset(interaction.user.id, "global")
        if isinstance(check, tuple):
            embed = nextcord.Embed(title="Daily", description=f"You got your daily cookie allowance of {check[1]} {COOKIE}'s\n\n You now have {check[0].balance} {COOKIE}.\n\nYou can use `daily` again <t:{check[0].daily}:R>", colour=COLOUR_GOOD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            await interaction.send(embed=embed)
        
        else:
            await interaction.send("Your `daily` command is on cooldown. You can use it again <t:{}:R>".format(check))

    @nextcord.slash_command(name="weekly", description="Get your weekly cookies")
    async def weekly(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        check = await self.weekly_check_reset(interaction.user.id, "global")
        if isinstance(check, tuple):
            embed = nextcord.Embed(title="Weekly", description=f"You got your weekly cookie allowance of {check[1]} {COOKIE}'s\n\n You now have {check[0].balance} {COOKIE}.\n\nYou can use `weekly` again <t:{check[0].weekly}:R>", colour=COLOUR_GOOD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            await interaction.send(embed=embed)
        
        else:
            await interaction.send("Your `weekly` command is on cooldown. You can use it again <t:{}:R>".format(check))

    @nextcord.slash_command(name="monthly", description="Get your monthly cookies")
    async def monthly(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        check = await self.monthly_check_reset(interaction.user.id, "global")
        if isinstance(check, tuple):
            embed = nextcord.Embed(title="Monthly", description=f"You got your monthly cookie allowance of {check[1]} {COOKIE}'s\n\n You now have {check[0].balance} {COOKIE}.\n\nYou can use `monthly` again <t:{check[0].monthly}:R>", colour=COLOUR_GOOD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            await interaction.send(embed=embed)
        
        else:
            await interaction.send("Your `monthly` command is on cooldown. You can use it again <t:{}:R>".format(check))


    #     if amount > user[0].balance or amount < 1:
    #         await interaction.send("You only have {} {} available to bet.".format(user[0].balance, COOKIE), ephemeral=True)
    #         return
    
        

    #     await self.update_user(user[0])

    #     await interaction.send(embed=embed)

    @nextcord.slash_command(name="pray", description="Pray to the nom Gods for some more cookies")
    @cooldowns.cooldown(1, 30, bucket=cooldowns.SlashBucket.author)
    async def pray(self,
        interaction: nextcord.Interaction):
        amount = random.randint(2,60)
        data = await self.get_user(guild="global", user=interaction.user.id)
        if int(data[0].pedestal) > 0:
            amount = random.randint(20, 80)
            breakchance = random.randint(1, 350)
            if breakchance == 274:
                data[0].pedestal -= 1
                data = await self.update_user(data[0])
                embed = nextcord.Embed(title="Pray", description=f"You have used your pedestal so much that it broke!\n\nYou now have {data.pedestal} pedestals left", colour=COLOUR_BAD)
                embed.set_footer(text=f"Run by {interaction.user.name}")
                await interaction.send(embed=embed)
                return

        data[0].balance += round(amount*data[0].current_boost)
        if amount < 10:
            message = f"The God's gave you {round(amount*data[0].current_boost)} {COOKIE}'s out of pity ({data[0].current_boost}x boost)"
        elif amount < 40:
            message = f"The God's gave you a medicore {round(amount*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)"
        else:
            message=f"The God's gave you {round(amount*data[0].current_boost)} {COOKIE}'s out of respect ({data[0].current_boost}x boost)"

        embed=nextcord.Embed(title="Pray", description=message + "\n\nYou now have {} {}'s".format(data[0].balance, COOKIE), colour=COLOUR_GOOD)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        msgsent=await interaction.send(embed=embed)
        await self.update_user(data[0])
        await self.end_tasks(msgsent, interaction)

    @nextcord.slash_command(name="shop", description="Open the shop")
    async def shop(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=False)
        user = await self.get_user(guild="global", user=interaction.user.id)
        boosts_bought = user[0].norm_boost
        embed = nextcord.Embed(title="Shop", description=f"""Use `/buy` to purchase any items from the shop.\n\n**Useful Items:**

Hunting Rifle - 2,500 🍪's [ID: rifle]
Hunting Spear - 1,000 🍪's [ID: spear]
Fishing Rod - 1,200 🍪's [ID: rod]
Spade - 1,000 🍪's [ID: spade]
Drill - 5,000 🍪's [ID: drill]
Fishing Bait - 5 🍪's [ID: bait]
Yeast - 5 🍪's [ID: yeast]
Praying Pedestal - 3,000 🍪's [ID: pedestal]
Energy Drink - 25 🍪's [ID: energy]
Poison - 10 🍪's [ID: poison]
Computer - 5,600 🍪's [ID: comp]
Minion - 100,000 🍪's [ID: minion]
        
    
**Trophies:**

Poor Trophy - ~~100~~ **1** 🍪's [ID: p\_trophy]
Rich Trophy - 100,000 🍪's [ID: r\_trophy]
Super Rich Trophy - 1,000,000 🍪's [ID: sr\_trophy]
Super Mega Rich Trophy - 10,000,000 🍪's [ID: smr\_trophy]
Super Insanely Mega Rich Trophy - 100,000,000 🍪's  [ID: simr\_trophy]


**Boosts:**

Permanent +0.01 boost (Max 100) - {round((5000)+(5000*(int(boosts_bought)*0.01465))+(int(boosts_bought)*143.56))} 🍪's [ID: norm_boost]""", colour=COLOUR_MAIN)
        embed.set_footer(text=f"Use `/item <item_ID>` to get information about a specific item.")
        await interaction.send(embed=embed)

    @nextcord.slash_command(name="item", description=f"Check the information of an item")
    async def item(self,
        interaction:nextcord.Interaction,
        item: str = nextcord.SlashOption(
            name="item",
            description="Item to check",
            required=True
        )):
        if not item.lower() in POSSIBLEITEMS:
            await interaction.send(embed=create_error_embed(title="Invalid item", description=f"That is not a valid item"))
            return
        itemname = POSSIBLEITEMSINFO[item.lower()]["name"]
        itemid = POSSIBLEITEMSINFO[item.lower()]["id"]
        itemmax = POSSIBLEITEMSINFO[item.lower()]["max"]
        itemcost = POSSIBLEITEMSINFO[item.lower()]["cost"]
        itemdescription = POSSIBLEITEMSINFO[item.lower()]["description"]
        embed = nextcord.Embed(title=f"{itemname} information", description=f"""
        {itemdescription}

        **Extra Information:**

        Name: {itemname}
        ID: {itemid}
        Cost: {itemcost} {COOKIE}'s
        Max: {itemmax}""", colour=COLOUR_MAIN)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        await interaction.send(embed=embed)

    @item.on_autocomplete("item")
    async def autocomplete_item(self, interaction:nextcord.Interaction, item:str):
        if item == "":
            await interaction.response.send_autocomplete(SHOPITEMS)
            return
        get_near_item = [
            ite for ite in SHOPITEMS if ite.lower().startswith(item.lower())
        ]
        await interaction.response.send_autocomplete(get_near_item)

    @nextcord.slash_command(name="buy", description="Buy an item from the shop")
    async def buy(self,
        interaction: nextcord.Interaction,
        item: str = nextcord.SlashOption(
            name="item",
            description="Item to buy",
            required=True
        )):
        user = await self.get_user(guild="global", user=interaction.user.id)
        if item.lower() == "norm_boost":
            if user[0].norm_boost == 100:
                await interaction.send(embed=create_error_embed(title="Maximum Reached", description="You have reached the maximum amount of boosts."))
                return
            
            cost = round((5000)+(5000*(int(user[0].norm_boost)*0.01465))+(int(user[0].norm_boost)*143.56))
            amount_choose, amount, maximum_allowed = False, 1, 100

        else:
            try:
                item_info = SHOPITEMINFO[item.lower()]
                cost = int(item_info["cost"])
                amount_choose = True
                maximum_allowed = int(item_info["max"])
                if int(item_info["max"]) == 1:
                   amount_choose, amount = False, 1

            except KeyError:
                await interaction.send(embed=create_error_embed(title="Invalid Item", description="That is not an item! Make sure you use the item's ID in the item field."))
                return

        if amount_choose:
            amountchoosing = EconomyPurchaseAmount()
            await interaction.response.send_modal(amountchoosing)
            await amountchoosing.wait()
            amount = int(amountchoosing.amount)

        if not item.lower() == "norm_boost":
            if user[0].__dict__[item.lower()] + amount > maximum_allowed:
                await interaction.send(embed=create_error_embed(title="Invalid Amount", description=f"You cannot buy that many of `{item.lower()}`. The maximum amount allowed of this item is {maximum_allowed}"))
                return

        if cost * amount > int(user[0].balance):
            await interaction.send(embed=create_error_embed(title="Not enough cookies", description="You haven't nommed enough cookies to be able to buy this item"))
            return

        user[0].balance -= cost * amount
        user[0].__dict__[item.lower()] += int(amount)

        msg = await interaction.send(embed=create_success_embed(title="Item purchased!", description=f"You successfully purchased `{amount}` of `{item.lower()}` for {cost * amount} {COOKIE}`s. You now have {user[0].balance} {COOKIE}'s"))
        if item.lower() == "minion":            
            await interaction.channel.send(f"{interaction.user.mention}, you just purchased a minion! Use </minion view:1055861120721756190> to activate it.")
            
        if item.lower() == "norm_boost":
            user[0].current_boost += 0.01

        await self.update_user(user[0])

    @buy.on_autocomplete("item")
    async def autocomplete_buy(self, interaction: nextcord.Interaction, item: str):
        if item == "":
            await interaction.response.send_autocomplete(SHOPITEMS)
            return
        get_near_item = [
            ite for ite in SHOPITEMS if ite.lower().startswith(item.lower())
        ]
        await interaction.response.send_autocomplete(get_near_item)

    @nextcord.slash_command(name="share", description="Share some of your cookies with another member")
    @cooldowns.cooldown(1, 600, bucket=cooldowns.SlashBucket.author)
    async def share(self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            name="member",
            description="Member to share cookies with",
            required=True
        ),
        amount: int = nextcord.SlashOption(
            name="cookies",
            description="Amount of cookies to share",
            required=True
        )):
        if amount <= 0:
            await interaction.send("Amount must be > 0", ephemeral=True)
            return
        if round(time.time()) - int(time.mktime(time.strptime(str(interaction.user.joined_at)[:19],"%Y-%m-%d %H:%M:%S"))) < 172800:
            await interaction.send("You must have been in the server for at least 2 days to share cookies", ephemeral=True)
            return
        if round(time.time()) - int(time.mktime(time.strptime(str(interaction.user.created_at)[:19],"%Y-%m-%d %H:%M:%S"))) < 1209600:
            await interaction.send("You must have an account age of over 2 weeks to share cookies", ephemeral=True)
            return
        if interaction.user == member:
            await interaction.send("You cannot share cookies with yourself", ephemeral=True)
            return

        await interaction.response.defer()

        sharer = await self.get_user(guild="global", user=interaction.user.id, create_if_not_exist=False)
        if not sharer:
            await interaction.send("You are not currently registered with our economy system. Please use `/nom` to start nomming cookies")
            return

        receiver = await self.get_user(guild="global", user=member.id, create_if_not_exist=False)
        if not receiver:
            await interaction.send(f"**{member.name}** is not currently registered with our economy system. They can use `/nom` to start nomming cookies")
            return
            

        if int(sharer[0].balance) < amount:
            await interaction.send(f"You do not have {amount} {COOKIE}'s to give. Your current balance is {sharer[0].balance} {COOKIE}'s")
            return

        confirmation = Confirm(org_user=int(interaction.user.id))
        embed = nextcord.Embed(title="Are you sure?", description=f"You are about to give {amount} {COOKIE}'s to **{member.name}**. Are you sure you want to proceed?", colour=COLOUR_NEUTRAL)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        await interaction.send(embed=embed, view=confirmation)
        await confirmation.wait()
        if confirmation.value:
            sharer[0].balance -= amount
            receiver[0].balance += amount
            await interaction.edit_original_message(embed=create_success_embed(title="Success!", description=f"You successfully gave **{member.name}** {amount} {COOKIE}'s. Your balance is now {sharer[0].balance} {COOKIE}'s. {member.name}'s balance is now {receiver[0].balance} {COOKIE}'s"), view=None)
            async with aiohttp.ClientSession() as session:
                webhook = nextcord.Webhook.from_url("https://canary.discord.com/api/webhooks/1035987969498173531/6RyGQrWK6SBIurVopgL-AU_DSfo4jZWK_MT6Z1v7rmk294bWp0NmbyrIxtxqK-W3aiZe", session=(session))
                await webhook.send(f"``{interaction.user} ({interaction.user.id}) ({sharer[0].balance} {COOKIE}'s)`` Shared ``{amount} {COOKIE}'s`` with ``{member} ({member.id}) ({receiver[0].balance} {COOKIE}'s)``\n\nGuild: ``{interaction.guild.name} ({interaction.guild.id})``\nChannel: ``{interaction.channel} ({interaction.channel.id})``")

            await self.update_user(sharer[0])
            await self.update_user(receiver[0])

        else:
            embed=nextcord.Embed(title="Cancelled", description=f"You cancelled your `/share` to **{member.name}**", colour=COLOUR_NEUTRAL)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            await interaction.edit_original_message(embed=embed, view=None)        

    @nextcord.slash_command(name="hunt", description="Hunt in the scary woods to find some cookies")
    @cooldowns.cooldown(1, 25, bucket=cooldowns.SlashBucket.author)
    async def hunt(self, interaction: nextcord.Interaction):
        data = await self.get_user(guild="global", user=interaction.user.id)
        extra_boost = 0
        if data[0].rifle == 0 and data[0].spear == 0:
            await interaction.send("You required a spear or rifle to use `/hunt`. Check them out in `/shop`", ephemeral=True)
            return

        chance = 50
        if data[0].poison > 0:
            chance = 65
            extra_boost += random.randint(2, 13)
            data[0].poison -= 1
        
        winningchance = random.randint(0, 100)
        if winningchance <= chance:
            item = random.choice(HUNTWINITEMS)
            iteminfo = HUNTWINOPTIONS[item]
            itemprice = iteminfo["amount"]
            itemmessage = random.choice(iteminfo["messages"])
            winningamount = random.randint((int(itemprice)-10), (int(itemprice)+10)) + extra_boost
            data[0].balance += round(winningamount*data[0].current_boost)
            embed = nextcord.Embed(title="Hunt", description=f"{itemmessage} {round(winningamount*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\n You now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            msgsent=await interaction.send(embed=embed)
            await self.end_tasks(msgsent, interaction)

        else:
            embed = nextcord.Embed(title="Hunt", description=f"You found nothing. LLLLL!", colour=COLOUR_BAD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            breaknum = random.randint(1,20)
            if breaknum == 5:
                items = data[0].spear if data[0].rifle == 0 else data[0].rifle
                if data[0].rifle == 0:
                    data[0].spear -= 1

                else:
                    data[0].rifle -= 1
                
                embed = nextcord.Embed(title="Hunt", description=f"Your {'Spear' if data[0].rifle == 0 else 'Rifle'} broke! You now have {items-1} {'spear(s)' if data[0].rifle == 0 else 'rifle(s)'} left", colour=COLOUR_BAD)
                embed.set_footer(text=f"Run by {interaction.user.name}")
            
            await interaction.send(embed=embed)
        
        await self.update_user(data[0])

    @nextcord.slash_command(name="fish", description="Go fishing to find some treasures")
    @cooldowns.cooldown(1, 25, bucket=cooldowns.SlashBucket.author)
    async def fish(self, interaction:nextcord.Interaction):
        data = await self.get_user(guild="global", user=interaction.user.id)
        if data[0].rod == 0:
            await interaction.send("You required a fishing rod to use `/fish`. Check them out in `/shop`", ephemeral=True)
            return
            
        num1 = random.randint(1,100)
        if data[0].bait > 0:
            data[0].bait -= 1
            win=True if num1 <= 80 else False

        else:
            win=True if num1 <= 50 else False

        if win:
            embed=nextcord.Embed(title="Fish", description=f"You feel a tug at the end of your rod. You need to make sure you click catch when it becomes available to catch the fish!", colour=COLOUR_MAIN)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            msg = await interaction.send(embed=embed, view=FishDisabled(org_user=interaction.user.id))
            await asyncio.sleep(random.randint(2, 5))
            enabled = FishEnabled(org_user=interaction.user.id)
            await msg.edit(embed=embed, view=enabled)
            await enabled.wait()
            await msg.edit(embed=embed, view=FishDisabled(org_user=interaction.user.id))
            caught = enabled.value
            if caught:
                item = random.choice(FISHWINITEMS)
                iteminfo = FISHINGWINOPTIONS[item]
                itemprice = iteminfo["amount"]
                itemmessage = random.choice(iteminfo["messages"])
                winningamount = random.randint((int(itemprice)-10), (int(itemprice)+10))
                data[0].balance += round(winningamount*data[0].current_boost)
                embed = nextcord.Embed(title="Fish", description=f"{itemmessage} {round(winningamount*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\n You now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
                embed.set_footer(text=f"Run by {interaction.user.name}")
                await msg.edit(embed=embed, view=None)
                await self.end_tasks(msg, interaction)
            
            else:
                embed=nextcord.Embed(title="Fish", description=f"You were too slow! You get nothing LLLLLLL!", colour=COLOUR_BAD)
                embed.set_footer(text=f"Run by {interaction.user.name}")
                await msg.edit(embed=embed, view=None)
        else:
            embed = nextcord.Embed(title="Fish", description=f"You fished up nothing. LLLLL!", colour=COLOUR_BAD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            breaknum = random.randint(1,20)
            if breaknum == 5:
                data[0].rod -= 1
                embed = nextcord.Embed("Fish", description=f"Your fishing rod broke! You now have {data[0].rod} fishing rods left.", colour=COLOUR_BAD)
                embed.set_footer(text=f"Run by {interaction.user.name}")

            await interaction.send(embed=embed)
        
        await self.update_user(data[0])

    @nextcord.slash_command(name="dig", description=f"Dig for hidden treasure.")
    @cooldowns.cooldown(1, 25, bucket=cooldowns.SlashBucket.author)
    async def dig(self, interaction:nextcord.Interaction):
        data = await self.get_user(guild="global", user=interaction.user.id)
        if data[0].spade == 0 and data[0].drill == 0:
            await interaction.send("You required a spade or drill to use `/dig`. Check them out in `/shop`", ephemeral=True)
            return

        digview = DigSpade(org_user=interaction.user.id)
        breakchance = random.randint(1, 30)
        if data[0].drill > 0:
            digview = DigDrill(org_user=interaction.user.id)
            breakchance = random.randint(1, 250)
       
        embed = nextcord.Embed(title="Dig", description="Click the button below to choose where you want to mine\n- Indium Mine - 100% chance of success - Low profit\n- Silver Mine - 80% chance of success - Low-Mid profit\n- Osmium Mine - 60% chance of success - Mid profit\n- Platinum Mine - 35% chance of success - Mid-High profit\n\n- Gold Mine - 90% chance of success - Mid profit (Drill Only)\n- Rhenium Mine - 75% chance of success - Mid-High profit (Drill Only)\n- Palladium Mine - 50% chance of success - High rofit (Drill Only)\n- Rhodium Mine - 20% chance of success - Very High profit (Drill Only)", colour=COLOUR_MAIN)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        msg = await interaction.send(embed=embed, view=digview)
        await digview.wait()
        if digview.value == "Not Given":
            await msg.delete()
            await interaction.send(f"{interaction.user.mention} You took too long to answer.")
            return

        if breakchance == 27:
            if data[0].drill > 0:
                data[0].drill -= 1
                embed = nextcord.Embed("Dig", description=f"Your drill broke! You now have {data[0].drill} drills left.", colour=COLOUR_BAD)
                embed.set_footer(text=f"Run by {interaction.user.name}")
                await interaction.send(embed=embed, view=None)
                return

            else:
                data[0].spade -= 1
                embed = nextcord.Embed("Dig", description=f"Your spade broke! You now have {data[0].spade} spades left.", colour=COLOUR_BAD)
                embed.set_footer(text=f"Run by {interaction.user.name}")
                await interaction.send(embed=embed, view=None)
                return
                
        chancenum = random.randint(0, 100)
        if chancenum < DIGCHANCES[digview.value]:
            profit = random.randint(int(DIGPROFIT[digview.value])-15, int(DIGPROFIT[digview.value]+15))
            data[0].balance += round(profit*data[0].current_boost)
            embed = nextcord.Embed(title="Dig", description=f"You found {round(profit*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost) from the **{digview.value} mine**\n\n You now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            await msg.edit(embed=embed, view=None)
            await self.end_tasks(msg, interaction)

        else:
            embed = nextcord.Embed(title="Dig", description=f"You found nothing in the **{digview.value} mine**, LLLLL!", colour=COLOUR_BAD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            await msg.edit(embed=embed, view=None)
        
        await self.update_user(data[0])
            
    @nextcord.slash_command(name="postvideo", description="Post a video and hope it does well")
    @cooldowns.cooldown(1, 30, bucket=cooldowns.SlashBucket.author)
    async def postvideo(self, interaction:nextcord.Interaction):
        data = await self.get_user(guild="global", user=interaction.user.id)
        if data[0].comp == 0:
            await interaction.send("You required a computer to use `/postvideo`. Check it out in `/shop`", ephemeral=True)
            return

        videoChoice = PostVideoChoice(org_user=interaction.user.id)
        embed = nextcord.Embed(title="Post video", description=f"What type of video do you want to post?", colour=COLOUR_MAIN)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        msg = await interaction.send(embed=embed, view=videoChoice)
        await videoChoice.wait()
        chosen = videoChoice.value
        chance = random.randint(1, 3)
        if chance == 1:
            money = random.randint(10, 30)
            chance2 = random.randint(1, 100)
            if chance2 == 1:
                data[0].comp -= 1
                embed = nextcord.Embed(title="Post video", description=f"Your video did so bad that your computer somehow broke! You now have {data[0].comp} computer(s) left.", colour=COLOUR_BAD)
                embed.set_footer(text=f"Run by {interaction.user.name}")
                await msg.edit(embed=embed, view=None)
                return

        elif chance == 2:
            money = random.randint(75, 100)

        else:
            money = random.randint(120, 160)

        if chosen == "Not Given":
            await interaction.delete_original_message()
            await interaction.send(f"{interaction.user.mention} You took too long to answer.")
            return
            
        data[0].balance += round(money*data[0].current_boost)

        if chosen == "Gaming":
            embed = nextcord.Embed(title="Post video", description=f"Your gaming video got you {round(money*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\nYou now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
        elif chosen == "Debate":
            embed = nextcord.Embed(title="Post video", description=f"Your debate managed to get you {round(money*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\nYou now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
        elif chosen == "Educational":
            embed = nextcord.Embed(title="Post video", description=f"Your educational video got you {round(money*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\nYou now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
        elif chosen == "Meme":
            embed = nextcord.Embed(title="Post video", description=f"Your meme compilation video got you {round(money*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\nYou now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
        elif chosen == "Music":
            embed = nextcord.Embed(title="Post video", description=f"Your music video got you {round(money*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\nYou now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
        
        embed.set_footer(text=f"Run by {interaction.user.name}")

        await msg.edit(embed=embed, view=None)
        
        await self.update_user(data[0])
        await self.end_tasks(msg, interaction)

    @nextcord.slash_command(name="higher-or-lower", description=f"Play higher or lower for cookies")
    @cooldowns.cooldown(1, 30, bucket=cooldowns.SlashBucket.author)
    async def higher_or_lower(self, interaction:nextcord.Interaction):
        data = await self.get_user(guild="global", user=interaction.user.id)
        num1 = random.randint(0,100)
        num2 = random.randint(0,100)
        embed = nextcord.Embed(title="Higher or lower", description=f"I am thinking of a number... Is it higher or lower or  than **{num2}**?", colour=COLOUR_MAIN)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        choice_view = HigherOrLower(org_user=interaction.user.id)
        msg = await interaction.send(embed=embed, view=choice_view)
        await choice_view.wait()
        if choice_view.value is None:
            await msg.edit(content="You took too long to answer!", view=None)
            return
        if (num1 > num2 and choice_view.value == "higher") or (num1 < num2 and choice_view.value == "lower"):
            money = random.randint(30, 100)
            data[0].balance += round(money*data[0].current_boost)
            embed = nextcord.Embed(title=f"Higher or lower", description=f"Correct! I was thinking of the number **{num1}**. You won {round(money*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\nYou now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
        elif (num1 == num2 and choice_view.value == "spot"):
            money = random.randint(100, 350)
            data[0].balance += round(money*data[0].current_boost)
            embed = nextcord.Embed(title=f"Higher or lower", description=f"Spot On! I was thinking of the number **{num1}**. You won {round(money*data[0].current_boost)} {COOKIE}'s ({data[0].current_boost}x boost)\n\nYou now have {data[0].balance} {COOKIE}'s.", colour=COLOUR_GOOD)
        else:
            embed = nextcord.Embed(title=f"Higher or lower", description=f"Wrong! I was actually thinking of the number **{num1}**.", colour=COLOUR_BAD)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        await self.update_user(data[0])
        await msg.edit(embed=embed, view=None)
        await self.end_tasks(msg, interaction)

            


    #     elif user[0].balance < amount:
    #         await interaction.send("You only have {} {} available to bet.".format(user[0].balance, COOKIE), ephemeral=True)
    #         return

    #     if str(user[0].comp) == 0:
    #         await interaction.send("You required a computer to use `/invest`. Check it out in `/shop`", ephemeral=True)
    #         return

        
        
        

    #     await interaction.send(embed=embed)

    @nextcord.slash_command(name="minion", description="Minion base")
    async def minion(self, interaction: nextcord.Interaction):
        pass

    @minion.subcommand(name="view", description="View your minions information")
    async def minion_view(self, interaction:nextcord.Interaction):
        data = await self.get_user(guild="global", user=interaction.user.id)
        if data[0].minion == 0:
            await interaction.send("You don't have a minion! You can buy one in `/shop`", ephemeral=True)
            return

        await interaction.response.defer()

        embed = nextcord.Embed(title=f"Minion", colour=COLOUR_MAIN)
        if not data[0].minion_last_check:
            embed = nextcord.Embed(title=f"Minion", description=f"Congrats! You just activated your minion. Here is some of its information:", colour=COLOUR_GOOD)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            data[0].minion_last_check = round(time.time())
            data[0].minion_full = round(time.time()) + 86400
            embed.add_field(name="Minion last emptied", value=f"<t:{data[0].minion_last_check}> (<t:{data[0].minion_last_check}:R>)")
            embed.add_field(name="Minion full", value=f"<t:{data[0].minion_full}> (<t:{data[0].minion_full}:R>)")
            embed.add_field(name="Cookies", value=f"0/8640")
            await interaction.send(embed=embed)
            return
            
        embed.add_field(name="Minion last emptied", value=f"<t:{data[0].minion_last_check}> (<t:{data[0].minion_last_check}:R>)")
        embed.add_field(name="Minion full", value=f"<t:{data[0].minion_full}> (<t:{data[0].minion_full}:R>)" if int(data[0].minion_full) > round(time.time()) else "FULL")
        cookies_available = 8640
        if int(data[0].minion_full) > round(time.time()):
            cookies_available = 8640 - math.ceil((int(data[0].minion_full) - int(round(time.time())))/10)
            
        embed.add_field(name="Cookies", value=f"{cookies_available}/8640")
        await interaction.send(embed=embed)

    @minion.subcommand(name="empty", description="Empty the cookies in your minion")
    async def minion_empty(self, interaction:nextcord.Interaction):
        data = await self.get_user(guild="global", user=interaction.user.id)
        if data[0].minion == 0:
            await interaction.send("You don't have a minion! You can buy one in `/shop`", ephemeral=True)
            return

        elif not data[0].minion_full:
            data[0].minion_last_check = round(time.time())
            data[0].minion_full = round(time.time()) + 86400
            await self.update_user(data[0])
            await interaction.send("You minion hasn't generated any cookies yet. Come back in a bit and you will have some cookies to claim!", ephemeral=True)
            return

        cookies_available = 8640
        
        if int(data[0].minion_full) > round(time.time()):
            cookies_available = 8640 - math.ceil((int(data[0].minion_full) - int(round(time.time())))/10)

        if cookies_available == 0:
            await interaction.send("You minion hasn't generated any cookies yet. Come back in a bit and you will have some cookies to claim!", ephemeral=True)
            return

        data[0].balance += cookies_available
        data[0].minion_last_check = round(time.time())
        data[0].minion_full = round(time.time()) + 86400

        embed = nextcord.Embed(title="Minion", description=f"You emptied your minion and got {cookies_available} {COOKIE}'s from it.\n\nYou now have {data[0].balance} {COOKIE}'s", colour=COLOUR_GOOD)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        await interaction.send(embed=embed)

        await self.update_user(data[0])

    @nextcord.slash_command("task", description=f"Task base")
    async def task(self, interaction:nextcord.Interaction):
        pass

    @task.subcommand(name="all", description=f"Do all money making commands")
    @cooldowns.cooldown(1, 5, bucket=cooldowns.SlashBucket.author)
    async def task_all(self, interaction:nextcord.Interaction):
        embed=nextcord.Embed(description="Starting `all` task", colour=COLOUR_MAIN)
        embed.set_footer(text=f"Run by {interaction.user.name}")
        tempmsg = await interaction.send(embed=embed)
        try:
            await Economy.nom(interaction)
        except Exception as e:
            print(e)
            pass
        Task = TaskButton()
        tempmsg = await interaction.send(embed=nextcord.Embed(description=f"Next Command: `/pray`"), view=Task, ephemeral=True)
        await Task.wait()
        if Task.value is False:
            await interaction.send(embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN))
            embed.set_footer(text=f"Run by {interaction.user.name}")
            return
        elif Task.value is None:
            Task = TaskButton()
            await tempmsg.edit(embed=nextcord.Embed(description=f"Next Command: `/higher-or-lower`"), view=Task)
            await Task.wait()
        elif Task.value is True:
            await tempmsg.delete()
            try:
                await Economy.pray(interaction)
            except Exception as e:
                pass
            Task = TaskButton()
            tempmsg = await interaction.send(embed=nextcord.Embed(description=f"Next Command: `/higher-or-lower`"), view=Task, ephemeral=True)
            await Task.wait()
        if Task.value is False:
            await interaction.send(embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN))
            embed.set_footer(text=f"Run by {interaction.user.name}")
            return
        elif Task.value is None:
            Task = TaskButton()
            await tempmsg.edit(embed=nextcord.Embed(description=f"Next Command: `/hunt`"), view=Task)
            await Task.wait()
        elif Task.value is True:
            await tempmsg.delete()
            try:
                await Economy.higher_or_lower(interaction)
            except:
                pass
            Task = TaskButton()
            tempmsg = await interaction.send(embed=nextcord.Embed(description=f"Next Command: `/hunt`"), view=Task, ephemeral=True)
            await Task.wait()
        if Task.value is False:
            await interaction.send(embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN))
            embed.set_footer(text=f"Run by {interaction.user.name}")
            return
        elif Task.value is None:
            Task = TaskButton()
            await tempmsg.edit(embed=nextcord.Embed(description=f"Next Command: `/postvideo`"), view=Task)
            await Task.wait()
        elif Task.value is True:
            await tempmsg.delete()
            try:
                await Economy.hunt(interaction)
            except:
                pass
            Task = TaskButton()
            tempmsg = await interaction.send(embed=nextcord.Embed(description=f"Next Command: `/postvideo`"), view=Task, ephemeral=True)
            await Task.wait()
        if Task.value is False:
            await interaction.send(embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN))
            embed.set_footer(text=f"Run by {interaction.user.name}")
            return
        elif Task.value is None:
            Task = TaskButton()
            await tempmsg.edit(embed=nextcord.Embed(description=f"Next Command: `/dig`"), view=Task)
            await Task.wait()
        elif Task.value is True:
            await tempmsg.delete()
            try:
                await Economy.postvideo(interaction)
            except:
                pass
            Task = TaskButton()
            tempmsg = await interaction.send(embed=nextcord.Embed(description=f"Next Command: `/dig`"), view=Task, ephemeral=True)
            await Task.wait()
        if Task.value is False:
            await interaction.send(embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN))
            embed.set_footer(text=f"Run by {interaction.user.name}")
            return
        elif Task.value is None:
            Task = TaskButton()
            await tempmsg.edit(embed=nextcord.Embed(description=f"Next Command: `/fish`"), view=Task)
            await Task.wait()
        elif Task.value is True:
            await tempmsg.delete()
            try:
                await Economy.dig(interaction)
            except:
                pass
            Task = TaskButton()
            tempmsg = await interaction.send(embed=nextcord.Embed(description=f"Next Command: `/fish`"), view=Task, ephemeral=True)
            await Task.wait()
        if Task.value is False:
            await interaction.send(embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN))
            embed.set_footer(text=f"Run by {interaction.user.name}")
            return
        elif Task.value is None:
            Task = TaskButton()
            await tempmsg.edit(embed=nextcord.Embed(description=f"Next Command: `/work`"), view=Task)
            await Task.wait()
        else:
            await tempmsg.delete()
            try:
                await Economy.fish(interaction)
            except Exception as e:
                pass
            Task = TaskButton()
            tempmsg = await interaction.send(embed=nextcord.Embed(description=f"Next Command: `/work`"), view=Task, ephemeral=True)
            await Task.wait()
        if Task.value is False:
            await interaction.send(embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN))
            embed.set_footer(text=f"Run by {interaction.user.name}")
            return
        elif Task.value is None:
            Task = TaskButton()
            await tempmsg.edit(embed=nextcord.Embed(description=f"Next Command: `/minion empty`"), view=Task)
            await Task.wait()
        elif Task.value is True:
            await tempmsg.delete()
            try:
                await Economy.work(interaction)
            except Exception as e:
                pass
            Task = TaskButton()
            tempmsg = await interaction.send(embed=nextcord.Embed(description=f"Next Command: `/minion empty`"), view=Task, ephemeral=True)
            await Task.wait()
        await tempmsg.delete()
        if Task.value is False:
            await interaction.send(embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN))
            embed.set_footer(text=f"Run by {interaction.user.name}")
            return
        elif Task.value is True:
            try:
                await Economy.minion_empty(interaction)
            except:
                pass
        try:
            tempmsg = await interaction.send(embed=nextcord.Embed(description=f"I have tried to run all commands. If any have not run it is because they are on cooldown.", colour=COLOUR_MAIN), ephemeral=True)
            redo = RedoTask(org_user=interaction.user.id)
            embed=nextcord.Embed(description=f"Task Ended", colour=COLOUR_MAIN)
            embed.set_footer(text=f"Run by {interaction.user.name}")
            tempmsg2 = await interaction.send(embed=embed, view=redo)
            await redo.wait()
            if redo.value:
                await tempmsg2.delete()
                embed=nextcord.Embed(description="Task started via button", colour=COLOUR_MAIN)
                embed.set_footer(text=f"Run by {interaction.user.name}")
                tempmsg = await interaction.send(embed=embed)
                await Economy.task_all(interaction)
        except Exception as e:
            print(e)
            pass

    @nextcord.slash_command("economy-settings", description=f"Base")
    async def economy_settings(self, interaction: nextcord.Interaction):
        pass

    @economy_settings.subcommand("user", description=f"Toggle your economy user settings")
    async def economy_user(self,
        interaction: nextcord.Interaction,
        tips:bool=nextcord.SlashOption(
            name=f"tips",
            description=f"Choose whether you want tips enabled",
            required=True
        )):
        data: List[Economy_User_Settings] = self.client.db.get_data(table="economy_user_settings", user=interaction.user.id)
        if not data:
            self.client.db.create_data(table="economy_user_settings", user=interaction.user.id, tips=tips)
            
        else:
            data[0].tips = tips
            self.client.db.update_data(table="economy_user_settings", data=data[0])
            
        await interaction.send(embed=create_success_embed(title=("I have successfully" + (" enabled " if tips else " disabled ") + "tips.")))


def get_colour(rank):
    if rank == 0:
        return "#ffd700"
        
    elif rank == 1:
        return "#c0c0c0"
        
    elif rank == 2:
        return "#cd7f32"
    
    else:
        return "#808080"

        

def setup(client: Bot):
    client.add_cog(Economy(client))

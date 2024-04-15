import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from constants import COLOUR_MAIN, COLOUR_GOOD, COLOUR_BAD, COLOUR_NEUTRAL
from views import WorkTriviaView
from bot import Bot
import requests, random
from io import BytesIO
from utils import *

snipe_message_author = {}
snipe_message_content = {}
snipe_message_link = {}

class Fun(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message): # Snipe logging
        if not message.author.bot and not message.content is None: # Makes sure the author is not a bot and that the there is content (In case it's just an image)
            snipe_message_author[message.channel.id] = message.author.id # Adds the message author ID as the most recently deleted message in the channel
            snipe_message_content[message.channel.id] = message.content# Adds the message content as the most recently deleted message in the channel
            snipe_message_link[message.channel.id] =  message.jump_url # Adds the link to the last message as the most recently deleted message in the channel

    @nextcord.slash_command(name="snipe", description="Get the content of the last message deleted in a channel")
    async def fun_snipe(self, interaction: Interaction):
        try: # If there is nothing matching my request in the dict this will error
            embed = nextcord.Embed(title=f"{str(snipe_message_content[interaction.channel.id])[:256]}", description=f"[Go to conversation]({snipe_message_link[interaction.channel.id]})", colour=COLOUR_MAIN) # Adds the first 256 characters of the message content as the embed title and the link as the description.
            embed.set_footer(text=f"Sniped by {interaction.user}") # Add who used the snipe command to the footer
            member = interaction.guild.get_member(int(snipe_message_author[interaction.channel.id])) # Get the member of the orininal message as a member item
            embed.set_author(name=member, icon_url=member.display_avatar.url) # Set the embed author to be the author of the original message 
            await interaction.send(embed=embed)
            del snipe_message_author[interaction.channel.id] # Reset deleted message content
            del snipe_message_content[interaction.channel.id] # Reset deleted message content
            del snipe_message_link[interaction.channel.id] # Reset deleted message content
            chance = random.randint(1, 3)
            if chance == 1:
                await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
        except KeyError: # The error is caught and sends a reasonable message.
            await interaction.send("No recently deleted message was found in this channel", ephemeral=True)

    @nextcord.slash_command(name="fun", description="Fun commands")
    async def fun(self, interaction: Interaction):
        pass

    @fun.subcommand(name="animal", description="Animal Commands")
    async def fun_animal(self, interaction: Interaction):
        pass

    @fun_animal.subcommand(name="cat", description="Get an image of a cat with a fun fact")
    async def fun_cat(self, interaction: Interaction):
        res = requests.get(f"https://some-random-api.com/animal/cat")
        imageData = res.json()
        fact = imageData["fact"]
        image = imageData["image"]
        embed = nextcord.Embed(description=f"Fact: [{fact}]({image})", colour=COLOUR_MAIN)
        embed.set_image(url=image)
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @fun_animal.subcommand(name="dog", description="Get an image of a dog with a fun fact")
    async def fun_dog(self, interaction: Interaction):
        res = requests.get(f"https://some-random-api.com/animal/dog")
        imageData = res.json()
        fact = imageData["fact"]
        image = imageData["image"]
        embed = nextcord.Embed(description=f"Fact: [{fact}]({image})", colour=COLOUR_MAIN)
        embed.set_image(url=image)
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @fun_animal.subcommand(name="bird", description="Get an image of a bird with a fun fact")
    async def fun_bird(self, interaction: Interaction):
        res = requests.get(f"https://some-random-api.com/animal/bird")
        imageData = res.json()
        fact = imageData["fact"]
        image = imageData["image"]
        embed = nextcord.Embed(description=f"Fact: [{fact}]({image})", colour=COLOUR_MAIN)
        embed.set_image(url=image)
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @fun_animal.subcommand(name="fox", description="Get an image of a fox with a fun fact")
    async def fun_fox(self, interaction: Interaction):
        res = requests.get(f"https://some-random-api.com/animal/fox")
        imageData = res.json()
        fact = imageData["fact"]
        image = imageData["image"]
        embed = nextcord.Embed(description=f"Fact: [{fact}]({image})", colour=COLOUR_MAIN)
        embed.set_image(url=image)
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun_animal.subcommand(name="kangaroo", description="Get an image of a kangaroo with a fun fact")
    async def fun_kangaroo(self, interaction: Interaction):
        res = requests.get(f"https://some-random-api.com/animal/kangaroo")
        imageData = res.json()
        fact = imageData["fact"]
        image = imageData["image"]
        embed = nextcord.Embed(description=f"Fact: [{fact}]({image})", colour=COLOUR_MAIN)
        embed.set_image(url=image)
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun_animal.subcommand(name="koala", description="Get an image of a koala with a fun fact")
    async def fun_koala(self, interaction: Interaction):
        res = requests.get(f"https://some-random-api.com/animal/koala")
        imageData = res.json()
        fact = imageData["fact"]
        image = imageData["image"]
        embed = nextcord.Embed(description=f"Fact: [{fact}]({image})", colour=COLOUR_MAIN)
        embed.set_image(url=image)
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun_animal.subcommand(name="panda", description="Get an image of a panda with a fun fact")
    async def fun_panda(self, interaction: Interaction):
        res = requests.get(f"https://some-random-api.com/animal/panda")
        imageData = res.json()
        fact = imageData["fact"]
        image = imageData["image"]
        embed = nextcord.Embed(description=f"Fact: [{fact}]({image})", colour=COLOUR_MAIN)
        embed.set_image(url=image)
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @fun.subcommand(name="filter", description="Filter Commands")
    async def fun_filter(self, interaction: Interaction):
        pass

    @fun_filter.subcommand(name="blue", description="Blue filter")
    async def fun_filter_blue(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to filter avatar",
            required=False
        )):
        if not member:
            member = interaction.user
        embed = nextcord.Embed(colour=COLOUR_MAIN)
        embed.set_image(url=f"https://some-random-api.com/canvas/blue?avatar={member.display_avatar.url}")
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @fun_filter.subcommand(name="green", description="Green filter")
    async def fun_filter_green(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to filter avatar",
            required=False
        )):
        if not member:
            member = interaction.user
        embed = nextcord.Embed(colour=COLOUR_MAIN)
        embed.set_image(url=f"https://some-random-api.com/canvas/green?avatar={member.display_avatar.url}")
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun_filter.subcommand(name="greyscale", description="Greyscale filter")
    async def fun_filter_greyscale(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to filter avatar",
            required=False
        )):
        if not member:
            member = interaction.user
        embed = nextcord.Embed(colour=COLOUR_MAIN)
        embed.set_image(url=f"https://some-random-api.com/canvas/greyscale?avatar={member.display_avatar.url}")
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun_filter.subcommand(name="red", description="Red filter")
    async def fun_filter_red(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to filter avatar",
            required=False
        )):
        if not member:
            member = interaction.user
        embed = nextcord.Embed(colour=COLOUR_MAIN)
        embed.set_image(url=f"https://some-random-api.com/canvas/red?avatar={member.display_avatar.url}")
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun_filter.subcommand(name="blurple", description="Blurple filter")
    async def fun_filter_blurple(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to filter avatar",
            required=False
        )):
        if not member:
            member = interaction.user
        embed = nextcord.Embed(colour=COLOUR_MAIN)
        embed.set_image(url=f"https://some-random-api.com/canvas/blurple?avatar={member.display_avatar.url}")
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun_filter.subcommand(name="sepia", description="Sepia filter")
    async def fun_filter_sepia(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to filter avatar",
            required=False
        )):
        if not member:
            member = interaction.user
        embed = nextcord.Embed(colour=COLOUR_MAIN)
        embed.set_image(url=f"https://some-random-api.com/canvas/sepia?avatar={member.display_avatar.url}")
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun_filter.subcommand(name="blur", description="Blur filter")
    async def fun_filter_blur(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to filter avatar",
            required=False
        )):
        if not member:
            member = interaction.user
        embed = nextcord.Embed(colour=COLOUR_MAIN)
        embed.set_image(url=f"https://some-random-api.com/canvas/blur?avatar={member.display_avatar.url}")
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @fun.subcommand(name="tweet", description="Generate a fake tweet")
    async def fun_tweet(self,
        interaction: Interaction,
        message: str = SlashOption(
            name="message",
            description="Tweet content",
            required=True
        ),
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member making tweet",
            required=False
        ),
        replies: str = SlashOption(
            name="replies",
            description="Number of replies",
            required=False,
            default="420"
        ),
        likes: str = SlashOption(
            name="likes",
            description="Number of likes",
            required=False,
            default="6.9K"
        ),
        retweets: str = SlashOption(
            name="retweets",
            description="Number of retweets",
            required=False,
            default="69"
        ),
        theme: str = SlashOption(
            name="theme",
            description="Tweet Theme",
            required=False,
            choices=["light", "dim", "dark"],
            default="light"
        )):

        await interaction.response.defer()

        if not member:
            member = interaction.user
        nick = member.nick if member.nick else member.name
        imageurl: requests.Response = requests.get(f"https://some-random-api.com/canvas/misc/tweet?avatar={member.display_avatar.url}&displayname={member.name[:25]}&username={nick[:25]}&comment={message[:1000]}&replies={replies}&likes={likes}&retweets={retweets}&theme={theme}").content
        await interaction.send(file = nextcord.File(BytesIO(imageurl), "tweet.png"))
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
    @fun.subcommand(name="youtube", description="Generate fake youtube comment")
    async def fun_youtube(self,
        interaction: Interaction,
        comment: str = SlashOption(
            name="comment",
            description="Comment content",
            required=True
        ),
        member: nextcord.Member = SlashOption(
            name="member",
            description="Comment Author",
            required=False
        )):
        
        await interaction.response.defer()

        if not member:
            member = interaction.user
        nick = member.nick if member.nick else member.name
        imageurl= requests.get(f"https://some-random-api.com/canvas/misc/youtube-comment?avatar={member.display_avatar.url}&username={nick[:25]}&comment={comment[:1000]}").content
        await interaction.send(file = nextcord.File(BytesIO(imageurl), "comment.png"))
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")
            

    @fun_filter.subcommand(name="brighten", description="Brighten filter")
    async def fun_filter_brighten(self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            name="member",
            description="Member to filter avatar",
            required=False
        ),
        brightness: int = SlashOption(
            name="brightness",
            description="brightness level (0-255)",
            required=False
        )):
        if brightness < 0 or brightness > 255:
            await interaction.send("Invalid brightness value. Must be > 0 and < 255", ephemeral=True)
            return
        if not member:
            member = interaction.user
        embed = nextcord.Embed(colour=COLOUR_MAIN)
        if not brightness:
            embed.set_image(url=f"https://some-random-api.com/canvas/brightness?avatar={member.display_avatar.url}")
        else:
            embed.set_image(url=f"https://some-random-api.com/canvas/brightness?avatar={member.display_avatar.url}?brightness={brightness}")
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @fun.subcommand(name="joke", description="Get a random joke")
    async def fun_joke(self, interaction: Interaction):
        res = requests.get(f"https://some-random-api.com/others/joke").json()
        joke = res["joke"]
        embed = nextcord.Embed(description=joke, colour=COLOUR_MAIN)
        await interaction.send(embed=embed)
        chance = random.randint(1, 3)
        if chance == 1:
            await interaction.edit_original_message(content=f"Invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)")

    @fun.subcommand(name=f"trivia", description=f"Get a trivia question")
    async def fun_trivia(self,
        interaction: Interaction,
        topic: str = SlashOption(
            name=f"topic",
            description=f"The question topic",
            choices={"Random":"random", "Arts & Literature": "arts_and_literature", "Film & TV":"film_and_tv","Food & Drink":"food_and_drink", "General Knowledge":"general_knowledge", "Geography":"geography", "History":"history", "Music":"music", "Science":"science", "Society & Culture":"society_and_culture", "Sport & Leisure":"sport_and_leisure"},
            required=False,
            default="Random"
        ),
        difficulty: str = SlashOption(
            name=f"difficulty",
            description=f"The difficulty of the question",
            choices=["All", "Easy", "Medium", "Hard"],
            required=False,
            default=f"All"
        )):
        if difficulty == "All":
            difficulty = random.choice(["easy", "medium", "hard"])
        if topic.lower() == "random":
            topic = "arts_and_literature,film_and_tv,food_and_drink,general_knowledge,geography,history,music,science,society_and_culture,sport_and_leisure"
        res = requests.get(f"https://the-trivia-api.com/api/questions?categories={topic}&limit=1&difficulty={difficulty.lower()}").json()[0]
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
        embed = nextcord.Embed(title=f"{category} Trivia Question ({difficulty.capitalize()})", description=f"{question}\n\n**Answers:**\n\n{answertext}", colour=embedcolours[difficulty.lower()])
        embed.set_footer(text=f"{questionid}")
        workview = WorkTriviaView(org_user=interaction.user.id, answers=answers)
        msg = await interaction.send(embed=embed, view=workview)
        await workview.wait()

        view = WorkTriviaView(org_user=interaction.user.id, answers=answers, selected_answer=answers[int(workview.value)-1], correct=answer)

        if answers[int(workview.value)-1] == answer:
            finishedembed = nextcord.Embed(title="Correct!", description=f"You correctly answered the trivia question!", colour=COLOUR_GOOD)

        else:
            finishedembed = nextcord.Embed(title=f"Incorrect", description=f"You got the answer wrong!\n\nThe correct answer was `{answer}`", colour=COLOUR_BAD)

        await msg.edit(embeds=[embed, finishedembed], view=view)





    

def setup(client):
    client.add_cog(cog=Fun(client=client))
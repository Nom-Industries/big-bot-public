import nextcord
import random
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from bot.bot import Bot
from PIL import Image, ImageFont, ImageDraw, ImageOps
from io import BytesIO
from constants import COLOUR_MAIN, WELCOME_MESSAGES
from utils.utils import create_warning_embed, get_user_name
import requests
from db_handler.schemas import *
from typing import List

from utils.utils import create_error_embed, create_success_embed

class Welcomer(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="welcome", description="Welcome settings")
    async def welcome(self, interaction: Interaction):
        pass

    @welcome.subcommand(name="channel", description="Set the welcome channel for your server")
    async def welcome_channel(self, interaction: Interaction, channel: nextcord.TextChannel = SlashOption(name="channel", description="Welcome channel", required=True)):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return
        
        guild_data: List[GuildMain] = Bot.db.get_data(table="guild_main", guild_id=interaction.guild.id)
        if not guild_data:
            guild_data = Bot.db.create_data(table="guild_main", guild_id=interaction.guild.id)
        
        else:
            guild_data: GuildMain = guild_data[0]
        
        guild_data.welcome_channel = channel.id
        Bot.db.update_data(table="guild_main", data=guild_data)

        await interaction.send(embed=create_success_embed(title="Success!", description=f"{channel.mention} has been set as the welcome channel for your server!"), ephemeral=True)
    
    @welcome.subcommand(name="message", description="Set a welcome message for your server (run command without a message for help)")
    async def welcome_msg(self, interaction: Interaction, message: str = SlashOption(name="message", description="Welcome message", required=False)):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return

        elif not message:
            embed = nextcord.Embed(title="Welcome Messages", description="Special symbols to use", colour=COLOUR_MAIN)
            embed.add_field(name="{$user}", value='''
            Description: Mentions a user in your message
            Usage: Hey welcome to the server {$user}!
            ''', inline=False)
            embed.add_field(name="#<channel>", value='''
            Description: Mentions a channel in your message
            Usage: Hey welcome to the server {$user}! Check out #welcome for more info!
            ''', inline=False)

            await interaction.send(embed=embed, ephemeral=True)
            return
        
        guild_data: List[GuildMain] = Bot.db.get_data(table="guild_main", guild_id=interaction.guild.id)
        if not guild_data:
            guild_data = Bot.db.create_data(table="guild_main", guild_id=interaction.guild.id)
        
        else:
            guild_data: GuildMain = guild_data[0]
        
        guild_data.welcome_msg = message
        Bot.db.update_data(table="guild_main", data=guild_data)

        await interaction.send(embed=create_success_embed(title="Success!", description=f"A welcome message has been set for your server!\nMessage:\n{message}"), ephemeral=True)
    
    @welcome.subcommand(name="disable", description="Disable the welcomer system")
    async def welcome_disable(self, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"))
            return

        data: List[GuildMain] = Bot.db.get_data(table="guild_main", guild_id=interaction.guild.id)
        if not data or data[0].welcome_channel:
            await interaction.send(embed=create_warning_embed(title="You don't have a welcome channel", description="You don't currently have welcomer set up. You can set it up using `/welcome channel` and `/welcome message`"))
            return

        data[0].welcome_channel = None
        Bot.db.update_data(table="guild_main", data=data[0])
        
        await interaction.send(embed=create_success_embed(title="Success!", description="I have successfully disabled welcomer."))

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        data: List[GuildMain] = Bot.db.get_data(table="guild_main", guild_id=member.guild.id)
        if not data or not data[0].welcome_channel:
            return
                
        channel = member.guild.get_channel(int(data[0].welcome_channel))

        while "{$" in data[0].welcome_msg:
            loc = data[0].welcome_msg.find("{$user}")
            data[0].welcome_msg = data[0].welcome_msg[:loc] + member.mention + data[0].welcome_msg[loc+7:]

        welcome_image = Image.open("assets/images/Welcome_Image.png")
        font = ImageFont.truetype("assets/fonts/Welcome_Font.ttf", size=40)
        draw = ImageDraw.Draw(welcome_image)
        
        draw.text((550, 445), (str(random.choice(WELCOME_MESSAGES)).replace("{user}", str(get_user_name(member)))), fill=(255, 255, 255), anchor="ms", font=font)
        draw.text((550, 500), f"Member #{len(member.guild.members)}", fill=(155, 155, 155), anchor="ms", font=font)

        with requests.get(member.display_avatar.with_size(512).url) as r:
            avatar = Image.open(BytesIO(r.content)).convert("RGBA")

        mask = Image.new('L', (300, 300), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 300, 300), fill=255)

        avatar = avatar.resize((300, 300))
        avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        welcome_image.paste(avatar, (400, 70), avatar)

        image_byte = BytesIO()
        welcome_image.save(image_byte, format="png")
        image_byte.seek(0)

        
        # Background file name: assets/images/Welcome_Image.png | 960px x 540px
        # Font file name: assets/fonts/Welcome_Font.ttf
        await channel.send(content=str(data[0].welcome_msg), file = nextcord.File(image_byte, f"{member.id}_{member.guild.id}.png"))

def setup(client: Bot):
    client.add_cog(cog=Welcomer(client=client))
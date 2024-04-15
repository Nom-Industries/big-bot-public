import nextcord, io
from nextcord import Interaction
from nextcord.ext import commands
from bot import Bot
from utils import *
import aiohttp
from typing import List, Union
from PIL import Image, ImageFont, ImageDraw
from views import Economy_Leaderboard_Graph
from db_handler.schemas import *
from constants import COLOUR_MAIN, COOKIE

class Leaderboards(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    async def get_lb_data(self):
        data: List[EconomyMain] = Bot.db.get_data(table="economy", guild_id="global")
        data.sort(key=lambda x: x.balance, reverse=True)
        text = ""

        for i in range(15):
            member = await self.client.fetch_user(data[i].user_id)
            name = member.name if str(member.discriminator) == "0" else member 
            text += f"`{i+1}.` `{name}` - {int(data[i].balance):,} {COOKIE}'s\n"
            data[i].user_id = member

        return data, text

    @nextcord.slash_command(name="leaderboard", description=f"Leaderboard base")
    async def leaderboard(self, interaction:Interaction):
        pass

        
    @leaderboard.subcommand(name="economy", description="View the global economy leaderboard")
    async def leaderboard_economy(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        leaderboard, lb_text = await self.get_lb_data()
        embed=nextcord.Embed(title="Leaderboard", description=lb_text, colour=COLOUR_MAIN)
        embed.set_footer(text=f"Run by {interaction.user}")
        await interaction.send(embed=embed, view=Economy_Leaderboard_Graph(leaderboard, lb_text))


    @leaderboard.subcommand(name=f"level", description=f"Shows you the levels leaderboard for the server")
    async def level(self, interaction:Interaction):
        await interaction.response.defer()

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=interaction.guild.id)
        if not maindata:
            maindata = Bot.db.create_data(table="level_main", guild_id=interaction.guild.id, enabled=False, min_xp=10, max_xp=20, level_up_message="Congratulations {$user}, you just reached level {$new_level}", drops=False)
            await interaction.send("Levelling is disabled in this guild.")
            return
        
        maindata = maindata[0]
        lb: List[LevelUsers] = Bot.db.get_data(table="level_users", guild_id=interaction.guild.id)
        lb = sorted(lb, key=lambda x: x.total_xp, reverse=True)
        unsortedlb = lb
        lb = lb[:10]
        img = Image.open(f"./big-bot/assets/images/lb/{maindata.background_color if not maindata.background_color is None else 'default'}.png")
        draw = ImageDraw.Draw(img)

        big_font = ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf', 60)
        medium_font = ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf', 40)
        small_font = ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf', 30)
        extra_small_front=ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf',10)

        def get_info(total_xp, maindata):
            if maindata.mee6_levels:
                return utils.mee_totalxp_to_level(total_xp)
            else:
                return totalxp_to_level(total_xp)

        TINT_COLOR = (3, 3, 3)
        TRANSPARENCY = .8
        OPACITY = int(255 * TRANSPARENCY)
        overlay = Image.new('RGBA', img.size, TINT_COLOR+(0,))
        draw = ImageDraw.Draw(overlay)
        for i in range(min(10, len(unsortedlb))):
            user = await self.client.fetch_user(lb[i].user_id)
            level, threshold, xp = get_info(lb[i].total_xp, maindata)
            xp_text_size = draw.textsize(f"{user} • LEVEL {level}", font=small_font)
            draw.rounded_rectangle([(120, 68*i+40), (120+xp_text_size[0], 68*i+35+50)], 10, fill=TINT_COLOR+(OPACITY,))
            draw.rounded_rectangle([(5, 68*i+40), (50+55, 68*i+35+50)], 10, fill=TINT_COLOR+(OPACITY,))
        img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)
        for i in range(min(10, len(unsortedlb))):
            user = await self.client.fetch_user(lb[i].user_id)
            colour = get_colour(i)
            level, threshold, xp = get_info(lb[i].total_xp, maindata)
            print(user.name)
            draw.text((120, 68*i+40), f"{(user.name) + (f'#{user.discriminator}' if not str(user.discriminator) == '0' else '')} • LEVEL {level}", font=small_font, fill=colour)
            if i == 9:
                draw.text((5, 68*i+40), f"#{i+1}", font=small_font, fill=colour)
            else:
                draw.text((5, 68*i+40), f" #{i+1}", font=small_font, fill=colour)
            user_avatar_image = str(user.display_avatar.with_size(512).url)
            async with aiohttp.ClientSession() as session:
                async with session.get(user_avatar_image) as resp:
                    avatar_bytes = io.BytesIO(await resp.read())
            logo = Image.open(avatar_bytes).resize((40, 40)).convert("RGBA")
            img.paste(logo, (60, 68*i+40))

        bytes = io.BytesIO()
        img.save(bytes, 'PNG')
        bytes.seek(0)
        embed = nextcord.Embed(title=f"{interaction.guild.name} leaderboard", colour=COLOUR_MAIN)
        file=nextcord.File(bytes, "lb.png")
        guild = self.client.get_guild(1015361041024155770)
        channel = guild.get_channel(1080236533426180188)
        msg = await channel.send(file=file)
        embed.set_image(url=msg.attachments[0].url)
        await interaction.send(embed=embed)

        return bytes
    

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
    client.add_cog(Leaderboards(client))

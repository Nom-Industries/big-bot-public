import nextcord, requests, json
from nextcord.ext import commands
from bot.bot import Bot
from constants import COLOUR_MAIN


class Music(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        
    
    @nextcord.slash_command(name="lyrics", description="Get the lyrics to a song")
    async def lyrics(self,
        interaction: nextcord.Interaction,
        title: str = nextcord.SlashOption(
            name="song",
            description="Name of the song",
            required=True
        )):
        await interaction.response.defer()
        response = requests.get(f"https://some-random-api.com/lyrics?title={title}")
        json_data = json.loads(response.content)
        lyrics = json_data.get('lyrics')
        if lyrics:
            song_title = json_data.get('title')
            author = json_data.get('author')
            thumbnail = json_data.get('thumbnail')
            links = json_data.get('links')
            if links:
                link = links.get('genius')
        if lyrics:
            embed = nextcord.Embed(title=f"``{song_title}`` Lyrics", description=f"[Lyrics]({link})\n{str(lyrics)[0:3500]}", colour=COLOUR_MAIN)
            embed.set_footer(text=f"Author: {author}")
            if thumbnail:
                embed.set_thumbnail(url=thumbnail.get("genius"))
            await interaction.send(embed=embed)
        else:
            await interaction.send("I was unable to find lyrics for that song.", delete_after=30)
        

def setup(client: Bot):
    client.add_cog(Music(client))
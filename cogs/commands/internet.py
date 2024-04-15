import nextcord, requests, qrcode, io
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from bot import Bot
from constants import COLOUR_MAIN
from utils import *
import matplotlib.pyplot as plt
import numpy as np
import wikipediaapi
from views.wikipedia_view import Wikipedia_Research

class Internet(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="wikipedia", description="Get information about a query")
    async def wikipedia(self,
        interaction: Interaction,
        query : str = SlashOption(
            name="query",
            description="What to search for on wikipedia",
            required=True
        )):
        await interaction.response.defer()
        wiki_wiki = wikipediaapi.Wikipedia("en")
        page_py = wiki_wiki.page(query)
        if page_py.exists():
            embed = nextcord.Embed(title=str(page_py.title)[0:250], description=f"[Wikipedia Page]({page_py.fullurl})\n\n {page_py.summary[0:3000]}", colour=COLOUR_MAIN)
            await interaction.send(embed=embed, view=Wikipedia_Research(org_user=interaction.user, org_link=page_py.fullurl))
        else:
            await interaction.send(embed=create_error_embed(title="Invalid Query", description="We couldn't find that query in wikipedia."), view=Wikipedia_Research(org_user=interaction.user))

    @nextcord.slash_command(name=f"weather", description=f"Get the weather in a specific location")
    async def weather(self, 
        interaction: nextcord.Interaction,
        place: str = SlashOption(
            name=f"place",
            description=f"Place you want to see the weather for. (City, state, etc.)",
            required=True
        ),
        temp_unit: str = SlashOption(
            name=f"temperature-unit",
            description=f"The unit to use for the temperature (Default: °C)",
            choices=["°C", "°F"],
            required=False,
            default="°C"
        )):
        if not place:
            if not interaction.locale:
                await interaction.send(embe=create_error_embed(title=f"Invalid Place", description=f"Please input a place to lookup the weather of."))
                return
            place = interaction.locale
        info = requests.get(f"http://api.weatherapi.com/v1/current.json?q={place}&key=86e01e35c0a94c1fb05160817232606").json()
        forecast = requests.get(f"http://api.weatherapi.com/v1/forecast.json?q={place}&key=86e01e35c0a94c1fb05160817232606&days=1").json()
        if temp_unit == "°C":
            embed = nextcord.Embed(title=f"{info['current']['condition']['text']} - {round(int(info['current']['temp_c']))}°C ({round(int(forecast['forecast']['forecastday'][0]['day']['maxtemp_c']))}°C :arrow_up:, {round(int(forecast['forecast']['forecastday'][0]['day']['mintemp_c']))}°C :arrow_down:)", colour=COLOUR_MAIN)
        elif temp_unit == "°F":
            embed = nextcord.Embed(title=f"{info['current']['condition']['text']} - {round(int(info['current']['temp_f']))}°F ({round(int(forecast['forecast']['forecastday'][0]['day']['maxtemp_f']))}°F :arrow_up:, {round(int(forecast['forecast']['forecastday'][0]['day']['mintemp_f']))}°F :arrow_down:)", colour=COLOUR_MAIN)
        embed.set_thumbnail(url = "https:" + str(info['current']['condition']['icon']))
        author_place = await self.create_weather_title(info)
        embed.set_author(name=f"Weather in {author_place}")
        embed.description=f"Local Time: {info['location']['localtime']}\nWind Speed (kph): {info['current']['wind_kph']}\nWind Speed (mph): {info['current']['wind_mph']}\nWind Direction: {info['current']['wind_dir']}\nHumidity: {info['current']['humidity']}\nVisibility (km): {info['current']['vis_km']}\nVisibility (miles): {info['current']['vis_miles']}"
        day_forecast_value = await self.create_day_forecast_value(info, forecast, temp_unit)
        embed.add_field(name=f"Day Forecast", value=day_forecast_value)
        await interaction.send(embed=embed, ephemeral=True)

    @nextcord.slash_command(name="time", description="Get the time of a specific location")
    async def get_time(self,
        interaction: nextcord.Interaction,
        place: str = SlashOption(
            name="place",
            description="The place you want to see the time of",
            required=True        
        )):
        data = requests.get(f"http://api.weatherapi.com/v1/current.json?q={place}&key=86e01e35c0a94c1fb05160817232606").json()
        author_place = await self.create_weather_title(data)
        embed = nextcord.Embed(title=f"Time in {author_place}", description=f"Date (YYYY-MM-DD): {data['location']['localtime'].split(' ')[0]}\n\nTime: {data['location']['localtime'].split(' ')[1]}")
        localtime = data['location']['localtime'].split(' ')[1]
        bytes = await self.generate_clock_face(localtime=localtime)
        file=nextcord.File(bytes, "lb.png")
        guild = self.client.get_guild(1015361041024155770)
        channel = guild.get_channel(1080236533426180188)
        msg = await channel.send(file=file)
        embed.set_image(url=msg.attachments[0].url)
        await interaction.send(embed=embed, ephemeral=True)

    @nextcord.slash_command("qrcode", description="Generate a QR Code for a custom link")
    async def qrcode(self, interaction: Interaction,
        links: str = SlashOption(
            name="link",
            description="Link to redirect to",
            required=True
        )):
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(links)
        qr.make(fit=True)

        image = qr.make_image(fill_color=(67, 161, 232), back_color="white")

        bytes = io.BytesIO()
        image.save(bytes, 'PNG')
        bytes.seek(0)
        await interaction.send(file=nextcord.File(bytes, "QRCode.png"), ephemeral=True)

    
    @staticmethod
    async def create_weather_title(info):
        title = ""
        title+=f"{info['location']['name']}, " if info['location']['name'] else ""
        title+=f"{info['location']['region']}, " if info['location']['region'] else ""
        title+=f"{info['location']['country']}" if info['location']['country'] else ""
        return title

    @staticmethod
    async def create_day_forecast_value(info, forecast, unit):
        current_hour = str(info['location']['localtime'])[11:13]
        day_forecast = ""
        for hour in forecast['forecast']['forecastday'][0]['hour']:
            if unit == "°C":
                if not str(hour['time'])[11:13] == current_hour:
                    day_forecast+=f"\n{str(hour['time'])[11:]} - {hour['condition']['text']} - {hour['temp_c']}°C"
                else:
                    day_forecast+=f"\n**{str(hour['time'])[11:]} - {hour['condition']['text']} - {hour['temp_c']}°C**"
            else:
                if not str(hour['time'])[11:13] == current_hour:
                    day_forecast+=f"\n{str(hour['time'])[11:]} - {hour['condition']['text']} - {hour['temp_f']}°F"
                else:
                    day_forecast+=f"\n**{str(hour['time'])[11:]} - {hour['condition']['text']} - {hour['temp_f']}°F**"
        
        return day_forecast
    
    @staticmethod
    async def generate_clock_face(localtime):
        hour, minute = localtime.split(":")
        hour = int(hour) % 12
        minute = int(minute) % 60

        hour_angle = (hour + minute / 60) * 30
        minute_angle = minute * 6

        plt.plot([0.5, 0.5 + 0.3 * np.cos(np.radians(90 - hour_angle))],
                [0.5, 0.5 + 0.3 * np.sin(np.radians(90 - hour_angle))], color='black', linewidth=4)
        plt.plot([0.5, 0.5 + 0.4 * np.cos(np.radians(90 - minute_angle))],
                [0.5, 0.5 + 0.4 * np.sin(np.radians(90 - minute_angle))], color='black', linewidth=2)

        for hour in range(1, 13):
            angle = np.radians(90 - (hour * 30))
            x = 0.5 + 0.4 * np.cos(angle)
            y = 0.5 + 0.4 * np.sin(angle)
            plt.text(x, y, str(hour), ha='center', va='center', fontsize=12)

        plt.axis('off')
        plt.axis('equal')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.gcf().set_size_inches(4, 4)
        plt.gcf().add_axes([0, 0, 1,1], frameon=False, xticks=[], yticks=[])

        bytes = io.BytesIO()
        plt.savefig(bytes, format="PNG")
        plt.close()
        bytes.seek(0)
        return bytes

def setup(client: Bot):
    client.add_cog(cog=Internet(client=client))
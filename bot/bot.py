import nextcord
import json, asyncio
import os
from nextcord.ext import commands, tasks
from utils.utils import *
from constants import DB_API_KEY, TOKEN, TOKEN_GAMMA
from db_handler.handler import Handler

class Bot(commands.AutoShardedBot):
    db = Handler(DB_API_KEY)
    def __init__(self):
        intents = nextcord.Intents.all()
        intents.presences = False
        super().__init__(shard_count=2, command_prefix="nom!", intents=nextcord.Intents.all())
        self.unloaded_cogs = []

    def initialize(self):
        os.system("cls")
        print(color_message(message='''
__________.__         __________        __   
\______   \__| ____   \______   \ _____/  |_ 
 |    |  _/  |/ ___\   |    |  _//  _ \   __\\
 |    |   \  / /_/  >  |    |   (  <_> )  |  
 |______  /__\___  /   |______  /\____/|__|  
        \/  /_____/           \/
''', color="yellow"))
        print(color_message(message="Bot has started", color="green"))
        self.load_extensions()
        self.run(TOKEN_GAMMA)
    
    def load_extensions(self):
        for folder in os.listdir("./cogs"):
            for cog in os.listdir(f"./cogs/{folder}"):
                if cog.endswith(".py"):
                    try:
                        self.load_extension(name=f"cogs.{folder}.{cog[:-3]}")
                        print(color_message(message=f"Loaded {cog[:-3]} cog", color="blue"))

                    except Exception as e:
                        print(e)
                        print(color_message(message=f"Failed to load {cog[:-3]} cog", color="yellow"))
                        self.unloaded_cogs.append(cog.capitalize()[-3])
    
    async def on_ready(self):
        print(color_message(message=f"Logged in as {self.user}!", color="green"))
        print(self.shards)
        for shard in self.shards:
            await self.change_presence(status=nextcord.Status.online, activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=f"nom! | Shard: {shard+1}/{len(self.shards)}"), shard_id=shard)

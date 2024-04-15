import nextcord, asyncio, random, ast, io
from nextcord.ext import commands, tasks
from bot import Bot
from utils import *
import time, aiohttp
from PIL import Image, ImageFont, ImageDraw
from typing import List, Union
from db_handler.schemas import *
from nextcord.errors import *

first = True

class LevellingManager(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
        self.voice_levelling_manager.start(client)


    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot or not message.guild:
            return

        
        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=message.guild.id)
        if not maindata:
            return
        maindata = maindata[0]
        if not maindata.enabled:
            return
        
        mee6_levels = maindata.mee6_levels

        cooldownTime = maindata.cooldown if maindata.cooldown is not None else 30

        #NO XP CHANNEL HANDLER
        if maindata.no_xp_channels is None:
            pass
        elif not "[" in maindata.no_xp_channels:
            pass
        else:
            maindata.no_xp_channels = ast.literal_eval(maindata.no_xp_channels)
            if message.channel.id in maindata.no_xp_channels:
                return
            
        #NO XP ROLE HANDLER    
        if maindata.no_xp_roles is None:
            pass
        elif not "[" in maindata.no_xp_roles:
            pass
        else:
            maindata.no_xp_roles = ast.literal_eval(maindata.no_xp_roles)
            for role in message.author.roles:
                if role.id in maindata.no_xp_roles:
                    return

        userdata: List[LevelUsers] = Bot.db.get_data(table="level_users", unique_id=f"{message.guild.id}-{message.author.id}")
        if not userdata:
            userdata = Bot.db.create_data(table="level_users", unique_id=f"{message.guild.id}-{message.author.id}", guild_id=message.guild.id, user_id=message.author.id, total_xp=0)
        else:
            userdata = userdata[0]

        old_total_xp = userdata.total_xp

        user_last_earned = userdata.last_xp_gain

        current_time = round(time.time())

        if (
            not user_last_earned is None
            and not current_time - user_last_earned > cooldownTime
        ):
            return
        # CHANNEL AND ROLE XP BOOST HANDLER
        role_xp_boost: List[LevelBonusRoles] = Bot.db.get_data(table="level_bonus_roles",guild_id=message.guild.id)
        if not role_xp_boost:
            role_xp_boost =[]
        else:
            role_xp_boost.sort(key=lambda r: r.boost, reverse=True)
        channel_xp_boost: List[LevelBonusChannels] = Bot.db.get_data(table="level_bonus_channels",guild_id=message.guild.id,channel_id=message.channel.id)
        channel_multiplier = 0
        role_multiplier = 0
        if channel_xp_boost:
            print(channel_xp_boost)
            channel_multiplier += channel_xp_boost[0].boost
            

        for boost_role in role_xp_boost:
            try:
                role = message.guild.get_role(boost_role.role_id)
                if role in message.author.roles:
                    role_multiplier += boost_role.boost
                    break
            except Exception as e:
                print(e + "CHAT XP")
                pass


        
        multiplier = role_multiplier + channel_multiplier
        xp_to_give = random.randint(int(maindata.min_xp), int(maindata.max_xp)) * (1+multiplier/100)

        if maindata.drops:
            chance = random.randint(0, 200)
            if chance <= 1:
                xp = random.randint(50, 200)
                await message.channel.send(f"[**XP DROP**] {message.author.mention} received {xp} XP from an XP drop!")
                userdata.total_xp += xp

        new_total_xp = userdata.total_xp + xp_to_give
        if not mee6_levels:
            old_level, old_threshold, old_xp = totalxp_to_level(old_total_xp)
            new_level, new_threshold, new_xp = totalxp_to_level(new_total_xp)
        else:
            old_level, old_threshold, old_xp = utils.mee_totalxp_to_level(old_total_xp)
            new_level, new_threshold, new_xp = utils.mee_totalxp_to_level(new_total_xp)
        userdata.total_xp += xp_to_give
        userdata.last_xp_gain = round(time.time())
        Bot.db.update_data(table="level_users", data=userdata)
        if not old_level == new_level:
            try:
                if maindata.level_up_channel == "current":
                    channel = message.channel
                elif maindata.level_up_channel is None:
                    return
                else:
                    channel = message.guild.get_channel(int(maindata.level_up_channel))
    
                messagesend = str(maindata.level_up_message).replace("{$user}", message.author.mention).replace("{$new_level}", str(new_level).replace("{$old_level}", str(old_level))).replace("{$new}", str(new_level).replace("{$old}", str(old_level)))
                bytes = await generate_level_up_image(message.author, message.guild, old_level, new_level, maindata.background_color)
            except Exception as e:
                print(e)
            try:
                roledata: List[LevelRoles] = Bot.db.get_data(table="level_roles", guild_id=message.guild.id)
                roledata = roledata
                rolestoadd = []
                roles = []
                highest_level = 0
                for reward in roledata:
                    role = message.guild.get_role(reward.role_id)
                    print(role)
                    roles.append(role)
                    if reward.level <= new_level:
                        try:
                            if maindata.stackable_rewards:
                                rolestoadd.append(role)
                            else:
                                if reward.level > highest_level:
                                    rolestoadd = [role]
                                    highest_level = reward.level
                        except Exception as e:
                            print(e)
                            pass
                    if reward.level == new_level and not maindata.reward_message is None:
                        role = message.guild.get_role(reward.role_id)
                        messagesend = str(maindata.reward_message).replace("{$user}", message.author.mention).replace("{$new_level}", str(new_level).replace("{$old_level}", str(old_level))).replace("{$new}", str(new_level)).replace("{$old}", str(old_level)).replace("{$role}", str(role.mention))
                if maindata.stackable_rewards:
                    await message.author.add_roles(*rolestoadd,atomic=False)
                else:
                    index = roles.index(rolestoadd[0])
                    del roles[index]
                    await message.author.remove_roles(*roles,atomic=False)
                    await message.author.add_roles(rolestoadd[0])
                    print(rolestoadd)
            except Exception as e:
                print(e)
                pass
            if not maindata.level_up_channel is None:
                await channel.send(messagesend, file=nextcord.File(bytes, "card.png"), allowed_mentions=nextcord.AllowedMentions(everyone=False, users=True, roles=False))

    @tasks.loop(minutes=1)
    async def voice_levelling_manager(self, client):
        print("voice loop started")
        await client.wait_until_ready()
        global first
        if first:
            print("waiting")
            await asyncio.sleep(30)
            first = False
        try:
            for guild in client.guilds:
                for channel in guild.channels:
                    if channel.type == nextcord.ChannelType.voice:
                        if len(channel.members) == 0:
                            pass
                        else:
                            stoping = False
                            maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=channel.guild.id)
                            if maindata:
                                maindata = maindata[0]
                                if maindata.no_xp_channels is None:
                                    pass
                                elif not "[" in maindata.no_xp_channels:
                                    pass
                                else:
                                    maindata.no_xp_channels = ast.literal_eval(maindata.no_xp_channels)
                                    if channel.id in maindata.no_xp_channels:
                                        stoping = True
                            if not stoping:
                                if len(channel.members) >=2:
                                    members_valid = []
                                    for member in channel.members:
                                        print(members_valid)
                                        if member.bot:
                                            pass
                                        elif member.voice.deaf or member.voice.mute or member.voice.self_mute or member.voice.self_deaf or member.voice.suppress:
                                            pass
                                        else:
                                            members_valid.append(member)
                                            if maindata:
                                                if maindata.no_xp_roles is None:
                                                    pass
                                                elif not "[" in maindata.no_xp_roles:
                                                    pass
                                                else:
                                                    maindata.no_xp_roles = ast.literal_eval(maindata.no_xp_roles)
                                                    for role in member.roles:
                                                        if role.id in maindata.no_xp_roles:
                                                            index = members_valid.index(member.id)
                                                            del members_valid[index]
                                    if len(members_valid) >= 2:
                                        print("count reached")
                                        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=channel.guild.id)
                                        if not maindata:
                                            pass
                                        else:
                                            maindata = maindata[0]
                                            if not maindata.enabled:
                                                pass
                                            else:
                                                for member in members_valid:
                                                    # CHANNEL AND ROLE XP BOOST HANDLER
                                                    mee6_levels = maindata.mee6_levels
                                                    role_xp_boost: List[LevelBonusRoles] = Bot.db.get_data(table="level_bonus_roles",guild_id=guild.id)
                                                    role_xp_boost.sort(key=lambda r: r.boost, reverse=True)
                                                    channel_xp_boost: List[LevelBonusChannels] = Bot.db.get_data(table="level_bonus_channels",guild_id=guild.id,channel_id=channel.id)
                                                    channel_multiplier = 0
                                                    role_multiplier = 0
                                                    if channel_xp_boost:
                                                        print(channel_xp_boost)
                                                        channel_multiplier += channel_xp_boost[0].boost

                                                    for boost_role in role_xp_boost:
                                                        try:
                                                            role = guild.get_role(boost_role.role_id)
                                                            if role in member.roles:
                                                                role_multiplier += boost_role.boost
                                                                break
                                                        except Exception as e:
                                                            print(e + "VOICE HERE")
                                                            pass

                                                    multiplier = role_multiplier + channel_multiplier
                                                    xp_to_give = random.randint(int(maindata.min_vc_xp), int(maindata.max_vc_xp)) * (1+multiplier/100)
                                                    userdata: List[LevelUsers] = Bot.db.get_data(table="level_users", unique_id=f"{channel.guild.id}-{member.id}")
                                                    if not userdata:
                                                        userdata = Bot.db.create_data(table="level_users", unique_id=f"{channel.guild.id}-{member.id}", guild_id=channel.guild.id, user_id=member.id, total_xp=0)
                                                    else:
                                                        userdata = userdata[0]
                                                    old_total_xp = userdata.total_xp
                                                    new_total_xp = userdata.total_xp + xp_to_give
                                                    if not mee6_levels:
                                                        old_level, old_threshold, old_xp = totalxp_to_level(old_total_xp)
                                                        new_level, new_threshold, new_xp = totalxp_to_level(new_total_xp)
                                                    else:
                                                        old_level, old_threshold, old_xp = utils.mee_totalxp_to_level(old_total_xp)
                                                        new_level, new_threshold, new_xp = utils.mee_totalxp_to_level(new_total_xp)
                                                    userdata.total_xp += xp_to_give
                                                    Bot.db.update_data(table="level_users", data=userdata)
                                                    if not old_level == new_level:
                                                        try:
                                                            if maindata.level_up_channel == "current":
                                                                channel = channel
                                                            elif maindata.level_up_channel is None:
                                                                return
                                                            else:
                                                                channel = guild.get_channel(maindata.level_up_channel)
                                                
                                                            messagesend = str(maindata.level_up_message).replace("{$user}", member.mention).replace("{$new_level}", str(new_level).replace("{$old_level}", str(old_level))).replace("{$new}", str(new_level).replace("{$old}", str(old_level)))
                                                            bytes = await generate_level_up_image(member, guild, old_level, new_level, maindata.background_color)
                                                        except Exception as e:
                                                            print(e)
                                                        try:
                                                            roledata: List[LevelRoles] = Bot.db.get_data(table="level_roles", guild_id=guild.id)
                                                            roledata = roledata
                                                            rolestoadd = []
                                                            roles = []
                                                            highest_level = 0
                                                            for reward in roledata:
                                                                role = guild.get_role(reward.role_id)
                                                                print(role)
                                                                roles.append(role)
                                                                if reward.level <= new_level:
                                                                    try:
                                                                        if maindata.stackable_rewards:
                                                                            rolestoadd.append(role)
                                                                        else:
                                                                            if reward.level > highest_level:
                                                                                rolestoadd = [role]
                                                                                highest_level = reward.level
                                                                    except Exception as e:
                                                                        print(e)
                                                                        pass
                                                                if reward.level == new_level and not maindata.reward_message is None:
                                                                    role = guild.get_role(reward.role_id)
                                                                    messagesend = str(maindata.reward_message).replace("{$user}", member.mention).replace("{$new_level}", str(new_level).replace("{$old_level}", str(old_level))).replace("{$new}", str(new_level)).replace("{$old}", str(old_level)).replace("{$role}", str(role.name))
                                                            if maindata.stackable_rewards:
                                                                await member.add_roles(*rolestoadd,atomic=False)
                                                            else:
                                                                index = roles.index(rolestoadd[0])
                                                                del roles[index]
                                                                await member.remove_roles(*roles,atomic=False)
                                                                await member.add_roles(rolestoadd[0])
                                                                print(rolestoadd)
                                                        except Exception as e:
                                                            print(e)
                                                            pass
                                                        if not maindata.level_up_channel is None:
                                                            await channel.send(messagesend, file=nextcord.File(bytes, "card.png"), allowed_mentions=nextcord.AllowedMentions(everyone=False, users=True, roles=False))
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        maindata: List[LevelMain] = Bot.db.get_data(table="level_main", guild_id=member.guild.id)
        if not maindata:
            return
        maindata = maindata[0]
        if not maindata.enabled:
            return
        
        mee6_levels = maindata.mee6_levels

        userdata: List[LevelUsers] = Bot.db.get_data(table="level_users", unique_id=f"{member.guild.id}-{member.id}")
        if not userdata:
            return
        else:
            userdata = userdata[0]

        total_xp = userdata.total_xp

        if not mee6_levels:
            new_level, new_threshold, new_xp = totalxp_to_level(total_xp)
        else:
            new_level, new_threshold, new_xp = utils.mee_totalxp_to_level(total_xp)

        roledata: List[LevelRoles] = Bot.db.get_data(table="level_roles", guild_id=member.guild.id)
        roledata = roledata
        rolestoadd = []
        roles = []
        highest_level = 0
        for reward in roledata:
            role = member.guild.get_role(reward.role_id)
            roles.append(role)
            if reward.level <= new_level:
                try:
                    if maindata.stackable_rewards:
                        rolestoadd.append(role)
                    else:
                        if reward.level > highest_level:
                            rolestoadd = [role]
                            highest_level = reward.level
                except Exception as e:
                    print(e)
                    pass
        if len(rolestoadd) == 0:
            return
        if maindata.stackable_rewards:
            await member.add_roles(*rolestoadd,atomic=False)
        else:
            index = roles.index(rolestoadd[0])
            del roles[index]
            await member.add_roles(rolestoadd[0])



async def generate_level_up_image(member, guild, oldlevel, newlevel, bg_colour):
    user_avatar_image = str(member.display_avatar.with_size(64).url)
    async with aiohttp.ClientSession() as session:
        async with session.get(user_avatar_image) as resp:
            avatar_bytes = io.BytesIO(await resp.read())

    if bg_colour is None:
        bg_colour = "default"
        
    img = Image.open(f"./big-bot/assets/images/levelup/{bg_colour}.png")
    logo = Image.open(avatar_bytes).resize((64, 64)).convert("RGBA")
    # Stack overflow helps :)
    bigsize = (logo.size[0] * 3, logo.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(logo.size, Image.ANTIALIAS)
    logo.putalpha(mask)
    ##############################
    img.paste(logo, (5, 5), mask=logo)

    draw = ImageDraw.Draw(img)

    # Working with fonts
    medium_font = ImageFont.FreeTypeFont('./big-bot/assets/fonts/font.ttf', 34)
    arrow_font=ImageFont.FreeTypeFont('./big-bot/assets/fonts/levelupfont.ttf',30)


    def convert_int(integer):
        if integer>=1000:
            integer = round(integer / 1000, 2)
            return f'{integer}K'
        else:
            return integer

    # Placing Level Up Text
    text = 'Level Up!'
    text_size = draw.textsize(text, font=medium_font)
    offset_x = 250 - 20 - text_size[0]
    offset_y = -5
    draw.text((offset_x,offset_y),text,font=medium_font, fill='#ffffff')

    #Placing Level Text
    text = f'{oldlevel} → {newlevel}'
    text_size = draw.textsize(text, font=arrow_font)
    offset_x = 160
    offset_y = 65
    draw.text((offset_x,offset_y),text,font=arrow_font, fill='#ffffff', anchor='ms')

    bytes = io.BytesIO()
    img.save(bytes, 'PNG')
    bytes.seek(0)
    return bytes


def setup(client: Bot):
    client.add_cog(cog=LevellingManager(client=client))

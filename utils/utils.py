from constants import COLORS, COLOUR_GOOD, COLOUR_NEUTRAL, COLOUR_BAD, COLOUR_MAIN
import nextcord, math, random
from string import ascii_letters, digits


#     cur = conn.cursor()
#     return conn, cur

def color_message(message: str, color: str = COLORS["default"]):
    color = COLORS.get(color, COLORS["default"])
    return color + message + "\033[0m"

def create_success_embed(title: str = "\u200b", description: str = "\u200b"):
    embed = nextcord.Embed(title=title, description=description, color=COLOUR_GOOD)
    embed.set_thumbnail(url="https://media.tenor.com/AWKzZ19awFYAAAAi/checkmark-transparent.gif")
    return embed

def create_warning_embed(title: str = "\u200b", description: str = "\u200b"):
    embed = nextcord.Embed(title=title, description=description, color=COLOUR_NEUTRAL)
    embed.set_thumbnail(url="https://c.tenor.com/26pNa498OS0AAAAi/warning-joypixels.gif")
    return embed

def create_error_embed(title: str = "\u200b", description: str = "\u200b"):
    embed = nextcord.Embed(title=title, description=description, color=COLOUR_BAD)
    embed.set_thumbnail(url="https://media.tenor.com/Gbp8h-dqDHkAAAAi/error.gif")
    return embed

def totalxp_to_level(total_xp):
    level = (-1 + math.sqrt(1 + 4*(total_xp // 50))) // 2
    threshold = (level+1)*100
    xp=total_xp - 50*(level**2 + level)
    return round(level), round(threshold), round(xp)

def mee_totalxp_to_level(total_xp):
    n = 0
    creq = 0
    xpl = total_xp
    while True:
        lvlreq = 5*(n**2) + 50*n + 100
        if xpl < lvlreq:
            progression = total_xp - creq
            return n, lvlreq, progression
        xpl = xpl - lvlreq
        creq = creq + lvlreq
        n = n + 1
    

def mee_lvl_to_xp(lvl):
    xp = 0
    for i in range(lvl):
        xp = 5*(i**2) + 50*i + 100 + xp
    return xp

def level_to_totalxp(level):
    return 100*(level*(level+1))/2

def generate_random_string(length: int = 0):
    return ''.join([random.choice(ascii_letters+digits) for i in range(length if length else random.randint(5, 10))])

def get_user_name(user):
    if str(user.discriminator) != "0":
        return user
    return str(user.name)

def duration_input_to_text(durationinput):
    try:
        if durationinput[-1] == "s":
            duration=int(int(durationinput[:-1]))
        elif durationinput[-1] == "m":
            duration = int(int(durationinput[:-1])*60)
        elif durationinput[-1] == "h":
            duration = int(int(durationinput[:-1])*3600)
        elif durationinput[-1] == "d":
            duration = int(int(durationinput[:-1])*86400)
        elif durationinput [-1] == "M":
            duration = int(int(durationinput[:-1])*2629746)
        elif durationinput[-2] =="mo":
            duration = int(int(durationinput[:-2])*2629746)
        elif durationinput[-1] == "y":
            duration=int(int(durationinput[:-1])*31556952)
        else:
            duration = "ERROR"
    except:
        duration = "ERROR"
    return duration
from typing import Text, Dict
from db_handler.schemas import *

TOKEN: Text = ""
VOTELINK: Text = "https://top.gg/bot/1016198853306884126/vote"

COLORS: Dict[str, str] = {"red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m", "blue": "\033[34m", "default": "\033[37m"}

NEXTCORD_PERM_LABELS = ['Create Instant Invite', 'Kick Members', 'Ban Members', 'Administrator', 'Manage Channels', 'Manage Guild', 'Add Reactions', 'View Audit Log', 'Priority Speaker', 'Stream', 'Read Messages', 'Send Messages', 'Send Tts Messages', 'Manage Messages', 'Embed Links', 'Attach Files', 'Read Message History', 'Mention Everyone', 'External Emojis', 'View Guild Insights', 'Connect', 'Speak', 'Mute Members', 'Deafen Members', 'Move Members', 'Use Voice Activation', 'Change Nickname', 'Manage Nicknames', 'Manage Roles', 'Manage Webhooks', 'Manage Emojis', 'Use Slash Commands', 'Request To Speak', 'Manage Events', 'Manage Threads', 'Create Public Threads', 'Create Private Threads', 'External Stickers', 'Send Messages In Threads', 'Start Embedded Activities', 'Moderate Members']
NEXTCORD_PERM_VALUES = ['create_instant_invite', 'kick_members', 'ban_members', 'administrator', 'manage_channels', 'manage_guild', 'add_reactions', 'view_audit_log', 'priority_speaker', 'stream', 'read_messages', 'send_messages', 'send_tts_messages', 'manage_messages', 'embed_links', 'attach_files', 'read_message_history', 'mention_everyone', 'external_emojis', 'view_guild_insights', 'connect', 'speak', 'mute_members', 'deafen_members', 'move_members', 'use_voice_activation', 'change_nickname', 'manage_nicknames', 'manage_roles', 'manage_webhooks', 'manage_emojis', 'use_slash_commands', 'request_to_speak', 'manage_events', 'manage_threads', 'create_public_threads', 'create_private_threads', 'external_stickers', 'send_messages_in_threads', 'start_embedded_activities', 'moderate_members']

RPS_CHOICES = ["Rock", "Paper", "Scissors"]
LOGGING_TYPES_LABELS = ["Message Logs", "Role Logs", "Member Logs", "Voice Logs", "Channel Logs", "Invite Logs", "User Logs"]
LOGGING_TYPES_VALUES = ["message", "role", "member", "voice", "channel", "invite", "user"]

LOGGING_TYPE_DBID = {
    "message":1,
    "role":2,
    "member":3,
    "voice":4,
    "channel":5,
    "invite":6,
    "user":7
}

COLOUR_MAIN = 0x43a1e8
COLOUR_GOOD = 0x03C04A
COLOUR_NEUTRAL = 0xFCAE1E
COLOUR_BAD = 0x900D09

BACKSLASH = '\n'

COOKIE = "🍪"

DBENDPOINT = ""
DBUSER = ""
DBPASS = ""
DBNAME = ""
DBPORT = 3306
DB_API_KEY = ""

NAME_TO_SCHEMA = {
    "guild_main": ("/guild/main/", GuildMain),
    "serverstats": ("/guild/stats/", ServerstatsMain),
    "guild_mod": ("/guild/mod/logs/", GuildMod),
    "logging": ("/guild/logging/", LoggingMain),
    "economy": ("/economy/", EconomyMain),
    "economy_user_settings": ("/economy/settings/", EconomyUserSettings),
    "tickets": ("/support/tickets", CurrentTickets),
    "autothread": ("/auto_threads/", AutoThreadMain),
    "sticky": ("/sticky_messages/", StickyMain),
    "support": ("/support/config", SupportMain),
    "ticket_blacklist": ("support/blacklists/", TicketBlacklists),
    "voice": ("/private_voice/channels", VoiceChannels),
    "voice_config": ("/private_voice/config", VoiceChannelsMain),
    "giveaway": ("/giveaway/", GiveawayMain),
    "giveaway_blocked": ("/giveaway/blocked/", GiveawayBlocked),
    "giveaway_booster": ("/giveaway/booster/", GiveawayBoosters),
    "suggestions": ("/suggestions/", SuggestionsMain),
    "suggestions_info": ("/suggestions/info/", SuggestionsInfo),
    "nickname_config": ("/nickname/config/", NicknameMain),
    "nickname_requests": ("/nickname/request/", NicknameRequests),
    "reaction_roles": ("/reaction_roles/", ReactionMain),
    "level_main": ("/levels/config/", LevelMain),
    "level_users": ("/levels/user/", LevelUsers),
    "level_roles": ("/levels/roles/", LevelRoles),
    "level_bonus_roles": ("/levels/boosts/roles/",LevelBonusRoles),
    "level_bonus_channels": ("/levels/boosts/channels/",LevelBonusChannels),
    "application_questions": ("/applications/application/", ApplicationQuestions),
    "application_responses": ("/applications/responses/", ApplicationAnswers),
    "autopublish": ("/autopublish/", Autopublish),
    "reminders": ("/reminders/", RemindersBase),
    "moderation_main": ("/guild/mod/main/", ModerationMain),
    "giveaway_temp_boosters": ("/giveaway/temp_booster/", GiveawayTempBoosterBase),
    "user_statistics": ("/user_statistics/", UserStatisticsBase)
}

ECONOMY_TIPS = [
    "**Tip:** Hunting Rifles, Hunting Spears, Fishing Rods, Spades. Drills, and computers have a chance of breaking when using their specific commands!",
    "**Tip:** You can use poison and bait to boost your chances of catching something in the hunt and fish commands",
    "**Tip:** A minion will generate 1 cookie every 10 seconds but it costs 100,000 cookies to buy!",
    "**Tip:** The permanent +0.01 boost will increase in price every time you buy a new one",
    "**Tip:** You can use </task all:1060300525138083920> to go through all money making commands more easily",
    "**Tip:** You can share cookies with friends using </share:1060300367780397136>",
    "**Tip:** You can invite me to your own server [here](<https://nomindustries.com/bigbot/invite>)"
]

POSSIBLEITEMS = ["spear", "rifle", "comp", "p_trophy", "r_trophy", "sr_trophy", "smr_trophy", "simr_trophy", "rod", "norm_boost", "bait", "minion", "yeast", "pedestal", "energy", "poison", "spade", "drill"]

POSSIBLEITEMSINFO = {
    "spear": {"db_id":6, "id":"spear", "max":50, "name":"Hunting Spear", "cost": 1000, "description":"Allows you to use the hunt command with a 50% success rate"},
    "rifle": {"db_id":7,"id":"rifle", "max":50, "name":"Hunting Rifle", "cost": 2500, "description":"Allows you to use the hunt command with an 80% success rate"},
    "comp": {"db_id":18,"id":"comp", "max":25, "name":"Computer", "cost": 5600, "description":"Gives you access to the invest command and the postvideo command"},
    "spade": {"db_id":28, "id":"spade", "max":50, "name":"Spade", "cost":1000, "description":"Gives you access to 4 mines in the dig command"},
    "drill": {"db_id":29, "id":"drill", "max":50, "name":"Drill", "cost":5000, "description":"Gives you access to 8 mins in the dig command"},
    "p_trophy": {"db_id":12,"id":"p_trophy", "max":1, "name":"Poor Trophy", "cost": 1, "description":"Shows that you're... well... poor"},
    "r_trophy": {"db_id":13,"id":"r_trophy", "max":1, "name":"Rich Trophy", "cost": 100000, "description":"Allows you to flex that you are rich"},
    "sr_trophy": {"db_id":14,"id":"sr_trophy", "max":1, "name":"Super Rich Trophy", "cost": 1000000, "description":"Allows you to flex that you are super rich"},
    "smr_trophy": {"db_id":15,"id":"smr_trophy", "max":1, "name":"Super Mega Rich Trophy", "cost": 10000000, "description":"Allows you to flex that you are super mega rich"},
    "simr_trophy": {"db_id":16,"id":"simr_trophy", "max":1, "name":"Super Insanely Mega Rich Trophy", "cost": 100000000, "description":"Allows you to flex that you are super insanely mega rich"},
    "rod": {"db_id":17,"id":"rod", "max":50, "name":"Fishing Rod", "cost":1200, "description":"Allows you to use the fish command with a 50% success rate"},
    "norm_boost": {"db_id":19,"id":"norm_boost", "max":100, "name":"Permanent +0.01 boost", "cost":None, "description":"Boosts the income you get on some commands by +0.01"},
    "bait": {"db_id":21,"id":"bait", "max":1000, "name":"Bait", "cost":5, "description":"Boosts your chance of catching a fish when doing the fish command to 80%. Used up when you use the fish command"},
    "minion": {"db_id":8, "id":"minion", "max":1, "name":"Minion", "cost":100000, "description":"Collects 1 🍪 per minute that you can claim using minion commands"},
    "yeast": {"db_id":24, "id":"yeast", "max":1000, "name":"Yeast", "cost":5, "description":"Allows you to get more 🍪's from the nom command! Used up on nom command usage."},
    "pedestal":{"db_id":25, "id":"pedestal", "max":50, "name":"Praying Pedestal", "cost":3000, "description":"Boosts your income from the pray command."},
    "energy":{"db_id":26, "id":"energy", "max":500, "name":"Energy Drink", "cost":25, "description":"Increases the income from using the work command."},
    "poison":{"db_id":27, "id":"poison", "max":750, "name":"Poison", "cost":10, "description":"Increase the income from using the hunt command and decrease the chance of not catching anything when using the hunt command. Used up on use"}
}
SHOPITEMS = ["spear", "rifle", "comp", "p_trophy", "r_trophy", "sr_trophy", "smr_trophy", "simr_trophy", "rod", "norm_boost", "bait", "minion", "yeast", "pedestal", "energy", "poison", "spade", "drill"]

SHOPITEMINFO = {
    "spear": {"db_id":6, "id":"spear", "max":50, "name":"Hunting Spear", "cost": 1000},
    "rifle": {"db_id":7,"id":"rifle", "max":50, "name":"Hunting Rifle", "cost": 2500},
    "comp": {"db_id":18,"id":"comp", "max":25, "name":"Computer", "cost": 5600},
    "spade": {"db_id":28, "id":"spade", "max":50, "name":"Spade", "cost":1000},
    "drill": {"db_id":29, "id":"drill", "max":50, "name":"Drill", "cost":5000},
    "p_trophy": {"db_id":12,"id":"p_trophy", "max":1, "name":"Poor Trophy", "cost": 1},
    "r_trophy": {"db_id":13,"id":"r_trophy", "max":1, "name":"Rich Trophy", "cost": 100000},
    "sr_trophy": {"db_id":14,"id":"sr_trophy", "max":1, "name":"Super Rich Trophy", "cost": 1000000},
    "smr_trophy": {"db_id":15,"id":"smr_trophy", "max":1, "name":"Super Mega Rich Trophy", "cost": 10000000},
    "simr_trophy": {"db_id":16,"id":"simr_trophy", "max":1, "name":"Super Insanely Mega Rich Trophy", "cost": 100000000},
    "rod": {"db_id":17,"id":"rod", "max":50, "name":"Fishing Rod", "cost":1200},
    "norm_boost": {"db_id":19,"id":"norm_boost", "max":100, "name":"Permanent +0.01 boost", "cost":None},
    "bait": {"db_id":21,"id":"bait", "max":1000, "name":"Bait", "cost":5},
    "minion": {"db_id":8, "id":"minion", "max":1, "name":"Minion", "cost":100000},
    "yeast": {"db_id":24, "id":"yeast", "max":1000, "name":"Yeast", "cost":5},
    "pedestal":{"db_id":25, "id":"pedestal", "max":50, "name":"Praying Pedestal", "cost":3000},
    "energy":{"db_id":26, "id":"energy", "max":500, "name":"Energy Drink", "cost":25},
    "poison":{"db_id":27, "id":"poison", "max":750, "name":"Poison", "cost":10}
}

WELCOME_MESSAGES = ["{user} joined!", "{user} hopped into the server!", "{user} has entered the server!", "{user} is now here!", "Welcome, {user}!", "{user} has appeared!", "We've been expecting you {user}..."]


DIGCHANCES = {
    "Indium": 100,
    "Silver": 80,
    "Osmium": 60,
    "Platinum":35,
    "Gold": 90,
    "Rhenium": 75,
    "Palladium": 50,
    "Rhodium": 20
}

DIGPROFIT = {
    "Indium": 40,
    "Silver": 60,
    "Osmium": 80,
    "Platinum": 105,
    "Gold": 80,
    "Rhenium": 130,
    "Palladium": 180,
    "Rhodium": 230
}

HUNTWINITEMS = ["duck", "chicken", "beaver", "deer", "weasel", "blue tit", "owl", "salmon", "trout"]

HUNTWINOPTIONS = {
    "duck": {
        "name":"Duck",
        "amount":50,
        "messages":
            [
                "You went hunting and found a duck! A duck breeder bought it off you for",
                f"You found and killed a duck on your hunt! You managed to sell it at the market for",
                f"On your adventure you found a duck and just about managed to capture it. On the way back a kind man offered to buy it off you for"
            ]
        },
    "chicken": {
        "name":"Chicken",
        "amount":15,
        "messages":
            [
                "You found a chicken on your hunt! Unfortunately, chicken prices are down at the moment and you could only sell it for",
                "You found a chicken on your adventure but just as you were about to capture it, it managed to escape! Luckily on your depressing walk back you found a wallet lying on the floor with",
                f"While hunting in the woods you came across a chicken and you were able to sell it to the local breeder for"
            ]
        },
    "beaver": {
        "name":"Beaver",
        "amount":63,
        "messages":[
            "On your hunt you found a beaver chilling in behind a tree. You rudely interrupted its peaceful afternoon and sold it to the highest bidder for",
            "While you were sneakily rummaging through the woods for any animal you came across an innocent little beaver but as you were sneaking up on it the beaver suddenly heard you and started running. This provoked the race of the century which ended 10 seconds later with you tripping over a tree log. Luckily for you, you face planted right into a ring that must have been dropped earlier on. You went to the local jeweler and after a few minutes of negotiating you managed to sell it for",
            "After hours of hunting you decided it was time to go back home empty handed but luckily on your way back from the woods you found a clueless beaver and you took your only opportunity of the day and pounced! Unfortunately, since it was late, you only managed to sell the beaver in the market for"
        ]
    },
    "deer": {
        "name":"Deer",
        "amount": 130,
        "messages":[
            "While you were walking through the woods, crushing leaves beneath your feet, you spotted a deer about 40 yards away. You wanted to make sure you got as close as possible to ensure you didn't miss your shot. After about 20 more feet of walking you were ready! You lined up your shot and fired, narrowly missing a tree trunk on the way to the deer. After collecting the deer you sold it to some travelers for",
            "On your hunt you found a deer and sold it for",
            "You went on a hunt in the woods and managed to capture a deer! You sold it for"
        ]
    },
    "weasel": {
        "name":"Weasel",
        "amount":35, "messages":[
            "On your journey through the wilderness, you stumble upon an early waking weasel and start to walk towards it quietly, as to not scare it away. You just about manage to catch it and after bringing it back to the market, you are able to sell it for",
            "You captured a weasel in one of your traps! You sold it to a friend for",
            "You found and captured a weasel in the forest. You sold it to a breeder for"
        ]
    },
    "blue tit": {
        "name":"Blue tit",
        "amount":20,
        "messages":[
            "You just about managed to hit a blue tit out of the sky and sold it in the market for",
            "On your hunt you found a blue tit that had fallen out of the sky and was injured. You took it to the vet and once it was all fixed up you sold it to a breeder for",
            "You were about to leave the forest after a bad day of hunting but on the very edge of the forest you saw and captured a blue tit. You sold it to a neighbour for"
        ]
    },
    "owl": {
        "name":"Owl",
        "amount": 50,
        "messages":[
            "You found an injured owl on your journey and sold it to a pet store for",
            "On your hunt you spotted an owl and just about managed to catch it. You sold it at the market for",
            "While strolling through the forest you managed to find a baby owl and sold to a breeder for"
        ]
    },
    "salmon": {
        "name":"Salmon",
        "amount":75,
        "messages":[
            "You found a lake during your hunt and managed to catch a salmon. You sold it at the market for",
            "On your adventure in the forest you cam across a pond and managed to catch a salmon from it. You sold it to a breeder for",
            "You stumbled upon a river in the forest and managed to kill a salmon. You sold it for"
        ]
    },
    "trout": {
        "name":"Trout",
        "amount":30,
        "messages":[
            "You came across a small lake and managed to catch a trout. You sold it for",
            "You found a pond in the woods and caught a trout in it. You sold it at the local market for",
            "You managed to catch a trout in a little river and sold it to a breeder for"
        ]
    }
}

FISHWINITEMS = ["cod", "brill", "crab", "crayfish", "eel", "haddock", "salmon"]

FISHINGWINOPTIONS ={
    "cod": {
        "name":"Cod",
        "amount":30,
        "messages":[
            "You caught a cod during your fish and sold it for",
            "During your fish you managed to catch a cod! You gave it to the aquarium who were somehow running low on them for",
            "You managed to catch a cod in a little river in the wood and sold it at the market for"
        ]
    },
    "brill":{
        "name":"Brill",
        "amount":20,
        "messages":[
            "You caught a small brill and sold it for a measly",
            "You managed to catch a small Brill and sold it to a breeder for",
            "During your fish you caught a brill in a pond and sold it at the market for"
        ]
    },
    "crab":{
        "name":"Crab",
        "amount":75,
        "messages":[
            "You found a crab on the outskirts of your usual fishing pond and sold it to a traveler for",
            "You caught a crab during your fish and sold it to a breeder for",
            "You managed to catch a crab and sold it in the market for"
        ]
    },
    "crayfish":{
        "name":"Crayfish",
        "amount":100,
        "messages":[
            "You caught a crayfish during your fish and sold it for",
            "You just about managed to catch the crayfish before you lost it! You sold it in the market for",
            "Your lucky pond never fails you! You found a crayfish and sold it to a breeder for"
        ]
    },
    "eel":{
        "name":"Eel",
        "amount":60,
        "messages":[
            "You caught a slimy little eel and sold it in the market for",
            "You managed to catch an eel during your fish and sold it to a random man you found in the woods for",
            "During your fish you managed to catch an eel and sell it for"
        ]
    },
    "haddock":{
        "name":"Haddock",
        "amount":40,
        "messages":[
            "You managed to catch a small haddock and sold it to the local breeder for",
            "You caught a haddock in a river and sold it at the market for",
            "You caught a haddock and the man fishing next to you offered to buy it for"
        ]
    },
    "tuna":{
        "name":"Tuna",
        "amount":80,
        "messages":[
            "A violent tuna bit on your rod and you just about managed to kill it before it bit your fingers off. You sold it at the market for",
            "You caught a tuna and sold it to a breeder for",
            "You managed to catch a tuna and sold it for"
        ]
    },
    "salmon":{
        "name":"Salmon",
        "amount":67,
        "messages":[
            "You managed to catch a salmon at a nearby lake and sold it for",
            "Your lucky pond never fails you! You caught a salmon at your lucky pond and sold it at the market for",
            "You caught a salmon and sold it to a breeder for"
        ]
    }
}

HELP_COMMAND_USER = {
    "Server":
    [
        {
            "name": "</serverinfo:1057397467752189962>",
            "command_name": "serverinfo",
            "description": "Gives information about the server",
            "usage": "/serverinfo "
        },
        {
            "name": "</membercount:1057397471728373881>",
            "command_name": "membercount",
            "description": "Find out the member count",
            "usage": "/membercount "
        }
    ],
    "Role":
        [
            {
                "name": "</role id:1057397465847967904>",
                "command_name": "role id",
                "description": "Gives you the ID of a role",
                "usage": "/role id <role> "
            },
            {
                "name": "</role info:1057397465847967904>",
                "command_name": "role info",
                "description": "Shows role info",
                "usage": "/role info <role> "
            },
    ],
    "Nickname":
        [
            {
                "name": "</nickname request submit:1057399221986263191>",
                "command_name": "nickname request submit",
                "description": "Submit a nickname change request",
                "usage": "/nickname request submit <nickname> "
            }
    ],
    "Misc":
        [
            {
                "name": "</botinfo:1057399053064863875>",
                "command_name": "botinfo",
                "description": "Information about the bot",
                "usage": "/botinfo "
            },
            {
                "name": "</ping:1057399054285406410>",
                "command_name": "ping",
                "description": "Get the bot's ping",
                "usage": "/ping "
            }
    ],
    "Games":
        [
            {
                "name": "</coinflip:1057399225282990180>",
                "command_name": "coinflip",
                "description": "Do a coin flip",
                "usage": "/coinflip "
            },
            {
                "name": "</rps:1057399226851659796>",
                "command_name": "rps",
                "description": "Play rock paper scissors",
                "usage": "/rps [choice] "
            },
            {
                "name": "</tictactoe:1057399227849916585>",
                "command_name": "tictactoe",
                "description": "Play tictactoe against an opponent",
                "usage": "/tictactoe <opponent> "
            }
    ],
    "Timers":
        [
            {
                "name": "</reminder create:1057399225282990180>",
                "command_name": "reminder new",
                "description": "Create a new reminder",
                "usage": "/reminder new <duration> [message] "
            },
            {
                "name": "</reminder list:1057399226851659796>",
                "command_name": "reminder list",
                "description": "List all your current reminders.",
                "usage": "/reminder list "
            },
            {
                "name": "</reminder remove:1057399227849916585>",
                "command_name": "reminder remove",
                "description": "Remove a reminder",
                "usage": "/reminder remove <reminder-id> "
            }
        ],
    "Economy":
        [
            {
                "name": "</inventory:1067927099211522088>",
                "command_name": "inventory",
                "description": "View your inventory items",
                "usage": "/inventory [user] "
            },
            {
                "name": "</work:1067927104185962648>",
                "command_name": "work",
                "description": "Work to nom some cookies",
                "usage": "/work "
            },
            {
                "name": "</nom:1067927107533021255>",
                "command_name": "nom",
                "description": "Nom some cookies",
                "usage": "/nom "
            },
            {
                "name": "</balance:1067927110972362864>",
                "command_name": "balance",
                "description": "View your or another user's cookie balance",
                "usage": "/balance [member] "
            },
            {
                "name": "</daily:1067927185496748112>",
                "command_name": "daily",
                "description": "Get your daily cookies",
                "usage": "/daily "
            },
            {
                "name": "</weekly:1067927188655054858>",
                "command_name": "weekly",
                "description": "Get your weekly cookies",
                "usage": "/weekly "
            },
            {
                "name": "</monthly:1067927191326818396>",
                "command_name": "monthly",
                "description": "Get your monthly cookies",
                "usage": "/monthly "
            },
            {
                "name": "</pray:1067927196758450307>",
                "command_name": "pray",
                "description": "Pray to the nom Gods for some more cookies",
                "usage": "/pray "
            },
            {
                "name": "</higher-or-lower:1074437831956639825>",
                "command_name": "higher-or-lower",
                "description": "Play higher or lower for cookies",
                "usage": "/higher-or-lower "
            },
            {
                "name": "</shop:1067927199447007363>",
                "command_name": "shop",
                "description": "Open the shop",
                "usage": "/shop "
            },
            {
                "name": "</item:1067927271882633366>",
                "command_name": "item",
                "description": "Check the information of an item",
                "usage": "/item <item> "
            },
            {
                "name": "</buy:1067927277272313917>",
                "command_name": "buy",
                "description": "Buy an item from the shop",
                "usage": "/buy <item> "
            },
            {
                "name": "</leaderboard economy:1067927280564830258>",
                "command_name": "leaderboard economy",
                "description": "View the global leaderboard",
                "usage": "/leaderboard economy "
            },
            {
                "name": "</share:1067927283651858462>",
                "command_name": "share",
                "description": "Share some of your cookies with another member",
                "usage": "/share <member> <cookies> "
            },
            {
                "name": "</hunt:1067927289570013284>",
                "command_name": "hunt",
                "description": "Hunt in the scary woods to find some cookies",
                "usage": "/hunt "
            },
            {
                "name": "</fish:1067927292325670972>",
                "command_name": "fish",
                "description": "Go fishing to find some treasures",
                "usage": "/fish "
            },
            {
                "name": "</postvideo:1067927381236535307>",
                "command_name": "postvideo",
                "description": "Post a video and hope it does well",
                "usage": "/postvideo "
            },
            {
                "name":"</dig:1067927375200923678>",
                "command_name":"dig",
                "description":"Dig for hidden treasure",
                "usage":"/dig "
            },
            {
                "name": "</minion view:1067927384713592882>",
                "command_name": "minion view",
                "description": "View your minions information",
                "usage": "/minion view "
            },
            {
                "name": "</minion empty:1067927384713592882>",
                "command_name": "minion empty",
                "description": "Empty the cookies in your minion",
                "usage": "/minion empty "
            },
            {
                "name":"</task all:1067927387356012676>",
                "command_name": "task all",
                "description":"Do all money making commands",
                "usage": "/task all "
            }
    ],
    "Levels":
        [
            {
                "name": "</level:1086786876419084410>",
                "command_name": "level",
                "description": "View yours or another users level",
                "usage": "/level [user] "
            },
            {
                "name": "</leaderboard level:1067927280564830258>",
                "command_name": "leaderboard level",
                "description": "View the level leaderboard",
                "usage": "/leaderboard level "
            },
            {
                "name": "</levels config user:1086786886460248176>",
                "command_name": "levels config user",
                "description": "Manage your personal levels settings",
                "usage": "/levels config user "
            }
    ],
    "Private VC":
        [
            {
                "name": "</privatevc invite:1057399306979659917>",
                "command_name": "privatevc invite",
                "description": "Invite a user to your voice channel",
                "usage": "/privatevc invite <member> "
            },
            {
                "name": "</privatevc block:1057399306979659917>",
                "command_name": "privatevc block",
                "description": "Block a user from your voice channel",
                "usage": "/privatevc block <member> "
            },
            {
                "name": "</privatevc public:1057399306979659917>",
                "command_name": "privatevc public",
                "description": "Creates a 'request to join' channel for other members",
                "usage": "/privatevc public "
            },
            {
                "name": "</privatevc transfer:1057399306979659917>",
                "command_name": "privatevc transfer",
                "description": "Transfer your voice channel to someone else",
                "usage": "/privatevc transfer <member> "
            }
    ],
    "Applications":
        [
            {
                "name": "</application submit:1095808577442173088>",
                "command_name": "application submit",
                "description": "Submit an application",
                "usage":"/application submit"
            }
        ],
    "Music":
        [
            {
                "name": "</lyrics:1057397239724650616>",
                "command_name": "lyrics",
                "description": "Get the lyrics to a song",
                "usage": "/lyrics <song> "
            }
    ],
    "User":
        [
            {
                "name": "</user id:1057397462366699541>",
                "command_name": "user id",
                "description": "Get the ID of a user",
                "usage": "/user id <user> "
            },
            {
                "name": "</user info:1057397462366699541>",
                "command_name": "user info",
                "description": "Shows user info",
                "usage": "/user info [user] "
            },
            {
                "name": "</user avatar:1057397462366699541>",
                "command_name": "user avatar",
                "description": "Shows a users avatar",
                "usage": "/user avatar [member] "
            }
    ],
    "Fun":
        [
            {
                "name": "</snipe:1057397548903563315>",
                "command_name": "snipe",
                "description": "Get the content of the last message deleted in a channel",
                "usage": "/snipe "
            },
            {
                "name": "</fun trivia:1057397550883283086>",
                "command_name": "fun trivia",
                "description": "Get a trivia question",
                "usage": "/fun trivia [topic] [difficulty] "
            },
            {
                "name": "</fun animal cat:1057397550883283086>",
                "command_name": "fun animal cat",
                "description": "Get an image of a cat with a fun fact",
                "usage": "/fun animal cat "
            },
            {
                "name": "</fun animal dog:1057397550883283086>",
                "command_name": "fun animal dog",
                "description": "Get an image of a dog with a fun fact",
                "usage": "/fun animal dog "
            },
            {
                "name": "</fun animal bird:1057397550883283086>",
                "command_name": "fun animal bird",
                "description": "Get an image of a bird with a fun fact",
                "usage": "/fun animal bird "
            },
            {
                "name": "</fun animal fox:1057397550883283086>",
                "command_name": "fun animal fox",
                "description": "Get an image of a fox with a fun fact",
                "usage": "/fun animal fox "
            },
            {
                "name": "</fun animal kangaroo:1057397550883283086>",
                "command_name": "fun animal kangaroo",
                "description": "Get an image of a kangaroo with a fun fact",
                "usage": "/fun animal kangaroo "
            },
            {
                "name": "</fun animal koala:1057397550883283086>",
                "command_name": "fun animal koala",
                "description": "Get an image of a koala with a fun fact",
                "usage": "/fun animal koala "
            },
            {
                "name": "</fun animal panda:1057397550883283086>",
                "command_name": "fun animal panda",
                "description": "Get an image of a panda with a fun fact",
                "usage": "/fun animal panda "
            },
            {
                "name": "</fun filter blue:1057397550883283086>",
                "command_name": "fun filter blue",
                "description": "Blue filter",
                "usage": "/fun filter blue [member] "
            },
            {
                "name": "</fun filter green:1057397550883283086>",
                "command_name": "fun filter green",
                "description": "Green filter",
                "usage": "/fun filter green [member] "
            },
            {
                "name": "</fun filter greyscale:1057397550883283086>",
                "command_name": "fun filter greyscale",
                "description": "Greyscale filter",
                "usage": "/fun filter greyscale [member] "
            },
            {
                "name": "</fun filter red:1057397550883283086>",
                "command_name": "fun filter red",
                "description": "Red filter",
                "usage": "/fun filter red [member] "
            },
            {
                "name": "</fun filter blurple:1057397550883283086>",
                "command_name": "fun filter blurple",
                "description": "Blurple filter",
                "usage": "/fun filter blurple [member] "
            },
            {
                "name": "</fun filter sepia:1057397550883283086>",
                "command_name": "fun filter sepia",
                "description": "Sepia filter",
                "usage": "/fun filter sepia [member] "
            },
            {
                "name": "</fun filter blur:1057397550883283086>",
                "command_name": "fun filter blur",
                "description": "Blur filter",
                "usage": "/fun filter blur [member] "
            },
            {
                "name": "</fun filter brighten:1057397550883283086>",
                "command_name": "fun filter brighten",
                "description": "Brighten filter",
                "usage": "/fun filter brighten [member] [brightness] "
            },
            {
                "name": "</fun tweet:1057397550883283086>",
                "command_name": "fun tweet",
                "description": "Generate a fake tweet",
                "usage": "/fun tweet <message> [member] [replies] [likes] [retweets] [theme] "
            },
            {
                "name": "</fun youtube:1057397550883283086>",
                "command_name": "fun youtube",
                "description": "Generate fake youtube comment",
                "usage": "/fun youtube <comment> [member] "
            },
            {
                "name": "</fun joke:1057397550883283086>",
                "command_name": "fun joke",
                "description": "Get a random joke",
                "usage": "/fun joke "
            }
    ],
    "Internet":
        [
            {
                "name": "</wikipedia:1057398491321741362>",
                "command_name": "wikipedia",
                "description": "Get information about a query",
                "usage": "/wikipedia <query> "
            },
            {
                "name": "</weather:1122956562475008140>",
                "command_name": "weather",
                "description": "Get the weather in a specific location",
                "usage": "/weather <place> " 
            }
    ]
}

HELP_COMMAND_MOD = {
    "Moderation":
    [
        {
            "name": "</purge:1057398578718453820>",
            "command_name": "purge",
            "description": "clear some messages from the chat",
            "usage": "/purge <amount> "
        },
        {
            "name": "</lock:1057398580182253689>",
            "command_name": "lock",
            "description": "lock a channel",
            "usage": "/lock <channel> "
        },
        {
            "name": "</unlock:1057398581222449172>",
            "command_name": "unlock",
            "description": "unlock a channel",
            "usage": "/unlock <channel> "
        },
        {
            "name": "</slowmode:1066371855201599579>",
            "command_name": "slowmode",
            "description": "Set a channels slowmode",
            "usage": "/slowmode [channel] [time]"
        },
        {
            "name": "</timeout:1057399056898461819>",
            "command_name": "timeout",
            "description": "Timeout a user",
            "usage": "/timeout <member> [reason] [duration] "
        },
        {
            "name": "</untimeout:1057399136527339570>",
            "command_name": "untimeout",
            "description": "Remove the timeout from a user",
            "usage": "/untimeout <member> [reason] "
        },
        {
            "name": "</warn:1057399140465782814>",
            "command_name": "warn",
            "description": "Warn a member",
            "usage": "/warn <member> [reason] "
        },
        {
            "name": "</kick:1057399141719888003>",
            "command_name": "kick",
            "description": "Kick a member",
            "usage": "/kick <member> [reason] "
        },
        {
            "name": "</ban:1066344835163901952>",
            "command_name": "ban",
            "description": "Ban a member from the server",
            "usage": "/ban <member> [reason] [duration]"
        },
        {
            "name": "</unban:1066344836178915370>",
            "command_name": "unban",
            "description": "Unban a member",
            "usage": "/unban <memberid> [reason]"
        },
        {
            "name": "</modlogs:1057399143238221876>",
            "command_name": "modlogs",
            "description": "Get the moderation history for a member",
            "usage": "/modlogs <member> "
        },
        {
            "name": "</warnings:1057399143238221876>",
            "command_name": "warnings",
            "description": "Get the warning history for a member",
            "usage": "/warnings <member> "
        },
        {
            "name": "</punishment info:1057399146354577538>",
            "command_name": "punishment info",
            "description": "Get the information on a specific punishment",
            "usage": "/punishment info <punishment-id> "
        },
        {
            "name": "</punishment edit:1057399146354577538>",
            "command_name": "punishment edit",
            "description": "Edit the information of a punishment",
            "usage": "/punishment edit <punishment-id> "
        },
        {
            "name": "</nickname request accept:1057399221986263191>",
            "command_name": "nickname request accept",
            "description": "Accept a nickname request",
            "usage": "/nickname request accept <member> "
        },
        {
            "name": "</nickname request deny:1057399221986263191>",
            "command_name": "nickname request deny",
            "description": "Deny a nickname request",
            "usage": "/nickname request deny <member> "
        },
        {
            "name": "</setnick:1079409890692431872>",
            "command_name": "setnick",
            "description": "Set a users nickname",
            "usage": "/setnick <user> <nickname> "
        },
    ],
    "Support":
    [
        {
            "name": "</add:1057398496669478922>",
            "command_name": "add",
            "description": "Add a member to a ticket",
            "usage": "/add <member> "
        },
        {
            "name": "</ticket-blacklist:1057398576268988526>",
            "command_name": "ticket-blacklist",
            "description": "Blacklist a user from creating any new tickets in the server",
            "usage": "/ticket-blacklist <member> [reason] "
        },
        {
            "name": "</ticket-unblacklist:1057398577334337606>",
            "command_name": "ticket-unblacklist",
            "description": "Remove a blacklist from a user, allowing them to create new tickets in the server",
            "usage": "/ticket-unblacklist <member> "
        }
    ],
    "Role":
    [
        {
            "name": "</role add:1057397465847967904>",
            "command_name": "role add",
            "description": "Adds role to user",
            "usage": "/role add <role> [member] "
        },
        {
            "name": "</role remove:1057397465847967904>",
            "command_name": "role remove",
            "description": "Removes role from user",
            "usage": "/role remove <role> [member] "
        }
    ]
}

HELP_COMMAND_ADMIN = {
    "Moderation":
    [
        {
            "name": "</moderation config:1108815760480010270>",
            "command_name": "moderation config",
            "description": "Configure your servers moderation settings",
            "usage": "/moderation config "
        },
        {
            "name": "</purge:1057398578718453820>",
            "command_name": "purge",
            "description": "clear some messages from the chat",
            "usage": "/purge <amount> "
        },
        {
            "name": "</lock:1057398580182253689>",
            "command_name": "lock",
            "description": "lock a channel",
            "usage": "/lock <channel> "
        },
        {
            "name": "</unlock:1057398581222449172>",
            "command_name": "unlock",
            "description": "unlock a channel",
            "usage": "/unlock <channel> "
        },
        {
            "name": "</slowmode:1066371855201599579>",
            "command_name": "slowmode",
            "description": "Set a channels slowmode",
            "usage": "/slowmode [channel] [time]"
        },
        {
            "name": "</timeout:1057399056898461819>",
            "command_name": "timeout",
            "description": "Timeout a user",
            "usage": "/timeout <member> [reason] [duration] "
        },
        {
            "name": "</untimeout:1057399136527339570>",
            "command_name": "untimeout",
            "description": "Remove the timeout from a user",
            "usage": "/untimeout <member> [reason] "
        },
        {
            "name": "</warn:1057399140465782814>",
            "command_name": "warn",
            "description": "Warn a member",
            "usage": "/warn <member> [reason] "
        },
        {
            "name": "</kick:1057399141719888003>",
            "command_name": "kick",
            "description": "Kick a member",
            "usage": "/kick <member> [reason] "
        },
        {
            "name": "</ban:1066344835163901952>",
            "command_name": "ban",
            "description": "Ban a member from the server",
            "usage": "/ban <member> [reason] [duration]"
        },
        {
            "name": "</unban:1066344836178915370>",
            "command_name": "unban",
            "description": "Unban a member",
            "usage": "/unban <memberid> [reason]"
        },
        {
            "name": "</modlogs:1057399143238221876>",
            "command_name": "modlogs",
            "description": "Get the moderation history for a member",
            "usage": "/modlogs <member> "
        },
        {
            "name": "</warnings:1057399143238221876>",
            "command_name": "warnings",
            "description": "Get the warning history for a member",
            "usage": "/warnings <member> "
        },
        {
            "name": "</punishment info:1057399146354577538>",
            "command_name": "punishment info",
            "description": "Get the information on a specific punishment",
            "usage": "/punishment info <punishment-id> "
        },
        {
            "name": "</punishment edit:1057399146354577538>",
            "command_name": "punishment edit",
            "description": "Edit the information of a punishment",
            "usage": "/punishment edit <punishment-id> "
        },
        {
            "name": "</nickname request disable:1057399221986263191>",
            "command_name": "nickname request disable",
            "description": "Disable the nickname request system",
            "usage": "/nickname request disable "
        },
        {
            "name": "</nickname request logchannel:1057399221986263191>",
            "command_name": "nickname request logchannel",
            "description": "Channel to send nickname requests to",
            "usage": "/nickname request logchannel <channel> <modrole> [required-role] "
        },
        {
            "name": "</nickname request accept:1057399221986263191>",
            "command_name": "nickname request accept",
            "description": "Accept a nickname request",
            "usage": "/nickname request accept <member> "
        },
        {
            "name": "</nickname request deny:1057399221986263191>",
            "command_name": "nickname request deny",
            "description": "Deny a nickname request",
            "usage": "/nickname request deny <member> "
        },
        {
            "name": "</setnick:1079409890692431872>",
            "command_name": "setnick",
            "description": "Set a users nickname",
            "usage": "/setnick <user> <nickname> "
        },
    ],
    "Support":
    [
        {
            "name": "</supportpanel create:1074437918099251300>",
            "command_name": "supportpanel create",
            "description": "Create a support pannel",
            "usage": "/supportpanel create <channel> [category] [supportrole] [logchannel] [pingrole] [template] [dmonclose] [customwelcomemessage] [custompaneltitle] [custompanelmessage] "
        },
        {
            "name": "</supportpanel setup:1074437918099251300>",
            "command_name": "supportpanel setup",
            "description": "Interactive support pannel setup",
            "usage": "/supportpanel setup "
        },
        {
            "name": "</add:1057398496669478922>",
            "command_name": "add",
            "description": "Add a member to a ticket",
            "usage": "/add <member> "
        },
        {
            "name": "</ticket-blacklist:1057398576268988526>",
            "command_name": "ticket-blacklist",
            "description": "Blacklist a user from creating any new tickets in the server",
            "usage": "/ticket-blacklist <member> [reason] "
        },
        {
            "name": "</ticket-unblacklist:1057398577334337606>",
            "command_name": "ticket-unblacklist",
            "description": "Remove a blacklist from a user, allowing them to create new tickets in the server",
            "usage": "/ticket-unblacklist <member> "
        }
    ],
    "Role":
    [
        {
            "name": "</role add:1057397465847967904>",
            "command_name": "role add",
            "description": "Adds role to user",
            "usage": "/role add <role> [member] "
        },
        {
            "name": "</role remove:1057397465847967904>",
            "command_name": "role remove",
            "description": "Removes role from user",
            "usage": "/role remove <role> [member] "
        },
        {
            "name": "</role create:1057397465847967904>",
            "command_name": "role create",
            "description": "Create a role",
            "usage": "/role create <name> "
        },
        {
            "name": "</role edit:1057397465847967904>",
            "command_name": "role edit",
            "description": "Edit a role",
            "usage": "/role edit <role> "
        },
        {
            "name": "</role delete:1057397465847967904>",
            "command_name": "role delete",
            "description": "Remove a role",
            "usage": "/role delete <role> "
        }
    ],
    "Giveaways": [
        {
            "name": "</giveaway create:1057399310947450971>",
            "command_name": "giveaway create",
            "description": "Create a giveaway",
            "usage": "/giveaway create <channel> <item> <duration> [winners] [host] [allowed-roles] [blocked-roles] [pingrole] "
        },
        {
            "name": "</giveaway add-boost-role:1057399310947450971>",
            "command_name": "giveaway add-boost-role",
            "description": "Add a boost role to giveaways",
            "usage": "/giveaway add-boost-role <role> <boost> "
        },
        {
            "name": "</giveaway remove-boost-role:1057399310947450971>",
            "command_name": "giveaway remove-boost-role",
            "description": "Remove a boost role from giveaways",
            "usage": "/giveaway remove-boost-role <roleid> "
        },
        {
            "name": "</giveaway list-boost-roles:1057399310947450971>",
            "command_name": "giveaway list-boost-roles",
            "description": "List all giveaway boost roles",
            "usage": "/giveaway list-boost-roles "
        },
        {
            "name": "</giveaway add-perm-blocked-role:1057399310947450971>",
            "command_name": "giveaway add-perm-blocked-role",
            "description": "Add a permanent blocked role",
            "usage": "/giveaway add-perm-blocked-role <role> "
        },
        {
            "name": "</giveaway remove-perm-blocked-role:1057399310947450971>",
            "command_name": "giveaway remove-perm-blocked-role",
            "description": "Remove a blocked role",
            "usage": "/giveaway remove-perm-blocked-role <role> "
        }
    ],
    "PrivateVoiceChannels": [
        {
            "name": "</privatevc create:1057399306979659917>",
            "command_name": "privatevc create",
            "description": "Create a private voice channel",
            "usage": "/privatevc create <name> <category> <logchannel> "
        }
    ],
    "Applications":
        [
            {
                "name": "</application create:1095808577442173088>",
                "command_name": "application create",
                "description": "Create an application template",
                "usage":"/application create <name> "
            },
            {
                "name": "</application manage:1095808577442173088>",
                "command_name": "application manage",
                "description": "Manage/Edit an application template",
                "usage":"/application manage "
            },
            {
                "name": "</application refresh:1095808577442173088>",
                "command_name": "application refresh",
                "description": "Refresh an application (Resend to the application channel)",
                "usage":"/application refresh <user> "
            },
            {
                "name": "</application view user:1095808577442173088>",
                "command_name": "application view user",
                "description": "View a users applications",
                "usage":"/application rview user <user> "
            }
        ],
    "Levels":
        [
            {
                "name": "</levels config server:1086786886460248176>",
                "command_name": "levels config server",
                "description": "Manage the servers levels settings",
                "usage": "/levels config server "
            },
            {
                "name": "</setlevel:1086786890084122698>",
                "command_name": "setlevel",
                "description": "Set a users level",
                "usage": "/setlevel <user> "
            },
            {
                "name": "</addxp:1086786964021321749>",
                "command_name": "addxp",
                "description": "Give a user XP",
                "usage": "/addxp <user> "
            },
            {
                "name": "</removexp:1099746490135625728>",
                "command_name": "removexp",
                "description": "Remove XP from a user",
                "usage": "/addxp <member> <xp> "
            },
            {
                "name": "</resetlevel:1099746496963936378>",
                "command_name": "resetlevel",
                "description": "Reset a users level.",
                "usage": "/resetlevel <user> "
            },
            {
                "name": "</levels boostroles add:1086786964021321749>",
                "command_name": "levels boostroles add",
                "description": "Add a boosted xp role",
                "usage": "/levels boostroles add <role> <boost> "
            },
            {
                "name": "</levels boostroles remove:1086786964021321749>",
                "command_name": "levels boostroles remove",
                "description": "Remove a boosted xp role",
                "usage": "/levels boostroles remove <role> "
            },
            {
                "name": "</levels boostroles list:1086786964021321749>",
                "command_name": "levels boostroles list",
                "description": "List all XP Boosted Roles",
                "usage": "/levels boostroles list "
            }
    ],
    "Reactionroles": [
        {
            "name": "</reactionroles create:1057399308175024240>",
            "command_name": "reactionroles create",
            "description": "Interactive creation of a reaction message",
            "usage": "/reactionroles create "
        }
    ],
    "Stickymessage": [
        {
            "name": "</stickymessage setup:1057399229611511808>",
            "command_name": "stickymessage setup",
            "description": "Interactive stickymessage setup",
            "usage": "/stickymessage setup "
        },
        {
            "name": "</stickymessage create:1057399229611511808>",
            "command_name": "stickymessage create",
            "description": "Create a new stickymessage",
            "usage": "/stickymessage create <channel> <type> "
        },
        {
            "name": "</stickymessage manage:1057399229611511808>",
            "command_name": "stickymessage manage",
            "description": "Edit or delete a sticky message",
            "usage": "/stickymessage manage "
        }
    ],
    "Suggestions": [
        {
            "name": "</suggestion config:1057398493695709264>",
            "command_name": "suggestion config",
            "description": "Configure your suggestion channels",
            "usage": "/suggestion config "
        }
    ],
    "Autoroles": [
        {
            "name": "</autorole add:1057397547662049400>",
            "command_name": "autorole add",
            "description": "Add autoroles",
            "usage": "/autorole add [role] "
        },
        {
            "name": "</autorole remove:1028821486288506880>",
            "command_name": "autorole remove",
            "description": "Remove autoroles",
            "usage": "/autorole remove [role] "
        },
        {
            "name": "</autorole list:1057397547662049400>",
            "command_name": "autorole list",
            "description": "Show all autoroles",
            "usage": "/autorole list "
        }
    ],
    "Auto Publish":[
        {
            "name":"/autopublish add",
            "command_name":"autopublish add",
            "description":"Add an autopublish channel",
            "Usage":"/autopublish add <channel> "
        },
        {
            "name":"/autopublish remove",
            "command_name":"autopublish remove",
            "description":"Remove an auto publish channel",
            "Usage":"/autopublish remove "
        }
    ],
    "Threads": [
        {
            "name": "</autothread config:1057399051244548217>",
            "command_name": "autothread config",
            "description": "Configure your autothread settings",
            "usage": "/autothread config "
        }
    ],
    "Welcomer": [
        {
            "name": "</welcome channel:1023429011369639977>",
            "command_name": "welcome channel",
            "description": "Set the welcome channel for your server",
            "usage": "/welcome channel <channel> "
        },
        {
            "name": "</welcome message:1023429011369639977>",
            "command_name": "welcome message",
            "description": "Set a welcome message for your server (run command without a message for help)",
            "usage": "/welcome message [message] "
        },
        {
            "name": "</welcome disable:1023429011369639977>",
            "command_name": "welcome disable",
            "description": "Disable the welcomer system",
            "usage": "/welcome disable "
        }
    ],
    "Logging": [
        {
            "name": "</logging config:1057398233984409660>",
            "command_name": "logging config",
            "description": "Logging Configuration",
            "usage": "/logging config <logchannel> "
        }
    ],
    "Server Statistics": [
        {
            "name": "</statistic channel create:1057399309580111882>",
            "command_name": "statistic channel create",
            "description": "Create a statistic counter channel",
            "usage": "/statistic channel create <type> "
        },
        {
            "name": "</statistic channel remove:1057399309580111882>",
            "command_name": "statistic channel remove",
            "description": "Remove a statistic counter channel",
            "usage": "/statistic channel remove <channelid> "
        },
        {
            "name": "</statistic channel list:1057399309580111882>",
            "command_name": "statistic channel list",
            "description": "List your current statistic counter channels",
            "usage": "/statistic channel create "
        },
        {
            "name": "</statistic channel possible:1057399309580111882>",
            "command_name": "statistic channel possible",
            "description": "List of valid counter channels",
            "usage": "/statistic channel possible "
        }
    ]
}

from dataclasses import dataclass
from typing import Dict, Optional, List, Union

@dataclass
class GuildMain:
    guild_id: int
    welcome_channel: Optional[int] = None
    log_channel: Optional[str] = None
    autorole_ids: Optional[List[str]] = None
    welcome_msg: Optional[str] = None
    auto_thread_channels: Optional[List[str]] = None

    def __post_init__(self):
        if self.autorole_ids and self.autorole_ids.replace(" ", "") == "[]":
            self.autorole_ids = []
        
        else:
            self.autorole_ids = [int(i) for i in self.autorole_ids.replace("[", "").replace("]", "").replace(" ", "").split(",")] if self.autorole_ids else None
        
        if self.auto_thread_channels and self.auto_thread_channels.replace(" ", "") == "[]":
            self.auto_thread_channels = []

        else:
            self.auto_thread_channels = [int(i) for i in self.auto_thread_channels.replace("[", "").replace("]", "").replace(" ", "").split(",")] if self.auto_thread_channels else None

@dataclass
class ServerstatsMain:
    guild_id: int
    channel_id: int
    type: str

@dataclass
class GuildMod:
    guild_id: int
    punishment_id: str
    member_id: int
    mod_id: int
    type: str
    duration: int
    expires: int
    given: int
    expired: Optional[str] = "no"
    reason: Optional[str] = None
    evidence: Optional[str] = None

@dataclass
class ModerationMain:
    guild: int
    muted_role: Optional[int] = None
    mod_log_channel: Optional[int] = None

@dataclass
class LoggingMain:
    guild_id: int
    webhook_link: Optional[str] = None
    message: Optional[bool] = None
    role: Optional[bool] = None
    member: Optional[bool] = None
    voice: Optional[bool] = None
    channel: Optional[bool] = None
    invite: Optional[bool] = None
    user: Optional[bool] = None
    channel_id: Optional[Union[int, str]] = None
    channel_channel_blacklist: Optional[List[int]] = None
    role_role_blacklist: Optional[List[int]] = None

@dataclass
class EconomyMain:
    user_id: int
    guild_id: str
    balance: int
    daily: int
    weekly: int
    monthly: int
    spear: Optional[int] = 0
    rifle: Optional[int] = 0
    minion: Optional[int] = 0
    lucky_pet: Optional[str] = None
    booster_pet: Optional[str] = None
    current_boost: Optional[float] = 1
    p_trophy: Optional[int] = 0
    r_trophy: Optional[int] = 0
    sr_trophy: Optional[int] = 0
    smr_trophy: Optional[int] = 0
    simr_trophy: Optional[int] = 0
    rod: Optional[int] = 0
    comp: Optional[int] = 0
    norm_boost: Optional[int] = 0
    job: Optional[str] = None
    bait: Optional[int] = 0
    minion_last_check: Optional[int] = 0
    minion_full: Optional[int] = 0
    yeast: Optional[int] = 0
    pedestal: Optional[int] = 0
    energy: Optional[int] = 0
    poison: Optional[int] = 0
    spade: Optional[int] = 0
    drill: Optional[int] = 0

@dataclass
class EconomyUserSettings:
    user: int
    tips: bool

@dataclass
class CurrentTickets:
    channel_id: int
    author_id: int
    originmessage_id: int

@dataclass
class AutoThreadMain:
    guild_id: int
    channel_id: int

@dataclass
class StickyMain:
    guild_id: int
    channel_id: int
    message_id: int
    type: str
    message: str = None
    title: str = None
    description: str = None

@dataclass
class SupportMain:
    guild_id: int
    message_id: int
    supportrole_id: int
    supportcategory_id: int
    creation_message: str
    pingrole_id: int
    logchannel_id: int
    dmonclose: bool

@dataclass
class TicketBlacklists:
    member: int
    guild: int
    moderator: int
    reason: str
    given: int

@dataclass
class VoiceChannels:
    guild_id: int
    owner_id: int
    private: int
    channel_id: int
    base_call_id: int
    request_join_id: int
    request_join_text_id: int

@dataclass
class VoiceChannelsMain:
    guild_id: int
    channel_id: int
    name: str
    logchannel: int

@dataclass
class GiveawayMain:
    guild_id: int
    channel_id: int
    message_id: int
    winners: int
    item: str
    ends: int
    entrants: Optional[List[int]] = None
    allowedroles: Optional[List[int]] = None
    blockedroles: Optional[List[int]] = None
    boostedroles: Optional[Union[str,int]] = None
    stackboostedroles: bool = None
    min_daily_msgs: Optional[int] = 0
    min_weekly_msgs: Optional[int] = 0
    min_monthly_msgs: Optional[int] = 0
    min_total_msgs: Optional[int] = 0
    bypassroles: Optional[List[int]] = None

@dataclass
class GiveawayBlocked:
    role_id: int
    guild_id: int

@dataclass
class GiveawayBoosters:
    role_id: int
    guild_id: int
    boost: int

@dataclass
class SuggestionsMain:
    guild_id: int
    channel_id: int
    type: str
    autothread: int
    send: Optional[str]
    accept_channel: Optional[int]
    deny_channel: Optional[int]

@dataclass
class NicknameMain:
    guild_id: int
    channel_id: int
    mod_role_id: Optional[int] = None
    required_role: Optional[int] = None

@dataclass
class NicknameRequests:
    guild: int
    requested_nick: str
    user: int
    message_id: int
    channel_sent_id: int

@dataclass
class ReactionMain:
    guild_id: int
    message_id: int
    channel_id: int
    reaction_type: str
    message_type: int
    roles: List[str]

    def __post_init__(self):
        self.roles = [int(i) for i in self.roles.replace("[", "").replace("]", "").replace(" ", "").split(",")] if self.roles else None

@dataclass
class Autopublish:
    guild_id: int
    channel_id: int
@dataclass
class Economy_User_Settings:
    user: int
    tips: bool
@dataclass
class LevelMain:
    guild_id: int
    enabled: bool = True
    min_xp: int = 10
    max_xp: int = 15
    min_vc_xp: int = 5
    max_vc_xp: int = 10
    level_up_message: str = None
    level_up_channel: str = None
    drops: bool = False
    background_color: str = "default"
    main_color: str = "default"
    primary_font_color: str = "default"
    secondary_font_color: str = "default"
    no_xp_channels: Optional[List[int]] = None
    no_xp_roles: Optional[List[int]] = None   
    voice_xp_gain: bool = False
    stackable_rewards: bool = False
    max_level: Optional[int] = None
    cooldown: Optional[int] = None
    reward_message: Optional[str] = None
    no_xp_roles: Optional[List[int]] = None
    stackable_rewards: bool = False
    reward_message: Optional[str] = None
    max_level: Optional[int] = None
    voice_xp_gain: bool = False
    mee6_levels: Optional[bool] = False

@dataclass
class LevelRoles:
    guild_id: int
    level: int
    role_id: int
@dataclass
class LevelUsers:
    unique_id: str
    guild_id: int
    user_id: int
    total_xp: int
    background_color: Optional[str] = None
    main_color: Optional[str] = None
    primary_font_color: Optional[str] = None
    secondary_font_color: Optional[str] = None
    last_xp_gain: Optional[int] = None
@dataclass
class Notifications:
    channel_id: int
    guild_id: int
    ping_channel_id: int
    ping_message: str
    type: str
@dataclass
class SuggestionsInfo:
    suggestion_id: str
    guild_id: int
    channel_id: int
    message_id: int
    user_id: int
    status: str = "Pending"
    upvotes: List[int] = None
    downvotes: List[int] = None
@dataclass
class LevelBonusRoles:
    guild_id: int
    role_id: int
    boost: int

@dataclass
class LevelBonusChannels:
    guild_id: int
    channel_id: int
    boost: int

@dataclass
class ApplicationQuestions:
    app_id: str
    guild_id: int
    name: str
    questions: List[str]
    channel_to_send: int
    enabled: bool = True
    roles_required: Optional[List[int]] = None
    category: Optional[int] = None
    
@dataclass
class ApplicationAnswers:
    app_id: str
    guild_id: int
    user_id: int
    app_name: str
    q_a: Dict[str, str]
    verdict: Optional[bool] = None
    reason: Optional[str] = None
    mod_id: Optional[int] = None
    channel_id: Optional[int] = None

@dataclass
class RemindersBase:
    reminder_id: str
    guild_id: int
    channel_id: int
    user_id: int
    message: str
    time: int
    completed: bool

@dataclass
class UserStatisticsBase:
    unique_id: str
    guild_id: int
    user_id: int
    total_msgs: Optional[int] = 0
    last_daily_msgs: Optional[int] = 0
    last_weekly_msgs: Optional[int] = 0
    last_monthly_msgs: Optional[int] = 0

@dataclass
class GiveawayTempBoosterBase:
    unique_id: Optional[str]
    message_id: int
    boost_role_id: int
    boost_amount: int


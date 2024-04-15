import nextcord
from constants import VOTELINK

class BotInfoLinkButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(nextcord.ui.Button(label="Support Server", url="https://discord.gg/WjdMjUnBvJ"))
        self.add_item(nextcord.ui.Button(label="Invite", url="https://discord.com/api/oauth2/authorize?client_id=1016198853306884126&permissions=8&scope=applications.commands%20bot"))
        self.add_item(nextcord.ui.Button(label="Vote", url=VOTELINK))
        self.add_item(nextcord.ui.Button(label="Privacy Policy", url="https://nomindustries.com/bigbot/privacy"))



class PrivacyPolicyButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(nextcord.ui.Button(label="Privacy Policy", url="https://nomindustries.com/bigbot/privacy"))
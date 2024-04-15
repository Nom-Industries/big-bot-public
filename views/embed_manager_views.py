import nextcord
from typing import List, Union


class EmbedCreationForm(nextcord.ui.Modal):
    def __init__(self, type):
        super().__init__(title="Embed Create", timeout=None)
        self.type = type
        self.name = nextcord.ui.TextInput(
                label = "What do you want the webhook name to be?",
                placeholder = "This will be the name of the message sender",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=32,
                required=True
            )
        self.add_item(self.name)

        self.embedtitle = nextcord.ui.TextInput(
                label = "What do you want the title to be?",
                placeholder = "Tip: Up to 256 characters!",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=256,
                required=True
            )
        self.add_item(self.embedtitle)

        self.embeddescription = nextcord.ui.TextInput(
                label = "What do you want the description to be?",
                placeholder = "Tip: To mention channels do <#channelid> (eg. <#1028741186380365865>)",
                style=nextcord.TextInputStyle.paragraph,
                min_length=1,
                max_length=4000,
                required=True
            )
        self.add_item(self.embeddescription)

        self.embedauthor = nextcord.ui.TextInput(
                label = "What do you want the author name to be",
                placeholder = "Note: the author image will automatically be the server icon",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=32,
                required=False
            )
        self.add_item(self.embedauthor)
        self.embedauthorurl = nextcord.ui.TextInput(
                label = "What do you want the author url to be",
                placeholder = "Note: This only works if you have also specified the embed author in the question above",
                style=nextcord.TextInputStyle.short,
                min_length=1,
                max_length=300,
                required=False
            )
        self.add_item(self.embedauthorurl)


    async def callback(self, interaction: nextcord.Interaction):
        self.name = self.name.value
        self.embeddescription = self.embeddescription.value
        self.embedtitle = self.embedtitle.value
        if self.embedauthor.value:
            self.embedauthor = self.embedauthor.value
            if self.embedauthorurl.value:
                self.embedauthorurl = self.embedauthorurl.value
            else:
                self.embedauthorurl = None
        else:
            self.embedauthor = None
            self.embedauthorurl = None
        self.stop()
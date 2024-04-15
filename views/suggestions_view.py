from asyncio import tasks
from venv import create
import nextcord
from nextcord.ext import commands
from bot.bot import Bot
from utils.utils import color_message
from views import List_Options
from constants import COLOUR_MAIN, COLOUR_BAD, COLOUR_GOOD
from typing import List, Union
from utils import create_error_embed, create_success_embed
from db_handler.schemas import SuggestionsMain, SuggestionsInfo

class SuggestionView(nextcord.ui.View):
    def __init__(self, user: nextcord.User, data: List[SuggestionsMain]):
        super().__init__()
        self.user = user
        self.data = data

    @nextcord.ui.button(label = "Create new suggestion channel", style = nextcord.ButtonStyle.green)
    async def create_suggestion_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        channel_id = Options(interaction.user.id)
        embed=nextcord.Embed(title="Suggestion Channel Add", description="Choose which channel you want to have as a suggestion channel by selecting it below.", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=channel_id)
        await channel_id.wait()
        channel = channel_id.values[0]
        if [i for i in self.data if i.channel_id == channel.id]:
            await interaction.edit_original_message(embed=create_error_embed(title="Error!", description=f"{channel.mention} is already a suggestion channel."), view=None)
            return
        
        suggtyperaw = TypeOption(org_user=interaction.user.id)
        embed=nextcord.Embed(title="Suggestion Channel Add", description="""I support multiple types of suggestion channels. Please use the buttons to select an option from below:
    
`Simple` - I will add a ✅ & ❎ emoji to any messages send in the channel
`Embedded` - I will resend the suggestion as an embed and add a ✅ & ❎ emoji to the embed message
`Complex` - All suggestions will be give their own ID allowing you to accept and deny them""", colour=COLOUR_MAIN)
        await interaction.edit_original_message(embed=embed, view=suggtyperaw)
        await suggtyperaw.wait()
        suggtype = suggtyperaw.value
        autothreadraw = AutoThreadOption(org_user=interaction.user.id)
        embed=nextcord.Embed(title="Suggestion Channel Add", description="""Select below whether you want me to automatically create a thread for every suggestion.""", colour=COLOUR_MAIN)
        await interaction.edit_original_message(embed=embed, view=autothreadraw)
        await autothreadraw.wait()

        autothread = autothreadraw.value
        separate = None
        acceptchannel = None
        deniedchannel = None

        if suggtype == "complex":
            seperateraw = SeperateChannels(org_user=interaction.user.id)
            embed = nextcord.Embed(title="Seperate channels", description="""Select below whether you want me to send accepted/denied suggestions to a different channel or just edit the original message to show updates.""", colour=COLOUR_MAIN)
            await interaction.edit_original_message(embed=embed, view=seperateraw)
            await seperateraw.wait()
            seperate = seperateraw.value

            if seperate:
                acceptedchannelid = Options(interaction.user.id)
                embed = nextcord.Embed(title="Accepted Channel Add", description="Choose which channel you want to have accepted suggestions sent to.", colour=COLOUR_MAIN)

                await interaction.edit(embed=embed, view=acceptedchannelid)
                await acceptedchannelid.wait()

                acceptchannel = acceptedchannelid.values[0].id

                if acceptchannel == channel:
                    await interaction.send(embed=create_error_embed(title="Invalid Channel", description="That channel is already being used as the suggestion channel."))
                    return
                
                deniedchannelid = Options(interaction.user.id)
                embed = nextcord.Embed(title="Denied Channel Add", description="Choose which channel you want to have denied suggestions sent to.", colour=COLOUR_MAIN)

                await interaction.edit(embed=embed, view=deniedchannelid)
                await deniedchannelid.wait()

                deniedchannel = deniedchannelid.values[0].id

                if deniedchannel in (channel, acceptchannel):
                    await interaction.send(embed=create_error_embed(title="Invalid Channel", description="That channel is already being used as the suggestion channel." if deniedchannel == channel else "That channel is already being used as the accepted suggestions channel."))
                    return

        self.data.append(Bot.db.create_data(table="suggestions", guild_id=interaction.guild.id, channel_id=channel.id, type=suggtype, autothread=autothread, send=separate, accept_channel=acceptchannel, deny_channel=deniedchannel))
        
        await interaction.edit_original_message(embed=create_success_embed(title="Suggestion Channel", description=f"{channel.mention} has been set as a suggestion channel"), view=None)
    
    @nextcord.ui.button(label = "Delete an existing suggestion channel", style = nextcord.ButtonStyle.red)
    async def delete_suggestion_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if len(self.data) > 0:
            optiontext = ""
            options = []
            for i, item in enumerate(self.data):
                optiontext = optiontext + f"{i+1}: `Channel ID` {item.channel_id}\n"
                options.append(str(i+1))
            
            embed = nextcord.Embed(title="Delete suggestion channel", description=f"Choose which suggestion channel you want to delete from the list below:\n\n {optiontext}", colour=COLOUR_MAIN)
            chosenoption = List_Options_Suggestions(options)
            await interaction.send(embed=embed, view=chosenoption)
            await chosenoption.wait()

            option = self.data[(int(chosenoption.values[0])-1)]

            Bot.db.delete_data("suggestions", option)

            self.data.pop(int(chosenoption.values[0])-1)

            await interaction.edit_original_message(embed=create_success_embed(title="Success!", description="I have deleted the selected suggestion channel"), view=None)

        else:
            await interaction.send("You don't have an exisiting suggestion channel to edit.", ephemeral=True)
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.user.id != interaction.user.id:
            await interaction.send("You can't click this!", ephemeral=True)
            return False

        return True

class List_Select_Suggestions(nextcord.ui.Select):
    def __init__(self, options: List[str], placeholder: str = "Select an option", max_values: int = 1):
        super().__init__(options=[nextcord.SelectOption(label=i, description=i) for i in options], placeholder=placeholder, max_values=max_values)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)

class List_Options_Suggestions(nextcord.ui.View):
    def __init__(self, options: List[str], placeholder: str = "Select an option", max_values: int = 1):
        super().__init__(timeout=120)
        self.values = []
        for i in range(0, len(options), 25):
            self.add_item(List_Select_Suggestions(options=options[i:i+25], placeholder=placeholder, max_values=max_values))

    @nextcord.ui.button(label="Complete", style=nextcord.ButtonStyle.green)
    async def complete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()

class TypeOption(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__()
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Simple", style = nextcord.ButtonStyle.blurple)
    async def simple(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "simple"
        self.stop()

        self.clear_items()
    
    @nextcord.ui.button(label = "Embedded", style = nextcord.ButtonStyle.blurple)
    async def embedded(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "embedded"
        self.stop()

        self.clear_items()

    @nextcord.ui.button(label = "Complex", style = nextcord.ButtonStyle.blurple)
    async def complex(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = "complex"
        self.stop()

        self.clear_items()
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.stop()

class AutoThreadOption(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__()
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Automatically create thread", style = nextcord.ButtonStyle.green)
    async def thread(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        self.stop()

        self.clear_items()
    
    @nextcord.ui.button(label = "Don't create thread", style = nextcord.ButtonStyle.red)
    async def no_thread(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        self.stop()

        self.clear_items()
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.stop()

class SeperateChannels(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__()
        self.value = None
        self.org_user = org_user

    @nextcord.ui.button(label = "Use seperate channels for accepted/denied suggestions", style = nextcord.ButtonStyle.green)
    async def seperate_channels_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        self.stop()

        self.clear_items()
    
    @nextcord.ui.button(label = "Don't use seperate channels for accepted/denied suggestions", style = nextcord.ButtonStyle.red)
    async def seperate_channels_dont(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        self.stop()

        self.clear_items()
    
    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        self.stop()

class AutoThreadJoin(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout=None

    @nextcord.ui.button(label="Join Thread", style = nextcord.ButtonStyle.blurple, custom_id="join_thread")
    async def add_to_thread(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.channel.add_user(interaction.user)


class ChannelList(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(custom_id="test", placeholder="Select a channel", min_values=1, max_values=1, channel_types=[nextcord.ChannelType.text])

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)
        self.view.stop()

class Options(nextcord.ui.View):
    def __init__(self, org_user:int):
        super().__init__(timeout=30)
        self.add_item(ChannelList())
        self.values = []
        self.choice = None
        self.org_user = org_user

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False
        
        return True

class VotingView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="0", emoji="👍",  style = nextcord.ButtonStyle.green, custom_id="upvote_suggestion")
    async def upvote_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("Registering Vote...", ephemeral=True)

        data: List[SuggestionsInfo] = Bot.db.get_data("suggestions_info", message_id=interaction.message.id)

        if interaction.user.id not in data[0].upvotes:
            data[0].upvotes.append(interaction.user.id)
            await interaction.edit_original_message(content="👍 Upvote Added")

            if interaction.user.id in data[0].downvotes:
                data[0].downvotes.remove(interaction.user.id)
        
        else:
            data[0].upvotes.remove(interaction.user.id)
            await interaction.edit_original_message(content="👍 Upvote Removed")

        embed = interaction.message.embeds[0]
        button.label = str(len(data[0].upvotes))

        Bot.db.update_data("suggestions_info", data[0])

        embed.set_footer(text=embed.footer.text[:embed.footer.text.find("| ")+2] + str(len(data[0].upvotes)) + " - " + str(len(data[0].downvotes)))

        await interaction.message.edit(embed=embed, view=self)

    @nextcord.ui.button(label="", emoji="⚙️",  style = nextcord.ButtonStyle.grey, custom_id="suggestion_settings")
    async def suggestion_settings(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        data: List[SuggestionsInfo] = Bot.db.get_data("suggestions_info", message_id=interaction.message.id)

        if interaction.user.id == data[0].user_id:
            embed = nextcord.Embed(title="Suggestion Creator Panel", description="Welcome to the suggestion creator panel. You can use the buttons below to edit or delete your suggestion")
            usermanagment = SuggestionManagementUser(org_msg=interaction.message)
            await interaction.send(embed=embed, view=usermanagment, ephemeral=True)
            await usermanagment.wait()
            if usermanagment.value is False:
                return
            
        if interaction.user.guild_permissions.moderate_members:
            embed = nextcord.Embed(title="Staff Panel", description="Welcome to the staff panel panel. You can use the buttons below accept, deny and delete this suggestion")
            staffmanagement = SuggestionManagementStaff(org_msg=interaction.message)
            await interaction.send(embed=embed, view=staffmanagement, ephemeral=True)
            await staffmanagement.wait()

        if not interaction.user.guild_permissions.moderate_members and not interaction.user.id == data[0].user_id:
            await interaction.send("You must be either the creator of a suggestion or a staff member to manage suggestions", ephemeral=True)
    
    @nextcord.ui.button(label="0", emoji="👎",  style = nextcord.ButtonStyle.red, custom_id="downvote_suggestion")
    async def downvote_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("Registering Vote...", ephemeral=True)

        data: List[SuggestionsInfo] = Bot.db.get_data("suggestions_info", message_id=interaction.message.id)

        if interaction.user.id not in data[0].downvotes:
            data[0].downvotes.append(interaction.user.id)
            await interaction.edit_original_message(content="👍 Downvote Added")

            if interaction.user.id in data[0].upvotes:
                data[0].upvotes.remove(interaction.user.id)
        
        else:
            data[0].downvotes.remove(interaction.user.id)
            await interaction.edit_original_message(content="👍 Downvote Removed")

        embed = interaction.message.embeds[0]
        button.label = str(len(data[0].downvotes))

        Bot.db.update_data("suggestions_info", data[0])

        embed.set_footer(text=embed.footer.text[:embed.footer.text.find("| ")+2] + str(len(data[0].upvotes)) + " - " + str(len(data[0].downvotes)))

        await interaction.message.edit(embed=embed, view=self)

class DisabledVotingView(nextcord.ui.View):
    def __init__(self, upvotes, downvotes):
        super().__init__(timeout=None)
        self.add_item(nextcord.ui.Button(label=upvotes, emoji="👍", style=nextcord.ButtonStyle.green, disabled=True))
        self.add_item(nextcord.ui.Button(label=downvotes, emoji="👍", style=nextcord.ButtonStyle.red, disabled=True))

class EditSuggestion(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Edit Suggestion", timeout=600)
        
        self.description = nextcord.ui.TextInput(
            label = "Type the description of your suggestion",
            placeholder = ":D",
            style = nextcord.TextInputStyle.paragraph,
            min_length=1,
            required=True
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction):
        self.description = self.description.value
        self.stop()


class SuggestionAcceptDeny(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Suggestion Verdict", timeout=None)
        self.reason = nextcord.ui.TextInput(
                label = "Reason",
                placeholder = "Reason for verdict",
                style=nextcord.TextInputStyle.paragraph,
                min_length=1,
                max_length=255,
                required=False
            )
        self.add_item(self.reason)


    async def callback(self, interaction: nextcord.Interaction):
        if not self.reason.value:
            self.reason=""
        else:
            self.reason = self.reason.value
        self.stop()

class SuggestionManagementUser(nextcord.ui.View):
    def __init__(self, org_msg:nextcord.Message):
        super().__init__()
        self.value = None
        self.org_msg = org_msg

    @nextcord.ui.button(label = "Edit Suggestion", style = nextcord.ButtonStyle.blurple)
    async def edit_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        edit_suggestion_modal = EditSuggestion()
        await interaction.response.send_modal(edit_suggestion_modal)
        await edit_suggestion_modal.wait()

        embed = self.org_msg.embeds[0]
        embed.description = edit_suggestion_modal.description
        
        await self.org_msg.edit(embed=embed)

    @nextcord.ui.button(label = "Delete Suggestion", style = nextcord.ButtonStyle.red)
    async def delete_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        data = Bot.db.get_data("suggestions_info", message_id=self.org_msg.id)
        Bot.db.delete_data("suggestions_info", data[0])

        await self.org_msg.delete()
        await interaction.response.defer(with_message=False)
        await interaction.edit_original_message(embed=nextcord.Embed(title="Suggestion Deleted", description=f"You have deleted your suggestion.", colour=COLOUR_BAD), view=None)
        self.value=False
        self.stop()

    @nextcord.ui.button(label="Done", style=nextcord.ButtonStyle.grey)
    async def finish_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=False)
        await interaction.delete_original_message()
        self.stop()

        self.clear_items()

    async def on_timeout(self):
        self.stop()

class SuggestionManagementStaff(nextcord.ui.View):
    def __init__(self, org_msg: nextcord.Message):
        super().__init__()
        self.value = None
        self.org_msg = org_msg

    @nextcord.ui.button(label = "Accept Suggestion", style = nextcord.ButtonStyle.green)
    async def accept_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        data: List[SuggestionsInfo] = Bot.db.get_data("suggestions_info", message_id=self.org_msg.id)
        reason = SuggestionAcceptDeny()
        await interaction.response.send_modal(modal=reason)
        await reason.wait()
        reason = reason.reason
        data[0].status = "Accepted"
        data = Bot.db.update_data("suggestions_info", data[0])
        
        server_settings: List[SuggestionsMain] = Bot.db.get_data("suggestions", channel_id=interaction.channel.id)
        if server_settings[0].accept_channel:
            acceptchannel = interaction.guild.get_channel(int(server_settings[0].accept_channel))
            orgembed = self.org_msg.embeds[0]
            embed = nextcord.Embed(title="Suggestion", description=f"{orgembed.description}", colour=COLOUR_GOOD)
            embed.set_author(name=orgembed.author.name, icon_url=orgembed.author.icon_url)
            embed.add_field(name=f"Status", value=f"Accepted")
            embed.add_field(name=f"Accepted by {interaction.user}", value=f"{reason}", inline=False)
            embed.set_image(self.org_msg.embeds[0].image.url)
            await self.org_msg.delete()
            await acceptchannel.send(embed=embed, view=DisabledVotingView(upvotes=len(data.upvotes), downvotes=len(data.downvotes)))
        else:
            orgembed = self.org_msg.embeds[0]
            embed = nextcord.Embed(title="Suggestion", description=f"{orgembed.description}", colour=COLOUR_GOOD)
            embed.set_author(name=orgembed.author.name, icon_url=orgembed.author.icon_url)
            embed.add_field(name=f"Status", value=f"Accepted")
            embed.add_field(name=f"Accepted by {interaction.user}", value=f"{reason}", inline=False)
            embed.set_image(self.org_msg.embeds[0].image.url)
            await self.org_msg.edit(embed=embed, view=DisabledVotingView(upvotes=len(data.upvotes), downvotes=len(data.downvotes)))
        await interaction.delete_original_message()


        
    
    @nextcord.ui.button(label = "Deny Suggestion", style = nextcord.ButtonStyle.red)
    async def deny_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        data: List[SuggestionsInfo] = Bot.db.get_data("suggestions_info", message_id=self.org_msg.id)
        reason = SuggestionAcceptDeny()
        await interaction.response.send_modal(modal=reason)
        await reason.wait()
        reason = reason.reason
        data[0].status = "Denied"
        data = Bot.db.update_data("suggestions_info", data[0])
        
        server_settings: List[SuggestionsMain] = Bot.db.get_data("suggestions", channel_id=interaction.channel.id)
        if server_settings[0].deny_channel:
            acceptchannel = interaction.guild.get_channel(int(server_settings[0].deny_channel))
            orgembed = self.org_msg.embeds[0]
            embed = nextcord.Embed(title="Suggestion", description=f"{orgembed.description}", colour=COLOUR_BAD)
            embed.set_author(name=orgembed.author.name, icon_url=orgembed.author.icon_url)
            embed.add_field(name=f"Status", value=f"Denied")
            embed.add_field(name=f"Denied by {interaction.user}", value=f"{reason}", inline=False)
            embed.set_image(self.org_msg.embeds[0].image.url)
            await self.org_msg.delete()
            await acceptchannel.send(embed=embed, view=DisabledVotingView(upvotes=len(data.upvotes), downvotes=len(data.downvotes)))
        else:
            orgembed = self.org_msg.embeds[0].description
            orgembed = self.org_msg.embeds[0]
            embed = nextcord.Embed(title="Suggestion", description=f"{orgembed.description}", colour=COLOUR_BAD)
            embed.set_author(name=orgembed.author.name, icon_url=orgembed.author.icon_url)
            embed.add_field(name=f"Status", value=f"Denied")
            embed.add_field(name=f"Denied by {interaction.user}", value=f"{reason}", inline=False)
            embed.set_image(self.org_msg.embeds[0].image.url)
            await self.org_msg.edit(embed=embed, view=DisabledVotingView(upvotes=len(data.upvotes), downvotes=len(data.downvotes)))
        await interaction.delete_original_message()

    @nextcord.ui.button(label = "Delete Suggestion", style = nextcord.ButtonStyle.grey)
    async def delete_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        data = Bot.db.get_data("suggestions_info", message_id=self.org_msg.id)
        Bot.db.delete_data("suggestions_info", data[0])
        await self.org_msg.delete()
        await interaction.response.defer(with_message=False)
        await interaction.edit_original_message(embed=nextcord.Embed(title="Suggestion Deleted", description=f"You have deleted the suggestion.", colour=COLOUR_BAD), view=None)
        self.stop()
        


    @nextcord.ui.button(label="Done", style=nextcord.ButtonStyle.grey)
    async def finish_suggestion(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=False)
        await interaction.delete_original_message()
        self.stop()

        self.clear_items()

    async def on_timeout(self):
        self.stop()
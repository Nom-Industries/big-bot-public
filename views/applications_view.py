import nextcord
from nextcord import Interaction
from .confirm_deny import Confirm
from bot import Bot
from utils import *
import asyncio
from constants import COLOUR_GOOD, COLOUR_MAIN, COLOUR_BAD
from db_handler.schemas import *
from typing import List, Union

class ApplicationCreateView(nextcord.ui.View):
    def __init__(self, embed, org_user, app_name, client):
        super().__init__()
        self.embed = embed
        self.org_user = org_user
        self.client = client
        self.app_name = app_name[:100]
        self.questions = []

    @nextcord.ui.button(label="Add Question", style=nextcord.ButtonStyle.blurple)
    async def add_application_question(self, button: nextcord.ui.Button, interaction:Interaction):
        if len(self.questions) >=10:
            embed = create_warning_embed(title=f"Max questions reached", description=f"You have reached the maximum amount of questions for 1 application. Click the Finish Application button to finish the application with the current questions.")
            await interaction.send(embed=embed, ephemeral=True)
            return
        add_question_modal = ApplicationAddQuestionModal()
        await interaction.response.send_modal(add_question_modal)
        await add_question_modal.wait()
        if add_question_modal.question in self.questions:
            await interaction.send(embed=create_warning_embed(title=f"Question already added", description=f"That question has already been added."))
            return
        if len(self.questions) == 0:
            self.embed.set_field_at(0, name=f"Question {len(self.questions)+1}", value=f"{add_question_modal.question[:150]}")
        else:
            self.embed.add_field(name=f"Question {len(self.questions)+1}", value=f"{add_question_modal.question}")
        self.questions.append(add_question_modal.question)
        self.embed.description = f"You are able to add `{10-len(self.questions)}` new questions."
        await interaction.message.edit(embed=self.embed)

    @nextcord.ui.button(label=f"Finish Application", style=nextcord.ButtonStyle.blurple)
    async def finish_application_creation(self, button: nextcord.ui.Button, interaction:Interaction):
        role_selected = Role_Select(interaction.user.id)
        embed = nextcord.Embed(title="Add required roles", description="Add roles which users will be required to have before they submit an application", colour=COLOUR_MAIN)
        await interaction.message.edit(embed=embed, view=role_selected)
        await role_selected.wait()
        selected_role = role_selected.values
        roles_chosen = []
        for role in selected_role:
            roles_chosen.append(role.id)
        channel_selected = Channel_Select(interaction.user.id)
        embed = nextcord.Embed(title="Add log channel", description="Add a channel which applications will get sent to when they are submitted", colour=COLOUR_MAIN)
        await interaction.message.edit(embed=embed, view=channel_selected)
        await channel_selected.wait()
        selected_channel= None
        if len(channel_selected.values) >0:
            selected_channel= channel_selected.values[0].id

        category_select = Category_Select(interaction.user.id)
        embed = nextcord.Embed(title="Create Channel for Application", description="If you want to, you can select a category for the bot to create a channel when a user submits an application so you can communicate with the applicant through the channel", colour=COLOUR_MAIN)
        await interaction.message.edit(embed=embed, view=category_select)
        await category_select.wait()
        category_select = category_select.values[0].id if len(category_select.values) > 0 else None

        await interaction.message.edit(embed=nextcord.Embed(description=f"We're finishing things up on our end. This shouldn't take too long...", colour=COLOUR_MAIN), view=None)
        app_id = generate_random_string()
        data: List[ApplicationQuestions] = Bot.db.get_data(table="application_questions", app_id=app_id)
        while data:
            app_id = generate_random_string()
            data: List[ApplicationQuestions] = Bot.db.get_data(table="application_questions", app_id=app_id)
        data: List[ApplicationQuestions] = Bot.db.create_data(table="application_questions", app_id=app_id, guild_id=interaction.guild.id, name=self.app_name, questions=self.questions, roles_required=roles_chosen if len(roles_chosen) > 0 else [], channel_to_send=selected_channel, enabled=True, category=category_select)
        await interaction.message.edit(embed=create_success_embed(title=f"Application Created", description=f"The application was successfully created with ID `{app_id}`. Users can run ``/application submit`` to fill it out"))

    async def on_interaction(self, interaction: Interaction) -> bool:
        return self.org_user.id == interaction.user.id


    






class ApplicationAddQuestionModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title=f"Add Question")
        self.question = nextcord.ui.TextInput(
            label="What is the question?",
            placeholder="e.g. What BigBot level are you?",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=250,
            required=True
        )
        self.add_item(self.question)

    async def callback(self, interaction: Interaction):
        self.question = self.question.value
        self.stop()
    
class ApplicationChangeQuestionModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title=f"Change Question")
        self.question = nextcord.ui.TextInput(
            label="What is the new question?",
            placeholder="e.g. What BigBot level are you?",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=250,
            required=True
        )
        self.add_item(self.question)

    async def callback(self, interaction: Interaction):
        self.question = self.question.value
        self.stop()

class ApplicationChangeQuestionPosModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title=f"Edit Question Position")
        self.new_pos = nextcord.ui.TextInput(
            label="What is the new position of the question?",
            placeholder="e.g. 4",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=2,
            required=True
        )
        self.add_item(self.new_pos)

    async def callback(self, interaction: Interaction):
        self.new_pos = self.new_pos.value
        self.stop()



class ChannelList(nextcord.ui.ChannelSelect):
    def __init__(self, org_user: int):
        super().__init__(custom_id="channel_list_app", placeholder="Select channel", min_values=1, max_values=1, row=1)
        self.org_user = org_user

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values = self.values

    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id

class RoleList(nextcord.ui.RoleSelect):
    def __init__(self, org_user: int):
        super().__init__(custom_id="role_list_app", placeholder="Select role", min_values=1, max_values=25, row=1)
        self.org_user = org_user

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values = self.values

    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id
    
class CategoryList(nextcord.ui.ChannelSelect):
    def __init__(self, org_user: int):
        super().__init__(channel_types=[nextcord.ChannelType.category], custom_id="category_list_app", placeholder="Select category", min_values=0, max_values=1, row=1)
        self.org_user = org_user

    async def callback(self, interaction: nextcord.Interaction):
        self.view.values = self.values

    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id

class Channel_Select(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=120)
        self.add_item(ChannelList(org_user))
        self.org_user = org_user
        self.values = []
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.values:
            self.values = []
            self.stop()
            self.clear_items()
    
        self.stop()
        self.clear_items()

    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id

class Role_Select(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=120)
        self.add_item(RoleList(org_user))
        self.org_user = org_user
        self.values = []
    
    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.values:
            self.values = []
            self.stop()
            self.clear_items()
    
        self.stop()
        self.clear_items()

    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id
    
class Category_Select(nextcord.ui.View):
    def __init__(self, org_user: int):
        super().__init__(timeout=120)
        self.add_item(CategoryList(org_user))
        self.org_user = org_user
        self.values = []

    @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.values:
            self.values = []
            self.stop()
            self.clear_items()
    
        self.stop()
        self.clear_items()

    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id

class SelectOptions(nextcord.ui.Select):
    def __init__(self, option_titles: list, options_description: list = None, option_values: list = None, min_val: int = 1, max_val: int = 1):
        super().__init__(options=[nextcord.SelectOption(label=option_titles[i], description=options_description[i] if options_description else option_values[i], value=option_values[i]) for i in range(len(option_titles))], min_values=min_val, max_values=max_val)
    
    async def callback(self, interaction: nextcord.Interaction):
        self.view.clicked.extend(self.values)

class Application_List_Options(nextcord.ui.View):
    def __init__(self, org_user: int, option_titles: list, options_description: list = None, option_values: list = None, min_val: int = 1, max_val: int = 1):
        super().__init__(timeout=600)

        self.org_user = org_user

        self.clicked = []
        self.min_val = min_val

        for i in range(0, len(option_titles), 25):
            self.add_item(SelectOptions(option_titles[i:i+25], options_description[i:i+25] if options_description else None, option_values[i:i+25], min_val, max_val))
        
    @nextcord.ui.button(label="Complete", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, interaction: nextcord.Interaction, button: nextcord.ui.Button):
        if self.min_val > 0 and not self.clicked:
            return False
        
        else:
            self.stop()

    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id
    
class ApplicationAnswerQuestionModal(nextcord.ui.Modal):
    def __init__(self, question):
        super().__init__(title=f"Application")
        self.question = nextcord.ui.TextInput(
            label=question[:45],
            placeholder="",
            style=nextcord.TextInputStyle.paragraph,
            min_length=1,
            max_length=2000,
            required=True
        )
        self.add_item(self.question)

    async def callback(self, interaction: Interaction):
        self.answer = self.question.value
        self.stop()


class ApplicationAnswerQuestion(nextcord.ui.View):
    def __init__(self, question):
        super().__init__(timeout=600)
        self.question = question
        self.answer = ""

    @nextcord.ui.button(label="Answer Question", style=nextcord.ButtonStyle.green)
    async def add_application_question(self, button: nextcord.ui.Button, interaction:Interaction):
        answer_modal = ApplicationAnswerQuestionModal(question=self.question)
        await interaction.response.send_modal(answer_modal)
        await answer_modal.wait()
        self.answer = answer_modal.answer
        self.stop()

class VerdictInput(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Application Verdict", timeout=None)
        self.reason = nextcord.ui.TextInput(
            label = "Reason",
            placeholder = "Reason for your verdict (Can be left blank)",
            style=nextcord.TextInputStyle.paragraph,
            min_length=1,
            max_length=2500,
            required=False
        )
        self.add_item(self.reason)



    async def callback(self, interaction: nextcord.Interaction):
        if not self.reason.value:
            self.reason = "No Reason Given"
        else:
            self.reason = self.reason.value
        self.stop()

class ApplicationVerdicts(nextcord.ui.View):
    def __init__(self, client):
        self.client = client
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Accept", style=nextcord.ButtonStyle.green, row=0, custom_id="accept_application")
    async def accept(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        embed_footer = embed.footer.text.replace(" ", "").split("|")
        
        applicant = interaction.guild.get_member(int(embed_footer[0]))
        if not applicant:
            await interaction.send(embed=create_warning_embed(title=f"Couldn't find member", description=f"I couldn't find that member in the member list. They must have left! I have removed their application from the database"), ephemeral=True)
            Bot.db.delete_data(table="application_responses", app_id=embed_footer[1])
            return

        app_id = embed_footer[1]
        main_app_id = embed_footer[2]
        app_name = ' '.join(embed.title.split(" ")[1:-1])

        verdict = VerdictInput()
        await interaction.response.send_modal(verdict)
        await verdict.wait()
        verdictreason = verdict.reason
        
        app: List[ApplicationAnswers] = Bot.db.get_data(table="application_responses", app_id=app_id)

        if app[0].verdict in (True, False):
            await interaction.send(embed=create_error_embed(title=f"This application has already revieved a verdict", description=f"This application was `{'Accepted' if app[0].verdict else 'Denied'}` by <@{app[0].mod_id}> for `{app[0].reason}`"), ephemeral=True)
            await interaction.message.delete()
            return
        
        try:
            await applicant.send(embed=nextcord.Embed(title=f"Application Accepted", description=f"Your **{app_name}** Application in **{interaction.guild.name}** was accepted\n\n{verdictreason}\n\nApp ID: `{app_id}`", colour=COLOUR_GOOD))
        except:
            pass
        
        app[0].verdict = True
        app[0].reason = verdictreason
        app[0].mod_id = interaction.user.id

        Bot.db.update_data(table="application_responses", data=app[0])

        embed = interaction.message.embeds[0]
        embed.set_field_at(index=len(embed.fields)-1, name="Verdict", value="Accepted", inline=False)
        embed.add_field(name="Reason", value=verdictreason, inline=False)
        embed.add_field(name="Moderator", value=f"{interaction.user.mention}", inline=False)
        embed.colour = COLOUR_GOOD

        await interaction.edit_original_message(embed=embed, view=None)

        roleselect = Role_Select(org_user=interaction.user.id)
        msg = await interaction.send(embed=create_success_embed(title=f"Application Accepted", description=f"You accepted {applicant.mention}'s application (App ID: `{app_id}`). You can select below which roles you want to give them (Just hit submit if you don't want to give any)"), view=roleselect, ephemeral=True)
        await roleselect.wait()
        await applicant.add_roles(*roleselect.values, atomic=False)
        await msg.edit(embed=create_success_embed(title=f"Application Accepted", description=f"You accepted {applicant.mention}'s application with reason `{verdictreason}`"), view=None)

        if app[0].channel_id:
            channel = interaction.guild.get_channel(int(app[0].channel_id))
            await channel.delete()

    @nextcord.ui.button(label="Deny", style=nextcord.ButtonStyle.red, row=0, custom_id="deny_application")
    async def deny(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        embed_footer = embed.footer.text.replace(" ", "").split("|")
        
        applicant = interaction.guild.get_member(int(embed_footer[0]))
        if not applicant:
            await interaction.send(embed=create_warning_embed(title=f"Couldn't find member", description=f"I couldn't find that member in the member list. They must have left! I have removed their application from the database"), ephemeral=True)
            Bot.db.delete_data(table="application_responses", app_id=embed_footer[1])
            return

        app_id = embed_footer[1]
        main_app_id = embed_footer[2]
        app_name = ' '.join(embed.title.split(" ")[1:-1])

        verdict = VerdictInput()
        await interaction.response.send_modal(verdict)
        await verdict.wait()
        verdictreason = verdict.reason
        
        app: List[ApplicationAnswers] = Bot.db.get_data(table="application_responses", app_id=app_id)

        if app[0].verdict in (True, False):
            await interaction.send(embed=create_error_embed(title=f"This application has already revieved a verdict", description=f"This application was `{'Accepted' if app[0].verdict else 'Denied'}` by <@{app[0].mod_id}> for `{app[0].reason}`"), ephemeral=True)
            await interaction.message.delete()
            return
        
        try:
            await applicant.send(embed=nextcord.Embed(title=f"Application Denied", description=f"Your **{app_name}** Application in **{interaction.guild.name}** was denied\n\n{verdictreason}\n\nApp ID: `{app_id}`", colour=COLOUR_BAD))
        except:
            pass
        
        app[0].verdict = False
        app[0].reason = verdictreason
        app[0].mod_id = interaction.user.id

        Bot.db.update_data(table="application_responses", data=app[0])

        embed = interaction.message.embeds[0]
        embed.set_field_at(index=len(embed.fields)-1, name="Verdict", value="Denied", inline=False)
        embed.add_field(name="Reason", value=verdictreason, inline=False)
        embed.add_field(name="Moderator", value=f"{interaction.user.mention}", inline=False)
        embed.colour = COLOUR_BAD

        await interaction.edit_original_message(embed=embed, view=None)

        await interaction.send(embed=create_success_embed(title=f"Application Denied", description=f"You denied {applicant.mention}'s application with reason `{verdictreason}`"), ephemeral=True)

        if app[0].channel_id:
            channel = interaction.guild.get_channel(int(app[0].channel_id))
            await channel.delete()



class EditApplications(nextcord.ui.View):
    def __init__(self, org_user: int, applications):
        super().__init__(timeout=600)

        self.applications = applications
        self.clicked = []
        self.org_user = org_user

        self.add_item(SelectOptions(option_titles=[i.name for i in applications], options_description=[f"ID: {i.app_id}" for i in applications], option_values=list(range(1, len(applications)+1))))

    @nextcord.ui.button(label="Select", style=nextcord.ButtonStyle.green, row=0)
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.clicked:
            return False
        
        else:
            selected = self.applications[int(self.clicked[0])-1]
            embed = nextcord.Embed(title=f"Edit Application (App ID: `{selected.app_id}`)", description="Use the buttons below to edit the application", colour=COLOUR_MAIN)
            embed.add_field(name="Name of Application", value=selected.name, inline=False)
            embed.add_field(name="Questions", value=('\n'.join(selected.questions))[:1024], inline=False)
            embed.add_field(name="Required Roles", value=', '.join(f"<@&{i}>" for i in selected.roles_required) if selected.roles_required else "None", inline=False)
            embed.add_field(name="Channel To Send", value=f"<#{selected.channel_to_send}>", inline=False)
            embed.add_field(name="Enabled", value=str(bool(selected.enabled)), inline=False)
            embed.add_field(name="Category", value=f"<#{selected.category}>" if selected.category else "None", inline=False)
            await interaction.edit(embed=embed, view=EditAnApplication(org_user=self.org_user, application=selected))


    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id
    
class EditAppName(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title=f"Edit Application Name")
        self.name = nextcord.ui.TextInput(
            label="What is the new application name",
            placeholder="Enter a name for the application",
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=150,
            required=True
        )
        self.add_item(self.name)

    async def callback(self, interaction: Interaction):
        self.name = self.name.value
        self.stop()


    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user.id == interaction.user.id
    
class EditAnApplication(nextcord.ui.View):
    def __init__(self, org_user: int, application: ApplicationQuestions):
        super().__init__(timeout=600)

        self.application = application
        self.values = []
        self.org_user=org_user
    
    @nextcord.ui.button(label="Edit Name", style=nextcord.ButtonStyle.blurple)
    async def edit_name(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        new_name = EditAppName()
        await interaction.response.send_modal(new_name)
        await new_name.wait()

        self.application.name = new_name.name

        await interaction.send(f"Successfully edited application name to `{new_name.name}`", ephemeral=True)
        await interaction.edit(embed=self.update_embed())

    @nextcord.ui.button(label="Edit Questions", style=nextcord.ButtonStyle.blurple)
    async def edit_questions(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title=f"Edit Questions for {self.application.name}", description="Use the buttons below to rearrange, add, or delete questions\nCurrent questions:\n" + '\n'.join([f"{i+1}. {self.application.questions[i]}" if i != 0 else f"**{i+1}. {self.application.questions[i]}**" for i in range(len(self.application.questions))])  + "\nBold means that question is currently selected and any edits made go on that question. Once you are finished, press complete", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=EditQuestions(org_user=self.org_user, application=self.application))

    @nextcord.ui.button(label="Edit Roles", style=nextcord.ButtonStyle.blurple)
    async def edit_roles(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        role_select = Role_Select(interaction.user.id)
        embed = nextcord.Embed(title="Edit Roles", description=f"Use the select menu to choose your allowed roles that users will be required to have to submit this application", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=role_select)
        await role_select.wait()
        roles_selected = []
        for role in role_select.values:
            roles_selected.append(role.id)
        self.application.roles_required = roles_selected
        await interaction.send(embed=create_success_embed(title="Required roles changed", description=f"Required roles changed to {', '.join(f'<@&{i}>' for i in self.application.roles_required) if self.application.roles_required else 'None'}"), ephemeral=True)
        await interaction.edit(embed=self.update_embed(), view=EditAnApplication(org_user=interaction.user.id, application=self.application))

    @nextcord.ui.button(label="Edit Channel", style=nextcord.ButtonStyle.blurple)
    async def edit_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        channel_select = Channel_Select(org_user=self.org_user)
        embed = nextcord.Embed(title="Select Channel", description=f"Select channel where to send applications made by users for this application. Currently selected channel is <#{self.application.channel_to_send}>", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=channel_select)
        await channel_select.wait()

        if len(channel_select.values) > 0:
            self.application.channel_to_send = channel_select.values[0].id
            await interaction.send(embed=create_success_embed(title="Channel Changed!", description=f"Channel changed to {channel_select.values[0].mention}"), ephemeral=True)
        await interaction.edit(embed=self.update_embed(), view=EditAnApplication(org_user=interaction.user.id, application=self.application))

    @nextcord.ui.button(label="Enabled", style=nextcord.ButtonStyle.blurple)
    async def enabled(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.application.enabled = not self.application.enabled

        await interaction.send(f"Application is now `{'enabled' if self.application.enabled else 'disabled'}`", ephemeral=True)
        await interaction.edit(embed=self.update_embed())

    @nextcord.ui.button(label="Category", style=nextcord.ButtonStyle.blurple)
    async def category(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        category_select = Category_Select(interaction.user.id)
        embed = nextcord.Embed(title="Create Channel for Application", description="If you want to, you can select a category for the bot to create a channel when a user submits an application so you can communicate with the applicant through the channel", colour=COLOUR_MAIN)
        await interaction.edit(embed=embed, view=category_select)
        await category_select.wait()
        category_select = category_select.values[0].id if len(category_select.values) > 0 else None

        self.application.category = category_select

        await interaction.send(f"Application Category channel is now: {f'<#{category_select}>' if category_select else 'None'}")
        await interaction.edit(embed=self.update_embed(), view=EditAnApplication(org_user=interaction.user.id, application=self.application))
    
    @nextcord.ui.button(label="Delete", style=nextcord.ButtonStyle.red)
    async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        confirm = Confirm(self.org_user)
        await interaction.edit(embed=create_warning_embed(title="Delete Application", description=f"Confirm that you want to delete the application, `{self.application.name} (ID: {self.application.app_id})`, by clicking the checkmark below or cancel by clicking the cross"), view=confirm)
        await confirm.wait()

        if confirm.value:
            self.application.roles_required = None if len(self.application.roles_required) == 0 else self.application.roles_required
            Bot.db.delete_data(table="application_questions", data=self.application)

            await interaction.edit(embed=create_success_embed(title="Applicaton deleted", description=f"The application, `{self.application.name}`, has been deleted"), view=None)

        else:
            await interaction.edit(embed=create_warning_embed(title="Action canceled"), view=None)
            await asyncio.sleep(2)
            await interaction.edit(embed=self.update_embed(), view=EditAnApplication(org_user=interaction.user.id, application=self.application))

    @nextcord.ui.button(label="Complete", style=nextcord.ButtonStyle.green)
    async def complete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        Bot.db.update_data(table="application_questions", data=self.application)
        
        await interaction.edit(embed=create_success_embed(title="All changes saved!", description="All your edits have been updated to the application!"), view=None)

    def update_embed(self):
        embed = nextcord.Embed(title=f"Edit Application (App ID: `{self.application.app_id}`)", description="Use the buttons below to edit the application", colour=COLOUR_MAIN)
        embed.add_field(name="Name of Application", value=self.application.name, inline=False)
        embed.add_field(name="Questions", value=('\n'.join(self.application.questions))[:1024], inline=False)
        embed.add_field(name="Required Roles", value=', '.join(f"<@&{i}>" for i in self.application.roles_required) if self.application.roles_required else "None", inline=False)
        embed.add_field(name="Channel To Send", value=f"<#{self.application.channel_to_send}>", inline=False)
        embed.add_field(name="Enabled", value=str(bool(self.application.enabled)), inline=False)
        embed.add_field(name="Category", value=f"<#{self.application.category}>" if self.application.category else "None", inline=False)
        return embed
    

    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id

class EditQuestions(nextcord.ui.View):
    def __init__(self, org_user: int, application , cur_pos: int = 0):
        super().__init__()

        self.application = application
        self.cur_pos = cur_pos
        self.org_user=org_user

        self.add_item(Select_Question(questions=application.questions))

    @nextcord.ui.button(emoji="<:left_arrow:1049429857488093275>", row=1, style=nextcord.ButtonStyle.blurple)
    async def previous_question(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.cur_pos > 0:
            self.cur_pos -= 1
        
        await interaction.edit(embed=self.update_embed(interaction))

    @nextcord.ui.button(emoji="<:right_arrow:1049430086257999882>", row=1, style=nextcord.ButtonStyle.blurple)
    async def next_question(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.cur_pos < len(self.application.questions) - 1:
            self.cur_pos += 1
        
        await interaction.edit(embed=self.update_embed(interaction))

    @nextcord.ui.button(label="Edit Position", row=2, style=nextcord.ButtonStyle.gray)
    async def edit_position(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.application.questions:
            await interaction.send(embed=create_warning_embed(title="No questions!", description="You must have at least one question in an application"), ephemeral=True)
            return
        
        new_pos = ApplicationChangeQuestionPosModal()
        await interaction.response.send_modal(new_pos)
        await new_pos.wait()
        
        try:
            if int(new_pos.new_pos) < 1 or int(new_pos.new_pos) > len(self.application.questions):
                await interaction.send(f"Invalid position! Please send a position between 1 and {len(self.application.questions)}", ephemeral=True)
                return
        
        except:
            await interaction.send(f"Invalid position! Please send a position between 1 and {len(self.application.questions)}", ephemeral=True)
            return

        question = self.application.questions[self.cur_pos]
        self.application.questions[self.cur_pos] = self.application.questions[int(new_pos.new_pos)-1]
        self.application.questions[int(new_pos.new_pos)-1] = question

        old_pos = self.cur_pos+1

        self.cur_pos = int(new_pos.new_pos)-1

        await interaction.edit(embed=self.update_embed(interaction), view=EditQuestions(org_user=self.org_user, application=self.application, cur_pos=self.cur_pos))
        await interaction.send(f"The question, `{question}`, has been moved from {old_pos} to {new_pos.new_pos}!", ephemeral=True)

    @nextcord.ui.button(label="Create Question", row=3, style=nextcord.ButtonStyle.green)
    async def create_question(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        new_question = ApplicationAddQuestionModal()
        await interaction.response.send_modal(new_question)
        await new_question.wait()

        if new_question.question.lower() in [i.lower() for i in self.application.questions]:
            await interaction.send("There is a question already in this application like this. Please try a different question", ephemeral=True)
            return
        
        self.application.questions.append(new_question.question)
        self.cur_pos = len(self.application.questions)-1

        await interaction.edit(embed=self.update_embed(interaction), view=EditQuestions(org_user=self.org_user, application=self.application, cur_pos=self.cur_pos))
        await interaction.send(f"New question added!", ephemeral=True)

    @nextcord.ui.button(label="Change Question", row=3, style=nextcord.ButtonStyle.gray)
    async def rename_question(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.application.questions:
            await interaction.send(embed=create_warning_embed(title="No questions!", description="You must have at least one question in an application"), ephemeral=True)
            return
        
        new_name = ApplicationChangeQuestionModal()
        await interaction.response.send_modal(new_name)
        await new_name.wait()
        
        if new_name.question.lower() in [i.lower() for i in self.application.questions]:
            await interaction.send("There is a question already in this application like this. Please try a different question", ephemeral=True)
            return
        
        self.application.questions[self.cur_pos] = new_name.question

        await interaction.edit(embed=self.update_embed(interaction), view=EditQuestions(org_user=self.org_user, application=self.application, cur_pos=self.cur_pos))
        await interaction.send(f"Question successfully changed!", ephemeral=True)
    
    @nextcord.ui.button(label="Delete Question", row=3, style=nextcord.ButtonStyle.red)
    async def delete_question(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.application.questions:
            await interaction.send(embed=create_warning_embed(title="No questions!", description="You must have at least one question in an application"), ephemeral=True)
            return
        
        confirm = Confirm(self.org_user)
        await interaction.send(embed=create_warning_embed(title="Delete question", description=f"Confirm that you want to delete the question, `{self.application.questions[self.cur_pos]}`, by clicking the checkmark below or cancel by clicking the cross"), view=confirm, ephemeral=True)
        await confirm.wait()

        if confirm.value:
            del self.application.questions[self.cur_pos]
            self.cur_pos = self.cur_pos - 1 if self.cur_pos != 0 else self.cur_pos

            await interaction.edit_original_message(embed=create_success_embed(title="Question deleted!"), view=None)

            await interaction.edit(embed=self.update_embed(interaction), view=EditQuestions(org_user=self.org_user, application=self.application, cur_pos=self.cur_pos))

        else:
            await interaction.edit_original_message(embed=create_warning_embed(title="Action canceled"), view=None)

    @nextcord.ui.button(label="Complete", row=4, style=nextcord.ButtonStyle.green)
    async def complete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.application.questions:
            await interaction.send(embed=create_warning_embed(title="No questions!", description="You must have at least one question in an application"), ephemeral=True)
            return
        
        embed = nextcord.Embed(title=f"Edit Application (App ID: `{self.application.app_id}`)", description="Use the buttons below to edit the application", colour=COLOUR_MAIN)
        embed.add_field(name="Name of Application", value=self.application.name, inline=False)
        embed.add_field(name="Questions", value=('\n'.join(self.application.questions))[:1024], inline=False)
        embed.add_field(name="Required Roles", value=', '.join(f"<@&{i}>" for i in self.application.roles_required) if self.application.roles_required else "None", inline=False)
        embed.add_field(name="Channel To Send", value=f"<#{self.application.channel_to_send}>", inline=False)
        embed.add_field(name="Enabled", value=str(bool(self.application.enabled)), inline=False)
        await interaction.edit(embed=embed, view=EditAnApplication(org_user=self.org_user, application=self.application))

    def update_embed(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        embed.description = "Use the buttons below to rearrange, add, or delete questions\nCurrent questions:\n" + '\n'.join([f"{i+1}. {self.application.questions[i]}" if i != self.cur_pos else f"**{i+1}. {self.application.questions[i]}**" for i in range(len(self.application.questions))]) + "\nBold means that question is currently selected and any edits made go on that question.  Once you are finished, press complete"
        return embed
    
    async def interaction_check(self, interaction:Interaction) -> bool:
        return self.org_user == interaction.user.id

class Select_Question(nextcord.ui.Select):
    def __init__(self, questions: list):
        super().__init__(placeholder="Select question", options=[nextcord.SelectOption(label=value[:100], description=index+1, value=index+1) for index, value in enumerate(questions)])
    
    async def callback(self, interaction: nextcord.Interaction):
        self.view.cur_pos = int(self.values[0])-1
        await interaction.edit(embed=self.view.update_embed(interaction))
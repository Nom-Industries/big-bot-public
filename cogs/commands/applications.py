from typing import List
import nextcord
import os, asyncio
from nextcord import SlashOption
from nextcord.ext import commands
from bot.bot import Bot
from utils.utils import color_message, create_success_embed, create_warning_embed, create_error_embed, generate_random_string
from views import ApplicationCreateView, Application_List_Options, ApplicationAnswerQuestion, ApplicationVerdicts, Confirm, EditApplications
from db_handler.schemas import *
from constants import COLOUR_BAD, COLOUR_GOOD, COLOUR_MAIN 

currently_applying = []


class Applications(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client
    
    @nextcord.slash_command(name="application", description="Application base")
    async def application(self, interaction: nextcord.Interaction):
        pass


    # Administrator commands

    @application.subcommand(name=f"create", description=f"Create a new application")
    async def application_create(self,
            interaction:nextcord.Interaction,
            app_name: str = SlashOption(
                name=f"name",
                description=f"Name of the application",
                required=True
            )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"), ephemeral=True)
            return
        
        applications: List[ApplicationQuestions] = Bot.db.get_data(table="application_questions", guild_id=interaction.guild.id)
        if applications:
            if len(applications) >=5:
                await interaction.send(embed=create_error_embed(title=f"Max applications reached", description=f"You have already created the max amount of applications (`5`). You can edit/delete previously created ones using `/application manage`"))
                return
        embed = nextcord.Embed(title=f"New Application", description=f"You are able to add `10` new questions.", colour=COLOUR_MAIN)
        embed.add_field(name=f"Question 1", value=f"Click the add questions button to add a question here.")
        create_view = ApplicationCreateView(embed, interaction.user, app_name, self.client)
        await interaction.send(embed=embed, view=create_view)

    @application.subcommand(name=f"manage", description=f"Manage your previous applications")
    async def application_manage(self, interaction:nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"), ephemeral=True)
            return

        applications: List[ApplicationQuestions] = Bot.db.get_data(table="application_questions", guild_id=interaction.guild.id)

        if not applications:
            await interaction.send(embed=create_warning_embed(title="No applications!", description=f"There are no applications for {interaction.guild.name}. Please use `/applications new` to make a new application"), ephemeral=True)
            return
        
        embed = nextcord.Embed(title="Edit Applications", description="Select an application to edit", colour=COLOUR_MAIN)
        await interaction.send(embed=embed, view=EditApplications(org_user=interaction.user.id, applications=applications))


    # Moderator commands

    @application.subcommand(name=f"refresh", description=f"Refresh an application (Resend to the application channel)")
    async def application_refresh(self, interaction: nextcord.Interaction, member: nextcord.Member = nextcord.SlashOption(name="member", description="Member's applications to backup", required=True)):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"), ephemeral=True)
            return

        user_apps: List[ApplicationAnswers] = Bot.db.get_data(table="application_responses", user_id=member.id)
        guild_apps: List[ApplicationQuestions] = Bot.db.get_data(table="application_questions", guild_id=interaction.guild.id)

        if not user_apps:
            await interaction.send(embed=create_warning_embed(title="No Applications!", description=f"{member.mention} has no applications"))
            return

        list_apps = Application_List_Options(org_user=interaction.user.id, option_titles=[next(app.name for app in guild_apps if app.app_id == user_app.app_name) for user_app in user_apps], option_values=[f"{user_app.app_id}{' - Denied' if user_app.verdict is False else (' - Accepted' if user_app.verdict else '')}" for user_app in user_apps])
        await interaction.send(embed=nextcord.Embed(title="Select Application", description="Select which application to restore", colour=COLOUR_MAIN), view=list_apps, ephemeral=True)
        await list_apps.wait()

        backup_app: ApplicationAnswers = [i for i in user_apps if i.app_id == list_apps.clicked[0].replace(" - Denied", "").replace(" - Accepted", "")][0]
        overall_backup_app: ApplicationQuestions = [i for i in guild_apps if i.app_id == backup_app.app_name][0]

        channel_to_send = interaction.guild.get_channel(int(overall_backup_app.channel_to_send))
        if not channel_to_send:
            await interaction.edit_original_message(embed=create_error_embed(title="Application Error!", description="Sorry, the server administrators have not set up a channel for receiving these applications. Please ask the server administrators to do so to allow applications to be submitted"), view=None)
            return

        embed = nextcord.Embed(title=f"{member}'s {overall_backup_app.name + ' Application' if 'app' not in overall_backup_app.name else ''}", colour=COLOUR_MAIN if backup_app.verdict is None else COLOUR_GOOD if backup_app.verdict else COLOUR_BAD)

        pastecontent = ""
        j=0

        for i in backup_app.q_a:
            embed.add_field(name=i[:50], value=backup_app.q_a[i][:100], inline=False)
            pastecontent += f"Question {j+1} - {i}:\n\n{backup_app.q_a[i]}\n\n\n"
            j+=1


        if backup_app.verdict is not None:
            embed.add_field(name="Verdict", value="Accepted" if backup_app.verdict else "Denied", inline=False)
            embed.add_field(name="Reason", value=backup_app.reason, inline=False)
            embed.add_field(name="Moderator", value=f"<@{backup_app.mod_id}>")

        f = open(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "a")
        f.write(pastecontent)
        f.close()
        embed.description = f"View the full application in the text document attached"
        embed.set_footer(text=f"{member.id} | {backup_app.app_id} | {overall_backup_app.app_id}")
        try:
            msg = await channel_to_send.send(embed=embed, view=ApplicationVerdicts(self.client) if backup_app.verdict is None else None, file=nextcord.File(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "Application.txt"))
            await interaction.edit_original_message(embed=create_success_embed(title="Success!", description=f"The application has been successfully restored and set in {channel_to_send.mention}\n[Jump to Application]({msg.jump_url})"), view=None)
            
            if overall_backup_app.category:
                channel: nextcord.CategoryChannel = interaction.guild.get_channel(int(overall_backup_app.category))
                app_channel = await channel.create_text_channel(name=f"{overall_backup_app.name}-{member.id}")
                await app_channel.send(embed=embed, view=ApplicationVerdicts(self.client) if backup_app.verdict is None else None, file=nextcord.File(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "Application.txt"))

        except:
            pass
        os.remove(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt")


    @application.subcommand(name=f"view", description=f"Application view base")
    async def application_view(self, interaction:nextcord.Interaction):
        pass

    @application_view.subcommand(name=f"user", description=f"See a users applications")
    async def application_view_user(self,
        interaction:nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            name=f"user",
            description=f"User to view applications of",
            required=True
        )):
        if not interaction.user.guild_permissions.administrator:
            await interaction.send(embed=create_error_embed(title="Error!", description="You do not have permission to run this command!"), ephemeral=True)
            return

        user_apps: List[ApplicationAnswers] = Bot.db.get_data(table="application_responses", user_id=member.id)
        guild_apps: List[ApplicationQuestions] = Bot.db.get_data(table="application_questions", guild_id=interaction.guild.id)

        if not user_apps:
            await interaction.send(embed=create_warning_embed(title="No Applications!", description=f"{member.mention} has no applications"))
            return

        list_apps = Application_List_Options(org_user=interaction.user.id, option_titles=[next(app.name for app in guild_apps if app.app_id == user_app.app_name) for user_app in user_apps], option_values=[f"{user_app.app_id}{' - Denied' if user_app.verdict is False else (' - Accepted' if user_app.verdict else '')}" for user_app in user_apps])
        await interaction.send(embed=nextcord.Embed(title="Select Application", description="Select which application to restore", colour=COLOUR_MAIN), view=list_apps, ephemeral=True)
        await list_apps.wait()

        backup_app: ApplicationAnswers = [i for i in user_apps if i.app_id == list_apps.clicked[0].replace(" - Denied", "").replace(" - Accepted", "")][0]
        overall_backup_app: ApplicationQuestions = [i for i in guild_apps if i.app_id == backup_app.app_name][0]

        channel_to_send = interaction.guild.get_channel(int(overall_backup_app.channel_to_send))
        if not channel_to_send:
            await interaction.edit_original_message(embed=create_error_embed(title="Application Error!", description="Sorry, the server administrators have not set up a channel for receiving these applications. Please ask the server administrators to do so to allow applications to be submitted"), view=None)
            return

        embed = nextcord.Embed(title=f"{member}'s {overall_backup_app.name + ' Application' if 'app' not in overall_backup_app.name else ''}", colour=COLOUR_MAIN if backup_app.verdict is None else COLOUR_GOOD if backup_app.verdict else COLOUR_BAD)

        pastecontent = ""
        j=0

        print(backup_app)
        print(backup_app.q_a)

        for i in backup_app.q_a:
            embed.add_field(name=i[:50], value=backup_app.q_a[i][:100], inline=False)
            pastecontent += f"Question {j+1} - {i}:\n\n{backup_app.q_a[i]}\n\n\n"
            j+=1


        if backup_app.verdict is not None:
            embed.add_field(name="Verdict", value="Accepted" if backup_app.verdict else "Denied", inline=False)
            embed.add_field(name="Reason", value=backup_app.reason, inline=False)
            embed.add_field(name="Moderator", value=f"<@{backup_app.mod_id}>")

        f = open(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "a")
        f.write(pastecontent)
        f.close()
        embed.description = f"View the full application in the text document attached"
        embed.set_footer(text=f"{member.id} | {backup_app.app_id} | {overall_backup_app.app_id}")
        try:
            msg = await interaction.edit_original_message(embed=embed, view=None, file=nextcord.File(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "Application.txt"))
        except:
            pass
        os.remove(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt")

    # User commands

    @application.subcommand(name=f"submit", description=f"Submit an application")
    async def application_submit(self, interaction:nextcord.Interaction):
        if interaction.user.id in currently_applying:
            await interaction.send(embed=create_error_embed(title=f"You are already submitting an application. Please finish that application before starting a new one."))
            return
        
        await interaction.response.defer(ephemeral=True)
        data: List[ApplicationQuestions] = Bot.db.get_data(table="application_questions", guild_id=interaction.guild.id, enabled=True)
        if not data:
            await interaction.send(embed=create_warning_embed(title="No applications", description="There are no applications for this server"), ephemeral=True)
            return
        
        embed=nextcord.Embed(title=f"Submit an application", description=f"Use the dropdown below to select an application submit. The available applications are:", colour=COLOUR_MAIN)
        user_roles = [i.id for i in interaction.user.roles]
        applications = []

        for i in range(len(data)):
            if not data[i].enabled:
                applications.append(None)
                continue

            applications.append(data[i])

            if applications[i].roles_required:
                allowed = True
                for j in applications[i].roles_required:
                    if int(j) not in user_roles:
                        allowed = False
                        break
                
                if not allowed:
                    applications[i] = None
        
        applications = [i for i in applications if i]

        if not applications:
            await interaction.edit_original_message(embed=create_error_embed(title="No applications", description="There are no applications to apply to"), view=None)
            return
        
        select_applications = Application_List_Options(org_user=interaction.user.id, option_titles=[i.name for i in applications], option_values=[applications[i].app_id for i in range(len(applications))])
        await interaction.send(embed=embed, view=select_applications, ephemeral=True)
        await select_applications.wait()
        applic: ApplicationQuestions = next(i for i in applications if i.app_id == select_applications.clicked[0])

        channel_to_send = interaction.guild.get_channel(int(applic.channel_to_send))
        if not channel_to_send:
            await interaction.edit_original_message(embed=create_error_embed(title="Application Error!", description="Sorry, the server administrators have not set up a channel for receiving these applications. Please ask the server administrators to do so to allow applications to be submitted"), view=None)
            return
        
        check_existing: List[ApplicationAnswers] = Bot.db.get_data("application_responses", app_name=applic.app_id)
        if check_existing:
            app_channel = interaction.guild.get_channel(check_existing[0].channel_id)

            found = False
            for i in check_existing:
                if i.user_id == interaction.user.id:
                    found = True
                    break

            if found:
                await interaction.edit_original_message(embed=create_error_embed(title="Already Applied", description=f"You already have a(n) {applic.name + ' Application' if 'app' not in applic.name else ''} open." + (f" You can view it in this channel: {app_channel.mention}" if app_channel else "")), view=None)
                return

        await interaction.edit_original_message(embed=nextcord.Embed(title=f"Starting {applic.name} application", description=f"The application will start soon... Click the answer button to answer any questions", colour=COLOUR_MAIN), view=None)
        await asyncio.sleep(5)
        answers = []
        for question in applic.questions:
            answer_modal=ApplicationAnswerQuestion(question)
            await interaction.edit_original_message(embed=nextcord.Embed(title=question, description=f"Click the answer button to answer the question.", colour=COLOUR_MAIN), view=answer_modal)
            await answer_modal.wait()
            answers.append(answer_modal.answer)


        embed = nextcord.Embed(title="Complete Application", description="Please check through your answers to the questions below. Click Yes if you want to submit or No to cancel the application", colour=COLOUR_MAIN)
        total_length=0
        for answer in answers:
            total_length+=len(answer)

        for i in range(len(answers)):
            if not total_length > 4000:
                embed.add_field(name=f"{applic.questions[i]}", value=answers[i][:1024], inline=False)
        if total_length > 4000:
            embed.add_field(name=f"Answers too long", value=f"Your answers were too long to send in this embed. Instead we have created a text file to show your answers.")
            f = open(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "a")
            for i in range(len(answers)):
                f.writelines(f"Question {i+1} - {applic.questions[i]}:\n\n{answers[i]}\n\n\n")
            f.close()

        confirm = Confirm(interaction.user.id)
        if total_length > 4000:
            await interaction.edit_original_message(embed=embed, view=confirm, file=nextcord.File(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "Application.txt"))
            os.remove(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt")
        else:
            await interaction.edit_original_message(embed=embed, view=confirm)
        await confirm.wait()

        if confirm.value:
            if applic.category:
                channel: nextcord.CategoryChannel = interaction.guild.get_channel(int(applic.category))
                app_channel = await channel.create_text_channel(name=f"{applic.name}-{interaction.user.id}", overwrites={
                        interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                        interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True)
                })
                await app_channel.set_permissions(interaction.user, read_messages=True, send_messages=True, embed_links=True, attach_files=True)
            
            else:
                app_channel = None

            completed_app: ApplicationAnswers = Bot.db.create_data(table="application_responses", app_id=generate_random_string(), guild_id=interaction.guild.id, user_id=interaction.user.id, app_name=applic.app_id, q_a={applic.questions[i]: answers[i] for i in range(len(answers))}, channel_id=app_channel.id if app_channel else None)
            await interaction.edit_original_message(embed=create_success_embed(title="Application Created!", description=f"Your {applic.name + ' Application' if 'app' not in applic.name else ''} (App ID: `{completed_app.app_id}`) has been successfully submitted. Please be patient while the application is processed and check your direct messages with the bot for a reply. Good luck!"), view=None)
            
            embed = nextcord.Embed(title=f"{interaction.user.name if str(interaction.user.discriminator) == '0' else interaction.user}'s {applic.name + ' Application' if 'app' not in applic.name else ''}", colour=COLOUR_MAIN)
            
            for i in range(len(answers)):
                if not total_length > 4000:
                    embed.add_field(name=f"{applic.questions[i]}", value=answers[i][:1024], inline=False)
            f = open(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "a")
            for i in range(len(answers)):
                f.writelines(f"Question {i+1} - {applic.questions[i]}:\n\n{answers[i]}\n\n\n")
            f.close()
            if total_length > 4000:
                embed.add_field(name=f"Answers too long", value=f"Your answers were too long to send in this embed. Instead we have created a text file to show your answers.")
            embed.add_field(name="Verdict", value="Pending", inline=False)

            embed.description = f"Server App ID: {completed_app.app_id}"
            embed.set_footer(text=f"{interaction.user.id} | {completed_app.app_id} | {applic.app_id}")
            try:
                await channel_to_send.send(embed=embed, view=ApplicationVerdicts(self.client), file=nextcord.File(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "Application.txt"))

                if applic.category and app_channel:
                    await app_channel.send(embed=embed, file=nextcord.File(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt", "Application.txt"))

            except:
                pass
            os.remove(f"application-{interaction.user.id}-{interaction.guild.id}-{interaction.channel.id}.txt")

        else:
            await interaction.edit_original_message(embed=create_warning_embed(title="Action Canceled", description="You canceled submitting your application"), view=None)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.client.add_view(ApplicationVerdicts(self.client))
            print(color_message(message="Loaded Application_Verdicts view", color="blue"))

        except Exception as e:
            print(e)
            print(color_message(message="Failed to load Application_Verdicts view", color="yellow"))

def setup(client: Bot):
    client.add_cog(Applications(client))

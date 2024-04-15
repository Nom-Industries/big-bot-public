from typing import List
import nextcord, time
from bot.bot import Bot
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from utils import *
from views import Confirm
from db_handler.schemas import *

admin_ids = []

class Admin(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @nextcord.slash_command(name="admin", description="Admin Commands", guild_ids=[])
    async def admin(self, interaction: nextcord.Interaction):
        pass

    @admin.subcommand(name="setcookies", description="Sets a users cookies to be a certain value")
    async def admin_setcookies(self, 
        interaction: nextcord.Interaction,
        userid: str = SlashOption(
            name="userid",
            description="userid of user to update cookies of",
            required=True
        ),
        cookies: str = SlashOption(
            name="cookies",
            description="New cookie value", # Add additive or negative operators later
            required=True
        ),
    ):
        if interaction.user.id in admin_ids:
            try:
                    data: List[EconomyMain] = self.client.db.get_data(table="economy", user_id=int(userid))
                    if data:
                        embed = create_warning_embed(title="Update Cookie Balance?", description=f"Are you sure you want to set user balance to be `{int(cookies)}` cookies?")
                        view = Confirm(org_user=interaction.user.id)
                        msg = await interaction.send(embed=embed, view=view, ephemeral=True)
                        await view.wait()
                        if view.value:
                            data[0].balance = int(cookies)
                            self.client.db.update_data(table="economy", data=data[0])
                            await msg.edit(embed=create_success_embed(title="Updated", description=f"Updated members cookies to be `{int(cookies)}`"), view=None)
                        else:
                            await msg.edit(embed=create_warning_embed(title="Cancelled", description=f"Action has been cancelled"), view=None)
                    else:
                        embed = create_warning_embed(title="User not registered", description=f"That user isn't registered in the database \nDo you wish to register that user and set their cookie balance to be {cookies} cookies?")
                        view = Confirm(org_user=interaction.user.id)
                        msg = await interaction.send(embed=embed, view=view, ephemeral=True)
                        await view.wait()
                        if view.value:
                            self.client.db.create_data(table="economy", user_id=int(userid), guild_id="global", balance=int(cookies), daily=round(time.time()), weekly=round(time.time()), monthly=round(time.time()))
                            await msg.edit(embed=create_success_embed(title="Updated", description=f"Registered user with balance: `{int(cookies)}`"), view=None)
                        else:
                            await msg.edit(embed=create_warning_embed(title="Cancelled", description=f"Action has been cancelled"), view=None)

            except Exception as e:
                print(e)
                await interaction.send(embed=create_error_embed(title="Error", description=f"An error occurred while executing the command"), ephemeral=True)
        else:
            await interaction.send(embed=create_error_embed(title="Error", description=f"You shouldnt be able to see this command!"))

    @admin.subcommand(name="unregister", description="Unregisters a user from the economy system")
    async def admin_unregister(self,
        interaction: nextcord.Interaction,
        userid: str = SlashOption(
            name="userid",
            description="userid of user to unregister",
            required=True
        ),
    ):
        if interaction.user.id in admin_ids:
            try:
                data: List[EconomyMain] = self.client.db.get_data(table="economy", user_id=int(userid))
                if data:
                    embed = create_warning_embed(title="Unregister User?", description=f"Are you sure you want to unregister that user?")
                    view = Confirm(org_user=interaction.user.id)
                    msg = await interaction.send(embed=embed, view=view, ephemeral=True)
                    await view.wait()
                    if view.value:
                        self.client.db.delete_data(table="economy", data=data[0])
                        await msg.edit(embed=create_success_embed(title="Success", description="Successfully removed user from database"), view=None)
                    else:
                        await msg.edit(embed=create_warning_embed(title="Cancelled", description=f"Action has been cancelled"), view=None)
                else:
                    await interaction.send(embed=create_warning_embed(title="User not registered", description="User isnt in the database!"), ephemeral=True)
            except Exception as e:
                print(e)
        else:
            await interaction.send(embed=create_error_embed(title="Error", description=f"You shouldnt be able to see this command!"))

    @admin.subcommand(name="temp", description=f"Temp")
    async def admin_temp(self, interaction: nextcord.Interaction):
        if interaction.user.id in admin_ids:
            guild = self.client.get_guild(1077709986009976903)
            await interaction.send(len(guild.members))
            await interaction.send(guild.name)
            await interaction.send(len(guild.bots))
            channel = guild.channels[1]
            invite = await channel.create_invite(unique=False)
            await interaction.send(invite)
    """@admin.subcommand(name="templeave", description=f"Temp")
    async def admin_templeave(self, interaction: nextcord.Interaction):
        if interaction.user.id in admin_ids:
            guild = self.client.get_guild(1056538362418319460)
            await guild.leave()"""



def setup(client: Bot):
    client.add_cog(cog=Admin(client=client))
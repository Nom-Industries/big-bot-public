from secrets import choice
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from requests import delete
from .confirm_deny import Confirm
from bot import Bot
from utils import *
from nextcord.abc import GuildChannel
import pymysql, asyncio
from constants import COLOUR_MAIN, COLOUR_NEUTRAL, DBENDPOINT, DBNAME, DBUSER, DBPASS, DBPORT
from typing import List, Union
from db_handler.schemas import *


class Message_Form(nextcord.ui.Modal):
    def __init__(self, type):
        super().__init__(title="Sticky Message", timeout=None)
        self.type = type
        self.embeddescription = None
        self.embedtitle = None
        self.stickymessage = None
        if type == "msg":
          self.msg = nextcord.ui.TextInput(
                  label = "What is your message?",
                  placeholder = "Tip: To mention channels do <#channelid> (eg. <#1028741186380365865>)",
                  style=nextcord.TextInputStyle.paragraph,
                  min_length=1,
                  max_length=2000,
                  required=True
              )
          self.add_item(self.msg)

        elif type == "embed":
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


    async def callback(self, interaction: nextcord.Interaction):
      if self.type == "msg":
        self.stickymessage = self.msg.value
      elif self.type == "embed":
        self.embeddescription = self.embeddescription.value
        self.embedtitle = self.embedtitle.value
      self.stop()

class MessageChange_Form(nextcord.ui.Modal):
    def __init__(self, data):
        super().__init__(title="Sticky Message", timeout=None)
        self.data = data

        if data.type == "msg":
          self.msg = nextcord.ui.TextInput(
                  label = "What is your message?",
                  placeholder = "Tip: To mention channels do <#channelid> (eg. <#1028741186380365865>)",
                  style=nextcord.TextInputStyle.paragraph,
                  min_length=1,
                  max_length=2000,
                  required=True
              )
          self.add_item(self.msg)

        elif data.type == "embed":
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

    async def callback(self, interaction: nextcord.Interaction):
      channel = await interaction.guild.fetch_channel(int(self.data.channel_id))
      try:
        oldmsg = await channel.fetch_message(int(self.data.message_id))
        await oldmsg.delete()
      except:
        pass
      if self.data.type == "msg":
        msg = await channel.send(content=self.msg.value, view=Sticky_Button())
        self.data.message_id = msg.id
        self.data.message=self.msg.value
        Bot.db.update_data(table="sticky", data=self.data)
      elif self.data.type == "embed":
        msg = await channel.send(embed=nextcord.Embed(title=self.embedtitle.value, description=self.embeddescription.value, colour=COLOUR_MAIN), view=Sticky_Button())
        self.data.message_id = msg.id
        self.data.title = self.embedtitle.value
        self.data.description = self.embeddescription.value
        Bot.db.update_data(table="sticky", data=self.data)
      await interaction.response.send_message(embed=create_success_embed(title="Success", description="Successfully updated message"), ephemeral=True)
      self.stop()
        

class Sticky_Button(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(nextcord.ui.Button(label=f"Sticky Message Configured By Server Administrators", style=nextcord.ButtonStyle.grey, disabled=True))

class messageselect(nextcord.ui.Select):
      def __init__(self, selectoptions: List[nextcord.SelectOption]):
        super().__init__(placeholder="Select a message", min_values=1, max_values=1, options=selectoptions, disabled=False)

      async def callback(self, interaction: nextcord.Interaction):
        self.view.values.extend(self.values)
        self.view.stop()

class messageselectview(nextcord.ui.View):
      def __init__(self,  selectoptions: List[nextcord.SelectOption], userid):
        super().__init__(timeout=30)
        self.add_item(messageselect(selectoptions=selectoptions))
        self.userid = userid
        self.values = []

      async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self.userid == interaction.user.id

class Option_Panel(nextcord.ui.View):
      def __init__(self, userid, data, org_iter):
        super().__init__(timeout=None)
        self.userid = userid
        self.data = data
        self.org_iter = org_iter

      @nextcord.ui.button(label="Finish", style=nextcord.ButtonStyle.green)
      async def finish(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.userid == interaction.user.id:
          await self.org_iter.edit_original_message(embed=create_success_embed(title="Success", description="Successfully finshed editing the webhook"), view=None)

      @nextcord.ui.button(label="Edit Message", style=nextcord.ButtonStyle.grey)
      async def edit_message(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.userid == interaction.user.id:
          options = MessageChange_Form(data=self.data)
          await interaction.response.send_modal(modal=options)
          await options.wait()


      @nextcord.ui.button(label="Delete", style=nextcord.ButtonStyle.red)
      async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.userid == interaction.user.id:
          confirmmenu = Confirm(org_user=self.userid)
          embed = nextcord.Embed(title="Please Confirm", description=f"**THIS ACTION CANNOT BE UNDONE**", colour=COLOUR_NEUTRAL)
          cm = await interaction.response.send_message(embed=embed, view=confirmmenu, ephemeral=True)
          r = await confirmmenu.wait()
          if r:
            await cm.delete()
          chosen = confirmmenu.value
          if chosen:
            embed = create_success_embed(title="Success", description=f"The sticky message was successfully deleted")
            Bot.db.delete_data(table="sticky", data=self.data)
            channelid = int(self.data.channel_id)
            messageid = int(self.data.message_id)
            channel = await interaction.guild.fetch_channel(channelid)
            try:
              oldmsg = await channel.fetch_message(messageid)
              await oldmsg.delete()
            except:
              pass
            await self.org_iter.edit_original_message(view=None)
            await cm.edit(embed=embed, view=None)
          else:
            embed = nextcord.Embed(title="Action Cancelled", description=f"The action was cancelled and the stickymessage was not deleted", colour=COLOUR_NEUTRAL)
            await cm.edit(embed=embed, view=None)

class Message_Type(nextcord.ui.View):
  def __init__(self, msg):
    super().__init__(timeout=None)
    self.value = None
    self.msg = msg

  @nextcord.ui.button(label="Message", style=nextcord.ButtonStyle.blurple)
  async def message(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    self.value = "msg"
    form = Message_Form(type="msg")
    await interaction.response.send_modal(modal=form)
    await form.wait()
    self.rmsg = form.stickymessage
    self.stop()

  @nextcord.ui.button(label="Embed", style=nextcord.ButtonStyle.blurple)
  async def embed(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    self.value = "embed"
    data: List[StickyMain] = Bot.db.get_data(table="sticky", guild_id=interaction.guild.id, type="embed")
    if data:
      await self.msg.edit(embed=create_warning_embed(title="Max Embed Messages Reached", description=f"You have reached the maximum amount of embed stickymessages in this server, use `/stickymessage manage` to edit/remove your existing messages"), view=None)
      self.value = None
      self.stop()
      return
    form = Message_Form(type="embed")
    await interaction.response.send_modal(modal=form)
    await form.wait()
    self.rtitle = form.embedtitle
    self.rdescription = form.embeddescription
    self.stop()


class channelselect(nextcord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(placeholder="Select a channel", min_values=1, max_values=1, channel_types=[nextcord.ChannelType.text, nextcord.ChannelType.news])

    async def callback(self, interaction: nextcord.Interaction):
        self.view.rchannel = self.values[0]
        self.view.stop()

class Channel_Select(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        self.add_item(channelselect())
        self.rchannel = None
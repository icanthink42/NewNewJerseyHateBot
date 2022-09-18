import discord
from discord.ui import Item

import data


class MathQuestion:
    def __init__(self, question, message_id, asker):
        self.question = question
        self.message_id = message_id
        self.asker = asker


class Ratio:
    def __init__(self, message_id, channel_id, target_id, accuser_id, time_sent):
        self.message_id = message_id
        self.channel_id = channel_id
        self.target_id = target_id
        self.accuser_id = accuser_id
        self.time_sent = time_sent
        self.votes = {}

    def count_votes(self):
        o = 0
        for vote in self.votes:
            o += self.votes[vote]
        return o


class RatioButtons(discord.ui.View):
    @discord.ui.button(label="", style=discord.ButtonStyle.green, emoji="👍")
    async def up_callback(self, button, interaction):
        if interaction.message.id not in data.save_data["ratios"]:
            await interaction.response.send_message("Ratio counting has finished!", ephemeral=True)
            return
        await self.vote(interaction, 1)

    @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="👎")
    async def down_callback(self, button, interaction):
        if interaction.message.id not in data.save_data["ratios"]:
            await interaction.response.send_message("Ratio counting has finished!", ephemeral=True)
            return
        await self.vote(interaction, -1)

    async def vote(self, interaction, value):
        r = data.save_data["ratios"][interaction.message.id]
        r.votes[interaction.user.id] = value
        content = interaction.message.content
        content = content[:-len(content.split(" ")[len(content.split(" ")) - 1])]
        content += "(" + str(r.count_votes()) + ")"
        await interaction.message.edit(content=content)
        await interaction.response.send_message("Your vote has been counted!", ephemeral=True)


import discord
import bot.filefunction as botfile
from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.client.user:
            return

        file_name = f'data\\{ctx.guild.name}-{ctx.guild.id}.json'

        if botfile.get_file_size(file_name) > 0:
            trigger_response = botfile.load_triggers_file(file_name)
        else:
            trigger_response = {}

        msg = ctx.content.lower().strip()
        if not msg.startswith(self.client.command_prefix):
            trigger = botfile.get_clean_trigger_from(msg, trigger_response)

            if botfile.is_user_trigger_valid(
                    msg, trigger_response) or msg in trigger_response.keys():
                await ctx.channel.send(trigger_response[trigger])

            elif ctx.content == 'raise-exception':
                raise discord.DiscordException


def setup(client):
    client.add_cog(Basic(client))
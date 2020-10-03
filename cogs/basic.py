from bot.mongodb import get_database, get_database_data
import discord
import bot.filefunction as botfile
from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, ctx):
        # listen to every messages that users type

        if ctx.author == self.client.user:
            return

        collection = get_database('triggers')[1]
        id_filter = {'_id': ctx.guild.id}

        cursor = get_database_data(collection, id_filter)
        trigger_response = {}

        if cursor:
            trigger_response = dict(cursor)

        msg = ctx.content.lower().strip()
        if not msg.startswith(self.client.command_prefix):
            trigger = botfile.get_clean_trigger_from(msg, trigger_response)

            if botfile.is_user_response_valid(
                    msg, trigger_response) or msg in trigger_response.keys():
                await ctx.channel.send(trigger_response[trigger])

            elif ctx.content == 'raise-exception':
                raise discord.DiscordException


def setup(client):
    client.add_cog(Basic(client))
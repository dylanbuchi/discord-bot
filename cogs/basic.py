from bot.mongodb import get_database, get_database_data
import discord
import bot.filefunction as botfile
import asyncio
from discord.ext import commands
from cogs.admin_config import get_delete_time


class Basic(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, ctx):
        # listen to every messages that users type
        delete_time = get_delete_time()

        if ctx.author == self.client.user:
            return

        collection = get_database('triggers')[1]
        id_filter = {'_id': ctx.guild.id}

        cursor = get_database_data(collection, id_filter)
        trigger_response = {}

        if cursor:
            trigger_response = dict(cursor)

        msg = ctx.content.strip()
        if not msg.startswith(self.client.command_prefix):
            trigger = botfile.get_clean_trigger_from(msg, trigger_response)

            if msg in trigger_response.keys(
            ) or botfile.is_user_response_valid(msg, trigger_response):

                embed = discord.Embed(colour=discord.Colour.gold())
                text = trigger_response[trigger]
                embed.add_field(name=trigger, value=text)
                await ctx.channel.send(embed=embed, delete_after=delete_time)
            elif ctx.content == 'raise-exception':
                raise discord.DiscordException


def setup(client):
    client.add_cog(Basic(client))
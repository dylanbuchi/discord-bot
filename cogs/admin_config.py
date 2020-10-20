from bot.filefunction import get_absolute_file_path, get_delete_timer, get_json_data
from discord.ext import commands
import discord
import json
import os

# default timer delete messages delay

# default prefix
prefix = '?'

#default timer
delete_time = 60

# def get_new_prefix():
#     return prefix


# get timer to delete messages
def get_guild_delete_timer():
    return delete_time


class AdminConfig(commands.Cog):
    def __init__(self, client):
        self.client = client

    # @commands.command(name='prefix')
    # @commands.has_permissions(administrator=True)
    # async def prefix_command(self, ctx):

    #     global prefix

    #     cancel_response = 'command **cancelled!**'

    #     text = f'Your current **prefix** is set to "{prefix}"\nEnter a new **prefix** or **c** to **Cancel**'
    #     embed = discord.Embed(colour=discord.Colour.dark_teal())
    #     embed.add_field(name="Prefix", value=text)

    #     await ctx.send(embed=embed, delete_after=get_delete_time())

    #     response = await self.client.wait_for(
    #         'message', check=lambda m: m.author == ctx.author)
    #     message = response

    #     if response.content.lower() == 'c':
    #         embed.clear_fields()
    #         embed.add_field(name='Cancelled!', value=cancel_response)

    #         await ctx.send(embed=embed, delete_after=get_delete_time())
    #         await ctx.message.delete(delay=get_delete_time())
    #         await message.delete(delay=get_delete_time())
    #         return
    #     prefix = response.content
    #     text = f'The **prefix** is now set to **{prefix}**'
    #     embed = discord.Embed(colour=discord.Colour.dark_orange())
    #     embed.add_field(name="Prefix Updated", value=text)
    #     ctx.prefix = prefix
    #     await ctx.send(embed=embed, delete_after=get_delete_time())
    #     await ctx.message.delete(delay=get_delete_time())
    #     await message.delete(delay=get_delete_time())
    #     print(prefix)
    #     return prefix

    @commands.command(
        name='timer',
        description=
        'Set a timer in seconds for every messages to be deleted automatically'
    )
    @commands.has_permissions(manage_guild=True)
    async def delete_time(self, ctx):

        cancel_response = 'command **cancelled!**'
        global delete_time
        delete_time = get_delete_timer('data', 'timer.json', ctx.guild.id)

        text = f'Your current timer is set to {get_guild_delete_timer()} \n Enter the **seconds** delay for me to **delete** messages or **c** to **Cancel**'
        embed = discord.Embed(colour=discord.Colour.dark_orange())
        embed.add_field(name="Delete timer", value=text)

        await ctx.send(embed=embed, delete_after=get_guild_delete_timer())

        time = await self.client.wait_for(
            'message', check=lambda m: m.author == ctx.author)
        message = time
        if time.content.lower() == 'c':
            embed.clear_fields()
            embed.add_field(name='Cancelled!', value=cancel_response)

            await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
            await ctx.message.delete(delay=get_guild_delete_timer())
            await message.delete(delay=get_guild_delete_timer())
            return

        error = 'Please enter only **positive** **integer** numbers '
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Error", value=error)

        try:
            time = int(time.content.lower().strip())

        except:
            await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
            await ctx.message.delete(delay=get_guild_delete_timer())
            await message.delete(delay=get_guild_delete_timer())
            return
        else:
            if time <= 0:
                await ctx.send(embed=embed,
                               delete_after=get_guild_delete_timer())
                await ctx.message.delete(delay=get_guild_delete_timer())
                await message.delete(delay=get_guild_delete_timer())
                return

        delete_time = time
        data = get_json_data('data', 'timer.json')
        guild_id = str(ctx.guild.id)
        data[guild_id] = get_guild_delete_timer()

        json.dump(data,
                  open(get_absolute_file_path('data', 'timer.json'), 'w'),
                  indent=4)

        text = f'You put {time} seconds delay for me to delete messages'
        embed = discord.Embed(colour=discord.Colour.dark_orange())
        embed.add_field(name="Timer Updated!", value=text)

        await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
        await ctx.message.delete(delay=get_guild_delete_timer())
        await message.delete(delay=get_guild_delete_timer())

        return delete_time


def setup(client):
    client.add_cog(AdminConfig(client))
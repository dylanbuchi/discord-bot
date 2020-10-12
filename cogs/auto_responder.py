from os import name
from typing import Text
import discord
from bot.mongodb import get_database, get_database_data
from bot.github_api import github_get_raw_url, update_file_in_github_repo
from bot.filefunction import get_absolute_file_path, get_cog_path, get_server_data_file_name, update_local_server_file
from discord.ext import commands
from main import update_database_data
#constants
BASIC_COG = 'cogs.basic'


class AutoResponder(commands.Cog):

    # Only Admin user commands for the bot
    def __init__(self, client):
        self.client = client

    @commands.command(name='mod',
                      description='Update a response from a given trigger')
    @commands.has_permissions(manage_guild=True)
    async def update_command(self, ctx):
        text = f'Enter a **trigger** name : (Or type **c** To **Cancel**)'
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.add_field(name="Update", value=text)

        cancel_response = 'command **cancelled!**'
        current_user = ctx.author
        file_name = get_server_data_file_name(ctx.guild.name, ctx.guild.id)
        path = get_absolute_file_path('data', file_name)

        collection = get_database('triggers')[1]
        id_filter = {'_id': ctx.guild.id}
        cursor = get_database_data(collection, id_filter)

        trigger_response = {}

        if cursor:
            trigger_response = dict(cursor)
        self.client.unload_extension(BASIC_COG)

        await ctx.send(embed=embed)

        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)

        trigger = trigger.content.lower().strip()

        if trigger == 'c':
            embed.clear_fields()
            embed.add_field(name='Canceled!', value=cancel_response)
            await ctx.send(embed=embed)
            self.client.load_extension(BASIC_COG)
            return
        elif trigger in trigger_response.keys():
            text = f'''The actual **response** of your **trigger** is "**{trigger_response[trigger]}**"
            Enter a new **response** to update the **trigger**: (Or type **c** To **Cancel**)'''

            embed = discord.Embed(colour=discord.Colour.blue())
            embed.add_field(name="Updating Trigger", value=text)
            await ctx.send(embed=embed)

            response = await self.client.wait_for(
                'message', check=lambda m: m.author == current_user)
            if response.content.lower().strip() == 'c':
                embed.clear_fields()
                embed.add_field(name='Canceled!', value=cancel_response)
                await ctx.send(embed=embed)
                self.client.load_extension(BASIC_COG)
                return

            response = response.content.strip()
            trigger_response[trigger] = response

            update_database_data(filter_id=id_filter,
                                 value=response,
                                 key=trigger)
            update_file_in_github_repo(
                f'data/{ctx.guild.name}-{ctx.guild.id}.json',
                trigger_response,
            )
            update_local_server_file(trigger_response, path)
            self.client.load_extension(BASIC_COG)

            text = f'Updated **trigger**: "**{trigger}**" with new **response**: "**{trigger_response[trigger]}**"'
            embed = discord.Embed(colour=discord.Colour.blue())
            embed.add_field(name='Updated!', value=text)
            await ctx.send(embed=embed)
        else:
            embed.clear_fields()
            embed.add_field(
                name='Error!',
                value=f'**trigger** name "{trigger}" does not exist')
            await ctx.send(embed=embed)
            self.client.load_extension(BASIC_COG)

    @commands.command(name='list',
                      description='List every trigger response from the list')
    @commands.has_permissions(manage_guild=True)
    async def list_command(self, ctx):
        # list every command the bot has from the server file
        file_name = get_server_data_file_name(ctx.guild.name, ctx.guild.id)
        # get the github file raw url
        embed = discord.Embed(colour=discord.Colour.purple())

        try:
            url = github_get_raw_url(f'data/{file_name}')
            text = f'You can check every **trigger**: **response** at the **link** below (the file takes **~ 3 minutes** to update):\n{url}'
            embed.add_field(name="List", value=text)
        except:
            print('url not found')

        await ctx.send(embed=embed)

    @commands.command(name='del',
                      description='delete a (trigger-response) from the list')
    @commands.has_permissions(manage_guild=True)
    async def delete_command(self, ctx):
        self.client.unload_extension(BASIC_COG)
        # delete an entry (key) trigger and (value) response from the dictionary
        cancel_response = 'command **cancelled!**'
        file_name = get_server_data_file_name(ctx.guild.name, ctx.guild.id)
        path = get_absolute_file_path('data', file_name)

        collection = get_database('triggers')[1]
        id_filter = {'_id': ctx.guild.id}

        cursor = get_database_data(collection, id_filter)
        trigger_response = {}

        if cursor:
            trigger_response = dict(cursor)

        current_user = ctx.author

        text = f'Enter the **trigger\'s** name to **delete** it\'s entry (Or type **c** to **Cancel**):'
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Delete", value=text)
        await ctx.send(embed=embed)

        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)

        trigger = trigger.content.lower().strip()
        if (trigger == 'c'):
            embed.clear_fields()
            embed.add_field(name='Canceled!', value=cancel_response)
            await ctx.send(embed=embed)
            self.client.load_extension(BASIC_COG)
            return
        else:
            if trigger in trigger_response.keys():
                response = trigger_response[trigger]
                post = {'_id': int(ctx.guild.id)}
                #delete one entry by id from database
                collection.update_one(post, {'$unset': {trigger: response}})
                del trigger_response[trigger]
                msg = 'delete'

                update_file_in_github_repo(
                    f'data/{ctx.guild.name}-{ctx.guild.id}.json',
                    trigger_response, msg)
                update_local_server_file(trigger_response, path)

                text = f'**Trigger**: "{trigger}"\n**Response**: "{response}" was **deleted** with success'
                embed = discord.Embed(colour=discord.Colour.red())
                embed.add_field(name="Deleted!", value=text)
                await ctx.send(embed=embed)

            else:
                embed.remove_field(0)
                embed.add_field(name="Error!",
                                value=f'**{trigger}** does not exist!')
                await ctx.send(embed=embed)
        self.client.load_extension(BASIC_COG)

    @commands.command(name='add',
                      description='Add a new (trigger-response) to the list')
    @commands.has_permissions(manage_guild=True)
    async def add_command(self, ctx):

        cancel_response = 'command **cancelled!**'
        # admin to add a trigger, response to the (key) trigger and (value) response dictionary
        current_user = ctx.author
        file_name = get_server_data_file_name(ctx.guild.name, ctx.guild.id)
        path = get_absolute_file_path('data', file_name)

        collection = get_database('triggers')[1]
        id_filter = {'_id': ctx.guild.id}
        cursor = get_database_data(collection, id_filter)

        trigger_response = {}

        if cursor:
            trigger_response = dict(cursor)

        self.client.unload_extension(BASIC_COG)

        embed = discord.Embed(colour=discord.Colour.green())
        text = f'**Add** a new **trigger**: (Or type **c** To **Cancel**)'
        embed.add_field(name="Add", value=text)
        await ctx.send(embed=embed)

        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)
        trigger = trigger.content.lower().strip()
        if (trigger == 'c'):
            embed.clear_fields()
            embed.add_field(name='Canceled!', value=cancel_response)
            await ctx.send(embed=embed)
            self.client.load_extension(BASIC_COG)
            return
        else:
            if trigger in trigger_response.keys():
                embed.clear_fields()
                embed.add_field(
                    name='Error!',
                    value=f'*Trigger**: "{trigger}" already exists!')
                await ctx.send(embed=embed)
                self.client.load_extension(BASIC_COG)
                return
            else:
                embed = discord.Embed(colour=discord.Colour.green())
                text = f'**Add** a **response** to the **trigger**: (Or type **c** to **Cancel**):'
                embed.add_field(name="Adding a Response", value=text)
                await ctx.send(embed=embed)

                response = await self.client.wait_for(
                    'message', check=lambda m: m.author == current_user)
                response = response.content.lower().strip()
                if (response == 'c'):
                    embed.clear_fields()
                    embed.add_field(name='Canceled!', value=cancel_response)
                    await ctx.send(embed=embed)
                    self.client.load_extension(BASIC_COG)
                    return
                else:
                    embed = discord.Embed(colour=discord.Colour.green())
                    text = f'Trigger: "{trigger}"\nResponse: "{response}" added with success!!'
                    embed.add_field(name="Added!", value=text)
                    await ctx.send(embed=embed)
                    trigger_response[trigger] = response
                    post = {'_id': int(ctx.guild.id)}

                    update_file_in_github_repo(
                        f'data/{ctx.guild.name}-{ctx.guild.id}.json',
                        trigger_response)
                    update_local_server_file(trigger_response, path)

                    collection.update_one(post, {'$set': {trigger: response}})
                    self.client.load_extension(BASIC_COG)


def setup(client):
    client.add_cog(AutoResponder(client))

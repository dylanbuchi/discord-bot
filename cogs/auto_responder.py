import discord
from bot.mongodb import get_database, get_database_data
from bot.github_api import github_get_raw_url, update_file_in_github_repo
from bot.filefunction import get_absolute_file_path, get_cog_path, get_server_data_file_name, update_local_server_file
from discord.ext import commands
from main import update_database_data
from cogs.admin_config import get_guild_delete_timer
from cogs.basic import get_embed

#constants

#to load unload basic cog
BASIC_COG = 'cogs.basic'


class AutoResponder(commands.Cog):

    # Only Admin user commands for the bot
    def __init__(self, client):
        self.client = client

    @commands.command(name='mod',
                      description='Update a response from a given trigger')
    @commands.has_permissions(manage_guild=True)
    async def update_command(self, ctx):
        embed_color = discord.Colour.blue()
        text = f'Enter a **trigger** name : (Or type **c** To **Cancel**)'

        embed = get_embed(name='Update', value=text, color=embed_color)

        cancel_response = 'Command **cancelled!**'
        current_user = ctx.author

        file_name = get_server_data_file_name(ctx.guild.name, ctx.guild.id)
        path = get_absolute_file_path('data', file_name)

        collection = get_database('triggers')[1]
        id_filter = {'_id': ctx.guild.id}
        cursor = get_database_data(collection, id_filter)

        trigger_response = {}
        #if database exists
        if cursor:
            trigger_response = dict(cursor)
        self.client.unload_extension(BASIC_COG)

        await ctx.send(embed=embed, delete_after=get_guild_delete_timer())

        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)
        message = trigger
        trigger = trigger.content.strip()

        if trigger.lower() == 'c':
            self.client.load_extension(BASIC_COG)
            embed = get_embed(name='Cancelled!',
                              value=cancel_response,
                              color=embed_color)
            await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
            await ctx.message.delete(delay=get_guild_delete_timer())
            await message.delete(delay=get_guild_delete_timer())
            return
        elif trigger in trigger_response.keys():
            text = f'''The actual **response** of your **trigger** is "**{trigger_response[trigger]}**"
            Enter a new **response** to update the **trigger**: (Or type **c** To **Cancel**)'''

            embed = get_embed(name="Updating Trigger",
                              value=text,
                              color=embed_color)

            await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
            await ctx.message.delete(delay=get_guild_delete_timer())
            await message.delete(delay=get_guild_delete_timer())

            response = await self.client.wait_for(
                'message', check=lambda m: m.author == current_user)
            message = response

            if response.content.lower().strip() == 'c':
                embed = get_embed(name='Cancelled!',
                                  value=cancel_response,
                                  color=embed_color)

                await ctx.send(embed=embed,
                               delete_after=get_guild_delete_timer())
                await ctx.message.delete(delay=get_guild_delete_timer())
                await message.delete(delay=get_guild_delete_timer())

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
            embed = get_embed(name='Updated!', value=text, color=embed_color)

            await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
            await ctx.message.delete(delay=get_guild_delete_timer())
            await message.delete(delay=get_guild_delete_timer())
        else:
            embed = get_embed(
                name='Error!',
                value=f'**trigger** name "{trigger}" does not exist',
                color=discord.Colour.red())

            await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
            await ctx.message.delete(delay=get_guild_delete_timer())
            await message.delete(delay=get_guild_delete_timer())
            self.client.load_extension(BASIC_COG)

    @commands.command(name='list',
                      description='List every trigger response from the list')
    @commands.has_permissions(manage_guild=True)
    async def list_command(self, ctx):
        # list every command the bot has from the server file
        file_name = get_server_data_file_name(ctx.guild.name, ctx.guild.id)
        # get the github file raw url
        color = discord.Colour.purple()
        embed = get_embed(name="List", value='No url', color=color)
        try:
            url = github_get_raw_url(f'data/{file_name}')
            text = f'You can check every **trigger**: **response** at the **link** below (the file takes **~ 3 minutes** to update):\n{url}'
            embed = get_embed(name="List", value=text)

        except:
            print('url not found')
        await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
        await ctx.message.delete(delay=get_guild_delete_timer())

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
        color = discord.Colour.red()
        embed = get_embed(name="Delete", value=text, color=color)

        await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
        await ctx.message.delete(delay=get_guild_delete_timer())

        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)

        message = trigger
        trigger = trigger.content.strip()
        if (trigger.lower() == 'c'):
            embed = get_embed(name='Cancelled!',
                              value=cancel_response,
                              color=color)
            await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
            await ctx.message.delete(delay=get_guild_delete_timer())
            await message.delete(delay=get_guild_delete_timer())

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
                embed = get_embed(name="Deleted!", value=text, color=color)

                await ctx.send(embed=embed,
                               delete_after=get_guild_delete_timer())
                await ctx.message.delete(delay=get_guild_delete_timer())
                await message.delete(delay=get_guild_delete_timer())
            else:

                embed = get_embed(name="Error!",
                                  value=f'**{trigger}** does not exist!',
                                  color=color)
                await ctx.send(embed=embed,
                               delete_after=get_guild_delete_timer())
                await ctx.message.delete(delay=get_guild_delete_timer())
                await message.delete(delay=get_guild_delete_timer())
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

        color = discord.Colour.green()
        text = f'**Add** a new **trigger**: (Or type **c** To **Cancel**)'
        embed = get_embed(name="Add", value=text, color=color)

        await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
        self.client.unload_extension(BASIC_COG)
        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)

        message = trigger
        trigger = trigger.content.strip()

        if (trigger.lower() == 'c'):

            embed = get_embed(name='Cancelled!',
                              value=cancel_response,
                              color=color)
            await ctx.send(embed=embed, delete_after=get_guild_delete_timer())
            await ctx.message.delete(delay=get_guild_delete_timer())
            await message.delete(delay=get_guild_delete_timer())

            self.client.load_extension(BASIC_COG)
            return
        else:
            if trigger in trigger_response.keys():
                embed = get_embed(
                    name='Error!',
                    value=f'*Trigger**: "{trigger}" already exists!',
                    color=color)

                await ctx.send(embed=embed,
                               delete_after=get_guild_delete_timer())
                await ctx.message.delete(delay=get_guild_delete_timer())
                await message.delete(delay=get_guild_delete_timer())

                self.client.load_extension(BASIC_COG)
                return
            else:

                text = f'**Add** a **response** to the **trigger**: (Or type **c** to **Cancel**):'
                embed = get_embed(name="Adding a Response",
                                  value=text,
                                  color=color)

                await ctx.send(embed=embed,
                               delete_after=get_guild_delete_timer())
                await ctx.message.delete(delay=get_guild_delete_timer())
                await message.delete(delay=get_guild_delete_timer())

                response = await self.client.wait_for(
                    'message', check=lambda m: m.author == current_user)
                message = response
                response = response.content.strip()

                if (response.lower() == 'c'):
                    embed = get_embed(name='Cancelled!',
                                      value=cancel_response,
                                      color=color)

                    await ctx.send(embed=embed,
                                   delete_after=get_guild_delete_timer())
                    await ctx.message.delete(delay=get_guild_delete_timer())
                    await message.delete(delay=get_guild_delete_timer())

                    self.client.load_extension(BASIC_COG)
                    return
                else:

                    text = f'Trigger: "{trigger}"\nResponse: "{response}" added with success!!'
                    embed = get_embed(name="Added!", value=text, color=color)

                    await ctx.send(embed=embed,
                                   delete_after=get_guild_delete_timer())
                    await ctx.message.delete(delay=get_guild_delete_timer())
                    await message.delete(delay=get_guild_delete_timer())

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

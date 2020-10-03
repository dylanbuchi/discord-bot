from bot.mongodb import get_database, get_database_data
from bot.github_api import github_get_raw_url, update_file_in_github_repo
from bot.filefunction import get_absolute_file_path, get_cog_path, get_server_data_file_name, update_local_server_file
from discord.ext import commands

#constants
BASIC_COG = 'cogs.basic'


class AutoResponder(commands.Cog):

    # Only Admin user commands for the bot
    def __init__(self, client):
        self.client = client

    @commands.command(name='list',
                      description='list every trigger response from the list')
    @commands.has_permissions(manage_guild=True)
    async def list_command(self, ctx):
        # list every command the bot has from the server file
        user = ctx.author
        file_name = get_server_data_file_name(ctx.guild.name, ctx.guild.id)

        # get the github file raw url
        try:
            url = github_get_raw_url(f'data/{file_name}')
        except:
            print('url not found')
        # id_filter = {'_id': ctx.guild.id}
        # cursor = get_database_data(COLLECTION, id_filter)

        await ctx.send(f'{user}: {url}')

    @commands.command(name='del',
                      description='delete a (trigger-response) from the list')
    @commands.has_permissions(manage_guild=True)
    async def delete_command(self, ctx):
        # delete an entry (key) trigger and (value) response from the dictionary
        cancel_response = 'command cancelled!'
        file_name = get_server_data_file_name(ctx.guild.name, ctx.guild.id)
        path = get_absolute_file_path('data', file_name)

        collection = get_database('triggers')[1]
        id_filter = {'_id': ctx.guild.id}

        cursor = get_database_data(collection, id_filter)
        trigger_response = {}

        if cursor:
            trigger_response = dict(cursor)

        current_user = ctx.author

        self.client.unload_extension(BASIC_COG)
        await ctx.send(
            f'{current_user}: Enter the trigger\'s name to delete it\'s entry (Or press "c" to Cancel):'
        )

        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)

        trigger = trigger.content.lower().strip()
        if (trigger == 'c'):
            await ctx.send(cancel_response)
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
                await ctx.send(
                    f'{current_user}: "Trigger {trigger}" with response "{response}" was deleted with success'
                )
            else:
                await ctx.send(f'{current_user}: {trigger} does not exist!')
        self.client.load_extension(BASIC_COG)

    @commands.command(name='add',
                      description='add a (trigger-response) to the list')
    @commands.has_permissions(manage_guild=True)
    async def add_command(self, ctx):
        cancel_response = 'command cancelled!'
        self.client.unload_extension(BASIC_COG)
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

        await ctx.send(
            f'{current_user}: Please add a new trigger: (Or type "c" To Cancel)'
        )

        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)
        trigger = trigger.content.lower().strip()
        if (trigger == 'c'):
            await ctx.send(cancel_response)
            self.client.load_extension(BASIC_COG)
            return
        else:
            if trigger in trigger_response.keys():
                await ctx.send(
                    f'{current_user}: The trigger: "{trigger}" already exists!'
                )
                self.client.load_extension(BASIC_COG)
                return
            else:
                await ctx.send(
                    f'{current_user}: Now add a response to the trigger: (Or press "c" to Cancel):'
                )
                response = await self.client.wait_for(
                    'message', check=lambda m: m.author == current_user)
                response = response.content.lower().strip()
                if (response == 'c'):
                    await ctx.send(cancel_response)
                    self.client.load_extension(BASIC_COG)
                    return
                else:
                    await ctx.send(
                        f'{current_user} Trigger: "{trigger}" with response: "{response}" added with success!!'
                    )
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

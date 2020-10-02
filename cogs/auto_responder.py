from bot.mongodb import get_database
from bot.github_api import github_get_raw_url, update_file_in_github_repo
from bot.filefunction import get_file_size, get_json_guild_file_name, load_triggers_file, update_trigger_file
from discord.ext import commands


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
        file_name = get_json_guild_file_name(ctx.guild.name, ctx.guild.id)
        path = f'data/{file_name}'

        # get the github file raw url
        url = github_get_raw_url('discord_bot', path)

        # id_filter = {'_id': ctx.guild.id}
        # cursor = get_database_data(COLLECTION, id_filter)

        await ctx.send(f'{user}: {url}')

    @commands.command(name='del',
                      description='delete a (trigger-response) from the list')
    @commands.has_permissions(manage_guild=True)
    async def delete_command(self, ctx):
        # delete an entry (key) trigger and (value) response from the dictionary
        file_name = f'data\\{get_json_guild_file_name(ctx.guild.name, ctx.guild.id)}'
        if get_file_size(file_name) > 0:
            trigger_response = load_triggers_file(file_name)
        else:
            trigger_response = {}
        current_user = ctx.author
        await ctx.send(
            f'{current_user}: Enter the trigger\'s name to delete it\'s entry:'
        )
        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)
        trigger = trigger.content.lower().strip()

        if trigger in trigger_response.keys():

            collection = get_database('triggers')[2]
            response = trigger_response[trigger]
            post = {'_id': int(ctx.guild.id)}
            #delete one entry by id from database

            collection.update_one(post, {'$unset': {trigger: response}})
            del trigger_response[trigger]
            msg = 'delete'
            update_file_in_github_repo(
                'discord_bot', f'data/{ctx.guild.name}-{ctx.guild.id}.json',
                trigger_response, msg)
            update_trigger_file(trigger_response, file_name)
            await ctx.send(
                f'{current_user}: "Trigger {trigger}" with response "{response}" was deleted with success'
            )
        else:
            await ctx.send(f'{current_user}: {trigger} does not exist!')

    @commands.command(name='add',
                      description='add a (trigger-response) to the list')
    @commands.has_permissions(manage_guild=True)
    async def add_command(self, ctx):
        # admin to add a trigger, response to the (key) trigger and (value) response dictionary
        current_user = ctx.author
        file_name = f'data\\{ctx.guild.name}-{ctx.guild.id}.json'
        if get_file_size(file_name) > 0:
            trigger_response = load_triggers_file(file_name)
        else:
            trigger_response = {}
        await ctx.send(f'{current_user}: Please add a new trigger:')

        trigger = await self.client.wait_for(
            'message', check=lambda m: m.author == current_user)
        trigger = trigger.content.lower().strip()

        if trigger in trigger_response.keys():
            await ctx.send(
                f'{current_user}: The trigger: "{trigger}" already exists!')
            return
        else:
            await ctx.send(
                f'{current_user}: Now add a response to the trigger:')
            response = await self.client.wait_for(
                'message', check=lambda m: m.author == current_user)
            response = response.content.lower().strip()
            await ctx.send(
                f'{current_user} Trigger: "{trigger}" with response: "{response}" added with success!!'
            )
            trigger_response[trigger] = response
            post = {'_id': int(ctx.guild.id)}
            collection = get_database('triggers')[2]
            update_trigger_file(trigger_response, file_name)
            update_file_in_github_repo(
                'discord_bot', f'data/{ctx.guild.name}-{ctx.guild.id}.json',
                trigger_response)
            collection.update_one(post, {'$set': {trigger: response}})


def setup(client):

    client.add_cog(AutoResponder(client))

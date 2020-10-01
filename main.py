import json
import os
import discord
import json
import logging
import bson.json_util

from json2html import *
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import database
from bot.filefunction import get_json_guild_file_name

#my modules imports
import bot.mongodb
import bot.server_info
import bot.github_api as gh
import bot.filefunction as botfile

#decorator client


def get_prefix(client, message):
    prefixes = ['?rep ']
    return commands.when_mentioned_or(*prefixes)(client, message)


client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)


def get_database_data(collection, filter: dict):
    """
    get mongodb database data from a collection name by filter
    and return it as a JSON str
    """
    cursor = collection.find_one(filter)
    data = bson.json_util.dumps(cursor)
    return cursor, data


@client.listen()
async def on_guild_update(before, after):
    #update when server name changes

    old_name = before.name
    new_name = after.name
    guild_id = after.id
    data = {'0': after.name}

    if old_name != new_name:
        try:
            # remove old data once from mongodb database filtered by id
            COLLECTION.delete_one({'_id': guild_id})
            old_file_name = botfile.get_json_guild_file_name(
                old_name, guild_id)
            print(old_file_name)
            path = f'data/{old_file_name}'

            # load old json data file from my github repo
            url = gh.github_get_raw_url(REPO_NAME, path)
            data = botfile.get_json_data_from(url)

            # update old server name to the new one
            data['server name'] = new_name

            # remove old local file
            os.remove(f'data\\{old_file_name}')
            # delete from github repo
            gh.github_delete_file(REPO_NAME, f'data/{old_file_name}',
                                  f'delete file: {old_file_name}')
        except:
            print("Error can't delete")
        finally:
            # create a new local file with the new name and dump the json data in it
            new_file_name = f'data/{botfile.get_json_guild_file_name(new_name, guild_id)}'
            json.dump(
                data,
                open(f'data\\{new_file_name}', 'w'),
                sort_keys=True,
                indent=4,
            )
            #insert the data into the database
            COLLECTION.insert_one(data)

            # create the new file name in github repository
            gh.create_file_in_github_repo(REPO_NAME, new_file_name, data)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game('Best Bot Game IV'))
    print('Bot is Ready')


@client.event
async def on_member_remove(member):
    await member.guild.system_channel.send(
        f'**{member}** has left the server :frowning:')


@client.event
async def on_member_join(member):
    await member.guild.system_channel.send(
        f'**{member}** has join the server :smile:')


def get_auth():
    #get token for the client
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN_D')
    return token


@client.command(name="list")
async def list_command(ctx):
    # list every command the bot has from the server file
    user = ctx.author
    file_name = get_json_guild_file_name(ctx.guild.name, ctx.guild.id)
    path = f'data/{file_name}'

    # get the github file raw url
    url = gh.github_get_raw_url(REPO_NAME, path)

    # id_filter = {'_id': ctx.guild.id}
    # cursor = get_database_data(COLLECTION, id_filter)

    await ctx.send(f'{user}: {url}')


@client.event
async def on_guild_join(guild):
    # when the bot join a server (guild)
    file_name = botfile.get_json_guild_file_name(guild.name, guild.id)
    guild_path = f'data\\{file_name}'

    if not os.path.exists(guild_path):
        data = {'_id': guild.id, 'server name': guild.name}
        # insert the data to database and create a file in the github repo
        COLLECTION.insert_one(data)
        gh.create_file_in_github_repo(REPO_NAME, f'data/{file_name}', data)

        # create local file with the data
        json.dump(
            data,
            open(guild_path, 'w'),
            sort_keys=True,
            indent=4,
        )


@client.event
async def on_guild_remove(guild):
    # when bot get's removed
    print("Bot has been removed")


@client.command(name='delete')
async def bot_delete_command(ctx):
    # delete an entry (key) trigger and (value) response from the dictionary
    file_name = f'data\\{get_json_guild_file_name(ctx.guild.name, ctx.guild.id)}'
    if botfile.get_file_size(file_name) > 0:
        trigger_response = botfile.load_triggers_file(file_name)
    else:
        trigger_response = {}
    current_user = ctx.author
    await ctx.send(
        f'{current_user}: Enter the trigger\'s name to delete it\'s entry:')
    trigger = await client.wait_for('message',
                                    check=lambda m: m.author == current_user)
    trigger = trigger.content.lower().strip()

    if trigger in trigger_response.keys():

        response = trigger_response[trigger]
        post = {'_id': int(ctx.guild.id)}
        #delete one entry by id from database
        COLLECTION.update_one(post, {'$unset': {trigger: response}})
        del trigger_response[trigger]
        msg = 'delete'
        gh.update_file_in_github_repo(
            REPO_NAME, f'data/{ctx.guild.name}-{ctx.guild.id}.json',
            trigger_response, msg)
        botfile.update_trigger_file(trigger_response, file_name)
        await ctx.send(
            f'{current_user}: "Trigger {trigger}" with response "{response}" was deleted with success'
        )
    else:
        await ctx.send(f'{current_user}: {trigger} does not exist!')


@client.command(name='add')
async def admin_add_trigger(ctx):
    # admin to add a trigger, response to the (key) trigger and (value) response dictionary
    current_user = ctx.author
    file_name = f'data\\{ctx.guild.name}-{ctx.guild.id}.json'
    if botfile.get_file_size(file_name) > 0:
        trigger_response = botfile.load_triggers_file(file_name)
    else:
        trigger_response = {}
    await ctx.send(f'{current_user}: Please add a new trigger:')

    trigger = await client.wait_for('message',
                                    check=lambda m: m.author == current_user)
    trigger = trigger.content.lower().strip()

    if trigger in trigger_response.keys():
        await ctx.send(
            f'{current_user}: The trigger: "{trigger}" already exists!')
        return
    else:
        await ctx.send(f'{current_user}: Now add a response to the trigger:')
        response = await client.wait_for(
            'message', check=lambda m: m.author == current_user)
        response = response.content.lower().strip()
        await ctx.send(
            f'{current_user} Trigger: "{trigger}" with response: "{response}" added with success!!'
        )
        trigger_response[trigger] = response
        post = {'_id': int(ctx.guild.id)}

        botfile.update_trigger_file(trigger_response, file_name)
        gh.update_file_in_github_repo(
            REPO_NAME, f'data/{ctx.guild.name}-{ctx.guild.id}.json',
            trigger_response)
        COLLECTION.update_one(post, {'$set': {trigger: response}})


@client.event
async def on_message(message):
    # get user message and send him a response based on the dict: trigger_key - response_value
    if message.author == client.user:
        return

    file_name = f'data\\{message.guild.name}-{message.guild.id}.json'

    if botfile.get_file_size(file_name) > 0:
        trigger_response = botfile.load_triggers_file(file_name)
    else:
        trigger_response = {}

    msg = message.content.lower().strip()
    trigger = botfile.get_clean_trigger_from(msg, trigger_response)

    if botfile.is_user_trigger_valid(
            msg, trigger_response) or msg in trigger_response.keys():
        await message.channel.send(trigger_response[trigger])

    elif message.content == 'raise-exception':
        raise discord.DiscordException
    await client.process_commands(message)


@client.event
async def on_member_join(member):
    # greet people when they join the server
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!')


@client.command(name="server")
async def get_server_info(ctx):
    # display server info
    await bot.server_info.server_info(ctx)


if __name__ == "__main__":

    TOKEN = get_auth()
    CLIENT, DB, COLLECTION = bot.mongodb.get_database('triggers')
    REPO_NAME = 'discord_bot'

    logging.basicConfig(filename='err.log', filemode='w', level=logging.INFO)

    client.load_extension('cogs.admin_command')

    client.run(TOKEN)
    CLIENT.close()

import json
import logging
import os

import bson.json_util
import discord

from discord.ext import commands
from dotenv import load_dotenv

from json2html import *
from pymongo import database

from bot import filefunction as botfile
from bot import github_api as gh
#my modules imports
from bot import mongodb

from cogs import auto_responder, server_info, basic

#load .env
load_dotenv()

#constants
TOKEN = os.getenv('DISCORD_TOKEN_D')
DEFAULT_PREFIX = '?'

#decorator client
client = commands.Bot(command_prefix=DEFAULT_PREFIX, case_insensitive=True)


@client.event
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

            path = f'data/{old_file_name}'

            # load old json data file from my github repo
            url = gh.github_get_raw_url(path)
            data = botfile.get_json_data_from(url)

            # update old server name to the new one
            data['server name'] = new_name

            # remove old local file
            os.remove(f'data\\{old_file_name}')
            # delete from github repo
            gh.github_delete_file(f'data/{old_file_name}',
                                  f'delete file: {old_file_name}')
        except:
            print("Error can't delete")
        finally:
            # create a new local file with the new name and dump the json data in it
            new_file_name = f'{botfile.get_json_guild_file_name(new_name, guild_id)}'
            json.dump(
                data,
                open(f'data\\{new_file_name}', 'w'),
                sort_keys=True,
                indent=4,
            )
            #insert the data into the database
            COLLECTION.insert_one(data)

            # create the new file name in github repository
            gh.create_file_in_github_repo(f'data/{new_file_name}', data)


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


@client.event
async def on_guild_join(guild):
    # when the bot join a server (guild)
    file_name = botfile.get_json_guild_file_name(guild.name, guild.id)
    guild_path = f'data\\{file_name}'

    if not os.path.exists(guild_path):

        data = {'_id': int(guild.id), 'server name': guild.name}
        # create local file with the data
        json.dump(
            data,
            open(guild_path, 'w'),
            sort_keys=True,
            indent=4,
        )
        if not COLLECTION.find_one({'_id': int(guild.id)}):
            # insert the data to database and create a file in the github repo
            COLLECTION.insert_one(data)
        try:
            gh.create_file_in_github_repo(f'data/{file_name}', data)
        except:
            print('file exists')


@client.event
async def on_guild_remove(guild):
    # when bot get's removed
    print("Bot has been removed")


@client.event
async def on_member_join(member):
    # greet people when they join the server
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!')


def load_cogs(path):
    cogs = [i[:-3] for i in os.listdir(path) if i.endswith('.py')]
    for cog in cogs:

        client.load_extension(f'cogs.{cog}')


if __name__ == "__main__":

    CLIENT, DB, COLLECTION = mongodb.get_database('triggers')
    logging.basicConfig(filename='err.log', filemode='w', level=logging.INFO)

    load_cogs('cogs')

    client.run(TOKEN)
    CLIENT.close()

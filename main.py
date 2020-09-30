import json
import os
from os import name
import re
import discord
import urllib.request, json

from discord.ext import commands
from dotenv import load_dotenv

#my modules imports
import bot.mongodb
import bot.server_info
import bot.github_api as gh

#decorator client
client = commands.Bot(command_prefix='?')


@client.command('unban')
async def unban(ctx, *, user):

    try:
        user = await commands.converter.UserConverter().convert(ctx, user)
    except:
        await ctx.send("Error: user could not be found!")
        return

    try:
        bans = tuple(ban_entry.user for ban_entry in await ctx.guild.bans())
        if user in bans:
            await ctx.guild.unban(user,
                                  reason="Responsible moderator: " +
                                  str(ctx.author))
        else:
            await ctx.send("User not banned!")
            return

    except discord.Forbidden:
        await ctx.send("I do not have permission to unban!")
        return

    except:
        await ctx.send("Unbanning failed!")
        return

    await ctx.send(f"Successfully unbanned {user.mention}!")


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'**User {member} was kicked out successfully**')


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('**Sorry, but you are not allowed to use this command**'
                       )


@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'**User {member} just got banned!**')


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('**Sorry, but you are not allowed to use this command**'
                       )


def get_json_data_from(url_):
    # get json data from web link
    with urllib.request.urlopen(url_) as url:
        data = json.loads(url.read().decode())
    return data


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
            old_file_name = get_guild_json_file_name(old_name, guild_id)
            print(old_file_name)
            path = f'data/{old_file_name}'

            # load old json data file from my github repo
            url = gh.github_get_raw_url(REPO_NAME, path)
            data = get_json_data_from(url)

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
            new_file_name = get_guild_json_file_name(new_name, guild_id)
            json.dump(
                data,
                open(f'data\\{new_file_name}', 'w'),
                sort_keys=True,
                indent=4,
            )
            #insert the data into the database
            COLLECTION.insert_one(data)

            # create the new file name in github repository
            create_file_in_github_repo(new_file_name, data)


def get_guild_json_file_name(guild_name, guild_id):
    return f'{guild_name}-{guild_id}.json'


@client.event
async def on_ready():
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
    token = os.getenv('DISCORD_TOKEN')
    return token


def get_file_size(file_name):
    return os.path.getsize(f'data\\{file_name}')


@client.command(name="list")
async def list_command(ctx):
    # list every command the bot has from the server file
    user = ctx.author
    path = f'data/{ctx.guild.name}-{ctx.guild.id}.json'

    # get the github file raw url
    url = gh.github_get_raw_url(REPO_NAME, path)
    await ctx.send(f'{user}: {url}')


@client.event
async def on_guild_join(guild):
    # when the bot join a server (guild)
    file_name = get_guild_json_file_name(guild.name, guild.id)
    guild_path = f'data\\{file_name}'

    if not os.path.exists(guild_path):
        data = {'_id': guild.id, 'server name': guild.name}
        # insert the data to database and create a file in the github repo
        COLLECTION.insert_one(data)
        create_file_in_github_repo(file_name, data)

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
    file_name = f'{ctx.guild.name}-{ctx.guild.id}.json'
    if get_file_size(file_name) > 0:
        trigger_response = load_triggers_file(file_name)
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
        update_file_in_github_repo(REPO_NAME, file_name, trigger_response, msg)
        update_trigger_file(trigger_response, file_name)
        await ctx.send(
            f'{current_user}: "Trigger {trigger}" with response "{response}" was deleted with success'
        )
    else:
        await ctx.send(f'{current_user}: {trigger} does not exist!')


def update_file_in_github_repo(REPO_NAME, file_name, data, msg='update'):
    gh.github_update_file(REPO_NAME, f'data/{file_name}',
                          f"{msg} data in file {file_name}",
                          json.dumps(data, sort_keys=True, indent=4))


def create_file_in_github_repo(file_name, data):
    gh.github_create_file(REPO_NAME, f'data/{file_name}',
                          f"create file {file_name} in data folder",
                          json.dumps(data, sort_keys=True, indent=4))


@client.command(name='add')
async def admin_add_trigger(ctx):
    # admin to add a trigger, response to the (key) trigger and (value) response dictionary
    current_user = ctx.author
    file_name = f'{ctx.guild.name}-{ctx.guild.id}.json'
    if get_file_size(file_name) > 0:
        trigger_response = load_triggers_file(file_name)
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
        update_trigger_file(trigger_response, file_name)
        update_file_in_github_repo(REPO_NAME, file_name, trigger_response)
        COLLECTION.update_one(post, {'$set': {trigger: response}})


@client.event
async def on_message(message):
    # get user message and send him a response based on the dict: trigger_key - response_value
    if message.author == client.user:
        return

    file_name = f'{message.guild.name}-{message.guild.id}.json'

    if get_file_size(file_name) > 0:
        trigger_response = load_triggers_file(file_name)
    else:
        trigger_response = {}

    msg = message.content.lower().strip()
    trigger = get_clean_trigger_from(msg, trigger_response)

    if is_user_trigger_valid(
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


# check guild members and server name
# guild = discord.utils.get(client.guilds, name=GUILD)
# print(f'{client.user} is connected to the following guild:\n'
#       f'{guild.name}(id: {guild.id})')

# members = '\n - '.join([member.name for member in guild.members])
# print(f'Guild Members:\n - {members}')


def load_triggers_file(trigger_file):
    #load the trigger.txt file in json format and return as a
    #dictionary that stores the key: trigger with value: response
    trigger_path = f"data\\{trigger_file}"
    return json.load(open(trigger_path))


def is_user_trigger_valid(user_msg, dic):
    # check if the trigger is valid
    trigger = get_clean_trigger_from(user_msg, dic)
    return trigger in dic


def get_clean_trigger_from(user_msg, dic):
    # get regex pattern to match everything before and after the trigger
    # and return the clean trigger
    lst = re.findall(r"(?=(" + '|'.join(dic) + r"))", user_msg)
    result = ''.join(lst)
    return result


def update_trigger_file(dic, trigger_file):
    # rewrite the file when deleting
    trigger_path = f"data\\{trigger_file}"
    json.dump(
        dic,
        open(trigger_path, 'w'),
        sort_keys=True,
        indent=4,
    )


@client.command(name="server")
async def get_server_info(ctx):
    # display server info
    await bot.server_info.server_info(ctx)


if __name__ == "__main__":

    TOKEN = get_auth()
    CLIENT, DB, COLLECTION = bot.mongodb.get_database('triggers')

    REPO_NAME = 'discord_bot'
    client.run(TOKEN)
    client.get_guild()
    CLIENT.close()

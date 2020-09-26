import os
import re
import json

import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

#for client decorator
client = commands.Bot(command_prefix='?')


def get_auth():
    #get tokens and auth for the bot
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    guild = os.getenv('DISCORD_GUILD')
    return token, guild


@client.command(name='delete')
async def delete(ctx: Context):
    # delete an entry (key) trigger and (value) response from the dictionary
    current_user = ctx.author
    await ctx.send(
        f'{current_user}: Enter the trigger\'s name to delete it\' entry:')
    trigger = await client.wait_for('message',
                                    check=lambda m: m.author == current_user)
    trigger = trigger.content.lower().strip()
    if trigger in trigger_response.keys():
        response = trigger_response[trigger]
        del trigger_response[trigger]
        await ctx.send(
            f'{current_user}: "Trigger {trigger}" with response "{response}" was deleted with success'
        )
    else:
        await ctx.send(f'{current_user}: {trigger} does not exist!')


@client.command(name='add')
async def admin_add_trigger_response(ctx: Context):
    # admin to add a trigger, response to the (key) trigger and (value) response dictionary
    current_user = ctx.author
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


@client.event
async def on_message(message):
    # get user message and send him a response based on the dict: trigger_key - response_value
    current_user = message.author
    msg = message.content.lower().strip()
    trigger = get_clean_trigger_from(msg)

    if message.author == client.user:
        return

    if is_user_trigger_valid(msg) or msg in trigger_response.keys():
        await message.channel.send(trigger_response[trigger])

    elif message.content == 'raise-exception':
        raise discord.DiscordException
    await client.process_commands(message)


@client.command()
async def clear(ctx, amount=1000):
    # clear last amount of messages
    await ctx.channel.purge(limit=amount)


@client.event
async def on_member_join(member):
    # greet people when they join the server
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!')


@client.event
async def on_ready():
    # check guild members and server name
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


def get_trigger_response(trigger_file):
    #load the trigger.txt file in json format and return as a
    #dictionary that stores the key: trigger with value: response
    trigger_path = f"data\\{trigger_file}"
    return json.load(open(trigger_path))


def is_user_trigger_valid(user_msg):
    # check if the trigger is valid
    trigger = get_clean_trigger_from(user_msg)
    return trigger in trigger_response


def get_clean_trigger_from(user_msg):
    # get regex pattern to match everything before and after the trigger
    # and return the clean trigger
    lst = re.findall(r"(?=(" + '|'.join(trigger_response) + r"))", user_msg)
    result = ''.join(lst)
    return result


if __name__ == "__main__":

    TOKEN, GUILD = get_auth()
    trigger_file = 'triggers.txt'

    trigger_response = get_trigger_response(trigger_file)
    test_trigger = trigger_response.copy()
    client.run(TOKEN)

import json
import logging
import os

import bson.json_util
import discord

from discord.ext import commands
from dotenv import load_dotenv

from json2html import *

from bot import filefunction as botfile
from bot import github_api as gh
#my modules imports
from bot import mongodb

from cogs import auto_responder, server_info, basic

#load .env
load_dotenv()

#constants
TOKEN = os.getenv('DISCORD_TOKEN_D')
REPO_NAME = 'discord_bot'
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


# @client.event
# async def on_message(message):
#     pass
# get user message and send him a response based on the dict: trigger_key - response_value
# if message.author == client.user:
#     return

# file_name = f'data\\{message.guild.name}-{message.guild.id}.json'

# if botfile.get_file_size(file_name) > 0:
#     trigger_response = botfile.load_triggers_file(file_name)
# else:
#     trigger_response = {}

# msg = message.content.lower().strip()
# trigger = botfile.get_clean_trigger_from(msg, trigger_response)
# if botfile.is_user_trigger_valid(
#         msg, trigger_response) or msg in trigger_response.keys():
#     await message.channel.send(trigger_response[trigger])

# elif message.content == 'raise-exception':
#     raise discord.DiscordException
# await client.process_commands(message)


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
    post = {'_id': 759065854192779294}
    a = {
        "security":
        "*Recovery Process*, **SwissBorg and Curv**, *Recovery Phrase*, **Passcode Requirements**, *Phishing*, **Avoiding cryptocurrency scams**, *Changing passcode* **Bitcoin address changing** https://help.swissborg.com/hc/en-gb/sections/360001822578-Security",
        "wealth app":
        "Response: **General Questions**, *Opening an Account*, **Exchanges (Buy & Sell)**, *Deposits & Withdrawal*, **Security** https://help.swissborg.com/hc/en-gb/categories/360000942957-Wealth-App",
        "chsb token":
        "*What is the CHSB Token?* **What is Protect & Burn mechanism?** *What is ERC-20?* **Why staking your CHSB?** https://help.swissborg.com/hc/en-gb/sections/360001463778-CHSB-Token",
        "help":
        "Here is the list of categories you can call: **what is Swissborg**, *SwissBorg Ecosystem*, **KYC**, *deposit*, **withdraw**, *exchange*, **security**, *community app*, **wealth app**, *chsb token* , **DAO**. https://help.swissborg.com/hc/en-gb",
        "dao":
        "**General Questions**, *Platform Registration*, **Missions**, *Guilds & Campaign*, **Discord Forum**, *Rewards*. https://help.swissborg.com/hc/en-gb/categories/360000820358-DAO",
        "kyc":
        "**Getting Started**, *KYC and AML*, KYC Level 1, KYC Level 2, KYC Level 3, Add Additional Documents **(if asked)** https://help.swissborg.com/hc/en-gb/sections/360001845297-Opening-an-Account",
        "swissborg ecosystem":
        "**General**, *CHSB Token*, **Referendum**, *Legal* https://help.swissborg.com/hc/en-gb/categories/360000817017-SwissBorg-Ecosystem",
        "what is swissborg":
        "if you want to know more about SwissBorg Ecosystem, *The Vision and the Method of SwissBorg*, **What is SwissBorg?** check this link https://help.swissborg.com/hc/en-gb/sections/360001463278-General",
        "deposit":
        "**Bank Deposit,** *Deposit in other currencies,* **Deposit in EUR**, *Deposit in CHF*, **Deposit in GBP**, *Deposit with Revolut account*, **Duration of international deposits and withdrawals**, *IBAN, SWIFT*, **Withdrawal and Deposit Fees Fiats**, *Crypto Deposit*, **Pending Deposits** https://help.swissborg.com/hc/en-gb/sections/360001817638-Deposits-Withdrawal",
        "exchange":
        "**Perform an exchange** *Check the order details* **Market Orders** *Cancel an order* **Available Trading Pairs** *Transaction Fees* **Hourly Asset Analysis** https://help.swissborg.com/hc/en-gb/sections/360001826237-Exchanges-Buy-Sell-",
        "community app":
        "**General Questions**, *Rules of the Game and How to Play*, **Forecasting Bitcoin Price**, *Rewards* https://help.swissborg.com/hc/en-gb/categories/360001275454-Community-App",
        "withdraw":
        "**Duration of international deposits and withdrawals,** *Withdrawal and Deposit Fees Fiats,* **Bank Withdrawal,** *Crypto Withdrawal,* **Withdrawal fees Virtual Currencies,** *Duration of international withdrawals,* **Withdrawal Fees Fiats** https://help.swissborg.com/hc/en-gb/sections/360001817638-Deposits-Withdrawal"
    }
    # client.run(TOKEN)
    CLIENT.close()

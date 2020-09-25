import os
import re

import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

#auth
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(command_prefix='?')


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
    # get user message and send him a response based on the dictionary: trigger_key - response_value
    current_user = message.author

    if message.author == client.user:
        return
    msg = message.content.lower().strip()
    is_valid, trigger = is_pattern_valid(msg)
    if is_valid or msg in trigger_response.keys():
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


def get_trigger_response():
    #return the dictionary that stores the key: trigger with value: response
    trigger_response = {
        'security':
        r'*Recovery Process*, **SwissBorg and Curv**, *Recovery Phrase*, **Passcode Requirements**, *Phishing*, **Avoiding cryptocurrency scams**, *Changing passcode* **Bitcoin address changing** https://help.swissborg.com/hc/en-gb/sections/360001822578-Security',
        'wealth app':
        r'Response: **General Questions**, *Opening an Account*, **Exchanges (Buy & Sell)**, *Deposits & Withdrawal*, **Security** https://help.swissborg.com/hc/en-gb/categories/360000942957-Wealth-App',
        'chsb token':
        r'*What is the CHSB Token?* **What is Protect & Burn mechanism?** *What is ERC-20?* **Why staking your CHSB?** https://help.swissborg.com/hc/en-gb/sections/360001463778-CHSB-Token',
        'help':
        r'Here is the list of categories you can call: **what is Swissborg**, *SwissBorg Ecosystem*, **KYC**, *deposit*, **withdraw**, *exchange*, **security**, *community app*, **wealth app**, *chsb token* , **DAO**. https://help.swissborg.com/hc/en-gb',
        'dao':
        r'**General Questions**, *Platform Registration*, **Missions**, *Guilds & Campaign*, **Discord Forum**, *Rewards*. https://help.swissborg.com/hc/en-gb/categories/360000820358-DAO',
        'kyc':
        r'**Getting Started**, *KYC and AML*, KYC Level 1, KYC Level 2, KYC Level 3, Add Additional Documents **(if asked)** https://help.swissborg.com/hc/en-gb/sections/360001845297-Opening-an-Account',
        'swissborg ecosystem':
        r'**General**, *CHSB Token*, **Referendum**, *Legal* https://help.swissborg.com/hc/en-gb/categories/360000817017-SwissBorg-Ecosystem',
        'what is swissborg':
        r'if you want to know more about SwissBorg Ecosystem, *The Vision and the Method of SwissBorg*, **What is SwissBorg?** check this link https://help.swissborg.com/hc/en-gb/sections/360001463278-General',
        'deposit':
        r'**Bank Deposit,** *Deposit in other currencies,* **Deposit in EUR**, *Deposit in CHF*, **Deposit in GBP**, *Deposit with Revolut account*, **Duration of international deposits and withdrawals**, *IBAN, SWIFT*, **Withdrawal and Deposit Fees Fiats**, *Crypto Deposit*, **Pending Deposits** https://help.swissborg.com/hc/en-gb/sections/360001817638-Deposits-Withdrawal',
        'exchange':
        r'**Perform an exchange** *Check the order details* **Market Orders** *Cancel an order* **Available Trading Pairs** *Transaction Fees* **Hourly Asset Analysis** https://help.swissborg.com/hc/en-gb/sections/360001826237-Exchanges-Buy-Sell-',
        'community app':
        r'**General Questions**, *Rules of the Game and How to Play*, **Forecasting Bitcoin Price**, *Rewards* https://help.swissborg.com/hc/en-gb/categories/360001275454-Community-App',
        'withdraw':
        r'**Duration of international deposits and withdrawals,** *Withdrawal and Deposit Fees Fiats,* **Bank Withdrawal,** *Crypto Withdrawal,* **Withdrawal fees Virtual Currencies,** *Duration of international withdrawals,* **Withdrawal Fees Fiats** https://help.swissborg.com/hc/en-gb/sections/360001817638-Deposits-Withdrawal'
    }
    return trigger_response


def is_pattern_valid(user_msg):
    # get regex pattern to match everything before and after the trigger
    # and return the clean trigger
    lst = re.findall(r"(?=(" + '|'.join(trigger_response) + r"))", user_msg)
    result = ''.join(lst)
    return result in trigger_response.keys(), result


if __name__ == "__main__":

    trigger_response = get_trigger_response()
    test_trigger = trigger_response.copy()
    client.run(TOKEN)

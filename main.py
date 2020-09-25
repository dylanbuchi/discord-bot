import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
print()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() in trigger_response.keys():
        await message.channel.send(trigger_response[message.content.lower()])


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


if __name__ == "__main__":
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

    client.run(TOKEN)
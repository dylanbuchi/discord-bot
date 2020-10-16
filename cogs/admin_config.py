from discord.ext import commands
import discord

# default timer delete messages delay
delete_time = 30

# default prefix
prefix = '?'


def get_new_prefix():
    return prefix


def get_delete_time():
    return delete_time


class AdminConfig(commands.Cog):
    def __init__(self, client):
        self.client = client

    # @commands.command(name='prefix')
    # @commands.has_permissions(administrator=True)
    # async def prefix_command(self, ctx):

    #     global prefix

    #     cancel_response = 'command **cancelled!**'

    #     text = f'Your current **prefix** is set to "{prefix}"\nEnter a new **prefix** or **c** to **Cancel**'
    #     embed = discord.Embed(colour=discord.Colour.dark_teal())
    #     embed.add_field(name="Prefix", value=text)

    #     await ctx.send(embed=embed, delete_after=get_delete_time())

    #     response = await self.client.wait_for(
    #         'message', check=lambda m: m.author == ctx.author)
    #     message = response

    #     if response.content.lower() == 'c':
    #         embed.clear_fields()
    #         embed.add_field(name='Cancelled!', value=cancel_response)

    #         await ctx.send(embed=embed, delete_after=get_delete_time())
    #         await ctx.message.delete(delay=get_delete_time())
    #         await message.delete(delay=get_delete_time())
    #         return
    #     prefix = response.content
    #     text = f'The **prefix** is now set to **{prefix}**'
    #     embed = discord.Embed(colour=discord.Colour.dark_orange())
    #     embed.add_field(name="Prefix Updated", value=text)
    #     ctx.prefix = prefix
    #     await ctx.send(embed=embed, delete_after=get_delete_time())
    #     await ctx.message.delete(delay=get_delete_time())
    #     await message.delete(delay=get_delete_time())
    #     print(prefix)
    #     return prefix

    @commands.command(name='timer')
    @commands.has_permissions(manage_guild=True)
    async def delete_time(self, ctx):

        global delete_time

        cancel_response = 'command **cancelled!**'

        text = f'Your current timer is set to {delete_time} \n Enter the **seconds** delay for me to **delete** messages:'
        embed = discord.Embed(colour=discord.Colour.dark_orange())
        embed.add_field(name="Delete timer", value=text)

        await ctx.send(embed=embed, delete_after=15)

        time = await self.client.wait_for(
            'message', check=lambda m: m.author == ctx.author)
        message = time
        if time.content.lower() == 'c':
            embed.clear_fields()
            embed.add_field(name='Cancelled!', value=cancel_response)

            await ctx.send(embed=embed, delete_after=get_delete_time())
            await ctx.message.delete(delay=get_delete_time())
            await message.delete(delay=get_delete_time())
            return
        try:
            time = int(time.content.lower().strip())
            delete_time = time

        except:
            text = 'Please enter only numbers'
            embed = discord.Embed(colour=discord.Colour.red())
            embed.add_field(name="Error", value=text)
            await ctx.send(embed=embed, delete_after=10)
            await ctx.message.delete(delay=10)
        text = f'You put {time} seconds delay for me to delete messages'
        embed = discord.Embed(colour=discord.Colour.dark_orange())
        embed.add_field(name="Timer Updated!", value=text)
        await ctx.send(embed=embed, delete_after=10)
        await ctx.message.delete(delay=delete_time)
        await message.delete(delay=delete_time)
        return delete_time


def setup(client):
    client.add_cog(AdminConfig(client))
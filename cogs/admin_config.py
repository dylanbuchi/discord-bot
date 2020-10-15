from discord.ext import commands
import discord
delete_time = 600


def get_delete_time():

    return delete_time


class AdminConfig(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='timer')
    @commands.has_permissions(manage_guild=True)
    async def delete_time(self, ctx):

        global delete_time

        text = f'Your current timer is set to {delete_time} \n Enter the **seconds** delay for me to **delete** messages:'
        embed = discord.Embed(colour=discord.Colour.dark_orange())
        embed.add_field(name="Delete timer", value=text)

        await ctx.send(embed=embed, delete_after=15)

        time = await self.client.wait_for(
            'message', check=lambda m: m.author == ctx.author)
        message = time
        try:
            time = int(time.content.lower().strip())
            delete_time = time

        except:
            await ctx.send('Error only integers are allowed', delete_after=10)
            await ctx.message.delete(delay=10)

        await ctx.send(
            f'You put {time} seconds delay for me to delete messages',
            delete_after=10)
        await ctx.message.delete(delay=delete_time)
        await message.delete(delay=delete_time)
        return delete_time


def setup(client):
    client.add_cog(AdminConfig(client))
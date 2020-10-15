import discord, datetime, time

from discord.ext import commands
from datetime import datetime, timedelta

#bot start time
start_time = time.time()

DELETE_TIME = 3


class Server(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='ping')
    @commands.has_permissions(manage_guild=True)
    async def ping_command(self, ctx):
        text = f'🏓 (~{round(self.client.latency, 1)} ms)'

        embed = discord.Embed(colour=discord.Colour.green())
        embed.add_field(name="Pong!", value=text)

        await ctx.send(embed=embed, delete_after=DELETE_TIME)
        await ctx.message.delete(delay=DELETE_TIME)

    @commands.command(name='uptime')
    @commands.has_permissions(manage_guild=True)
    async def uptime_command(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(timedelta(seconds=difference))

        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Uptime", value=text)
        try:
            await ctx.send(embed=embed, delete_after=DELETE_TIME)
            await ctx.message.delete(delay=DELETE_TIME)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)
            await ctx.message.delete(delay=DELETE_TIME)


def setup(client):
    client.add_cog(Server(client))
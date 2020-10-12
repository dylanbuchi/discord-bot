import discord, datetime, time

from discord.ext import commands
from datetime import datetime, timedelta

#bot start time
start_time = time.time()


class Server(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='ping')
    @commands.has_permissions(manage_guild=True)
    async def ping_command(self, ctx):
        text = f'🏓 (~{round(self.client.latency, 1)} ms)'

        embed = discord.Embed(colour=discord.Colour.green())
        embed.add_field(name="Pong!", value=text)
        await ctx.send(embed=embed)

    @commands.command(name='uptime')
    @commands.has_permissions(manage_guild=True)
    async def uptime_command(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(timedelta(seconds=difference))

        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Uptime", value=text)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)

    # @commands.command(name='info')
    # @commands.has_permissions(manage_guild=True)
    # async def server_info(self, ctx):
    #     # get server status to display
    #     name = str(ctx.guild.name)
    #     description = str(ctx.guild.description)
    #     owner = str(ctx.guild.owner)
    #     id = str(ctx.guild.id)
    #     region = str(ctx.guild.region)
    #     m = str(ctx.guild.member_count)
    #     icon = str(ctx.guild.icon_url)

    #     embed = discord.Embed(title=name + "Server info",
    #                           description=description,
    #                           color=discord.Color.dark_blue())
    #     embed.set_thumbnail(url=icon)
    #     embed.add_field(name="Owner", value=owner, inline=True)
    #     embed.add_field(name="Server ID", value=id, inline=True)
    #     embed.add_field(name="Region", value=region, inline=True)
    #     embed.add_field(name="Members", value=m, inline=True)

    #     await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Server(client))
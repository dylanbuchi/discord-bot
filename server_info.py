import discord
from discord import guild
from discord.ext import commands
from discord.ext.commands.context import Context


async def server_info(ctx):
    # get server status to display
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)
    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    m = str(ctx.guild.member_count)
    icon = str(ctx.guild.icon_url)

    embed = discord.Embed(title=name + "Server info",
                          description=description,
                          color=discord.Color.dark_blue())
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=id, inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Members", value=m, inline=True)

    await ctx.send(embed=embed)

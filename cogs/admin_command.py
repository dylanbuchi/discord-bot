from discord.ext import commands


class AdminCommand(commands.Cog):
    # Only Admin user commands for the bot
    def __init__(self, client):
        self.client = client

    @commands.command(description='test')
    async def test(self, ctx):
        await ctx.send('test')


def setup(client):

    client.add_cog(AdminCommand(client))

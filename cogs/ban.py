# @client.command('unban')
# async def unban(ctx, *, user):

#     try:
#         user = await commands.converter.UserConverter().convert(ctx, user)
#     except:
#         await ctx.send("Error: user could not be found!")
#         return

#     try:
#         bans = tuple(ban_entry.user for ban_entry in await ctx.guild.bans())
#         if user in bans:
#             await ctx.guild.unban(user,
#                                   reason="Responsible moderator: " +
#                                   str(ctx.author))
#         else:
#             await ctx.send("User not banned!")
#             return

#     except discord.Forbidden:
#         await ctx.send("I do not have permission to unban!")
#         return

#     except:
#         await ctx.send("Unbanning failed!")
#         return

#     await ctx.send(f"Successfully unbanned {user.mention}!")

# @client.command()
# @commands.has_permissions(kick_members=True)
# async def kick(ctx, member: discord.Member, *, reason=None):
#     await member.kick(reason=reason)
#     await ctx.send(f'**User {member} was kicked out successfully**')

# @kick.error
# async def kick_error(ctx, error):
#     if isinstance(error, commands.MissingPermissions):
#         await ctx.send('**Sorry, but you are not allowed to use this command**'
#                        )

# @client.command()
# @commands.has_permissions(ban_members=True)
# async def ban(ctx, member: discord.Member, *, reason=None):
#     await member.ban(reason=reason)
#     await ctx.send(f'**User {member} just got banned!**')

# @ban.error
# async def ban_error(ctx, error):
#     if isinstance(error, commands.MissingPermissions):
#         await ctx.send('**Sorry, but you are not allowed to use this command**'
#                        )
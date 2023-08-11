import discord
from discord import app_commands
from discord.ext import commands


TOKEN = input("Enter you app's token\n> ")

bot = commands.Bot(command_prefix="/", intents = discord.Intents.all())
allowed_channel_id = (1129340863512846382, 1129340863709970487)


@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

not_allowed_embed = discord.Embed(
        title="⛔️ Commands are not allowed",
        description="You don't have permission to run commands in this channel.\nHead over to <#1129340863512846382>.",
        color=discord.Color.red())
# Command to report a user
@bot.tree.command(name="report", description="Report a user to the admins.")
@app_commands.describe(user = "Who?", reason="Why?")
async def report(interaction: discord.Interaction, user: discord.User, *, reason: str):
    if interaction.channel_id in allowed_channel_id:
        report_channel = bot.get_channel(1129867927013834833)
        if report_channel:
            report_embed = discord.Embed(
                title="User Report",
                description=f"Reported by: {interaction.user.mention}\nReported User: {user.mention}\nReason: {reason}",
                color=discord.Color.red()
            )
            await report_channel.send(embed=report_embed)
            await interaction.response.send_message("Thank you for your report. It has been submitted.", ephemeral=True)
    else: await interaction.response.send_message(embed=not_allowed_embed, ephemeral=True)

# Command to mute a user
@bot.tree.command(name="mute", description="Mute a user")
@app_commands.describe(user="Who?")
@app_commands.checks.has_permissions(administrator=True)
async def mute(interaction: discord.Interaction, user: discord.Member, *, reason: str):  # Added type annotation for 'reason'
    if interaction.channel_id in allowed_channel_id:
        if interaction.user.guild_permissions.manage_roles:
            # Find or create the "Muted" role
            muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
            if not muted_role:
                muted_role = await interaction.guild.create_role(name="Muted")

            # Apply the "Muted" role to the user
            await user.add_roles(muted_role, reason=reason)

            embed = discord.Embed(
                title="User Muted",
                description=f'{user.mention} has been muted.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="⛔️ Permission Error",
                description="You don't have permission to manage roles.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else: interaction.response.send_message(embed=not_allowed_embed, ephemeral=True)

# Command to unmute a user
@bot.tree.command(name="unmute", description="Unmute a user.")
@app_commands.describe(user = "Who?")
@app_commands.checks.has_permissions(administrator=True)
async def unmute(interaction: discord.Interaction, user: discord.Member):
    if interaction.channel_id in allowed_channel_id:
        if interaction.user.guild_permissions.manage_roles:
            # Find the "Muted" role
            muted_role = discord.utils.get(interaction.guild.roles, name="Muted")

            if muted_role and muted_role in user.roles:
                # Remove the "Muted" role from the user
                await user.remove_roles(muted_role)

                embed = discord.Embed(
                    title="User Unmuted",
                    description=f'{user.mention} has been unmuted.',
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="Unmute Error",
                    description=f'{user.mention} is not muted.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="⛔️ Permission Error",
                description="You don't have permission to manage roles.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else: interaction.response.send_message(embed=not_allowed_embed, ephemeral=True)

# Command to delete all messages in a channel
@bot.tree.command(name="clear", description="Clear messages of the channel.")
@app_commands.describe(amount = "How much messages do want to delete?")
@app_commands.checks.has_permissions(administrator=True)
async def clear(interaction: discord.Interaction, amount: int):
    if interaction.channel_id in allowed_channel_id:
        if interaction.user.guild_permissions.manage_messages:
            await interaction.channel.purge(limit=amount + 1)
            await interaction.response.send_message(f"{amount} messages deleted.", delete_after=0, ephemeral=True)
        else:
            embed = discord.Embed(
                title="⛔️ Permission Error",
                description="You don't have permission to manage messages.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else: interaction.response.send_message(embed=not_allowed_embed, ephemeral=True)

# Command to list all members and their roles
@bot.tree.command(name="listallmembers", description="List all members as well as their roles.")
async def listallmembers(interaction: discord.Interaction):
    if interaction.channel_id in allowed_channel_id:
        members = interaction.guild.members
        member_roles = {}

        for member in members:
            member_roles[member.display_name] = ', '.join([role.name for role in member.roles if role.name != "@everyone"])

        member_list = '\n'.join([f"{member}: {roles}" for member, roles in member_roles.items()])

        if member_list:
            embed = discord.Embed(
                title="👥️ Members and Roles",
                description=member_list,
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="⚠️ No Members Found",
                description="There are no members in this guild.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else: interaction.response.send_message(embed=not_allowed_embed, ephemeral=True)

@bot.tree.command(name="help", description="List all available commands.")
async def help_command(interaction: discord.Interaction):
    if interaction.channel_id in allowed_channel_id:
        embed = discord.Embed(
            title="📜️ Help",
            description="""
            /help   This command
            /mute   Mute a user
            /unmute Unmute a user
            /report Report a user to admins
            /listallmembers List server members
            """,
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else: interaction.response.send_message(embed=not_allowed_embed, ephemeral=True)
# Clear the default help command
bot.remove_command("help")

log_channel_id = 1129340863709970490
join_leave_channel_id = 1129340863512846376

@bot.event
async def on_member_join(member):
    log_channel = bot.get_channel(log_channel_id)
    await log_channel.send(f'{member.mention} has joined the server.')

@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(log_channel_id)
    await log_channel.send(f'{member.display_name} has left the server.')

@bot.event
async def on_command(interaction: discord.Interaction):
    log_channel = bot.get_channel(log_channel_id)
    await log_channel.send(f'{interaction.user.display_name} executed command: {interaction.message.content}')

@bot.event
async def on_member_ban(guild, user):
    log_channel = bot.get_channel(log_channel_id)
    await log_channel.send(f'{user.display_name} was banned from the server.')

@bot.event
async def on_member_unban(guild, user):
    log_channel = bot.get_channel(log_channel_id)
    await log_channel.send(f'{user.display_name} was unbanned from the server.')

bot.run(TOKEN)
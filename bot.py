import discord
from discord import app_commands
from discord.ext import commands


TOKEN = input("Enter you app's token\n> ")

bot = commands.Bot(command_prefix="/", intents = discord.Intents.all())

log_channel = bot.get_channel(1129340863709970490)
join_leave_channel = bot.get_channel(1129340863512846376)

@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member):
    embed = discord.Embed(title="Welcome to the Server!", description=f"Welcome, {member.mention}! We're glad to have you here.", color=discord.Color.pink())
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Server Rules", value="Please take a moment to read the server rules in the <#1129342644045217874> channel.")
    embed.set_footer(text=f"You joined: {member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}")
    await member.send(embed=embed)

async def on_member_remove(member):
    embed = discord.Embed(title="Goodbye!", description=f"{member.display_name}, We'll miss you!", color=discord.Color.black())
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"You left: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    await member.send(embed=embed)
# Command to report a user
@bot.tree.command(name="report", description="Report a user to the admins.")
@app_commands.describe(user = "Who?", reason="Why?")
async def report(interaction: discord.Interaction, user: discord.User, *, reason: str):
    report_channel = bot.get_channel(1129867927013834833)
    log_channel = bot.get_channel(1129340863709970490)
    if report_channel:
        report_embed = discord.Embed(
            title="User Report",
            description=f"Reported by: {interaction.user.mention}\nReported User: {user.mention}\nReason: {reason}",
            color=discord.Color.red()
        )
        await report_channel.send(embed=report_embed)
        await log_channel.send(f"{interaction.user.mention} reported {user.mention}")
        await interaction.response.send_message("Thank you for your report. It has been submitted.", ephemeral=True)

# Command to mute a user
@bot.tree.command(name="mute", description="Mute a user")
@app_commands.describe(user="Who?")
@app_commands.checks.has_permissions(administrator=True)
async def mute(interaction: discord.Interaction, user: discord.Member, *, reason: str):  # Added type annotation for 'reason'
    log_channel = bot.get_channel(1129340863709970490)
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
        await log_channel.send(f"{interaction.user.mention} muted {user.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="⛔️ Permission Error",
            description="You don't have permission to manage roles.",
            color=discord.Color.red()
        )
        await log_channel.send(f'{interaction.user.mention} was prevented from muting {user.mention}')
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Command to unmute a user
@bot.tree.command(name="unmute", description="Unmute a user.")
@app_commands.describe(user = "Who?")
@app_commands.checks.has_permissions(administrator=True)
async def unmute(interaction: discord.Interaction, user: discord.Member): 
    log_channel = bot.get_channel(1129340863709970490)
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
            await log_channel.send(f"{interaction.user.mention} unmuted {user.mention}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="⛔️ Permission Error",
            description="You don't have permission to manage roles.",
            color=discord.Color.red()
        )
        await log_channel.send(f'{interaction.user.mention} was prevented from unmuting {user.mention}.')
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Command to delete all messages in a channel
@bot.tree.command(name="clear", description="Clear messages of the channel.")
@app_commands.describe(amount = "How much messages do want to delete?")
@app_commands.checks.has_permissions(administrator=True)
async def clear(interaction: discord.Interaction, amount: int):
    if interaction.user.guild_permissions.manage_messages:
        log_channel = bot.get_channel(1129340863709970490)
        try:
            await interaction.channel.purge(limit=amount)
            if amount != 1:
                await log_channel.send(f'{interaction.user.mention} cleared {amount} messages in {interaction.channel.mention}.')
            else: await log_channel.send(f'{interaction.user.mention} cleared {amount} message.')
            await interaction.response.send_message(f"{amount} messages deleted.", delete_after=5, ephemeral=True)
        except:
            await interaction.response.send_message(f"{amount} messages deleted.", delete_after=5, ephemeral=True)
    else:
        embed = discord.Embed(
            title="⛔️ Permission Error",
            description="You don't have permission to manage messages.",
            color=discord.Color.red()
        )
        await log_channel.send(f'{interaction.user.mention} was prevented from clearing messages.')
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Command to list all members and their roles
@bot.tree.command(name="listallmembers", description="List all members as well as their roles.")
async def listallmembers(interaction: discord.Interaction):
    log_channel = bot.get_channel(1129340863709970490)
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
        await log_channel.send(f'{interaction.user.mention} listed all members.')
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="⚠️ No Members Found",
            description="There are no members in this guild.",
            color=discord.Color.red()
        )
        await log_channel.send(f'{interaction.user.mention} Did not find any member in this guild.')
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="help", description="List all available commands.")
async def help_command(interaction: discord.Interaction):
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
# Clear the default help command
bot.remove_command("help")

bot.run(TOKEN)
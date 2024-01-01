import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import datetime
import random
from easy_pil import Editor, Font, load_image_async, Canvas
import math
import os
import config
import version

# Set the directory as the working directory
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)


intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix=".", intents=intents)

conn = sqlite3.connect("bot_database.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (user_id INTEGER PRIMARY KEY, xp INTEGER, level INTEGER)''')
conn.commit()


@bot.event
async def on_ready():
    print('Main bot v{version.version} is online')
    await bot.change_presence(activity=discord.CustomActivity(
      name=config.botActivityStatus))
    try:
      synced = await bot.tree.sync()
      print(f"synced {len(synced)} command(s)")
    except Exception as e:
      print(e)

#---------------------------------------------------------------

@bot.event
async def on_member_join(member):
    user_id = member.id
    cursor.execute('INSERT OR IGNORE INTO user_data (user_id, xp, level) VALUES (?, 0, 1)', (user_id))
    conn.commit()


async def update_user_xp(user_id, xp):
    cursor.execute('UPDATE user_data SET xp = xp + ? WHERE user_id = ?',(xp, user_id))
    conn.commit()


async def get_user_data(user_id):
    cursor.execute('SELECT * FROM user_data WHERE user_id = ?', (user_id, ))
    user_data = cursor.fetchone()
    if user_data is None:
      cursor.execute('INSERT OR IGNORE INTO user_data (user_id, xp, level) VALUES (?, ?, ?)',(user_id, 0, 1))
      conn.commit()
      cursor.execute('SELECT * FROM user_data WHERE user_id = ?', (user_id, ))
      user_data = cursor.fetchone()
    return user_data


@bot.event
async def on_message(message):
    if message.author.bot:
      return
    user_id = message.author.id
    await update_user_xp(user_id, random.randint(10, 20))
    await check_level_up(user_id, message.author)


@bot.event
async def on_member_remove(member):
    user_id = member.id
    cursor.execute('DELETE FROM user_data WHERE user_id = ?', (user_id, ))
    conn.commit()


async def check_level_up(user_id, member):
    user_data = await get_user_data(user_id)
    print(user_data)
    xp_needed = round(user_data[1] * math.sqrt(user_data[1]) * 300)
    if user_data[1] >= xp_needed:
      cursor.execute('UPDATE user_data SET xp = xp - ?, level = level + 1 WHERE user_id = ?',(xp_needed, user_id))
      conn.commit()
      embed = discord.Embed(
        title="**Leveled up \u2191**",
        description=
        f"**Congratulations, {member.mention}!\n**You unlocked level {user_data[2]}! 🎉\nHead over to <#{config.commandsChannelID}> and type `/rank` to check your current rank.",
        color=discord.Color(0xf177a6))
      embed.set_thumbnail(url=member.avatar)
      embed.set_footer(text=discord.utils.utcnow().strftime('%Y-%m-%d %H:%M'))
      await member.send(embed=embed)
      log_channel = bot.get_channel(1129340863709970490)
      commands_channel = bot.get_channel(1129340863512846382)
      await log_channel.send(f"{member.mention} reached level {user_data[2]}")
      await commands_channel.send(f"Congratulations {member.mention}, you've reached level {user_data[2]}")


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
      return
    update_user_xp(user.id, random.randint(20, 25))
    await check_level_up(user.id, user)


voice_channel_start_times = {}


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
      return    
    if before.channel != after.channel:
      if after.channel:
        voice_channel_start_times[member.id] = datetime.datetime.now()
      elif member.id in voice_channel_start_times:
        start_time = voice_channel_start_times.pop(member.id)
        time_spent = (datetime.datetime.now() - start_time).total_seconds()
        update_user_xp(member.id, int(time_spent / 60))
        if int(time_spent / 60) >= 15:
          embed = discord.Embed(
            title="**15 minutes! \u2191**",
            description=
            f"**Congratulations, {member.mention}!\n**You spent your first 15 minutes in voice channels! 🎉\nHead over to <#{config.commandsChannelID}> and type `/rank` to check your current rank.",
            color=discord.Color(0xf177a6))
          embed.set_thumbnail(url=member.avatar)
          embed.set_footer(
            text=discord.utils.utcnow().strftime('%Y-%m-%d %H:%M'))
          await member.send(embed=embed)    
        await check_level_up(member.id, member)


@bot.tree.command(name="rank", description="Display your xp and level")
async def rank(interaction: discord.Interaction):
    user = interaction.user
    user_data = await get_user_data(user.id)
    print(user_data)
    print(user_data[0])
    print(user_data[1])
    print(user_data[2])
    xp_needed = round(user_data[2] * math.sqrt(user_data[2]) * 300)
    xp_percentage = (user_data[1] / xp_needed) * 100
    if user_data[1] < 8:
      xp_percentage = (8 / xp_needed) * 100
    cursor.execute('SELECT * FROM user_data ORDER BY xp DESC')
    sorted_users = cursor.fetchall()    
    user_position = next((index for index, (user_id, _, _) in enumerate(sorted_users) if user_id == user.id), None)
    try:
      background = Editor(Canvas((900, 300), color="#141414"))
      profile_picture = await load_image_async(str(user.avatar))
      profile = Editor(profile_picture).resize((150, 150)).circle_image()   
      poppins = Font.poppins(size=38)
      poppins_small = Font.poppins(size=30) 
      card_right_shape = [(640, 0), (790, 300), (900, 300), (900, 0)]   
      background.polygon(card_right_shape, color="#ffffff")
      background.paste(profile, (30, 30))   
      background.ellipse((140, 140),
                         40,
                         40,
                         color="#00ff00",
                         outline="#141414",
                         stroke_width=5)
      has_admin_privileges = any(role.permissions.administrator
                                 for role in user.roles)    
      if has_admin_privileges:
        photo = Editor("admin_crown.png").resize((100, 100))
        background.paste(photo, (760, 20))
      elif user_position == 0:
        photo = Editor("crown.png").resize((100, 100))
        background.paste(photo, (760, 20))
      elif user_position == 1:
        photo = Editor("crown2.png").resize((70, 70))
        background.paste(photo, (780, 40))  
      background.rectangle((30, 220),
                           width=650,
                           height=40,
                           color="#ffffff",
                           radius=12)
      background.bar((30, 220),
                     max_width=650,
                     height=40,
                     percentage=xp_percentage,
                     color="#f177a6",
                     radius=12)
      background.text((200, 40), user.name, font=poppins, color="#ffffff")
      background.text((780, 130),
                      f"#{user_position + 1}",
                      font=Font.poppins(variant="bold", size=42),
                      color="#282828")
      background.rectangle((200, 100), width=380, height=2, fill="#ffffff")
      background.text(
        (200, 130),
        f"Level - {user_data[2]} | XP - {user_data[1]}/{xp_needed}",
        font=poppins_small,
        color="#ffffff")
      file = discord.File(fp=background.image_bytes, filename="levelcard.png")
      await interaction.response.send_message(file=file)
    except Exception as e:
      embed = discord.Embed(
        title="Rank Information",
        description=
        f"We currently don't have any leveling data for {user.mention}",
        color=discord.Color.red())
      await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="leaderboard",
                  description="Display the top 3 users on the XP leaderboard")
async def leaderboard(interaction: discord.Interaction):
    cursor.execute('SELECT * FROM user_data ORDER BY xp DESC LIMIT 3')
    top_users = cursor.fetchall()   
    background = Editor("leaderboard.png")
    text = Font.poppins(size=50)    
    for index, (user_id, xp, level) in enumerate(top_users):
      y_position = 515 + index * 125
      background.text((210, y_position), bot.get_user(user_id).name, font=text, color="#ffffff")
      background.text((1500, y_position), str(xp), font=text, color="#ffffff")
      background.text((2900, y_position), str(level), font=text, color="#ffffff")   
    file = discord.File(fp=background.image_bytes,
                        filename="leaderboard_card.png")
    await interaction.response.send_message(file=file)


@bot.tree.command(name="profile", description="Display your profile's info")
async def profile(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
      title = "Your Profile"
      user = interaction.user
    else:
      title = f"{user.display_name}'s Profile"
    roles = ' '.join(
      [role.mention for role in user.roles if role.name != "@everyone"])
    join_date = user.joined_at.strftime('%B %d, %Y')    
    embed = discord.Embed(title=title, color=discord.Color(0xf177a6))
    embed.set_thumbnail(url=user.avatar)
    embed.add_field(name="Username", value=user.name, inline=True)
    embed.add_field(name="User ID", value=user.id, inline=True)
    embed.add_field(name="Roles", value=roles, inline=False)
    embed.add_field(name="Achivements", value="Not available", inline=False)
    embed.add_field(name="Join Date", value=join_date, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="add_xp", description="Add XP to a user")
async def add_xp(interaction: discord.Interaction, user: discord.User, added_xp: int):
    await update_user_xp(user.id, added_xp)
    await check_level_up(user.id, user)
    await interaction.response.send_message(f"Added {added_xp} to {user.mention} successfully")

# Command to report a user
@bot.tree.command(name="report", description="Report a user to the admins.")
@app_commands.describe(user="Who?", reason="Why?")
async def report(interaction: discord.Interaction, user: discord.User, *, reason: str):
    report_channel = bot.get_channel(1129867927013834833)
    if report_channel:
      report_embed = discord.Embed(
        title="User Report",
        description=
        f"Reported by: {interaction.user.mention}\nReported User: {user.mention}\nReason: {reason}",
        color=discord.Color.red())
      await report_channel.send(embed=report_embed)
      log_channel = bot.get_channel(1129340863709970490)
      await log_channel.send(
        f'{interaction.user.mention} reported {user.mention}')
      await interaction.response.send_message(
        "Thank you for your report. It has been submitted.", ephemeral=True)


# Command to mute a user
@bot.tree.command(name="mute", description="Mute a user")
@app_commands.describe(user="Who?")
@commands.has_permissions(mute_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, *, reason: str):
    # Find or create the "Muted" role
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
      muted_role = await interaction.guild.create_role(name="Muted")
    # Apply the "Muted" role to the user
    await user.add_roles(muted_role, reason=reason)
    embed = discord.Embed(title="User Muted",
                          description=f'{user.mention} has been muted.',
                          color=discord.Color.red())
    dm_embed = discord.Embed(
      title="**Important: Regarding Your Recent Mute**",
      description=
      f"**Hello {user.mention}**,\nYou've been temporarily muted by an admin to ensure a positive environment. If you have questions, Head over to <#1129340863512846379>.",
      color=discord.Color(0xf177a6))
    dm_embed.add_field(name="Reason", value=reason)
    dm_embed.set_footer(text=discord.utils.utcnow().strftime('%Y-%m-%d %H:%M'))
    dm_embed.set_thumbnail(url=user.avatar)
    await user.send(embed=dm_embed)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    log_channel = bot.get_channel(1129340863709970490)
    await log_channel.send(f'{interaction.user.mention} muted {user.mention}\nReason: {reason}')


# Command to unmute a user
@bot.tree.command(name="unmute", description="Unmute a user.")
@app_commands.describe(user="Who?")
@commands.has_permissions(mute_members=True)
async def unmute(interaction: discord.Interaction, user: discord.Member):
    # Find the "Muted" role
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if muted_role and muted_role in user.roles:
      # Remove the "Muted" role from the user
      await user.remove_roles(muted_role)
      embed = discord.Embed(title="User Unmuted",
                            description=f'{user.mention} has been unmuted.',
                            color=discord.Color.green())
      await interaction.response.send_message(embed=embed, ephemeral=True)
      log_channel = bot.get_channel(1129340863709970490)
      await log_channel.send(f'{interaction.user.mention} unmuted {user.mention}')
    else:
      embed = discord.Embed(title="Unmute Error",
                            description=f'{user.mention} is not muted.',
                            color=discord.Color.red())
      await interaction.response.send_message(embed=embed, ephemeral=True)


# Command to kick a user
@bot.tree.command(name="kick", description="Kick a user.")
@app_commands.describe(user="Who?")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    await user.kick(reason=reason)
    embed = discord.Embed(title="User kicked",
                          description=f'{user.mention} has been kicked.',
                          color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)
    log_channel = bot.get_channel(1129340863709970490)
    await log_channel.send(f'{interaction.user.mention} kicked {user.mention}\nReason: {reason}')


# Command to ban a user
@bot.tree.command(name="ban", description="Ban a user.")
@app_commands.describe(user="Who?")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str):
    await user.ban(reason=reason)
    embed = discord.Embed(title="User banned",
                          description=f'{user.mention} has been banned.',
                          color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)
    log_channel = bot.get_channel(1129340863709970490)
    await log_channel.send(f'{interaction.user.mention} banned {user.mention}')


# Command to timeout a user
@bot.tree.command(name='timeout', description='timeouts a user for a specific time')
@commands.has_permissions(kick_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0, reason: str = None):
    duration = datetime.timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)
    await user.timeout(duration, reason=reason)
    await interaction.response.send_message(f'{user.mention} was timed out until for {duration}', ephemeral=True)
    log_channel = bot.get_channel(1129340863709970490)
    await log_channel.send(f'{interaction.user.mention} timed out {user.mention} for {duration}')


# Command to delete all messages in a channel
@bot.tree.command(name="clear", description="Clear messages of the channel.")
@app_commands.describe(amount="How much messages do you want to delete?")
@commands.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.send_message(f"{amount} messages deleted.", delete_after=10, ephemeral=True)
    await interaction.channel.purge(limit=amount)
    log_channel = bot.get_channel(1129340863709970490)
    await log_channel.send(f'{interaction.user.mention} cleared {amount} message(s) in {interaction.channel.mention}')


ban.hidden = True
kick.hidden = True
mute.hidden = True
unmute.hidden = True
timeout.hidden = True
clear.hidden = True
add_xp.hidden = True


@bot.tree.command(name="help", description="List all available commands.")
async def help_command(interaction: discord.Interaction):
    user_permissions = interaction.user.guild_permissions   
    embed = discord.Embed(title="📜️ Help", color=discord.Color.green()) 
    for command in bot.tree.walk_commands():
      if user_permissions.kick_members or not getattr(command, "hidden", False):
        embed.add_field(name=f"`/{command.qualified_name}`",
                        value=command.description,
                        inline=False)   
    await interaction.response.send_message(embed=embed)


bot.run(config.TOKEN)
conn.close()
import discord
import ujson
import random
from easy_pil import Editor, Font, load_image_async, Canvas
import config
import version

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

with open('welcome_messages.json', 'r') as file:
    welcome_messages = ujson.load(file)

@bot.event
async def on_ready():
    print('Log bot v{version.version} is online')

@bot.event
async def on_member_join(member):
    role = member.guild.get_role(config.memberRoleID)
    await member.add_roles(role)
    log_channel = bot.get_channel(config.logChannelID)
    embed = discord.Embed(title=f"Welcome to {config.serverName}!", description=f"Welcome, {member.mention}! We're glad to have you here.", color=discord.Color.pink())
    embed.set_thumbnail(url=member.avatar)
    embed.add_field(name="Server Rules", value=f"Please take a moment to read the server rules in the <#{config.rulesChannelID}> channel.")
    embed.set_footer(text=f"You joined: {member.joined_at.strftime('%Y-%m-%d %H:%M')}")
    await member.send(embed=embed)
    #______________________________________
    random_message = random.choice(welcome_messages).format(member=member)
    background = Editor(Canvas((800, 450), color="#282828"))
    profile_picture = await load_image_async(str(member.avatar))
    profile = Editor(profile_picture).resize((150, 150)).circle_image()
    poppins = Font.poppins(size=50, variant='bold')
    poppins_small = Font.poppins(size=20)
    card_right_shape = [(640, 0), (800, 300), (800, 0)]
    background.polygon(card_right_shape, color="#ffffff")
    background.paste(profile, (325, 90))
    background.text((400, 260), f"Welcome to {config.serverName}", color="#ffffff", font=poppins, align="center")
    background.text((400, 325), f"{member.display_name}#{member.name}", color="#f1f1f1", font=poppins_small, align="center")
    file = discord.File(fp=background.image_bytes, filename="welcome.png")
    channel = bot.get_channel(config.logChannelID)
    await channel.send(random_message, file=file)
    await log_channel.send(f'{member.mention} has joined the server.')

@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send(f'{member.mention} has left the server.')
    
@bot.event
async def on_member_ban(guild, member):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send(f'{member.mention} has been banned.')

@bot.event
async def on_member_unban(guild, member):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send(f'{member.mention} has been unbanned.')

@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        log_channel = bot.get_channel(config.logChannelID)
        await log_channel.send(f'{after.name}\'s roles have been updated.')

@bot.event
async def on_message_delete(message):
    if not message.author.bot:
        log_channel = bot.get_channel(config.logChannelID)
        await log_channel.send(f'Message from {message.author.mention} in {message.channel.mention} was deleted: `{message.content}`')

@bot.event
async def on_message_edit(before, after):
    if not after.author.bot:
        log_channel = bot.get_channel(config.logChannelID)
        await log_channel.send(f'Message from {after.author.mention} in {after.channel.mention} was edited: `{before.content}` -> `{after.content}`')

@bot.event
async def on_reaction_add(reaction, user):
    if not user.bot:
        log_channel = bot.get_channel(config.logChannelID)
        message_link = f"https://discord.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{reaction.message.id}"
        await log_channel.send(f'Reaction `{reaction.emoji}` from {user.mention} was added to [a message]({message_link})')

@bot.event
async def on_reaction_remove(reaction, user):
    if not user.bot:
        log_channel = bot.get_channel(config.logChannelID)
        message_link = f"https://discord.com/channels/{reaction.message.guild.id}/{reaction.message.channel.id}/{reaction.message.id}"
        await log_channel.send(f'Reaction `{reaction.emoji}` from {user.mention} was removed from [a message]({message_link})')

@bot.event
async def on_guild_update(before, after):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send('Guild information updated')

@bot.event
async def on_guild_role_create(role):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send(f'New role created: `{role.name}`')

@bot.event
async def on_guild_role_delete(role):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send(f'Role deleted: `{role.name}`')

@bot.event
async def on_guild_role_update(before, after):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send(f'Role updated: `{before.name}` -> `{after.name}`')

@bot.event
async def on_guild_channel_create(channel):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send(f'New channel created: {channel.mention}')

@bot.event
async def on_guild_channel_delete(channel):
    log_channel = bot.get_channel(config.logChannelID)
    await log_channel.send(f'Channel deleted: `{channel.name}`')

@bot.event
async def on_guild_channel_update(before, after):
    if before.name != after.name:
        log_channel = bot.get_channel(config.logChannelID)
        await log_channel.send(f'{after.mention} name updated: `{before.name}` -> `{after.name}`')
    elif before.overwrites != after.overwrites:
        log_channel = bot.get_channel(config.logChannelID)
        await log_channel.send(f'{after.mention} permissions updated')

bot.run(config.TOKEN)
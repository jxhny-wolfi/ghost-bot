import disnake
from disnake.ext import commands
import json
import os
import asyncio

# Load or initialize welcome settings
def load_welcome_settings():
    if os.path.exists("welcome_settings.json"):
        with open("welcome_settings.json", "r") as file:
            return json.load(file)
    return {}

def save_welcome_settings(settings):
    with open("welcome_settings.json", "w") as file:
        json.dump(settings, file)

# Define the bot and intents
intents = disnake.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="/", intents=intents)

# Load welcome settings from file
welcome_settings = load_welcome_settings()

@bot.slash_command(name="welcome", description="Set the welcome channel, message, image, and delay. | SOON")
async def welcome(
    inter: disnake.AppCmdInter,
    channel: disnake.TextChannel,
    message: str,
    delay: int,
    image_url: str = None
):
    # Save settings
    welcome_settings[str(inter.guild.id)] = {
        "channel_id": channel.id,
        "message": message,
        "delay": delay,
        "image_url": image_url
    }
    save_welcome_settings(welcome_settings)

    await inter.response.send_message(f"Welcome settings saved! Messages will be sent to {channel.mention}.")

@bot.event
async def on_member_join(member: disnake.Member):
    guild_id = str(member.guild.id)
    if guild_id in welcome_settings:
        settings = welcome_settings[guild_id]
        channel = bot.get_channel(settings["channel_id"])
        if channel:
            # Wait for the specified delay before sending the welcome message
            await asyncio.sleep(settings["delay"])
            
            # Create the embed with a smaller image
            embed = disnake.Embed(title="Willkommen!", description=settings["message"], color=0x00ff00)
            if settings["image_url"]:
                embed.set_image(url=settings["image_url"])
                embed.set_footer(text="Made by Ghost", icon_url="https://media.discordapp.net/attachments/1242127020062933062/1289798885681926155/image.png?ex=66fa2251&is=66f8d0d1&hm=bce9a1f2d732d17e8092e046c2573af2278ad75222d25b996bd6c5cd5daf96a0&=&format=webp&quality=lossless")
                
                # Limit the image size in the message if necessary
                embed.description += "\n\n![Image](https://media.discordapp.net/attachments/1242127020062933062/1289798885681926155/image.png?ex=66fa2251&is=66f8d0d1&hm=bce9a1f2d732d17e8092e046c2573af2278ad75222d25b996bd6c5cd5daf96a0&=&format=webp&quality=lossless)"
                
            await channel.send(embed=embed)



@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}.")


# Setze den Status des Bots
@bot.event
async def on_ready():
    activity = disnake.Game(name="Ghost")
    await bot.change_presence(status=disnake.Status.online, activity=activity)

import disnake
from disnake.ext import commands
import pytz
from datetime import datetime



@bot.slash_command(name="ping", description="Check the bot's latency and get the current time in a specified timezone.")
async def ping(inter: disnake.AppCmdInter, timezone: str = "UTC"):
    # Defer the interaction to allow time for processing
    await inter.response.defer()

    # Calculate the latency
    latency = round(bot.latency * 1000)  # Convert latency to milliseconds

    # Get current time in the specified timezone
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    except pytz.UnknownTimeZoneError:
        return await inter.edit_original_response(content="Unknown timezone. Please provide a valid timezone string.", ephemeral=True)

    # Create an embed message
    embed = disnake.Embed(title="Ping Information", color=0x00ff00)
    embed.add_field(name="Latency", value=f"{latency} ms", inline=False)
    embed.add_field(name="Current Time", value=current_time, inline=False)
    embed.add_field(name="Timezone", value=timezone, inline=False)

    await inter.edit_original_response(embed=embed)



import disnake
from disnake.ext import commands


async def update_status():
    while True:
        # Set the bot's activity to streaming with a link
        activity = disnake.Streaming(name="Currently streaming!", url="https://www.youtube.com/live/ralJmHG-DII?si=I8-SEoly2wlkKddM")
        await bot.change_presence(activity=activity)
        
        # Sleep for a certain period before updating again (optional)
        await disnake.utils.sleep(60)  # Updates every minute (60 seconds)

   
import disnake
from disnake.ext import commands
import json
import os
from datetime import datetime, timezone



# Load or create ticket data file
data_file = "tickets.json"

if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f)

# Load existing tickets
with open(data_file, 'r') as f:
    tickets = json.load(f)

# Function to create a new ticket
async def create_ticket_channel(ticket_name, guild):
    # Create a new channel for the ticket
    channel = await guild.create_text_channel(ticket_name)
    
    # Deny @everyone from reading messages in the ticket channel
    await channel.set_permissions(guild.default_role, read_messages=False)  

    return channel

# Function to create a ticket button
async def send_ticket_button(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(
        title="Create a Ticket",
        description="Click the button below to create a ticket.",
        color=0x00ff00
    )
    embed.set_footer(text="Made by Ghost")  # Update footer text

    # Create a button with an emoji
    button = disnake.ui.Button(label="🎟️ Create Ticket", style=disnake.ButtonStyle.green)

    async def button_callback(interaction):
        guild = interaction.guild
        ticket_name = f"ticket-{interaction.user.name}-{interaction.user.id}"
        
        # Check if the ticket already exists
        if ticket_name in tickets:
            await interaction.response.send_message("You already have an open ticket!", ephemeral=True)
            return

        # Create the ticket channel
        channel = await create_ticket_channel(ticket_name, guild)

        # Store the ticket info
        tickets[ticket_name] = {"user_id": interaction.user.id, "channel_id": channel.id}
        with open(data_file, 'w') as f:
            json.dump(tickets, f)

        # Send a welcome message in the new ticket channel
        embed = disnake.Embed(
            title="Ticket Created",
            description="Please describe your issue below.",
            color=0x00ff00
        )
        embed.set_footer(text="Made by Ghost")  # Update footer text
        embed.timestamp = datetime.now(timezone.utc)  # Use timezone-aware UTC datetime
        await channel.send(embed=embed)

        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

    button.callback = button_callback
    view = disnake.ui.View()
    view.add_item(button)

    await inter.response.send_message(embed=embed, view=view)

# Command to create a ticket
@bot.slash_command(name="ticket", description="Create a ticket ")
async def ticket(inter: disnake.ApplicationCommandInteraction):
    await send_ticket_button(inter)

# Command to close a ticket
@bot.slash_command(name="close_ticket", description="Close your ticket | SOON")
async def close_ticket(inter: disnake.ApplicationCommandInteraction):
    # Check if the user is in a ticket channel
    channel = inter.channel
    if not channel or not channel.name.startswith("ticket-"):
        await inter.response.send_message("You can only close tickets in ticket channels.", ephemeral=True)
        return

    # Check if the ticket exists in the dictionary
    ticket_name = channel.name
    if ticket_name not in tickets:
        await inter.response.send_message("This ticket does not exist.", ephemeral=True)
        return

    user_id = tickets[ticket_name]["user_id"]
    
    # Check if the user is the ticket owner
    if inter.user.id != user_id:
        await inter.response.send_message("You cannot close this ticket because you are not the owner.", ephemeral=True)
        return

    # Confirm ticket closure
    await channel.send(f"Ticket closed by {inter.user.mention}. Thank you for using our support!")
    await channel.delete()

    # Remove the ticket from the stored tickets
    del tickets[ticket_name]
    with open(data_file, 'w') as f:
        json.dump(tickets, f)

    await inter.response.send_message("Your ticket has been closed.", ephemeral=True)

# Load existing tickets on startup
@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}.")
    guild = bot.guilds[0]  # Get the first guild the bot is in
    
    for ticket_name, ticket_data in tickets.items():
        channel_id = ticket_data["channel_id"]
        channel = guild.get_channel(channel_id)
        
        # Check if the channel still exists
        if channel is None:
            continue
        
        # Send a message to the existing ticket channel to notify the user
        user = guild.get_member(ticket_data["user_id"])
        if user is not None:
            await channel.send(f"Welcome back, {user.mention}! You can continue your support here.")

# Note: The bot's token will be set outside of this script or managed through your deployment environment.




import disnake
from disnake.ext import commands
from collections import defaultdict


# Store AFK statuses
afk_users = defaultdict(str)

@bot.slash_command(name="afk", description="Set your AFK status.")
async def afk(inter: disnake.ApplicationCommandInteraction, reason: str = "No reason provided."):
    # Set the user's AFK status
    afk_users[inter.user.id] = reason
    await inter.response.send_message(f"You are now AFK: {reason}", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if the author is AFK
    if message.author.id in afk_users:
        reason = afk_users[message.author.id]
        await message.channel.send(f"{message.author.mention} is currently AFK: {reason}")
        
    # Process commands
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    # Check if the author is AFK on message edit
    if after.author.bot:
        return

    if after.author.id in afk_users:
        reason = afk_users[after.author.id]
        await after.channel.send(f"{after.author.mention} is currently AFK: {reason}")

@bot.event
async def on_member_update(before, after):
    # Check if the member comes back from AFK
    if before.status == disnake.Status.offline and after.status != disnake.Status.offline:
        if before.id in afk_users:
            reason = afk_users[before.id]
            del afk_users[before.id]  # Remove AFK status
            channel = await after.create_dm()
            await channel.send(f"Welcome back, {before.mention}! You were AFK for: {reason}")


import disnake
from disnake.ext import commands



# Define the permissions required by the bot
REQUIRED_PERMISSIONS = [
    'administrator',  # Example: Administrator permission
    'manage_channels',
    'send_messages',
    'read_messages',
    'embed_links',
]

@bot.slash_command()
async def permissions(interaction: disnake.ApplicationCommandInteraction):
    """Displays the permissions required by the bot."""
    # Get the bot's permissions in the guild
    bot_permissions = interaction.guild.me.guild_permissions
    missing_permissions = [perm for perm in REQUIRED_PERMISSIONS if not getattr(bot_permissions, perm)]

    if not missing_permissions:
        await interaction.send("The bot has all the required permissions!")
    else:
        missing_permissions_names = [perm.replace('_', ' ').capitalize() for perm in missing_permissions]
        await interaction.send(f"The bot is missing the following permissions: {', '.join(missing_permissions_names)}")



import disnake
from disnake.ext import commands
import random


@bot.slash_command()
async def clear(interaction: disnake.ApplicationCommandInteraction, amount: int):
    """Clears a specified number of messages in the channel with a bit of humor."""
    if amount < 1 or amount > 100:
        await interaction.send("Whoa there! Please provide a number between 1 and 100. Even my programming has limits!", ephemeral=True)
        return

    # Create a funny confirmation message
    funny_lines = [
        "Are you sure you want to send these messages to the void? They're just gonna float away!",
        "Deleting messages is like cleaning your room... necessary but not fun!",
        "Do you really want to clear these messages? They had dreams, you know!",
        "Let’s do this! Say goodbye to those messages like it’s the last slice of pizza!"
    ]
    
    confirmation_text = random.choice(funny_lines)
    
    confirm_embed = disnake.Embed(
        title="Hold on a second!",
        description=confirmation_text,
        color=disnake.Color.green()
    )

    try:
        # Send the confirmation message
        confirm_message = await interaction.send(embed=confirm_embed)

        # Wait for confirmation from the user
        await interaction.send("Type `yes` to confirm or `no` to cancel.", ephemeral=True)
        
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        # Wait for the user's response
        response = await bot.wait_for('message', timeout=30.0, check=check)

        if response.content.lower() == 'yes':
            # If confirmed, delete the messages
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.send(f"Boom! {len(deleted)} messages have been sent to the digital abyss. Goodbye forever!", ephemeral=True)
        else:
            await interaction.send("Phew! Those messages are safe for now. You're welcome!", ephemeral=True)

    except Exception as e:
        # Handle any errors that occur during the sending of the message
        await interaction.send(f"An error occurred: {str(e)}. My bad!", ephemeral=True)




import disnake
from disnake.ext import commands
import random
import string



# Dictionary to store premium codes and their associated user IDs
premium_codes = {}
user_premium_status = {}
owner_id = 1242092673096220763
@bot.slash_command()
async def generate_code(interaction: disnake.ApplicationCommandInteraction):
    """Generate a premium code for the bot owner."""
    # Only allow the bot owner to generate codes
    if interaction.user.id != bot.owner_id:
        await interaction.send("Only the bot owner can generate premium codes!", ephemeral=True)
        return

    # Generate a unique 8-character premium code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Store the code privately
    premium_codes[code] = interaction.user.id  # Associate the code with the owner
    await interaction.send(f"Generated premium code: `{code}`. Share it with users privately!")

@bot.slash_command()
async def redeem_code(interaction: disnake.ApplicationCommandInteraction, code: str):
    """Redeem a premium code."""
    if code in premium_codes:
        user_id = interaction.user.id
        
        # Check if the code has already been redeemed
        if user_id in user_premium_status:
            await interaction.send("You already have premium access!", ephemeral=True)
            return
        
        # Redeem the code
        user_premium_status[user_id] = code
        await interaction.send("Congratulations! You've redeemed a premium code!")
    else:
        await interaction.send("Invalid premium code. Please check and try again.", ephemeral=True)

@bot.slash_command()
async def check_premium(interaction: disnake.ApplicationCommandInteraction):
    """Check if the user has premium access."""
    if interaction.user.id in user_premium_status:
        await interaction.send("You have premium access! Enjoy exclusive features.", ephemeral=True)
    else:
        await interaction.send("You do not have premium access. Consider redeeming a premium code!", ephemeral=True)

@bot.slash_command()
async def premium_command(interaction: disnake.ApplicationCommandInteraction):
    """A premium-only command."""
    if interaction.user.id in user_premium_status:
        await interaction.send("This is a premium command. Enjoy your exclusive access!", ephemeral=True)
    else:
        await interaction.send("You need premium access to use this command. Redeem a code!", ephemeral=True)




import disnake
from disnake.ext import commands



@bot.slash_command()
async def rules(interaction: disnake.ApplicationCommandInteraction):
    """Send the bot rules."""
    embed = disnake.Embed(title="Bot Rules", color=disnake.Color.green())

    # Add rules for the bot
    embed.add_field(name="1. Use Commands Responsibly", value="Do not spam commands. Use them as intended to ensure smooth operation.", inline=False)
    embed.add_field(name="2. Respect the Bot's Limitations", value="Understand that the bot may not always respond immediately or may have limitations on certain commands.", inline=False)
    embed.add_field(name="3. Report Issues", value="If you encounter a bug or issue with the bot, report it to the bot owner for resolution.", inline=False)
    embed.add_field(name="4. No Abuse of Commands", value="Avoid exploiting any commands for malicious purposes. This can lead to a ban from using the bot.", inline=False)
    embed.add_field(name="5. Follow Discord's Community Guidelines", value="Ensure that your interactions with the bot comply with Discord's terms and community standards.", inline=False)
    embed.add_field(name="6. Have Fun!", value="Enjoy using the bot and make the most out of its features!", inline=False)

    # Send the embed message
    await interaction.send(embed=embed)




import disnake
from disnake.ext import commands

@bot.slash_command()
async def say(interaction: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel, message: str, embed_message: bool = False):
    """Make the bot say a message in the specified channel."""
    if embed_message:
        # Create an embed if the embed option is true
        embed = disnake.Embed(description=message, color=disnake.Color.blue())
        await channel.send(embed=embed)
    else:
        await channel.send(message)
    
    await interaction.send(f"Message sent to {channel.mention}!", ephemeral=True)



import disnake
from disnake.ext import commands

# Define the bot and intents


# Dictionary to store user websites
user_websites = {}

@bot.slash_command()
async def website(interaction: disnake.ApplicationCommandInteraction, user_website: str, description: str):
    """Store and display user websites with a description."""
    
    # Save the user's website and description
    user_id = interaction.user.id
    user_websites[user_id] = {
        "url": user_website,
        "description": description
    }
    
    # Create an embed to display the information
    embed = disnake.Embed(
        title=f"Website Submitted!",
        description=f"**URL**: {user_website}\n**Description**: {description}",
        color=disnake.Color.green()
    )
    
    await interaction.send(embed=embed)

@bot.slash_command()
async def show_website(interaction: disnake.ApplicationCommandInteraction):
    """Show the user's submitted website and description."""
    
    user_id = interaction.user.id
    
    # Check if the user has submitted a website
    if user_id in user_websites:
        info = user_websites[user_id]
        embed = disnake.Embed(
            title="Your Website Information",
            description=f"**URL**: {info['url']}\n**Description**: {info['description']}",
            color=disnake.Color.blue()
        )
        await interaction.send(embed=embed)
    else:
        await interaction.send("You haven't submitted any website information yet.", ephemeral=True)





import disnake
import random
import string
from disnake.ext import commands



# Dictionary to store verified users and their codes
verified_users = {}

# Generate a random verification code
def generate_verification_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Verification command
@bot.slash_command(name="verify", description="Verify yourself to get the invite link.")
async def verify(interaction: disnake.ApplicationCommandInteraction):
    user_id = str(interaction.user.id)

    # Check if the user is already verified
    if user_id in verified_users:
        await interaction.send("You are already verified! Use `/invite` to get the bot invite link.", ephemeral=True)
        return

    # Generate a new verification code and store it
    verification_code = generate_verification_code()
    verified_users[user_id] = verification_code

    await interaction.send(f"Your verification code is: `{verification_code}`. Please keep it safe!", ephemeral=True)

# Check verification command
@bot.slash_command(name="check_verification", description="Check your verification status.")
async def check_verification(interaction: disnake.ApplicationCommandInteraction):
    user_id = str(interaction.user.id)

    # Check if the user is verified
    if user_id in verified_users:
        await interaction.send("You are verified! Use `/invite` to get the bot invite link.", ephemeral=True)
    else:
        await interaction.send("You are not verified yet. Use `/verify` to get your verification code.", ephemeral=True)

# Invite command that requires verification
@bot.slash_command(name="invite", description="Get the invite link for the bot.")
async def invite(interaction: disnake.ApplicationCommandInteraction):
    user_id = str(interaction.user.id)

    # Check if the user is verified
    if user_id not in verified_users:
        await interaction.send("You need to verify before you can get the invite link! Use `/verify` to get started.", ephemeral=True)
        return

    # Send the bot invite link
    invite_link = "https://discord.com/oauth2/authorize?client_id=1289763054858534952&permissions=8&scope=bot"
    await interaction.send(f"Here is your invite link: {invite_link}")



import disnake
from disnake.ext import commands



# Help command that dynamically fetches registered commands
@bot.slash_command(name="help", description="Get help about bot commands.")
async def help_command(interaction: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="Help Command", color=disnake.Color.blue())
    embed.set_footer(text="Use /<command> to execute.")

    # Iterate over all registered commands
    for command in bot.commands:
        embed.add_field(name=f"/{command.name}", value=command.description or "No description available.", inline=False)

    await interaction.response.send_message(embed=embed)



@bot.slash_command(name="info", description="Get information about the bot.")
async def info(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.send_message("I am your friendly bot!")

@bot.slash_command(name="kick", description="Kick a user from the server.")
async def kick(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.send_message("User kicked!")

@bot.slash_command(name="ban", description="Ban a user from the server.")
async def ban(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.send_message("User banned!")

@bot.slash_command(name="joke", description="Get a random joke.")
async def joke(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.send_message("Here's a funny joke!")

@bot.slash_command(name="meme", description="Get a random meme.")
async def meme(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.send_message("Here's a meme!")










# Run the bot
bot.run("MTI4OTc2MzA1NDg1ODUzNDk1Mg.GtVj3v.M1KBzuBnGOCZyw-XXQ-m9rg5_4DPWvzL2nrjcc")
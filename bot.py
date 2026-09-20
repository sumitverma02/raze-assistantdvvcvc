



import os
import threading
from flask import Flask

# Dummy HTTP server Render ke port timeout error ko rokn ke liye
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# Flask server start karein
keep_alive()

# --- Aapka baaki purana discord bot code niche same rahega ---


import discord
from discord.ext import commands
from discord import app_commands, Interaction, ButtonStyle
from discord.ui import View, Button, Select
from googleapiclient.discovery import build
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
BOT_TOKEN = "MTU1MTEzMjIyMTk2MjcxNTIwNw.GXAeXH.wq99ye4oXL1jlxs_3CeQDeVI0My2rgPXGulUw8"
YOUTUBE_API_KEY = "AIzaSyD6omIKIyD8VQuH972HalMsX6fwil9bX4w"

# Channel IDs Set Karo
WELCOME_CHANNEL_ID = 15199704691331564826  # Welcome message channel
LOG_CHANNEL_ID = 15501440331275388096    # Join/Leave & Moderation logs channel
TICKET_CATEGORY_ID = 15199656774931578886  # Category jahan ticket channels banenge

intents = discord.Intents.all()

class RazeAssistant(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Persistent Views register kar rahe hain taaki bot restart hone par bhi buttons kaam karein
        self.add_view(TicketLauncher())
        self.add_view(RoleSelectionView())
        await self.tree.sync()
        print("✅ Slash commands and persistent views synced globally!")

    async def on_ready(self):
        print(f'👑 {self.user.name} is now online and fully equipped for Raze Town!')
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name="over Raze Town | /help"
            )
        )

bot = RazeAssistant()
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# ==========================================
# 1. INTERACTIVE TICKET SYSTEM (BUTTONS)
# ==========================================
class TicketCloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🔒", style=ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: Interaction, button: Button):
        await interaction.response.send_message("🔒 Closing ticket in 5 seconds...")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketLauncher(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket 📩", style=ButtonStyle.green, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: Interaction, button: Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        
        # Check if user already has a ticket
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"⚠️ You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"🎫 Ticket Created by {interaction.user.display_name}",
            description="Please explain your issue here. Staff will assist you shortly.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed, view=TicketCloseButton())
        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

@bot.tree.command(name="sendticketembed", description="Send ticket creation panel (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def sendticketembed(interaction: Interaction):
    embed = discord.Embed(
        title="📩 Raze Town Support Center",
        description="Click the button below to open a ticket if you need assistance from our staff.",
        color=discord.Color.gold()
    )
    await interaction.channel.send(embed=embed, view=TicketLauncher())
    await interaction.response.send_message("Ticket panel sent!", ephemeral=True)

# ==========================================
# 2. REACTION ROLES (DROPDOWN MENU)
# ==========================================
class RoleDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Gamer", emoji="🎮", description="Access gaming channels"),
            discord.SelectOption(label="Updates", emoji="📢", description="Get notified for announcements"),
            discord.SelectOption(label="Events", emoji="🎉", description="Get notified for server events"),
        ]
        super().__init__(placeholder="Choose your roles...", min_values=0, max_values=3, custom_id="role_dropdown_menu")

    async def callback(self, interaction: Interaction):
        # Apne roles ke exact names yahan match karein
        role_map = {
            "Gamer": "Gamer",
            "Updates": "Announcement Ping",
            "Events": "Event Ping"
        }
        
        guild = interaction.guild
        member = interaction.user
        selected = self.values
        
        added_roles = []
        removed_roles = []

        for label, role_name in role_map.items():
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                if label in selected:
                    await member.add_roles(role)
                    added_roles.append(role.name)
                else:
                    await member.remove_roles(role)
                    removed_roles.append(role.name)

        await interaction.response.send_message("✅ Roles updated successfully!", ephemeral=True)

class RoleSelectionView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleDropdown())

@bot.tree.command(name="sendrolesembed", description="Send self-roles selection panel (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def sendrolesembed(interaction: Interaction):
    embed = discord.Embed(
        title="🎭 Pick Your Roles",
        description="Select the roles you want from the dropdown menu below to get notifications!",
        color=discord.Color.purple()
    )
    await interaction.channel.send(embed=embed, view=RoleSelectionView())
    await interaction.response.send_message("Roles panel sent!", ephemeral=True)

# ==========================================
# 3. MODERATION MODULE
# ==========================================
@bot.tree.command(name="purge", description="Bulk delete messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: Interaction, amount: int):
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Deleted **{len(deleted)}** messages.", ephemeral=True)

@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"🚨 **{member.display_name}** kicked. Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ **{member.display_name}** banned. Reason: {reason}")

@bot.tree.command(name="timeout", description="Mute/Timeout a member (in minutes)")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    from datetime import timedelta
    duration = timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 **{member.display_name}** timed out for {minutes}m. Reason: {reason}")

# ==========================================
# 4. UTILITY & INFO MODULE
# ==========================================
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: Interaction):
    await interaction.response.send_message(f"🏓 Pong! Latency: **{round(bot.latency * 1000)}ms**")

@bot.tree.command(name="userinfo", description="Get details of a user")
async def userinfo(interaction: Interaction, member: discord.Member = None):
    target = member or interaction.user
    embed = discord.Embed(title=f"👤 {target.display_name}'s Info", color=target.color)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="Username", value=str(target), inline=True)
    embed.add_field(name="Account Created", value=target.created_at.strftime("%d %b %Y"), inline=True)
    embed.add_field(name="Joined Server", value=target.joined_at.strftime("%d %b %Y"), inline=True)
    embed.add_field(name="Roles", value=", ".join([role.mention for role in target.roles[1:]]) or "None", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Display Raze Town statistics")
async def serverinfo(interaction: Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 {guild.name} Stats", color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Total Members", value=f"👥 {guild.member_count}", inline=True)
    embed.add_field(name="Channels", value=f"💬 {len(guild.channels)}", inline=True)
    embed.add_field(name="Owner", value=f"👑 {guild.owner.mention}", inline=True)
    await interaction.response.send_message(embed=embed)

# ==========================================
# 5. YOUTUBE STATS MODULE
# ==========================================
@bot.tree.command(name="ytstats", description="Fetch live YouTube stats")
async def ytstats(interaction: Interaction, channel_handle: str):
    await interaction.response.defer()
    try:
        handle = channel_handle.replace("@", "")
        search_res = youtube.search().list(q=handle, type='channel', part='id', maxResults=1).execute()
        if not search_res['items']:
            await interaction.followup.send(f"❌ No channel found for `{channel_handle}`.", ephemeral=True)
            return

        channel_id = search_res['items'][0]['id']['channelId']
        res = youtube.channels().list(id=channel_id, part='snippet,statistics').execute()
        snippet, stats = res['items'][0]['snippet'], res['items'][0]['statistics']

        created_date = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d %B %Y")
        subscribers = f"{int(stats['subscriberCount']):,}" if 'subscriberCount' in stats else "Hidden"

        embed = discord.Embed(title=f"🔴 {snippet['title']}", url=f"https://youtube.com/channel/{channel_id}", color=discord.Color.red())
        embed.set_thumbnail(url=snippet['thumbnails']['high']['url'])
        embed.add_field(name="👥 Subscribers", value=f"**{subscribers}**", inline=True)
        embed.add_field(name="📹 Videos", value=f"**{int(stats['videoCount']):,}**", inline=True)
        embed.add_field(name="👁️ Views", value=f"**{int(stats['viewCount']):,}**", inline=True)
        embed.add_field(name="📅 Created", value=f"**{created_date}**", inline=False)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: `{str(e)}`", ephemeral=True)

# ==========================================
# 6. AUTO-WELCOME & LOGS EVENTS
# ==========================================
@bot.event
async def on_member_join(member):
    # 1. Send Welcome Message
    welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        embed = discord.Embed(
            title="🎉 Welcome to Raze Town!",
            description=f"Hey {member.mention}, welcome to our community! Make sure to grab your roles and read the rules.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await welcome_channel.send(embed=embed)

    # 2. Join Log
    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} ({member}) joined the server.",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    # Leave Log
    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="📤 Member Left",
            description=f"**{member}** has left the server.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        await log_channel.send(embed=embed)

import os

# Baaki saara bot code same rahega
bot.run(os.getenv("BOT_TOKEN"))
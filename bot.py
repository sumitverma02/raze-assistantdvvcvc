
import os
import threading
from flask import Flask

# Dummy HTTP server Render ke port timeout error ko rokne ke liye
app = Flask('')

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "Bot is alive!", 200

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# Flask server start karein
keep_alive()

# --- Aapka baaki purana discord bot code niche same rahega ---


import asyncio
import os
import threading
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks
from flask import Flask, render_template_string

# ==========================================
# 1. KEEP-ALIVE FLASK SERVER FOR RENDER
# ==========================================
app = Flask('')

INVITE_URL = "https://discord.com/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=8&scope=bot%20applications.commands"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Raze Assistant - Bot Status</title>
    <style>
        body { background-color: #0f172a; color: white; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 40px; border-radius: 15px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .status { background: #22c55e; color: black; padding: 5px 10px; border-radius: 10px; font-weight: bold; font-size: 12px; }
        .btn { display: inline-block; margin-top: 20px; padding: 12px 24px; background: #5865f2; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <span class="status">🟢 ONLINE 24/7</span>
        <h1>Raze Assistant</h1>
        <p>Official Multipurpose Discord Bot for Raze Town</p>
        <a href="{{ invite_url }}" target="_blank" class="btn">🤖 Add to Discord</a>
    </div>
</body>
</html>
"""


@app.route('/', methods=['GET', 'HEAD'])
def home():
  return render_template_string(HTML_TEMPLATE, invite_url=INVITE_URL), 200


def run():
  port = int(os.environ.get("PORT", 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = threading.Thread(target=run)
  t.start()


keep_alive()

# ==========================================
# 2. DISCORD BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Global IDs (Apne Server aur YouTube Channel ke hisab se set karein)
GUILD_ID = None  # Server ID (optional for global slash commands)
MEMBER_COUNT_CHANNEL_ID = None  # Voice channel ID for Member Counter
YT_SUBS_CHANNEL_ID = None  # Voice channel ID for YT Subs Counter
YT_CHANNEL_ID = "UC_YOUR_YOUTUBE_CHANNEL_ID"  # YouTube Channel ID
YT_API_KEY = "YOUR_YOUTUBE_API_KEY"  # Optional: YouTube Data API Key


# ==========================================
# 3. INTERACTIVE TICKET SYSTEM VIEWS
# ==========================================
class TicketCreateView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="📩 Create Ticket",
      style=discord.ButtonStyle.primary,
      custom_id="create_ticket_btn",
  )
  async def create_ticket(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    guild = interaction.guild
    user = interaction.user

    # Check if channel already exists
    channel_name = f"ticket-{user.name}".lower().replace(" ", "-")
    existing_channel = discord.utils.get(
        guild.text_channels, name=channel_name
    )

    if existing_channel:
      return await interaction.response.send_message(
          f"❌ Aapka ticket pehle se khula hai: {existing_channel.mention}",
          ephemeral=True,
      )

    # Permission Overwrites
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(
            read_messages=True, send_messages=True
        ),
        guild.me: discord.PermissionOverwrite(
            read_messages=True, send_messages=True
        ),
    }

    ticket_channel = await guild.create_text_channel(
        name=channel_name, overwrites=overwrites, reason="Support Ticket"
    )

    embed = discord.Embed(
        title="🎫 Ticket Created",
        description=(
            f"Hello {user.mention}, humari support team jald hi aapki help"
            " karegi.\n\nTicket close karne ke liye niche **Close** button par"
            " click karein."
        ),
        color=discord.Color.green(),
    )

    await ticket_channel.send(
        content=f"{user.mention}", embed=embed, view=TicketCloseView()
    )
    await interaction.response.send_message(
        f"✅ Aapka ticket yahan create ho gaya hai: {ticket_channel.mention}",
        ephemeral=True,
    )


class TicketCloseView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="🔒 Close Ticket",
      style=discord.ButtonStyle.danger,
      custom_id="close_ticket_btn",
  )
  async def close_ticket(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_message(
        "Deleting ticket in 5 seconds..."
    )
    await asyncio.sleep(5)
    await interaction.channel.delete(reason="Ticket Closed")


# ==========================================
# 4. BOT EVENTS & MENTION RESPONDER
# ==========================================
@bot.event
async def on_ready():
  print(f"Logged in as {bot.user} (ID: {bot.user.id})")

  # Add Persistent Views
  bot.add_view(TicketCreateView())
  bot.add_view(TicketCloseView())

  # Sync Slash Commands
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash command(s)")
  except Exception as e:
    print(f"Failed to sync slash commands: {e}")

  # Set Presence
  await bot.change_presence(
      activity=discord.Activity(
          type=discord.ActivityType.watching,
          name="Watching over Raze Town | /help",
      )
  )

  # Start Background Counter Loop
  update_counters.start()


@bot.event
async def on_message(message: discord.Message):
  if message.author.bot:
    return

  # Respond when bot is mentioned
  if bot.user.mentioned_in(message) and not message.mention_everyone:
    embed = discord.Embed(
        title="👋 Hello! Main hoon Raze Assistant",
        description=(
            f"Aap mujhe mention kyu kar rahe ho? Mujhe commands dene ke liye"
            f" **`/help`** type karein!\n\n**Server:**"
            f" {message.guild.name}\n**Bot Status:** 🟢 Online 24/7"
        ),
        color=discord.Color.blue(),
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await message.channel.send(embed=embed)

  await bot.process_commands(message)


# ==========================================
# 5. LIVE MEMBER & YT COUNTERS (BACKGROUND TASK)
# ==========================================
@tasks.loop(minutes=10)
async def update_counters():
  for guild in bot.guilds:
    # 1. Update Discord Member Count Voice Channel
    if MEMBER_COUNT_CHANNEL_ID:
      channel = guild.get_channel(MEMBER_COUNT_CHANNEL_ID)
      if channel:
        member_count = guild.member_count
        await channel.edit(name=f"💙 Members: {member_count}")

    # 2. Update YouTube Subs Count Voice Channel (If API Key Present)
    if YT_SUBS_CHANNEL_ID and YT_API_KEY and YT_CHANNEL_ID:
      url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YT_CHANNEL_ID}&key={YT_API_KEY}"
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
          if resp.status == 200:
            data = await resp.json()
            if "items" in data and len(data["items"]) > 0:
              subs = data["items"][0]["statistics"]["subscriberCount"]
              yt_channel = guild.get_channel(YT_SUBS_CHANNEL_ID)
              if yt_channel:
                await yt_channel.edit(name=f"🔴 YT Subs: {subs}")


# ==========================================
# 6. SLASH COMMANDS
# ==========================================


# /help Command
@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
  embed = discord.Embed(
      title="🛠️ Raze Assistant Commands List",
      description=(
          "Raze Town server ke sabhi active commands ki list niche di gayi"
          " hai:"
      ),
      color=discord.Color.purple(),
  )
  embed.add_field(
      name="📌 General", value="`/ping` - Check bot latency\n`/help` - Show help menu", inline=False
  )
  embed.add_field(
      name="⚙️ Moderation & Utility",
      value=(
          "`/clear <amount>` - Delete messages\n`/embed` - Create Sapphire-style"
          " custom embed\n`/poll` - Create interactive button poll"
      ),
      inline=False,
  )
  embed.add_field(
      name="🎫 Ticket System",
      value="`/ticket-setup` - Deploy Ticket creation panel",
      inline=False,
  )
  embed.add_field(
      name="📊 Live Stats",
      value="`/setup-counters` - Configure member counter channel ID",
      inline=False,
  )
  embed.set_footer(
      text="Raze Assistant | Raze Town",
      icon_url=interaction.guild.icon.url if interaction.guild.icon else None,
  )
  await interaction.response.send_message(embed=embed)


# /ping Command
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
  latency = round(bot.latency * 1000)
  await interaction.response.send_message(f"🏓 Pong! Latency: `{latency}ms`")


# /clear Command
@bot.tree.command(name="clear", description="Purge messages from channel")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
  await interaction.response.defer(ephemeral=True)
  deleted = await interaction.channel.purge(limit=amount)
  await interaction.followup.send(
      f"🧹 Successfully deleted `{len(deleted)}` messages.", ephemeral=True
  )


# /embed Command (Sapphire Style Rich Embed Builder)
@bot.tree.command(name="embed", description="Create a custom Sapphire-style Embed")
@app_commands.checks.has_permissions(manage_messages=True)
async def custom_embed(
    interaction: discord.Interaction,
    title: str,
    description: str,
    color_hex: str = "3498db",
    image_url: str = None,
    thumbnail_url: str = None,
):
  try:
    color_int = int(color_hex.replace("#", ""), 16)
  except ValueError:
    color_int = 0x3498DB

  embed = discord.Embed(
      title=title, description=description, color=discord.Color(color_int)
  )
  if image_url:
    embed.set_image(url=image_url)
  if thumbnail_url:
    embed.set_thumbnail(url=thumbnail_url)
  embed.set_footer(
      text=f"Sent by {interaction.user.name}",
      icon_url=interaction.user.display_avatar.url,
  )

  await interaction.channel.send(embed=embed)
  await interaction.response.send_message(
      "✅ Embed sent successfully!", ephemeral=True
  )


# /poll Command
@bot.tree.command(name="poll", description="Create a simple yes/no or custom poll")
async def create_poll(interaction: discord.Interaction, question: str):
  embed = discord.Embed(
      title="📊 Community Poll",
      description=f"**{question}**",
      color=discord.Color.gold(),
  )
  embed.set_footer(text=f"Poll created by {interaction.user.name}")

  message = await interaction.channel.send(embed=embed)
  await message.add_reaction("👍")
  await message.add_reaction("👎")
  await interaction.response.send_message("✅ Poll published!", ephemeral=True)


# /ticket-setup Command
@bot.tree.command(name="ticket-setup", description="Deploy the Ticket Panel")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(interaction: discord.Interaction):
  embed = discord.Embed(
      title="🎫 Raze Town Support & Tickets",
      description=(
          "Agar aapko koi query, report ya issue hai, toh niche diye gaye"
          " **📩 Create Ticket** button par click karke ticket open karein."
      ),
      color=discord.Color.blue(),
  )
  embed.set_thumbnail(
      url=interaction.guild.icon.url if interaction.guild.icon else None
  )
  await interaction.channel.send(embed=embed, view=TicketCreateView())
  await interaction.response.send_message(
      "✅ Ticket panel successfully deployed!", ephemeral=True
  )


# /setup-counters Command
@bot.tree.command(
    name="setup-counters", description="Link Voice Channel for Member Count"
)
@app_commands.checks.has_permissions(administrator=True)
async def setup_counters(
    interaction: discord.Interaction, voice_channel_id: str
):
  global MEMBER_COUNT_CHANNEL_ID
  try:
    MEMBER_COUNT_CHANNEL_ID = int(voice_channel_id)
    await interaction.response.send_message(
        f"✅ Member counter channel set to `<#{MEMBER_COUNT_CHANNEL_ID}>`!",
        ephemeral=True,
    )
  except ValueError:
    await interaction.response.send_message(
        "❌ Please provide a valid Voice Channel ID.", ephemeral=True
    )


# ==========================================
# 7. BOT RUNNER
# ==========================================
TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN:
  bot.run(TOKEN)
else:
  print("Error: DISCORD_TOKEN environment variable not set.")

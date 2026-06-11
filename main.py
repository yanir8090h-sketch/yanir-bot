import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime

STAFF_ROLE_ID = 1493335218004820180
ADMIN_ROLE_ID = 1485440480459227227

ROLE_LEVEL_1_ID = 1484226514051665930
ROLE_LEVEL_2_ID = 1491063689502003360
ROLE_LEVEL_3_ID = 1490894966262726687
ROLE_LEVEL_4_ID = 1490894817373196388

XP_FILE = "xp_data.json"

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_xp(user_id, amount):
    data = load_xp()
    user_key = str(user_id)

    if user_key not in data:
        data[user_key] = {"xp": 0, "level": 1}

    data[user_key]["xp"] += amount

    expected_level = (data[user_key]["xp"] // 150) + 1
    if expected_level > data[user_key]["level"]:
        data[user_key]["level"] = expected_level

    save_xp(data)
    return False, data[user_key]["level"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= פקודה שהוספתי לך =================

@bot.command()
async def test(ctx):
    await ctx.send("✅ הבוט עובד ומגיב לפקודות!")

# ================= HELP =================

class HelpClaimView(discord.ui.View):
    def __init__(self, user_id=None):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.blurple)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        if staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ אין הרשאה", ephemeral=True)

        await interaction.response.defer()

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.orange()

        embed.add_field(
            name="Claimed",
            value=interaction.user.mention,
            inline=False
        )

        for c in self.children:
            c.disabled = True

        await interaction.message.edit(embed=embed, view=self)

        await interaction.followup.send("✔ נלקח לטיפול")

# ================= START =================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)  # 🔥 חובה כדי שפקודות יעבדו

bot.run("TOKEN")

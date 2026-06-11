import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime

# --- הגדרות קבועות ---
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
    leveled_up = False

    if expected_level > data[user_key]["level"]:
        data[user_key]["level"] = expected_level
        leveled_up = True

    save_xp(data)
    return leveled_up, data[user_key]["level"]

# --- BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= XP SHOP =================

class BuyRoleModal(discord.ui.Modal, title="🛒 רכישת רול"):
    role_num = discord.ui.TextInput(label="מספר רול (1-4)")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        data = load_xp()
        user_key = str(interaction.user.id)
        user_xp = data.get(user_key, {}).get("xp", 0)

        shop = {
            "1": (10000, ROLE_LEVEL_1_ID),
            "2": (12000, ROLE_LEVEL_2_ID),
            "3": (15000, ROLE_LEVEL_3_ID),
            "4": (20000, ROLE_LEVEL_4_ID),
        }

        choice = self.role_num.value.strip()

        if choice not in shop:
            return await interaction.followup.send("❌ בחירה לא תקינה", ephemeral=True)

        cost, role_id = shop[choice]

        if user_xp < cost:
            return await interaction.followup.send("❌ אין מספיק XP", ephemeral=True)

        role = interaction.guild.get_role(role_id)

        if not role:
            return await interaction.followup.send("❌ רול לא נמצא", ephemeral=True)

        data[user_key]["xp"] -= cost
        save_xp(data)

        await interaction.user.add_roles(role)

        await interaction.followup.send(f"✅ קנית את {role.name}")

class XpShopNewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy Role", style=discord.ButtonStyle.green)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BuyRoleModal())

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

# ================= STAFF FRIEND =================

class StaffFriendView(discord.ui.View):
    def __init__(self, staff_id=None, target_id=None):
        super().__init__(timeout=None)
        self.staff_id = staff_id
        self.target_id = target_id

    @discord.ui.button(label="אשר", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):

        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)

        if admin_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ אין הרשאה", ephemeral=True)

        await interaction.response.defer()

        target = interaction.guild.get_member(self.target_id)
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        if target and staff_role:
            await target.add_roles(staff_role)

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()

        for c in self.children:
            c.disabled = True

        await interaction.message.edit(embed=embed, view=self)

        await interaction.followup.send("✅ אושר")

    @discord.ui.button(label="דחה", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):

        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)

        if admin_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ אין הרשאה", ephemeral=True)

        await interaction.response.defer()

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()

        for c in self.children:
            c.disabled = True

        await interaction.message.edit(embed=embed, view=self)

        await interaction.followup.send("❌ נדחה")

# ================= EVENTS =================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    leveled_up, level = add_xp(message.author.id, random.randint(5, 15))

    if leveled_up:
        await message.channel.send(f"🎉 {message.author.mention} עלה לרמה {level}")

    await bot.process_commands(message)

# ================= COMMAND EXAMPLE =================

@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="XP Shop")
    await ctx.send(embed=embed, view=XpShopNewView())

# ================= RUN =================

bot.run("TOKEN")
bot.run(os.environ.get("DISCORD_TOKEN"))

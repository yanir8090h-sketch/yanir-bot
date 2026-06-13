import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio
import os

# ==========================================
# הגדרות בסיסיות של הבוט והרשאות
# ==========================================
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# הגדרות ה-ID של הרולים והמחירים שלך
# ==========================================
ROLE_1_ID = 1484226514051665930  # רול 1 - 30,000
ROLE_2_ID = 1491063689502003360  # רול 2 - 20,000
ROLE_3_ID = 1490894966262726687  # שלישי - 10,000
ROLE_4_ID = 1490894895618195577  # רביעי - 5,000
ROLE_5_ID = 1490894817373196388  # חמישי - 2,500

STAFF_ROLE_ID = 1490894966262726687  # ID של תפקיד הצוות לניהול טיקטים
STAFF_FRIENDS_LOG_CHANNEL_ID = 123456789012345678  # ערוץ לוגים לבקשות סטאף פרנד

# ==========================================
# 1. מערכת חנות ה-XP (תפריט נפתח)
# ==========================================
class ShopDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="רול ראשון 🥇", description="מחיר: 30,000 XP", value=str(ROLE_1_ID)),
            discord.SelectOption(label="רול שני 🥈", description="מחיר: 20,000 XP", value=str(ROLE_2_ID)),
            discord.SelectOption(label="רול שלישי 🥉", description="מחיר: 10,000 XP", value=str(ROLE_3_ID)),
            discord.SelectOption(label="רול רביעי 🎖️", description="מחיר: 5,000 XP", value=str(ROLE_4_ID)),
            discord.SelectOption(label="רול חמישי 🏅", description="מחיר: 2,500 XP", value=str(ROLE_5_ID)),
        ]
        super().__init__(placeholder="בחר תפקיד לקנייה מהחנות...", min_values=1, max_values=1, options=options, custom_id="shop_select_persistent")

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values)
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(role_id)

        if not role:
            await interaction.response.send_message("❌ שגיאה: התפקיד הזה לא נמצא בשרת!", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message(f"❌ אתה כבר מחזיק בתפקיד {role.mention}!", ephemeral=True)
            return

        await member.add_roles(role)
        await interaction.response.send_message(f"🎉 תתחדש! רכשת בהצלחה את התפקיד {role.mention}!", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

# ==========================================
# 2. מערכת הטיקטים (פתיחה, לקיחה וסגירה)
# ==========================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לקיחת טיקט 🔒", style=discord.ButtonStyle.green, custom_id="claim_ticket_persistent")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        global STAFF_ROLE_ID
        if STAFF_ROLE_ID:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff_role not in interaction.user.roles:
                await interaction.response.send_message("❌ שגיאה: רק אנשי צוות יכולים לקחת טיקט זה!", ephemeral=True)
                return
        await interaction.channel.edit(name=f"claimed-{interaction.user.name}")
        await interaction.response.send_message(f"🔒 הטיקט נלקח לטיפול על ידי {interaction.user.mention}!", ephemeral=False)

    @discord.ui.button(label="סגירת טיקט ❌", style=discord.ButtonStyle.red, custom_id="close_ticket_persistent")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ הטיקט ייסגר ויימחק בעוד 5 שניות...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="פתח טיקט ✉️", style=discord.ButtonStyle.blurple, custom_id="open_ticket_persistent")
    async def open_button(interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(name=f"ticket-{member.name}", overwrites=overwrites)
        ticket_embed = discord.Embed(
            title="🎫 טיקט חדש נפתח!",
            description=f"שלום {member.mention},\nצוות התמיכה עודכן ויענה לך בהקדם.\nבאפשרותך לנהל את הטיקט בעזרת הכפתורים למטה.",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=ticket_embed, view=TicketView())
        await interaction.response.send_message(f"הטיקט שלך נפתח בהצלחה! לחץ כאן: {ticket_channel.mention}", ephemeral=True)

# ==========================================
# 3. מערכת אימות (Verification) בכפתור
# ==========================================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="להתחלת אימות 🛡️", style=discord.ButtonStyle.green, custom_id="verify_user_persistent")
    async def verify_button(interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        verified_role = discord.utils.get(guild.roles, name="Verified")
        if not verified_role:
            verified_role = await guild.create_role(name="Verified")

        if verified_role in member.roles:
            await interaction.response.send_message("❌ אתה כבר מאומת בשרת!", ephemeral=True)
        else:
            await member.add_roles(verified_role)
            await interaction.response.send_message("✅ האימות בוצע בהצלחה! כעת נפתחו עבורך הערוצים.", ephemeral=True)

# ==========================================
# 4. מערכת בקשות Staff Friend (עם אישור/דחייה)
# ==========================================
class StaffFriendReview(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Accept  ✔️", style=discord.ButtonStyle.success, custom_id="staff_friend_accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        staff_friend_role = discord.utils.get(guild.roles, name="Staff Friend")
        if not staff_friend_role:
            staff_friend_role = await guild.create_role(name="Staff Friend")

        if member:
            await member.add_roles(staff_friend_role)
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.green()
            embed.set_field_at(2, name="🟢 סטטוס:", value=f"אושר על ידי {interaction.user.mention}", inline=False)
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message(f"✅ הבקשה אושרה והרול הוענק.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ המשתמש עזב את השרת.", ephemeral=True)

    @discord.ui.button(label="Deny  ❌", style=discord.ButtonStyle.danger, custom_id="staff_friend_deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.set_field_at(2, name="🔴 סטטוס:", value=f"נדחה על ידי {interaction.user.mention}", inline=False)
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("❌ הבקשה נדחתה.", ephemeral=True)

# ==========================================
# 5. פקודות הניהול להצבת ההודעות (Commands)
# ==========================================
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    embed = discord.Embed(title="🎫 פתיחת טיקט תמיכה", description="צריך עזרה או יש לך שאלה לצוות המנהלים?\nלחץ על הכפתור למטה כדי לפתוח טיקט פרטי!", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketOpenView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_shop(ctx):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    guild = ctx.guild
    embed = discord.Embed(
        title=f"🎁 חנות ה-XP הרשמית - {guild.name}",
        description=f"🛍️ **חנות הרולים של השרת**\n\n"
                    f"👑 <@&{ROLE_1_ID}> — 30,000 XP\n"
                    f"💎 <@&{ROLE_2_ID}> — 20,000 XP\n"
                    f"🔥 <@&{ROLE_3_ID}> — 10,000 XP\n"
                    f"⚡ <@&{ROLE_4_ID}> — 5,000 XP\n"
                    f"✨ <@&{ROLE_5_ID}> — 2,500 XP",
        color=discord.Color.from_rgb(142, 201, 57)
    )
    if guild.icon:
        embed.set_image(url=guild.icon.url)
    await ctx.send(embed=embed, view=ShopView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_verify(ctx):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    embed = discord.Embed(title="🔒 אימות חשבון - Verification", description="ברוך הבא לשרת!\nכדי לקבל גישה לשאר הערוצים, לחץ על הכפתור הירוק למטה.", color=discord.Color.green())
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=VerifyView())

@bot.command()
async def apply_staff_friend(ctx):
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_verify(ctx):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    embed = discord.Embed(title="🔒 אימות חשבון - Verification", description="ברוך הבא לשרת!\nכדי לקבל גישה לשאר הערוצים, לחץ על הכפתור הירוק למטה.", color=discord.Color.green())
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=VerifyView())

@bot.command()
async def apply_staff_friend(ctx):
    log_channel = bot.get_channel(STAFF_FRIENDS_LOG_CHANNEL_ID)
    if not log_channel:
        await ctx.send("❌ ערוץ הלוגים לא הוגדר.", ephemeral=True)
        return
    embed = discord.Embed(title="🛠️ בקשת Staff Friend חדשה", color=discord.Color.purple())
    embed.add_field(name="👤 מגיש הבקשה:", value=ctx.author.mention, inline=True)
    embed.add_field(name="🕒 זמן:", value=discord.utils.format_dt(ctx.message.created_at), inline=True)
    embed.add_field(name="🟡 סטטוס:", value="ממתין לטיפול...", inline=False)
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
    await log_channel.send(embed=embed, view=StaffFriendReview(ctx.author.id))
    await ctx.send("✅ בקשתך נשלחה לצוות הניהול!", ephemeral=True)

@bot.command(name="h")
async def help_ticket_info(ctx, *, reason: str = "לא צוינה סיבה"):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    guild = ctx.guild
    embed = discord.Embed(title="⚠️ בקשת עזרה", color=discord.Color.from_rgb(47, 49, 54))
    embed.add_field(name="👥 צוות מתוייג:", value=f"<@&{STAFF_ROLE_ID}>", inline=False)
    embed.add_field(name="📝 סיבה:", value=reason, inline=False)
    embed.add_field(name="🌐 וייס:", value="🔈 (🔒) Private", inline=False)
    embed.add_field(name="🔒 נלקח על ידי:", value=f"@{ctx.author.name} · <@&{ROLE_3_ID}>", inline=False)
    if guild.icon:
        embed.set_image(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    bot.add_view(ShopView())
    bot.add_view(TicketView())
    bot.add_view(TicketOpenView())
    bot.add_view(VerifyView())
    print(f'🤖 הבוט מחובר בהצלחה כאל: {bot.user.name}')

app = Flask('')

@app.route('/')
def home():
    return "הבוט דלוק ובאוויר!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

import os
bot.run(os.getenv("DISCORD_TOKEN"))

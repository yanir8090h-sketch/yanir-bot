import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio
import os

# הגדרת ה-Intents והרשאות הבוט
intents = discord.Intents.all()
intents.message_content = True # השורה שמאפשרת לקרוא את ה-! בכל ערוץ

bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================================
# הגדרות ומשתנים קבועים (הרולים והמחירים שלך)
# ==========================================
ROLE_1_ID = 1484226514051665930  # רול 1 - 30,000
ROLE_2_ID = 1491063689502003360  # רול 2 - 20,000
ROLE_3_ID = 1490894966262726687  # שלישי - 10,000
ROLE_4_ID = 1490894895618195577  # רביעי - 5,000
ROLE_5_ID = 1490894817373196388  # חמישי - 2,500

STAFF_ROLE_ID = 1490894966262726687  # ID של תפקיד הצוות לניהול הטיקטים
STAFF_FRIENDS_LOG_CHANNEL_ID = 123456789012345678  # ערוץ לוגים לבקשות סטאף פרנד

# דיקשנרי פנימי לשמירת ה-XP של המשתמשים (במקום דאטהבייס מורכב)
user_xp_data = {}

# ==========================================
# מערכת ה-XP האוטומטית (נקודות על הודעות)
# ==========================================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    if user_id not in user_xp_data:
        user_xp_data[user_id] = {"xp": 0, "level": 1}

    # הוספת 15 נקודות XP על כל הודעה בצ'אט
    user_xp_data[user_id]["xp"] += 15
    
    # חישוב עליית רמה (כל 1000 XP עולים רמה)
    current_xp = user_xp_data[user_id]["xp"]
    current_lvl = user_xp_data[user_id]["level"]
    next_lvl_xp = current_lvl * 1000

    if current_xp >= next_lvl_xp:
        user_xp_data[user_id]["level"] += 1
        await message.channel.send(f"🎉 כל הכבוד {message.author.mention}! עלית לרמה **{current_lvl + 1}**!")

    # פקודה קריטית המאפשרת לשאר הפקודות בבוט לעבוד במקביל!
    await bot.process_commands(message)

@bot.command()
async def xp(ctx, member: discord.Member = None):
    """פקודה לבדיקת ה-XP הנוכחי של המשתמש"""
    if member is None:
        member = ctx.author

    user_id = member.id
    xp_amount = user_xp_data.get(user_id, {"xp": 0})["xp"]
    lvl_amount = user_xp_data.get(user_id, {"level": 1})["level"]

    embed = discord.Embed(title=f"📊 סטטיסטיקת ה-XP של {member.name}", color=discord.Color.blue())
    embed.add_field(name="⭐ רמה נוכחית:", value=str(lvl_amount), inline=True)
    embed.add_field(name="✨ נקודות XP:", value=f"{xp_amount} / {lvl_amount * 1000}", inline=True)
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)

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
        super().__init__(placeholder="בחר תפקיד לקנייה מהחנות...", min_values=1, max_values=1, options=options, custom_id="shop_select_p")

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values)
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(role_id)

        # מילון מחירים לבדיקה
        prices = {
            ROLE_1_ID: 30000, ROLE_2_ID: 20000, ROLE_3_ID: 10000, ROLE_4_ID: 5000, ROLE_5_ID: 2500
        }
        price = prices.get(role_id, 0)
        user_xp = user_xp_data.get(member.id, {"xp": 0})["xp"]

        if not role:
            await interaction.response.send_message("❌ שגיאה: התפקיד לא נמצא בשרת!", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message("❌ אתה כבר מחזיק בתפקיד הזה!", ephemeral=True)
            return
        if user_xp < price:
            await interaction.response.send_message(f"❌ אין לך מספיק נקודות! חסר לך {price - user_xp} XP.", ephemeral=True)
            return

        # הורדת ה-XP ומתן הרול בפועל
        user_xp_data[member.id]["xp"] -= price
        await member.add_roles(role)
        await interaction.response.send_message(f"🎉 תתחדש! קנית את התפקיד {role.mention} ונשארת עם {user_xp - price} XP!", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

# ==========================================
# 2. מערכת הטיקטים (ניהול פנימי ופתיחה)
# ==========================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לקיחת טיקט 🔒", style=discord.ButtonStyle.green, custom_id="claim_t_p")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if STAFF_ROLE_ID:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff_role not in interaction.user.roles:
                await interaction.response.send_message("❌ רק אנשי צוות יכולים לקחת טיקט זה!", ephemeral=True)
                return
        await interaction.channel.edit(name=f"claimed-{interaction.user.name}")
        await interaction.response.send_message(f"🔒 הטיקט נלקח לטיפול על ידי {interaction.user.mention}!", ephemeral=False)

    @discord.ui.button(label="סגירת טיקט ❌", style=discord.ButtonStyle.red, custom_id="close_t_p")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ הערוץ יימחק בעוד 5 שניות...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="פתח טיקט ✉️", style=discord.ButtonStyle.blurple, custom_id="open_t_p")
    async def open_button(interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(name=f"ticket-{member.name}", overwrites=overwrites)
        embed = discord.Embed(title="🎫 טיקט חדש נפתח!", description=f"שלום {member.mention},\nצוות התמיכה יענה לך בהקדם.\nבאפשרותך לנהל את הטיקט בכפתורים למטה.", color=discord.Color.green())
        await ticket_channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message(f"הטיקט שלך נפתח בהצלחה: {ticket_channel.mention}", ephemeral=True)

# ==========================================
# 3. מערכת אימות (Verification) בכפתור
# ==========================================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="להתחלת אימות 🛡️", style=discord.ButtonStyle.green, custom_id="verify_u_p")
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
            await interaction.response.send_message("✅ האימות בוצע בהצלחה!", ephemeral=True)

# ==========================================
# 4. מערכת בקשות Staff Friend
# ==========================================
class StaffFriendReview(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Accept  ✔️", style=discord.ButtonStyle.success, custom_id="sf_accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        role = discord.utils.get(guild.roles, name="Staff Friend")
        if not role: role = await guild.create_role(name="Staff Friend")
        if member:
            await member.add_roles(role)
            await interaction.response.send_message("✅ הבקשה אושרה והרול הוענק.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ המשתמש עזב.", ephemeral=True)

    @discord.ui.button(label="Deny  ❌", style=discord.ButtonStyle.danger, custom_id="sf_deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ הבקשה נדחתה.", ephemeral=True)

# ==========================================
# פקודות סטאפ להרצה בדיסקורד
# ==========================================
# ==========================================
# פקודת העזרה המעוצבת המוכרת (!h) עם סיבה דינמית
# ==========================================
@bot.command(name="h")
async def help_ticket_info(ctx, *, reason: str = "לא צוינה סיבה"):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass

    guild = ctx.guild
    embed = discord.Embed(title="⚠️ בקשת עזרה", color=discord.Color.from_rgb(47, 49, 54))
    
    # הצגת הנתונים והרולים בדיוק כמו בתמונה ששלחת
    embed.add_field(name="👥 צוות מתוייג:", value=f"<@&{STAFF_ROLE_ID}>", inline=False)
    embed.add_field(name="📝 סיבה:", value=reason, inline=False)
    embed.add_field(name="🌐 וייס:", value="🔈 (🔒) Private", inline=False)
    embed.add_field(name="🔒 נלקח על ידי:", value=f"@{ctx.author.name} · <@&{ROLE_3_ID}>", inline=False)

    if guild.icon:
        embed.set_image(url=guild.icon.url)
    
    await ctx.send(embed=embed)

# ==========================================
# פקודת חנות ה-XP המעוצבת
# ==========================================
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

# ==========================================
# קוד Flask לשמירה על הבוט דלוק בחינם ב-Render
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "הבוט דלוק ובאוויר!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# הפעלת שרת האינטרנט
keep_alive()

# ==========================================
# שורות ההפעלה הסופיות של הבוט
# ==========================================
import os
bot.run(os.getenv("DISCORD_TOKEN"))

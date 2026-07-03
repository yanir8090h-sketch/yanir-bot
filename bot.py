import os, discord, asyncio, random, sqlite3
from threading import Thread
from flask import Flask
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
processed_message_ids = set()

# 🆔 מזהי רולים כלליים של השרת שלך:
STAFF_ROLE_ID = 1521955150334263437     
STAFF_ROLE_NAMES = (1521955150309359747)
MNG_ROLE =   1521955150309359747
MEMBER_ROLE = 1521955150246445184       
VETERAN_ROLE_ID = 1521955150246445184  

# 🆔 מזהי ארבעת הרולים החדשים של החנות:
ROLE_MNG_SUPPORT = 1520802461306271825    # Manager Support
ROLE_EV_MNG = 1520807998505312431         # Event Manager
ROLE_SUP_TEAM = 1520870990535312431       # Support Team
ROLE_LEAK_TEAM = 1520870990505312430      # Leaks Team
STAFF_FRIEND_ROLE_ID = 1521955150275809377  # Staff Friend
STAFF_REQUEST_CHANNEL_ID = 1522010120089895032  # אם תרצה, שנה ל-ID של חדר staff-request
GUILD_ID = int(os.getenv("GUILD_ID", "0")) or None
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "0")) or None
ROLE_PREFIX = "קזינו - "
CASINO_START_BALANCE = 10000
SPECIAL_CASINO_ROLE_ID = 1521955150246445179
CASINO_ROLE_SHOP = {
    "mng_support": ("דילר/ית תמיכה", 25000, ROLE_MNG_SUPPORT),
    "evt_mng": ("מנהל/ת קופה", 20000, ROLE_EV_MNG),
    "sup_team": ("צוות VIP", 15000, ROLE_SUP_TEAM),
    "leak_team": ("צייד/ת בונוסים", 10000, ROLE_LEAK_TEAM),
    "special": ("רול קזינו מיוחד", 18000, SPECIAL_CASINO_ROLE_ID),
}
TOKEN = os.getenv("TOKEN")

# 🔄 חיבור לבסיס הנתונים הסופי והנקי:
conn = sqlite3.connect("xp_server_final.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0)")
conn.commit()

def get_xp(uid):
    cursor.execute("SELECT xp FROM users WHERE user_id = ?", (uid,))
    r = cursor.fetchone()
    return r[0] if r else 0

def add_xp(uid, amt):
    nxp = max(0, get_xp(uid) + amt)
    cursor.execute("INSERT INTO users (user_id, xp) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET xp = ?", (uid, nxp, nxp))
    conn.commit()
    return nxp

def ensure_casino_balance(uid):
    xp = get_xp(uid)
    if xp < CASINO_START_BALANCE:
        add_xp(uid, CASINO_START_BALANCE - xp)
        return CASINO_START_BALANCE
    return xp

def find_role(guild, role_identifier):
    if isinstance(role_identifier, int):
        return guild.get_role(role_identifier)
    if isinstance(role_identifier, str):
        if role_identifier.isdigit():
            return guild.get_role(int(role_identifier))
        role = discord.utils.get(guild.roles, name=role_identifier)
        if role:
            return role
        return discord.utils.get(guild.roles, name=f"{ROLE_PREFIX}{role_identifier}")
    return None

class HelpView(discord.ui.View):
    def __init__(self, req, reason, vc): super().__init__(timeout=None); self.req = req; self.reason = reason; self.vc = vc
    @discord.ui.button(label="לקיחת הלפ", style=discord.ButtonStyle.success, custom_id="c_h", emoji="👋")
    async def claim(self, inter, btn):
        btn.label = "בטיפול"; btn.disabled = True; await inter.response.edit_message(view=self)
        await inter.channel.send(f"🚀 {inter.user.mention} לקח את הטיפול בקריאה של {self.req.mention}!")

class MngButtons(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="טפל כאן", style=discord.ButtonStyle.success, custom_id="t_c", emoji="✋")

# כפתורי הניהול בתוך הטיקט שנפתח - גרסה מתוקנת
class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 סגור טיקט", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "ticket-" in interaction.channel.name:
            await interaction.response.send_message("הטיקט ייסגר בעוד 5 שניות...", ephemeral=False)
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("❌ ניתן להשתמש בכפתור זה רק בתוך ערוץ טיקט!", ephemeral=True)

    @discord.ui.button(label="🛠️ טפל כאן", style=discord.ButtonStyle.success, custom_id="claim_ticket")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label = f"בטיפול של: {interaction.user.display_name}"
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"הצוות {interaction.user.mention} לקח את הטיקט לטיפולו! 👨‍💻", ephemeral=False)


# כפתור פתיחת הטיקט הראשי - גרסה מתוקנת
class CreateTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 פתח טיקט תמיכה", style=discord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}", 
            overwrites=overwrites,
            topic=f"טיקט תמיכה עבור {user.display_name}"
        )
        
        await interaction.response.send_message(f"✅ הטיקט שלך נפתח בהצלחה! לחץ כאן: {channel.mention}", ephemeral=True)
        
        ticket_embed = discord.Embed(
            title="🎯 פנייה חדשה למחלקת התמיכה",
            description=(
                f"שלום {user.mention},\n\n"
                "צוות הניהול קיבל את פנייתך ויגיע לעזור בהקדם האפשרי.\n"
                "בזמן הזה, נשמח אם תפרט כאן את סיבת הפנייה שלך.\n\n"
                "**לשימוש הצוות:** לחץ על הכפתורים למטה כדי לנהל את הפנייה."
            ),
            color=discord.Color.orange()
        )
        if guild.icon:
            ticket_embed.set_thumbnail(url=guild.icon.url)
        
        await channel.send(content=f"{user.mention} | @everyone", embed=ticket_embed, view=TicketControls())




import discord
from discord.ext import commands
import json
import os

# הגדרת הבוט עם כל ההרשאות (Intents) הדרושות
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# יצירת קובץ ה-XP אוטומטית אם הוא לא קיים
if not os.path.exists("levels.json"):
    with open("levels.json", "w") as f:
        json.dump({}, f)

# פונקציות לקריאה וכתיבה של ה-XP מהקובץ
def load_xp():
    with open("levels.json", "r") as f:
        return json.load(f)

def save_xp(data):
    with open("levels.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------------------------------------------------------
# 1. מערכת עדכון הסטטוס (נא לא להפריע + ספירת ממברס בזמן אמת)
# ------------------------------------------------------------------

async def update_bot_status():
    member_count = sum(guild.member_count for guild in bot.guilds)
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name=f"{member_count} members"
    )
    await bot.change_presence(status=discord.Status.dnd, activity=activity)

@bot.event
async def on_ready():
    print(f'הבוט {bot.user.name} עלה לאוויר בהצלחה!')
    await update_bot_status()

@bot.event
async def on_member_join(member):
    await update_bot_status()

@bot.event
async def on_member_remove(member):
    await update_bot_status()

# ------------------------------------------------------------------
# 2. מערכת הוספת XP אוטומטית על כל הודעה בצ'אט
# ------------------------------------------------------------------

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    users_data = load_xp()
    user_id = str(message.author.id)

    if user_id not in users_data:
        users_data[user_id] = 0

    users_data[user_id] += 15
    save_xp(users_data)

    await bot.process_commands(message)

# ------------------------------------------------------------------
# 3. תפריט הבחירה והלוגיקה של חנות ה-XP
# ------------------------------------------------------------------

class ShopDropdown(discord.ui.Select):
    def __init__(self):
        # הגדרת הרולים ומחיריהם מהשרת שלך
        self.role_prices = {
            1522553430034616351: 5000,   # רול 1
            1522553732984733867: 10000,  # רול 2
            1522553933833441330: 20000,  # רול 3
            1522554104063201301: 35000,  # רול 4
            1522554362965000283: 50000,  # רול 5
        }

        options = [
            discord.SelectOption(label="רול 1", value="1522553430034616351", description="מחיר: 5,000 XP", emoji="👑"),
            discord.SelectOption(label="רול 2", value="1522553732984733867", description="מחיר: 10,000 XP", emoji="🌟"),
            discord.SelectOption(label="רול 3", value="1522553933833441330", description="מחיר: 20,000 XP", emoji="💎"),
            discord.SelectOption(label="רול 4", value="1522554104063201301", description="מחיר: 35,000 XP", emoji="🌀"),
            discord.SelectOption(label="רול 5", value="1522554362965000283", description="מחיר: 50,000 XP", emoji="🟢"),
        ]
        super().__init__(placeholder="בחר רול לקנייה...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_role_id = int(self.values[0])
        price = self.role_prices.get(selected_role_id)
        user = interaction.user
        guild = interaction.guild
        
        role = guild.get_role(selected_role_id)
        if not role:
            return await interaction.response.send_message("❌ שגיאה: הרול המבוקש לא נמצא בשרת.", ephemeral=True)
            
        if role in user.roles:
            return await interaction.response.send_message("❌ כבר יש לך את הרול הזה!", ephemeral=True)

        users_data = load_xp()
        user_id = str(user.id)
        user_xp = users_data.get(user_id, 0)

        if user_xp < price:
            missing_xp = price - user_xp
            return await interaction.response.send_message(f"❌ אין לך מספיק XP לרול הזה! יש לך {user_xp:,} XP וחסר לך עוד {missing_xp:,} XP.", ephemeral=True)

        try:
            users_data[user_id] -= price
            save_xp(users_data)
            await user.add_roles(role)
            await interaction.response.send_message(f"✅ קנית את הרול {role.mention} בהצלחה! הורדו מחשבונך {price:,} XP וכעת נשארו לך {users_data[user_id]:,} XP.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ לבוט אין הרשאות מתאימות (Manage Roles) כדי לתת לך את הרול הזה.", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

# ------------------------------------------------------------------
# 4. פקודות הדיסקורד (!shop ו- !xp)
# ------------------------------------------------------------------

@bot.command()
async def shop(ctx):
    shop_text = (
        "👑 **רול 1** ➔ מחיר: 5,000 XP\n"
        "🌟 **רול 2** ➔ מחיר: 10,000 XP\n"
        "💎 **רול 3** ➔ מחיר: 20,000 XP\n"
        "🌀 **רול 4** ➔ מחיר: 35,000 XP\n"
        "🟢 **רול 5** ➔ מחיר: 50,000 XP\n\n"
        "*Developed By: Main Bot -- Soon.*"
    )

    embed1 = discord.Embed(title="👑 NextZone XP Shop", description=shop_text, color=discord.Color.blue())
    if ctx.guild.icon:
        embed1.set_thumbnail(url=ctx.guild.icon.url)

    embed2 = discord.Embed(title="בחר רול לקנייה", color=discord.Color.blue())
    await ctx.send(embeds=[embed1, embed2], view=ShopView())

@bot.command(aliases=["level"])
async def xp(ctx, member: discord.Member = None):
    member = member or ctx.author
    users_data = load_xp()
    user_id = str(member.id)
    user_xp = users_data.get(user_id, 0)
    
    embed = discord.Embed(
        title="📊 מצב ה-XP שלך",
        description=f"היי {member.mention},\nכרגע יש לך בדיוק **{user_xp:,} XP** בחשבון!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# ------------------------------------------------------------------
# 5. הרצת הבוט (משיכת הטוקן מ-Railway)
# ------------------------------------------------------------------
# הרצה נקייה של הבוט ללא משתנה הסטטוס שגורם לקריסה
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)






class VeteranView(discord.ui.View):
    def __init__(self, days): super().__init__(timeout=None); self.days = days
    @discord.ui.button(label="🎖️ בקש לקבל רול ווטרן", style=discord.ButtonStyle.success, custom_id="claim_veteran")
    async def claim_vet(self, inter, button):
        r = inter.guild.get_role(VETERAN_ROLE_ID)
        if self.days >= 90: await inter.user.add_roles(r); await inter.response.send_message("🎉 מזל טוב! קיבלת את רול הווטרן! 🎖️", ephemeral=True)
        else: await inter.response.send_message(f"❌ חסרים לך עוד {90 - self.days} ימים.", ephemeral=True)

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ לחץ כאן לאימות", style=discord.ButtonStyle.success, custom_id="v_c")
    async def verify(self, inter, btn):
        r = inter.guild.get_role(MEMBER_ROLE)
        if not r:
            await inter.response.send_message("❌ רול האימות לא נמצא. בקש מהמנהל לבדוק את ההגדרות.", ephemeral=True)
            return
        if r in inter.user.roles:
            await inter.response.send_message("✅ כבר אימתנו אותך. תודה!", ephemeral=True)
            return
        await inter.user.add_roles(r)
        await inter.response.send_message("🎉 אימות בוצע בהצלחה!", ephemeral=True)

class StaffFriendApproveView(discord.ui.View):
    def __init__(self, target, requester, role):
        super().__init__(timeout=None)
        self.target = target
        self.requester = requester
        self.role = role

    @discord.ui.button(label="אשר", style=discord.ButtonStyle.success, custom_id="sf_approve")
    async def approve(self, interaction, button):
        if self.role and self.role not in self.target.roles:
            await self.target.add_roles(self.role)
            await interaction.response.edit_message(
                content=f"✅ בקשת Staff Friend אושרה עבור {self.target.mention} על ידי {interaction.user.mention}.",
                view=None,
            )
            try:
                await self.requester.send(f"✅ בקשתך אושרה! קיבלת את הרול {self.role.name}.")
            except Exception:
                pass
        else:
            await interaction.response.edit_message(
                content=f"⚠️ {self.target.mention} כבר מחזיק ברול זה או שהרול לא קיים.",
                view=None,
            )

    @discord.ui.button(label="דחה", style=discord.ButtonStyle.danger, custom_id="sf_reject")
    async def reject(self, interaction, button):
        await interaction.response.edit_message(
            content=f"❌ בקשת Staff Friend נדחתה עבור {self.target.mention} על ידי {interaction.user.mention}.",
            view=None,
        )
        try:
            await self.requester.send("❌ בקשתך נדחתה.")
        except Exception:
            pass

async def update_member_presence():
    member_count = 0
    if GUILD_ID:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            member_count = guild.member_count
    if member_count == 0:
        member_count = sum(g.member_count for g in bot.guilds)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"{member_count} חברים"))

def get_welcome_channel(guild: discord.Guild) -> discord.TextChannel | None:
    if WELCOME_CHANNEL_ID:
        channel = guild.get_channel(WELCOME_CHANNEL_ID)
        if channel and channel.permissions_for(guild.me).send_messages and channel.permissions_for(guild.me).view_channel:
            return channel
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages and guild.system_channel.permissions_for(guild.me).view_channel:
        return guild.system_channel
    return next(
        (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages and c.permissions_for(guild.me).view_channel),
        None,
    )

@bot.event
async def on_ready():
    bot.add_view(TicketView()); bot.add_view(VerifyView()); bot.add_view(ShopView()); bot.add_view(CasinoView()); bot.add_view(MngButtons())
    await update_member_presence()
    try:
        if GUILD_ID:
            synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        else:
            synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Slash command sync failed: {e}")
    print("Your Bot is officially live, logging and ready! 🚀")

@bot.event
async def on_member_join(member):
    await update_member_presence()

    # אין הודעת ברוכים הבאים עם אמבד עבור משתמשים חדשים.

@bot.event
async def on_member_remove(member):
    await update_member_presence()

@bot.hybrid_command(name="ping", description="בדוק אם הבוט חי")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

def build_veteran_embed(user):
    jd = user.joined_at
    days = (datetime.now(jd.tzinfo) - jd).days
    emb = discord.Embed(title=f"🕸️ סטטוס הוותק שלך בשרת | {user.name}", color=0x2f3136)
    emb.add_field(name="📅 מתי נכנסת לשרת?", value=f"```text\n{jd.strftime('%d/%m/%Y')}\n```", inline=False)
    emb.add_field(name="⏳ לפני כמה זמן זה היה?", value=f"```text\n{days} ימים\n```", inline=False)
    return emb, days

@bot.hybrid_command(name="vt", description="הצג את סטטוס הוותק שלך")
async def vt_command(ctx):
    user = getattr(ctx, "author", None) or ctx.user
    emb, days = build_veteran_embed(user)
    await ctx.send(embed=emb, view=VeteranView(days))

@bot.hybrid_command(name="sf", description="בקש רול Staff Friend")
async def sf_command(ctx, user: discord.Member = None):
    target = user or getattr(ctx, "author", None) or ctx.user
    role = ctx.guild.get_role(STAFF_FRIEND_ROLE_ID)
    if not role:
        await ctx.send("❌ לא נמצא רול Staff Friend בשרת.")
        return

    request_channel = ctx.channel
    if STAFF_REQUEST_CHANNEL_ID:
        request_channel = ctx.guild.get_channel(1521955150275809377)
        if not request_channel:
            request_channel = ctx.channel

    embed = discord.Embed(
        title="📩 בקשת Staff Friend",
        description=f"{target.mention} ביקש/ה את הרול {role.name}",
        color=0x00ff00,
    )
    embed.add_field(name="מבקש", value=getattr(ctx, "author", ctx.user).mention, inline=True)
    embed.add_field(name="מועמד", value=target.mention, inline=True)
    embed.set_footer(text="לחץ על אשר או דחה")

    await request_channel.send(embed=embed, view=StaffFriendApproveView(target, getattr(ctx, "author", ctx.user), role))
    await ctx.send("📨 הבקשה נשלחה לצוות לאישור.")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!", 200


def keep_alive():
    port = int(os.getenv("PORT", "8080"))
    thread = Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": port}, daemon=True)
    thread.start()


@bot.event
async def on_message(msg):
    if msg.author.bot or not msg.guild:
        return

    add_xp(msg.author.id, random.randint(15, 25))

    text = msg.content.strip()
    lower_text = text.lower()

    if lower_text == "!ping":
        await msg.channel.send("🏓 Pong!")
        return

    if lower_text.startswith("!xp"):
        target = msg.mentions[0] if msg.mentions else msg.author
        await msg.channel.send(f"✨ יתרת ה-XP של {target.mention} היא: **{get_xp(target.id):,} XP**")
        return

    if lower_text == "!vt":
        emb, days = build_veteran_embed(msg.author)
        await msg.channel.send(embed=emb, view=VeteranView(days))
        return

    if lower_text.startswith("!sf"):
        target = msg.mentions[0] if msg.mentions else msg.author
        role = msg.guild.get_role(STAFF_FRIEND_ROLE_ID)
        if not role:
            await msg.channel.send("❌ לא נמצא רול Staff Friend בשרת.")
            return

        embed = discord.Embed(
            title="📩 בקשת Staff Friend",
            description=f"{target.mention} ביקש/ה את הרול {role.name}",
            color=0x00ff00,
        )
        embed.add_field(name="מבקש", value=msg.author.mention, inline=True)
        embed.add_field(name="מועמד", value=target.mention, inline=True)
        embed.set_footer(text="לחץ על אשר או דחה")

        await msg.channel.send(embed=embed, view=StaffFriendApproveView(target, msg.author, role))
        await msg.channel.send("📨 הבקשה נשלחה לצוות לאישור.")
        return

    if lower_text == "!setup_verify":
        await msg.delete()
        await msg.channel.send("🔒 **Verification System** 🔒\n\nClick the button below to get verified:", view=VerifyView())
        return

    if lower_text == "!setup_tickets":
        await msg.delete()
        await msg.channel.send("📩 **Staff & Support Center** 📩\n\nבחר את סוג הפנייה שלך מתוך התפריט הנפתח למטה כדי לפתוח כרטיס אישי:", view=TicketView())
        return

    if lower_text == "!setup_shop":
        await msg.delete()
        await msg.channel.send("🛒 **XP Shop** 🛒\n\nפתח את התפריט למטה ובחר את הרול החדש שברצונך לרכוש באמצעות נקודות ה-XP שלך:", view=ShopView())
        return

   # ==================================================================
# מערכת קזינו מלאה, מעוצבת ומעודכנת - NextZone Casino
# ==================================================================

# ------------------------------------------------------------------
# פקודה למנהלים: שליחת תפריט המשחקים המרכזי עם תמונת השרת
# ------------------------------------------------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_casino(ctx):
    embed = discord.Embed(
        title="🎰 ברוכים הבאים לקזינו הרשמי - NextZone",
        description=(
            "כאן תוכלו להמר על ה-XP שלכם ולזכות בפרסים מטורפים לחנות הקזינו!\n\n"
            "🎮 **המשחקים הזמינים בקזינו:**\n"
            "• 🎰 **מכונת מזל:** `!slots [סכום]` או `!slots all`\n"
            "• 🛞 **רולטה:** `!roulette [סכום] [red/black/even/odd/מספר]`\n"
            "• 🃏 **בלאק ג'ק:** `!blackjack [סכום]` או `!bj [סכום]`\n\n"
            "💰 *רוצים לבדוק כמה כסף יש לכם? הקלידו:* `!xp`"
        ),
        color=discord.Color.gold()
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
        
    await ctx.send(embed=embed)
    await ctx.message.delete() # מוחק את ה-!setup_casino של המנהל

# ------------------------------------------------------------------
# 1. משחק מכונת מזל (!slots)
# ------------------------------------------------------------------
@bot.command(aliases=["slot", "gamble"])
async def slots(ctx, bet_amount: str = None):
    if bet_amount is None:
        embed_error = discord.Embed(
            title="🎰 קזינו NextZone - שגיאה",
            description="❌ נא לציין סכום הימור!\nדוגמה: `!slots 500`",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed_error)

    users_data = load_xp()
    user_id = str(ctx.author.id)
    user_xp = users_data.get(user_id, 0)

    if bet_amount.lower() == "all":
        bet_amount = user_xp
    else:
        try:
            bet_amount = int(bet_amount)
        except ValueError:
            return await ctx.send("❌ סכום ההימור חייב להיות מספר שלם או `all`!")

    if bet_amount <= 0 or user_xp < bet_amount:
        return await ctx.send(f"❌ הימור לא חוקי או שאין לך מספיק XP (ברשותך: **{user_xp:,} XP**)")

    emojis = ["🍒", "🍇", "🍊", "💎", "👑", "🍀"]
    slot1, slot2, slot3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)

    if slot1 == slot2 == slot3:
        win_amount = bet_amount * 3
        users_data[user_id] += win_amount
        title = "🎉 ג'קפוט מטורף! ניצחת! 🎉"
        description = f"🎰 |  [ {slot1} | {slot2} | {slot3} ]  | 🎰\n\nכל הכבוד! 3 סמלים זהים!\n**הרווחת:** `{win_amount:,} XP`"
        color = discord.Color.gold()
    elif slot1 == slot2 or slot1 == slot3 or slot2 == slot3:
        win_amount = int(bet_amount * 1.5)
        users_data[user_id] += (win_amount - bet_amount)
        title = "💰 ניצחון חלקי! הרווחת! 💰"
        description = f"🎰 |  [ {slot1} | {slot2} | {slot3} ]  | 🎰\n\nהשגת 2 סמלים זהים!\n**הרווחת:** `{win_amount:,} XP`"
        color = discord.Color.green()
    else:
        users_data[user_id] -= bet_amount
        title = "😢 הפסדת, אולי פעם הבאה..."
        description = f"🎰 |  [ {slot1} | {slot2} | {slot3} ]  | 🎰\n\nאף סמל לא התאים.\n**הפסדת:** `{bet_amount:,} XP`"
        color = discord.Color.red()

    save_xp(users_data)
    embed_result = discord.Embed(title=title, description=description, color=color)
    embed_result.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed_result.add_field(name="💳 יתרה חדשה בחשבון", value=f"**{users_data[user_id]:,} XP**", inline=False)
    await ctx.send(embed=embed_result)

# ------------------------------------------------------------------
# 2. משחק רולטה (!roulette)
# ------------------------------------------------------------------
@bot.command(aliases=["roulet"])
async def roulette(ctx, bet_amount: str = None, bet_type: str = None):
    if not bet_amount or not bet_type:
        embed_err = discord.Embed(
            title="🔴 🛞 קזינו NextZone - רולטה",
            description=(
                "❌ נא לציין סכום הימור וסוג הימור!\n\n"
                "**איך מהמרים?**\n"
                "• לפי צבע: `!roulette 500 red` או `black`\n"
                "• לפי סוג מספר: `!roulette 500 even` או `odd`\n"
                "• לפי מספר מדויק: `!roulette 500 14` (בין 0 ל-36)"
            ),
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed_err)

    users_data = load_xp()
    user_id = str(ctx.author.id)
    user_xp = users_data.get(user_id, 0)

    if bet_amount.lower() == "all":
        bet_amount = user_xp
    else:
        try:
            bet_amount = int(bet_amount)
        except ValueError:
            return await ctx.send("❌ סכום ההימור חייב להיות מספר שלם!")

    if bet_amount <= 0 or user_xp < bet_amount:
        return await ctx.send(f"❌ הימור לא חוקי או שאין לך מספיק XP")

    winning_number = random.randint(0, 36)
    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    winning_color = "green" if winning_number == 0 else "red" if winning_number in red_numbers else "black"

    is_win = False
    payout_multiplier = 2
    bet_type = bet_type.lower()

    if bet_type == "red" and winning_color == "red":
        is_win = True
    elif bet_type == "black" and winning_color == "black":
        is_win = True
    elif bet_type == "even" and winning_number != 0 and winning_number % 2 == 0:
        is_win = True
    elif bet_type == "odd" and winning_number % 2 != 0:
        is_win = True
    elif bet_type.isdigit() and int(bet_type) == winning_number:
        is_win = True
        payout_multiplier = 35

    color_emoji = "🔴" if winning_color == "red" else "⚫" if winning_color == "black" else "🟢"
    
    if is_win:
        win_xp = bet_amount * payout_multiplier
        users_data[user_id] += (win_xp - bet_amount)
        title = "🎉 ניצחון ברולטה! 🎉"
        desc = f"הגלגל נעצר על: **{color_emoji} {winning_number}**\n\nהימרת נכון על `{bet_type}`!\n**הרווחת:** `{win_xp:,} XP`"
        embed_color = discord.Color.green()
    else:
        users_data[user_id] -= bet_amount
        title = "😢 הפסדת ברולטה..."
        desc = f"הגלגל נעצר על: **{color_emoji} {winning_number}**\n\nההימור שלך על `{bet_type}` נכשל.\n**הפסדת:** `{bet_amount:,} XP`"
        embed_color = discord.Color.red()

    save_xp(users_data)
    embed = discord.Embed(title=title, description=desc, color=embed_color)
    embed.add_field(name="💳 יתרה חדשה", value=f"**{users_data[user_id]:,} XP**")
    await ctx.send(embed=embed)

# ------------------------------------------------------------------
# 3. משחק בלאק ג'ק אינטראקטיבי (!blackjack)
# ------------------------------------------------------------------
class BlackjackGame(discord.ui.View):
    def __init__(self, ctx, bet_amount, user_xp):
        super().__init__(timeout=60.0)
        self.ctx = ctx
        self.bet_amount = bet_amount
        self.user_xp = user_xp
        suits = ["♠️", "♥️", "♦️", "♣️"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.deck = [{"rank": r, "suit": s, "value": 11 if r == "A" else 10 if r in ["J", "Q", "K"] else int(r)} for r in ranks for s in suits]
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

    def calculate_score(self, hand):
        score = sum(card["value"] for card in hand)
        aces = sum(1 for card in hand if card["rank"] == "A")
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def make_embed(self, finished=False, status_text="המשחק בעיצומו..."):
        p_score = self.calculate_score(self.player_hand)
        d_score = self.calculate_score(self.dealer_hand)
        p_cards = " ".join(f"`{c['rank']}{c['suit']}`" for c in self.player_hand)
        if finished:
            d_cards = " ".join(f"`{c['rank']}{c['suit']}`" for c in self.dealer_hand)
            d_text = f"**יד הדילר ({d_score}):**\n{d_cards}"
        else:
            d_text = f"**יד הדילר (?):**\n`{self.dealer_hand[0]['rank']}{self.dealer_hand[0]['suit']}` `❓`"
            
        embed = discord.Embed(title="🃏 שולחן בלאק ג'ק - NextZone", description=status_text, color=discord.Color.blue())
        embed.add_field(name=f"**היד שלך ({p_score}):**", value=p_cards, inline=False)
        embed.add_field(name=d_text, value="\u200b", inline=False)
        embed.add_field(name="💰 סכום ההימור:", value=f"`{self.bet_amount:,} XP`", inline=True)
        return embed

    async def end_game(self, interaction, result):
        users_data = load_xp()
        user_id = str(self.ctx.author.id)
        if result == "win":
            users_data[user_id] += self.bet_amount
            status = "🎉 ניצחת! הרווחת את סכום ההימור! 🎉"
        elif result == "push":
            status = "🤝 תיקו (Push)! ה-XP חזר לחשבונך."
        else:
            users_data[user_id] -= self.bet_amount
            status = "😢 הפסדת, הדילר לקח את הקופה."
            
        save_xp(users_data)
        for child in self.children:
            child.disabled = True
        embed = self.make_embed(finished=True, status_text=status)
        embed.add_field(name="💳 יתרה חדשה", value=f"**{users_data[user_id]:,} XP**", inline=False)
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="🃏 Hit (קלף)", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("❌ זה לא השולחן שלך!", ephemeral=True)
        self.player_hand.append(self.deck.pop())
        if self.calculate_score(self.player_hand) > 21:


# פונקציה שמפעילה את שרת ה-Flask
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# הפעלת שרת ה-Flask בנפרד ברקע
threading.Thread(target=run_flask, daemon=True).start()
import asyncio

import discord
from discord.ext import commands

# 1. פונקציה מרכזית שמחשבת את הממברס ומעדכנת את הסטטוס
async def update_bot_status():
    # ספירת כל האנשים בכל השרתים שהבוט נמצא בהם
    member_count = sum(guild.member_count for guild in bot.guilds)
    
    # הגדרת הטקסט והפעילות (Watching X members)
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name=f"{member_count} members"
    )
    
    # עדכון הסטטוס ומצב "נא לא להפריע" (dnd)
    await bot.change_presence(status=discord.Status.dnd, activity=activity)

# 2. עדכון הסטטוס כשהבוט נדלק
@bot.event
async def on_ready():
    print(f'הבוט {bot.user.name} מחובר בהצלחה!')
    await update_bot_status()

# 3. עדכון הסטטוס מיד כשמישהו נכנס לשרת
@bot.event
async def on_member_join(member):
    await update_bot_status()

# 4. עדכון הסטטוס מיד כשמישהו עוזב את השרת
@bot.event
async def on_member_remove(member):
    await update_bot_status()



if __name__ == "__main__":
    keep_alive()
    if not TOKEN:
        raise RuntimeError("TOKEN environment variable is not set. Set TOKEN in .env or in the host config.")
    bot.run(TOKEN)

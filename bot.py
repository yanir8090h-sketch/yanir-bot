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
    async def claim(self, inter, btn):
        btn.label = "בטיפול"; btn.disabled = True; await inter.response.edit_message(view=self)
        await inter.channel.send(embed=discord.Embed(title="⚡ הטיקט נלקח לטיפול ⚡", description=f"איש הצוות {inter.user.mention} לקח את הטיקט לטיפול!", color=0x00ff00))
    @discord.ui.button(label="סגור כאן", style=discord.ButtonStyle.danger, custom_id="t_s", emoji="🔒")
    async def close(self, inter, btn):
        await inter.response.defer()
        await inter.channel.delete()

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="👑 בחינה לקבלת צוות השרת", value="staff", emoji="👑", description="פתיחת טיקט מבחן קבלה לסטאף"),
            discord.SelectOption(label="🛠️ פנייה כללית לצוות העזרה", value="general", emoji="🛠️", description="עזרה כללית, דיווחים או שאלות לצוות")
        ]
        super().__init__(placeholder="🎫 בחר את סיבת הפנייה שלך כאן...", custom_id="t_drop", options=options)

    async def callback(self, inter):
        g = inter.guild; u = inter.user
        choice = self.values[0]
        
        if choice == "staff":
            ch = await g.create_text_channel(name=f"📝-בחינה-{u.name}", overwrites={g.default_role: discord.PermissionOverwrite(read_messages=False), u: discord.PermissionOverwrite(read_messages=True, send_messages=True)})
            await inter.response.send_message(f"✅ חדר הבחינה שלך נפתח בהצלחה: {ch.mention}", ephemeral=True)
            emb = discord.Embed(title="👑 שאלון מועמדות לצוות השרת - NextZone 👑", description=f"שלום {u.mention},\nאנא ענה על 14 השאלות הבאות כאן בצ'אט:\n\n1️⃣ שם מלא / כינוי:\n2️⃣ גיל:\n3️⃣ כמה זמן אתה בשרת?\n4️⃣ ניסיון קודם וסיבת עזיבה:\n5️⃣ איך אתה מגדיר צוות ותכונות טובות?\n6️⃣ מה תעשה בריב/מתחצף בויס? תן דוגמה:\n7️⃣ תגובה לתקיפה מצוות מתחתיך/מעליך:\n8️⃣ כמה זמן תוכל לתת בשבוע כל יום?\n9️⃣ שינוי מצב של חוסר פעילות? איך?:\n🔟 באיזה תחומים אתה רוצה לעזור?\n1️⃣1️⃣ תרומה לשרת ויעדי הגעה:\n1️⃣2️⃣ מאיפה הרצון להצטרף?:\n1️⃣3️⃣ למה אתה מתאים? רעיונות לשיפור?:\n1️⃣4️⃣ האם יש לך 2FA מופעל בחשבון?\n\n⚠️ **נא לענות ברצינות, בהצלחה!**", color=0x00ff00)
            await ch.send(embed=emb, view=MngButtons())
        else:
            ch = await g.create_text_channel(name=f"🛠️-פנייה-{u.name}", overwrites={g.default_role: discord.PermissionOverwrite(read_messages=False), u: discord.PermissionOverwrite(read_messages=True, send_messages=True)})
            await inter.response.send_message(f"✅ חדר הפנייה הכללית נפתח בהצלחה: {ch.mention}", ephemeral=True)
            emb = discord.Embed(title="🛠️ פנייה כללית לצוות העזרה - NextZone 🛠️", description=f"שלום {u.mention},\nפתחת פנייה כללית לצוות השרת.\nאנא רשום כאן בפירוט את סיבת הפנייה שלך, ואיש צוות יתפנה אליך בהקדם!", color=0x3498db)
            await ch.send(embed=emb, view=MngButtons())

# ==================================================================
# 👑 חנות ה-XP הרשמית (Shop System) מחוברת ל-DATABASE האמיתי
# ==================================================================

class ShopDropdown(discord.ui.Select):
    def __init__(self):
        # הגדרת הרולים ומחיריהם בדיוק לפי ה-IDs של השרת שלך
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
        # מונע את השגיאה This interaction failed
        await interaction.response.defer(ephemeral=True)
        
        selected_role_id = int(self.values)
        price = self.role_prices.get(selected_role_id)
        user = interaction.user
        guild = interaction.guild
        
        role = guild.get_role(selected_role_id)
        if not role:
            return await interaction.followup.send("❌ שגיאה: הרול המבוקש לא נמצא בשרת.", ephemeral=True)
        if role in user.roles:
            return await interaction.followup.send("❌ כבר יש לך את הרול הזה!", ephemeral=True)

        # בדיקת ה-XP מתוך ה-Database של ה-SQLite שלך
        user_xp = get_xp(user.id)
        if user_xp < price:
            missing_xp = price - user_xp
            return await interaction.followup.send(f"❌ אין לך מספיק XP לרול הזה! יש לך {user_xp:,} XP וחסר לך עוד {missing_xp:,} XP.", ephemeral=True)

        try:
            add_xp(user.id, -price)
            await user.add_roles(role)
            await interaction.followup.send(f"✅ קנית את הרול {role.mention} בהצלחה! הורדו מחשבונך {price:,} XP.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ לבוט אין הרשאות מתאימות (Manage Roles) כדי לתת לך את הרול הזה.", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

@bot.command(name="shop")
async def shop_command(ctx):
    shop_text = (
        "1. 👑 ➔ <@&1522553430034616351> ➔ 5,000 XP\n"
        "2. 🌟 ➔ <@&1522553732984733867> ➔ 10,000 XP\n"
        "3. 💎 ➔ <@&1522553933833441330> ➔ 20,000 XP\n"
        "4. 🌀 ➔ <@&1522554104063201301> ➔ 35,000 XP\n"
        "5. 🟢 ➔ <@&1522554362965000283> ➔ 50,000 XP\n\n"
        "*Developed By: Main Bot -- Soon.*"
    )
    embed1 = discord.Embed(title="👑 NextZone XP Shop", description=shop_text, color=discord.Color.blue())
    if ctx.guild.icon: 
        embed1.set_thumbnail(url=ctx.guild.icon.url)
    embed2 = discord.Embed(title="בחר רול לקנייה", color=discord.Color.blue())
    await ctx.send(embeds=[embed1, embed2], view=ShopView())



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

    if lower_text == "!setup_casino":
        await msg.delete()
        bal = ensure_casino_balance(msg.author.id)
        description = "🎰 ברוכים הבאים לקזינו!\n"
        description += f"יש לך {bal:,} XP.\n\n"
        description += "להימור: `!הימור <סכום>`\n"
        description += "למשחקים: `!קזינו משחקים`\n"
        description += "לרכישה: לחץ על אחד הכפתורים למטה או השתמש ב-`!קזינו קנה <מזהה>`\n\n"
        description += "רולים זמינים:\n"
        for key, (label, price, _) in CASINO_ROLE_SHOP.items():
            description += f"• `{key}` — {label} ב-{price:,} XP\n"
        emb = discord.Embed(title="🎰 קזינו XP", description=description, color=0xFFD700)
        await msg.channel.send(embed=emb, view=CasinoView())
        return

    if lower_text in ("!קזינו משחקים", "!משחקים"):
        await msg.channel.send(
            "🎲 משחקי קזינו זמינים:\n"
            "• `!קזינו משחק מטבע <סכום>` — משחק מטבע, זכייה x2\n"
            "• `!קזינו משחק חריצים <סכום>` — חריצים, 3 סמלים זהים x4, 2 סמלים זהים x2\n"
            "• `!קזינו משחק גלגל <סכום>` — גלגל מזל, זכייה x3 אם נוחת על 7\n"
        )
        return

    if lower_text.startswith("!קזינו משחק"):
        parts = text.split()
        if len(parts) < 3:
            await msg.channel.send("❌ השתמש: `!קזינו משחק <מטבע|חריצים|גלגל> <סכום>`")
            return
        game = parts[2]
        if len(parts) < 4:
            await msg.channel.send("❌ הכנס סכום לאחר סוג המשחק.")
            return
        try:
            amount = int(parts[3].replace(',', ''))
        except ValueError:
            await msg.channel.send("❌ הכנס סכום תקין.")
            return
        xp = get_xp(msg.author.id)
        if amount <= 0:
            await msg.channel.send("❌ סכום צריך להיות גדול מ-0.")
            return
        if amount > xp:
            await msg.channel.send(f"❌ אין לך מספיק XP. יש לך {xp:,} XP.")
            return

        if game == "מטבע":
            win = random.choice([True, False])
            if win:
                add_xp(msg.author.id, amount)
                await msg.channel.send(f"🪙 פגעת בהימור! קיבלת {amount:,} XP נוספים. יש לך כעת {get_xp(msg.author.id):,} XP.")
            else:
                add_xp(msg.author.id, -amount)
                await msg.channel.send(f"🪙 הפסדת {amount:,} XP. נשאר לך {get_xp(msg.author.id):,} XP.")
            return

        if game == "חריצים":
            symbols = ["🍒", "🍋", "🍉", "7️⃣", "⭐"]
            spin = [random.choice(symbols) for _ in range(3)]
            result = " ".join(spin)
            if spin[0] == spin[1] == spin[2]:
                win_amount = amount * 4
                add_xp(msg.author.id, win_amount)
                await msg.channel.send(f"🎰 {result}\nפגשת שלושה סמלים זהים! זכית {win_amount:,} XP.")
            elif spin[0] == spin[1] or spin[1] == spin[2] or spin[0] == spin[2]:
                win_amount = amount * 2
                add_xp(msg.author.id, win_amount)
                await msg.channel.send(f"🎰 {result}\nשני סמלים זהים! זכית {win_amount:,} XP.")
            else:
                add_xp(msg.author.id, -amount)
                await msg.channel.send(f"🎰 {result}\nלא נצחת הפעם. הפסדת {amount:,} XP.")
            return

        if game == "גלגל":
            number = random.randint(1, 10)
            if number == 7:
                win_amount = amount * 3
                add_xp(msg.author.id, win_amount)
                await msg.channel.send(f"🎡 מספר {number}! זכית {win_amount:,} XP. יש לך כעת {get_xp(msg.author.id):,} XP.")
            else:
                add_xp(msg.author.id, -amount)
                await msg.channel.send(f"🎡 מספר {number}. הפסדת {amount:,} XP.")
            return

        await msg.channel.send("❌ סוג משחק לא מוכר. בחר: מטבע, חריצים או גלגל.")
        return

    if lower_text in ("!casino", "!קזינו"):
        bal = ensure_casino_balance(msg.author.id)
        description = "🎰 ברוכים הבאים לקזינו!\n"
        description += f"יש לך {bal:,} XP.\n\n"
        description += "להימור: `!הימור <סכום>`\n"
        description += "למשחקים: `!קזינו משחקים`\n"
        description += "לרכישה: לחץ על אחד הכפתורים למטה או השתמש ב-`!קזינו קנה <מזהה>`\n\n"
        description += "רולים זמינים:\n"
        for key, (label, price, _) in CASINO_ROLE_SHOP.items():
            description += f"• `{key}` — {label} ב-{price:,} XP\n"
        emb = discord.Embed(title="🎰 קזינו XP", description=description, color=0xFFD700)
        await msg.channel.send(embed=emb, view=CasinoView())
        return

    if lower_text.startswith("!קזינו קנה"):
        parts = text.split()
        if len(parts) < 3:
            await msg.channel.send("❌ השתמש: `!קזינו קנה <מזהה>`")
            return
        key = parts[2].lower()
        if key not in CASINO_ROLE_SHOP and not (key.isdigit() and int(key) == SPECIAL_CASINO_ROLE_ID):
            await msg.channel.send("❌ רול לא חוקי. בחר את אחד המזהים הבאים: " + ", ".join(CASINO_ROLE_SHOP.keys()) + ", או את ה-ID המלא אם זה הרול המיוחד.")
            return
        if key in CASINO_ROLE_SHOP:
            label, price, role_id = CASINO_ROLE_SHOP[key]
        else:
            label, price, role_id = ("רול קזינו מיוחד", 18000, SPECIAL_CASINO_ROLE_ID)
        if get_xp(msg.author.id) < price:
            await msg.channel.send(f"❌ אין לך מספיק XP לקנות את {label}. צריך {price:,} XP.")
            return
        role = find_role(msg.guild, role_id)
        if not role:
            await msg.channel.send("❌ הרול לא קיים בשרת.")
            return
        if role in msg.author.roles:
            await msg.channel.send(f"❌ כבר יש לך את {label}.")
            return
        add_xp(msg.author.id, -price)
        await msg.author.add_roles(role)
        await msg.channel.send(f"🎉 קנית את {label} ב-{price:,} XP! מזל טוב.")
        return

    if lower_text.startswith("!הימור"):
        parts = text.split()
        if len(parts) < 2:
            await msg.channel.send("❌ השתמש: `!הימור <סכום>`")
            return
        try:
            amount = int(parts[1].replace(',', ''))
        except ValueError:
            await msg.channel.send("❌ הכנס סכום תקין.")
            return
        if amount <= 0:
            await msg.channel.send("❌ סכום צריך להיות גדול מ-0.")
            return
        xp = get_xp(msg.author.id)
        if amount > xp:
            await msg.channel.send(f"❌ אין לך מספיק XP. יש לך {xp:,} XP.")
            return
        roll = random.randint(1, 100)
        if roll <= 45:
            add_xp(msg.author.id, -amount)
            await msg.channel.send(f"🎲 הפסדת {amount:,} XP. נשאר לך {get_xp(msg.author.id):,} XP.")
        elif roll <= 85:
            add_xp(msg.author.id, amount)
            await msg.channel.send(f"🎲 זכית! קיבלת {amount:,} XP. סך הכל יש לך {get_xp(msg.author.id):,} XP.")
        else:
            add_xp(msg.author.id, amount * 2)
            await msg.channel.send(f"🎉 ג'קפוט! קיבלת {amount * 2:,} XP! סך הכל יש לך {get_xp(msg.author.id):,} XP.")
        return

    if lower_text.startswith("!h"):
        if msg.id in processed_message_ids:
            return
        processed_message_ids.add(msg.id)
        reason = text[3:].strip()
        if not reason:
            await msg.channel.send("❌ נא לציין סיבה לפתיחת קריאת העזרה!", delete_after=5)
            return
        vt = msg.author.voice.channel.mention if msg.author.voice and msg.author.voice.channel else "מחוץ לווייס"
        emb = discord.Embed(title="⚠️ בקשת עזרה ⚠️", description=f"📝 סיבה: {reason} | 🎧 ווייס: {vt}", color=0xff0000)
        staff_role = msg.guild.get_role(1521955150309359747)
        if staff_role and not any(sub in staff_role.name.lower() for sub in STAFF_ROLE_NAMES):
            staff_role = None
                # בדיקה ישירה לפי ה-ID של רול הצוות
        staff_role = msg.guild.get_role(STAFF_ROLE_ID)
        
        if not staff_role:
            await msg.channel.send(f"❌ לא נמצא רול צוות עם ה-ID {STAFF_ROLE_ID} בשרת זה.")
            return

            return
        mention = staff_role.mention
        allowed = discord.AllowedMentions(roles=True)
        await msg.channel.send(content=mention, embed=emb, view=HelpView(msg.author, reason, vt), allowed_mentions=allowed)
        return

    await bot.process_commands(msg)


if __name__ == "__main__":
    keep_alive()
    if not TOKEN:
        raise RuntimeError("TOKEN environment variable is not set. Set TOKEN in .env or in the host config.")
    bot.run(TOKEN)

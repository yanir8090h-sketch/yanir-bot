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
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
processed_message_ids = set()


# 🆔 מזהי רולים כלליים של השרת שלך:
STAFF_ROLE_ID = 1520870990543065111    
MNG_ROLE =   1520870990564032614
MEMBER_ROLE = 1520870990526021694       
VETERAN_ROLE_ID = 1520870990526021694

# 🆔 מזהי ארבעת הרולים החדשים של החנות:
ROLE_MNG_SUPPORT = 1520802461306271825    # Manager Support
ROLE_EV_MNG = 1520807998505312431         # Event Manager
ROLE_SUP_TEAM = 1520870990535312431       # Support Team
ROLE_LEAK_TEAM = 1520870990505312430      # Leaks Team
STAFF_FRIEND_ROLE_ID = 1521762736944709742  # Staff Friend
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
    def __init__(self):
        super().__init__(timeout=None) # הכפתורים יישארו פעילים לתמיד ולא יינעלו

    @discord.ui.button(label="✋ טפל בטיקט", style=discord.ButtonStyle.success, custom_id="ticket_claim")
    async def claim(self, inter: discord.Interaction, btn: discord.ui.Button):
        # בדיקה אם הלוחץ הוא איש צוות (סטאף או היי סטאף)
        is_staff = any(r.id in [STAFF_ROLE_ID, MNG_ROLE] for r in inter.user.roles)
        if not is_staff and not inter.user.guild_permissions.administrator:
            return await inter.response.send_message("❌ רק חברי צוות יכולים לטפל בטיקטים!", ephemeral=True)

        # נעילת הכפתור ושינוי הטקסט שלו
        btn.disabled = True
        btn.label = "🔒 בטיפול"
        await inter.response.edit_message(view=self)

        # שינוי שם הערוץ לסטטוס בטיפול כדי ששאר הצוות ידע
        current_name = inter.channel.name.replace("🎫-", "").replace("📝-", "").replace("🛠️-", "")
        try:
            await inter.channel.edit(name=f"⚙️-בטיפול-{current_name}")
        except:
            pass # מונע קריסה של הבוט במקרה של מגבלת קצב של דיסקורד

        await inter.channel.send(f"🔒 הטיקט ננעל לטיפול על ידי {inter.user.mention}.")

    @discord.ui.button(label="🔒 סגור טיקט", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    async def close(self, inter: discord.Interaction, btn: discord.ui.Button):
        # בדיקה אם הלוחץ מורשה לסגור את החדר
        is_staff = any(r.id in [STAFF_ROLE_ID, MNG_ROLE] for r in inter.user.roles)
        if not is_staff and not inter.user.guild_permissions.administrator:
            return await inter.response.send_message("❌ רק חברי צוות יכולים לסגור טיקטים!", ephemeral=True)

        await inter.response.send_message("⚠️ הטיקט ייסגר ויימחק סופית בעוד 5 שניות...")
        await asyncio.sleep(5)
        await inter.channel.delete()

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="בחינה לצוות", value="staff", emoji="📝", description="פתיחת טיקט להגשת מועמדות לצוות השרת"),
            discord.SelectOption(label="עזרה כללית", value="general", emoji="🛠️", description="פתיחת טיקט לקבלת עזרה כללית מחברי הצוות")
        ]
        super().__init__(placeholder="🎫 נא לבחור את סוג הפנייה שלך...", custom_id="t_drop", options=options)

    async def callback(self, inter: discord.Interaction):
        g = inter.guild
        u = inter.user
        choice = self.values[0] if self.values else ""

        if choice == "staff":
            # 🎯 בחינה לצוות: רול היי סטאף (MNG_ROLE) מקבל גישה בלבד
            high_staff = g.get_role(1520870990543065117)
            overwrites = {
                g.default_role: discord.PermissionOverwrite(read_messages=False),
                u: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            if high_staff:
                overwrites[high_staff] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            ch = await g.create_text_channel(name=f"📝-בחינה-{u.name}", overwrites=overwrites)
            await inter.response.send_message(f"✅ טיקט בחינה נפתח בהצלחה: {ch.mention}", ephemeral=True)
            
            # יצירת ה-Embed עם 14 השאלות המלאות
            emb = discord.Embed(
                title="📝 טופס הגשת מועמדות לצוות השרת 📝", 
                description=f"👋 שלום {u.mention},\nפתחת פנייה עבור **בחינה לצוות השרת**.\nאנא העתק את השאלות הבאות וענה עליהן בפירוט מלא.\n\n"
                            "1️⃣ **שם מלא / כינוי:**\n\n"
                            "2️⃣ **גיל:**\n\n"
                            "3️⃣ **כמה זמן אתה בשרת?**\n\n"
                            "4️⃣ **ניסיון קודם וסיבת עזיבה:**\n\n"
                            "5️⃣ **איך אתה מגדיר צוות ותכונות טובות?**\n\n"
                            "6️⃣ **מה תעשה בריב/מתחצף בויס? תן דוגמה:**\n\n"
                            "7️⃣ **תגובה לתקיפה מצוות מתחתיך/מעליך:**\n\n"
                            "8️⃣ **כמה זמן תוכל לתת בשבוע כל יום?**\n\n"
                            "9️⃣ **שינוי מצב של חוסר פעילות? איך?:**\n\n"
                            "🔟 **באיזה תחומים אתה רוצה לעזור?**\n\n"
                            "1️⃣1️⃣ **תרומה לשרת ויעדי הגעה:**\n\n"
                            "1️⃣2️⃣ **מאיפה הרצון להצטרף?:**\n\n"
                            "1️⃣3️⃣ **למה אתה מתאים? רעיונות לשיפור?:**\n\n"
                            "1️⃣4️⃣ **האם יש לך 2FA מופעל בחשבון?**", 
                color=0x3498db
            )
            emb.set_footer(text="בהצלחה! צוות היי-סטאף יבחן את טופס המועמדות שלך.")
            await ch.send(embed=emb, view=MngButtons())
            
        else:
            # 🎯 עזרה כללית: רול סטאף רגיל ומעלה (STAFF_ROLE_ID) מקבל גישה
            general_staff = g.get_role(1520870990543065111)
            overwrites = {
                g.default_role: discord.PermissionOverwrite(read_messages=False),
                u: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            if general_staff:
                overwrites[general_staff] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            ch = await g.create_text_channel(name=f"🛠️-עזרה-{u.name}", overwrites=overwrites)
            await inter.response.send_message(f"✅ טיקט עזרה נפתח בהצלחה: {ch.mention}", ephemeral=True)
            
            emb = discord.Embed(
                title="🔔 פנייה חדשה - עזרה כללית 🔔", 
                description=f"👋 שלום {u.mention},\nפתחת פנייה לעזרה כללית מצוות השרת (**סטאף**).\nאנא רשום כאן בפירוט את שאלתך, ואחד מחברי הצוות יעזור לך בהקדם.", 
                color=0x2ecc71
            )
            emb.set_footer(text="צוות השרת יענה לך בהקדם.")
            await ch.send(embed=emb, view=MngButtons())

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(TicketDropdown())

XP_ROLE_SHOP = {
    "mng_sup": {"id": 1520802461306271825, "price": 50000},   # Manager Support
    "evt_mng": {"id": 1520807998505312431, "price": 35000},   # Event Manager
    "sup_team": {"id": 1520870990535312431, "price": 20000},  # Support Team
    "leak_team": {"id": 1520870990505312430, "price": 10000}  # Leaks Team
}

class XPShopSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Manager Support", value="mng_sup", description="Price: 50,000 XP", emoji="✨"),
            discord.SelectOption(label="Event Manager", value="evt_mng", description="Price: 35,000 XP", emoji="🎉"),
            discord.SelectOption(label="Support Team", value="sup_team", description="Price: 20,000 XP", emoji="🛠️"),
            discord.SelectOption(label="Leaks Team", value="leak_team", description="Price: 10,000 XP", emoji="📡")
        ]
        super().__init__(placeholder="🛒 Select a role to buy...", min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        item_id = self.values[0]
        role_data = XP_ROLE_SHOP.get(item_id)
        
        if not role_data:
            return await inter.response.send_message("❌ השגיאה: הפריט לא נמצא בחנות.", ephemeral=True)

        price = role_data["price"]
        role_id = role_data["id"]

        current_xp = add_xp(inter.user.id, 0)
        if current_xp < price:
            return await inter.response.send_message(f"❌ אין לך מספיק XP! חסרים לך {price - current_xp:,} XP לרול זה.", ephemeral=True)

        role = inter.guild.get_role(role_id)
        if not role:
            return await inter.response.send_message("❌ שגיאה: הרול המבוקש לא נמצא בשרת זה.", ephemeral=True)

        if role in inter.user.roles:
            return await inter.response.send_message("❌ כבר יש לך את הרול הזה!", ephemeral=True)

        add_xp(inter.user.id, -price)
        await inter.user.add_roles(role)
        
        new_xp = add_xp(inter.user.id, 0)
        await inter.response.send_message(f"✅ קנית בהצלחה את הרול **{role.name}**! ירד לך {price:,} XP. יתרה נוכחית: {new_xp:,} XP.", ephemeral=True)

        # הבאת הרול מתוך השרת באמצעות ה-ID שלו
        role = inter.guild.get_role(role_id)
        if not role:
            return await inter.response.send_message("❌ שגיאה: הרול המבוקש לא נמצא בשרת זה.", ephemeral=True)

        # בדיקה אם המשתמש כבר מחזיק ברול המבוקש
        if role in inter.user.roles:
            return await inter.response.send_message("❌ כבר יש לך את הרול הזה!", ephemeral=True)

        # ביצוע הרכישה: החסרת ה-XP והענקת הרול
        add_xp(inter.user.id, -price)
        await inter.user.add_roles(role)
        
        # שליחת הודעת הצלחה פרטית (רק המשתמש רואה אותה)
        new_xp = add_xp(inter.user.id, 0)
        await inter.response.send_message(f"✅ קנית בהצלחה את הרול **{role.name}**! ירד לך {price:,} XP. יתרה נוכחית: {new_xp:,} XP.", ephemeral=True)

class XPShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(XPShopSelect())

@bot.tree.command(name="xpshop", description="פתיחת חנות הרולים הרשמית ב-XP")
async def xpshop_slash(inter: discord.Interaction):
    emb = discord.Embed(
        title="🛒 חנות הרולים הרשמית ב-XP 🛒",
        description="ברוכים הבאים לחנות ה-XP! \nפתחו את התפריט הנפתח למטה ובחרו את הרול שברצונכם לרכוש.",
        color=0x00ff00
    )
    emb.set_footer(text="הרכישה תוריד XP באופן מיידי מחשבונכם")
    await inter.response.send_message(embed=emb, view=XPShopView())

@bot.command(name="sync")
@commands.is_owner() # רק אתה (יוצר הבוט) תוכל להפעיל אותה
async def sync_commands(ctx):
    try:
        fmt = await bot.tree.sync()
        await ctx.send(f"✅ סונכרנו בהצלחה {len(fmt)} פקודות סלאש לשרת!")
    except Exception as e:
        await ctx.send(f"❌ שגיאה בזמן הסנכרון: {e}")

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
    print(f"Logged in as {bot.user.name}")
    print("Bot is ready and active!")
    
    # טעינת ה-Views הקיימים והתקינים שלך כדי שימשיכו לעבוד לתמיד
    try:
        bot.add_view(TicketView())
        bot.add_view(VerifyView())
        bot.add_view(CasinoView())
        bot.add_view(MngButtons())
    except Exception as e:
        print(f"Error adding persistent views: {e}")
        
    # סנכרון אוטומטי של פקודות הסלאש
    try:
        if GUILD_ID:
            await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        else:
            await bot.tree.sync()
        print("Slash commands synced successfully!")
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
        if staff_role and staff_role.id != STAFF_ROLE_NAMES:
            staff_role = None
                # בדיקה ישירה לפי ה-ID של רול הצוות
        staff_role = msg.guild.get_role(1520870990543065111)
        
        if not staff_role:
            await msg.channel.send(f"❌ לא נמצא רול צוות עם ה-ID {STAFF_ROLE_ID} בשרת זה.")
            return

            return
        mention = staff_role.mention
        allowed = discord.AllowedMentions(roles=True)
        await msg.channel.send(content=mention, embed=emb, view=HelpView(msg.author, reason, vt), allowed_mentions=allowed)
        return

    await bot.process_commands(msg)
def get_log_channel(guild):
    # מחק את המספר הישן והדבק כאן את המספר שהעתקת הרגע בדיסקורד!
    return guild.get_channel(1523091026720591973)


@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    ch = get_log_channel(message.guild)
    if not ch:
        return

    emb = discord.Embed(title="🗑️ הודעה נמחקה", color=0xff0000, timestamp=datetime.utcnow())
    emb.add_field(name="👤 כותב ההודעה:", value=message.author.mention, inline=True)
    emb.add_field(name="📺 ערוץ:", value=message.channel.mention, inline=True)
    emb.add_field(name="📝 תוכן ההודעה שנמחקה:", value=message.content if message.content else "*הודעה ללא טקסט (תמונה/קובץ)*", inline=False)
    await ch.send(embed=emb)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    ch = get_log_channel(before.guild)
    if not ch:
        return

    emb = discord.Embed(title="✏️ הודעה נערכה", color=0xffa500, timestamp=datetime.utcnow())
    emb.add_field(name="👤 משתמש:", value=before.author.mention, inline=True)
    emb.add_field(name="📺 ערוץ:", value=before.channel.mention, inline=True)
    emb.add_field(name="⬅️ לפני השינוי:", value=before.content, inline=False)
    emb.add_field(name="➡️ אחרי השינוי:", value=after.content, inline=False)
    await ch.send(embed=emb)

@bot.event
async def on_member_join(member):
    ch = get_log_channel(member.guild)
    if not ch:
        return

    emb = discord.Embed(title="📥 משתמש נכנס לשרת", color=0x00ff00, timestamp=datetime.utcnow())
    emb.add_field(name="👤 משתמש:", value=member.mention, inline=True)
    emb.add_field(name="🆔 ID:", value=member.id, inline=True)
    emb.set_thumbnail(url=member.display_avatar.url)
    await ch.send(embed=emb)

@bot.event
async def on_member_remove(member):
    ch = get_log_channel(member.guild)
    if not ch:
        return

    emb = discord.Embed(title="📤 משתמש עזב את השרת", color=0xff0000, timestamp=datetime.utcnow())
    emb.add_field(name="👤 משתמש:", value=member.mention, inline=True)
    emb.add_field(name="🆔 ID:", value=member.id, inline=True)
    emb.set_thumbnail(url=member.display_avatar.url)
    await ch.send(embed=emb)

@bot.event
async def on_voice_state_update(member, before, after):
    ch = get_log_channel(member.guild)
    if not ch:
        return

    if before.channel is None and after.channel is not None:
        emb = discord.Embed(title="🔊 כניסה לוויס", color=0x2ecc71, timestamp=datetime.utcnow())
        emb.add_field(name="👤 משתמש:", value=member.mention, inline=True)
        emb.add_field(name="📥 התחבר לחדר:", value=after.channel.name, inline=True)
        await ch.send(embed=emb)

    elif before.channel is not None and after.channel is None:
        emb = discord.Embed(title="🔇 יציאה מהוויס", color=0xe74c3c, timestamp=datetime.utcnow())
        emb.add_field(name="👤 משתמש:", value=member.mention, inline=True)
        emb.add_field(name="📤 התנתק מהחדר:", value=before.channel.name, inline=True)
        await ch.send(embed=emb)

# ==========================================
#      פונקציות עזר למערכת ה-XP שלך
# ==========================================
if 'user_xp' not in globals():
    user_xp = {}

def get_xp(user_id):
    return user_xp.get(user_id, 100)  # 100 XP מתנה להתחלה

def update_xp(user_id, amount):
    current = get_xp(user_id)
    user_xp[user_id] = max(0, current + amount)  # מונע מה-XP לרדת מתחת ל-0


# ==========================================
#             פקודות המשחקים באנגלית
# ==========================================

# ---- תפריט המשחקים המעוצב ----
@bot.command(name="games")
async def games_menu(ctx):
    embed = discord.Embed(
        title="🎮 מרכז משחקי ה-XP של השרת!",
        description="המר את ה-XP שלך ושחק במשחקים הבאים כדי להרוויח או להפסיד!",
        color=discord.Color.purple()
    )
    embed.add_field(name="🎰 רולטה (`!roulette [כמות] [אדום/שחור/ירוק או מספר]`)", value="המר על צבע או מספר (0-36).", inline=False)
    embed.add_field(name="🎲 קוביות (`!dice [כמות]`)", value="הטל קוביות נגד הבוט. מי שמקבל תוצאה גבוהה יותר מנצח!", inline=False)
    embed.add_field(name="🪙 מטבע (`!coin [כמות] [עץ/פלי]`)", value="הטל מטבע ונחש האם ייצא עץ או פלי.", inline=False)
    embed.add_field(name="🔮 ניחוש (`!guess [כמות] [מספר]`)", value="נחש מספר בין 1 ל-5. פי 4 זכייה אם צדקת!", inline=False)
    embed.set_footer(text="בהצלחה! שחקו באחריות.")
    await ctx.send(embed=embed)

# ---- 1. משחק רולטה ----
@bot.command(name="roulette")
async def roulette(ctx, amount: int, bet: str):
    xp = get_xp(ctx.author.id)
    if amount <= 0:
        return await ctx.send("❌ סכום ההימור חייב להיות גדול מ-0!")
    if xp < amount:
        return await ctx.send(f"❌ אין לך מספיק XP כדי להמר על סכום זה!")

    bet = bet.lower()
    valid_colors = ["אדום", "שחור", "ירוק"]
    
    roll_num = random.randint(0, 36)
    if roll_num == 0:
        roll_color = "ירוק"
    elif roll_num % 2 == 0:
        roll_color = "אדום"
    else:
        roll_color = "שחור"

    win = False
    payout = amount

    if bet in valid_colors:
        if bet == roll_color:
            win = True
            payout = amount * 14 if bet == "ירוק" else amount
    else:
        try:
            bet_num = int(bet)
            if bet_num == roll_num:
                win = True
                payout = amount * 35
        except ValueError:
            return await ctx.send("❌ הימור לא תקין! בחר צבע (אדום/שחור/ירוק) או מספר (0-36).")

    if win:
        update_xp(ctx.author.id, payout)
        color_embed = discord.Color.green()
        result_text = f"🎉 נחת על **{roll_color} ({roll_num})**! ניצחת והרווחת **{payout} XP**!"
    else:
        update_xp(ctx.author.id, -amount)
        color_embed = discord.Color.red()
        result_text = f"📉 נחת על **{roll_color} ({roll_num})**! הפסדת **{amount} XP**."

    embed = discord.Embed(title="🎰 תוצאת הרולטה", description=result_text, color=color_embed)
    await ctx.send(embed=embed)

# ---- 2. משחק קוביות ----
@bot.command(name="dice")
async def dice(ctx, amount: int):
    xp = get_xp(ctx.author.id)
    if amount <= 0 or xp < amount:
        return await ctx.send("❌ סכום לא תקין או שאין לך מספיק XP!")

    user_roll = random.randint(1, 6) + random.randint(1, 6)
    bot_roll = random.randint(1, 6) + random.randint(1, 6)

    if user_roll > bot_roll:
        update_xp(ctx.author.id, amount)
        res = f"🎉 ניצחת! גלגלת **{user_roll}** והבוט גלגל **{bot_roll}**. הרווחת **{amount} XP**!"
        color = discord.Color.green()
    elif user_roll < bot_roll:
        update_xp(ctx.author.id, -amount)
        res = f"📉 הפסדת! גלגלת **{user_roll}** והבוט גלגל **{bot_roll}**. הפסדת **{amount} XP**."
        color = discord.Color.red()
    else:
        res = f"🤝 תיקו! שניכם גלגלתם **{user_roll}**. ה-XP שלך לא השתנה."
        color = discord.Color.gold()

    embed = discord.Embed(title="🎲 קרב קוביות", description=res, color=color)
    await ctx.send(embed=embed)

# ---- 3. משחק מטבע ----
@bot.command(name="coin")
async def coinflip(ctx, amount: int, bet: str):
    xp = get_xp(ctx.author.id)
    if amount <= 0 or xp < amount:
        return await ctx.send("❌ סכום לא תקין או שאין לך מספיק XP!")

    if bet not in ["עץ", "פלי"]:
        return await ctx.send("❌ עליך לבחור `עץ` או `פלי`!")

    result = random.choice(["עץ", "פלי"])

    if bet == result:
        update_xp(ctx.author.id, amount)
        res = f"🪙 המטבע נחת על **{result}**! צדקת והרווחת **{amount} XP**!"
        color = discord.Color.green()
    else:
        update_xp(ctx.author.id, -amount)
        res = f"🪙 המטבע נחת על **{result}**! טעית והפסדת **{amount} XP**."
        color = discord.Color.red()

    embed = discord.Embed(title="🪙 הטלת מטבע", description=res, color=color)
    await ctx.send(embed=embed)

# ---- 4. משחק ניחוש מספר ----
@bot.command(name="guess")
async def guess(ctx, amount: int, number: int):
    xp = get_xp(ctx.author.id)
    if amount <= 0 or xp < amount:
        return await ctx.send("❌ סכום לא תקין או שאין לך מספיק XP!")
    if number < 1 or number > 5:
        return await ctx.send("❌ עליך לנחש מספר בין 1 ל-5!")

    secret_number = random.randint(1, 5)

    if number == secret_number:
        payout = amount * 4
        update_xp(ctx.author.id, payout)
        res = f"🔮 מדהים! המספר היה **{secret_number}**! ניצחת פי 4 והרווחת **{payout} XP**!"
        color = discord.Color.green()
    else:
        update_xp(ctx.author.id, -amount)
        res = f"🔮 פספוס! המספר היה **{secret_number}**. הפסדת **{amount} XP**."
        color = discord.Color.red()

    embed = discord.Embed(title="🔮 ניחוש המספר הסודי", description=res, color=color)
    await ctx.send(embed=embed)

# ==========================================
#        תפיסת שגיאות קלט (טיפול ב-BadArgument)
# ==========================================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ שגיאה בקלט הפקודה",
            description="נראה שהזנת אותיות/טקסט במקום מספר (למשל בכמות ההימור). אנא נסה שוב עם מספר שלם תקין בלבד!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        await bot.process_respond_error(ctx, error) if hasattr(bot, 'process_respond_error') else None
        raise error


# ==========================================
#    מערכת נתונים מדומה לסטטיסטיקות פעילות
# ==========================================
def get_user_stats(user_id):
    return {
        "daily": {"messages": 45, "hours": 1.5},
        "weekly": {"messages": 320, "hours": 12.0},
        "monthly": {"messages": 1420, "hours": 54.2},
        "yearly": {"messages": 12450, "hours": 410.5}
    }

# ==========================================
#        יצירת כפתורי הניווט המתוקנים
# ==========================================
class StatsView(discord.ui.View):
    def __init__(self, target_user):
        super().__init__(timeout=60)
        self.target_user = target_user
        self.stats = get_user_stats(target_user.id)

    def create_stats_embed(self, timeframe, title_text, color):
        data = self.stats[timeframe]
        embed = discord.Embed(
            title=f"📊 סטטיסטיקות פעילות - {title_text}",
            description=f"הפעילות של {self.target_user.mention} בשרת לתקופה זו:",
            color=color
        )
        embed.add_field(name="💬 הודעות שנשלחו", value=f"**{data['messages']}** הודעות", inline=True)
        embed.add_field(name="🎙️ זמן בחדרי קול", value=f"**{data['hours']}** שעות", inline=True)
        embed.set_thumbnail(url=self.target_user.display_avatar.url)
        embed.set_footer(text="המערכת מתעדכנת בזמן אמת")
        return embed

    @discord.ui.button(label="📅 יומי", style=discord.ButtonStyle.primary, custom_id="stats_daily")
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_user.id:
            return await interaction.response.send_message("❌ רק מי שהפעיל את הפקודה יכול ללחוץ!", ephemeral=True)
        embed = self.create_stats_embed("daily", "היום", discord.Color.blue())
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="🗓️ שבועי", style=discord.ButtonStyle.success, custom_id="stats_weekly")
    async def weekly_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_user.id:
            return await interaction.response.send_message("❌ רק מי שהפעיל את הפקודה יכול ללחוץ!", ephemeral=True)
        embed = self.create_stats_embed("weekly", "השבוע", discord.Color.green())
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="📊 חודשי", style=discord.ButtonStyle.secondary, custom_id="stats_monthly")
    async def monthly_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_user.id:
            return await interaction.response.send_message("❌ רק מי שהפעיל את הפקודה יכול ללחוץ!", ephemeral=True)
        embed = self.create_stats_embed("monthly", "החודש", discord.Color.orange())
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="👑 שנתי", style=discord.ButtonStyle.danger, custom_id="stats_yearly")
    async def yearly_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_user.id:
            return await interaction.response.send_message("❌ רק מי שהפעיל את הפקודה יכול ללחוץ!", ephemeral=True)
        embed = self.create_stats_embed("yearly", "השנה", discord.Color.red())
        await interaction.response.edit_message(embed=embed)


# ==========================================
#             פקדת הסטטיסטיקות
# ==========================================
@bot.command(name="stats")
async def user_activity_stats(ctx, member: discord.Member = None):
    target = member or ctx.author
    view = StatsView(target)
    initial_embed = view.create_stats_embed("daily", "היום", discord.Color.blue())
    await ctx.send(embed=initial_embed, view=view)



# ... כאן נמצאים הלוגים בעברית שהדבקנו קודם (on_message_delete, on_voice_state_update וכו') ...

# שורות ההפעלה חייבות להיות האחרונות בהחלט בקובץ!
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("TOKEN"))

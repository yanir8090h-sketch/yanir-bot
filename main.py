import os, discord, asyncio, random, sqlite3
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# 🆔 מזהי רולים כלליים של השרת שלך:
STAFF_ROLE = 1520870990543065111       
MNG_ROLE = 1520870990564032614   
MEMBER_ROLE = 1520870990526021694       
VETERAN_ROLE_ID = 1521720542314780684  

# 🆔 מזהי ארבעת הרולים החדשים של החנות:
ROLE_MNG_SUPPORT = 1520802461306271825    # Manager Support
ROLE_EV_MNG = 1520807998505312431         # Event Manager
ROLE_SUP_TEAM = 1520870990535312431       # Support Team
ROLE_LEAK_TEAM = 1520870990505312430      # Leaks Team
STAFF_FRIEND_ROLE_ID = 1520870990526021694  # Staff Friend
STAFF_REQUEST_CHANNEL_ID = None  # אם תרצה, שנה ל-ID של חדר staff-request

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
    async def close(self, inter, btn): await inter.channel.delete()

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

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(TicketDropdown())

class ShopDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="👤 Manager Support (25,000 XP)", value="mng_sup:25000", emoji="👤", description="רכישת רול מנהל תמיכה בשרת"),
            discord.SelectOption(label="🎨 Event Manager (20,000 XP)", value="evt_mng:20000", emoji="🎨", description="רכישת רול מנהל איוונטים בשרת"),
            discord.SelectOption(label="🛠️ Support Team (15,000 XP)", value="sup_team:15000", emoji="🛠️", description="רכישת רול צוות תמיכה בשרת"),
            discord.SelectOption(label="👁️ Leaks Team (10,000 XP)", value="leak_team:10000", emoji="👁️", description="רכישת רול צוות הדלפות בשרת")
        ]
        super().__init__(placeholder="🛒 בחר את הרול שברצונך לקנות מתוך התפריט...", custom_id="shop_drop", options=options)

    async def callback(self, inter):
        item_id, price = self.values[0].split(":")
        price = int(price)
        
        if get_xp(inter.user.id) < price:
            return await inter.response.send_message(f"❌ אין לך מספיק נקודות XP לרכישת רול זה!", ephemeral=True)
        
        role_map = {
            "mng_sup": ROLE_MNG_SUPPORT,
            "evt_mng": ROLE_EV_MNG,
            "sup_team": ROLE_SUP_TEAM,
            "leak_team": ROLE_LEAK_TEAM
        }
        
        role = inter.guild.get_role(role_map[item_id])
        if not role:
            return await inter.response.send_message("❌ שגיאה: הרול שנבחר לא הוגדר נכון בקוד על ידי המנהל!", ephemeral=True)
            
        await inter.user.add_roles(role)
        new_bal = add_xp(inter.user.id, -price)
        await inter.response.send_message(f"🎉 תתחדש! הרכישה בוצעה בהצלחה וקיבלת את הרול: {role.name}! 🌟\nיתרת ה-XP החדשה שלך היא: `{new_bal:,} XP`", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(ShopDropdown())

class VeteranView(discord.ui.View):
    def __init__(self, days): super().__init__(timeout=None); self.days = days
    @discord.ui.button(label="🎖️ בקש לקבל רול ווטרן", style=discord.ButtonStyle.success, custom_id="claim_veteran")
    async def claim_vet(self, inter, button):
        r = inter.guild.get_role(VETERAN_ROLE_ID)
        if self.days >= 90: await inter.user.add_roles(r); await inter.response.send_message("🎉 מזל טוב! קיבלת את רול הווטרן! 🎖️", ephemeral=True)
        else: await inter.response.send_message(f"❌ חסרים לך עוד {90 - self.days} ימים.", ephemeral=True)

class VerifyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="✅ לחץ כאן לאימות", style=discord.ButtonStyle.success, custom_id="v_c")
    async def verify(self, inter, btn):
        r = inter.guild.get_role(MEMBER_ROLE); await inter.user.add_roles(r); await inter.response.send_message("🎉 אימות בוצע בהצלחה!", ephemeral=True)

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

@bot.event
async def on_ready():
    bot.add_view(TicketView()); bot.add_view(VerifyView()); bot.add_view(ShopView())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Slash command sync failed: {e}")
    print("Your Bot is officially live, logging and ready! 🚀")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.tree.command(name="ping", description="בדוק אם הבוט חי")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!", ephemeral=True)

@bot.command(name="xp")
async def xp_command(ctx, user: discord.Member = None):
    target = user or ctx.author
    await ctx.send(f"✨ יתרת ה-XP של {target.mention} היא: **{get_xp(target.id):,} XP**")

@bot.tree.command(name="xp", description="בדוק XP לעצמך או למישהו אחר")
async def slash_xp(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    await interaction.response.send_message(f"✨ יתרת ה-XP של {target.mention} היא: **{get_xp(target.id):,} XP**")

@bot.command(name="vt")
async def vt_command(ctx):
    jd = ctx.author.joined_at
    days = (datetime.now(jd.tzinfo) - jd).days
    emb = discord.Embed(title=f"🕸️ סטטוס הוותק שלך בשרת | {ctx.author.name}", color=0x2f3136)
    emb.add_field(name="📅 מתי נכנסת לשרת?", value=f"```text\n{jd.strftime('%d/%m/%Y')}\n```", inline=False)
    emb.add_field(name="⏳ לפני כמה זמן זה היה?", value=f"```text\n{days} ימים\n```", inline=False)
    await ctx.send(embed=emb)

@bot.tree.command(name="vt", description="הצג את סטטוס הוותק שלך")
async def slash_vt(interaction: discord.Interaction):
    jd = interaction.user.joined_at
    days = (datetime.now(jd.tzinfo) - jd).days
    emb = discord.Embed(title=f"🕸️ סטטוס הוותק שלך בשרת | {interaction.user.name}", color=0x2f3136)
    emb.add_field(name="📅 מתי נכנסת לשרת?", value=f"```text\n{jd.strftime('%d/%m/%Y')}\n```", inline=False)
    emb.add_field(name="⏳ לפני כמה זמן זה היה?", value=f"```text\n{days} ימים\n```", inline=False)
    await interaction.response.send_message(embed=emb)

@bot.command(name="sf")
async def sf_command(ctx, user: discord.Member = None):
    target = user or ctx.author
    role = ctx.guild.get_role(STAFF_FRIEND_ROLE_ID)
    if not role:
        await ctx.send("❌ לא נמצא רול Staff Friend בשרת.")
        return

    request_channel = ctx.channel
    if STAFF_REQUEST_CHANNEL_ID:
        request_channel = ctx.guild.get_channel(STAFF_REQUEST_CHANNEL_ID)
        if not request_channel:
            request_channel = ctx.channel

    embed = discord.Embed(
        title="📩 בקשת Staff Friend",
        description=f"{target.mention} ביקש/ה את הרול {role.name}",
        color=0x00ff00,
    )
    embed.add_field(name="מבקש", value=ctx.author.mention, inline=True)
    embed.add_field(name="מועמד", value=target.mention, inline=True)
    embed.set_footer(text="לחץ על אשר או דחה")

    await request_channel.send(embed=embed, view=StaffFriendApproveView(target, ctx.author, role))
    await ctx.send("📨 הבקשה נשלחה לצוות לאישור.")

@bot.tree.command(name="sf", description="בקש רול Staff Friend")
async def slash_sf(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    role = interaction.guild.get_role(1521762736944709742)
    if not role:
        await interaction.response.send_message("❌ לא נמצא רול Staff Friend בשרת.", ephemeral=True)
        return

    request_channel = interaction.channel
    if STAFF_REQUEST_CHANNEL_ID:
        request_channel = interaction.guild.get_channel(1521760013557694624)
        if not request_channel:
            request_channel = interaction.channel

    embed = discord.Embed(
        title="📩 בקשת Staff Friend",
        description=f"{target.mention} ביקש/ה את הרול {role.name}",
        color=0x00ff00,
    )
    embed.add_field(name="מבקש", value=interaction.user.mention, inline=True)
    embed.add_field(name="מועמד", value=target.mention, inline=True)
    embed.set_footer(text="לחץ על אשר או דחה")

    await request_channel.send(embed=embed, view=StaffFriendApproveView(target, interaction.user, role))
    await interaction.response.send_message("📨 הבקשה נשלחה לצוות לאישור.", ephemeral=True)

@bot.event
async def on_message(msg):
    if msg.author.bot or not msg.guild:
        return

    add_xp(msg.author.id, random.randint(15, 25))
    await bot.process_commands(msg)

        bot.run("DISCORD_TOKEN")

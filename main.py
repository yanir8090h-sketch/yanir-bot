yanir
yanir8090
Do Not Disturb
In voice





Direct Message

yanir bot
AKA
VCS BOT 1Voice Chat Server
Search yanir bot#5648

yanir bot chat
June 11, 2026

yanir bot
APP
 — 6/11/2026 3:47 PMThursday, June 11, 2026 3:47 PM
 חנות הרולים הרשמית של השרת
רכוש רולים יוקרתיים באמצעות נקודות ה-XP שצברת בצ'אט!

איך קונים?
חזור לצ'אט של השרת ורשום את הפקודה המתאימה מהרשימה למטה:
 1. רול ראשון
מחיר: 10,000 XP
פקודה בשרת: !buy level1
 2. רול שני
מחיר: 12,000 XP
פקודה בשרת: !buy level2
 3. רול שלישי
מחיר: 15,000 XP
פקודה בשרת: !buy level3
 4. רול רביעי
מחיר: 20,000 XP
פקודה בשרת: !buy level4

[3:50 PM]Thursday, June 11, 2026 3:50 PM
 חנות הרולים של השרת
רוצה לראות את הרולים, המחירים ולדעת מה אתה יכול לקנות?
לחץ על הכפתור הירוק למטה והחנות תיפתח אצלך בפרטי!
[3:51 PM]Thursday, June 11, 2026 3:51 PM
 חנות הרולים של השרת
רוצה לראות את הרולים, המחירים ולדעת מה אתה יכול לקנות?
לחץ על הכפתור הירוק למטה והחנות תיפתח אצלך בפרטי!
June 12, 2026

yanir [JEW], Server Tag: JEWJEW — 6/12/2026 8:11 PMFriday, June 12, 2026 8:11 PM
שם: @yanir 
שם המקבל: 
דרגה: 
עונש: 
סיבה: 
זמן: 
אחראים:

yanir [JEW], Server Tag: JEWJEW — 6/12/2026 11:24 PMFriday, June 12, 2026 11:24 PM
PythonAnywhere תכינות בוט אתר
June 13, 2026

yanir bot
APP
 — 6/13/2026 2:02 AMSaturday, June 13, 2026 2:02 AM
 חנות השרת
שלום @yanir, כאן תוכל לרכוש מוצרים עם נקודות ה-XP שלך.
צבעלשםזהב
500 XP
רול_VIP
1500 XP
תואר_אלוף
3000 XP

yanir [JEW], Server Tag: JEWJEW — 6/13/2026 2:03 AMSaturday, June 13, 2026 2:03 AM
רול_VIP
[2:03 AM]Saturday, June 13, 2026 2:03 AM
VIP
[2:03 AM]Saturday, June 13, 2026 2:03 AM
2

yanir [JEW], Server Tag: JEWJEW — 6/13/2026 4:41 PMSaturday, June 13, 2026 4:41 PM
טופס מועמדות לצוות השרת,
שם מלא (שלך) / כינוי בדיסקורד:,

2 . גיל:

3:כמה זמן אתה בשרת שלנו?

4: ניסיון קודם בצוות ניהול / מודרטור? ספר קצת.. ואם עזבת אז מדוע? (שלח הוכחה במידה ויש)

5: איך אתה מגדיר צוות טוב?מה בעינייך התכונות שצריכות להיות לחבר צוות?

6: בתור צוות, מה היית עושה במידה ויש סיטואציה פחות נעימה בחדרי השרת / הוויס,

מישהו מתחצף/ עובר על החוקים, ריבים בין כמה חברי השרת… תן דוגמה:

7: איך היית מגיב אם צוות מתחתיך תוקף אותך? ואיך היית מגיב אם הוא היה מעליך?

8: כמה זמן בערך אתה חושב שתוכל לתת ממך למען השרת בשבוע כל יום?

9: במידה והשרת מתחיל טיפה להראות חוסר פעילות האם לדעתך תוכל לשנות את המצב? איך?

10: באיזה תחומים אתה רוצה לעזור בשרת?

11:איך אתה חושב שתוכל לתרום לשרת, וכמה רחוק אתה חושב שתוכל להגיע?

12:מאיפה הרצון להצטרף לצוות?

13: למה דווקא אתה מתאים לצוות שלנו?

יש לך רעיון לשיפור השרת?

האם יש לך 2FA,
June 16, 2026

yanir [JEW], Server Tag: JEWJEW — 9:54 PMTuesday, June 16, 2026 9:54 PM
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio
class HelpButtonView(discord.ui.View):

Expand (292 lines)
message.txt
message.txt (15 KB)
15 KB
:white_check_mark:
Click to react
:heart:
Click to react
:thumbsup:
Click to react
Add Reaction
Edit
Forward
More

Message @yanir bot
﻿
yanir bot's profile

yanir bot 
APP
yanir bot
#5648

Supports Commands
Created On
Mar 9, 2026
Mutual Servers — 1
View Full Profile
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio
class HelpButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\u05d8\u05e4\u05dc \u05db\u05d0\u05df \u2694\ufe0f", style=discord.ButtonStyle.success, custom_id="take_help_call")
    async def take_call(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        
        embed.set_field_at(2, name="\u05e0\u05dc\u05e7\u05d7 \u05e2\u05dc \u05d9\u05d3\u05d9 \u2694\ufe0f", value=f"{interaction.user.mention}", inline=False)
        embed.color = discord.Color.green()
        
        button.disabled = True
        button.label = "\u05d1\u05d8\u05d9\u05e4\u05d5\u05dc \ud83d\udee0\ufe0f"
        button.style = discord.ButtonStyle.secondary

        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"\u2694\ufe0f {interaction.user.mention} \u05dc\u05e7\u05d7 \u05d0\u05ea \u05d4\u05e7\u05e5 \u05dc\u05d8\u05d9\u05e4\u05d5\u05dc\u05df!", ephemeral=False)


הגדרת הרשאות הבוט לקריאת הודעות ותוכן
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# הגדרות ומשתנים קבועים של השרת שלך
# ==========================================
ROLE_1_ID = 1484226514051665930  # רול 1 - 30,000
ROLE_2_ID = 1491063689502003360  # רול 2 - 20,000
ROLE_3_ID = 1490894966262726687 # שלישי - 10,000
ROLE_4_ID = 1490894895618195577  # רביעי - 5,000
ROLE_5_ID = 1490894817373196388  # חמישי - 2,500

STAFF_ROLE_ID = 1488259168593772554  # ID של תפקיד הצוות לניהול
STAFF_FRIENDS_LOG_CHANNEL_ID = 1499531407859388496  # ערוץ לוגים לבקשות סגל

# ==========================================
# מערכת Staff Friend מעוצבת אחד לאחד כמו בתמונה
# ==========================================
class StaffFriendReview(discord.ui.View):


    @discord.ui.button(label="Accept 🟢", style=discord.ButtonStyle.green, custom_id="staff_friend_accept_persistent")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        role = discord.utils.get(guild.roles, name="Staff Friend")
        
        if not role:
            role = await guild.create_role(name="Staff Friend")

        if member:
            await member.add_roles(role)
            embed = interaction.message.embeds
            embed.color = discord.Color.green()
            embed.set_field_at(0, name="🟢 אושר:", value="🟢", inline=True)
            embed.set_field_at(1, name="🛡️ אושר על ידי:", value=interaction.user.mention, inline=True)
            embed.set_field_at(2, name="⏰ זמן טיפול:", value=discord.utils.format_dt(discord.utils.utcnow()), inline=False)
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message(f"✅ אישרת את הבקשה של {member.mention} והרול הוענק!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ המשתמש כבר לא נמצא בשרת.", ephemeral=True)

    @discord.ui.button(label="Deny ❌", style=discord.ButtonStyle.red, custom_id="staff_friend_deny_persistent")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds
        embed.color = discord.Color.red()
        embed.set_field_at(0, name="🔴 נדחה:", value="🔴", inline=True)
        embed.set_field_at(1, name="🛡️ נדחה על ידי:", value=interaction.user.mention, inline=True)
        embed.set_field_at(2, name="⏰ זמן טיפול:", value=discord.utils.format_dt(discord.utils.utcnow()), inline=False)
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("❌ הבקשה נדחתה בהצלחה.", ephemeral=True)

@bot.command()
async def apply_staff_friend(ctx):
    log_channel = bot.get_channel(STAFF_FRIENDS_LOG_CHANNEL_ID)
    if not log_channel:
        await ctx.send("❌ ערוץ הלוגים של המערכת לא הוגדר כראוי בקוד.", ephemeral=True)
        return
    try: await ctx.message.delete()
    except discord.NotFound: pass

    embed = discord.Embed(title="⚙️ בקשת Staff Friend", color=discord.Color.from_rgb(47, 49, 54))
    embed.add_field(name="👤 איש צוות:", value=ctx.author.mention, inline=True)
    embed.add_field(name="👥 חבר מקבל:", value="@unknown-user", inline=True)
    embed.add_field(name="📅 זמן השליחה:", value=discord.utils.format_dt(ctx.message.created_at), inline=False)
    embed.add_field(name="📊 בקשות שהוגשו בזמן השליחה:", value="1/1", inline=False)
    embed.add_field(name="🟡 סטטוס:", value="ממתין לטיפול...", inline=False)
    embed.set_image(url="https://discordapp.net")
    
    await log_channel.send(embed=embed, view=StaffFriendReview(ctx.author.id))
    await ctx.send("✅ בקשתך נשלחה בהצלחה לבדיקת צוות הניהול!", ephemeral=True)

# ==========================================
# פקודת !xp בעיצוב כרטיס שחור ומיושר
# ==========================================
@bot.command()
async def xp(ctx, member: discord.Member = None):
    try: await ctx.message.delete()
    except discord.NotFound: pass
    if member is None: member = ctx.author
    guild = ctx.guild
    embed = discord.Embed(title="📊 מידע XP והתקדמות", color=discord.Color.from_rgb(47, 49, 54))
    embed.add_field(name="👤 משתמש:", value=member.mention, inline=True)
    embed.add_field(name="⭐ רמה נוכחית:", value="`Level 5`", inline=True)
    embed.add_field(name="📈 נקודות XP:", value="`1,500 / 3,000 XP`", inline=False)
    embed.add_field(name="🏅 מיקום בשרת:", value="`Rank #1`", inline=False)
    if guild.icon: embed.set_image(url=guild.icon.url)
    await ctx.send(embed=embed)

# ==========================================
# פקודת העזרה המעוצבת המוכרת (!h) החדשה עם הבאנר הסגול
# ==========================================
@bot.command(name="h")
async def help_ticket_info(ctx, *, reason: str = "לא צוינה סיבה"):
    try: await ctx.message.delete()
    except discord.NotFound: pass
    guild = ctx.guild
    embed = discord.Embed(title="⚙️ בקשת עזרה", color=discord.Color.from_rgb(47, 49, 54))
    embed.add_field(name="👥 צוות מתוייג:", value=f"<@&{STAFF_ROLE_ID}>", inline=True)
    embed.add_field(name="📝 סיבה:", value=f"`{reason}`", inline=True)
    embed.add_field(name="📅 זמן פתיחה:", value=discord.utils.format_dt(ctx.message.created_at), inline=False)
    embed.add_field(name="🌐 וייס / מיקום:", value="🔈 `(🔒) Private Voice`", inline=False)
    embed.add_field(name="🔒 נלקח לטיפול על ידי:", value=f"{ctx.author.mention} · <@&{ROLE_3_ID}>", inline=False)
    embed.set_image(url="https://discordapp.net")
    await ctx.send(embed=embed)

# ==========================================
# פקודות הניהול המעוצבות לעבודה מכל ערוץ
# ==========================================
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_shop(ctx, target_channel: discord.TextChannel = None):
    try: await ctx.message.delete()
    except discord.NotFound: pass
    channel_to_send = target_channel if target_channel else ctx.channel
    guild = ctx.guild
    embed = discord.Embed(
        title=f"🎁 חנות ה-XP הרשמית - {guild.name}",
        description=f"🛍️ **חנות הרולים של השרת**\n\n👑 <@&{ROLE_1_ID}> — 30,000 XP\n"
                    f"💎 <@&{ROLE_2_ID}> — 20,000 XP\n"
                    f"🔥 <@&{ROLE_3_ID}> — 10,000 XP\n"
                    f"⚡ <@&{ROLE_4_ID}> — 5,000 XP\n"
                    f"✨ <@&{ROLE_5_ID}> — 2,500 XP",
        color=discord.Color.from_rgb(142, 201, 57)
    )
    if guild.icon: embed.set_image(url=guild.icon.url)
    await channel_to_send.send(embed=embed, view=ShopView())



@commands.has_permissions(administrator=True)
async def setup_verify(ctx, target_channel: discord.TextChannel = None):
    try: await ctx.message.delete()
    except discord.NotFound: pass
    channel_to_send = target_channel if target_channel else ctx.channel
    embed = discord.Embed(title="🔒 אימות חשבון - Verification", description="ברוך הבא לשרת!\nכדי לקבל גישה לשאר הערוצים, לחץ על הכפתור הירוק למטה.", color=discord.Color.green())
    if ctx.guild.icon: embed.set_thumbnail(url=ctx.guild.icon.url)
    await channel_to_send.send(embed=embed, view=VerifyView())

# ==========================================
# הפעלת ה-Views הקבועים ואירועים קריטיים
# ==========================================
@bot.event
async def on_ready():
    bot.add_view(ShopView())
    bot.add_view(TicketView())
    bot.add_view(TicketDropdownView())
    bot.add_view(VerifyView())
    bot.add_view(StaffFriendReview(0))
    print(f'🤖 הבוט מחובר בהצלחה כאל: {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)

# ==========================================
# קוד Flask לשמירה על הבוט דלוק בחינם ב-Render
# ==========================================
app = Flask('')

@app.route('/')
def home(): return "הבוט דלוק ובאוויר!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
# ==========================================
# מערכת הטיקטים המלאה - עם כפתור לקיחה וסגירה
# ==========================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # כפתור לקיחת הטיקט המעוצב בסטייל של השרת שלך
    @discord.ui.button(label="טפל כאן 🔓", style=discord.ButtonStyle.green, custom_id="claim_ticket_persistent")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        global STAFF_ROLE_ID
        
        # בדיקה האם המשתמש שלחץ הוא אכן איש צוות
        if STAFF_ROLE_ID:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff_role and staff_role not in interaction.user.roles:
                await interaction.response.send_message("❌ שגיאה: רק אנשי צוות מורשים לטפל בטיקט זה!", ephemeral=True)
                return
                
        # שינוי שם הערוץ והודעה חגיגית שהטיקט בטיפול
        await interaction.channel.edit(name=f"🔒-בטיפול-{interaction.user.name}")
        
       # ==========================================
# פקודות הניהול המעוצבות לעבודה מכל ערוץ
# ==========================================

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx, target_channel: discord.TextChannel = None):
    """פקודת טיקטים - מריצים כך: setup_ticket #ערוץ_הטיקטים!"""
    try: await ctx.message.delete()
    except discord.NotFound: pass
    channel_to_send = target_channel if target_channel else ctx.channel
    
    embed = discord.Embed(
        title="תמיכה טכנית 🎫", 
        description="בחר את סוג הפנייה שברצונך לפתוח מתוך תפריט הבחירה שלמטה.\nצוות המנהלים יתפנה אליך בהקדם האפשרי!", 
        color=discord.Color.from_rgb(47, 49, 54)
    )
    if ctx.guild.icon: embed.set_image(url=ctx.guild.icon.url)
    await channel_to_send.send(embed=embed, view=TicketDropdownView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_verify(ctx, target_channel: discord.TextChannel = None):
    """פקודת אימות - מריצים כך: setup_verify #ערוץ_האימות!"""
    try: await ctx.message.delete()
    except discord.NotFound: pass
    channel_to_send = target_channel if target_channel else ctx.channel
    
    embed = discord.Embed(
        title="🔒 אימות חשבון - Verification", 
        description="ברוך הבא לשרת!\nכדי לקבל גישה לשאר הערוצים, לחץ על הכפתור הירוק למטה.", 
        color=discord.Color.green()
    )
    if ctx.guild.icon: embed.set_thumbnail(url=ctx.guild.icon.url)
    await channel_to_send.send(embed=embed, view=VerifyView())

# ==========================================
# הפעלת ה-Views הקבועים ואירועים קריטיים
# ==========================================
@bot.event
async def on_ready():
    # רישום מאוחד ומלא של כל ה-Views כדי שיעבדו קבוע בשרת לתמיד!
    bot.add_view(ShopView())
    bot.add_view(TicketView())
    bot.add_view(TicketDropdownView())
    bot.add_view(VerifyView())
    bot.add_view(StaffFriendReview(0))
    print(f'🤖 הבוט מחובר בהצלחה ומפעיל את כל הכפתורים כאל: {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot: return
    # משחרר את החסימה ומבטיח שכל פקודה בשרת תענה מיידית
    await bot.process_commands(message)

# ==========================================
# קוד Flask לשמירה על הבוט דלוק בחינם ב-Render
# ==========================================
app = Flask('')

@app.route('/')
def home(): return "הבוט דלוק ובאוויר!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

import os
bot.run(os.getenv("DISCORD_TOKEN"))




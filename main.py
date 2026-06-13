import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio

# הגדרת הרשאות הבוט לקריאת הודעות ותוכן
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

STAFF_ROLE_ID = 1485440480459227227  # ID של תפקיד הצוות לניהול
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

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx, target_channel: discord.TextChannel = None):
    try: await ctx.message.delete()
    except discord.NotFound: pass
    channel_to_send = target_channel if target_channel else ctx.channel
    embed = discord.Embed(title="תמיכה טכנית 🎫", description="בחר את סוג הפנייה שברצונך לפתוח מתוך תפריט הבחירה שלמטה.\nצוות המנהלים יתפנה אליך בהקדם האפשרי!", color=discord.Color.from_rgb(47, 49, 54))
    if ctx.guild.icon: embed.set_image(url=ctx.guild.icon.url)
    await channel_to_send.send(embed=embed, view=TicketDropdownView())

@bot.command()
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
import os
bot.run(os.getenv("DISCORD_TOKEN"))

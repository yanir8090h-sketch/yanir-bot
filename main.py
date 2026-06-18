import discord
import os
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio
import random
import io
from easy_pil import Editor, Canvas, load_image, Font

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

# הגדרות השרת והאינטנטים
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

# הגדרת משתנים ורולים
ROLE_1_ID = 1434226514051665920 
ROLE_2_ID = 1434236285220202100 
ROLE_3_ID = 1434023456252726607 
ROLE_4_ID = 1434023485618195577 
ROLE_5_ID = 1434034812251396305 

STAFF_ROLE_ID = 1484235285220202100 
STAFF_FRIENDS_LOG_CHANNEL_ID = 1434311487832883406 

class StaffFriendReview(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept ✅", style=discord.ButtonStyle.green, custom_id="staff_friend_accept_persistent")
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
            embed.set_field_at(0, name="סטטוס:", value="אושר ✅", inline=True)
            embed.set_field_at(1, name="מאשר:", value=interaction.user.mention, inline=True)
            embed.set_field_at(2, name="זמן אישור:", value=discord.utils.format_dt(discord.utils.utcnow()), inline=False)
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message(f"המשתמש {member.mention} פתח חבר צוות!", ephemeral=True)
        else:
            await interaction.response.send_message("המשתמש לא נמצא בשרת.", ephemeral=True)

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
    #try: await ctx.message.delete()
    #except discord.NotFound: pass

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
#@bot.command()
#async def apply_staff_friend2(ctx):2
   #except discord.NotFound: pass
    #if member is None: member = ctx.author
    #guild = ctx.guild
    #embed = discord.Embed(title="📊 מידע XP והתקדמות", color=discord.Color.from_rgb(47, 49, 54))
    #embed.add_field(name="👤 משתמש:", value=member.mention, inline=True)
    #embed.add_field(name="⭐ רמה נוכחית:", value="`Level 5`", inline=True)
    #embed.add_field(name="📈 נקודות XP:", value="`1,500 / 3,000 XP`", inline=False)
    #embed.add_field(name="🏅 מיקום בשרת:", value="`Rank #1`", inline=False)
    #if guild.icon: embed.set_image(url=guild.icon.url)
    #await ctx.send(embed=embed)



# =================================================================
# 🛒 פקודת הקמת חנות ה-XP
# =================================================================
@bot.command(name="myshop")
@commands.has_permissions(administrator=True)
async def myshop(ctx, target_channel: discord.TextChannel = None):
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"🛒 חנות ה-XP של השרת - {guild.name}",
        description=(
            "ברוכים הבאים לחנות! כאן תוכלו לבזבז את נקודות ה-XP שלכם על רולים שווים:\n\n"
            "• **רול 10K XP** ➔ עלות: 10,000 XP\n"
            "• **רול 18K XP** ➔ עלות: 18,000 XP\n"
            "• **רול 28K XP** ➔ עלות: 28,000 XP"
        ),
        color=discord.Color.from_rgb(142, 203, 57)
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        
    #try:
        #await channel_to_send.send(embed=embed, view=ShopDropdownView())
    #except NameError:
        #await channel_to_send.send(embed=embed, view=View())
    await channel_to_send.send(embed=embed)
# =================================================================
# 📩 פקודת הקמת מערכת האימות (Verify)
# =================================================================
@bot.command(name="myverify")
@commands.has_permissions(administrator=True)
async def myverify_cmd(ctx, target_channel: discord.TextChannel = None):
    channel_to_send = target_channel if target_channel else ctx.channel
    guild = ctx.guild
    
    embed = discord.Embed(
        title="🛡️ מערכת אימות ואישור כניסה 🛡️",
        description="ברוכים הבאים! כדי לקבל גישה לשאר ערוצי השרת, אנא לחצו על כפתור האימות למטה.",
        color=discord.Color.green()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        
    #try:
     #await channel_to_send.send(embed=embed, view=View())
    #except NameError:
       #await channel_to_send.send(embed=embed)
    await channel_to_send.send(embed=embed)
# =================================================================
# ⚠️ פקודת עזרה ותמיכה (!h) המעוצבת של מאסטר אוהד
# =================================================================
#@bot.command(name="bot_help", aliases=["h"])
#async def help_call_custom(ctx):
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"⚠️ מרכז התמיכה והעזרה - {guild.name} ⚠️",
        description=(
            "שלום חברים! נתקלתם בבעיה, שגיאה, או שאתם זקוקים לעזרת צוות הניהול המורחב?\n"
            "הגעתם למקום הנכון. אנו זמינים עבורכם לכל פנייה, שאלה או בקשת עזרה בשרת.\n\n"
            "**💡 דגשים חשובים לפני פתיחת פנייה:**\n"
            "• נא לשמור על שפה מכבדת מול חברי הסטאף.\n"
            "• אין לפתוח טיקטים סתם ללא סיבה מוצדקת.\n"
            "• צוות השרת עושה את מירב המאמצים לענות במהירות האפשרית."
        ),
        color=discord.Color.from_rgb(47, 49, 54)
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        
    embed.add_field(name="⏰ שעות פעילות הטיקטים", value="```24/7 - בהתאם לזמינות הצוות```", inline=False)
    embed.add_field(name="🛡️ בורר פניות אוטומטי", value="לאחר לחיצה על הכפתור, ייפתח לכם חדר אישי ומאובטח.", inline=False)
    embed.set_footer(text=f"MasterOhad Network • כל הזכויות שמורות")
    
    #try:
      #await ctx.send(embed=embed, view=TicketView())
   #except NameError:
      #    await ctx.send(embed=embed)
   
    #print(f' {bot.user.name} is online and fully synced!')
    await ctx.send(embed=embed)
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

# ==========================================
# מערכת 3 כפתורי טיקטים משולבת (לפי רולים)
# ==========================================
ADMIN_TICKET_ROLE_ID = 1485440480459227227  # רול הנהלה גבוהה
STAFF_EXAM_ROLE_ID = 1485440385206456452    # רול בוחני צוות
GENERAL_STAFF_ROLE_ID = 1488259168593772554 # רול צוות כללי

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # 1. כפתור בחינות לצוות
    @discord.ui.button(label="בחינות לצוות 📝", style=discord.ButtonStyle.primary, custom_id="btn_staff_exam")
    async def staff_exam(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffModalPart1())

    # 2. כפתור עזרה מצוות
    @discord.ui.button(label="עזרה מצוות 🛠️", style=discord.ButtonStyle.success, custom_id="btn_general_help")
    async def general_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(GENERAL_STAFF_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(name=f"עזרה-{user.name}", overwrites=overwrites)
        embed = discord.Embed(
            title="🛠️ פנייה לצוות התמיכה",
            description=f"שלום {user.mention},\nפתחת פנייה לצוות הכללי. נציג מתוך <@&{GENERAL_STAFF_ROLE_ID}> יתפנה אלייך בהקדם.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ הטיקט שלך נפתח! כנס לערוץ: {channel.mention}", ephemeral=True)

    # 3. כפתור עזרה מהנהלה
    @discord.ui.button(label="עזרה מהנהלה ⚠️", style=discord.ButtonStyle.danger, custom_id="btn_admin_help")
    async def admin_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(ADMIN_TICKET_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(name=f"הנהלה-{user.name}", overwrites=overwrites)
        embed = discord.Embed(
            title="⚠️ פנייה חסויה להנהלה הגבוהה",
            description=f"שלום {user.mention},\nפנייתך חסויה ורגישה. רק חברי <@&{ADMIN_TICKET_ROLE_ID}> יכולים לצפות בה. אנא רשום את סיבת הפנייה.",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ טיקט הנהלה נפתח! כנס לערוץ: {channel.mention}", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx, target_channel: discord.TextChannel = None):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    channel_to_send = target_channel if target_channel else ctx.channel
    embed = discord.Embed(
        title=f"🎫 מרכז פניות ותמיכה - {ctx.guild.name}",
        description=(
            "ברוכים הבאים למרכז העזרה הרשמי של השרת.\n"
            "על מנת לקבל מענה מדויק, לחצו על הכפתור המתאים לכם ביותר:\n\n"
            "📝 **בחינות לצוות** ➔ לפתיחת שאלון הגשת מועמדות לשרת.\n"
            "🛠️ **עזרה מצוות** ➔ לפתיחת פנייה כללית בנושאי תמיכה וקהילה.\n"
            "⚠️ **עזרה מהנהלה** ➔ לפתיחת פנייה חסויה ודחופה מול ההנהלה הגבוהה."
        ),
        color=discord.Color.from_rgb(47, 49, 54)
    )
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
    await channel_to_send.send(embed=embed, view=TicketView())


        
    await channel_to_send.send(embed=embed, view=TicketView())


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_verify(ctx, target_channel: discord.TextChannel = None):
    """פקודה להקמת מערכת אימות עם ה-ID הנכון ותמונה גדולה"""
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
        
    channel_to_send = target_channel if target_channel else ctx.channel
    
    embed = discord.Embed(
        title=f"✅ אימות חברים - {ctx.guild.name}",
        description=(
            "ברוכים הבאים לשרת! על מנת לבצע אימות ולקבל גישה, לכל ערוצי השרת:\n\n"
            "**📜 חוקים בסיסיים:**\n"
            "• כבדו את כל חברי השרת\n"
            "• אין ספאם או פלוד\n"
            "• עקבו אחר הוראות הצוות\n\n"
            "• קראו את ערוץ <#1483920420414554272> לפני שאתם מתחילים"
        ),
        color=discord.Color.green()
    )
    
    # מציג את תמונת השרת שלך כתמונה גדולה
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
        
    await channel_to_send.send(embed=embed, view=TicketView())

    embed = discord.Embed(
        title="✅ מערכת אימות - Verification",
        description="ברוכים הבאים לשרת! כדי לקבל גישה לשאר הערוצים, לחצו על הכפתור למטה.",
        color=discord.Color.green()
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
        
    # שינוי כאן: שימוש ב-TicketView() הקיים בקוד שלך במקום ב-VerifyView הלא קיים
    await channel_to_send.send(embed=embed, view=TicketView())

# ==========================================
# הפעלת ה-Views הקבועים ואירועים קריטיים
# ==========================================
@bot.event
async def on_ready():
    # סנכרון פקודות הסלאש (חובה בשביל פקודת /sf שביקשת!)
    await bot.tree.sync()
    
    # הפעלה בטוחה של ה-views ללא קריסות
    try:
        bot.add_view(TicketView())
    except:
        pass
        
    try:
        bot.add_view(StaffFriendReview())
    except:
        pass
        
    print(f' {bot.user.name} is online and fully synced!')


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
@bot.command(name="staff")
async def staff_shortcut(ctx, *, message: str = None):
    if message is None:
        await ctx.send("❌ נא לכתוב את הפירוט של הבקשה. דוגמה: `!staff אני רוצה להגיש מועמדות לצוות`")
        return
    # --- מערכת כפתורי אישור/דחייה לרול Staff Friend ---
class StaffButtons(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Accept | אישור", style=discord.ButtonStyle.success, custom_id="accept_staff")
    async def accept_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # בדיקה האם הלוחץ הוא מנהל (בעל הרשאת ניהול שרת או ניהול רולים)
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ אין לך הרשאה לאשר בקשות צוות!", ephemeral=True)
            return

        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        
        # מחפש את הרול בשרת לפי השם שלו (שנה את השם אם הוא שונה אצלך בשרת)
        role = discord.utils.get(guild.roles, name="Staff Friend")
        
        if not role:
            await interaction.response.send_message("❌ השגיאה: הרול 'Staff Friend' לא נמצא בשרת. ודא שהשם מדויק!", ephemeral=True)
            return

        if member:
            await member.add_roles(role)
            
            # עדכון האמבד שהבקשה אושרה
            embed = interaction.message.embeds[0]
            embed.title = "✅ הבקשה אושרה!"
            embed.color = discord.Color.green()
            embed.add_field(name="סטטוס:", value=f"אושר על ידי {interaction.user.mention} והרול הוענק.", inline=False)
            
            

 # --- מערכת כפתורי אישור/דחייה לפקודת /sf ---
class SFApprovalButtons(discord.ui.View):
    def __init__(self, target_member_id: int):
        super().__init__(timeout=None)
        self.target_member_id = target_member_id

    @discord.ui.button(label="Accept | אשר", style=discord.ButtonStyle.success, custom_id="sf_accept_btn")
    async def accept_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # בדיקה שללחוץ יש הרשאה לנהל רולים
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ אין לך הרשאה לאשר את הרולים האלו!", ephemeral=True)
            return

        guild = interaction.guild
        member = guild.get_member(self.target_member_id)
        
        # שליפת הרולים מהשרת (סטאף פרנד לפי ID וממבר לפי שם)
        staff_friend_role = guild.get_role(1493335218004820180)
        member_role = discord.utils.get(guild.roles, name="Member")
        
        if not staff_friend_role or not member_role:
            await interaction.response.send_message("❌ שגיאה: אחד מהרולים ('Member' או ID של Staff Friend) לא נמצא בשרת.", ephemeral=True)
            return

        if member:
            try:
                # הענקת שני הרולים ביחד
                await member.add_roles(member_role, staff_friend_role)
                
                # עדכון ההודעה בערוץ שהבקשה אושרה
                embed = interaction.message.embeds[0]
                embed.title = "✅ החברות בצוות אושרה!"
                embed.color = discord.Color.green()
                embed.add_field(name="סטטוס:", value=f"אושר בהצלחה על ידי {interaction.user.mention}. הרולים הוענקו!", inline=False)
                
                # נטרול הכפתורים שלא יהיה כפל לחיצות
                for child in self.children:
                    child.disabled = True
                    
                await interaction.message.edit(embed=embed, view=self)
                await interaction.response.send_message(f"🎉 הרולים הוענקו בהצלחה ל-{member.mention}!", ephemeral=True)
                
                # שליחת הודעה פרטית למשתמש
                try:
                    await member.send(f"✨ שמחים לעדכן שאושרת! קיבלת את הרולים **Member** ו-**Staff Friend** בשרת {guild.name}!")
                except:
                    pass
            except discord.Forbidden:
                await interaction.response.send_message("❌ שגיאה: לבוט אין הרשאה לשים את הרולים. גרור את הרול שלו לראש הרשימה!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ המשתמש כבר לא נמצא בשרת.", ephemeral=True)

    @discord.ui.button(label="Deny | דחה", style=discord.ButtonStyle.danger, custom_id="sf_deny_btn")
    async def deny_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ אין לך הרשאה לדחות את הבקשה!", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.title = "❌ הבקשה נדחתה"
        embed.color = discord.Color.red()
        embed.add_field(name="סטטוס:", value=f"הבקשה נדחתה על ידי {interaction.user.mention}.", inline=False)
        
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("הבקשה נדחתה בהצלחה.", ephemeral=True)

# --- פקודת הסלאש המקורית ששולחת את הכפתורים ---
@bot.tree.command(name="sf", description="שליחת בקשת אישור לרולים Member ו-Staff Friend")
@discord.app_commands.describe(member="המשתמש שברצונך להעניק לו את הרולים לאחר אישור")
async def sf_command(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ פקודה זו מיועדת לצוות הניהול בלבד!", ephemeral=True)
        return

    guild = interaction.guild
    
    # יצירת ההודעה המעוצבת עם הכפתורים
    embed = discord.Embed(
        title="❓ בקשת אישור דרגה חדשה",
        description=f"האם להעניק למשתמש {member.mention} את הרולים שלו?",
        color=discord.Color.orange()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        
    embed.add_field(name="הרולים המיועדים:", value="• Member\n• Staff Friend", inline=False)
    embed.add_field(name="נשלח על ידי:", value=interaction.user.mention, inline=False)
    embed.set_footer(text=f"User ID: {member.id} • {guild.name}")
    
    # הצמדת הכפתורים להודעה
    view = SFApprovalButtons(target_member_id=member.id)
    await interaction.response.send_message(embed=embed, view=view)

    
    # שליפת הרולים מהשרת (סטאף פרנד לפי ID וממבר לפי שם)
    staff_friend_role = guild.get_role(1493335218004820180)
    member_role = discord.utils.get(guild.roles, name="Member")
    
    # בדיקה אם הרולים קיימים בשרת
    if not staff_friend_role:
        await interaction.response.send_message("❌ שגיאה: רול ה-Staff Friend לא נמצא בשרת באמצעות ה-ID שסופק.", ephemeral=True)
        return
        
    if not member_role:
        await interaction.response.send_message("❌ שגיאה: הרול בשם 'Member' לא נמצא בשרת. ודא שהשם שלו מדויק!", ephemeral=True)
        return




class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="טפל כאן 🛠️", style=discord.ButtonStyle.success, custom_id="handle_help_btn")
    async def handle_here(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_mention = f"<@&{1488259168593772554}>"
        user_mention = interaction.user.mention
        await interaction.channel.send(f"🔔 {staff_mention}, המשתמש {user_mention} ביקש עזרה כאן!")
        await interaction.response.send_message("✅ בקשת העזרה נשלחה לצוות, מייד יתפנו אלייך.", ephemeral=True)


@bot.command(name="help_call", aliases=["h"])
async def help_call_custom(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"⚠️ מרכז התמיכה והעזרה - {guild.name} ⚠️",
        description=(
            "שלום חברים! נתקלתם בבעיה, שגיאה, או שאתם זקוקים לעזרה כלשהי?\n"
            "הגעתם למקום הנכון. אנו זמינים עבורכם לכל פנייה, שאלה או בקשת עזרה רשתית.\n\n"
            "**💡 מידע על כל הפקודות:**\n"
            "• ניתן ללחוץ על הכפתור למטה כדי להזעיק תמיכה.\n"
            "• נציג מהצוות יתייג את עצמו ויטפל בכם מיד."
        ),
        color=discord.Color.from_rgb(47, 49, 54)
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.set_footer(text=f"בקשה נשלחה על ידי: {ctx.author.name} • {guild.name}")
    await ctx.send(embed=embed, view=HelpView())

# --- פקדת ה-XP המעוצבת ---
@bot.command(name="xp", aliases=["rank"])
async def xp_card_command(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_xp = 7681  
    user_level = 31 
    next_level_xp = 10000 
    percentage = int((user_xp / next_level_xp) * 100)
    
    background = Canvas(shape=(900, 250), color="#2f3136")
    editor = Editor(background)
    avatar_image = load_image(member.display_avatar.url)
    editor.avatar(avatar_image, position=(50, 50), size=(150, 150), circle=True)
    
    editor.text((240, 60), f"◆ IN|★{member.name}★", color="#ffffff", font=Font.poppins(size=35, variant="bold"))
    editor.text((240, 120), f"XP: {user_xp:,} / {next_level_xp:,}", color="#aaaaaa", font=Font.poppins(size=25))
    editor.text((240, 160), f"רמה: {user_level}", color="#ffaa00", font=Font.poppins(size=28, variant="bold"))
    
    editor.bar(position=(240, 200), max_width=600, height=20, percentage=percentage, fill="#ffaa00", background="#4f545c")
    file = discord.File(fp=editor.image_bytes, filename="xp_card.png")
    await ctx.send(file=file)

# --- משחקי XP ---
@bot.command(name="rps", aliases=["rock", "paper", "scissors"])
async def rps_game(ctx, choice: str = None):
    if not choice or choice.lower() not in ["אבן", "נייר", "מספריים"]:
        return await ctx.send("❌ נא לבחור: `!rps אבן`, `!rps נייר` או `!rps מספריים`")
    bot_choice = random.choice(["אבן", "נייר", "מספריים"])
    user_choice = choice.lower()
    if user_choice == bot_choice:
        await ctx.send("🤝 תיקו! שנינו בחרנו את אותו הדבר.")
    elif (user_choice == "אבן" and bot_choice == "מספריים") or (user_choice == "נייר" and bot_choice == "אבן") or (user_choice == "מספריים" and bot_choice == "נייר"):
        await ctx.send(f"🎉 ניצחת! בחרת {user_choice} ואני בחרתי {bot_choice}. זכית!")
    else:
        await ctx.send(f"😢 הפסדת! בחרת {user_choice} ואני בחרתי {bot_choice}.")

@bot.command(name="guess", aliases=["g"])
async def guess_game(ctx, number: int = None):
    if not number or number < 1 or number > 5:
        return await ctx.send("❌ נא לנחש מספר בין 1 ל-5! דוגמה: `!guess 3`")
    secret_number = random.randint(1, 5)
    if number == secret_number:
        await ctx.send(f"🎯 בול! המספר היה {secret_number}. זכית!")
    else:
        await ctx.send(f"❌ פספוס! ניחשת {number} אבל המספר האמיתי היה {secret_number}.")

@bot.command(name="football", aliases=["fb", "goal"])
async def football_game(ctx, direction: str = None):
    if not direction or direction not in ["ימין", "שמאל", "אמצע"]:
        return await ctx.send("⚽ לאן לבעוט? תבחר: `!football ימין`, `!football שמאל` או `!football אמצע`")
    gk_jump = random.choice(["ימין", "שמאל", "אמצע"])
    if direction == gk_jump:
        await ctx.send(f"🧤 השוער זינק ל{gk_jump} והדף את הכדור! אין גול.")
    else:
        await ctx.send(f"⚽ GOAL!! השוער זינק ל{gk_jump} ואתה הבקעת ל{direction}! זכית!")

@bot.command(name="blackjack", aliases=["bj"])
async def blackjack_game(ctx, amount: int = 0):
    user_card1 = random.randint(1, 11)
    user_card2 = random.randint(1, 10)
    user_total = user_card1 + user_card2
    bot_total = random.randint(15, 22)
    if user_total > 21:
        await ctx.send(f"💥 נשרפת! הקלפים שלך: {user_card1} + {user_card2} = {user_total}. הפסדת.")
    elif bot_total > 21 or user_total > bot_total:
        await ctx.send(f"🃏 ניצחת בבלאקג'ק! לך יש {user_total} ולבוט יש {bot_total}. זכית!")
    elif user_total == bot_total:
        await ctx.send(f"🤝 תיקו! לשניכם יש {user_total}.")
    else:
        await ctx.send(f"😢 הפסדת! לך יש {user_total} ולבוט יש {bot_total}.")

@bot.command(name="gamble", aliases=["gift"])
async def gamble_gift(ctx, box: int = None):
    if not box or box < 1 or box > 3:
        return await ctx.send("🎁 יש 3 קופסאות. נחש איפה המתנה: `!gamble 1`, `!gamble 2` או `!gamble 3`")
    gift_box = random.randint(1, 3)
    if box == gift_box:
        await ctx.send(f"🎉 מצאת את המתנה בקופסה {gift_box}! זכית!")
    else:
        await ctx.send(f"📦 קופסה ריקה! המתנה הייתה בקופסה מספר {gift_box}.")

@bot.command(name="coinsflip", aliases=["cf", "flip"])
async def coins_flip(ctx, choice: str = None, amount: int = 0):
    if not choice or choice not in ["עץ", "פאלי"]:
        return await ctx.send("🪙 תבחר צד: `!coinsflip עץ` או `!coinsflip פאלי`")
    side = random.choice(["עץ", "פאלי"])
    if choice == side:
        await ctx.send(f"🤑 יצא {side}! ניחשת נכון וזכית!")
    else:
        await ctx.send(f"😭 יצא {side}! ניחשת {choice} והפסדת.")

@bot.command(name="mathquiz", aliases=["math"])
async def math_quiz(ctx):
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(["+", "-", "*"])
    correct_answer = eval(f"{num1} {operator} {num2}")
    await ctx.send(f"🧮 פתור את התרגיל תוך 15 שניות: **{num1} {operator} {num2} = ?**")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.strip().replace('-', '').isdigit()
    try:
        msg = await bot.wait_for("message", check=check, timeout=15.0)
        if int(msg.content) == correct_answer:
            await ctx.send(f"👑 גאון! התשובה נכונה. זכית!")
        else:
            await ctx.send(f"❌ טעות! התשובה הנכונה היא {correct_answer}.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ נגמר הזמן! התשובה הייתה {correct_answer}.")

@bot.command(name="slot", aliases=["slots"])
async def slot_machine(ctx):
    emojis = ["🍒", "🍋", "🍇", "💎", "7️⃣"]
    slot1 = random.choice(emojis)
    slot2 = random.choice(emojis)
    slot3 = random.choice(emojis)
    await ctx.send(f"🎰 **[ {slot1} | {slot2} | {slot3} ]** 🎰")
    if slot1 == slot2 == slot3:
        await ctx.send("🔥 ג'קפוט מטורף! 3 סמלים זהים! זכית!")
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        await ctx.send("✨ נחמד מאוד! 2 סמלים זהים. זכית!")
    else:
        await ctx.send("💸 אין התאמה, נסה את מזלך שוב בפעם הבאה!")
# ==========================================
# המודאלים של 14 שאלות המבחן (שלב 1, 2, 3)
# ==========================================

# שלב 3 - שאלות 11-14
class StaffModalPart3(discord.ui.Modal, title="טופס מועמדות - שלב 3 מתוך 3"):
    def __init__(self, answers_part1, answers_part2):
        super().__init__()
        self.answers_part1 = answers_part1
        self.answers_part2 = answers_part2

        self.q11 = discord.ui.TextInput(label="11. איך תתרום לשרת, וכמה רחוק תגיע?", style=discord.TextStyle.paragraph, max_length=300)
        self.q12 = discord.ui.TextInput(label="12. מאיפה הרצון להצטרף לצוות?", style=discord.TextStyle.paragraph, max_length=300)
        self.q13 = discord.ui.TextInput(label="13. למה אתה מתאים ורעיונות לשיפור?", style=discord.TextStyle.paragraph, max_length=400)
        self.q14 = discord.ui.TextInput(label="14. האם יש לך 2FA פעיל בחשבון? (כן/לא)", style=discord.TextStyle.short, max_length=10)

        self.add_item(self.q11)
        self.add_item(self.q12)
        self.add_item(self.q13)
        self.add_item(self.q14)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("⌛ מעבד ושולח את הטופס המלא להנהלה...", ephemeral=True)
        logs_channel = interaction.guild.get_channel(STAFF_LOGS_CHANNEL_ID)
        if not logs_channel:
            return
            
        embed = discord.Embed(
            title=f"📝 טופס מועמדות חדש - {interaction.user.name}",
            description=f"**מגיש הטופס:** {interaction.user.mention}\n**ID:** {interaction.user.id}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="📋 פרטים אישיים (שם, גיל, זמן בשרת):", value=str(self.answers_part1), inline=False)
        embed.add_field(name="🧠 תשובות סיטואציות וזמן השקעה:", value=str(self.answers_part2), inline=False)
        embed.add_field(name="11. תרומה ושאיפות:", value=self.q11.value, inline=False)
        embed.add_field(name="12. מאיפה הרצון להצטרף:", value=self.q12.value, inline=False)
        embed.add_field(name="13. למה דווקא אתה ושיפורים:", value=self.q13.value, inline=False)
        embed.add_field(name="14. האם יש 2FA?", value=self.q14.value, inline=False)
        
        if interaction.user.display_avatar:
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
        await logs_channel.send(embed=embed, view=StaffApprovalButtons(interaction.user.id))

# שלב 2 - שאלות 6-10
class StaffModalPart2(discord.ui.Modal, title="טופס מועמדות - שלב 2 מתוך 3"):
    def __init__(self, answers_part1):
        super().__init__()
        self.answers_part1 = answers_part1

        self.q6 = discord.ui.TextInput(label="6. התמודדות עם סיטואציה פחות נעימה/ריב", style=discord.TextStyle.paragraph, max_length=400)
        self.q7 = discord.ui.TextInput(label="7. איך תגיב אם צוות מתחתיך/מעליך תוקף?", style=discord.TextStyle.paragraph, max_length=300)
        self.q8 = discord.ui.TextInput(label="8. כמה זמן תוכל לתת לשרת בשבוע/יום?", style=discord.TextStyle.short, max_length=100)
        self.q9 = discord.ui.TextInput(label="9. השרת לא פעיל, איך תשנה את המצב?", style=discord.TextStyle.paragraph, max_length=300)
        self.q10 = discord.ui.TextInput(label="10. באיזה תחומים אתה רוצה לעזור בשרת?", style=discord.TextStyle.paragraph, max_length=200)

        self.add_item(self.q6)
        self.add_item(self.q7)
        self.add_item(self.q8)
        self.add_item(self.q9)
        self.add_item(self.q10)

    async def on_submit(self, interaction: discord.Interaction):
        answers_part2 = [self.q6.value, self.q7.value, self.q8.value, self.q9.value, self.q10.value]
        await interaction.response.send_modal(StaffModalPart3(self.answers_part1, answers_part2))

# שלב 1 - שאלות 1-5
class StaffModalPart1(discord.ui.Modal, title="טופס מועמדות - שלב 1 מתוך 3"):
    def __init__(self):
        super().__init__()
        self.q1 = discord.ui.TextInput(label="1. שם מלא / כינוי בדיסקורד", style=discord.TextStyle.short, max_length=100)
        self.q2 = discord.ui.TextInput(label="2. גיל", style=discord.TextStyle.short, max_length=3)
        self.q3 = discord.ui.TextInput(label="3. כמה זמן אתה בשרת שלנו?", style=discord.TextStyle.short, max_length=100)
        self.q4 = discord.ui.TextInput(label="4. ניסיון קודם בניהול וסיבת עזיבה", style=discord.TextStyle.paragraph, max_length=400)
        self.q5 = discord.ui.TextInput(label="5. איך אתה מגדיר צוות טוב ותכונותיו?", style=discord.TextStyle.paragraph, max_length=400)

        self.add_item(self.q1)
        self.add_item(self.q2)
        self.add_item(self.q3)
        self.add_item(self.q4)
        self.add_item(self.q5)

    async def on_submit(self, interaction: discord.Interaction):
        answers_part1 = [self.q1.value, self.q2.value, self.q3.value, self.q4.value, self.q5.value]
        await interaction.response.send_modal(StaffModalPart2(answers_part1))

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))

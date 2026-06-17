import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio
class HelpButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

  
    @discord.ui.button(label="עזרה", style=discord.ButtonStyle.success, custom_id="take_help_call")
    async def take_call(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds
        
        embed.set_field_at(2, name="טופל על ידי", value=f"{interaction.user.mention}", inline=False)
        embed.color = discord.Color.green()
        
        button.disabled = True
        button.label = "בטיפול"
        button.style = discord.ButtonStyle.secondary
        
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"{interaction.user.mention} קיבל את הקריאה!", ephemeral=False)


# חנות של הרמות ודברים חנות
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')
# ==========================================
# הגדרות ומשתנים קבועים של השרת שלך
# ==========================================
ROLE_1_ID = 1484226514051665930  # רול 1 - 30,000
ROLE_2_ID = 1491063689502003360 # רול 2 - 20,000
ROLE_3_ID = 1490894966262726687# שלישי - 10,000
ROLE_4_ID = 1490894895618195577 # רביעי - 5,000
ROLE_5_ID = 1490894817373196388 # חמישי - 2,500

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
@bot.command(name="h")
async def help_call_custom(ctx):
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

    # הענקת הרולים למשתמש שתוייג
    try:
        await member.add_roles(member_role, staff_friend_role)
        
        # יצירת הודעה מעוצבת לאישור הפעולה עם תמונת השרת
        embed = discord.Embed(
            title="✨ חבר צוות חדש הצטרף! ✨",
            description=f"המשתמש {member.mention} קיבל בהצלחה את הרולים שלו.",
            color=discord.Color.purple()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        embed.add_field(name="הרולים שהוענקו:", value=f"• {member_role.mention}\n• {staff_friend_role.mention}", inline=False)
        embed.set_footer(text=f"בוצע על ידי: {interaction.user.name} • {guild.name}")
        
        # שליחת ההודעה לערוץ שבו הופעלה הפקודה
        await interaction.response.send_message(embed=embed)
        
        # שליחת הודעה פרטית למשתמש שקיבל את הרול
        try:
            await member.send(f"🎉 תתחדש! הוענקו לך הרולים **Member** ו-**Staff Friend** בשרת {guild.name}!")
        except:
            pass # אם הדיאמ שלו סגור הבוט לא יקרוס
            
    except discord.Forbidden:
        await interaction.response.send_message("❌ שגיאה: לבוט אין הרשאה מספקת. ודא שהרול של הבוט נמצא בראש רשימת הרולים בדיסקורד!", ephemeral=True)

# --- פקודת עזרה ותמיכה (!h) בעיצוב המקצועי של מאסטר אוהד ---
@bot.command(name="help_call", aliases=["h"])
async def help_call_custom(ctx):
    guild = ctx.guild
    
    # יצירת אמבד יוקרתי ומעוצב
    embed = discord.Embed(
        title=f"⚠️ מרכז התמיכה והעזרה - {guild.name} ⚠️",
        description=(
            "שלום חברים! נתקלתם בבעיה, שגיאה, או שאתם זקוקים לעזרת צוות הניהול המורחב?\n"
            "הגעתם למקום הנכון. אנו זמינים עבורכם לכל פנייה, שאלה או בקשת עזרה בשרת.\n\n"
            "**💡 דגשים חשובים לפני פתיחת פנייה:**\n"
            "• נא לשמור על שפה מכבדת מול חברי הסטאף.\n"
            "• אין לפתוח טיקטים סתם ללא סיבה מוצדקת (הדבר עלול לגרור ענישה).\n"
            "• צוות השרת עושה את מירב המאמצים לענות במהירות האפשרית."
        ),
        color=discord.Color.from_rgb(47, 49, 54) # צבע כהה ומקצועי כמו של דיסקורד
    )
    
    # הוספת תמונת השרת (לוגו) בצד האמבד
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        
    # שדות מידע מעוצבים
    embed.add_field(name="⏰ שעות פעילות הטיקטים", value="```24/7 - בהתאם לזמינות הצוות```", inline=False)
    embed.add_field(name="🛡️ בורר פניות אוטומטי", value="לאחר לחיצה על הכפתור, ייפתח לכם חדר אישי ומאובטח.", inline=False)
    
    # שורת תחתית (Footer) עם השם שלך/שם השרת
    embed.set_footer(text=f"MasterOhad Network • כל הזכויות שמורות", icon_url=guild.icon.url if guild.icon else None)
    
    # חיבור כפתור הטיקט הקיים שלך מהקוד (TicketView) בשביל לפתוח חדר
    try:
        view = TicketView()
    except NameError:
        # פתרון גיבוי במידה והקלאס לא מוגדר תחת השם הזה
        view = None
        
    if view:
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send(embed=embed)
        await ctx.send("⚠️ שגיאה זמנית: מערכת הכפתורים של הטיקטים (TicketView) לא נמצאה בקוד.")

keep_alive()

bot.run('MTQ4MDMzMjIxMTQyODUyODI0OA.GcMON6.URtsRJs7WqWju3gSHmC-MJaIZeJ2T_q8_1tVPE')





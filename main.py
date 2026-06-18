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
# מחלקה נפרדת עבור כפתור האימות בלבד
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="אימות קבלת גישה ✅", style=discord.ButtonStyle.success, custom_id="verify_member_btn")
    async def verify_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # הדבק כאן את ה-ID של הרול שחברים מקבלים (Member)
        member_role = guild.get_role(1483920420414554272) 
        
        if member_role:
            await user.add_roles(member_role)
            await interaction.response.send_message("🎉 אומתת בהצלחה! כל ערוצי השרת נפתחו בפניך.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ שגיאה: רול החברים לא מוגדר נכון בקוד.", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
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


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_verify(ctx, target_channel: discord.TextChannel = None):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    channel_to_send = target_channel if target_channel else ctx.channel
    embed = discord.Embed(
        title=f"✅ אימות חברים - {ctx.guild.name}",
        description=(
            f"ברוכים הבאים לשרת **{ctx.guild.name}**!\n"
            "על מנת לבצע אימות ולקבל גישה לכל ערוצי השרת, לחצו על הכפתור למטה.\n\n"
            "**📜 חוקים בסיסיים:**\n"
            "• כבדו את כל חברי השרת\n"
            "• אין ספאם או פלוד\n"
            "• עקבו אחר הוראות הצוות\n\n"
            "• קראו את ערוץ החוקים והתקנון לפני שאתם מתחילים!"
        ),
        color=discord.Color.from_rgb(47, 49, 54)
    )
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
    embed.set_footer(text=f"{ctx.guild.name} • מערכת אימות אוטומטית")
    await channel_to_send.send(embed=embed, view=VerifyView())


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
            
       # ==========================================
# 1. פקודת העזרה והתמיכה (!h) + הגבלת סטאף
# ==========================================
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="טפל כאן 🛠️", style=discord.ButtonStyle.success, custom_id="handle_help_btn")
    async def handle_here(self, interaction: discord.Interaction, button: discord.ui.Button):
        # בדיקה: האם ללוחץ יש את רול הסטאף הכללי?
        has_staff_role = interaction.user.get_role(GENERAL_STAFF_ROLE_ID) is not None
        is_admin = interaction.user.guild_permissions.administrator
        
        if not has_staff_role and not is_admin:
            return await interaction.response.send_message("❌ כפתור זה מיועד לחברי צוות השרת בלבד!", ephemeral=True)
            
        # הכרזה מי איש הצוות שלקח את הטיפול
        await interaction.channel.send(f"🙋‍♂️ הפנייה נלקחה לטיפול על ידי איש הצוות: {interaction.user.mention}")
        button.disabled = True
        await interaction.response.edit_message(view=self)

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


# ==========================================
# 2. חנות ה-XP המקצועית בשרת (!myshop)
# ==========================================
@bot.command(name="myshop", aliases=["shop"])
async def xp_shop_command(ctx):
    embed = discord.Embed(
        title=f"🛒 חנות ה-XP הרשמית - {ctx.guild.name}",
        description="צברתם מספיק נקודות? זה הזמן לרכוש רולים ייחודיים ולהשתדרג בשרת!",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎖️ רול: Iron Member", value="💰 עלות: **5,000 XP**\n*רמה נדרשת: 5*", inline=False)
    embed.add_field(name="🥇 רול: Bronze Member", value="💰 עלות: **10,000 XP**\n*רמה נדרשת: 10*", inline=False)
    embed.add_field(name="💎 רול: Silver Member", value="💰 עלות: **25,000 XP**\n*רמה נדרשת: 20*", inline=False)
    embed.add_field(name="👑 רול: Gold VIP", value="💰 עלות: **50,000 XP**\n*רמה נדרשת: 35*", inline=False)
    embed.set_footer(text="לקנייה יש לרשום בקשה בטיקט מול אחד מבוחני או מנהלי השרת.")
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)


# ==========================================
# 3. פקודת ה-XP המעוצבת (כרטיס רמות)
# ==========================================
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


# ==========================================
# 4. קטגוריית משחקי ה-XP
# ==========================================
@bot.command(name="rps", aliases=["rock", "paper", "scissors"])
async def rps_game(ctx, choice: str = None):
    if not choice or choice.lower() not in ["אבן", "נייר", "מספריים"]: return await ctx.send("❌ נא לבחור: `!rps אבן`, `!rps נייר` או `!rps מספריים`")
    bot_choice = random.choice(["אבן", "נייר", "מספריים"])
    user_choice = choice.lower()
    if user_choice == bot_choice: await ctx.send("🤝 תיקו! שנינו בחרנו את אותו הדבר.")
    elif (user_choice == "אבן" and bot_choice == "מספריים") or (user_choice == "נייר" and bot_choice == "אבן") or (user_choice == "מספריים" and bot_choice == "נייר"):
        await ctx.send(f"🎉 ניצחת! בחרת {user_choice} ואני בחרתי {bot_choice}. זכית!")
    else: await ctx.send(f"😢 הפסדת! בחרת {user_choice} ואני בחרתי {bot_choice}.")

@bot.command(name="guess", aliases=["g"])
async def guess_game(ctx, number: int = None):
    if not number or number < 1 or number > 5: return await ctx.send("❌ נא לנחש מספר בין 1 ל-5! דוגמה: `!guess 3`")
    secret_number = random.randint(1, 5)
    if number == secret_number: await ctx.send(f"🎯 בול! המספר היה {secret_number}. זכית!")
    else: await ctx.send(f"❌ פספוס! ניחשת {number} אבל המספר האמיתי היה {secret_number}.")

@bot.command(name="football", aliases=["fb", "goal"])
async def football_game(ctx, direction: str = None):
    if not direction or direction not in ["ימין", "שמאל", "אמצע"]: return await ctx.send("⚽ לאן לבעוט? תבחר: `!football ימין`, `!football שמאל` או `!football אמצע`")
    gk_jump = random.choice(["ימין", "שמאל", "אמצע"])
    if direction == gk_jump: await ctx.send(f"🧤 השוער זינק ל{gk_jump} והדף את הכדור! אין גול.")
    else: await ctx.send(f"⚽ GOAL!! השוער זינק ל{gk_jump} ואתה הבקעת ל{direction}! זכית!")

@bot.command(name="blackjack", aliases=["bj"])
async def blackjack_game(ctx, amount: int = 0):
    user_card1 = random.randint(1, 11)
    user_card2 = random.randint(1, 10)
    user_total = user_card1 + user_card2
    bot_total = random.randint(15, 22)
    if user_total > 21: await ctx.send(f"💥 נשרפת! הקלפים שלך: {user_card1} + {user_card2} = {user_total}. הפסדת.")
    elif bot_total > 21 or user_total > bot_total: await ctx.send(f"🃏 ניצחת בבלאקג'ק! לך יש {user_total} ולבוט יש {bot_total}. זכית!")
    elif user_total == bot_total: await ctx.send(f"🤝 תיקו! לשניכם יש {user_total}.")
    else: await ctx.send(f"😢 הפסדת! לך יש {user_total} ולבוט יש {bot_total}.")

# ==========================================
# 1. פקדת ה-XP המעוצבת (כרטיס רמות)
# ==========================================
@bot.command(name="xp", aliases=["rank"])
async def xp_card_command(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    if user_id in user_data:
        user_xp = user_data[user_id].get('xp', 0)
        user_level = user_data[user_id].get('level', 1)
    else:
        user_xp = 0
        user_level = 1
    next_level_xp = user_level * 10000 if user_level > 0 else 10000
    percentage = int((user_xp / next_level_xp) * 100) if next_level_xp > 0 else 0
    if percentage > 100: percentage = 100
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


# ==========================================
# 2. חנות ה-XP המקצועית בשרת (!myshop)
# ==========================================
@bot.command(name="myshop", aliases=["shop"])
async def xp_shop_command(ctx):
    embed = discord.Embed(
        title=f"🛒 חנות ה-XP הרשמית - {ctx.guild.name}",
        description="צברתם מספיק נקודות? זה הזמן לרכוש רולים ייחודיים ולהשתדרג בשרת!",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎖️ רול: Iron Member", value="💰 עלות: **5,000 XP**\n*רמה נדרשת: 5*", inline=False)
    embed.add_field(name="🥇 רול: Bronze Member", value="💰 עלות: **10,000 XP**\n*רמה נדרשת: 10*", inline=False)
    embed.add_field(name="💎 רול: Silver Member", value="💰 עלות: **25,000 XP**\n*רמה נדרשת: 20*", inline=False)
    embed.add_field(name="👑 רול: Gold VIP", value="💰 עלות: **50,000 XP**\n*רמה נדרשת: 35*", inline=False)
    embed.set_footer(text="לקנייה יש לרשום בקשה בטיקט מול אחד מבוחני או מנהלי השרת.")
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)


# ==========================================
# 3. קטגוריית משחקי ה-XP
# ==========================================
@bot.command(name="rps", aliases=["rock", "paper", "scissors"])
async def rps_game(ctx, choice: str = None):
    if not choice or choice.lower() not in ["אבן", "נייר", "מספריים"]: return await ctx.send("❌ נא לבחור: `!rps אבן`, `!rps נייר` או `!rps מספריים`")
    bot_choice = random.choice(["אבן", "נייר", "מספריים"])
    user_choice = choice.lower()
    if user_choice == bot_choice: await ctx.send("🤝 תיקו! שנינו בחרנו את אותו הדבר.")
    elif (user_choice == "אבן" and bot_choice == "מספריים") or (user_choice == "נייר" and bot_choice == "אבן") or (user_choice == "מספריים" and bot_choice == "נייר"):
        await ctx.send(f"🎉 ניצחת! בחרת {user_choice} ואני בחרתי {bot_choice}. זכית!")
    else: await ctx.send(f"😢 הפסדת! בחרת {user_choice} ואני בחרתי {bot_choice}.")

@bot.command(name="guess", aliases=["g"])
async def guess_game(ctx, number: int = None):
    if not number or number < 1 or number > 5: return await ctx.send("❌ נא לנחש מספר בין 1 ל-5! דוגמה: `!guess 3`")
    secret_number = random.randint(1, 5)
    if number == secret_number: await ctx.send(f"🎯 בול! המספר היה {secret_number}. זכית!")
    else: await ctx.send(f"❌ פספוס! ניחשת {number} אבל המספר האמיתי היה {secret_number}.")

@bot.command(name="football", aliases=["fb", "goal"])
async def football_game(ctx, direction: str = None):
    if not direction or direction not in ["ימין", "שמאל", "אמצע"]: return await ctx.send("⚽ לאן לבעוט? תבחר: `!football ימין`, `!football שמאל` או `!football אמצע`")
    gk_jump = random.choice(["ימין", "שמאל", "אמצע"])
    if direction == gk_jump: await ctx.send(f"🧤 השוער זינק ל{gk_jump} והדף את הכדור! אין גול.")
    else: await ctx.send(f"⚽ GOAL!! השוער זינק ל{gk_jump} ואתה הבקעת ל{direction}! זכית!")

@bot.command(name="blackjack", aliases=["bj"])
async def blackjack_game(ctx, amount: int = 0):
    user_card1 = random.randint(1, 11)
    user_card2 = random.randint(1, 10)
    user_total = user_card1 + user_card2
    bot_total = random.randint(15, 22)
    if user_total > 21: await ctx.send(f"💥 נשרפת! הקלפים שלך: {user_card1} + {user_card2} = {user_total}. הפסדת.")
    elif bot_total > 21 or user_total > bot_total: await ctx.send(f"🃏 ניצחת בבלאקג'ק! לך יש {user_total} ולבוט יש {bot_total}. זכית!")
    elif user_total == bot_total: await ctx.send(f"🤝 תיקו! לשניכם יש {user_total}.")
    else: await ctx.send(f"😢 הפסדת! לך יש {user_total} ולבוט יש {bot_total}.")

@bot.command(name="gamble", aliases=["gift"])
async def gamble_gift(ctx, box: int = None):
    if not box or box < 1 or box > 3: return await ctx.send("🎁 יש 3 קופסאות. נחש איפה המתנה: `!gamble 1`, `!gamble 2` או `!gamble 3`")
    gift_box = random.randint(1, 3)
    if box == gift_box: await ctx.send(f"🎉 מצאת את המתנה בקופסה {gift_box}! זכית!")
    else: await ctx.send(f"📦 קופסה ריקה! המתנה הייתה בקופסה מספר {gift_box}.")

@bot.command(name="coinsflip", aliases=["cf", "flip"])
async def coins_flip(ctx, choice: str = None, amount: int = 0):
    if not choice or choice not in ["עץ", "פאלי"]: return await ctx.send("🪙 תבחר צד: `!coinsflip עץ` או `!coinsflip פאלי`")
    side = random.choice(["עץ", "פאלי"])
    if choice == side: await ctx.send(f"🤑 יצא {side}! ניחשת נכון וזכית!")
    else: await ctx.send(f"😭 יצא {side}! ניחשת {choice} והפסדת.")

@bot.command(name="mathquiz", aliases=["math"])
async def math_quiz(ctx):
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(["+", "-", "*"])
    correct_answer = eval(f"{num1} {operator} {num2}")
    await ctx.send(f"🧮 פתור את התרגיל תוך 15 שניות: **{num1} {operator} {num2} = ?**")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.strip().replace('-', '').isdigit()
    try:
        msg = await bot.wait_for("message", check=check, timeout=15.0)
        if int(msg.content) == correct_answer: await ctx.send(f"👑 גאון! התשובה נכונה. זכית!")
        else: await ctx.send(f"❌ טעות! התשובה הנכונה היא {correct_answer}.")
    except asyncio.TimeoutError: await ctx.send(f"⏰ נגמר הזמן! התשובה הייתה {correct_answer}.")

@bot.command(name="slot", aliases=["slots"])
async def slot_machine(ctx):
    emojis = ["🍒", "🍋", "🍇", "💎", "7️⃣"]
    slot1 = random.choice(emojis)
    slot2 = random.choice(emojis)
    slot3 = random.choice(emojis)
    await ctx.send(f"🎰 **[ {slot1} | {slot2} | {slot3} ]** 🎰")
    if slot1 == slot2 == slot3: await ctx.send("🔥 ג'קפוט מטורף! 3 סמלים זהים! זכית!")
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3: await ctx.send("✨ נחמד מאוד! 2 סמלים זהים. זכית!")
    else: await ctx.send("💸 אין התאמה, נסה את מזלך שוב בפעם הבאה!")

# ==========================================
# 1. פקדת ה-XP המעוצבת (שונה ל-myxp כדי למנוע כפילות)
# ==========================================
@bot.command(name="myxp", aliases=["rank"])
async def xp_card_command(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    if user_id in user_data:
        user_xp = user_data[user_id].get('xp', 0)
        user_level = user_data[user_id].get('level', 1)
    else:
        user_xp = 0
        user_level = 1
    next_level_xp = user_level * 10000 if user_level > 0 else 10000
    percentage = int((user_xp / next_level_xp) * 100) if next_level_xp > 0 else 0
    if percentage > 100: percentage = 100
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


# ==========================================
# 2. חנות ה-XP המקצועית בשרת (!myshop)
# ==========================================
@bot.command(name="myshop", aliases=["shop"])
async def xp_shop_command(ctx):
    embed = discord.Embed(
        title=f"🛒 חנות ה-XP הרשמית - {ctx.guild.name}",
        description="צברתם מספיק נקודות? זה הזמן לרכוש רולים ייחודיים ולהשתדרג בשרת!",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎖️ רול: Iron Member", value="💰 עלות: **5,000 XP**\n*רמה נדרשת: 5*", inline=False)
    embed.add_field(name="🥇 רול: Bronze Member", value="💰 עלות: **10,000 XP**\n*רמה נדרשת: 10*", inline=False)
    embed.add_field(name="💎 רול: Silver Member", value="💰 עלות: **25,000 XP**\n*רמה נדרשת: 20*", inline=False)
    embed.add_field(name="👑 רול: Gold VIP", value="💰 עלות: **50,000 XP**\n*רמה נדרשת: 35*", inline=False)
    embed.set_footer(text="לקנייה יש לרשום בקשה בטיקט מול אחד מבוחני או מנהלי השרת.")
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)


# ==========================================
# 3. קטגוריית משחקי ה-XP המלאה
# ==========================================
@bot.command(name="rps", aliases=["rock", "paper", "scissors"])
async def rps_game(ctx, choice: str = None):
    if not choice or choice.lower() not in ["אבן", "נייר", "מספריים"]: return await ctx.send("❌ נא לבחור: `!rps אבן`, `!rps נייר` או `!rps מספריים`")
    bot_choice = random.choice(["אבן", "נייר", "מספריים"])
    user_choice = choice.lower()
    if user_choice == bot_choice: await ctx.send("🤝 תיקו! שנינו בחרנו את אותו הדבר.")
    elif (user_choice == "אבן" and bot_choice == "מספריים") or (user_choice == "נייר" and bot_choice == "אבן") or (user_choice == "מספריים" and bot_choice == "נייר"):
        await ctx.send(f"🎉 ניצחת! בחרת {user_choice} ואני בחרתי {bot_choice}. זכית!")
    else: await ctx.send(f"😢 הפסדת! בחרת {user_choice} ואני בחרתי {bot_choice}.")

@bot.command(name="guess", aliases=["g"])
async def guess_game(ctx, number: int = None):
    if not number or number < 1 or number > 5: return await ctx.send("❌ נא לנחש מספר בין 1 ל-5! דוגמה: `!guess 3`")
    secret_number = random.randint(1, 5)
    if number == secret_number: await ctx.send(f"🎯 בול! המספר היה {secret_number}. זכית!")
    else: await ctx.send(f"❌ פספוס! ניחשת {number} אבל המספר האמיתי היה {secret_number}.")

@bot.command(name="football", aliases=["fb", "goal"])
async def football_game(ctx, direction: str = None):
    if not direction or direction not in ["ימין", "שמאל", "אמצע"]: return await ctx.send("⚽ לאן לבעוט? תבחר: `!football ימין`, `!football שמאל` או `!football אמצע`")
    gk_jump = random.choice(["ימין", "שמאל", "אמצע"])
    if direction == gk_jump: await ctx.send(f"🧤 השוער זינק ל{gk_jump} והדף את הכדור! אין גול.")
    else: await ctx.send(f"⚽ GOAL!! השוער זינק ל{gk_jump} ואתה הבקעת ל{direction}! זכית!")

@bot.command(name="blackjack", aliases=["bj"])
async def blackjack_game(ctx, amount: int = 0):
    user_card1 = random.randint(1, 11)
    user_card2 = random.randint(1, 10)
    user_total = user_card1 + user_card2
    bot_total = random.randint(15, 22)
    if user_total > 21: await ctx.send(f"💥 נשרפת! הקלפים שלך: {user_card1} + {user_card2} = {user_total}. הפסדת.")
    elif bot_total > 21 or user_total > bot_total: await ctx.send(f"🃏 ניצחת בבלאקג'ק! לך יש {user_total} ולבוט יש {bot_total}. זכית!")
    elif user_total == bot_total: await ctx.send(f"🤝 תיקו! לשניכם יש {user_total}.")
    else: await ctx.send(f"😢 הפסדת! לך יש {user_total} ולבוט יש {bot_total}.")

@bot.command(name="gamble", aliases=["gift"])
async def gamble_gift(ctx, box: int = None):
    if not box or box < 1 or box > 3: return await ctx.send("🎁 יש 3 קופסאות. נחש איפה המתנה: `!gamble 1`, `!gamble 2` או `!gamble 3`")
    gift_box = random.randint(1, 3)
    if box == gift_box: await ctx.send(f"🎉 מצאת את המתנה בקופסה {gift_box}! זכית!")
    else: await ctx.send(f"📦 קופסה ריקה! המתנה הייתה בקופסה מספר {gift_box}.")

@bot.command(name="coinsflip", aliases=["cf", "flip"])
async def coins_flip(ctx, choice: str = None, amount: int = 0):
    if not choice or choice not in ["עץ", "פאלי"]: return await ctx.send("🪙 תבחר צד: `!coinsflip עץ` או `!coinsflip פאלי`")
    side = random.choice(["עץ", "פאלי"])
    if choice == side: await ctx.send(f"🤑 יצא {side}! ניחשת נכון וזכית!")
    else: await ctx.send(f"😭 יצא {side}! ניחשת {choice} והפסדת.")

@bot.command(name="mathquiz", aliases=["math"])
async def math_quiz(ctx):
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(["+", "-", "*"])
    correct_answer = eval(f"{num1} {operator} {num2}")
    await ctx.send(f"🧮 פתור את התרגיל תוך 15 שניות: **{num1} {operator} {num2} = ?**")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel and m.content.strip().replace('-', '').isdigit()
    try:
        msg = await bot.wait_for("message", check=check, timeout=15.0)
        if int(msg.content) == correct_answer: await ctx.send(f"👑 גאון! התשובה נכונה. זכית!")
        else: await ctx.send(f"❌ טעות! התשובה הנכונה היא {correct_answer}.")
    except asyncio.TimeoutError: await ctx.send(f"⏰ נגמר הזמן! התשובה הייתה {correct_answer}.")

@bot.command(name="slot", aliases=["slots"])
async def slot_machine(ctx):
    emojis = ["🍒", "🍋", "🍇", "💎", "7️⃣"]
    slot1 = random.choice(emojis)
    slot2 = random.choice(emojis)
    slot3 = random.choice(emojis)
    await ctx.send(f"🎰 **[ {slot1} | {slot2} | {slot3} ]** 🎰")
    if slot1 == slot2 == slot3: await ctx.send("🔥 ג'קפוט מטורף! 3 סמלים זהים! זכית!")
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3: await ctx.send("✨ נחמד מאוד! 2 סמלים זהים. זכית!")
    else: await ctx.send("💸 אין התאמה, נסה את מזלך שוב בפעם הבאה!")


# ==========================================
# 4. פקודת עזרה משודרגת עם סיבה וחדר וויס (!h)
# ==========================================
class RequestHelpView(discord.ui.View):
    def __init__(self, request_msg_url=None):
        super().__init__(timeout=None)
        self.request_msg_url = request_msg_url

    @discord.ui.button(label="טפל כאן 🛠️", style=discord.ButtonStyle.success, custom_id="btn_handle_help_request")
    async def handle_here(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_staff_role = interaction.user.get_role(GENERAL_STAFF_ROLE_ID) is not None
        is_admin = interaction.user.guild_permissions.administrator
        if not has_staff_role and not is_admin:
            return await interaction.response.send_message("❌ כפתור זה מיועד לחברי צוות השרת בלבד!", ephemeral=True)
        await interaction.channel.send(f"🙋‍♂️ הפנייה נלקחה לטיפול על ידי איש הצוות: {interaction.user.mention}")
        try:
            dm_embed = discord.Embed(
                title="🚀 קריאת עזרה נלקחה בהצלחה",
                description=f"לקחת לטיפול את הפנייה בערוץ {interaction.channel.mention}.\n🔗 [לחץ כאן כדי לקפוץ ישירות להודעה]({self.request_msg_url or ''})",
                color=discord.Color.green()
            )
            await interaction.user.send(embed=dm_embed)
        except discord.Forbidden:
            pass
        button.disabled = True
        button.label = f"בטיפול של {interaction.user.name} ✔️"
        button.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)

@bot.command(name="h")
async def help_call_custom(ctx, *, args: str = None):
    reason = "לא צוינה סיבה"
    voice_room = "לא צוין חדר וויס"
    if args:
        if "|" in args:
            parts = args.split("|", 1)
            reason = parts[0].strip()
            voice_room = parts[1].strip()
        else:
            reason = args.strip()
    guild = ctx.guild
    embed = discord.Embed(
        title=f"⚠️ קריאת עזרה דחופה - {guild.name} ⚠️",
        description=(
            f"**👤 המבקש:** {ctx.author.mention}\n**📂 ערוץ טקסט:** {ctx.channel.mention}\n\n"
            f"**📝 סיבת הפנייה:**\n`{reason}`\n\n**🔊 חדר וויס נוכחי:**\n`{voice_room}`\n\n"
            f"**💡 מידע לצוות:**\nנציג פנוי מתוך <@&{GENERAL_STAFF_ROLE_ID}> מתבקש ללחוץ למטה ולהתייצב לעזרה."
        ),
        color=discord.Color.from_rgb(47, 49, 54)
    )
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.set_footer(text=f"נשלח על ידי: {ctx.author.name} • {guild.name}")
    sent_message = await ctx.send(embed=embed)
    await sent_message.edit(view=RequestHelpView(request_msg_url=sent_message.jump_url))


keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))


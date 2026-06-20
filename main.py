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

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


# הגדרת משתנים ורולים
ROLE_1_ID = 1434226514051665920 
ROLE_2_ID = 1434236285220202100 
ROLE_3_ID = 1434023456252726607 
ROLE_4_ID = 1434023485618195577 
ROLE_5_ID = 1434034812251396305 

STAFF_ROLE_ID = 1484235285220202100 
STAFF_FRIENDS_LOG_CHANNEL_ID = 1434311487832883406 

@bot.event
async def on_ready():
    print(f'{bot.user.name} מחובר בהצלחה ומערכות הסטאף והטיקטים פעילות!')
    bot.add_view(StaffFriendReview())
    bot.add_view(TicketActionButtons())



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
# --- מערכת XP ורמות פשוטה ---
user_xp = {} # שומר את ה-XP של המשתמשים בזיכרון

@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    # הוספת XP על כל הודעה
    user_id = str(message.author.id)
    if user_id not in user_xp:
        user_xp[user_id] = {"xp": 0, "level": 1}
        
    user_xp[user_id]["xp"] += random.randint(15, 25)
    
    # חישוב עליית רמה (כל 1000 XP עולים רמה)
    xp_needed = user_xp[user_id]["level"] * 1000
    if user_xp[user_id]["xp"] >= xp_needed:
        user_xp[user_id]["level"] += 1
        await message.channel.send(f"🎉 כל הכבוד {message.author.mention}! עלית לרמה **{user_xp[user_id]['level']}**!")

    await bot.process_commands(message)

@bot.command(name="xp", aliases=["rank", "רמה"])
async def show_xp(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    
    # אם המשתמש עדיין לא דיבר בצ'אט
    if user_id not in user_xp:
        user_xp[user_id] = {"xp": 0, "level": 1}
        
    current_xp = user_xp[user_id]["xp"]
    current_lvl = user_xp[user_id]["level"]
    next_lvl_xp = current_lvl * 1000
    
    embed = discord.Embed(title=f"📊 כרטיס ה-XP של {member.name}", color=discord.Color.from_rgb(47, 49, 54))
    if member.avatar:
        embed.set_thumbnail(url=member.display_avatar.url)
        
    embed.add_field(name="👤 משתמש:", value=member.mention, inline=True)
    embed.add_field(name="⭐ רמה:", value=f"Level {current_lvl}", inline=True)
    embed.add_field(name="✨ נקודות XP:", value=f"{current_xp:,} / {next_lvl_xp:,} XP", inline=False)
    
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
        
    await ctx.send(embed=embed)


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
        member_role = guild.get_role(1485680386972455042) 
        
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
# הגדרת מחירי הדרגות ב-XP
SHOP_PRICES = {
    "Iron Member": 5000,
    "Bronze Member": 10000,
    "Silver Member": 25000,
    "Gold VIP": 50000
}

# הגדרת האיידי (ID) של הרולים בשרת שלך - שנה את המספרים לאיידי האמיתי מהשרת שלך!
SHOP_ROLES = {
    "Iron Member": 1517997156173217945,
    "Bronze Member": 1517997331822284912,
    "Silver Member": 1517997465566052493,
    "Gold VIP": 123456789012345678
}

class ShopDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Iron Member", description="מחיר: 5,000 XP", emoji="🪙"),
            discord.SelectOption(label="Bronze Member", description="מחיר: 10,000 XP", emoji="🥉"),
            discord.SelectOption(label="Silver Member", description="מחיר: 25,000 XP", emoji="🥈"),
            discord.SelectOption(label="Gold VIP", description="מחיר: 50,000 XP", emoji="👑")
        ]
        super().__init__(placeholder="בחר דרגה לקנייה...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        selected_item = self.values[0]
        price = SHOP_PRICES[selected_item]
        role_id = SHOP_ROLES[selected_item]
        
        # 1. בדיקה אם למשתמש יש בכלל XP במערכת
        if user_id not in user_xp:
            return await interaction.response.send_message("❌ אין לך מספיק XP בשביל לקנות בחנות!", ephemeral=True)
            
        # 2. בדיקה אם יש לו מספיק נקודות לקנייה
        if user_xp[user_id]["xp"] < price:
            missing_xp = price - user_xp[user_id]["xp"]
            return await interaction.response.send_message(f"❌ חסרים לך עוד {missing_xp:,} XP כדי לקנות את הדרגה {selected_item}!", ephemeral=True)
            
        # 3. בדיקה אם כבר יש לו את הרול הזה
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.response.send_message("❌ שגיאה: הרול הזה לא נמצא בשרת, פנה למנהל.", ephemeral=True)
            
        if role in interaction.user.roles:
            return await interaction.response.send_message("❌ כבר יש לך את הדרגה הזו!", ephemeral=True)
            
        # 4. ביצוע הקנייה: הורדת XP והוספת הרול
        user_xp[user_id]["xp"] -= price
        await interaction.user.add_role(role)
        await interaction.response.send_message(f"🎉 תתחדש! קנית את הדרגה **{selected_item}** בהצלחה! ירדו מחשבונך {price:,} XP.", ephemeral=False)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

@bot.command(name="myshop", aliases=["shop", "חנות"])
async def xp_shop_command(ctx):
    embed = discord.Embed(
        title=f"🛒 חנות ה-XP של {ctx.guild.name}",
        description="כאן תוכלו לבזבז את נקודות ה-XP שצברתם מדיבורים בצ'אט כדי לקנות תפקידים ודרגות ייחודיות!",
        color=discord.Color.gold()
    )
    for role_name, price in SHOP_PRICES.items():
        embed.add_field(name=f"✨ דרגת {role_name}", value=f"מחיר: **{price:,} XP**", inline=False)
        
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
        
    await ctx.send(embed=embed, view=ShopView())




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
  # ==========================================


class RequestHelpView(discord.ui.View):
    def __init__(self, request_msg_url=None):
        super().__init__(timeout=None)
        self.request_msg_url = request_msg_url

    @discord.ui.button(label="טפל בפנייה", style=discord.ButtonStyle.success, custom_id="btn_handle_help_request")
    async def handle_here(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_staff_role = interaction.user.get_role(GENERAL_STAFF_ROLE_ID) is not None
        is_admin = interaction.user.guild_permissions.administrator
        if not has_staff_role and not is_admin:
            return await interaction.response.send_message("אין לך הרשאות מתאימות לפעולה זו.", ephemeral=True)
            
        await interaction.channel.send(f"הפנייה מטופלת כעת על ידי: {interaction.user.mention}")
        try:
            dm_embed = discord.Embed(
                title="פנייתך בטיפול",
                description=f"הפנייה שלך בשרת {interaction.channel.mention} בטיפול. [לחץ כאן למעבר להודעה]({self.request_msg_url or ''})",
                color=discord.Color.green()
            )
            await interaction.user.send(embed=dm_embed)
        except discord.Forbidden:
            pass

            
        button.disabled = True
        button.label = f"טופל על ידי {interaction.user.name} ✔"
        button.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)
        
bot.remove_command('h')        
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
    try: await ctx.message.delete()
    except discord.NotFound: pass

# הגדרת הרולים שסיפקת
ROLE_MANAGEMENT_HELP = 1485440480459227227  # עזרה מההנהלה
ROLE_GENERAL_QUESTIONS = 1488259168593772554  # שאלות כלליות
ROLE_STAFF_TEST = 1485440385206456452  # בחינות לצוות

TICKET_CATEGORY_ID = None 

class TicketActionButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="טפל בפנייה 👮", style=discord.ButtonStyle.success, custom_id="btn_ticket_handle")
    async def handle_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_roles = [role.id for role in interaction.user.roles]
        if not any(r in user_roles for r in [ROLE_MANAGEMENT_HELP, ROLE_GENERAL_QUESTIONS, ROLE_STAFF_TEST]) and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ אין לך הרשאה לטפל בטיקט זה!", ephemeral=True)
            
        button.disabled = True
        button.label = f"בטיפול של {interaction.user.name} ✔"
        button.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"🔒 החדר ננעל לטיפולו הבלעדי של {interaction.user.mention}.")

   # הגדרת הרולים שסיפקת
ROLE_MANAGEMENT_HELP = 1485440480459227227  # עזרה מההנהלה
ROLE_GENERAL_QUESTIONS = 1488259168593772554  # שאלות כלליות
ROLE_STAFF_TEST = 1485440385206456452  # בחינות לצוות

TICKET_CATEGORY_ID = None 

class TicketActionButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="טפל בפנייה 👮", style=discord.ButtonStyle.success, custom_id="btn_ticket_handle")
    async def handle_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_roles = [role.id for role in interaction.user.roles]
        if not any(r in user_roles for r in [ROLE_MANAGEMENT_HELP, ROLE_GENERAL_QUESTIONS, ROLE_STAFF_TEST]) and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ אין לך הרשאה לטפל בטיקט זה!", ephemeral=True)
            
        button.disabled = True
        button.label = f"בטיפול של {interaction.user.name} ✔"
        button.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(f"🔒 החדר ננעל לטיפולו הבלעדי של {interaction.user.mention}.")

    @discord.ui.button(label="סגור טיקט ❌", style=discord.ButtonStyle.danger, custom_id="btn_ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_roles = [role.id for role in interaction.user.roles]
        if not any(r in user_roles for r in [ROLE_MANAGEMENT_HELP, ROLE_GENERAL_QUESTIONS, ROLE_STAFF_TEST]) and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ אין לך הרשאה לסגור טיקט זה!", ephemeral=True)
            
        await interaction.response.send_message("⚠️ הטיקט ייסגר ויימחק בעוד 5 שניות...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class AdvancedTicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="עזרה מההנהלה", description="פנייה ישירה להנהלת השרת", emoji="👑"),
            discord.SelectOption(label="שאלות כלליות", description="בירורים, שאלות ועזרה כללית מהסטאף", emoji="💬"),
            discord.SelectOption(label="בחינות לצוות", description="פתיחת חדר ומילוי טופס מועמדות לצוות", emoji="📝")
        ]
        super().__init__(placeholder="בחר את סוג הפנייה שלך...", min_values=1, max_values=1, options=options, custom_id="dropdown_advanced_tickets")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        choice = self.values[0]

        target_role_id = None
        if choice == "עזרה מההנהלה":
            target_role_id = ROLE_MANAGEMENT_HELP
        elif choice == "שאלות כלליות":
            target_role_id = ROLE_GENERAL_QUESTIONS
        elif choice == "בחינות לצוות":
            target_role_id = ROLE_STAFF_TEST

        target_role = guild.get_role(target_role_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if target_role:
            overwrites[target_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        category = guild.get_channel(TICKET_CATEGORY_ID) if TICKET_CATEGORY_ID else None
        clean_name = choice.replace(" ", "-")
        
        channel = await guild.create_text_channel(
            name=f"🎫-{user.name}-{clean_name}",
            category=category,
            overwrites=overwrites
        )

        await interaction.response.send_message(f"✅ הטיקט שלך נפתח בהצלחה! {channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title=f"🎫 פנייה בנושא: {choice}",
            description=f"שלום {user.mention},\nפתחת בהצלחה פנייה לצוות. אנא פרט את כל המידע הרלוונטי כאן.\n\n**לצוות השרת:** השתמשו בכפתורים למטה כדי לנהל את הפנייה.",
            color=discord.Color.blue()
        )
        role_mention = target_role.mention if target_role else "@צוות"

        if choice == "בחינות לצוות":
            embed.title = "📝 טופס מועמדות לצוות השרת"
            embed.color = discord.Color.gold()
            embed.description = (
                f"שלום {user.mention},\n"
                "על מנת להגיש מועמדות לצוות, אנא **העתק את השאלות הבאות, ענה עליהן ושלח אותן כאן בצ'אט**:\n\n"
                "1. שם מלא (שלך) / כינוי בדיסקורד:\n"
                "2. גיל:\n"
                "3. כמה זמן אתה בשרת שלנו?\n"
                "4. ניסיון קודם בצוות ניהול / מודרטור? ספר קצת.. ואם עזבת אז מדוע? (שלח הוכחה במידה ויש)\n"
                "5. איך אתה מגדיר צוות טוב? מה בעינייך התכונות שצריכות להיות לחבר צוות?\n"
                "6. בתור צוות, מה היית עושה במידה ויש סיטואציה פחות נעימה בחדרי השרת / הוויס (מישהו מתחצף/ עובר על החוקים, ריבים בין כמה חברי השרת… תן דוגמה):\n"
                "7. איך היית מגיב אם צוות מתחתיך תוקף אותך? ואיך היית מגיב אם הוא היה מעליך?\n"
                "8. כמה זמן בערך אתה חושב שתוכל לתת ממך למען השרת בשבוע כל יום?\n"
                "9. במידה והשרת מתחיל טיפה להראות חוסר פעילות האם לדעתך תוכל לשנות את המצב? איך?\n"
                "10. באיזה תחומים אתה רוצה לעזור בשרת?\n"
                "11. איך אתה חושב שתוכל לתרום לשרת, וכמה רחוק אתה חושב שתוכל להגיע?\n"
                "12. מאיפה הרצון להצטרף לצוות?\n"
                "13. למה דווקא אתה מתאים לצוות שלנו? יש לך רעיון לשיפור השרת?\n"
                "14. האם יש לך 2FA?\n\n"
                "**לצוות השרת:** השתמשו בכפתורים למטה כדי לנהל את הפנייה."
            )

        await channel.send(content=f"{user.mention} | {role_mention}", embed=embed, view=TicketActionButtons())

class AdvancedTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AdvancedTicketDropdown())


@bot.command(name="setup_tickets2")
async def setup_tickets_cmd(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🎫 מרכז הפניות והתמיכה",
        description="צריכים עזרה מההנהלה? רוצים לשאול שאלה או להבחן לצוות השרת?\nבצעו בחירה מהתפריט הנפתח למטה והבוט יפתח לכם חדר פרטי מיידי.",
        color=discord.Color.purple()
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=AdvancedTicketView())
    
class AdvancedTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AdvancedTicketDropdown())

@bot.command(name="setup_tickets", aliases=["פתיחת_טיקטים"])
@commands.has_permissions(administrator=True)
async def setup_tickets_cmd(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🎫 מרכז הפניות והתמיכה",
        description="צריכים עזרה מההנהלה? רוצים לשאול שאלה או להבחן לצוות השרת?\nבצעו בחירה מהתפריט הנפתח למטה והבוט יפתח לכם חדר פרטי מיידי.",
        color=discord.Color.purple()
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=AdvancedTicketView())


keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))



import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# מערכת keep_alive לאירוח 24/7 ב-Railway
app = Flask('')
@app.route('/')
def home(): return "Online"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- הגדרות איידיז ותמונות של השרת (שנה לפי האיידיז שלך) ---
STAFF_ROLE_ID = 1484259160593772554
VERIFY_ROLE_ID = 1484226514851665930
LOG_CHANNEL_ID = 1492511487814881406
SERVER_ICON_URL = "https://discordapp.net"

# ==========================================
# 1. מערכת אימות (Verification)
# ==========================================
class VerifyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="התחל אימות / Verify ✅", style=discord.ButtonStyle.success, custom_id="verify_global")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFY_ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message("❌ אתה כבר מאומת בשרת!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ האימות בוצע בהצלחה! ברוך הבא.", ephemeral=True)

# ==========================================
# 2. מערכת בקשת סטאף פרנד (Staff Friend Acceptance)
# ==========================================
class StaffFriendReview(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Accept 🟢", style=discord.ButtonStyle.success, custom_id="sf_accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ אין לך הרשאה של אדמין!", ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.set_field_at(0, name="🟢 סטטוס קריאה", value="המשתמש אושר כסטאף פרנד בהצלחה!", inline=False)
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("✅ המשתמש אושר.", ephemeral=True)

    @discord.ui.button(label="Deny 🔴", style=discord.ButtonStyle.danger, custom_id="sf_deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ אין לך הרשאה של אדמין!", ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.set_field_at(0, name="🔴 סטטוס קריאה", value="הבקשה נדחתה על ידי ההנהלה.", inline=False)
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("❌ הבקשה נדחתה.", ephemeral=True)

# ==========================================
# 3. מערכת פקודת עזרה עם כפתור לצוות
# ==========================================
class HelpButtonView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="\u05d8\u05e4\u05dc \u05db\u05d0\u05df \u2694\ufe0f", style=discord.ButtonStyle.success, custom_id="take_help_call")
    async def take_call(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator and not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            return await interaction.response.send_message("❌ אינך איש צוות!", ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.set_field_at(2, name="\u05e0\u05dc\u05e7\u05d7 \u05e2\u05dc \u05d9\u05d3\u05d9 \u2694\ufe0f", value=f"{interaction.user.mention}", inline=False)
        embed.color = discord.Color.green()
        button.disabled = True
        button.label = "\u05d1\u05d8\u05d9\u05e4\u05d5\u05dc \ud83d\udee0\ufe0f"
        button.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(embed=embed, view=self)

# ==========================================
# 4. מערכת טיקטים מתקדמת עם השאלון שלך
# ==========================================
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="עזרה כללית", description="פתיחת פנייה כללית לצוות השרת", emoji="🎫"),
            discord.SelectOption(label="בחינה לצוות", description="הורדת טופס מועמדות רשמי לצוות השרת", emoji="📝"),
            discord.SelectOption(label="עזרה מההנהלה", description="פנייה ישירה לאדמינים הגבוהים", emoji="👑")
        ]
        super().__init__(placeholder="בחר את סוג הטיקט לפתיחה...", min_values=1, max_values=1, custom_id="ticket_select_global")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # יצירת חדר הטיקט
        channel_prefix = "exam" if self.values[0] == "בחינה לצוות" else "ticket"
        ticket_channel = await interaction.guild.create_text_channel(
            name=f"{channel_prefix}-{interaction.user.name}",
            category=interaction.channel.category,
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )
        
        if self.values[0] == "בחינה לצוות":
            # עיצוב ושליחת השאלון המלא שלך בתוך חדר הטיקט
            exam_embed = discord.Embed(
                title="📝 טופס מועמדות לצוות השרת",
                description="ברוך הבא! אנא העתק את השאלות הבאות, ענה עליהן במדויק ושלח אותן בחדר זה.\nצוות השרת יבחן את תשובותיך בהקדם.",
                color=discord.Color.purple()
            )
            exam_embed.set_thumbnail(url=SERVER_ICON_URL)
            
            # הכנסת כל 14 השאלות שלך בצורה מסודרת ומקצועית
            questions_text = (
                "**1.** שם מלא (שלך) / כינוי בדיסקורד:\n"
                "**2.** גיל:\n"
                "**3.** כמה זמן אתה בשרת שלנו?\n"
                "**4.** ניסיון קודם בצוות ניהול / מודרטור? ספר קצת.. ואם עזבת אז מדוע? (שלח הוכחה במידה ויש)\n"
                "**5.** איך אתה מגדיר צוות טוב? מה בעינייך התכונות שצריכות להיות לחבר צוות?\n"
                "**6.** בתור צוות, מה היית עושה במידה ויש סיטואציה פחות נעימה בחדרי השרת / הוויס (מישהו מתחצף, עובר על החוקים, ריבים... תן דוגמה):\n"
                "**7.** איך היית מגיב אם איש צוות מתחתיך תוקף אותך? ואיך היית מגיב אם הוא היה מעליך?\n"
                "**8.** כמה זמן בערך אתה חושב שתוכל לתת ממך למען השרת בשבוע / כל יום?\n"
                "**9.** במידה והשרת מתחיל טיפה להראות חוסר פעילות, האם לדעתך תוכל לשנות את המצב? איך?\n"
                "**10.** באיזה תחומים אתה רוצה לעזור בשרת?\n"
                "**11.** איך אתה חושב שתוכל לתרום לשרת, וכמה רחוק אתה חושב שתוכל להגיע?\n"
                "**12.** מאיפה הרצון להצטרף לצוות?\n"
                "**13.** למה דווקא אתה מתאים לצוות שלנו? יש לך רעיון לשיפור השרת?\n"
                "**14.** האם יש לך הגנת דו-שלבית (2FA) מופעלת בחשבון?"
            )
            exam_embed.add_field(name="📋 השאלות למילוי:", value=questions_text, inline=False)
            
            await ticket_channel.send(content=f"{interaction.user.mention} | <@&{STAFF_ROLE_ID}>", embed=exam_embed)
            await interaction.followup.send(f"✅ חדר הבחינה לצוות נפתח עבורך: {ticket_channel.mention}", ephemeral=True)
        
        else:
            # טיקט רגיל לשאר הפניות
            embed = discord.Embed(title=f"🎫 כרטיס תמיכה - {self.values[0]}", description="איש צוות יתפנה אליך בהקדם, אנא רשום את פנייתך מראש.", color=discord.Color.blue())
            embed.set_thumbnail(url=SERVER_ICON_URL)
            await ticket_channel.send(content=f"{interaction.user.mention} | <@&{STAFF_ROLE_ID}>", embed=embed)
            await interaction.followup.send(f"✅ הטיקט נפתח בהצלחה: {ticket_channel.mention}", ephemeral=True)

class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

# ==========================================
# 5. מערכת חנות רולים של אקספי (XP Shop Dropdown)
# ==========================================
class XpShopDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="50,000 XP", description="קניית רול דרגה ב-50 אלף נקודות", emoji="🥉"),
            discord.SelectOption(label="100,000 XP", description="קניית רול דרגה ב-100 אלף נקודות", emoji="🥈"),
            discord.SelectOption(label="150,000 XP", description="קניית רול דרגה ב-150 אלף נקודות", emoji="🥇"),
            discord.SelectOption(label="200,000 XP", description="קניית רול דרגה ב-200 אלף נקודות", emoji="💎"),
            discord.SelectOption(label="250,000 XP", description="קניית רול דרגה ב-250 אלף נקודות", emoji="👑")
        ]
        super().__init__(placeholder="בחר תפקיד לקנייה...", min_values=1, max_values=1, custom_id="xp_shop_select")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🛒 שלחת בקשת רכישה עבור הדרגה: **{self.values[0]}**! במידה ויש לך מספיק נקודות, הרול יוענק לך.", ephemeral=True)

class XpShopDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(XpShopDropdown())

# ==========================================
# 6. פקודות הבוט (XP, Setup, Help)
# ==========================================
@bot.command()
bot.run(os.getenv("DISCORD_TOKEN"))

import discord
from discord.ext import commands
import json
import os

# הגדרת ה-Intents
intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True

# הגדרת הבוט עם ביטול פקודת העזרה המובנית למניעת התנגשויות
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- ניהול מאגר נתונים פשוט של XP בקובץ JSON ---
XP_FILE = "xp_data.json"

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_xp = load_xp()

@bot.event
async def on_ready():
    print(f'-----------------------------------------')
    print(f'הבוט מחובר בהצלחה בתור {bot.user.name}')
    print(f'-----------------------------------------')

# מערכת קריאת הודעות ישירה
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    if user_id not in user_xp:
        user_xp[user_id] = 0
        
    user_xp[user_id] += 5
    save_xp(user_xp)

    # בדיקה ישירה של פקודות טקסט
    if message.content.strip() == "!xp":
        points = user_xp.get(user_id, 0)
        embed = discord.Embed(title="📊 סטטיסטיקת נקודות ה-XP שלך", color=0x57F287)
        embed.add_field(name="👤 משתמש:", value=message.author.mention, inline=True)
        embed.add_field(name="✨ נקודות ניסיון (XP):", value=f"**{points} XP**", inline=True)
        embed.set_thumbnail(url=message.author.display_avatar.url)
        await message.channel.send(embed=embed)
        return

    if message.content.strip() == "!send_shop":
        if message.author.guild_permissions.administrator:
            embed = discord.Embed(title="🛒 חנות ה-XP של Voice Chat Server", description="כאן אתם יכולים לבזבז את נקודות ה-XP שצברתם מהודעות בצ'אט ומשחקים כדי לקנות תפקידים יוקרתיים בשרת!\n\n**לחצו על הכפתורים למטה כדי לרכוש:**", color=0xFEE75C)
            embed.add_field(name="💎 רול VIP", value="מחיר: **500 XP**", inline=False)
            embed.add_field(name="🌟 רול ProBot", value="מחיר: **1000 XP**", inline=False)
            embed.set_footer(text="הקנייה היא אוטומטית ומורידה נקודות מהחשבון.")
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(embed=embed, view=XpShopView())
        return

    if message.content.startswith("!h"):
        args = message.content[2:].strip()
        if not args or "|" not in args:
            await message.channel.send("❌ **שימוש שגוי!** יש לכתוב את הפקודה בצורה הבאה:\n`!h סיבה | מיקום` (הפרד בין הסיבה למיקום בעזרת הקו `|`)")
            return

        reason, location = args.split("|", 1)
        reason = reason.strip()
        location = location.strip()

        guild = message.guild
        staff_role = discord.utils.get(guild.roles, name="Staff")
        
        embed = discord.Embed(title="🚨 קריאת עזרה דחופה", color=0x5865F2)
        embed.add_field(name="📍 מיקום הפנייה / וויס:", value=location, inline=False)
        embed.add_field(name="📝 סיבה שצויינה:", value=reason, inline=False)
        embed.add_field(name="👤 אחראי:", value=message.author.mention, inline=False)
        embed.set_footer(text="אנא המתן בסבלנות, הצוות יסייע לך בהקדם האפשרי!")

        staff_mention = staff_role.mention if staff_role else "@Staff"
        await message.channel.send(content=staff_mention, embed=embed)
        return

    await bot.process_commands(message)

# ==========================================
# חלק 1: מערכת האימות (לחיצה על כפתור)
# ==========================================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לחץ כאן לאימות", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        roles_to_give = ["Member", "Staff", "Friend"]
        guild_roles = []

        for role_name in roles_to_give:
            role = discord.utils.get(guild.roles, name=role_name)
            if not role:
                await interaction.response.send_message(f"❌ שגיאה: לא מצאתי בשרת רול בשם '{role_name}'.", ephemeral=True)
                return
            guild_roles.append(role)

        if any(role in member.roles for role in guild_roles):
            await interaction.response.send_message("אתה כבר מאומת בשרת עם הרולים המתאימים!", ephemeral=True)
            return

        try:
            await member.add_roles(*guild_roles)
            await interaction.response.send_message("אימות הצליח! קיבלת את הרולים: **Member, Staff, Friend** ופתחת את הגישה לשרת. 🎉", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("התרחשה שגיאה בהענקת הרולים. ודא שהרול של הבוט נמצא בראש הרשימה בהגדרות השרת.", ephemeral=True)

# ==========================================
# חלק 2: מערכת הטיקטים (תפריט בחירה Dropdown)
# ==========================================
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="בחינות לצוות", value="team_apply", description="פתיחת טיקט להגשת מועמדות לצוות"),
            discord.SelectOption(label="עזרה כללית", value="general_help", description="פתיחת פנייה לקבלת תמיכה כללית"),
            discord.SelectOption(label="פנייה להנהלה", value="admin_help", description="פנייה דיחופה לדרגים הגבוהים")
        ]
        super().__init__(placeholder="...בחר את סוג הטיקט שברצונך לפתוח", min_values=1, max_values=1, options=options, custom_id="ticket_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        allowed_roles = ["Member", "Staff", "Friend"]
        can_open = any(role.name in allowed_roles for role in member.roles)

        if not can_open:
            await interaction.response.send_message("❌ **שגיאה:** רק משתמשים מאומתים בעלי הרולים המתאימים רשאים לפתוח טיקטים בשרת!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        category_id = None
        ticket_name = ""
        embeds_to_send = []

        if self.values == "team_apply":
            category_id = 1485440385206456452
            ticket_name = f"💡-בחינות-{member.name}"

            embed1 = discord.Embed(title="📋 טופס מועמדות לצוות השרת - חלק א'", description=f"שלום {member.mention}, אנא ענה על השאלות הבאות בהודעה מפורטת אחת:", color=0x5865F2)
            embed1.add_field(name="1. פרטים אישיים", value="שם מלא (שלך) / כינוי בדיסקורד:", inline=False)
            embed1.add_field(name="2. גיל", value="מה הגיל שלך?", inline=False)
            embed1.add_field(name="3. ותק בשרת", value="כמה זמן אתה בשרת שלנו?", inline=False)
            embed1.add_field(name="4. ניסיון קודם", value="ניסיון קודם בצוות ניהול / מודרטור? ספר קצת.. ואם עזבת אז מדוע? (שלח הוכחה במידה ויש)", inline=False)
            embed1.add_field(name="5. הגדרת חבר צוות", value="איך אתה מגדיר צוות טוב? מה בעינייך התכונות שצריכות להיות לחבר צוות?", inline=False)
            embed1.add_field(name="6. התמודדות עם סיטואציות", value="בתור צוות, מה היית עושה במידה ויש סיטואציה פחות נעימה בחדרי השרת / הוויס (מישהו מתחצף / עובר על החוקים, ריבים בין כמה חברי השרת)? תן דוגמה:", inline=False)
            embed1.add_field(name="7. היררכיה וסמכות", value="איך היית מגיב אם צוות מתחתיך תוקף אותך? ואיך היית מגיב אם הוא היה מעליך?", inline=False)

            embed2 = discord.Embed(title="📋 טופס מועמדות לצוות השרת - חלק ב'", color=0x5865F2)
            embed2.add_field(name="8. זמינות וזמן השקעה", value="כמה זמן בערך אתה חושב שתוכל לתת ממך למען השרת בשבוע כל יום?", inline=False)
            embed2.add_field(name="9. התמודדותstyle לחוסר פעילות", value="במידה והשרת מתחיל טיפה להראות חוסר פעילות האם לדעתך תוכל לשנות את המצב? איך?", inline=False)
            embed2.add_field(name="10. תחומי עניין", value="באיזה תחומים אתה רוצה לעזור בשרת?", inline=False)
            embed2.add_field(name="11. תרומה ושאיפות", value="איך אתה חושב שתוכל לתרום לשרת, וכמה רחוק אתה חושב שתוכל להגיע?", inline=False)
            embed2.add_field(name="12. מוטיבציה", value="מאיפה הרצון להצטרף לצוות?", inline=False)
            embed2.add_field(name="13. התאמה ושיפורים", value="למה דווקא אתה מתאים לצוות שלנו? יש לך רעיון לשיפור השרת?", inline=False)
            embed2.add_field(name="14. אבטחת חשבון", value="האם יש לך 2FA (אימות דו-שלבי)?", inline=False)
            embed2.set_footer(text="צוות Voice Chat Server מאחל לך בהצלחה!")

            embeds_to_send = [embed1, embed2]

        elif self.values == "general_help":
            category_id = 1488259168593772554
            ticket_name = f"🎫-עזרה-{member.name}"

            embed = discord.Embed(title="🎫 פנייה בנושא עזרה כללית", description=f"שלום {member.mention},\nפתחת פנייה בנושא עזרה כללית בשרת.\n\n**אנא רשום כאן את שאלתך או את הבעיה בצורה מפורטת**, וחבר צוות יתפנה לעזור לך בהקדם!", color=0x57F287)
            embed.set_footer(text="Voice Chat Server Support")
            embeds_to_send = [embed]

        elif self.values == "admin_help":
            category_id = 1485440480459227227
            ticket_name = f"👑-הנהלה-{member.name}"

            embed = discord.Embed(title="👑 פנייה דחופה להנהלת השרת", description=f"שלום {member.mention},\nפנייתך הופנתה ישירות לדרגים הגבוהים ומנהלי השרת.\n\nאנא רשום את סיבת הפנייה ופירוט מלא של המקרה.", color=0xED4245)
            embed.set_footer(text="Voice Chat Server Management")
            embeds_to_send = [embed]

        if category_id:
            category = discord.utils.get(guild.categories, id=category_id)
            # תיקון הסוגר המסולסל שהיה חסר בשורה הבאה:
            overwrites = {





# ====== הרצת הבוט בצורה מאובטחת ======
import os
bot.run(os.getenv('DISCORD_TOKEN'))





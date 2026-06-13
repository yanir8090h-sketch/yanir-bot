import discord
from discord.ext import commands
import os
import json

# הגדרת ה-Intents בצורה תקינה באותיות קטנות (פותר את בעיית הבוט שלא מגיב)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# מילון לשמירת ה-XP של המשתמשים (מחובר למערכת שלך)
user_xp = {}

# פונקציה מדומה לטעינת XP (אם יש לך קובץ JSON קיים בקוד, הוא ייטען כאן)
try:
    with open("xp.json", "r") as f:
        user_xp = json.load(f)
except FileNotFoundError:
    user_xp = {}

def save_xp():
    with open("xp.json", "w") as f:
        json.dump(user_xp, f)

# -------------------------------------------------------------
# 🔒 1. מערכת אימות וסינון (Verify System)
# -------------------------------------------------------------
class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # פועל 24/7

    @discord.ui.button(label="לחץ כאן לאימות 🔐", style=discord.ButtonStyle.success, custom_id="verify_member_button")
    async def verify_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        member = interaction.user
        
        ROLE_NAME = "Member"
        role = discord.utils.get(guild.roles, name=ROLE_NAME)

        if not role:
            await interaction.followup.send(f"❌ שגיאה: הרול `{ROLE_NAME}` לא נמצא בשרת.", ephemeral=True)
            return

        if role in member.roles:
            await interaction.followup.send("⭐ אתה כבר מאומת בשרת!", ephemeral=True)
            return

        try:
            await member.add_roles(role)
            await interaction.followup.send(f"🎉 אימות בוצע בהצלחה! קיבלת את הרול **{ROLE_NAME}**.", ephemeral=True)
            
            # הודעת ברוכים הבאים אוטומטית בערוץ #ברוכים-הבאים
            welcome_channel = discord.utils.get(guild.text_channels, name="ברוכים-הבאים")
            if welcome_channel:
                welcome_embed = discord.Embed(
                    title=f"👋 ברוכים הבאים ל- {guild.name}!",
                    description=f"המבוט המוכשר {member.mention} עבר את האימות בהצלחה והצטרף אלינו! 🎉\nתתחיל לדבר בצ'אט ולצבור XP!",
                    color=0x2ecc71
                )
                welcome_embed.set_thumbnail(url=member.display_avatar.url)
                if guild.icon:
                    welcome_embed.set_image(url=guild.icon.url)
                welcome_embed.set_footer(text=f"משתמש מספר {guild.member_count} בשרת")
                await welcome_channel.send(embed=welcome_embed)
        except discord.Forbidden:
            await interaction.followup.send("❌ לבוט אין הרשאה לתת רולים! תעלה את הרול של הבוט מעל הרול Member.", ephemeral=True)

@bot.command(name="setup_verify")
@commands.has_permissions(administrator=True)
async def setup_verify(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🔒 מערכת אימות וסינון המשתמשים",
        description="ברוכים הבאים לשרת! על מנת לקבל גישה מלאה לכל החדרים, הערוצים, ומערכת ה-XP שלנו,\n"
                    "עליכם לעבור את מערכת הסינון האוטומטית.\n\n"
                    "**לחצו על הכפתור הירוק למטה כדי לקבל רול Member!**",
        color=0x2ecc71
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.set_footer(text=f"{ctx.guild.name} | מערכת הגנה רשמית", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
    await ctx.send(embed=embed, view=VerifyButton())

# -------------------------------------------------------------
# 🚨 2. מערכת קריאה לעזרה/דיווחים (Help System)
# -------------------------------------------------------------
class HelpStaffView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="נלקח על ידי", style=discord.ButtonStyle.secondary, emoji="🛡️", custom_id="claim_help")
    async def claim_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ כפתור זה מיועד לצוות השרת בלבד!", ephemeral=True)
            return

        await interaction.response.defer()
        embed = interaction.message.embeds[0]
        
        field_updated = False
        for i, field in enumerate(embed.fields):
            if "נלקח על ידי" in field.name:
                embed.set_field_at(i, name="🤝 נלקח על ידי", value=f"{interaction.user.mention}", inline=False)
                field_updated = True
                break
        if not field_updated:
            embed.add_field(name="🤝 נלקח על ידי", value=f"{interaction.user.mention}", inline=False)

        embed.color = discord.Color.green()
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        await interaction.channel.send(f"⚡ הפנייה של המשתמש נלקחה לטיפול על ידי {interaction.user.mention}!")

@bot.command(name="h", aliases=["help"])
async def h(ctx, *, reason: str = None):
    if not reason:
        await ctx.send("⚠️ נא לציין את סיבת הפנייה! דוגמה: `!h יש בעיה בצ'אט`")
        return
    await ctx.message.delete()
    
    # כאן תוכל לשים קישור לבאנר הסגול שעיצבת
    HELP_BANNER_URL = "https://imgur.com"

    embed = discord.Embed(
        title="🚨 בקשת עזרה / דיווח חדש",
        description="איש צוות זמין נדרש להגיע לסייע.",
        color=0xe74c3c
    )
    embed.add_field(name="👤 המבקש", value=f"{ctx.author.mention}", inline=True)
    embed.add_field(name="💬 סיבה / פירוט", value=f"```{reason}```", inline=False)
    embed.add_field(name="🤝 נלקח על ידי", value="טרם נלקח - ממתין לצוות ⏳", inline=False)
    
    embed.set_image(url=HELP_BANNER_URL)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text=f"Help System • {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
    await ctx.send(embed=embed, view=HelpStaffView())

# -------------------------------------------------------------
# 🛠️ 3. מערכת בקשות חברים לצוות (Staff Friends System)
# -------------------------------------------------------------
class StaffFriendButtons(discord.ui.View):
    def __init__(self, requester: discord.Member, target_user: str):
        super().__init__(timeout=None)
        self.requester = requester
        self.target_user = target_user

    @discord.ui.button(label="Accept | אישור", style=discord.ButtonStyle.success, emoji="🟢", custom_id="accept_friend")
    async def accept_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ רק מנהלי השרת רשאים לאשר בקשות זו!", ephemeral=True)
            return

        await interaction.response.defer()
        embed = interaction.message.embeds[0]
        embed.title = "✅ הבקשה אושרה בהצלחה"
        embed.color = discord.Color.green()
        
        for i, field in enumerate(embed.fields):
            if "סטטוס" in field.name:
                embed.set_field_at(i, name="🟢 סטטוס", value=f"אושר על ידי {interaction.user.mention}\n⏰ זמן טיפול: הרגע", inline=False)

        await interaction.message.edit(embed=embed, view=None)

    @discord.ui.button(label="Deny | דחייה", style=discord.ButtonStyle.danger, emoji="🔴", custom_id="deny_friend")
    async def deny_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ רק מנהלי השרת רשאים לדחות בקשות זו!", ephemeral=True)
            return

        await interaction.response.defer()
        embed = interaction.message.embeds[0]
        embed.title = "❌ הבקשה נדחתה"
        embed.color = discord.Color.red()
        
        for i, field in enumerate(embed.fields):
            if "סטטוס" in field.name:
                embed.set_field_at(i, name="🔴 סטטוס", value=f"נדחה על ידי {interaction.user.mention}\n⏰ זמן טיפול: הרגע", inline=False)

        await interaction.message.edit(embed=embed, view=None)

@bot.command(name="staff_friend", aliases=["sfriend"])
async def staff_friend(ctx, member_mention: str = None):
    if not member_mention:
        await ctx.send("⚠️ נא לתייג את המשתמש שברצונך להוסיף! דוגמה: `!staff_friend @user`")
        return
    await ctx.message.delete()
    
    STAFF_BANNER_URL = "https://imgur.com"

    embed = discord.Embed(
        title="🛠️ בקשת Staff Friend חדשה",
        description="הוגשה בקשה חדשה לצירוף חבר לדרגת סטאף פרנד בשרת.",
        color=0x9b59b6
    )
    embed.add_field(name="👤 איש צוות מגיש", value=f"{ctx.author.mention}", inline=True)
    embed.add_field(name="👥 חבר לקבלת הדרגה", value=f"{member_mention}", inline=True)
    embed.add_field(name="🟡 סטטוס", value="המתנה לאישור הנהלה גבוהה...", inline=False)
    
    embed.set_image(url=STAFF_BANNER_URL)
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.set_footer(text=f"Staff Friend System • {ctx.guild.name}")
    await ctx.send(embed=embed, view=StaffFriendButtons(ctx.author, member_mention))

# -------------------------------------------------------------
# 🎫 4. מערכת טיקטים ותמיכה (Ticket System)
# -------------------------------------------------------------
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="עזרה כללית", description="לפניות ותמיכה כללית בשרת", emoji="📁"),
            discord.SelectOption(label="בחינה לצוות", description="בירורים לגבי קבלה לצוות השרת", emoji="📝"),
            discord.SelectOption(label="עזרה מההנהלה", description="פניות רגישות ודחופות להנהלה הגבוהה", emoji="👑")
        ]
        super().__init__(placeholder="בחר את סוג הפנייה שלך מתוך הרשימה...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

import os
bot.run(os.getenv("DISCORD_TOKEN"))

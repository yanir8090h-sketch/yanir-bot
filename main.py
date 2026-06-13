import discord
from discord.ext import commands
import os
import random
import asyncio

# הגדרות בסיס ואינטנטים
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# מילון ה-XP המקורי
user_xp = {}

# ==========================================
# 🔒 מערכת אימות (VERIFY SYSTEM)
# ==========================================
class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

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
            
            welcome_channel = discord.utils.get(guild.text_channels, name="ברוכים-הבאים")
            if welcome_channel:
                welcome_embed = discord.Embed(
                    title=f"👋 ברוכים הבאים ל- {guild.name}!",
                    description=f"המשתמש {member.mention} עבר את האימות בהצלחה והצטרף אלינו! 🎉\nתתחיל לדבר בצ'אט ולצבור XP!",
                    color=0x2ecc71
                )
                welcome_embed.set_thumbnail(url=member.display_avatar.url)
                if guild.icon:
                    welcome_embed.set_image(url=guild.icon.url)
                welcome_embed.set_footer(text=f"משתמש מספר {guild.member_count} בשרת")
                await welcome_channel.send(embed=welcome_embed)
        except discord.Forbidden:
            await interaction.followup.send("❌ לבוט אין הרשאה לתת רולים!", ephemeral=True)

# ==========================================
# 📝 מערכת טיקטים וטופס מועמדות לצוות
# ==========================================
class StaffFormModal(discord.ui.Modal, title="📝 טופס מועמדות לצוות השרת"):
    name_input = discord.ui.TextInput(label="שם מלא / כינוי בדיסקורד", placeholder="ישראל ישראלי", required=True)
    age_input = discord.ui.TextInput(label="גיל", placeholder="למשל: 16", required=True)
    time_input = discord.ui.TextInput(label="כמה זמן אתה בשרת שלנו?", placeholder="למשל: חודשיים", required=True)
    exp_input = discord.ui.TextInput(label="ניסיון קודם בניהול? (פרט בקצרה)", style=discord.TextStyle.long, required=True)
    why_input = discord.ui.TextInput(label="למה דווקא אתה מתאים לצוות?", style=discord.TextStyle.long, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        member = interaction.user
        category_id = 1245448484859227227

        category = discord.utils.get(guild.categories, id=category_id)
        if not category:
            await interaction.followup.send("❌ שגיאה: קטגוריית הטיקטים לא נמצאה בשרת. ודא שה-ID נכון בקוד!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        channel = await guild.create_text_channel(name=f"📝-צוות-{member.name}", category=category, overwrites=overwrites)

        embed = discord.Embed(title="📝 הגשת מועמדות חדשה לצוות", color=0x9b59b6)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤 מגיש הטופס", value=member.mention, inline=False)
        embed.add_field(name="1. שם מלא / כינוי", value=self.name_input.value, inline=True)
        embed.add_field(name="2. גיל", value=self.age_input.value, inline=True)
        embed.add_field(name="3. זמן בשרת", value=self.time_input.value, inline=True)
        embed.add_field(name="4. ניסיון קודם", value=self.exp_input.value, inline=False)
        embed.add_field(name="13. למה מתאים", value=self.why_input.value, inline=False)
        embed.set_footer(text=f"Staff System • {guild.name}")

        await channel.send(embed=embed)

        continued_questions = (
            f"👋 שלום {member.mention}, החלק הראשון של הטופס נשלח בהצלחה לצוות!\n"
            f"על מנת להשלים את המועמדות שלך, **אנא ענה כאן בחדר על שאר השאלות הבאות:**\n\n"
            "**5.** איך אתה מגדיר צוות טוב? מה בעינייך התכונות שצריכות להיות לחבר צוות?\n"
            "**6.** בתור צוות, מה היית עושה במידה ויש סיטואציה פחות נעימה בחדרי השרת (ריבים, מישהו מתחצף)? תן דוגמה.\n"
            "**7.** איך היית מגיב אם איש צוות מתחתיך תוקף אותך? ואיך היית מגיב אם הוא היה מעליך?\n"
            "**8.** כמה זמן בשבוע/כל יום תוכל להשקיע לטובת השרת?\n"
            "**9.** במידה והשרת מראה חוסר פעילות, איך לדעתך תוכל לשנות את המצב?\n"
            "**10.** באיזה תחומים תרצה לעזור בשרת?\n"
            "**11.** איך תוכל לתרום לשרת, וכמה רחוק אתה שואף להגיע?\n"
            "**12.** מאיפה הרצון להצטרף לצוות?\n"
            "**14.** האם יש לך אבטחת 2FA מופעלת בדיסקורד?\n\n"
            "*יש לך רעיון נוסף לשיפור השרת? רשום אותו כאן בסוף!*"
        )
        await channel.send(continued_questions)
        await interaction.followup.send(f"✅ הטיקט שלך נפתח! לחץ כאן למעבר: {channel.mention}", ephemeral=True)

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="עזרה כללית", description="לפניות ותמיכה כללית בשרת", emoji="📁"),
            discord.SelectOption(label="בחינה לצוות", description="טופס הגשת מועמדות לצוות השרת", emoji="📝"),
            discord.SelectOption(label="עזרה מההנהלה", description="פניות רגישות ודחופות להנהלה הגבוהה", emoji="👑")
        ]
        super().__init__(placeholder="בחר את סוג הפנייה שלך מתוך הרשימה...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        
        if selected_value == "בחינה לצוות":
            await interaction.response.send_modal(StaffFormModal())
            return

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        member = interaction.user
        category_id = 1245448484859227227
        
        clean_name = selected_value.replace(" ", "-")
        ticket_name = f"🎫-{clean_name}-{member.name}"
        category = discord.utils.get(guild.categories, id=category_id)
        
        if not category:
            await interaction.followup.send("❌ שגיאה: קטגוריית הטיקטים לא נמצאה בשרת.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        
        channel = await guild.create_text_channel(name=ticket_name, category=category, overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎯 פנייתך התקבלה בהצלחה",
            description=f"שלום {member.mention},\nנפתח עבורך חדר טיקט בנושא **{selected_value}**.\nאנא פרט את פנייתך בצורה ברורה, ונציג מצוות השרת יתפנה אליך בהקדם.",
            color=0x004245
        )
        await channel.send(embed=embed)
        await interaction.followup.send(f"✅ הטיקט שלך נוצר! לחץ כאן למעבר: {channel.mention}", ephemeral=True)

class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

@bot.command(name="setup_tickets")
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx):
    await ctx.message.delete()
    
    embed = discord.Embed(
        title="תמיכה ופניות • הגשת מועמדות",
        description="צריך עזרה? רוצה להגיש מועמדות לצוות השרת?\nבחר את הקטגוריה המתאימה ביותר בתפריט למטה והבוט יפתח לך חדר פרטי מיידית.\n\n⚠️ **חוקי המערכת:**\n• אין לפתוח טיקטים ללא סיבה מוצדקת.\n• הגשת טופס מועמדות שקרי או מזלזל תיפסל מיידית.",
        color=0x004245
    )
    # תיקון: משיכת לוגו השרת באופן אוטומטי ללא צורך בלינקים חיצוניים פגומים
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
        
    await ctx.send(embed=embed, view=TicketDropdownView())

# ==========================================
# 🚨 פקודת עזרה (HELP STAFF COMMAND)
# ==========================================
# ==========================================
# 🚨 פקודת עזרה (HELP STAFF COMMAND)
# ==========================================
class HelpStaffView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="נלקח על ידי", style=discord.ButtonStyle.secondary, emoji="🛡️", custom_id="claim_help")
    async def claim_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ כפתור זה מיועד לצוות השרת בלבד!", ephemeral=True)
            return

        await interaction.response.defer()
        embed = interaction.message.embeds
        
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

@bot.command(name="h", aliases=["עזרה"])
async def h(ctx, *, reason: str = None):
    if not reason:
        await ctx.send("⚠️ נא לציין את סיבת הפנייה! דוגמה: `!h יש בעיה בצ'אט`")
        return

    await ctx.message.delete()

    embed = discord.Embed(
        title="🚨 בקשת עזרה / דיווח חדש",
        description="איש צוות זמין נדרש להגיע לסייע.",
        color=0xe74c3c
    )
    embed.add_field(name="👤 המבקש", value=f"{ctx.author.mention}", inline=True)
    embed.add_field(name="💬 סיבה / פירוט", value=f"```{reason}```", inline=False)
    embed.add_field(name="🤝 נלקח על ידי", value="טרם נלקח - ממתין לצוות ⏳", inline=False)
    
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text=f"Help System • {ctx.guild.name}")

    await ctx.send(embed=embed, view=HelpStaffView())



import os
bot.run(os.getenv("DISCORD_TOKEN"))

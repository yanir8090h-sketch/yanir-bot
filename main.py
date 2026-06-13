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
        
        # ה-ID של רול האימות ששלחת
        ROLE_ID = 1487501792488067182
        role = guild.get_role(ROLE_ID)

        if not role:
            await interaction.followup.send("❌ שגיאה: רול האימות לא נמצא בשרת.", ephemeral=True)
            return

        if role in member.roles:
            await interaction.followup.send("⭐ אתה כבר מאומת בשרת!", ephemeral=True)
            return

        try:
            await member.add_roles(role)
            await interaction.followup.send(f"🎉 אימות בוצע בהצלחה! קיבלת את הרול **{role.name}**.", ephemeral=True)
            
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
# 📝 מערכת טיקטים (TICKETS SYSTEM)
# ==========================================
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="עזרה כללית", description="לפניות ותמיכה כללית בשרת", emoji="📁"),
            discord.SelectOption(label="בחינה לצוות", description="טופס הגשת מועמדות לצוות השרת", emoji="📝"),
            discord.SelectOption(label="עזרה מההנהלה", description="פניות רגישות ודחופות להנהלה הגבוהה", emoji="👑")
        ]
        super().__init__(placeholder="בחר את סוג הפנייה שלך מתוך הרשימה...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        selected_value = self.values[0]
        guild = interaction.guild
        member = interaction.user
        
        # ה-ID של קטגוריית הטיקטים ששלחת
        category_id = 1480327808445059072
        category = guild.get_channel(category_id)
        
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.followup.send("❌ שגיאה: קטגוריית הטיקטים לא נמצאה בשרת.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        
        clean_name = selected_value.replace(" ", "-")
        ticket_name = f"🎫-{clean_name}-{member.name}"
        
        channel = await guild.create_text_channel(name=ticket_name, category=category, overwrites=overwrites)
        
               if selected_value == "בחינה לצוות":
            embed = discord.Embed(
                title="📝 טופס מועמדות לצוות השרת - Voice Chat Server",
                description=f"שלום {member.mention},\nעל מנת להגיש מועמדות לצוות, **אנא העתק את השאלות הבאות, וענה עליהן בצורה מפורשת ומושקעת כאן בצ'אט:**\n\n"
                            "**1.** שם מלא (שלך) / כינוי בדיסקורד:\n"
                            "**2.** גיל:\n"
                            "**3.** כמה זמן אתה בשרת שלנו?\n"
                            "**4.** ניסיון קודם בצוות ניהול / מודרטור? ספר קצת.. ואם עזבת אז מדוע? (שלח הוכחה במידה ויש)\n"
                            "**5.** איך אתה מגדיר צוות טוב? מה בעינייך התכונות שצריכות להיות לחבר צוות?\n"
                            "**6.** בתור צוות, מה היית עושה במידה ויש סיטואציה פחות נעימה בחדרי השרת / הוויס (מישהו מתחצף/עובר על החוקים, ריבים)? תן דוגמה:\n"
                            "**7.** איך היית מגיב אם איש צוות מתחתיך תוקף אותך? ואיך היית מגיב אם הוא היה מעליך?\n"
                            "**8.** כמה זמן בערך אתה חושב שתוכל לתנת ממך למען השרת בשבוע כל יום?\n"
                            "**9.** במידה והשרת מתחיל טיפה להראות חוסר פעילות האם לדעתך תוכל לשנות את המצב? איך?\n"
                            "**10.** באיזה תחומים אתה רוצה לעזור בשרת?\n"
                            "**11.** איך אתה חושב שתוכל לתרום לשרת, וכמה רחוק אתה חושב שתוכל להגיע?\n"
                            "**12.** מאיפה הרצון להצטרף לצוות?\n"
                            "**13.** למה דווקא אתה מתאים לצוות שלנו? יש לך רעיון לשיפור השרת?\n"
                            "**14.** האם יש לך אבטחת 2FA מופעלת בדיסקורד?\n\n"
                            "📌 *צוות הניהול הגבוה יעבור על התשובות שלך וייתן לך תשובה בהקדם! בהצלחה!*",
                color=0x9b59b6
            )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            await channel.send(embed=embed)
        else:

        else:
            embed = discord.Embed(
                title="🎯 פנייתך התקבלה בהצלחה",
                description=f"שלום {member.mention},\nנפתח עבורך חדר טיקט בנושא **{selected_value}**.\nאנא פרט את פנייתך בצורה ברורה, ונציג מצוות השרת יתפנה אליך בהקדם.",
                color=0x004245
            )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            await channel.send(embed=embed)
            
        await interaction.followup.send(f"✅ הטיקט שלך נוצר בהצלחה! לחץ כאן למעבר: {channel.mention}", ephemeral=True)

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
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=TicketDropdownView())

# ==========================================
# 🛒 חנות רולים בלחיצת כפתור (XP SHOP SYSTEM)
# ==========================================
class ShopButton(discord.ui.Button):
    def __init__(self, label, role_id, cost, custom_id):
        super().__init__(label=f"{label} - {cost:,} XP", style=discord.ButtonStyle.primary, custom_id=custom_id)
        self.role_id = role_id
        self.cost = cost

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        current_xp = user_xp.get(user_id, 0)
        guild = interaction.guild
        role = guild.get_role(self.role_id)

        if not role:
            await interaction.followup.send("❌ שגיאה: רול זה לא נמצא בשרת.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.followup.send(f"⭐ כבר יש לך את הרול **{role.name}**!", ephemeral=True)
            return

        if current_xp < self.cost:
            await interaction.followup.send(f"❌ אין לך מספיק XP! חסר לך עוד `{self.cost - current_xp:,}` XP כדי לרכוש את הרול.", ephemeral=True)
            return

        try:
            user_xp[user_id] -= self.cost
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"🎉 תתחדש! רכשת בהצלחה את הרול **{role.name}** עבור `{self.cost:,}` XP!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ לבוט אין הרשאה להעניק רולים. ודא שהתפקיד של הבוט נמצא גבוה יותר ב-Roles.", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # הוספת 5 הכפתורים עם ה-IDs והמחירים המדויקים ששלחת
        self.add_item(ShopButton("רול 1", 1491063689502003360, 5000, "shop_role_1"))
        self.add_item(ShopButton("רול 2", 1490894966262726687, 15000, "shop_role_2"))
        self.add_item(ShopButton("רול 3", 1490894895618195577, 20000, "shop_role_3"))
        self.add_item(ShopButton("רול 4", 1490894817373196388, 25000, "shop_role_4"))
        self.add_item(ShopButton("רול 5", 1484226514051665930, 30000, "shop_role_5"))

@bot.command(name="setup_shop")
@commands.has_permissions(administrator=True)
async def setup_shop(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🛒 חנות הרולים הרשמית של השרת",
        description="צברתם מספיק נקודות XP מהדיבורים בצ'אט ומהמשחקים?\nזה הזמן להחליף אותם ברולים בלעדיים ויוקרתיים בשרת!\n\n**לחצו על אחד הכפתורים למטה כדי לרכוש את הרול מיידית:**",
        color=0xe67e22
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)


import os
bot.run(os.getenv("DISCORD_TOKEN"))

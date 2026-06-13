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

# מילון ה-XP המקורי של השרת
user_xp = {}

# מערכת הגדרות ה-IDs ששלחת
CATEGORY_TICKETS_ID = 1480327808445059072
CHANNEL_XP_ID = 1483946813944758413
CHANNEL_XP_SHOP_ID = 1484129709414416434
CHANNEL_VERIFY_ID = 1487501792488067182

# רשימת הרולים והמחירים לחנות
SHOP_ROLES = {
    1491063689502003360: 5000,
    1490894966262726687: 15000,
    1490894895618195577: 20000,
    1490894817373196388: 25000,
    1484226514051665930: 30000
}

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
        
        role = discord.utils.get(guild.roles, name="Member")
        if not role:
            await interaction.followup.send("❌ שגיאה: הרול `Member` לא נמצא בשרת.", ephemeral=True)
            return

        if role in member.roles:
            await interaction.followup.send("⭐ אתה כבר מאומת בשרת!", ephemeral=True)
            return

        try:
            await member.add_roles(role)
            await interaction.followup.send("🎉 אימות בוצע בהצלחה! קיבלת את הרול **Member**.", ephemeral=True)
            
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

@bot.command(name="setup_verify")
@commands.has_permissions(administrator=True)
async def setup_verify(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🔒 מערכת אימות וסינון המשתמשים",
        description="ברוכים הבאים לשרת! על מנת לקבל גישה מלאה לכל החדרים והערוצים,\nעליכם למזער סיכונים ולעבור אימות.\n\n**לחצו על הכפתור הירוק למטה כדי לקבל רול Member!**",
        color=0x2ecc71
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=VerifyButton())

# ==========================================
# 🛒 חנות רולים בלחיצת כפתור (XP SHOP SYSTEM)
# ==========================================
class ShopButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    async def process_purchase(self, interaction: discord.Interaction, role_id: int, cost: int):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        current_xp = user_xp.get(user_id, 0)
        
        if current_xp < cost:
            await interaction.followup.send(f"❌ אין לך מספיק XP! הרול עולה **{cost} XP** ויש לך כרגע **{current_xp} XP**.", ephemeral=True)
            return
            
        guild = interaction.guild
        role = guild.get_role(role_id)
        
        if not role:
            await interaction.followup.send("❌ שגיאה: הרול הזה לא נמצא בשרת, פנה למנהל.", ephemeral=True)
            return
            
        if role in interaction.user.roles:
            await interaction.followup.send(f"⭐ כבר יש לך את הרול {role.mention}!", ephemeral=True)
            return
            
        try:
            user_xp[user_id] -= cost
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"🎉 תתחדש! קנית את הרול {role.mention} בהצלחה עבור **{cost} XP**!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ לבוט אין הרשאה להעניק רולים. ודא שהרול של הבוט נמצא בראש הרשימה!", ephemeral=True)

    @discord.ui.button(label="קניית רול דרגה 1 • 5,000 XP", style=discord.ButtonStyle.primary, custom_id="shop_r1")
    async def r1_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_purchase(interaction, 1491063689502003360, 5000)

    @discord.ui.button(label="קניית רול דרגה 2 • 15,000 XP", style=discord.ButtonStyle.primary, custom_id="shop_r2")
    async def r2_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_purchase(interaction, 1490894966262726687, 15000)

    @discord.ui.button(label="קניית רול דרגה 3 • 20,000 XP", style=discord.ButtonStyle.primary, custom_id="shop_r3")
    async def r3_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_purchase(interaction, 1490894895618195577, 20000)

    @discord.ui.button(label="קניית רול דרגה 4 • 25,000 XP", style=discord.ButtonStyle.primary, custom_id="shop_r4")
    async def r4_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_purchase(interaction, 1490894817373196388, 25000)

    @discord.ui.button(label="קניית רול דרגה 5 • 30,000 XP", style=discord.ButtonStyle.primary, custom_id="shop_r5")
    async def r5_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_purchase(interaction, 1484226514051665930, 30000)

@bot.command(name="setup_shop")
@commands.has_permissions(administrator=True)
async def setup_shop(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🛒 חנות הרולים הרשמית של השרת",
        description="צברתם מספיק נקודות פעילות בצ'אט ובוויס?\nזה הזמן להתקדם ולהשוויץ בדירוג שלכם בשרת!\n\n**לחצו על אחד הכפתורים למטה כדי לרכוש את הרול המתאים:**",
        color=0xe67e22
    )
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=ShopButtons())

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
        selected_value = self.values
        guild = interaction.guild
        member = interaction.user
        
        category = discord.utils.get(guild.categories, id=CATEGORY_TICKETS_ID)
        if not category:
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
                            "**9.** במידה והשרת מתחיל טיפה להראות חוססר פעילות האם לדעתך תוכל לשנות את המצב? איך?\n"
                            "**10.** באיזה תחומים אתה רוצה לעזור בשרת?\n"
                            "**11.** איך אתה חושב שתוכל לתרום לשרת, וכמה רחוק אתה חושב שתוכל להגיע?\n"
                            "**12.** מאיפה הרצון להצטרף לצוות?\n"
                            "**13.** למה דווקא אתה מתאים לצוות שלנו? יש לך רעיון לשיפור השרת?\n"
                            "**14.** האם יש לך אבטחת 2FA מופעלת בדיסקורד?\n\n"



import os
bot.run(os.getenv("DISCORD_TOKEN"))

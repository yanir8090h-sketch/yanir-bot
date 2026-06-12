import discord
from discord.ext import commands
import random
import asyncio

# הגדרות הרשאות ובוט
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# יצירת הבוט עם הגדרת הפרוקסי של PythonAnywhere
bot = commands.Bot(command_prefix="!", intents=intents)


# מאגרי נתונים זמניים בזיכרון
xp_data = {}  # user_id: xp
inventory = {}  # user_id: [items]

# מחירי חנות ה-XP
SHOP_ITEMS = {
    "צבע_לשם_זהב": 500,
    "רול_VIP": 1500,
    "תואר_אלוף": 3000
}

# --- הגדרות איידי מותאמות אישית לשרת שלך ---
STAFF_LOG_CHANNEL_ID = 123456789012345678  # איידי של ערוץ אליו יישלחו טפסי המועמדות לצוות
TICKET_CATEGORY_ID = 123456789012345678    # איידי של הקטגוריה שבה ייפתחו חדרי הטיקטים הסודיים
VERIFY_ROLE_ID = 123456789012345678        # איידי של הרול שנקרא "Member" בשרת שלך

# --- הגדרות איידי של רולי הצוות והתפקידים ---
ROLE_STAFF = 1488259168593772554           # רול @STAFF - הבלעדי שיכול להגיש ולטפל!
ROLE_STAFF_FRIEND = 1493335218004820180    # רול @Staff Friend שמוענק באישור
ROLE_MANAGEMENT = 1485440480459227227      # רול בעל גישה לטיקט עזרה מההנהלה
ROLE_GENERAL_HELP = 1485680386972455042    # רול בעל גישה לטיקט עזרה כללית

# פונקציית עזר להוספת XP
def add_xp(user_id, amount):
    xp_data[user_id] = xp_data.get(user_id, 0) + amount

# ==========================================
# 🤝 מערכת בקשות Staff Friend (כמו בתמונה)
# ==========================================

class StaffFriendView(discord.ui.View):
    def __init__(self, target_user_id):
        super().__init__(timeout=None)
        self.target_user_id = target_user_id

    @discord.ui.button(label="אישור", style=discord.ButtonStyle.green, custom_id="accept_sf_btn")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        staff_role = guild.get_role(ROLE_STAFF)

        # רק בעלי רול STAFF יכולים ללחוץ על הכפתורים
        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message("❌ רק חברי צוות ברול @STAFF יכולים לטפל בבקשה זו!", ephemeral=True)

        target_member = guild.get_member(self.target_user_id)
        sf_role = guild.get_role(ROLE_STAFF_FRIEND)

        if target_member and sf_role:
            try:
                await target_member.add_roles(sf_role)
            except discord.Forbidden:
                return await interaction.response.send_message("❌ שגיאה: לבוט אין הרשאה להעניק את הרול הזה. ודא שהרול של הבוט נמצא מעליו ברשימה!", ephemeral=True)

        await interaction.response.defer()

        # עדכון ההודעה למצב אושר (בדיוק כמו בתמונה)
        updated_embed = interaction.message.embeds[0]
        updated_embed.color = discord.Color.green()

        # הוספת שדות העדכון
        updated_embed.add_field(name="אושר / נדחה:", value=f"✅ אושר על ידי: {interaction.user.mention}", inline=False)

        disabled_view = discord.ui.View()
        approved_btn = discord.ui.Button(label="אושר", style=discord.ButtonStyle.green, disabled=True)
        disabled_view.add_item(approved_btn)

        await interaction.message.edit(embed=updated_embed, view=disabled_view)

    @discord.ui.button(label="דחייה", style=discord.ButtonStyle.danger, custom_id="deny_sf_btn")
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        staff_role = guild.get_role(ROLE_STAFF)

        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message("❌ רק חברי צוות ברול @STAFF יכולים לטפל בבקשה זו!", ephemeral=True)

        await interaction.response.defer()

        # עדכון ההודעה למצב נדחה
        updated_embed = interaction.message.embeds[0]
        updated_embed.color = discord.Color.red()
        updated_embed.add_field(name="אושר / נדחה:", value=f"❌ נדחה על ידי: {interaction.user.mention}", inline=False)

        disabled_view = discord.ui.View()
        denied_btn = discord.ui.Button(label="נדחה", style=discord.ButtonStyle.danger, disabled=True)
        disabled_view.add_item(denied_btn)

        await interaction.message.edit(embed=updated_embed, view=disabled_view)

@bot.command(name="stafffriend_req")
async def staff_friend_req_cmd(ctx, member: discord.Member = None):
    # בדיקה שרק בעל רול STAFF רשאי לשלוח את הפקודה
    staff_role = ctx.guild.get_role(ROLE_STAFF)
    if staff_role not in ctx.author.roles:
        return await ctx.send("❌ אין לך הרשאה להשתמש בפקודה זו! היא מיועדת לחברי צוות @STAFF בלבד.")

    if not member:
        return await ctx.send("❌ יש לתייג משתמש שברצונך לבקש עבורו את הרול! דוגמה: `!stafffriend_req @user`")

    embed = discord.Embed(
        title="⚔️ בקשת Staff Friend",
        color=discord.Color.from_rgb(47, 49, 54) # הצבע הכהה והנקי מהתמונה
    )
    embed.set_author(name="● Staff Friend Request", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

    embed.add_field(name="מגיש הבקשה:", value=ctx.author.mention, inline=True)
    embed.add_field(name="המשתמש המבוקש:", value=member.mention, inline=True)
    embed.add_field(name="הודעת מערכת:", value="הבקשה פתוחה כעת. חברי הנהלת השרת רשאים לאשר או לדחות בלחיצת כפתור.", inline=False)

    # הוספת תמונת הבאנר היפה של השרת שלכם בתחתית ההודעה (כמו שרואים בתמונה)
    embed.set_image(url="https://discordapp.net") # שנה לקישור הבאנר של השרת שלך
    embed.set_footer(text=f"{ctx.guild.name} | מערכת תפקידים אוטומטית")

    await ctx.send(embed=embed, view=StaffFriendView(member.id))
    try: await ctx.message.delete()
    except: pass

# ==========================================
# 🛑 שאר המערכות הקודמות (Claim, Tickets, XP, Verify, Shop)
# ==========================================

class ClaimTicketView(discord.ui.View):
    def __init__(self, help_type):
        super().__init__(timeout=None)
        self.help_type = help_type

    @discord.ui.button(label="טפל כאן", style=discord.ButtonStyle.green, custom_id="claim_btn")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        staff_role = guild.get_role(ROLE_STAFF)
        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message("❌ רק חברי צוות @STAFF יכולים לקחת פנייה זו!", ephemeral=True)
        await interaction.response.defer()

        claimed_embed = discord.Embed(color=discord.Color.from_rgb(47, 49, 54))
        claimed_embed.set_author(name="● Help Request Handled", icon_url=guild.icon.url if guild.icon else None)
        claimed_embed.add_field(name="אחראי:", value=interaction.user.mention, inline=False)

        if self.help_type == "help":
            claimed_embed.add_field(name="סיבה:", value="🔊 פקודת עזרה כללית של השרת", inline=False)
            commands_text = "**🛠️ ניהול ואבטחה:**\n`!setup_verify` | `!setup_ticket`\n\n**🎮 משחקים ו-XP:**\n`!xp_games` | `!gamma`\n\n**💰 כלכלת שרת:**\n`!xp` | `!shop`"
            claimed_embed.add_field(name="הודעת מערכת (רשימת פקודות):", value=commands_text, inline=False)
        else:
            claimed_embed.add_field(name="סיבה:", value="🔊 מרכז משחקי ה-XP המלא", inline=False)
            games_text = "✊ `!rps` - אבן נייר ומספריים\n🔮 `!guess` - ניחוש מספר 1-5\n⚽ `!football` - בעיטת פנדל\n🃏 `!blackjack` - משחק הקלפים 21\n🎁 `!gamble` - תיבת המתנה בכפתורים\n🪙 `!coinsflip` - הטלת מטבע עץ/פלי\n🧮 `!mathquiz` - תרגיל מתמטיקה\n🎰 `!slot` - מכונת מזל"
            claimed_embed.add_field(name="הודעת מערכת (רשימת משחקים):", value=games_text, inline=False)

        disabled_view = discord.ui.View()
        close_btn = discord.ui.Button(label="סגור טיקט", style=discord.ButtonStyle.danger, disabled=True)
        disabled_view.add_item(close_btn)
        await interaction.message.edit(embed=claimed_embed, view=disabled_view)

class VerifyView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="✅ לחץ כאן לאימות", style=discord.ButtonStyle.green, custom_id="verify_member_btn")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        role = guild.get_role(VERIFY_ROLE_ID)
        if not role: return await interaction.response.send_message("❌ רול לא נמצא.", ephemeral=True)
        if role in interaction.user.roles: return await interaction.response.send_message("ℹ️ אתה כבר מאומת!", ephemeral=True)
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("🎉 אימות עבר בהצלחה!", ephemeral=True)
        except: pass

# ==================== קוד חנות ה-XP החדשה ====================

SHOP_ROLES = {
    "VIP": 500,
    "תואר_אלוף": 1500,
    "VIP_פלוס": 3000,
    "תואר_אגדה": 5000,
    "מלך_השרת": 10000
}


class XpShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="קניית VIP (500 XP)", style=discord.ButtonStyle.green, custom_id="buy_vip_btn")
    async def buy_vip(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name="VIP")
        if not role:
            await interaction.response.send_message("❌ הרול `VIP` לא נמצא בשרת.", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message("כבר יש לך את הרול `VIP`!", ephemeral=True)
            return
        try:
            await member.add_roles(role)
            await interaction.response.send_message("🎉 תתחדש! קיבלת את הרול **VIP** בהצלחה!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ אין לבוט הרשאה. תעלה את הרול שלו גבוה יותר בהגדרות השרת.", ephemeral=True)

    @discord.ui.button(label="קניית תואר אלוף (1500 XP)", style=discord.ButtonStyle.green, custom_id="buy_aluf_btn")
    async def buy_aluf(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name="תואר_אלוף")
        if not role:
            await interaction.response.send_message("❌ הרול `תואר_אלוף` לא נמצא בשרת.", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message("כבר יש לך את הרול `תואר_אלוף`!", ephemeral=True)
            return
        try:
            await member.add_roles(role)
            await interaction.response.send_message("🎉 תתחדש! קיבלת את הרול **תואר אלוף** בהצלחה!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ אין לבוט הרשאה. תעלה את הרול שלו גבוה יותר בהגדרות השרת.", ephemeral=True)

@bot.command(name="shop")
async def send_shop(ctx):
    embed = discord.Embed(
        title="🛒 חנות השרת - XP SHOP",
        description="שלום, כאן תוכל לרכוש רולים ותארים מהשרת עם נקודות ה-XP שלך!\n\n**הרולים הזמינים לרכישה:**",
        color=discord.Color.purple()
    )
    embed.add_field(name="💰 500 XP", value="רול: **VIP**", inline=False)
    embed.add_field(name="💰 1500 XP", value="רול: **תואר אלוף**", inline=False)
    await ctx.send(embed=embed, view=XpShopView())

# =============================================================



    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("הכרטיס שלך נוצר בהצלחה!", ephemeral=True)

# ====== פקודת הכרטיסים בצ'אט ======
# למחוק את כל השורות האלו:

   # =============================================================

@bot.command()
async def ticket(ctx):
    embed = discord.Embed(title="יצירת כרטיס תמיכה", description="לחצו על הכפתור למטה כדי לפתוח פנייה למנהלים.", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketSetupView())





# ====== הרצת הבוט בצורה מאובטחת ======
import os
bot.run(os.getenv('DISCORD_TOKEN'))





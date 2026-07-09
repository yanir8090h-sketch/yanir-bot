"""
מערכת טיקטים לדיסקורד - discord.py
=====================================
כולל:
- פאנל מעוצב עם תפריט נפתח (Select Menu) לבחירת סוג טיקט (Staff Application / XP Shop / תמיכה כללית)
- כל embed מעוצב עם צבע אחיד ותמונה/אייקון של השרת (לוגו השרת) - מראה אחיד ומקצועי
- יצירת ערוץ פרטי לכל טיקט, עם הרשאות רק לפותח ולצוות
- כפתור סגירה + מחיקה של הטיקט
- פקודת בדיקת "ותק" בשרת (כמה זמן חבר נמצא בשרת) - !ותק / !seniority
- פקודת בדיקת "שעות פעילות" בסיסית (זמן מאז שהצטרף) - אפשר להרחיב לשעות קוליות אם יש בוט מעקב נפרד

דרישות:
    pip install discord.py

הגדרות שצריך לשנות למטה (מסומן ב-⚠️):
    - GUILD_ID
    - STAFF_ROLE_ID
    - TICKET_CATEGORY_ID (הקטגוריה שבה ייווצרו ערוצי הטיקטים)
"""

import discord
from discord.ext import commands
from discord import app_commands
import datetime

# =============================
# ⚠️ הגדרות - יש לערוך בהתאם לשרת שלך
# =============================
GUILD_ID = 123456789012345678          # ID של השרת
STAFF_ROLE_ID = 123456789012345678     # ID של תפקיד הצוות (Staff)
TICKET_CATEGORY_ID = 123456789012345678  # ID של הקטגוריה לטיקטים
VETERAN_ROLE_ID = 123456789012345678   # ID של תפקיד "ותיק" שיינתן אוטומטית
VETERAN_MIN_DAYS = 365                 # כמות הימים הנדרשת לקבלת הרול (כרגע: שנה)

TICKET_TYPES = {
    "staff_app": {"label": "בקשת סטאף", "emoji": "📋", "desc": "הגשת מועמדות להצטרפות לצוות"},
    "xp_shop": {"label": "חנות XP", "emoji": "🛒", "desc": "בעיה ברכישה או פדיון XP"},
    "support": {"label": "תמיכה כללית", "emoji": "🎫", "desc": "כל בעיה או שאלה אחרת"},
}

# צבע אחיד לכל ה-embeds של המערכת - אפשר לשנות לצבע שמתאים ללוגו/מיתוג השרת
THEME_COLOR = discord.Color.from_str("#5865F2")  # סגול-כחול (Discord Blurple) - שנה לצבע השרת שלך

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# =============================
# תפריט נפתח (Select Menu) לבחירת סוג טיקט
# =============================
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=data["label"],
                value=key,
                description=data["desc"],
                emoji=data["emoji"],
            )
            for key, data in TICKET_TYPES.items()
        ]
        super().__init__(
            placeholder="🎫 בחר סוג טיקט לפתיחה...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select_menu",
        )

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        await create_ticket(interaction, ticket_type)


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


async def create_ticket(interaction: discord.Interaction, ticket_type: str):
    guild = interaction.guild
    member = interaction.user
    category = guild.get_channel(TICKET_CATEGORY_ID)
    staff_role = guild.get_role(STAFF_ROLE_ID)
    ticket_info = TICKET_TYPES[ticket_type]

    # בדיקה אם כבר יש לו טיקט פתוח מאותו סוג
    channel_name = f"{ticket_type}-{member.name}".lower()
    existing = discord.utils.get(guild.text_channels, name=channel_name)
    if existing:
        await interaction.response.send_message(
            f"כבר יש לך טיקט פתוח: {existing.mention}", ephemeral=True
        )
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(
            view_channel=True, send_messages=True, read_message_history=True
        )

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        overwrites=overwrites,
        topic=f"טיקט של {member} | סוג: {ticket_info['label']}",
    )

    embed = discord.Embed(
        title=f"{ticket_info['emoji']} {ticket_info['label']}",
        description=(
            f"שלום {member.mention}! תודה שפתחת טיקט.\n"
            f"צוות ה-{staff_role.mention if staff_role else 'סטאף'} יגיע בהקדם.\n\n"
            f"**תיאור:** {ticket_info['desc']}\n"
            f"**נפתח בתאריך:** {discord.utils.format_dt(datetime.datetime.now(), style='F')}"
        ),
        color=THEME_COLOR,
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)
    else:
        embed.set_footer(text=guild.name)

    await channel.send(
        content=f"{member.mention} {staff_role.mention if staff_role else ''}",
        embed=embed,
        view=CloseTicketView(),
    )
    await interaction.response.send_message(
        f"✅ נפתח לך טיקט: {channel.mention}", ephemeral=True
    )


# =============================
# View - כפתור סגירת טיקט
# =============================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="סגור טיקט", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        is_staff = staff_role in interaction.user.roles if staff_role else False

        if not (is_staff or interaction.user.guild_permissions.manage_channels):
            await interaction.response.send_message("🚫 רק צוות יכול לסגור את הטיקט.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔒 הטיקט נסגר",
            description=f"הטיקט ייסגר וימחק בעוד 5 שניות, נסגר על ידי {interaction.user.mention}.",
            color=THEME_COLOR,
        )
        await interaction.response.send_message(embed=embed)
        await interaction.channel.edit(name=f"closed-{interaction.channel.name}")
        await discord.utils.sleep_until(datetime.datetime.now() + datetime.timedelta(seconds=5))
        await interaction.channel.delete()


# =============================
# פקודה: פרסום הפאנל (רק לצוות)
# =============================
@bot.command(name="ticketpanel")
@commands.has_permissions(manage_guild=True)
async def ticket_panel(ctx: commands.Context):
    guild = ctx.guild
    lines = "\n".join(
        f"{data['emoji']} **{data['label']}** — {data['desc']}"
        for data in TICKET_TYPES.values()
    )
    embed = discord.Embed(
        title=f"🎫 מרכז הטיקטים | {guild.name}",
        description=(
            "בחר מהתפריט למטה 👇 את סוג הטיקט שברצונך לפתוח, "
            "וייווצר עבורך ערוץ פרטי מול הצוות.\n\n" + lines
        ),
        color=THEME_COLOR,
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_image(url=guild.icon.url)  # אפשר להחליף לבאנר/תמונה ייעודית של השרת
        embed.set_footer(text=f"{guild.name} • מערכת טיקטים", icon_url=guild.icon.url)
    else:
        embed.set_footer(text=f"{guild.name} • מערכת טיקטים")

    await ctx.send(embed=embed, view=TicketPanelView())


# =============================
# פקודה: בדיקת ותק בשרת (Veteran check)
# =============================
@bot.command(name="ותק", aliases=["seniority", "veteran"])
async def check_seniority(ctx: commands.Context, member: discord.Member = None):
    member = member or ctx.author
    joined = member.joined_at
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = now - joined

    days = delta.days
    years = days // 365
    months = (days % 365) // 30
    remaining_days = (days % 365) % 30

    embed = discord.Embed(
        title=f"⏳ ותק של {member.display_name}",
        color=THEME_COLOR,
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    if ctx.guild.icon:
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
    embed.add_field(name="הצטרף לשרת", value=discord.utils.format_dt(joined, style="F"), inline=False)
    embed.add_field(
        name="ותק כולל",
        value=f"{years} שנים, {months} חודשים, {remaining_days} ימים ({days} ימים סה\"כ)",
        inline=False,
    )

    # דוגמה לתגית "ותיק" אוטומטית - ניתן להתאים את הסף לפי הצורך
    if days >= 365:
        embed.add_field(name="סטטוס", value="🏆 חבר ותיק (מעל שנה)", inline=False)
    elif days >= 180:
        embed.add_field(name="סטטוס", value="⭐ חבר פעיל (מעל חצי שנה)", inline=False)
    else:
        embed.add_field(name="סטטוס", value="🆕 חבר חדש יחסית", inline=False)

    await ctx.send(embed=embed)


# =============================
# View - כפתור "קח בקשה" (Claim) לבקשת עזרה
# =============================
class HelpRequestClaimView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔧 קח בקשה", style=discord.ButtonStyle.primary, custom_id="claim_help_request")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        is_staff = staff_role in interaction.user.roles if staff_role else False

        if not (is_staff or interaction.user.guild_permissions.manage_guild):
            await interaction.response.send_message("🚫 רק צוות יכול לקחת בקשה זו.", ephemeral=True)
            return

        if button.disabled:
            await interaction.response.send_message("הבקשה כבר נלקחה.", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.add_field(name="🛠️ נלקח על ידי", value=interaction.user.mention, inline=False)

        button.label = f"✦ {interaction.user.display_name}"
        button.style = discord.ButtonStyle.secondary
        button.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


# =============================
# פקודה: !h - בקשת עזרה מהצוות
# =============================
@bot.command(name="h", aliases=["help", "עזרה"])
async def help_command(ctx: commands.Context, *, reason: str = None):
    guild = ctx.guild
    member = ctx.author
    staff_role = guild.get_role(STAFF_ROLE_ID)

    reason_text = reason if reason else "לא צוינה סיבה"
    if member.voice and member.voice.channel:
        voice_text = f"🔊 {member.voice.channel.mention}"
    else:
        voice_text = "המשתמש לא נמצא בוויס"

    embed = discord.Embed(
        title="⚠️ בקשת עזרה",
        description=f"{staff_role.mention if staff_role else '@Staff'} {member.mention}",
        color=discord.Color.orange(),
    )
    embed.add_field(name="✅ סיבה", value=reason_text, inline=False)
    embed.add_field(name="🔊 וויס", value=voice_text, inline=False)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)

    await ctx.send(embed=embed, view=HelpRequestClaimView())


# =============================
# View - כפתור "בקשת ותיק"
# =============================
class VeteranRequestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🏆 בקשת ותיק", style=discord.ButtonStyle.success, custom_id="veteran_request_button")
    async def request_veteran(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild
        veteran_role = guild.get_role(VETERAN_ROLE_ID)

        if veteran_role is None:
            await interaction.response.send_message(
                "⚠️ תפקיד הותיק לא הוגדר כראוי, יש לפנות לצוות.", ephemeral=True
            )
            return

        if veteran_role in member.roles:
            await interaction.response.send_message("כבר יש לך את דרגת הותיק! 🏆", ephemeral=True)
            return

        joined = member.joined_at
        now = datetime.datetime.now(datetime.timezone.utc)
        days = (now - joined).days

        if days >= VETERAN_MIN_DAYS:
            await member.add_roles(veteran_role, reason="בקשת ותיק אושרה אוטומטית - עמד בתנאי הוותק")
            embed = discord.Embed(
                title="🏆 מזל טוב!",
                description=f"{member.mention} עמד/ה בתנאי הוותק ({days} ימים) וקיבל/ה את דרגת {veteran_role.mention}!",
                color=discord.Color.gold(),
            )
            await interaction.response.send_message(embed=embed)
        else:
            remaining = VETERAN_MIN_DAYS - days
            await interaction.response.send_message(
                f"⏳ עדיין לא הגעת לוותק הנדרש ({VETERAN_MIN_DAYS} ימים).\n"
                f"יש לך כרגע {days} ימים - נותרו לך עוד **{remaining} ימים**.",
                ephemeral=True,
            )


# =============================
# פקודה: !vt - פרסום פאנל בקשת ותיק
# =============================
@bot.command(name="vt")
@commands.has_permissions(manage_guild=True)
async def veteran_panel(ctx: commands.Context):
    guild = ctx.guild
    embed = discord.Embed(
        title="🏆 דרגת ותיק",
        description=(
            f"לחץ על הכפתור למטה כדי לבדוק אם צברת מספיק ותק בשרת "
            f"({VETERAN_MIN_DAYS} ימים ומעלה).\n"
            f"אם עמדת בתנאי - תקבל/י את הרול **באופן אוטומטי ומיידי**! ✅"
        ),
        color=THEME_COLOR,
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)

    await ctx.send(embed=embed, view=VeteranRequestView())


# =============================
# הפעלת הבוט
# =============================
@bot.event
async def on_ready():
    # רישום ה-Views הקבועים כדי שהכפתורים ימשיכו לעבוד גם אחרי ריסטארט לבוט
    bot.add_view(TicketPanelView())
    bot.add_view(CloseTicketView())
    bot.add_view(HelpRequestClaimView())
    bot.add_view(VeteranRequestView())
    print(f"✅ הבוט מחובר בתור {bot.user} | טיקטים, בקשות עזרה, ותק וותיק פעילים")


# ⚠️ הכנס כאן את הטוקן של הבוט שלך
bot.run("TOKEN")

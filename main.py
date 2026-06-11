import discord
from discord.ext import commands
import random
import os
import asyncio

# הגדרות הרשאות ובוט
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# ---- מערכת XP ו-SHOP ----
def add_xp(user_id, amount):
    xp_data[user_id] = xp_data.get(user_id, 0) + amount

@bot.command(name="xp")
async def show_xp(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_xp = xp_data.get(member.id, 0)
    embed = discord.Embed(title="✨ פרופיל XP", description=f"למשתמש {member.mention} יש `{user_xp}` נקודות XP!", color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name="shop")
async def show_shop(ctx):
    embed = discord.Embed(title="🛒 חנות ה-XP הגדולה", description="קנה רולים ועיצובים באמצעות ה-XP שלך!\nשימוש: `!buy [שם הפריט]`", color=discord.Color.purple())
    for item, price in SHOP_ITEMS.items():
        embed.add_field(name=item, value=f"💰 מחיר: `{price}` XP", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="buy")
async def buy_item(ctx, *, item_name: str):
    user_xp = xp_data.get(ctx.author.id, 0)
    if item_name not in SHOP_ITEMS:
        return await ctx.send("❌ הפריט לא קיים בחנות. בדוק שרשמת נכון!")
    
    price = SHOP_ITEMS[item_name]
    if user_xp < price:
        return await ctx.send(f"❌ אין לך מספיק XP! חסר לך `{price - user_xp}` XP.")
    
    xp_data[ctx.author.id] -= price
    inventory.setdefault(ctx.author.id, []).append(item_name)
    await ctx.send(f"🎉 תתחדש! קנית את **{item_name}** בהצלחה ומנוכו ממך `{price}` XP.")

# ---- פקודת עזרה מעוצבת ----
@bot.command(name="h")
async def help_command(ctx):
    embed = discord.Embed(title="❓ תפריט עזרה ופקודות", description="הנה כל הפקודות הזמינות בבוט:", color=discord.Color.gold())
    embed.add_field(name="💰 מערכת XP", value="`!xp` - בדיקת ה-XP שלך\n`!shop` - חנות ה-XP\n`!buy [פריט]` - קנייה מהחנות", inline=False)
    embed.add_field(name="🎮 משחקים (מעל 4 משחקים!)", value="`!dice` - קוביות\n`!coin` - מטבע\n`!slots` - מכונת מזל\n`!gamma` - משחק הגמא הסודי", inline=False)
    embed.add_field(name="🎫 תמיכה וצוות", value="`!ticket` - פתיחת קריאת שירות מעוצבת\n`!staff_req` - שליחת בקשת הצטרפות לצוות", inline=False)
    await ctx.send(embed=embed)

# ---- 4 משחקים מובנים ----
@bot.command(name="dice")
async def game_dice(ctx):
    user = random.randint(1, 6)
    bot_num = random.randint(1, 6)
    win = user > bot_num
    if win: add_xp(ctx.author.id, 50)
    msg = f"🎲 קובייה שלך: `{user}` | קובייה שלי: `{bot_num}`\n" + ("🏆 ניצחת וקיבלת 50 XP!" if win else "💥 הפסדת!")
    await ctx.send(msg)

@bot.command(name="coin")
async def game_coin(ctx, choice: str):
    if choice not in ["עץ", "פלי"]: return await ctx.send("יש לבחור `!coin עץ` או `!coin פלי`")
    result = random.choice(["עץ", "פלי"])
    win = choice == result
    if win: add_xp(ctx.author.id, 30)
    msg = f"🪙 יצא: `{result}`! " + ("🏆 צדקת! קיבלת 30 XP!" if win else "💥 טעית!")
    await ctx.send(msg)

@bot.command(name="slots")
async def game_slots(ctx):
    emojis = ["🍒", "🍇", "🍊", "💎"]
    r1, r2, r3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
    win = r1 == r2 == r3
    if win: add_xp(ctx.author.id, 500)
    msg = f"🎰 [ {r1} | {r2} | {r3} ]\n" + ("💎 ג'קפוט מטורף! זכית ב-500 XP!" if win else "ניסיון יפה, נסה שוב!")
    await ctx.send(msg)

@bot.command(name="gamma")
async def game_gamma(ctx):
    secret = random.randint(1, 10)
    await ctx.send("🔮 ברוך הבא ל-XP Gamma! ניחשתי מספר בין 1 ל-10. יש לך 15 שניות לרשום מספר בצ'אט!")
    try:
        guess = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.isdigit(), timeout=15.0)
        if int(guess.content) == secret:
            add_xp(ctx.author.id, 200)
            await ctx.send(f"🎯 מדהים! המספר היה `{secret}`. זכית ב-200 XP גמא!")
        else:
            await ctx.send(f"💥 לא נכון! המספר היה `{secret}`.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ נגמר הזמן! המספר היה `{secret}`.")

# ---- מערכת טיקטים מעוצבת ----
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 פתח טיקט תמיכה", style=discord.ButtonStyle.danger, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        staff_role_id = int(os.environ.get("STAFF_ROLE_ID", 0))
        staff_role = guild.get_role(staff_role_id)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"✅ הטיקט שלך נפתח בחדר: {ticket_channel.mention}", ephemeral=True)

        staff_mention = staff_role.mention if staff_role else "@STAFF"
        embed_welcome = discord.Embed(title="🎫 אימות ופתיחת טיקט שירות", description=f"ברוך הבא {interaction.user.mention}.\nנא לענות על השאלות הבאות כדי שהצוות יוכל לעזור לך.", color=discord.Color.red())
        await ticket_channel.send(content=staff_mention, embed=embed_welcome)

        await ticket_channel.send("❓ **שאלה 1:** מהי סיבת פתיחת הטיקט?")
        reason = await bot.wait_for("message", check=lambda m: m.author == interaction.user and m.channel == ticket_channel)

        await ticket_channel.send("❓ **שאלה 2:** האם תרצה שנציג ייכנס איתך לחדר וויס (Voice)? (כן/לא)")
        voice_req = await bot.wait_for("message", check=lambda m: m.author == interaction.user and m.channel == ticket_channel)

        embed_summary = discord.Embed(title="📝 פרטי קריאת השירות", color=discord.Color.orange())
        embed_summary.add_field(name="👤 פותח הטיקט", value=interaction.user.mention, inline=True)
        embed_summary.add_field(name="📌 סיבה", value=reason.content, inline=False)
        embed_summary.add_field(name="🔊 דרישת וויס", value=voice_req.content, inline=True)
        await ticket_channel.send(embed=embed_summary)

@bot.command(name="ticket")
@commands.has_permissions(administrator=True)
async def send_ticket_launcher(ctx):
    view = TicketView()
    embed = discord.Embed(title="🎫 מרכז התמיכה והאימות", description="זקוק לעזרה מהצוות או לאימות מהיר?\nלחץ על הכפתור למטה כדי לפתוח פנייה פרטית.", color=discord.Color.red())
    await ctx.send(embed=embed, view=view)

# ---- בקשת סטאף ----
class StaffActionView(discord.ui.View):
    def __init__(self, applicant):
        super().__init__(timeout=None)
        self.applicant = applicant

    @discord.ui.button(label="✅ אשר סטאף", style=discord.ButtonStyle.green, custom_id="approve_staff")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name != "helena" and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק הלנה יכולה לאשר בקשות בחדר זה!", ephemeral=True)
        
        await interaction.response.send_message(f"🎉 הבקשה אושרה! {self.applicant.mention} התקבל לצוות!")
        self.stop()

@bot.command(name="staff_req")
async def staff_request(ctx):
    target_channel_id = 1492894356091179008
    channel = bot.get_channel(target_channel_id)
    if not channel:
        return await ctx.send("❌ חדר בקשות הצוות לא נמצא!")

    embed = discord.Embed(title="📩 בקשת סטאף פרנד חדשה", description=f"חבר הצוות {ctx.author.mention} שלח בקשת קידום.\nממתין לאישור של הלנה.", color=discord.Color.blue())
    view = StaffActionView(ctx.author)
    await channel.send(embed=embed, view=view)
    await ctx.send("✅ בקשת הסטאף שלך נשלחה בהצלחה לחדר האישורים של הלנה!")

# שימוש במשתנה המאובטח מה-Variables
import os
bot.run(os.environ.get("MTQ4MDMzMjIxMTQyODUyODI0OA.GS1nCR.6TvF-I5209vJ4XzZtMTAf7H2_y9ikdvp9N3b78"))








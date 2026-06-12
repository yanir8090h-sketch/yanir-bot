import discord
from discord.ext import commands
import random
import os
import asyncio
from flask import Flask
import threading

app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

# הגדרות הרשאות ובוט
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# מאגרי נתונים זמניים בזיכרון (מתאפס בריסטארט)
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
    print(f"🤖 הבוט {bot.user.name} עלה לאוויר בהצלחה ב-Railway!")

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

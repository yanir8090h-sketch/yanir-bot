import os
import discord
from discord.ext import commands
import random

# הגדרת הבוט והרשאות
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# משחק 3: רולטת קוביות בכפתור
class DiceView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=60.0)
        self.author = author

    @discord.ui.button(label="גלגל קובייה!", style=discord.ButtonStyle.primary)
    async def roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("❌ אין לך מספיק אלפים כדי לשחק!", ephemeral=True)

        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        # תיקון שורה 107 - בחירת הבוט מוצגת בצורה תקינה עם גרשיים מסודרים
        bot_choice = random.choice(["אבן", "נייר", "מספריים"])
        print(f"הבוט בחר {bot_choice}.") 

        if user_roll > bot_roll:
            color = discord.Color.green()
            msg = f"🏆 **ניצחת את הבוט!**\n\nהקובייה שלך: `{user_roll}`\nהקובייה של הבוט: `{bot_roll}`\n\n**הרווחת 50 אלפים!**"
        elif bot_roll > user_roll:
            color = discord.Color.red()
            msg = f"💥 **הפסדת לבוט...**\n\nהקובייה שלך: `{user_roll}`\nהקובייה של הבוט: `{bot_roll}`\n\n**איבדת 50 אלפים.**"
        else:
            color = discord.Color.red()
            # תיקון שורה 187 - גרשיים סוגרים בצורה מושלמת בסוף ה-f-string
            msg = f"💛 **תיקו! וקית**\n\nשניכם קיבלתם `{user_roll}`"

        embed = discord.Embed(title="🎲 תוצאת הטלת המטבע!", description=msg, color=color)
        await interaction.response.edit_message(embed=embed, view=self)

@bot.command(name="dice")
async def dice(ctx):
    view = DiceView(ctx.author)
    await ctx.send("לחץ על הכפתור כדי לגלגל קובייה!", view=view)
bot.run("MTQ4MDMzMjIxMTQyODUyODI0OA.G1qeDN.92WecniqxDPSviKmmyrfDyqm7Cr5ZsFFXVY55E")



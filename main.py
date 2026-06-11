import discord
from discord.ext import commands
import json
import os
from datetime import datetime

# --- הגדרות קבועות (תחליף ל-ID האמיתיים של השרת שלך) ---
STAFF_ROLE_ID = 1493335218004820180  # ID של רול הסטאף המבקש / הרול שמוענק בסטאף פרנד
ADMIN_ROLE_ID = 1111111111111111111  # תחליף ל-ID של רול ההנהלה הגבוהה שיכולה לאשר

# --- הגדרות ה-ID והמחירים המדויקים של הרולים לחנות לפי מה ששלחת ---
ROLE_LEVEL_1_ID = 1484226514051665930  # מחיר: 10,000 XP
ROLE_LEVEL_2_ID = 1491063689502003360  # מחיר: 12,000 XP
ROLE_LEVEL_3_ID = 1490894966262726687  # מחיר: 15,000 XP
ROLE_LEVEL_4_ID = 1490894817373196388  # מחיר: 20,000 XP

# --- מערכת שמירת ה-XP בקובץ מקומי ---
XP_FILE = "xp_data.json"

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_xp(user_id, amount):
    data = load_xp()
    user_key = str(user_id)
    if user_key not in data:
        data[user_key] = {"xp": 0, "level": 1}
    data[user_key]["xp"] += amount
    
    expected_level = (data[user_key]["xp"] // 150) + 1  # עליית רמה כל 150 XP
    if expected_level > data[user_key]["level"]:
        data[user_key]["level"] = expected_level
        save_xp(data)
        return True, expected_level
    save_xp(data)
    return False, data[user_key]["level"]

# הגדרת הבוט
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 הבוט {bot.user.name} עלה לאוויר בהצלחה ב-Railway!")

# ==========================================
# 1. פקודות מערכת ה-XP והחנות (מעודכן ל-4 רולים שלך)
# ==========================================

@bot.command(name="xp")
async def check_xp(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_xp()
    user_key = str(member.id)
    
    user_xp = data.get(user_key, {}).get("xp", 0)
    user_level = data.get(user_key, {}).get("level", 1)
    
    embed = discord.Embed(title=f"📊 סטטיסטיקות ה-XP של {member.display_name}", color=discord.Color.blue())
    embed.add_field(name="✨ סך הכל XP", value=f"`{user_xp:,}` XP", inline=True)
    embed.add_field(name="⭐ רמה נוכחית", value=f"רמה `{user_level}`", inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="give_xp")
@commands.has_permissions(administrator=True)
async def give_xp(ctx, member: discord.Member, amount: int):
    leveled_up, level = add_xp(member.id, amount)
    await ctx.send(f"✅ הוענקו `{amount:,}` XP למשתמש {member.mention}!")
    if leveled_up:
        await ctx.send(f"🎉 מזל טוב {member.mention}! עלית לרמה **{level}**!")

        # תצוגת הכפתור שישלח את החנות לפרטי
# חלון קופץ (Modal) שנפתח בלחיצה על כפתור הקנייה
class BuyRoleModal(discord.ui.Modal, title="🛒 רכישת רול מחנות ה-XP"):
    role_num = discord.ui.TextInput(
        label="הכנס את מספר הרול שברצונך לקנות (1-4)", 
        placeholder="לדוגמה: 1", 
        max_length=1, 
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        data = load_xp()
        user_key = str(interaction.user.id)
        user_xp = data.get(user_key, {}).get("xp", 0)
        
        # מילון הרולים והמחירים המדויקים שלך
        shop_items = {
            "1": {"cost": 10000, "role_id": ROLE_LEVEL_1_ID, "name": "רול ראשון"},
            "2": {"cost": 12000, "role_id": ROLE_LEVEL_2_ID, "name": "רול שני"},
            "3": {"cost": 15000, "role_id": ROLE_LEVEL_3_ID, "name": "רול שלישי"},
            "4": {"cost": 20000, "role_id": ROLE_LEVEL_4_ID, "name": "רול רביעי"}
        }
        
        choice = self.role_num.value.strip()
        if choice not in shop_items:
            return await interaction.followup.send("❌ מספר לא תקין! נא לבחור מספר בין 1 ל-4 לפי הרשימה בחנות.", ephemeral=True)
            
        selected = shop_items[choice]
        cost = selected["cost"]
        role_id = selected["role_id"]
        role_name = selected["name"]
        
        if user_xp < cost:
            return await interaction.followup.send(f"❌ אין לך מספיק XP! הרול עולה `{cost:,} XP` וכרגע יש לך רק `{user_xp:,} XP`.", ephemeral=True)
            
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.followup.send("❌ שגיאה: הרול המבוקש לא הוגדר בצורה תקינה בקוד הבוט.", ephemeral=True)
            
        if role in interaction.user.roles:
            return await interaction.followup.send(f"❌ כבר יש לך את הרול `{role.name}`!", ephemeral=True)
            
        data[user_key]["xp"] -= cost
        save_xp(data)
        
        try:
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"🎉 ברכות! רכשת בהצלחה את הרול **{role.name}** עבור `{cost:,} XP`!", ephemeral=True)
            
            channel = interaction.channel
            await channel.send(f"👑 כל הכבוד ל-{interaction.user.mention} שרכש את הרול **{role.name}** מהחנות עבור `{cost:,} XP`!")
        except discord.Forbidden:
            await interaction.followup.send(f"⚠️ ה-XP ירד, אך לבוט אין מספיק הרשאות כדי לתת לך את הרול פיזית בשרת.", ephemeral=True)

# תצוגת הכפתור הכחול "Buy Role"
class XpShopNewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy Role", style=discord.ButtonStyle.blurple, custom_id="buy_role_main_button")
    async def buy_button(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BuyRoleModal())

# הפקודה המרכזית שמייצרת את החנות בדיוק כמו בתמונה
@bot.command(name="xp_shop")
async def xp_shop(ctx):
    embed = discord.Embed(
        title="🛒 חנות הרולים של השרת", 
        description="To buy a role click on the buttons!", 
        color=discord.Color.from_rgb(47, 49, 54)
    )
    
    embed.add_field(name="(1)", value=f"<@&{ROLE_LEVEL_1_ID}> - **10,000 XP**", inline=False)
    embed.add_field(name="(2)", value=f"<@&{ROLE_LEVEL_2_ID}> - **12,000 XP**", inline=False)
    embed.add_field(name="(3)", value=f"<@&{ROLE_LEVEL_3_ID}> - **15,000 XP**", inline=False)
    embed.add_field(name="(4)", value=f"<@&{ROLE_LEVEL_4_ID}> - **20,000 XP**", inline=False)
    
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
        
    view = XpShopNewView()
    await ctx.send(embed=embed, view=view)


# ==========================================
# 2. מערכת בקשת סטאף פרנד (Staff Friend)
# ==========================================

class ClaimReasonModal(discord.ui.Modal, title="טיפול בבקשת סטאף פרנד"):
    reason = discord.ui.TextInput(label="סיבה / הערות לטיפול (וויס/בדיקה)", style=discord.TextStyle.paragraph, placeholder="רשום כאן פרטים על הטיפול או סיבת הבדיקה בוויס...", required=True)
    
    def __init__(self, staff_member, target_member, embed_msg):
        super().__init__()
        self.staff_member = staff_member
        self.target_member = target_member
        self.embed_msg = embed_msg

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = self.embed_msg.embeds[0]
        embed.color = discord.Color.orange()
        embed.set_field_at(3, name="สถานะ (מצב בקשה)", value=f"🔶 בטיפול בוויס על ידי: {interaction.user.mention}\n📝 הערה: {self.reason.value}", inline=False)
        
        await self.embed_msg.edit(embed=embed)
        await interaction.followup.send(f"📢 הבקשה נלקחה לטיפול ובדיקת וויס על ידי {interaction.user.mention}.", ephemeral=False)

class StaffFriendView(discord.ui.View):
    def __init__(self, staff_member, target_member):
        super().__init__(timeout=None)
        self.staff_member = staff_member
        self.target_member = target_member

    @discord.ui.button(label="✅ אשר בקשה", style=discord.ButtonStyle.green, custom_id="approve_friend")
    async def approve(self, interaction: discord.Interaction):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק הנהלת השרת הגבוהה מוסמכת לאשר בקשה זו!", ephemeral=True)
        
        await interaction.response.defer()
        
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        role_status = "אך חסרה לבוט הרשאה להעניק את הרול פיזית."
        if staff_role:
            try:
                await self.target_member.add_roles(staff_role)
                role_status = "והרול הוענק לו בהצלחה!"
            except:
                pass
        
        embed = interaction.message.embeds
        embed.color = discord.Color.green()
        embed.title = "✅ בקשת סטאף פרנד - אושרה סופית!"
        embed.set_field_at(3, name="สถานะ (מצב בקשה)", value=f"💚 הבקשה אושרה על ידי ההנהלה הגבוהה ({interaction.user.mention})!", inline=False)
        embed.set_footer(text=f"אושר על ידי: {interaction.user.display_name} בשעה {datetime.now().strftime('%H:%M')}")
        
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        await interaction.followup.send(f"🎉 הבקשה אושרה! {self.target_member.mention} קיבל את הרול {role_status}\nחבר הצוות הממליץ: {self.staff_member.mention}")

    @discord.ui.button(label="❌ דחה בקשה", style=discord.ButtonStyle.red, custom_id="deny_friend")
    async def deny(self, interaction: discord.Interaction):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק הנהלת השרת הגבוהה מוסמכת לדחות בקשה זו!", ephemeral=True)
        
        await interaction.response.defer()
        
        embed = interaction.message.embeds
        embed.color = discord.Color.red()
        embed.title = "❌ בקשת סטאף פרנד - נדחתה"
        embed.set_field_at(3, name="สถานะ (מצב בקשה)", value=f"❤️ הבקשה נדחתה על ידי ההנהלה ({interaction.user.mention}).", inline=False)
        embed.set_footer(text=f"נדחה על ידי: {interaction.user.display_name}")
        
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        await interaction.followup.send(f"📢 בקשתו של {self.staff_member.mention} להעניק סטאף פרנד ל-{self.target_member.mention} **נדחתה**.")

    @discord.ui.button(label="🛠️ טפל כאן (סיבה/וויס)", style=discord.ButtonStyle.blurple, custom_id="claim_friend")
    async def claim(self, interaction: discord.Interaction):
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק חברי צוות בעלי רול @STAFF יכולים לקחת את הבקשה לטיפול!", ephemeral=True)
            
        modal = ClaimReasonModal(self.staff_member, self.target_member, interaction.message)
        import random

# ==========================================
# 4. מערכת משחקי אקפי (XP Games)
# ==========================================

# משחק 1: הימורי אקפי (רולטה / קוביות)
@bot.command(name="gamble")
async def gamble_xp(ctx, amount: int):
    if amount <= 0:
        return await ctx.send("❌ נא להזין כמות אקפי חוקית והגדולה מ-0!")
        
    data = load_xp()
    user_key = str(ctx.author.id)
    user_xp = data.get(user_key, {}).get("xp", 0)
    
    # בדיקה שיש לו מספיק אקפי להמר
    if user_xp < amount:
        return await ctx.send(f"❌ אין לך מספיק XP בשביל להמר על כמות זו! (יש לך כרגע `{user_xp:,}` XP).")
        
    # סיכוי של 50% לנצח
    if random.choice([True, False]):
        data[user_key]["xp"] += amount
        save_xp(data)
        await ctx.send(f"🎉 **ניצחת בהימור!** {ctx.author.mention} הגרלת קוביות מוצלחת והרווחת `{amount:,}` XP!")
    else:
        data[user_key]["xp"] -= amount
        save_xp(data)
        await ctx.send(f"📉 **הפסדת בהימור!** {ctx.author.mention} המזל לא היה איתך והפסדת `{amount:,}` XP.")

# משחק 2: הטלת מטבע (עץ או פלי)
@bot.command(name="coinflip")
async def coin_flip(ctx, choice: str, amount: int):
    choice = choice.strip()
    if choice not in ["עץ", "פלי"]:
        return await ctx.send("❌ נא לבצע בחירה תקינה! רשום `!coinflip עץ <כמות>` או `!coinflip פלי <כמות>`.")
        
    if amount <= 0:
        return await ctx.send("❌ נא להזין כמות אקפי חוקית הגדולה מ-0!")
        
    data = load_xp()
    user_key = str(ctx.author.id)
    user_xp = data.get(user_key, {}).get("xp", 0)
    
    if user_xp < amount:
        return await ctx.send(f"❌ אין לך מספיק XP בשביל להמר! (יש לך כרגע `{user_xp:,}` XP).")
        
    result = random.choice(["עץ", "פלי"])
    
    if choice == result:
        data[user_key]["xp"] += amount
        save_xp(data)
        await ctx.send(f"🪙 המטבע נחת על **{result}**! {ctx.author.mention} צדקת וזכית ב-`{amount:,}` XP!")
    else:
        data[user_key]["xp"] -= amount
        save_xp(data)
        await ctx.send(f"🪙 המטבע נחת על **{result}**! {ctx.author.mention} טעית והפסדת `{amount:,}` XP.")

# משחק 3: גלגל המזל יומי (פעם ביום / בדיקה חופשית ללא סיכון)
@bot.command(name="wheel")
@commands.cooldown(1, 3600, commands.BucketType.user) # הגבלת שימוש: פעם בשעה
async def slots_wheel(ctx):
    # רשימת פרסים או קנסות אפשריים בגלגל
    outcomes = [
        {"msg": "🎰 מטורף! הגלגל נעצר על הבונוס הגדול! זכית ב-`500` XP!", "xp": 500},
        {"msg": "✨ נחמד מאד! הגלגל העניק לך `150` XP!", "xp": 150},
        {"msg": "👍 זכית בפרס קטן של `50` XP.", "xp": 50},
        {"msg": "💨 הגלגל נעצר על ריק... לא זכית בכלום הפעם.", "xp": 0},
        {"msg": "💥 אאוץ'! הגלגל נעצר על פצצה והפסדת `100` XP!", "xp": -100}
    ]
    
    selected = random.choice(outcomes)
    reward = selected["xp"]
    
    data = load_xp()
    user_key = str(ctx.author.id)
    if user_key not in data:
        data[user_key] = {"xp": 0, "level": 1}
        
    data[user_key]["xp"] += reward
    # מניעת מצב שה-XP יורד מתחת ל-0
    if data[user_key]["xp"] < 0:
        data[user_key]["xp"] = 0
        
    save_xp(data)
    await ctx.send(f"{ctx.author.mention} סובב את גלגל המזל... \n{selected['msg']}")

# טיפול בשגיאת ה-Cooldown של גלגל המזל
@slots_wheel.error
async def wheel_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        minutes = int(error.retry_after // 60)
        seconds = int(error.retry_after % 60)
        await ctx.send(f"⏳ {ctx.author.mention}, הגלגל עדיין חם! תוכל לסובב אותו שוב בעוד `{minutes}` דקות ו-`{seconds}` שניות.")

bot.run(os.environ.get("DISCORD_TOKEN"))

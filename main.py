import discord
from discord.ext import commands
import json
import os
from datetime import datetime

# --- הגדרות קבועות (תחליף ל-ID האמיתיים של השרת שלך) ---
STAFF_ROLE_ID = 1493335218004820180  # ID של רול הסטאף המבקש / הרול שמוענק בסטאף פרנד
ADMIN_ROLE_ID = 1111111111111111111  # תחליף ל-ID של רול ההנהלה הגבוהה שיכולה לאשר

# --- הגדרות ה-ID של 5 הרולים לחנות (תחליף את ה-1111... ב-ID האמיתיים של הרולים בשרת שלך) ---
ROLE_LEVEL_1_ID = 1111111111111111111  # ID לרול ארנב אקפי
ROLE_LEVEL_2_ID = 2222222222222222222  # ID לרול חייל אקפי
ROLE_LEVEL_3_ID = 3333333333333333333  # ID לרול לוחם אקפי
ROLE_LEVEL_4_ID = 4444444444444444444  # ID לרול מאסטר אקפי
ROLE_LEVEL_5_ID = 5555555555555555555  # ID לרול אלוהי אקפי

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
    
    expected_level = (data[user_key]["xp"] // 150) + 1  # עריכה: עליית רמה כל 150 XP
    if expected_level > data[user_key]["level"]:
        data[user_key]["level"] = expected_level
        save_xp(data)
        return True, expected_level
    save_xp(data)
    return False, data[user_key]["level"]

# ==========================================
# 1. פקודות מערכת ה-XP והחנות המעודכנת
# ==========================================

# פקודה לבדיקת ה-XP שלך או של חבר
@bot.command(name="xp")
async def check_xp(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_xp()
    user_key = str(member.id)
    
    user_xp = data.get(user_key, {}).get("xp", 0)
    user_level = data.get(user_key, {}).get("level", 1)
    
    embed = discord.Embed(title=f"📊 סטטיסטיקות ה-XP של {member.display_name}", color=discord.Color.blue())
    embed.add_field(name="✨ סך הכל XP", value=f"`{user_xp}` XP", inline=True)
    embed.add_field(name="⭐ רמה נוכחית", value=f"רמה `{user_level}`", inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# פקודה למנהלים להעניק XP
@bot.command(name="give_xp")
@commands.has_permissions(administrator=True)
async def give_xp(ctx, member: discord.Member, amount: int):
    leveled_up, level = add_xp(member.id, amount)
    await ctx.send(f"✅ הוענקו `{amount}` XP למשתמש {member.mention}!")
    if leveled_up:
        await ctx.send(f"🎉 מזל טוב {member.mention}! עלית לרמה **{level}**!")

# חנות ה-XP עם המחירים המועלים
@bot.command(name="xp_shop")
async def xp_shop(ctx):
    embed = discord.Embed(
        title="🛒 חנות הרולים הרשמית של השרת", 
        description="רכוש רולים יוקרתיים באמצעות נקודות ה-XP שצברת בצ'אט!\nלקנייה רשום: `!buy <שם הרול>`", 
        color=discord.Color.purple()
    )
    embed.add_field(name="🐰 1. רול: ארנב אקפי (XPRabbit)", value="מחיר: `500 XP`\nפקודה: `!buy rabbit`", inline=False)
    embed.add_field(name="🎖️ 2. רול: חייל אקפי (XPSoldier)", value="מחיר: `1,500 XP`\nפקודה: `!buy soldier`", inline=False)
    embed.add_field(name="⚔️ 3. רול: לוחם אקפי (XPFighter)", value="מחיר: `3,500 XP`\nפקודה: `!buy fighter`", inline=False)
    embed.add_field(name="🔮 4. רול: מאסטר אקפי (XPMaster)", value="מחיר: `6,000 XP`\nפקודה: `!buy master`", inline=False)
    embed.add_field(name="👑 5. רול: אלוהי אקפי (XPGod)", value="מחיר: `10,000 XP`\nפקודה: `!buy god`", inline=False)
    
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)

# פקודת הקנייה שמורידה XP ומעניקה את הרול בדיסקורד
@bot.command(name="buy")
async def buy_item(ctx, item: str):
    data = load_xp()
    user_key = str(ctx.author.id)
    user_xp = data.get(user_key, {}).get("xp", 0)
    
    shop_items = {
        "rabbit": {"cost": 500, "role_id": ROLE_LEVEL_1_ID, "name": "ארנב אקפי"},
        "soldier": {"cost": 1500, "role_id": ROLE_LEVEL_2_ID, "name": "חייל אקפי"},
        "fighter": {"cost": 3500, "role_id": ROLE_LEVEL_3_ID, "name": "לוחם אקפי"},
        "master": {"cost": 6000, "role_id": ROLE_LEVEL_4_ID, "name": "מאסטר אקפי"},
        "god": {"cost": 10000, "role_id": ROLE_LEVEL_5_ID, "name": "אלוהי אקפי"}
    }
    
    item = item.lower()
    if item not in shop_items:
        return await ctx.send("❌ פריט זה לא קיים בחנות! רשום `!xp_shop` כדי לראות את הרשימה.")
        
    selected = shop_items[item]
    cost = selected["cost"]
    role_id = selected["role_id"]
    role_name = selected["name"]
    
    if user_xp < cost:
        return await ctx.send(f"❌ אין לך מספיק XP! הרול `{role_name}` עולה `{cost:,} XP` וכרגע יש לך רק `{user_xp:,} XP`.")
        
    role = ctx.guild.get_role(role_id)
    if not role:
        return await ctx.send("❌ שגיאה: הרול המבוקש לא הוגדר בצורה תקינה בקוד על ידי המנהל.")
        
    if role in ctx.author.roles:
        return await ctx.send(f"❌ כבר יש לך את הרול `{role_name}`!")
        
    data[user_key]["xp"] -= cost
    save_xp(data)
    
    try:
        await ctx.author.add_roles(role)
        await ctx.send(f"🎉 ברכות {ctx.author.mention}! רכשת בהצלחה את הרול **{role.name}** עבור `{cost:,} XP`!")
    except discord.Forbidden:
        await ctx.send(f"⚠️ ה-XP ירד, אך לבוט אין מספיק הרשאות כדי לתת לך את הרול (ודא שרול הבוט נמצא מעל הרול הנקנה בהגדרות השרת).")


# ==========================================
# 2. מערכת בקשת סטאף פרנד (Staff Friend)
# ==========================================

# חלון קופץ להזנת סיבה לכפתור ה"טפל כאן"
class ClaimReasonModal(discord.ui.Modal, title="טיפול בבקשת סטאף פרנד"):
    reason = discord.ui.TextInput(label="סיבה / הערות לטיפול (וויס/בדיקה)", style=discord.ui.TextStyle.paragraph, placeholder="רשום כאן פרטים על הטיפול או סיבת הבדיקה בוויס...", required=True)
    
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

# תצוגת הכפתורים שמתחת לבקשה
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
        
        embed = interaction.message.embeds[0]
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
        
        embed = interaction.message.embeds[0]
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

bot.run(os.environ.get("DISCORD_TOKEN"))

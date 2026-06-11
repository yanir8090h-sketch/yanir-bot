import discord
from discord.ext import commands
import json
import os
from datetime import datetime

# --- הגדרות קבועות (תחליף ל-ID האמיתיים של השרת שלך במידת הצורך) ---
STAFF_ROLE_ID = 1493335218004820180  # ה-ID של הרול שיש להעניק / רול סטאף המבקש
ADMIN_ROLE_ID = 1111111111111111111  # תחליף ל-ID של רול ההנהלה הגבוהה שיכולה לאשר

# --- סימולציית מסד נתונים ל-XP (שומר בקובץ מקומי בשרת) ---
XP_FILE = "xp_data.json"

def load_xp():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {}

def save_xp(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=4)

# פונקציית עזר להוספת XP (תוכל לקרוא לה בתוך אירוע on_message אם תרצה)
def add_xp(user_id, amount):
    data = load_xp()
    user_key = str(user_id)
    if user_key not in data:
        data[user_key] = {"xp": 0, "level": 1}
    data[user_key]["xp"] += amount
    
    # חישוב עליית רמות פשוט (כל 100 XP עולים רמה)
    expected_level = (data[user_key]["xp"] // 100) + 1
    if expected_level > data[user_key]["level"]:
        data[user_key]["level"] = expected_level
        save_xp(data)
        return True, expected_level
    save_xp(data)
    return False, data[user_key]["level"]

# ==========================================
# 1. מערכת XP, חנות ובדיקת אקספי
# ==========================================

# פקודה לבדיקת ה-XP והרמה שלך או של חבר
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

# פקודה למנהלים להעניק XP למישהו (לצורך בדיקות ומבצעים)
@bot.command(name="give_xp")
@commands.has_permissions(administrator=True)
async def give_xp(ctx, member: discord.Member, amount: int):
    leveled_up, level = add_xp(member.id, amount)
    await ctx.send(f"✅ הוענקו `{amount}` XP למשתמש {member.mention}!")
    if leveled_up:
        await ctx.send(f"🎉 מזל טוב {member.mention}! עלית לרמה **{level}**!")

# חנות ה-XP (דוגמה בסיסית - ניתן להרחיב)
@bot.command(name="xp_shop")
async def xp_shop(ctx):
    embed = discord.Embed(title="🛒 חנות ה-XP של השרת", description="רכוש פריטים ורולים באמצעות נקודות ה-XP שלך!", color=discord.Color.purple())
    embed.add_field(name="👑 רול VIP", value="מחיר: `500 XP`\nלרכישה רשום: `!buy vip`", inline=False)
    embed.add_field(name="🎨 שינוי צבע ניקודם", value="מחיר: `200 XP`\nלרכישה רשום: `!buy color`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="buy")
async def buy_item(ctx, item: str):
    data = load_xp()
    user_key = str(ctx.author.id)
    user_xp = data.get(user_key, {}).get("xp", 0)
    
    item = item.lower()
    if item == "vip":
        cost = 500
        if user_xp < cost:
            return await ctx.send("❌ אין לך מספיק XP בשביל לקנות את רול ה-VIP!")
        
        data[user_key]["xp"] -= cost
        save_xp(data)
        # כאן תוכל להוסיף קוד שנותן את הרול פיזית למשתמש בשרת
        await ctx.send(f"🎉 {ctx.author.mention} רכשת בהצלחה את רול ה-VIP עבור 500 XP!")
        
    elif item == "color":
        cost = 200
        if user_xp < cost:
            return await ctx.send("❌ אין לך מספיק XP בשביל שינוי צבע!")
            
        data[user_key]["xp"] -= cost
        save_xp(data)
        await ctx.send(f"🎨 {ctx.author.mention} רכשת בהצלחה שינוי צבע עבור 200 XP!")
    else:
        await ctx.send("❌ פריט זה לא קיים בחנות. רשום `!xp_shop` לצפייה בפריטים.")


# ==========================================
# 2. מערכת בקשת סטאף פרנד (Staff Friend)
# ==========================================

# חלון קופץ להזנת סיבה לכפתור ה"טפל כאן"
class ClaimReasonModal(discord.ui.Modal, title="טיפול בבקשת סטאף פרנד"):
    reason = discord.ui.TextInput(label="סיבה / הערות לטיפול בבקשה", style=discord.ui.TextStyle.paragraph, placeholder="רשום כאן את הסיבה או הערות לחבר הצוות...", required=True)
    
    def __init__(self, staff_member, target_member, embed_msg):
        super().__init__()
        self.staff_member = staff_member
        self.target_member = target_member
        self.embed_msg = embed_msg

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # עדכון ההודעה המקורית שהיא בטיפול
        embed = self.embed_msg.embeds[0]
        embed.color = discord.Color.orange()
        embed.set_footer(text=f"📜 בטיפול על ידי: {interaction.user.display_name} | סיבה: {self.reason.value}")
        
        # עדכון הכפתורים (משאיר את כפתורי האישור והדחייה רק להנהלה הגבוהה)
        await self.embed_msg.edit(embed=embed)
        await interaction.followup.send(f"📢 הבקשה נלקחה לטיפול על ידי {interaction.user.mention}.", ephemeral=False)

# תצוגת הכפתורים שתופיע מתחת לבקשה
class StaffFriendView(discord.ui.View):
    def __init__(self, staff_member, target_member):
        super().__init__(timeout=None) # הופך את הכפתורים לקבועים (לא יפוג תוקפם)
        self.staff_member = staff_member
        self.target_member = target_member

    @discord.ui.button(label="✅ אשר בקשה", style=discord.ButtonStyle.green, custom_id="approve_friend")
    async def approve(self, interaction: discord.Interaction):
        # בדיקה האם ללוחץ יש את רול ההנהלה הגבוהה
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק הנהלת השרת הגבוהה מוסמכת לאשר בקשה זו!", ephemeral=True)
        
        await interaction.response.defer()
        
        # הענקת הרול למשתמש שקיבל את ההמלצה
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role:
            try:
                await self.target_member.add_roles(staff_role)
                role_status = "והקוד העניק לו את הרול בהצלחה!"
            except:
                role_status = "אך חסרה לבוט הרשאה להעניק את הרול פיזית."
        
        # עדכון ה-Embed שהבקשה אושרה
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ בקשת סטאף פרנד - אושרה!"
        embed.set_footer(text=f"אושר על ידי: {interaction.user.display_name} בשעה {datetime.now().strftime('%H:%M')}")
        
        # כיבוי הכפתורים
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        
        # שליחת הודעת עדכון לצוות ולחבר
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
        embed.set_footer(text=f"נדחה על ידי: {interaction.user.display_name}")
        
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        await interaction.followup.send(f"📢 בקשתו של {self.staff_member.mention} להעניק סטאף פרנד ל-{self.target_member.mention} **נדחתה** על ידי ההנהלה.")

    @discord.ui.button(label="🛠️ טפל כאן (סיבה/וויס)", style=discord.ButtonStyle.blurple, custom_id="claim_friend")
    async def claim(self, interaction: discord.Interaction):
        # כל מי שהוא סטאף (בעל הרול) יכול ללחוץ על טפל כאן כדי לציין שהוא בודק את זה בוויס
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק חברי צוות יכולים לקחת את הפקודה לטיפול!", ephemeral=True)
            
        # פתיחת החלון הקופץ להזנת סיבה/פרטי וויס
        modal = ClaimReasonModal(self.staff_member, self.target_member, interaction.message)
        await interaction.response.send_modal(modal)


# הפקודה שחבר הסטאף מריץ כדי לבקש עבור חבר שלו
@bot.command(name="staff_friend")
async def staff_friend_req(ctx, member: discord.Member):
    # 1. בדיקה שרק מי שיש לו את רול הסטאף (או אדמין) יכול להשתמש בפקודה
    staff_role = ctx.guild.get_role(STAFF_ROLE_ID)
    if staff_role not in ctx.author.roles and not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ פקודה זו מיועדת לחברי צוות @STAFF בלבד!")
        
    # 2. תיוג הסטאף והגדרת ה-Embed
    embed = discord.Embed(title="📜 בקשת סטאף פרנד חדשה!", color=discord.Color.gold(), timestamp=datetime.now())
    embed.add_field(name="👤 חבר הצוות הממליץ", value=ctx.author.mention, inline=False)
    embed.add_field(name="🎁 החבר המוצע לקבלת הרול", value=member.mention, inline=False)
    embed.add_field(name="📌 הרול המבוקש", value=f"<@&{STAFF_ROLE_ID}>", inline=False)
    embed.add_field(name="สถานะ (מצב בקשה)", value="⏳ ממתין להחלטת הנהלה עליונה או בדיקת וויס", inline=False)
    
    # שליחת ההודעה בדיוק באותו הערוץ שבו בוצעה הפקודה + תיוג ה-Staff
bot.run(os.environ.get("DISCORD_TOKEN"))

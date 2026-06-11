import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime

# --- הגדרות קבועות ---
STAFF_ROLE_ID = 1493335218004820180  # ID של רול הסטאף שלכם
ADMIN_ROLE_ID = 1485440480459227227  # תחליף ל-ID של רול ההנהלה הגבוהה שיכולה לאשר

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
    
    expected_level = (data[user_key]["xp"] // 150) + 1
    if expected_level > data[user_key]["level"]:
        data[user_key]["level"] = expected_level
        save_xp(data)
        return True, expected_level
    save_xp(data)
    return False, data[user_key]["level"]

# --- הגדרת הבוט ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- הגדרות ה-Views לטעינה קבועה ---
class HelpClaimView(discord.ui.View):
    def __init__(self, user_id=None):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="🛠️ טפל כאן (Claim)", style=discord.ButtonStyle.blurple, custom_id="help_claim_button_v2")
    async def help_claim(self, interaction: discord.Interaction):
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק חברי צוות בעלי רול @STAFF יכולים לטפל בקריאה זו!", ephemeral=True)
            
        await interaction.response.defer()
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.orange()
        embed.add_field(name="🔒 מצב טיפול", value=f"🔶 הקריאה נלקחה לטיפול על ידי חבר הצוות: {interaction.user.mention}", inline=False)
        
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        
        caller_mention = f"<@{self.user_id}>" if self.user_id else "המשתמש"
        await interaction.followup.send(f"📢 חבר הצוות {interaction.user.mention} החל לטפל בפנייה של {caller_mention}! נא להמתין בסבלנות.")

class BuyRoleModal(discord.ui.Modal, title="🛒 רכישת רול מחנות ה-XP"):
    role_num = discord.ui.TextInput(label="הכנס את מספר הרול שברצונך לקנות (1-4)", placeholder="לדוגמה: 1", max_length=1, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = load_xp()
        user_key = str(interaction.user.id)
        user_xp = data.get(user_key, {}).get("xp", 0)
        
        shop_items = {
            "1": {"cost": 10000, "role_id": ROLE_LEVEL_1_ID, "name": "רול ראשון"},
            "2": {"cost": 12000, "role_id": ROLE_LEVEL_2_ID, "name": "רול שני"},
            "3": {"cost": 15000, "role_id": ROLE_LEVEL_3_ID, "name": "רול שלישי"},
            "4": {"cost": 20000, "role_id": ROLE_LEVEL_4_ID, "name": "רול רביעי"}
        }
        
        choice = self.role_num.value.strip()
        if choice not in shop_items:
            return await interaction.followup.send("❌ מספר לא תקין! נא לבחור מספר בין 1 ל-4.", ephemeral=True)
            
        selected = shop_items[choice]
        cost = selected["cost"]
        role_id = selected["role_id"]
        role_name = selected["name"]
        
        if user_xp < cost:
            return await interaction.followup.send(f"❌ אין לך מספיק XP! הרול עולה `{cost:,} XP` וכרגע יש לך רק `{user_xp:,} XP`.", ephemeral=True)
            
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.followup.send("❌ שגיאה: הרול המבוקש לא הוגדר בצורה תקינה.", ephemeral=True)
            
        if role in interaction.user.roles:
            return await interaction.followup.send(f"❌ כבר יש לך את הרול `{role.name}`!", ephemeral=True)
            
        data[user_key]["xp"] -= cost
        save_xp(data)
        
        try:
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"🎉 ברכות! רכשת בהצלחה את הרול **{role.name}** עבור `{cost:,} XP`!", ephemeral=True)
            await interaction.channel.send(f"👑 כל הכבוד ל-{interaction.user.mention} שרכש את הרול **{role.name}** מהחנות עבור `{cost:,} XP`!")
        except discord.Forbidden:
            await interaction.followup.send(f"⚠️ לבוט אין מספיק הרשאות לתת את הרול פיזית בשרת.", ephemeral=True)

class XpShopNewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy Role", style=discord.ButtonStyle.blurple, custom_id="buy_role_main_button_v2")
    async def buy_button(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BuyRoleModal())

class StaffFriendView(discord.ui.View):
    def __init__(self, staff_id=None, target_id=None):
        super().__init__(timeout=None)
        self.staff_id = staff_id
        self.target_id = target_id

    @discord.ui.button(label="✅ אשר בקשה", style=discord.ButtonStyle.green, custom_id="approve_friend_v2")
    async def approve(self, interaction: discord.Interaction):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק הנהלת השרת הגבוהה מוסמכת לאשר בקשה זו!", ephemeral=True)
        
        await interaction.response.defer()
        target_member = interaction.guild.get_member(self.target_id) if self.target_id else None
        
        role_status = "אך לא הצלחתי לתת את הרול פיזית."
        if target_member:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff_role:
                try:
                    await target_member.add_roles(staff_role)
                    role_status = "והרול הוענק לו בהצלחה!"
                except:
                    pass
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ בקשת סטאף פרנד - אושרה סופית!"
        embed.set_field_at(3, name="สถานะ (מצב בקשה)", value=f"💚 הבקשה אושרה על ידי ההנהלה הגבוהה ({interaction.user.mention})!", inline=False)
        
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        target_mention = f"<@{self.target_id}>" if self.target_id else "המשתמש"
        staff_mention = f"<@{self.staff_id}>" if self.staff_id else "הצוות הממליץ"
        await interaction.followup.send(f"🎉 הבקשה אושרה! {target_mention} קיבל את הרול {role_status}\nחבר הצוות הממליץ: {staff_mention}")

    @discord.ui.button(label="❌ דחה בקשה", style=discord.ButtonStyle.red, custom_id="deny_friend_v2")
    async def deny(self, interaction: discord.Interaction):
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if admin_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק הנהלת השרת הגבוהה מוסמכת לדחות בקשה זו!", ephemeral=True)
        
        await interaction.response.defer()
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "❌ בקשת סטאף פרנד - נדחתה"
        embed.set_field_at(3, name="สถานะ (מצב בקשה)", value=f"❤️ הבקשה נדחתה על ידי ההנהלה ({interaction.user.mention}).", inline=False)
        
        for child in self.children:
            child.disabled = True
            
        await interaction.message.edit(embed=embed, view=self)
        staff_mention = f"<@{self.staff_id}>" if self.staff_id else "חבר הצוות"
        await interaction.followup.send(f"📢 בקשתו של {staff_mention} להעניק סטאף פרנד **נדחתה**.")

    @discord.ui.button(label="🛠️ טפל כאן (וויס)", style=discord.ButtonStyle.blurple, custom_id="claim_friend_v2")
    async def claim(self, interaction: discord.Interaction):
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ רק חברי צוות בעלי רול @STAFF יכולים לקחת את הבקשה לטיפול!", ephemeral=True)
            
        await interaction.response.defer()
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.orange()
        embed.set_field_at(3, name="สถานะ (מצב בקשה)", value=f"🔶 בטיפול ובבדיקת וויס על ידי: {interaction.user.mention}", inline=False)
        await interaction.message.edit(embed=embed)
        await interaction.followup.send(f"📢 הבקשה נלקחה לבדיקת וויס על ידי {interaction.user.mention}.", ephemeral=False)

@bot.event
async def on_ready():
    bot.add_view(XpShopNewView())
    bot.add_view(HelpClaimView())
    bot.add_view(StaffFriendView())
    print(f"🤖 הבוט {bot.user.name} עלה לאוויר ב-Railway!")

# ==========================================
# פקודות מערכת ה-XP והחנות המעוצבת
# ==========================================

@bot.command(name="xp")
async def check_xp(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_xp()
bot.run(os.environ.get("DISCORD_TOKEN"))

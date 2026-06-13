import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio

# ==========================================
# הגדרות ומשתנים קבועים (תחליף ל-ID האמיתיים שלך)
# ==========================================
ROLE_SILVER_ID = 1484226514051665930   # רול 1 - 30,000
ROLE_GOLD_ID = 1491063689502003360     # רול 2 - 20,000
ROLE_DIAMOND_ID = 1490894966262726687  # שלישי - 10,000
ROLE_MASTER_ID = 1490894895618195577   # רביעי - 5,000
ROLE_GOD_ID = 1490894817373196388      # חמישי - 2,500

# 🛑 שנה את ה-ID האלו ל-ID האמיתיים של השרת שלך כדי שהתיוגים יעבדו פיקס!
STAFF_ROLE_ID = 123456789012345678     # ID של תפקיד הצוות (לניהול טיקטים)
STAFF_FRIENDS_LOG_CHANNEL_ID = 123456789012345678  # ערוץ לוגים לבקשות Staff Friend

# ==========================================
# 1. מערכת חנות ה-XP (רולים ומחירים)
# ==========================================
class ShopDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="רול ראשון 🥇", description="מחיר: 30,000 XP", value=str(ROLE_SILVER_ID)),
            discord.SelectOption(label="רול שני 🥈", description="מחיר: 20,000 XP", value=str(ROLE_GOLD_ID)),
            discord.SelectOption(label="רול שלישי 🥉", description="מחיר: 10,000 XP", value=str(ROLE_DIAMOND_ID)),
            discord.SelectOption(label="רול רביעי 🎖️", description="מחיר: 5,000 XP", value=str(ROLE_MASTER_ID)),
            discord.SelectOption(label="רול חמישי 🏅", description="מחיר: 2,500 XP", value=str(ROLE_GOD_ID)),
        ]
        super().__init__(placeholder="בחר תפקיד לקנייה מהחנות...", min_values=1, max_values=1, options=options, custom_id="shop_select_persistent")

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values)
        role = interaction.guild.get_role(role_id)
        if not role or role in interaction.user.roles:
            await interaction.response.send_message("❌ שגיאה: התפקיד לא קיים או שאתה כבר מחזיק בו!", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"🎉 תתחדש! רכשת בהצלחה את התפקיד {role.mention}!", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

# ==========================================
# 2. מערכת הטיקטים (ניהול פנימי)
# ==========================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לקיחת טיקט 🔒", style=discord.ButtonStyle.green, custom_id="claim_ticket_persistent")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if STAFF_ROLE_ID:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff_role not in interaction.user.roles:
                await interaction.response.send_message("❌ רק אנשי צוות יכולים לקחת טיקט זה!", ephemeral=True)
                return
        await interaction.channel.edit(name=f"claimed-{interaction.user.name}")
        await interaction.response.send_message(f"🔒 הטיקט נלקח לטיפול על ידי {interaction.user.mention}!", ephemeral=False)

    @discord.ui.button(label="סגירת טיקט ❌", style=discord.ButtonStyle.red, custom_id="close_ticket_persistent")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ הטיקט ייסגר ויימחק בעוד 5 שניות...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="פתח טיקט ✉️", style=discord.ButtonStyle.blurple, custom_id="open_ticket_persistent")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(name=f"ticket-{member.name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎫 טיקט חדש נפתח!",
            description=f"שלום {member.mention},\nצוות התמיכה יענה לך בהקדם.\nניתן לנהל את הטיקט בכפתורים מטה.",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message(f"✅ הטיקט שלך נפתח: {ticket_channel.mention}", ephemeral=True)

# ==========================================
# 3. מערכת אימות (Verification) בכפתור
# ==========================================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="להתחלת אימות 🛡️", style=discord.ButtonStyle.green, custom_id="verify_user_persistent")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        verified_role = discord.utils.get(guild.roles, name="Verified")
        if not verified_role:
            verified_role = await guild.create_role(name="Verified")

        if verified_role in member.roles:
            await interaction.response.send_message("❌ אתה כבר מאומת בשרת!", ephemeral=True)
        else:
            await member.add_roles(verified_role)
            await interaction.response.send_message("✅ האימות בוצע בהצלחה! הערוצים נפתחו עבורך.", ephemeral=True)

# ==========================================
# 4. מערכת בקשות Staff Friend (אישור/דחייה)
# ==========================================
class StaffFriendReview(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Accept  ✔️", style=discord.ButtonStyle.success, custom_id="staff_friend_accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        staff_friend_role = discord.utils.get(guild.roles, name="Staff Friend")
        
        if not staff_friend_role:
            staff_friend_role = await guild.create_role(name="Staff Friend")

        if member:
            await member.add_roles(staff_friend_role)
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.green()
            embed.set_field_at(0, name="🟢 סטטוס:", value=f"אושר על ידי {interaction.user.mention}", inline=False)
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message(f"✅ אישרת את הבקשה והרול הוענק ל-{member.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ המשתמש כבר לא נמצא בשרת.", ephemeral=True)

    @discord.ui.button(label="Deny  ❌", style=discord.ButtonStyle.danger, custom_id="staff_friend_deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.set_field_at(0, name="🔴 סטטוס:", value=f"נדחה על ידי {interaction.user.mention}", inline=False)
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("❌ הבקשה נדחתה בהצלחה.", ephemeral=True)

# ==========================================
# הגדרות ומשתנים קבועים (תחליף ל-ID האמיתיים שלך)
# ==========================================
ROLE_SILVER_ID = 1484226514051665930   # רול 1 - 30,000
ROLE_GOLD_ID = 1491063689502003360     # רול 2 - 20,000
ROLE_DIAMOND_ID = 1490894966262726687  # שלישי - 10,000
ROLE_MASTER_ID = 1490894895618195577   # רביעי - 5,000
ROLE_GOD_ID = 1490894817373196388      # חמישי - 2,500

STAFF_ROLE_ID = 1490894966262726687     # ID של תפקיד הצוות לניהול טיקטים
STAFF_FRIENDS_LOG_CHANNEL_ID = 123456789012345678  # ערוץ לוגים לבקשות Staff Friend

# ==========================================
# 1. מערכת חנות ה-XP (רולים ומחירים)
# ==========================================
class ShopDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="רול ראשון 🥇", description="מחיר: 30,000 XP", value=str(ROLE_SILVER_ID)),
            discord.SelectOption(label="רול שני 🥈", description="מחיר: 20,000 XP", value=str(ROLE_GOLD_ID)),
            discord.SelectOption(label="רול שלישי 🥉", description="מחיר: 10,000 XP", value=str(ROLE_DIAMOND_ID)),
            discord.SelectOption(label="רול רביעי 🎖️", description="מחיר: 5,000 XP", value=str(ROLE_MASTER_ID)),
            discord.SelectOption(label="רול חמישי 🏅", description="מחיר: 2,500 XP", value=str(ROLE_GOD_ID)),
        ]
        super().__init__(placeholder="בחר תפקיד לקנייה מהחנות...", min_values=1, max_values=1, options=options, custom_id="shop_select")

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values)
        role = interaction.guild.get_role(role_id)
        if not role or role in interaction.user.roles:
            await interaction.response.send_message("❌ שגיאה: התפקיד לא קיים או שאתה כבר מחזיק בו!", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"🎉 תתחדש! רכשת בהצלחה את התפקיד {role.mention}!", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

# ==========================================
# 2. מערכת הטיקטים (ניהול פנימי)
# ==========================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לקיחת טיקט 🔒", style=discord.ButtonStyle.green, custom_id="claim_ticket")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if STAFF_ROLE_ID:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff_role not in interaction.user.roles:
                await interaction.response.send_message("❌ רק אנשי צוות יכולים לקחת טיקט זה!", ephemeral=True)
                return
        await interaction.channel.edit(name=f"claimed-{interaction.user.name}")
        await interaction.response.send_message(f"🔒 הטיקט נלקח לטיפול על ידי {interaction.user.mention}!", ephemeral=False)

    @discord.ui.button(label="סגירת טיקט ❌", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ הטיקט ייסגר ויימחק בעוד מספר שניות...")
        await interaction.channel.delete()

bot = client  # התיקון שיפתור את ה-NameError

import asyncio

# ==========================================
# הגדרות ומשתנים קבועים
# ==========================================
ROLE_1_ID = 1484226514051665930  
ROLE_2_ID = 1491063689502003360  
ROLE_3_ID = 1490894966262726687  
ROLE_4_ID = 1490894895618195577  
ROLE_5_ID = 1490894817373196388  

STAFF_ROLE_ID = 1490894966262726687  
STAFF_FRIENDS_LOG_CHANNEL_ID = 123456789012345678  

# ==========================================
# 1. מערכת חנות ה-XP (תפריט נפתח + באנר שרת)
# ==========================================
class ShopDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="רול ראשון 🥇", description="מחיר: 30,000 XP", value=str(ROLE_1_ID)),
            discord.SelectOption(label="רול שני 🥈", description="מחיר: 20,000 XP", value=str(ROLE_2_ID)),
            discord.SelectOption(label="רול שלישי 🥉", description="מחיר: 10,000 XP", value=str(ROLE_3_ID)),
            discord.SelectOption(label="רול רביעי 🎖️", description="מחיר: 5,000 XP", value=str(ROLE_4_ID)),
            discord.SelectOption(label="רול חמישי 🏅", description="מחיר: 2,500 XP", value=str(ROLE_5_ID)),
        ]
        super().__init__(placeholder="בחר תפקיד לקנייה מהחנות...", min_values=1, max_values=1, options=options, custom_id="shop_select_persistent")

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values)
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(role_id)

        if not role or role in member.roles:
            await interaction.response.send_message("❌ שגיאה: התפקיד לא נמצא או שאתה כבר מחזיק בו!", ephemeral=True)
            return
        await member.add_roles(role)
        await interaction.response.send_message(f"🎉 תתחדש! רכשת בהצלחה את התפקיד {role.mention}!", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ShopDropdown())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_shop(ctx):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    guild = ctx.guild
    embed = discord.Embed(
        title=f"🎁 חנות ה-XP הרשמית - {guild.name}",
        description=f"🛍️ **חנות הרולים של השרת**\n\n"
                    f"👑 <@&{ROLE_1_ID}> — 30,000 XP\n"
                    f"💎 <@&{ROLE_2_ID}> — 20,000 XP\n"
                    f"🔥 <@&{ROLE_3_ID}> — 10,000 XP\n"
                    f"⚡ <@&{ROLE_4_ID}> — 5,000 XP\n"
                    f"✨ <@&{ROLE_5_ID}> — 2,500 XP",
        color=discord.Color.from_rgb(142, 201, 57)
    )
    if guild.icon:
        embed.set_image(url=guild.icon.url)
    await ctx.send(embed=embed, view=ShopView())

# ==========================================
# 2. מערכת הטיקטים
# ==========================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="לקיחת טיקט 🔒", style=discord.ButtonStyle.green, custom_id="claim_ticket_persistent")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if STAFF_ROLE_ID:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff_role not in interaction.user.roles:
                await interaction.response.send_message("❌ רק אנשי צוות יכולים לקחת טיקט זה!", ephemeral=True)
                return
        await interaction.channel.edit(name=f"claimed-{interaction.user.name}")
        await interaction.response.send_message(f"🔒 הטיקט נלקח לטיפול על ידי {interaction.user.mention}!", ephemeral=False)

    @discord.ui.button(label="סגירת טיקט ❌", style=discord.ButtonStyle.red, custom_id="close_ticket_persistent")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ הטיקט ייסגר ויימחק בעוד 5 שניות...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="פתח טיקט ✉️", style=discord.ButtonStyle.blurple, custom_id="open_ticket_persistent")
    async def open_button(interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(name=f"ticket-{member.name}", overwrites=overwrites)
        ticket_embed = discord.Embed(
            title="🎫 טיקט חדש נפתח!",
            description=f"שלום {member.mention},\nצוות התמיכה עודכן ויענה לך בהקדם.\nבאפשרותך לנהל את הטיקט בעזרת הכפתורים למטה.",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=ticket_embed, view=TicketView())
        await interaction.response.send_message(f"הטיקט שלך נפתח בהצלחה! {ticket_channel.mention}", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    embed = discord.Embed(title="🎫 פתיחת טיקט תמיכה", description="צריך עזרה או יש לך שאלה לצוות המנהלים?\nלחץ על הכפתור למטה כדי לפתוח טיקט פרטי!", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketOpenView())

# ==========================================
# 3. מערכת אימות (Verification)
# ==========================================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="להתחלת אימות 🛡️", style=discord.ButtonStyle.green, custom_id="verify_user_persistent")
    async def verify_button(interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        verified_role = discord.utils.get(guild.roles, name="Verified")
        if not verified_role:
            verified_role = await guild.create_role(name="Verified")

        if verified_role in member.roles:
            await interaction.response.send_message("❌ אתה כבר מאומת בשרת!", ephemeral=True)
        else:
            await member.add_roles(verified_role)
            await interaction.response.send_message("✅ האימות בוצע בהצלחה!", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_verify(ctx):
    try:
        await ctx.message.delete()
    except discord.NotFound:
        pass
    embed = discord.Embed(title="🔒 אימות חשבון - Verification", description="ברוך הבא לשרת!\nכדי לקבל גישה לשאר הערוצים, לחץ על הכפתור למטה.", color=discord.Color.green())
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=VerifyView())

# ==========================================
# 4. מערכת בקשות Staff Friend
# ==========================================
class StaffFriendReview(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Accept  ✔️", style=discord.ButtonStyle.success, custom_id="staff_friend_accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        staff_friend_role = discord.utils.get(guild.roles, name="Staff Friend")
        if not staff_friend_role:
            staff_friend_role = await guild.create_role(name="Staff Friend")

        if member:
            await member.add_roles(staff_friend_role)
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.green()
            embed.set_field_at(2, name="🟢 סטטוס:", value=f"אושר על ידי {interaction.user.mention}", inline=False)
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message("✅ הבקשה אושרה!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ המשתמש עזב.", ephemeral=True)

    @discord.ui.button(label="Deny  ❌", style=discord.ButtonStyle.danger, custom_id="staff_friend_deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.set_field_at(2, name="🔴 סטטוס:", value=f"נדחה על ידי {interaction.user.mention}", inline=False)
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("❌ הבקשה נדחתה.", ephemeral=True)

@bot.command()
async def apply_staff_friend(ctx):
    log_channel = bot.get_channel(STAFF_FRIENDS_LOG_CHANNEL_ID)
    if not log_channel:
        await ctx.send("❌ ערוץ הלוגים לא נמצא.", ephemeral=True)
        return
    embed = discord.Embed(title="🛠️ בקשת Staff Friend חדשה", color=discord.Color.purple())
    embed.add_field(name="👤 מגיש הבקשה:", value=ctx.author.mention, inline=True)
    embed.add_field(name="🕒 זמן:", value=discord.utils.format_dt(ctx.message.created_at), inline=True)
    embed.add_field(name="🟡 סטטוס:", value="ממתין לטיפול...", inline=False)
    if ctx.guild.icon:
        embed.set_image(url=ctx.guild.icon.url)
    await log_channel.send(embed=embed, view=StaffFriendReview(ctx.author.id))
    await ctx.send("✅ בקשתך נשלחה לצוות הניהול!", ephemeral=True)

# ==========================================
# 5. פקודת העזרה המעוצבת החדשה (!h)
# ==========================================
@bot.command(name="h")


import os
bot.run(os.getenv("DISCORD_TOKEN"))

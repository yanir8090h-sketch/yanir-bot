import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

  Client,
  GatewayIntentBits,
  Partials,
  Events,
  EmbedBuilder,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
  PermissionFlagsBits,
  ChannelType,
  ComponentType,
  type Interaction,
  type Message,
  type ButtonInteraction,
  type StringSelectMenuInteraction,
  type GuildMember,
  type TextChannel,
} from "discord.js";
import { logger } from "./lib/logger.js";




}

// ==========================================
// ROLE & CHANNEL IDs
// ==========================================
const ROLE_STAFF_FRIEND_ID = BigInt("1493335218004820180");
const ROLE_MANAGEMENT_HELP = BigInt("1485440480459227227");
const ROLE_GENERAL_QUESTIONS = BigInt("1488259168593772554");
const ROLE_STAFF_TEST = BigInt("1485440385206456452");
const MEMBER_ROLE_ID = BigInt("1485680386972455042");

const SHOP_PRICES: Record<string, number> = {
  "Iron Member": 5000,
  "Bronze Member": 10000,
  "Silver Member": 25000,
  "Gold VIP": 50000,
};

const SHOP_ROLE_IDS: Record<string, bigint> = {
  "Iron Member": BigInt("1517997156173217945"),
  "Bronze Member": BigInt("1517997331822284912"),
  "Silver Member": BigInt("1517997465566052493"),
  "Gold VIP": BigInt("123456789012345678"),
};

// ==========================================
// XP STORE (in-memory)
// ==========================================
interface UserXP {
  xp: number;
  level: number;
}
const userXP = new Map<string, UserXP>();

function getUser(userId: string): UserXP {
  if (!userXP.has(userId)) {
    userXP.set(userId, { xp: 0, level: 1 });
  }
  return userXP.get(userId)!;
}

// ==========================================
// CLIENT
// ==========================================
export function startBot() {
  if (!TOKEN) return;

  const client = new Client({
    intents: [
      GatewayIntentBits.Guilds,
      GatewayIntentBits.GuildMessages,
      GatewayIntentBits.MessageContent,
      GatewayIntentBits.GuildMembers,
    ],
    partials: [Partials.Channel, Partials.Message],
  });

  // ==========================================
  // on_ready
  // ==========================================
  client.once(Events.ClientReady, async (c) => {
    logger.info(`Discord bot connected as ${c.user.tag}`);
    try {
      await c.application.commands.set([
        {
          name: "sf",
          description: "המלצה על חבר לקבלת רול Staff Friend",
          options: [
            {
              name: "member",
              description: "המשתמש שאתה ממליץ עליו",
              type: 6,
              required: true,
            },
          ],
        },
      ]);
      logger.info("Slash commands synced");
    } catch (e) {
      logger.error(e, "Failed to sync slash commands");
    }
  });

  // ==========================================
  // MESSAGE — XP + prefix commands
  // ==========================================
  client.on(Events.MessageCreate, async (message: Message) => {
    if (message.author.bot || !message.guild) return;

    const userId = message.author.id;
    const user = getUser(userId);
    const gain = Math.floor(Math.random() * 11) + 15;
    user.xp += gain;

    const xpNeeded = user.level * 1000;
    if (user.xp >= xpNeeded) {
      user.level += 1;
      await (message.channel as TextChannel).send(
        `🎉 כל הכבוד ${message.author}! עלית לרמה **${user.level}**!`
      );
    }

    if (!message.content.startsWith("!")) return;

    const args = message.content.slice(1).trim().split(/\s+/);
    const cmd = args.shift()?.toLowerCase();

    // ---- !xp / !rank / !רמה ----
    if (cmd === "xp" || cmd === "rank" || cmd === "רמה") {
      const target =
        message.mentions.members?.first() ||
        (message.guild.members.cache.get(message.author.id) as GuildMember);
      const tId = target?.id || message.author.id;
      const tUser = getUser(tId);
      const member =
        message.guild.members.cache.get(tId) ||
        (await message.guild.members.fetch(tId).catch(() => null));
      const displayName = member?.displayName || "משתמש";

      const embed = new EmbedBuilder()
        .setTitle(`📊 כרטיס ה-XP של ${displayName}`)
        .setColor(0x2f3136)
        .addFields(
          { name: "👤 משתמש:", value: `<@${tId}>`, inline: true },
          { name: "⭐ רמה:", value: `Level ${tUser.level}`, inline: true },
          {
            name: "✨ נקודות XP:",
            value: `${tUser.xp.toLocaleString()} / ${(tUser.level * 1000).toLocaleString()} XP`,
            inline: false,
          }
        );
      if (member?.displayAvatarURL()) embed.setThumbnail(member.displayAvatarURL());
      if (message.guild.iconURL()) embed.setImage(message.guild.iconURL()!);
      await message.reply({ embeds: [embed] });
    }

    // ---- !myshop / !shop / !חנות ----
    else if (cmd === "myshop" || cmd === "shop" || cmd === "חנות") {
      const embed = new EmbedBuilder()
        .setTitle(`🛒 חנות ה-XP של ${message.guild.name}`)
        .setDescription(
          "כאן תוכלו לבזבז את נקודות ה-XP שצברתם מדיבורים בצ׳אט כדי לקנות תפקידים ייחודיים!"
        )
        .setColor(0xffd700);

      for (const [name, price] of Object.entries(SHOP_PRICES)) {
        embed.addFields({ name: `✨ דרגת ${name}`, value: `מחיר: **${price.toLocaleString()} XP**`, inline: false });
      }
      if (message.guild.iconURL()) embed.setThumbnail(message.guild.iconURL()!);

      const row = new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
        new StringSelectMenuBuilder()
          .setCustomId("shop_buy")
          .setPlaceholder("בחר דרגה לקנייה...")
          .addOptions(
            new StringSelectMenuOptionBuilder()
              .setLabel("Iron Member").setDescription("מחיר: 5,000 XP").setEmoji("🪙").setValue("Iron Member"),
            new StringSelectMenuOptionBuilder()
              .setLabel("Bronze Member").setDescription("מחיר: 10,000 XP").setEmoji("🥉").setValue("Bronze Member"),
            new StringSelectMenuOptionBuilder()
              .setLabel("Silver Member").setDescription("מחיר: 25,000 XP").setEmoji("🥈").setValue("Silver Member"),
            new StringSelectMenuOptionBuilder()
              .setLabel("Gold VIP").setDescription("מחיר: 50,000 XP").setEmoji("👑").setValue("Gold VIP")
          )
      );
      await message.reply({ embeds: [embed], components: [row] });
    }

    // ---- !h ----
    else if (cmd === "h") {
      const rest = args.join(" ");
      let reason = "לא צוינה סיבה";
      let voiceRoom = "לא צוין חדר וויס";
      if (rest.includes("|")) {
        const [r, v] = rest.split("|", 2);
        reason = r.trim() || reason;
        voiceRoom = v.trim() || voiceRoom;
      } else if (rest) {
        reason = rest;
      }

      const embed = new EmbedBuilder()
        .setTitle(`⚠️ קריאת עזרה דחופה - ${message.guild.name} ⚠️`)
        .setDescription(
          `**👤 המבקש:** ${message.author}\n**📂 ערוץ טקסט:** ${message.channel}\n\n` +
          `**📝 סיבת הפנייה:**\n\`${reason}\`\n\n**🔊 חדר וויס נוכחי:**\n\`${voiceRoom}\`\n\n` +
          `**💡 מידע לצוות:**\nנציג פנוי מתוך <@&${ROLE_GENERAL_QUESTIONS}> מתבקש ללחוץ למטה ולהתייצב לעזרה.`
        )
        .setColor(0x2f3136)
        .setFooter({ text: `נשלח על ידי: ${message.author.username} • ${message.guild.name}` });
      if (message.guild.iconURL()) embed.setThumbnail(message.guild.iconURL()!);

      const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setCustomId("handle_help_request")
          .setLabel("טפל בפנייה 🛠️")
          .setStyle(ButtonStyle.Success)
      );

      try { await message.delete(); } catch {}
      const sent = await (message.channel as TextChannel).send({ embeds: [embed], components: [row] });
      void sent; // message URL stored in button handler via message.url
    }

    // ---- !setup_verify ----
    else if (cmd === "setup_verify") {
      if (!message.member?.permissions.has(PermissionFlagsBits.Administrator)) {
        return void message.reply("❌ אין לך הרשאת מנהל.");
      }
      const target = message.mentions.channels.first() as TextChannel | undefined || message.channel as TextChannel;
      const embed = new EmbedBuilder()
        .setTitle(`✅ אימות חברים - ${message.guild.name}`)
        .setDescription(
          `ברוכים הבאים לשרת **${message.guild.name}**!\n` +
          "על מנת לבצע אימות ולקבל גישה לכל ערוצי השרת, לחצו על הכפתור למטה.\n\n" +
          "**📜 חוקים בסיסיים:**\n• כבדו את כל חברי השרת\n• אין ספאם או פלוד\n• עקבו אחר הוראות הצוות\n\n• קראו את ערוץ החוקים לפני שאתם מתחילים!"
        )
        .setColor(0x2f3136)
        .setFooter({ text: `${message.guild.name} • מערכת אימות אוטומטית` });
      if (message.guild.iconURL()) embed.setImage(message.guild.iconURL()!);

      const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setCustomId("verify_member")
          .setLabel("אימות קבלת גישה ✅")
          .setStyle(ButtonStyle.Success)
      );
      try { await message.delete(); } catch {}
      await target.send({ embeds: [embed], components: [row] });
    }

    // ---- !setup_tickets ----
    else if (cmd === "setup_tickets") {
      if (!message.member?.permissions.has(PermissionFlagsBits.Administrator)) {
        return void message.reply("❌ אין לך הרשאת מנהל.");
      }
      const target = message.mentions.channels.first() as TextChannel | undefined || message.channel as TextChannel;
      const embed = new EmbedBuilder()
        .setTitle("🎫 מרכז הפניות והתמיכה")
        .setDescription(
          "צריכים עזרה מההנהלה? רוצים לשאול שאלה או להבחן לצוות השרת?\nבצעו בחירה מהתפריט הנפתח למטה והבוט יפתח לכם חדר פרטי מיידי."
        )
        .setColor(0x9b59b6);
      if (message.guild.iconURL()) embed.setThumbnail(message.guild.iconURL()!);

      const row = new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(
        new StringSelectMenuBuilder()
          .setCustomId("ticket_open")
          .setPlaceholder("בחר את סוג הפנייה שלך...")
          .addOptions(
            new StringSelectMenuOptionBuilder()
              .setLabel("עזרה מההנהלה").setDescription("פנייה ישירה להנהלת השרת").setEmoji("👑").setValue("management"),
            new StringSelectMenuOptionBuilder()
              .setLabel("שאלות כלליות").setDescription("בירורים, שאלות ועזרה כללית מהסטאף").setEmoji("💬").setValue("general"),
            new StringSelectMenuOptionBuilder()
              .setLabel("בחינות לצוות").setDescription("פתיחת חדר ומילוי טופס מועמדות לצוות").setEmoji("📝").setValue("staff_exam")
          )
      );
      try { await message.delete(); } catch {}
      await target.send({ embeds: [embed], components: [row] });
    }

    // ---- !rps ----
    else if (cmd === "rps") {
      const choices = ["אבן", "נייר", "מספריים"];
      const userChoice = args[0]?.toLowerCase();
      if (!userChoice || !choices.includes(userChoice)) {
        return void message.reply("❌ נא לבחור: `!rps אבן`, `!rps נייר` או `!rps מספריים`");
      }
      const botChoice = choices[Math.floor(Math.random() * 3)]!;
      if (userChoice === botChoice) {
        await message.reply(`🤝 תיקו! שנינו בחרנו **${botChoice}**.`);
      } else if (
        (userChoice === "אבן" && botChoice === "מספריים") ||
        (userChoice === "נייר" && botChoice === "אבן") ||
        (userChoice === "מספריים" && botChoice === "נייר")
      ) {
        await message.reply(`🎉 ניצחת! בחרת **${userChoice}** ואני בחרתי **${botChoice}**. זכית!`);
      } else {
        await message.reply(`😢 הפסדת! בחרת **${userChoice}** ואני בחרתי **${botChoice}**.`);
      }
    }

    // ---- !guess ----
    else if (cmd === "guess" || cmd === "g") {
      const num = parseInt(args[0] ?? "");
      if (isNaN(num) || num < 1 || num > 5) {
        return void message.reply("❌ נא לנחש מספר בין 1 ל-5! דוגמה: `!guess 3`");
      }
      const secret = Math.floor(Math.random() * 5) + 1;
      if (num === secret) {
        await message.reply(`🎯 בול! המספר היה **${secret}**. זכית!`);
      } else {
        await message.reply(`❌ פספוס! ניחשת **${num}** אבל המספר האמיתי היה **${secret}**.`);
      }
    }

    // ---- !football ----
    else if (cmd === "football" || cmd === "fb" || cmd === "goal") {
      const dirs = ["ימין", "שמאל", "אמצע"];
      const dir = args[0];
      if (!dir || !dirs.includes(dir)) {
        return void message.reply("⚽ לאן לבעוט? תבחר: `!football ימין`, `!football שמאל` או `!football אמצע`");
      }
      const gk = dirs[Math.floor(Math.random() * 3)]!;
      if (dir === gk) {
        await message.reply(`🧤 השוער זינק ל**${gk}** והדף את הכדור! אין גול.`);
      } else {
        await message.reply(`⚽ GOAL!! השוער זינק ל**${gk}** ואתה הבקעת ל**${dir}**! זכית!`);
      }
    }

    // ---- !blackjack ----
    else if (cmd === "blackjack" || cmd === "bj") {
      const c1 = Math.floor(Math.random() * 11) + 1;
      const c2 = Math.floor(Math.random() * 10) + 1;
      const userTotal = c1 + c2;
      const botTotal = Math.floor(Math.random() * 8) + 15;
      if (userTotal > 21) {
        await message.reply(`💥 נשרפת! הקלפים שלך: ${c1} + ${c2} = **${userTotal}**. הפסדת.`);
      } else if (botTotal > 21 || userTotal > botTotal) {
        await message.reply(`🃏 ניצחת בבלאקג'ק! לך יש **${userTotal}** ולבוט יש **${botTotal}**. זכית!`);
      } else {
        await message.reply(`😔 הפסדת בבלאקג'ק! לך יש **${userTotal}** ולבוט יש **${botTotal}**.`);
      }
    }
  });

  // ==========================================
  // INTERACTION HANDLER
  // ==========================================
  client.on(Events.InteractionCreate, async (interaction: Interaction) => {
    // ---- Slash /sf ----
    if (interaction.isChatInputCommand() && interaction.commandName === "sf") {
      const member = interaction.options.getMember("member") as GuildMember | null;
      if (!member) return void interaction.reply({ content: "❌ משתמש לא נמצא.", ephemeral: true });

      const userRoles = interaction.member ? (interaction.member as GuildMember).roles.cache.map((r) => r.id) : [];
      const isStaff = userRoles.includes(String(ROLE_GENERAL_QUESTIONS)) || (interaction.memberPermissions?.has(PermissionFlagsBits.Administrator) ?? false);
      if (!isStaff) {
        return void interaction.reply({ content: "❌ רק חברי צוות יכולים להמליץ על חברים!", ephemeral: true });
      }

      const embed = new EmbedBuilder()
        .setTitle("⚔️ בקשת Staff Friend חדשה")
        .setDescription(`חבר הצוות ${interaction.user} ממליץ להעניק רול לחבר שלו.`)
        .setColor(0x9b59b6)
        .addFields(
          { name: "👤 המועמד:", value: `${member}`, inline: true },
          { name: "📋 סטטוס בקשה:", value: "⏳ ממתין לאישור הנהלת השרת", inline: true }
        )
        .setFooter({ text: `שרת ${interaction.guild?.name ?? ""} • החלטת הנהלה בלבד` });
      if (interaction.guild?.iconURL()) embed.setThumbnail(interaction.guild.iconURL()!);
      if (interaction.guild?.bannerURL()) embed.setImage(interaction.guild.bannerURL()!);

      const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
        new ButtonBuilder()
          .setCustomId(`sf_accept:${member.id}`)
          .setLabel("Accept ✔")
          .setStyle(ButtonStyle.Success),
        new ButtonBuilder()
          .setCustomId(`sf_deny:${member.id}`)
          .setLabel("Deny ✖")
          .setStyle(ButtonStyle.Danger)
      );
      await interaction.reply({ embeds: [embed], components: [row] });
    }

    // ---- Button interactions ----
    if (interaction.isButton()) {
      const btn = interaction as ButtonInteraction;

      // verify_member
      if (btn.customId === "verify_member") {
        const guild = btn.guild!;
        const memberRole = guild.roles.cache.get(String(MEMBER_ROLE_ID));
        if (!memberRole) {
          return void btn.reply({ content: "❌ שגיאה: רול החברים לא מוגדר נכון.", ephemeral: true });
        }
        const gMember = btn.member as GuildMember;
        if (gMember.roles.cache.has(String(MEMBER_ROLE_ID))) {
          return void btn.reply({ content: "✅ כבר אומתת בעבר!", ephemeral: true });
        }
        await gMember.roles.add(memberRole);
        return void btn.reply({ content: "🎉 אומתת בהצלחה! כל ערוצי השרת נפתחו בפניך.", ephemeral: true });
      }

      // handle_help_request
      if (btn.customId === "handle_help_request") {
        const gMember = btn.member as GuildMember;
        const isStaff = gMember.roles.cache.has(String(ROLE_GENERAL_QUESTIONS)) || gMember.permissions.has(PermissionFlagsBits.Administrator);
        if (!isStaff) {
          return void btn.reply({ content: "❌ כפתור זה מיועד לחברי צוות בלבד!", ephemeral: true });
        }
        const newBtn = new ButtonBuilder()
          .setCustomId("handle_help_request_done")
          .setLabel(`בטיפול של ${gMember.displayName} ✔`)
          .setStyle(ButtonStyle.Secondary)
          .setDisabled(true);
        const newRow = new ActionRowBuilder<ButtonBuilder>().addComponents(newBtn);
        await btn.update({ components: [newRow] });
        await (btn.channel as TextChannel).send(`🙋‍♂️ הפנייה נלקחה לטיפול על ידי: ${btn.user}`);
        return;
      }

      // ticket handle
      if (btn.customId === "btn_ticket_handle") {
        const gMember = btn.member as GuildMember;
        const allowed = gMember.roles.cache.some((r) =>
          [String(ROLE_MANAGEMENT_HELP), String(ROLE_GENERAL_QUESTIONS), String(ROLE_STAFF_TEST)].includes(r.id)
        ) || gMember.permissions.has(PermissionFlagsBits.Administrator);
        if (!allowed) return void btn.reply({ content: "❌ אין לך הרשאה לטפל בטיקט זה!", ephemeral: true });

        const newBtn = new ButtonBuilder()
          .setCustomId("btn_ticket_handle_done")
          .setLabel(`בטיפול של ${gMember.displayName} ✔`)
          .setStyle(ButtonStyle.Secondary)
          .setDisabled(true);

        const closeBtn = new ButtonBuilder()
          .setCustomId("btn_ticket_close")
          .setLabel("סגור טיקט ❌")
          .setStyle(ButtonStyle.Danger);

        const newRow = new ActionRowBuilder<ButtonBuilder>().addComponents(newBtn, closeBtn);
        await btn.update({ components: [newRow] });
        await (btn.channel as TextChannel).send(`🔒 הפנייה ננעלה לטיפולו הבלעדי של ${btn.user}.`);
        return;
      }

      // ticket close
      if (btn.customId === "btn_ticket_close") {
        const gMember = btn.member as GuildMember;
        const allowed = gMember.roles.cache.some((r) =>
          [String(ROLE_MANAGEMENT_HELP), String(ROLE_GENERAL_QUESTIONS), String(ROLE_STAFF_TEST)].includes(r.id)
        ) || gMember.permissions.has(PermissionFlagsBits.Administrator);
        if (!allowed) return void btn.reply({ content: "❌ אין לך הרשאה לסגור טיקט זה!", ephemeral: true });

        await btn.reply({ content: "⚠️ הטיקט ייסגר ויימחק בעוד 5 שניות..." });
        setTimeout(async () => {
          try { await (btn.channel as TextChannel).delete(); } catch {}
        }, 5000);
        return;
      }

      // sf_accept
      if (btn.customId.startsWith("sf_accept:")) {
        const gMember = btn.member as GuildMember;
        if (!gMember.permissions.has(PermissionFlagsBits.Administrator)) {
          return void btn.reply({ content: "❌ רק הנהלת השרת יכולה לאשר בקשות!", ephemeral: true });
        }
        const targetId = btn.customId.split(":")[1]!;
        const guild = btn.guild!;
        const target = await guild.members.fetch(targetId).catch(() => null);
        const role = guild.roles.cache.get(String(ROLE_STAFF_FRIEND_ID));

        if (!target || !role) {
          return void btn.reply({ content: "❌ שגיאה: המשתמש או הרול לא נמצאו בשרת.", ephemeral: true });
        }
        await target.roles.add(role);

        const newRow = new ActionRowBuilder<ButtonBuilder>().addComponents(
          new ButtonBuilder().setCustomId(`sf_accept:${targetId}`).setLabel("Approved 🟩").setStyle(ButtonStyle.Success).setDisabled(true),
          new ButtonBuilder().setCustomId(`sf_deny:${targetId}`).setLabel("Deny ✖").setStyle(ButtonStyle.Danger).setDisabled(true)
        );
        await btn.update({ components: [newRow] });
        await (btn.channel as TextChannel).send(`🎉 הבקשה אושרה! ${target} קיבל את הרול ${role} על ידי ${btn.user}.`);
        return;
      }

      // sf_deny
      if (btn.customId.startsWith("sf_deny:")) {
        const gMember = btn.member as GuildMember;
        if (!gMember.permissions.has(PermissionFlagsBits.Administrator)) {
          return void btn.reply({ content: "❌ רק הנהלת השרת יכולה לדחות בקשות!", ephemeral: true });
        }
        const targetId = btn.customId.split(":")[1]!;
        const newRow = new ActionRowBuilder<ButtonBuilder>().addComponents(
          new ButtonBuilder().setCustomId(`sf_accept:${targetId}`).setLabel("Accept ✔").setStyle(ButtonStyle.Success).setDisabled(true),
          new ButtonBuilder().setCustomId(`sf_deny:${targetId}`).setLabel("Denied 🟥").setStyle(ButtonStyle.Danger).setDisabled(true)
        );
        await btn.update({ components: [newRow] });
        await (btn.channel as TextChannel).send(`❌ הבקשה נדחתה על ידי ${btn.user}.`);
        return;
      }
    }

    // ---- Select Menu interactions ----
    if (interaction.isStringSelectMenu()) {
      const sel = interaction as StringSelectMenuInteraction;

      // shop_buy
      if (sel.customId === "shop_buy") {
        const item = sel.values[0]!;
        const price = SHOP_PRICES[item]!;
        const roleId = SHOP_ROLE_IDS[item]!;
        const userId = sel.user.id;
        const uData = getUser(userId);

        if (uData.xp < price) {
          const missing = price - uData.xp;
          return void sel.reply({ content: `❌ חסרים לך עוד **${missing.toLocaleString()} XP** כדי לקנות את הדרגה **${item}**!`, ephemeral: true });
        }
        const guild = sel.guild!;
        const role = guild.roles.cache.get(String(roleId));
        if (!role) return void sel.reply({ content: "❌ שגיאה: הרול הזה לא נמצא בשרת, פנה למנהל.", ephemeral: true });

        const gMember = sel.member as GuildMember;
        if (gMember.roles.cache.has(String(roleId))) {
          return void sel.reply({ content: "❌ כבר יש לך את הדרגה הזו!", ephemeral: true });
        }

        uData.xp -= price;
        await gMember.roles.add(role);
        await sel.reply({ content: `🎉 תתחדש! קנית את הדרגה **${item}** בהצלחה! ירדו מחשבונך **${price.toLocaleString()} XP**.` });
        return;
      }

      // ticket_open
      if (sel.customId === "ticket_open") {
        const choice = sel.values[0]!;
        const guild = sel.guild!;
        const user = sel.user;
        const gMember = sel.member as GuildMember;

        const roleMap: Record<string, bigint> = {
          management: ROLE_MANAGEMENT_HELP,
          general: ROLE_GENERAL_QUESTIONS,
          staff_exam: ROLE_STAFF_TEST,
        };
        const labelMap: Record<string, string> = {
          management: "עזרה מההנהלה",
          general: "שאלות כלליות",
          staff_exam: "בחינות לצוות",
        };

        const targetRoleId = roleMap[choice]!;
        const targetRole = guild.roles.cache.get(String(targetRoleId));
        const label = labelMap[choice]!;

        const channelName = `🎫-${user.username}-${choice}`;

        const overwrites: any[] = [
          { id: guild.id, deny: [PermissionFlagsBits.ViewChannel] },
          { id: user.id, allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages, PermissionFlagsBits.EmbedLinks, PermissionFlagsBits.AttachFiles] },
          { id: guild.members.me!.id, allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages] },
        ];
        if (targetRole) {
          overwrites.push({ id: targetRole.id, allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages] });
        }

        await sel.deferReply({ ephemeral: true });

        const channel = await guild.channels.create({
          name: channelName,
          type: ChannelType.GuildText,
          permissionOverwrites: overwrites,
        });

        await sel.editReply({ content: `✅ הטיקט שלך נפתח בהצלחה! <#${channel.id}>` });

        let description = `שלום ${gMember},\nפתחת בהצלחה פנייה לצוות. אנא פרט את כל המידע הרלוונטי כאן.\n\n**לצוות השרת:** השתמשו בכפתורים למטה כדי לנהל את הפנייה.`;
        let embedColor = 0x3498db;
        let embedTitle = `🎫 פנייה בנושא: ${label}`;

        if (choice === "staff_exam") {
          embedTitle = "📝 טופס מועמדות לצוות השרת";
          embedColor = 0xffd700;
          description =
            `שלום ${gMember},\nעל מנת להגיש מועמדות לצוות, אנא **העתק את השאלות הבאות, ענה עליהן ושלח אותן כאן:**\n\n` +
            "1. שם מלא / כינוי בדיסקורד:\n" +
            "2. גיל:\n" +
            "3. כמה זמן אתה בשרת שלנו?\n" +
            "4. ניסיון קודם בצוות ניהול / מודרטור? (ואם עזבת — מדוע?)\n" +
            "5. איך אתה מגדיר צוות טוב? מה התכונות שצריכות להיות לחבר צוות?\n" +
            "6. מה היית עושה אם מישהו עובר על החוקים בשרת?\n" +
            "7. כמה זמן אתה חושב שתוכל לתת ממך לשרת בשבוע?\n" +
            "8. מדוע אתה רוצה להצטרף לצוות שלנו?\n" +
            "9. למה דווקא אתה מתאים? יש לך רעיון לשיפור השרת?\n" +
            "10. האם יש לך 2FA?\n\n" +
            "**לצוות השרת:** השתמשו בכפתורים למטה כדי לנהל את הפנייה.";
        }

        const embed = new EmbedBuilder()
          .setTitle(embedTitle)
          .setDescription(description)
          .setColor(embedColor);

        const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
          new ButtonBuilder().setCustomId("btn_ticket_handle").setLabel("טפל בפנייה 👮").setStyle(ButtonStyle.Success),
          new ButtonBuilder().setCustomId("btn_ticket_close").setLabel("סגור טיקט ❌").setStyle(ButtonStyle.Danger)
        );

        const roleMention = targetRole ? `<@&${targetRole.id}>` : "@צוות";
        await (channel as TextChannel).send({ content: `${gMember} | ${roleMention}`, embeds: [embed], components: [row] });
        return;
      }
    }
  });

  client.login(TOKEN).catch((e) => {
    logger.error(e, "Failed to login Discord bot");
  });
}

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))



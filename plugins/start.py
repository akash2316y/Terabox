
from bot import Bot
from config import OWNER_ID, PICS
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, CallbackQuery

START_MSG = """<b>⚡ Hᴇʏ, {mention} ~

<blockquote expandable>I ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ғɪʟᴇ sʜᴀʀᴇ ʙᴏᴛ V3.
Tʜᴇ ʙᴇsᴛ ᴘᴀʀᴛ ɪs ɪ ᴀᴍ ᴀʟsᴏ sᴜᴘᴘᴏʀᴛ ʀᴇǫᴜᴇsᴛ ғᴏʀᴄᴇsᴜʙ ғᴇᴀᴛᴜʀᴇ, Tᴏ ᴋɴᴏᴡ ᴅᴇᴛᴀɪʟᴇᴅ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴄʟɪᴄᴋ ᴀʙᴏᴜᴛ ᴍᴇ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴋɴᴏᴡ ᴍʏ ᴀʟʟ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs</blockquote></b>"""

ABOUT_TXT = """<b>🤖 ᴍʏ ɴᴀᴍᴇ: {botname}
<blockquote expandable>›› ᴏᴡɴᴇʀ: <a href='tg://openmessage?user_id=6830432475'>ᴀᴅʀ</a>
›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: <a href='https://t.me/imakashrabha'>ᴀᴋᴀsʜ</a></b></blockquote>"""

SETTING_TXT = """<b>⚙️ Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴs</b>
<blockquote expandable>◈ ᴛᴏᴛᴀʟ ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ:  <b>{total_fsub}</b>
◈ ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs:  <b>{total_admin}</b>
◈ ᴛᴏᴛᴀʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs:  <b>{total_ban}</b>
◈ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ:  <b>{autodel_mode}</b>
◈ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:  <b>{protect_content}</b>
◈ ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ:  <b>{hide_caption}</b>
◈ ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ:  <b>{chnl_butn}</b>
◈ ʀᴇǫᴜᴇsᴛ ғsᴜʙ ᴍᴏᴅᴇ: <b>{reqfsub}</b></blockquote>"""

@Bot.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Aʙᴏᴜᴛ ᴍᴇ", callback_data="about"), InlineKeyboardButton("Sᴇᴛᴛɪɴɢs ⚙️", callback_data="setting")]
    ])
    await message.reply_photo(photo="https://telegra.ph/file/5593d624d11d92bceb48e.jpg",
                               caption=START_MSG.format(
                                   mention=message.from_user.mention),
                               reply_markup=btn)


@Bot.on_callback_query()
async def start_callback_handler(client, query: CallbackQuery):
    data = query.data

    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data == "about":
        user = await client.get_users(OWNER_ID)
        user_link = f"https://t.me/{user.username}" if user.username else f"tg://openmessage?user_id={OWNER_ID}"
        ownername = f"<a href={user_link}>{user.first_name}</a>" if user.first_name else f"<a href={user_link}>no name !</a>"

        await query.edit_message_media(
            InputMediaPhoto("https://telegra.ph/file/6219c9d5edbeecfd3a45e.jpg",
                            ABOUT_TXT.format(botname=client.name, ownername=ownername)),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="start"),
                 InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data="close")]
            ])
        )

    elif data == "start":
        await query.edit_message_media(
            InputMediaPhoto("https://telegra.ph/file/5593d624d11d92bceb48e.jpg",
                            START_MSG.format(mention=query.from_user.mention)),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 Aʙᴏᴜᴛ ᴍᴇ", callback_data="about"),
                 InlineKeyboardButton("Sᴇᴛᴛɪɴɢs ⚙️", callback_data="setting")]
            ])
        )

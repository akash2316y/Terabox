from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging
import asyncio
from datetime import datetime
from pyrogram.enums import ChatMemberStatus
from dotenv import load_dotenv
from os import environ
import os
import time
from status import format_progress_bar
from video import download_video, upload_video
from web import keep_alive

load_dotenv('config.env', override=True)

logging.basicConfig(level=logging.INFO)

api_id = os.environ.get('TELEGRAM_API', '')
if len(api_id) == 0:
    logging.error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

api_hash = os.environ.get('TELEGRAM_HASH', '')
if len(api_hash) == 0:
    logging.error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)
    
bot_token = os.environ.get('BOT_TOKEN', '')
if len(bot_token) == 0:
    logging.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)
dump_id = os.environ.get('DUMP_CHAT_ID', '')
if len(dump_id) == 0:
    logging.error("DUMP_CHAT_ID variable is missing! Exiting now")
    exit(1)
else:
    dump_id = int(dump_id)

fsub_id = os.environ.get('FSUB_ID', '')
if len(fsub_id) == 0:
    logging.error("FSUB_ID variable is missing! Exiting now")
    exit(1)
else:
    fsub_id = int(fsub_id)

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_mention = message.from_user.mention
    reply_message = f"𝖶𝖾𝗅𝖼𝗈𝗆𝖾, {user_mention}.\n\n𝖨 𝖺𝗆 𝖺 𝖳𝖾𝗋𝖺𝖻𝗈𝗑 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝗋 𝖡𝗈𝗍. 𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺𝗇𝗒 𝗍𝖾𝗋𝖺𝖻𝗈𝗑 𝗅𝗂𝗇𝗄 𝗂 𝗐𝗂𝗅𝗅 𝖽𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝗐𝗂𝗍𝗁𝗂𝗇 𝖿𝖾𝗐 𝗌𝖾𝖼𝗈𝗇𝖽𝗌 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗍𝗈 𝗒𝗈𝗎✨."

    join_button = InlineKeyboardButton("ᴊᴏɪɴ", url="https://t.me/lowerassam")
    developer_button = InlineKeyboardButton("about", callback_data='about')
    reply_markup = InlineKeyboardMarkup([[join_button, developer_button]])

    await client.send_photo(
        chat_id=message.chat.id,
        photo="https://envs.sh/JP6.jpg",
        caption=reply_message,
        reply_markup=reply_markup
    )
    else:
        await message.reply_text(reply_message, reply_markup=reply_markup)

async def is_user_member(client, user_id):
    try:
        member = await client.get_chat_member(fsub_id, user_id)
        logging.info(f"User {user_id} membership status: {member.status}")
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking membership status for user {user_id}: {e}")
        return False

@app.on_message(filters.text)
async def handle_message(client, message: Message):
    if message.from_user is None:
        logging.error("Message does not contain user information.")
        return

    user_id = message.from_user.id
    user_mention = message.from_user.mention
    is_member = await is_user_member(client, user_id)

    valid_domains = [
    'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 
    'momerybox.com', 'teraboxapp.com', '1024tera.com', 
    'terabox.app', 'gibibox.com', 'goaibox.com', 'terasharelink.com', 'teraboxlink.com', 'terafileshare.com'
    ]

    terabox_link = message.text.strip()

    if not any(domain in terabox_link for domain in valid_domains):
        return  # Ignore non-Terabox messages silently

    reply_msg = await message.reply_text("𝖲𝖾𝗇𝖽𝗂𝗇𝗀 𝗒𝗈𝗎 𝗍𝗁𝖾 𝗆𝖾𝖽𝗂𝖺...🤤")

    try:
        file_path, thumbnail_path, video_title, video_duration = await download_video(terabox_link, reply_msg, user_mention, user_id)

        if file_path is None:
            return await reply_msg.edit_text("Failed to download. The link may be broken.")

        await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, user_mention, user_id, message)
      
    except Exception as e:
        logging.error(f"Download error: {e}")
        return await reply_msg.edit_text("❌ API returned a broken link.")

@app.on_callback_query()
async def handle_callback(client, callback_query):
    data = callback_query.data

    if data == "about":
        await callback_query.answer()
        await callback_query.message.reply_text(
            "🤖 **Bot Information:**\n\n"
            "• Developer: @yourusername\n"
            "• Language: Python\n"
            "• Library: Pyrogram\n"
            "• Purpose: Download and send Terabox files easily.\n\n"
            "✨ Just send a valid Terabox link to get started!",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("ʜᴏᴍᴇ", callback_data='home'),
                    InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data='close')
                ]
            ]),
            quote=True
        )

    elif data == "home":
        user_mention = callback_query.from_user.mention
        reply_message = f"𝖶𝖾𝗅𝖼𝗈𝗆𝖾, {user_mention}.\n\n𝖨 𝖺𝗆 𝖺 𝖳𝖾𝗋𝖺𝖻𝗈𝗑 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝗋 𝖡𝗈𝗍. 𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺𝗇𝗒 𝗍𝖾𝗋𝖺𝖻𝗈𝗑 𝗅𝗂𝗇𝗄 𝗂 𝗐𝗂𝗅𝗅 𝖽𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝗐𝗂𝗍𝗁𝗂𝗇 𝖿𝖾𝗐 𝗌𝖾𝖼𝗈𝗇𝖽𝗌 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗍𝗈 𝗒𝗈𝗎✨."
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("ᴊᴏɪɴ", url="https://t.me/lowerassam"),
                InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')
            ]
        ])
        await callback_query.message.reply_text(reply_message, reply_markup=reply_markup, quote=True)

    elif data == "close":
        await callback_query.answer("Closing...", show_alert=False)
        try:
            await callback_query.message.delete()
        except Exception as e:
            logging.warning(f"Failed to delete message: {e}")
            
if __name__ == "__main__":
    keep_alive()
    app.run()

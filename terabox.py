from pyrogram.types import InputMediaPhoto
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging
import asyncio
from datetime import datetime
from pyrogram.enums import ChatMemberStatus
from dotenv import load_dotenv
import os
import time
from status import format_progress_bar
from video import download_video, upload_video
from web import keep_alive

# Load environment variables
load_dotenv('config.env', override=True)

logging.basicConfig(level=logging.INFO)

# Environment setup
api_id = os.environ.get('TELEGRAM_API', '')
api_hash = os.environ.get('TELEGRAM_HASH', '')
bot_token = os.environ.get('BOT_TOKEN', '')
dump_id = os.environ.get('DUMP_CHAT_ID', '')
fsub_id = os.environ.get('FSUB_ID', '')

if not api_id or not api_hash or not bot_token or not dump_id or not fsub_id:
    logging.error("One or more environment variables are missing! Exiting.")
    exit(1)

dump_id = int(dump_id)
fsub_id = int(fsub_id)

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
import logging

AUTH_CHANNEL = "AkashServers"  # Channel username without @

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_mention = message.from_user.mention
    user_id = message.from_user.id

    # Force Join Check
    if AUTH_CHANNEL:
        try:
            member = await client.get_chat_member(AUTH_CHANNEL, user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                raise Exception("User not a member")
        except Exception as e:
            username = (await client.get_me()).username
            start_param = message.command[1] if len(message.command) > 1 else "true"
            join_url = f"https://t.me/{AUTH_CHANNEL}"
            retry_url = f"https://t.me/{username}?start={start_param}"
            
            buttons = [
                [InlineKeyboardButton("✅ Join Channel", url=join_url)],
                [InlineKeyboardButton("♻️ Try Again", url=retry_url)]
            ]

            await message.reply_text(
                f"<b>👋 Hello {user_mention},\n\nPlease join our channel to use this bot, then click Try Again.</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

    # If user is subscribed, show main welcome
    reply_message = f"𝖶𝖾𝗅𝖼𝗈𝗆𝖾, {user_mention}.\n\n𝖨 𝖺𝗆 𝖺 𝖳𝖾𝗋𝖺𝖻𝗈𝗑 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝗋 𝖡𝗈𝗍. 𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺𝗇𝗒 𝗍𝖾𝗋𝖺𝖻𝗈𝗑 𝗅𝗂𝗇𝗄 𝗂 𝗐𝗂𝗅𝗅 𝖽𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝗐𝗂𝗍𝗁𝗂𝗇 𝖿𝖾𝗐 𝗌𝖾𝖼𝗈𝗇𝖽𝗌 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗍𝗈 𝗒𝗈𝗎✨."
    buttons = [
    [InlineKeyboardButton("ᴊᴏɪɴ", url=f"https://t.me/{AUTH_CHANNEL}")],
    [InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')]
    ]

    await message.reply_photo(
        photo="https://envs.sh/JP6.jpg",
        caption=reply_message,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
async def is_user_member(client, user_id):
    try:
        member = await client.get_chat_member(AUTH_CHANNEL, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False
        
# Callback handler for "About"
@app.on_callback_query(filters.regex("about"))
async def about_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()  # Just to stop loading circle

    about_text = (
        "<b>🤖 Bot Name:</b> Terabox Downloader\n"
        "<b>👨‍💻 Developer:</b> @AkashBotDev\n"
        "<b>⚙️ Features:</b>\n"
        "• Download from Terabox\n"
        "• Stream via Telegram\n"
        "• Force Join Enabled\n\n"
        "<b>📢 Channel:</b> @lowerassam"
    )
    reply_markup=InlineKeyboardMarkup([InlineKeyboardButton("ʜᴏᴍᴇ", callback_data='home'),
                                        InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data='close')]

# Optional: Back to start message
@app.on_callback_query(filters.regex("start_back"))
async def back_to_start(client, callback_query: CallbackQuery):
    await start_command(client, callback_query.message)


# Handle Terabox links
@app.on_message(filters.text)
async def handle_message(client, message: Message):
    if message.from_user is None:
        return

    user_id = message.from_user.id
    user_mention = message.from_user.mention
    is_member = await is_user_member(client, user_id)

    valid_domains = [
        'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 
        'momerybox.com', 'teraboxapp.com', '1024tera.com', 
        'terabox.app', 'gibibox.com', 'goaibox.com', 
        'terasharelink.com', 'teraboxlink.com', 'terafileshare.com'
    ]

    terabox_link = message.text.strip()

    if not any(domain in terabox_link for domain in valid_domains):
        return

    reply_msg = await message.reply_text("𝖲𝖾𝗇𝖽𝗂𝗇𝗀 𝗒𝗈𝗎 𝗍𝗁𝖾 𝗆𝖾𝖽𝗂𝖺...🤤")

    try:
        file_path, thumbnail_path, video_title, video_duration = await download_video(
            terabox_link, reply_msg, user_mention, user_id
        )

        if file_path is None:
            return await reply_msg.edit_text("Failed to download. The link may be broken.")

        await upload_video(
            client, file_path, thumbnail_path, video_title, reply_msg,
            user_mention, user_id, message
        )

    except Exception as e:
        logging.error(f"Download error: {e}")
        await reply_msg.edit_text("❌ API returned a broken link.")

# Handle button callbacks
@app.on_callback_query()
async def handle_callback(client, callback_query):
    data = callback_query.data

    if data == "about":
        await callback_query.answer()
        await callback_query.message.edit_caption(
            caption=(
                "🤖 **Bot Information:**\n\n"
                "• Developer: @yourusername\n"
                "• Language: Python\n"
                "• Library: Pyrogram\n"
                "• Purpose: Download and send Terabox files easily.\n\n"
                "✨ Just send a valid Terabox link to get started!"
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("ʜᴏᴍᴇ", callback_data='home'),
                    InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data='close')
                ]
            ])
        )

    elif data == "home":
        await callback_query.answer()

        user_mention = callback_query.from_user.mention
        reply_message = f"𝖶𝖾𝗅𝖼𝗈𝗆𝖾, {user_mention}.\n\n𝖨 𝖺𝗆 𝖺 𝖳𝖾𝗋𝖺𝖻𝗈𝗑 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝗋 𝖡𝗈𝗍. 𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺𝗇𝗒 𝗍𝖾𝗋𝖺𝖻𝗈𝗑 𝗅𝗂𝗇𝗄 𝗂 𝗐𝗂𝗅𝗅 𝖽𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝗐𝗂𝗍𝗁𝗂𝗇 𝖿𝖾𝗐 𝗌𝖾𝖼𝗈𝗇𝖽𝗌 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗍𝗈 𝗒𝗈𝗎✨."

        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("ᴊᴏɪɴ", url="https://t.me/lowerassam"),
                InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')
            ]
        ])

        try:
            await callback_query.message.edit_media(
                media=InputMediaPhoto(
                    media="https://envs.sh/JP6.jpg",
                    caption=reply_message
                ),
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.warning(f"Failed to edit home screen: {e}")

    elif data == "close":
        await callback_query.answer()
        
        try:
            await callback_query.message.delete()
        except Exception as e:
            logging.warning(f"Couldn't delete callback message: {e}")

        try:
            if callback_query.message.reply_to_message:
                await callback_query.message.reply_to_message.delete()
        except Exception as e:
            logging.warning(f"Couldn't delete reply_to_message: {e}")

# Run bot
if __name__ == "__main__":
    keep_alive()
    app.run()

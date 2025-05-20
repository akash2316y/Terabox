from pyrogram.types import InputMediaPhoto
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging
import asyncio
from datetime import datetime
from pyrogram.enums import ChatMemberStatus
from dotenv import load_dotenv
import os
user_queues = {}
user_tasks = {}
import time
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
                [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url=join_url)],
                [InlineKeyboardButton("ᴊᴏɪɴᴇᴅ", url=retry_url)]
            ]

            await message.reply_text(
                f"<b>👋 𝖧𝖾𝗅𝗅𝗈 {user_mention},\n\n𝖯𝗅𝖾𝖺𝗌𝖾 𝗃𝗈𝗂𝗇 𝗈𝗎𝗋 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖻𝗈𝗍,\n𝗍𝗁𝖾𝗇 𝖢𝗅𝗂𝖼𝗄 𝖩𝗈𝗂𝗇𝖾𝖽.</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

    # If user is subscribed, show main welcome
    reply_message = f"𝖶𝖾𝗅𝖼𝗈𝗆𝖾, {user_mention}.\n\n𝖨 𝖺𝗆 𝖺 𝖳𝖾𝗋𝖺𝖻𝗈𝗑 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝗋 𝖡𝗈𝗍. 𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺𝗇𝗒 𝗍𝖾𝗋𝖺𝖻𝗈𝗑 𝗅𝗂𝗇𝗄 \n𝗂 𝗐𝗂𝗅𝗅 𝖽𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝗐𝗂𝗍𝗁𝗂𝗇 𝖿𝖾𝗐 𝗌𝖾𝖼𝗈𝗇𝖽𝗌 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗍𝗈 𝗒𝗈𝗎✨."

    join_button = InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/AkashServers")
    developer_button = InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')
    reply_markup = InlineKeyboardMarkup([[join_button, developer_button]])

    await client.send_photo(
        chat_id=message.chat.id,
        photo="https://envs.sh/JP6.jpg",
        caption=reply_message,
        reply_markup=reply_markup
    )

# Subscription check
async def is_user_member(client, user_id):
    try:
        member = await client.get_chat_member(fsub_id, user_id)
        logging.info(f"User {user_id} membership status: {member.status}")
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logging.error(f"Error checking membership status for user {user_id}: {e}")
        return False

# Handle Terabox links
@app.on_message(filters.text & filters.private)
async def handle_message(client, message: Message):
    if message.from_user is None:
        logging.error("Message does not contain user information.")
        return

    user_id = message.from_user.id
    user_mention = message.from_user.mention
    is_member = await is_user_member(client, user_id)

    if not is_member:
        return await start_command(client, message)

    valid_domains = [
        'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 
        'momerybox.com', 'teraboxapp.com', '1024tera.com', 
        'terabox.app', 'gibibox.com', 'goaibox.com', 
        'terasharelink.com', 'teraboxlink.com', 'terafileshare.com'
    ]

    terabox_link = message.text.strip()

    if not any(domain in terabox_link for domain in valid_domains):
        return await message.reply_text("❌ Please send a valid Terabox link.")

    queue_position = len(user_queues.get(user_id, [])) + 1
reply_msg = await message.reply_text(f"🔄 Processing...\nYour position in queue: **{queue_position}**")

    if user_id not in user_queues:
        user_queues[user_id] = []

    user_queues[user_id].append({
        "url": terabox_link,
        "reply_msg": reply_msg,
        "user_mention": user_mention,
        "message": message
    })

    if user_id not in user_tasks:
        asyncio.create_task(queue_worker(user_id, client))
else:
    pending = len(user_queues[user_id])
    await reply_msg.edit_text(f"⏳ Added to queue.\nCurrently you have **{pending} pending** task(s).")
    

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
                InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/AkashServers"),
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
        await callback_query.message.delete()
        try:
            await callback_query.message.reply_to_message.delete()
        except Exception as e:
            logging.warning(f"Couldn't delete reply_to_message: {e}")

@app.on_message(filters.command("cancel"))
async def cancel_task(client: Client, message: Message):
    user_id = message.from_user.id
    task = user_tasks.get(user_id)
    if task:
        task.cancel()
        await message.reply("❌ Your current task has been cancelled.")
    else:
        await message.reply("ℹ️ No active task found.")

async def queue_worker(user_id, client):
    while user_queues.get(user_id):
        task_data = user_queues[user_id].pop(0)
        task = asyncio.create_task(
            process_download_upload(
                client,
                url=task_data['url'],
                user_id=user_id,
                reply_msg=task_data['reply_msg'],
                user_mention=task_data['user_mention'],
                message=task_data['message']
            )
        )
        user_tasks[user_id] = task
        try:
            await task
        except asyncio.CancelledError:
            await task_data['reply_msg'].edit_text("❌ Your download has been canceled.")
        finally:
            user_tasks.pop(user_id, None)

async def process_download_upload(client, url, user_id, reply_msg, user_mention, message):
    try:
        file_path, thumbnail_path, video_title, video_duration = await download_video(
            url, reply_msg, user_mention, user_id
        )
        if not file_path:
            await reply_msg.edit_text("❌ Download failed.")
            return
        await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, user_mention, user_id, message)
    except Exception as e:
        logging.error(f"Error in process_download_upload: {e}")
        await reply_msg.edit_text("❌ Something went wrong during processing.")
        
# Run bot
if __name__ == "__main__":
    keep_alive()
    app.run()

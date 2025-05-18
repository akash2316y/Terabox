from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import UserNotParticipant
from config import CHANNEL_ID, FORCE_JOIN


# ✅ Check if user is a member of the channel
async def check_user_in_channel(client: Client, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"[Membership check error] {e}")
        return False


# 🔗 Generate join link dynamically (public or private channels)
async def get_join_link(client: Client) -> str | None:
    try:
        chat = await client.get_chat(CHANNEL_ID)
        if chat.username:
            return f"https://t.me/{chat.username}"
        else:
            return chat.invite_link or await client.export_chat_invite_link(CHANNEL_ID)
    except Exception as e:
        print(f"[Join link error] {e}")
        return None


# 📢 Send message to force user to join
async def send_force_join_message(client: Client, message: Message):
    join_link = await get_join_link(client)
    if not join_link:
        await message.reply_text("❌ Unable to generate join link. Please contact the admin.")
        return

    await message.reply_text(
        "**🔒 Please join the required channel to use this bot.**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=join_link)],
            [InlineKeyboardButton("✅ I've Joined", callback_data="refresh_check")]
        ])
    )


# 🔁 Start command handler with force join check
@Client.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    if FORCE_JOIN:
        user_id = message.from_user.id
        if not await check_user_in_channel(client, user_id):
            await send_force_join_message(client, message)
            return

    # ✅ If user is a member, send welcome message
    await message.reply_text("🎉 Welcome to the bot!\nSend any Terabox link to get started.")


# 🔄 Handle callback query for "I've Joined" button
@Client.on_callback_query(filters.regex("refresh_check"))
async def refresh_check(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_user_in_channel(client, user_id):
        await callback_query.message.edit_text("✅ Access granted. You can now use the bot.")
    else:
        await callback_query.answer("❌ You still haven't joined the channel.", show_alert=True)
  

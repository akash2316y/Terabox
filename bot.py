from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from config import OWNER_ID
from database import kingdb

@Client.on_message(filters.command('add_fsub') & filters.private & filters.user(OWNER_ID))
async def add_forcesub(client, message: Message):
    pro = await message.reply("🔄 Processing...", quote=True)
    fsubs = message.text.split()[1:]

    if not fsubs:
        return await pro.edit("❌ Channel ID provide karo. Jaise: `/add_fsub -1001234567890`")

    added = []
    for channel_id in fsubs:
        if await kingdb.add_channel(channel_id):
            added.append(channel_id)
    
    if added:
        await pro.edit(f"✅ Added Force Sub channels:\n`{', '.join(added)}`")
    else:
        await pro.edit("⚠️ Koi bhi naya channel add nahi hua.")

@Client.on_message(filters.command('remove_fsub') & filters.private & filters.user(OWNER_ID))
async def remove_forcesub(client, message: Message):
    pro = await message.reply("🔄 Processing...", quote=True)
    fsubs = message.text.split()[1:]

    if not fsubs:
        return await pro.edit("❌ Channel ID provide karo. Jaise: `/remove_fsub -1001234567890`")

    removed = []
    for channel_id in fsubs:
        if await kingdb.remove_channel(channel_id):
            removed.append(channel_id)
    
    if removed:
        await pro.edit(f"✅ Removed:\n`{', '.join(removed)}`")
    else:
        await pro.edit("⚠️ Koi channel remove nahi hua.")

@Client.on_callback_query(filters.regex("toggle_request_mode"))
async def toggle_request_mode(client, query: CallbackQuery):
    current_mode = await kingdb.get_mode("request_mode")
    new_mode = "off" if current_mode == "on" else "on"
    await kingdb.set_mode("request_mode", new_mode)
    await query.answer(f"Mode changed to: {new_mode.upper()}", show_alert=True)
    await query.message.delete()
    await owner_dashboard(client, query.message)

@Client.on_message(filters.command("dashboard") & filters.user(OWNER_ID))
async def owner_dashboard(client, message: Message):
    current_mode = await kingdb.get_mode("request_mode")
    channels = await kingdb.get_all_channels()
    channel_list = "\n".join([f"`{ch}`" for ch in channels]) or "No channels added."

    text = (
        f"**👑 Owner Dashboard**\n\n"
        f"**📢 Force Sub Channels:**\n{channel_list}\n\n"
        f"**🔁 Request Mode:** `{current_mode.upper()}`"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add FSub", callback_data="add_fsub"),
         InlineKeyboardButton("➖ Remove FSub", callback_data="remove_fsub")],
        [InlineKeyboardButton("🔁 Toggle Request Mode", callback_data="toggle_request_mode")],
    ])

    await message.reply(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


from bot import Bot
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from database.database import kingdb 

@Bot.on_message(filters.command('add_fsub') & filters.private & filters.user(OWNER_ID))
async def add_forcesub(client:Client, message:Message):
    from plugins.autoDelete import convert_time
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    check=0
    channel_ids = await kingdb.get_all_channels()
    fsubs = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])

    if not fsubs:
        await pro.edit("<b>Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ Aᴅᴅ ᴄʜᴀɴɴᴇʟ ɪᴅs\n<blockquote><u>EXAMPLE</u> :\n/add_fsub [channel_ids] :</b> ʏᴏᴜ ᴄᴀɴ ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴀᴛ ᴀ ᴛɪᴍᴇ.</blockquote>", reply_markup=reply_markup)
        return

    channel_list = ""
    for id in fsubs:
        try:
            id = int(id)
        except:
            channel_list += f"<b><blockquote>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{id}</code></blockquote></b>\n\n"
            continue

        if id in channel_ids:
            channel_list += f"<blockquote><b>ɪᴅ: <code>{id}</code>, ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛ..</b></blockquote>\n\n"
            continue

        id = str(id)
        if id.startswith('-') and id[1:].isdigit() and len(id)==14:
            try:
                data = await client.get_chat(id)
                link = data.invite_link
                cname = data.title

                if not link:
                    link = await client.export_chat_invite_link(id)

                channel_list += f"<b><blockquote>NAME: <a href = {link}>{cname}</a> (ID: <code>{id}</code>)</blockquote></b>\n\n"
                check+=1

            except:
                channel_list += f"<b><blockquote>ɪᴅ: <code>{id}</code>\n<i>ᴜɴᴀʙʟᴇ ᴛᴏ ᴀᴅᴅ ғᴏʀᴄᴇ-sᴜʙ, ᴄʜᴇᴄᴋ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴏʀ ʙᴏᴛ ᴘᴇʀᴍɪsɪᴏɴs ᴘʀᴏᴘᴇʀʟʏ..</i></blockquote></b>\n\n"

        else:
            channel_list += f"<b><blockquote>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{id}</code></blockquote></b>\n\n"
            continue

    if check == len(fsubs):
        for id in fsubs:
            await kingdb.add_channel(int(id))

        await pro.edit(f'<b><i>Uᴘᴅᴀᴛɪɴɢ ᴄʜᴀᴛ-ɪᴅ ʟɪsᴛ...</i></b>')
        await client.update_chat_ids()

        await pro.edit(f'<b>Fᴏʀᴄᴇ-Sᴜʙ Cʜᴀɴɴᴇʟ Aᴅᴅᴇᴅ ✅</b>\n\n{channel_list}', reply_markup=reply_markup, disable_web_page_preview=True)

    else:
        await pro.edit(f'<b>❌ Eʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ Aᴅᴅɪɴɢ Fᴏʀᴄᴇ-Sᴜʙ Cʜᴀɴɴᴇʟs</b>\n\n{channel_list.strip()}\n\n<b><i>Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ...</i></b>', reply_markup=reply_markup, disable_web_page_preview = True)


@Bot.on_message(filters.command('del_fsub') & filters.private & filters.user(OWNER_ID))
async def delete_all_forcesub(client:Client, message:Message):
    pro = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
    channels = await kingdb.get_all_channels()
    fsubs = message.text.split()[1:]

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])

    if not fsubs:
        return await pro.edit("<b>⁉️ Pʟᴇᴀsᴇ, Pʀᴏᴠɪᴅᴇ ᴠᴀʟɪᴅ ɪᴅs ᴏʀ ᴀʀɢᴜᴍᴇɴᴛs\n<blockquote><u>EXAMPLES</u> :\n/del_fsub [channel_ids] :</b> ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ sᴘᴇᴄɪғɪᴇᴅ ɪᴅs\n<code>/del_fsub all</code> : ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀᴄᴇ-sᴜʙ ɪᴅs</blockquote>", reply_markup=reply_markup)

    if len(fsubs) == 1 and fsubs[0].lower() == "all":
        if channels:
            for id in channels:
                await kingdb.del_channel(id)
            ids = "\n".join(f"<blockquote><code>{channel}</code> ✅</blockquote>" for channel in channels)
            await pro.edit(f"<b>⛔️ Aʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ Cʜᴀɴɴᴇʟ ɪᴅ ᴀʀᴇ Dᴇʟᴇᴛᴇᴅ :\n{ids}</b>", reply_markup=reply_markup)
        else:
            return await pro.edit("<b><blockquote>⁉️ Nᴏ Cʜᴀɴɴᴇʟ ɪᴅ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Dᴇʟᴇᴛᴇ</blockquote></b>", reply_markup=reply_markup)

    if len(channels) >= 1:
        passed = ''
        for sub_id in fsubs:
            try:
                id = int(sub_id)
            except:
                passed += f"<b><blockquote><i>ɪɴᴠᴀʟɪᴅ ɪᴅ: <code>{sub_id}</code></i></blockquote></b>\n"
                continue
            if id in channels:
                await kingdb.del_channel(id)
                passed += f"<blockquote><code>{id}</code> ✅</blockquote>\n"
            else:
                passed += f"<b><blockquote><code>{id}</code> ɴᴏᴛ ɪɴ ғᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs</blockquote></b>\n"

        await client.update_chat_ids()
        await pro.edit(f"<b>⛔️ Pʀᴏᴠɪᴅᴇᴅ Cʜᴀɴɴᴇʟ ɪᴅ ᴀʀᴇ Dᴇʟᴇᴛᴇᴅ :\n\n{passed}</b>", reply_markup=reply_markup)
    else:
        await pro.edit("<b><blockquote>⁉️ Nᴏ Cʜᴀɴɴᴇʟ ɪᴅ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Dᴇʟᴇᴛᴇ</blockquote></b>", reply_markup=reply_markup)


@Bot.on_message(filters.command('fsub_chnl') & filters.private)
async def get_forcesub(client:Client, message: Message):
    from pyrogram.enums import ChatAction
    pro = await message.reply(f'<b><i>Fᴇᴛᴄʜɪɴɢ ᴄʜᴀᴛ ɪᴅ ʟɪsᴛ...</i></b>', quote=True)
    await message.reply_chat_action(ChatAction.TYPING)

    channel_list = await client.update_chat_ids()
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data = "close")]])
    await message.reply_chat_action(ChatAction.CANCEL)
    await pro.edit(f"<b>⚡ 𝗙𝗢𝗥𝗖𝗘-𝗦𝗨𝗕 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗜𝗦𝗧 :</b>\n\n{channel_list}", reply_markup=reply_markup, disable_web_page_preview=True)

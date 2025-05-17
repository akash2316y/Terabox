# handlers.py
from bot import Bot
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated

@Bot.on_chat_member_updated()
async def handle_Chatmembers(client, chat_member_updated: ChatMemberUpdated):
    # original code here
    pass

@Bot.on_chat_join_request()
async def handle_join_request(client, chat_join_request):
    # original code here
    pass

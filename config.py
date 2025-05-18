import os

# Basic Bot Config
BOT_TOKEN = os.environ.get("7859871122:AAGEtAxCh8Mw8OrIT3z8kCO3WWw8YD1cS-U")
TELEGRAM_API = os.environ.get("7721764")
TELEGRAM_HASH = os.environ.get("a9c08aae19aa4c8b37ff658d1951a1f7")

# Optional or Important IDs
try:
    DUMP_CHAT_ID = int(os.environ.get("DUMP_CHAT_ID", "-1002460543591"))
except ValueError:
    raise ValueError("DUMP_CHAT_ID must be an integer.")

try:
    OWNER_ID = int(os.environ.get("OWNER_ID", "6987158459"))
except ValueError:
    raise ValueError("OWNER_ID must be an integer.")

try:
    CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002008497819"))
except ValueError:
    raise ValueError("CHANNEL_ID must be an integer.")

# Boolean handling (e.g. True / False)
FORCE_JOIN = os.environ.get("FORCE_JOIN", "True").lower() in ("true", "1", "yes")

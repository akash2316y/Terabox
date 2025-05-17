# database.py

class KingDB:
    def __init__(self):
        self.channels = set()
        self.modes = {"request_mode": "off"}

    async def add_channel(self, channel_id):
        if channel_id not in self.channels:
            self.channels.add(channel_id)
            return True
        return False

    async def remove_channel(self, channel_id):
        if channel_id in self.channels:
            self.channels.remove(channel_id)
            return True
        return False

    async def get_all_channels(self):
        return list(self.channels)

    async def get_mode(self, mode_name):
        return self.modes.get(mode_name, "off")

    async def set_mode(self, mode_name, value):
        self.modes[mode_name] = value

kingdb = KingDB()

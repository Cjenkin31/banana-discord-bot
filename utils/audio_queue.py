import asyncio

class AudioQueue:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioQueue, cls).__new__(cls)
            cls._instance.queues = {}
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def get_queue(self, guild_id):
        async with self._instance._lock:
            return self._instance.queues.setdefault(guild_id, [])

    async def add_to_queue(self, guild_id, track_info):
        async with self._instance._lock:
            queue = self._instance.queues.setdefault(guild_id, [])
            queue.append(track_info)

    async def next_track(self, guild_id):
        async with self._instance._lock:
            queue = self._instance.queues.get(guild_id, [])
            if queue:
                return queue.pop(0)
            return None

    async def show_queue(self, guild_id):
        async with self._instance._lock:
            return list(self._instance.queues.get(guild_id, []))

    async def clear_queue(self, guild_id):
        async with self._instance._lock:
            if guild_id in self._instance.queues:
                self._instance.queues[guild_id] = []

    async def is_queue_empty(self, guild_id):
        async with self._instance._lock:
            return not self._instance.queues.get(guild_id, [])

    async def queue_length(self, guild_id):
        async with self._instance._lock:
            return len(self._instance.queues.get(guild_id, []))

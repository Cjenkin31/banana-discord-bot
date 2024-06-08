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
            if guild_id not in self._instance.queues:
                self._instance.queues[guild_id] = []
            return self._instance.queues[guild_id]

    async def add_to_queue(self, guild_id, track_info):
        async with self._instance._lock:
            queue = await self.get_queue(guild_id)
            queue.append(track_info)

    async def next_track(self, guild_id):
        async with self._instance._lock:
            queue = await self.get_queue(guild_id)
            if queue:
                return queue.pop(0)

    async def show_queue(self, guild_id):
        async with self._instance._lock:
            return await self.get_queue(guild_id)

    async def clear_queue(self, guild_id):
        async with self._instance._lock:
            if guild_id in self._instance.queues:
                self._instance.queues[guild_id] = []

    async def is_queue_empty(self, guild_id):
        async with self._instance._lock:
            queue = await self.get_queue(guild_id)
            return len(queue) == 0

    async def queue_length(self, guild_id):
        async with self._instance._lock:
            queue = await self.get_queue(guild_id)
            return len(queue)

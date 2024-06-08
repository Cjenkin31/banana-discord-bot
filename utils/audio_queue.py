import asyncio
import os
import random

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
            queue = self._instance.queues.get(guild_id, [])
            for track_info in queue:
                file_path = track_info["file"]
                self.remove_file_if_exists(file_path)
            self._instance.queues[guild_id] = []

    async def is_queue_empty(self, guild_id):
        async with self._instance._lock:
            queue = self._instance.queues.get(guild_id, [])
            if queue is None:
                return True
            return not queue

    async def queue_length(self, guild_id):
        async with self._instance._lock:
            queue = self._instance.queues.get(guild_id, [])
            if queue is None:
                return 0
            return len(queue)

    async def shuffle_queue(self, guild_id):
        async with self._instance._lock:
            queue = self._instance.queues.get(guild_id, [])
            if queue:
                random.shuffle(queue)

    def remove_file_if_exists(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File removed: {file_path}")
        except Exception as e:
            print(f"Failed to remove file {file_path}: {e}")

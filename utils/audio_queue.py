class AudioQueue:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioQueue, cls).__new__(cls)
            cls._instance.queues = {}
        return cls._instance

    def get_queue(self, guild_id):
        if guild_id not in self._instance.queues:
            self._instance.queues[guild_id] = []
        return self._instance.queues[guild_id]

    def add_to_queue(self, guild_id, track_info):
        self.get_queue(guild_id).append(track_info)

    def next_track(self, guild_id):
        queue = self.get_queue(guild_id)
        if queue:
            return queue.pop(0)

    def show_queue(self, guild_id):
        return self.get_queue(guild_id)

    def clear_queue(self, guild_id):
        if guild_id in self._instance.queues:
            self._instance.queues[guild_id] = []

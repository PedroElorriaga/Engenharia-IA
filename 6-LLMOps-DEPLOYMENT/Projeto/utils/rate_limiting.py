from time import time


class RateLimiter:
    def __init__(self, limit: int = 5, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests_log: dict[str, list] = {}

    def allow_request(self, user_id: str) -> bool:
        now = time()

        if user_id not in self.requests_log:
            self.requests_log[user_id] = []

        if len(self.requests_log[user_id]) >= self.limit:
            return False

        self.requests_log[user_id].append(now)
        return True

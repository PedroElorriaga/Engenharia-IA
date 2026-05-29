from time import time

requests_log: dict[str, list] = {}


def allow_request(user_id: str, limit: int = 5, window_seconds: int = 60) -> bool:
    now = time()

    if user_id not in requests_log:
        requests_log[user_id] = []

    if len(requests_log[user_id]) >= limit:
        return False

    requests_log[user_id].append(now)
    return True


user = "pedro"
for i in range(7):
    allowed = allow_request(user, limit=5, window_seconds=60)
    print(f"Request {i+1}: {'✅ Permitido' if allowed else '❌ Bloqueado'}")

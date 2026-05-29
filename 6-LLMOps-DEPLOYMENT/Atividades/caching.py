import redis

redis_client = redis.Redis(host='localhost', port=6379,
                           db=0, decode_responses=True)


def check_cache(id_embeding):
    cached_response = redis_client.get(id_embeding)
    return cached_response if cached_response else None


def generate_response():
    # Fingimos que pegamos o id de um texto em uma base de conhecimentos RAG...

    id_embeding = "123"
    response = check_cache(id_embeding)
    if not response:
        print("cache miss")
        redis_client.set(id_embeding, "Thung Thung Sahur", ex=60)
        return "Thung Thung Sahur"
    else:
        print("cache hit")
        return response


if __name__ == "__main__":
    while True:
        input("Enter ")
        print(generate_response())

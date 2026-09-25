import fakeredis

from app.cache import MemoryCache, RedisCache


def test_memory_cache_roundtrip_and_expiry():
    cache = MemoryCache()
    assert cache.get("missing") is None
    cache.setex("k", 60, "v")
    assert cache.get("k") == "v"
    cache.setex("k", -1, "v")
    assert cache.get("k") is None


def test_memory_cache_delete_pattern():
    cache = MemoryCache()
    cache.setex("recs:v1:1:10", 60, "a")
    cache.setex("recs:v1:1:20", 60, "b")
    cache.setex("other", 60, "c")
    cache.delete_pattern("recs:*:1:*")
    assert cache.get("recs:v1:1:10") is None
    assert cache.get("other") == "c"


def test_redis_cache_same_contract():
    cache = RedisCache.__new__(RedisCache)
    cache._client = fakeredis.FakeRedis(decode_responses=True)
    cache.setex("recs:v1:7:10", 60, "v")
    assert cache.get("recs:v1:7:10") == "v"
    cache.delete_pattern("recs:*:7:*")
    assert cache.get("recs:v1:7:10") is None

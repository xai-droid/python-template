import time
from cache import SimpleCache

def test_cache_basic(tmp_path):
    path = tmp_path / "c.json"
    c = SimpleCache(path=path, max_entries=3)
    c.set("x", 1)
    assert c.get("x") == 1
    # ttl expiration
    c.set("t", "val", ttl=0.3)
    assert c.get("t") == "val"
    time.sleep(0.35)
    assert c.get("t") is None
    # pruning by size
    c.set("a", 1); c.set("b", 2); c.set("c", 3); c.set("d", 4)
    assert c.size() <= 3
    # get_or_compute
    v = c.get_or_compute("compute", lambda: 999, ttl=1)
    assert v == 999
    assert c.get("compute") == 999
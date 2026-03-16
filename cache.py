import json
import os
import time

CACHE_FILE="airport_cache.json"
CACHE_EXPIRY_DAYS=7

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def get_cached(airport_name):
    cache = load_cache()
    entry = cache.get(airport_name)
    if not entry:
        return None
    # Check expiry
    age_days = (time.time() - entry["cached_at"]) / 86400
    if age_days > CACHE_EXPIRY_DAYS:
        print(f"Cache expired for {airport_name}, re-scraping...")
        return None
    print(f"Cache hit for {airport_name}")
    return entry["data"]


def set_cached(airport_name, data):
    cache = load_cache()
    cache[airport_name] = {
        "data": data,
        "cached_at": time.time()
    }
    save_cache(cache)
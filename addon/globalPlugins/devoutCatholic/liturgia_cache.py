import json
import os
import datetime
import urllib.request

# =========================
# Configurações
# =========================

CACHE_DAYS = 7
BASE_URL = "https://liturgia.up.railway.app"

ADDON_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(ADDON_DIR, "dados")
CACHE_FILE = os.path.join(DATA_DIR, "liturgia.json")


# =========================
# Helpers
# =========================

def _format_date(date):
    return date.strftime("%Y-%m-%d")


def _ensure_dirs():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


# =========================
# Cache
# =========================

def _load_cache():
    _ensure_dirs()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_cache(cache):
    _ensure_dirs()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# =========================
# Fetch
# =========================

def _fetch_single_day(date):
    url = (
        f"{BASE_URL}/"
        f"?dia={date.day}"
        f"&mes={date.month:02d}"
        f"&ano={date.year}"
    )

    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


# =========================
# API pública (igual ao React)
# =========================

def get_liturgia_by_date(date):
    cache = _load_cache()
    key = _format_date(date)

    # 1️⃣ já está no cache
    if key in cache:
        return cache[key]

    # 2️⃣ buscar na API
    data = _fetch_single_day(date)
    if not data:
        return None

    # 3️⃣ salvar no cache
    cache[key] = data

    # 4️⃣ manter só 7 dias
    if len(cache) > CACHE_DAYS:
        keys = sorted(cache.keys())
        for k in keys[:-CACHE_DAYS]:
            del cache[k]

    _save_cache(cache)
    return data

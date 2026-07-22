from __future__ import annotations

import html
import binascii
import hashlib
import hmac
import http.client
import ipaddress
import json
import os
import re
import secrets
import socket
import socketserver
import base64
import ssl
import sqlite3
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http.cookiejar import CookieJar
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed
from datetime import datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_local_env() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#") or "=" not in value:
            continue
        key, raw = value.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        raw = raw.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = raw


load_local_env()


PORT = int(os.environ.get("PORT") or os.environ.get("LEAD_TOOL_PORT", "8815"))
HOST = os.environ.get("LEAD_TOOL_HOST", "127.0.0.1")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")
ADMIN_SETTINGS_FILE = ROOT / "admin_settings.json"
APIFY_USAGE_SNAPSHOT_KEY = "_apifyUsageSnapshot"


def bootstrap_setting(key: str, default: str = "") -> str:
    sqlite_state_file = Path(os.environ.get("STATE_DATABASE_PATH") or (ROOT / "workbench-state.db"))
    if sqlite_state_file.exists():
        try:
            with sqlite3.connect(sqlite_state_file) as connection:
                row = connection.execute(
                    "SELECT settings FROM app_settings WHERE settings_key = ?",
                    ("admin",),
                ).fetchone()
            if row:
                settings = json.loads(row[0])
                value = settings.get(key) if isinstance(settings, dict) else None
                if value is not None and value != "":
                    return str(value)
        except (OSError, sqlite3.Error, json.JSONDecodeError):
            pass
    try:
        data = json.loads(ADMIN_SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return os.environ.get(key, default)
    value = data.get(key) if isinstance(data, dict) else None
    if value is None or value == "":
        return os.environ.get(key, default)
    return str(value)


GOOGLE_MAPS_KEY_FILE = ROOT / "google_maps_api_key.txt"
SOCIAL_CAPTURE_DIR = ROOT / "social-captures"
SOCIAL_CAPTURE_FILE = SOCIAL_CAPTURE_DIR / "captures.json"
SOCIAL_CAPTURE_LOCK = threading.Lock()
DISCOVERY_JOBS: dict[str, dict] = {}
DISCOVERY_JOBS_LOCK = threading.RLock()
LAST_JOB_CLEANUP_AT = 0.0
DISCOVERY_CREATE_LOCK = threading.Lock()
DISCOVERY_SCHEDULE_LOCK = threading.RLock()
ACTIVE_DISCOVERY_WORKERS: set[str] = set()
ACTIVE_DISCOVERY_WORKERS_LOCK = threading.Lock()
DISCOVERY_MAX_CONCURRENCY = max(1, int(bootstrap_setting("DISCOVERY_MAX_CONCURRENCY", "2")))
MAX_ACTIVE_DISCOVERY_JOBS_PER_USER = 3
MAX_ACTIVE_SCHEDULED_JOBS_PER_SALES = 9
SCHEDULE_CAPACITY_RETRY_MINUTES = 30
SCHEDULE_FAILED_RETRY_SLOTS = ((8, 0), (8, 30), (9, 0))
DISCOVERY_QUALIFIED_TARGET_MIN = 20
DISCOVERY_QUALIFIED_TARGET_MAX = 30
DISCOVERY_JOB_TTL = 60 * 60 * 24 * 7
NETWORK_DEFAULT_TIMEOUT = max(5, int(bootstrap_setting("NETWORK_DEFAULT_TIMEOUT", "12")))
DISCOVERY_SEARCH_TIMEOUT = max(8, int(os.environ.get("DISCOVERY_SEARCH_TIMEOUT", "18")))
APIFY_RUN_TIMEOUT_SECONDS = max(10, min(120, int(bootstrap_setting("APIFY_RUN_TIMEOUT_SECONDS", "120"))))
APIFY_DISCOVERY_SOURCE_MODES = {"social", "instagram", "facebook", "tiktok", "linkedin"}
ASSIGNED_COUNTRY_NONE = "__none__"
DISCOVERY_JOB_TIMEOUT_SECONDS = max(300, int(os.environ.get("DISCOVERY_JOB_TIMEOUT_SECONDS", "480")))
YOUTUBE_MAX_VIDEO_AGE_DAYS = 365 * 5
DISCOVERY_SCHEDULER_STOP = threading.Event()
DISCOVERY_SCHEDULER_STARTED = False
DISCOVERY_SCHEDULER_STARTED_LOCK = threading.Lock()
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
SQLITE_STATE_FILE = Path(os.environ.get("STATE_DATABASE_PATH") or (ROOT / "workbench-state.db"))
STATE_LOCK = threading.RLock()
STATE_STORE_INIT_LOCK = threading.Lock()
STATE_STORE_INITIALIZED = False
AUTH_USERNAME = os.environ.get("APP_USERNAME", "admin")
AUTH_PASSWORD = os.environ.get("APP_PASSWORD", "admin123")
HIDDEN_ADMIN_USERNAME = os.environ.get("HIDDEN_ADMIN_USERNAME", "17609281273")
HIDDEN_ADMIN_PASSWORD = os.environ.get("HIDDEN_ADMIN_PASSWORD", "17609281273")
AUTH_SECRET = os.environ.get("APP_AUTH_SECRET") or secrets.token_hex(32)
AUTH_COOKIE = "hima_session"
AUTH_MAX_AGE = 60 * 60 * 24 * 7
PASSWORD_HASH_ITERATIONS = 210_000

ADMIN_CONTROL_KEY = "_controlCenter"
ADMIN_CONTROL_DEFAULTS = {
    "schemaVersion": 2,
    "discovery": {
        "adminOnly": False,
        "targetMin": 20,
        "targetMax": 30,
        "taskTimeoutMinutes": 25,
        "fallbackEnabled": True,
        "globalSources": ["google", "osm", "dealer", "youtube", "facebook", "instagram", "tiktok", "linkedin"],
        "sourceCaps": {
            "google": 30, "osm": 20, "dealer": 40, "instagram": 30,
            "facebook": 30, "tiktok": 30, "youtube": 30, "linkedin": 30,
        },
        "sourceWeights": {
            "google": 3, "osm": 1, "dealer": 3, "instagram": 2,
            "facebook": 2, "tiktok": 2, "youtube": 2, "linkedin": 2,
        },
        "countrySourceOverrides": {},
    },
    "quality": {
        "scoreModelVersion": 11,
        "strictCountryMatch": True,
        "requireAutomotiveBusiness": True,
        "rejectPersonalAccounts": True,
        "requireContactOrWebsite": False,
        "blockRejectedMemory": True,
        "minimumAutoImportScore": 40,
        "minimumAiConfidence": 55,
        "scoreWeights": {
            "automotive": 20, "country": 20, "chineseNev": 10, "huawei": 10,
            "contact": 15, "officialWebsite": 10, "importDistribution": 8,
            "businessActivity": 4, "decisionMaker": 3,
        },
    },
    "ai": {
        "enabled": True,
        "failurePolicy": "manual_review",
        "dailyCallLimit": 1000,
        "dailyCostLimitUsd": 5.0,
        "promptVersion": "vehicle-export-v2",
    },
    "data": {
        "jobRetentionDays": 30,
        "searchRecordRetentionDays": 90,
        "backupReminderDays": 7,
        "lastBackupAt": "",
    },
    "security": {
        "sessionHours": 168,
        "passwordMinLength": 6,
        "sessionInvalidBefore": 0,
    },
}

socket.setdefaulttimeout(NETWORK_DEFAULT_TIMEOUT)

ADMIN_SETTING_DEFINITIONS = {
    "GOOGLE_MAPS_API_KEY": {"type": "secret", "label": "Google Maps Places API Key", "group": "maps", "status": "active", "use": "Google Maps 企业地点搜索"},
    "YOUTUBE_API_KEY": {"type": "secret", "label": "YouTube Data API Key", "group": "social", "status": "active", "use": "YouTube 官方频道/视频搜索"},
    "BRAVE_SEARCH_API_KEY": {"type": "secret", "label": "Brave Search API Key", "group": "search", "status": "active", "use": "Official Web Search API for websites and directories"},
    "SERPAPI_API_KEY": {"type": "secret", "label": "SerpApi API Key", "group": "search", "status": "active", "use": "Google Search and Google Maps result enrichment"},
    "HUNTER_API_KEY": {"type": "secret", "label": "Hunter.io API Key", "group": "email", "status": "active", "use": "Email candidates by company domain"},
    "APIFY_API_TOKEN": {"type": "secret", "label": "Apify API Token", "group": "social", "status": "active", "use": "Apify Actors for social and directory discovery"},
    "APIFY_FACEBOOK_ACTOR_ID": {"type": "text", "label": "Apify Facebook Actor ID", "group": "social", "status": "reserved", "use": "Override Facebook Actor, for example memo23/facebook-search-scraper"},
    "APIFY_INSTAGRAM_ACTOR_ID": {"type": "text", "label": "Apify Instagram Actor ID", "group": "social", "status": "reserved", "use": "Override Instagram Actor, for example apify/instagram-search-scraper"},
    "APIFY_TIKTOK_ACTOR_ID": {"type": "text", "label": "Apify TikTok Actor ID", "group": "social", "status": "reserved", "use": "Override TikTok Actor, for example clockworks/tiktok-scraper"},
    "APIFY_LINKEDIN_ACTOR_ID": {"type": "text", "label": "Apify LinkedIn Actor ID", "group": "social", "status": "reserved", "use": "Override LinkedIn Actor, for example harvestapi/linkedin-company-search"},
    "AI_PROVIDER": {"type": "text", "label": "AI Provider", "group": "ai", "status": "active", "use": "deepseek / qwen; used for lead verification"},
    "DEEPSEEK_API_KEY": {"type": "secret", "label": "DeepSeek API Key", "group": "ai", "status": "active", "use": "AI lead verification"},
    "DEEPSEEK_BASE_URL": {"type": "url", "label": "DeepSeek Base URL", "group": "ai", "status": "active", "use": "OpenAI-compatible endpoint"},
    "AI_MODEL_FAST": {"type": "text", "label": "AI Fast Model", "group": "ai", "status": "active", "use": "Fast lead screening model"},
    "AI_MODEL_DEFAULT": {"type": "text", "label": "AI Default Model", "group": "ai", "status": "active", "use": "Default lead verification model"},
    "AI_MODEL_STRONG": {"type": "text", "label": "AI Strong Model", "group": "ai", "status": "active", "use": "Manual/important lead review model"},
    "APOLLO_API_KEY": {"type": "secret", "label": "Apollo API Key", "group": "email", "status": "reserved", "use": "Reserved for B2B contacts and company enrichment"},
    "CLEARBIT_API_KEY": {"type": "secret", "label": "Clearbit API Key", "group": "company", "status": "reserved", "use": "Reserved for company/domain enrichment"},
    "FACEBOOK_ACCESS_TOKEN": {"type": "secret", "label": "Facebook Graph API Token", "group": "social", "status": "reserved", "use": "后续 Facebook 主页/线索接口"},
    "INSTAGRAM_ACCESS_TOKEN": {"type": "secret", "label": "Instagram Graph API Token", "group": "social", "status": "reserved", "use": "后续 Instagram 商业账号接口"},
    "TIKTOK_API_KEY": {"type": "secret", "label": "TikTok API Key", "group": "social", "status": "reserved", "use": "后续 TikTok 公开账号/商业接口"},
    "LINKEDIN_CLIENT_ID": {"type": "text", "label": "LinkedIn Client ID", "group": "social", "status": "reserved", "use": "后续 LinkedIn OAuth 接入"},
    "LINKEDIN_CLIENT_SECRET": {"type": "secret", "label": "LinkedIn Client Secret", "group": "social", "status": "reserved", "use": "后续 LinkedIn OAuth 接入"},
    "REDDIT_CLIENT_ID": {"type": "text", "label": "Reddit Client ID", "group": "social", "status": "reserved", "use": "后续 Reddit 社区接口"},
    "REDDIT_CLIENT_SECRET": {"type": "secret", "label": "Reddit Client Secret", "group": "social", "status": "reserved", "use": "后续 Reddit 社区接口"},
    "PUBLIC_BASE_URL": {"type": "url", "label": "公开访问地址", "group": "runtime", "status": "active", "use": "回调/公开链接"},
    "DISCOVERY_MAX_CONCURRENCY": {"type": "int", "label": "获客并发数", "group": "runtime", "status": "active", "use": "后台任务并发", "min": 1, "max": 8},
    "NETWORK_DEFAULT_TIMEOUT": {"type": "int", "label": "网络超时秒数", "group": "runtime", "status": "active", "use": "外部接口请求超时", "min": 5, "max": 60},
    "APIFY_RUN_TIMEOUT_SECONDS": {"type": "int", "label": "Apify 单次超时秒数", "group": "social", "status": "active", "use": "限制单个 Apify Actor 空跑时间", "min": 10, "max": 120},
}
ADMIN_RUNTIME_KEYS = {"PUBLIC_BASE_URL", "DISCOVERY_MAX_CONCURRENCY", "NETWORK_DEFAULT_TIMEOUT", "APIFY_RUN_TIMEOUT_SECONDS"}
ADMIN_CUSTOM_APIS_KEY = "_customApis"
ADMIN_SETTINGS_LOCK = threading.RLock()
ADMIN_SETTINGS_CACHE: dict | None = None
ADMIN_SETTINGS_CACHE_AT = 0.0


def cached_admin_settings(value: dict) -> dict:
    global ADMIN_SETTINGS_CACHE, ADMIN_SETTINGS_CACHE_AT
    ADMIN_SETTINGS_CACHE = value if isinstance(value, dict) else {}
    ADMIN_SETTINGS_CACHE_AT = time.monotonic()
    return json.loads(json.dumps(ADMIN_SETTINGS_CACHE, ensure_ascii=False))


class DynamicConcurrencyGate:
    def __init__(self, limit: int):
        self.limit = max(1, int(limit))
        self.active = 0
        self.condition = threading.Condition()

    def set_limit(self, limit: int) -> None:
        with self.condition:
            self.limit = max(1, int(limit))
            self.condition.notify_all()

    def __enter__(self):
        with self.condition:
            while self.active >= self.limit:
                self.condition.wait()
            self.active += 1
        return self

    def __exit__(self, exc_type, exc, traceback):
        with self.condition:
            self.active = max(0, self.active - 1)
            self.condition.notify_all()


DISCOVERY_WORKER_GATE = DynamicConcurrencyGate(DISCOVERY_MAX_CONCURRENCY)


def load_admin_settings_file() -> dict:
    if ADMIN_SETTINGS_CACHE is not None and time.monotonic() - ADMIN_SETTINGS_CACHE_AT < 5:
        return json.loads(json.dumps(ADMIN_SETTINGS_CACHE, ensure_ascii=False))
    try:
        initialize_state_store()
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT settings FROM app_settings WHERE settings_key = %s", ("admin",))
                    row = cursor.fetchone()
                    if row:
                        return cached_admin_settings(row[0] if isinstance(row[0], dict) else json.loads(row[0]))
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                row = connection.execute(
                    "SELECT settings FROM app_settings WHERE settings_key = ?",
                    ("admin",),
                ).fetchone()
                if row:
                    return cached_admin_settings(json.loads(row[0]))
    except (OSError, RuntimeError, sqlite3.Error, json.JSONDecodeError):
        pass
    if not ADMIN_SETTINGS_FILE.exists():
        return cached_admin_settings({})
    try:
        data = json.loads(ADMIN_SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return cached_admin_settings({})
    return cached_admin_settings(data if isinstance(data, dict) else {})


def save_admin_settings_file(settings: dict) -> None:
    encoded = json.dumps(settings, ensure_ascii=False)
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO app_settings (settings_key, settings, updated_at)
                    VALUES (%s, %s::jsonb, NOW())
                    ON CONFLICT (settings_key) DO UPDATE SET
                        settings = EXCLUDED.settings,
                        updated_at = NOW()
                    """,
                    ("admin", encoded),
                )
        cached_admin_settings(settings)
        return
    with sqlite3.connect(SQLITE_STATE_FILE) as connection:
        connection.execute(
            """
            INSERT INTO app_settings (settings_key, settings, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(settings_key) DO UPDATE SET
                settings = excluded.settings,
                updated_at = excluded.updated_at
            """,
            ("admin", encoded, datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
    cached_admin_settings(settings)


def runtime_setting(key: str, default: str = "") -> str:
    with ADMIN_SETTINGS_LOCK:
        settings = load_admin_settings_file()
        value = settings.get(key)
        if value is None or value == "":
            for item in settings.get(ADMIN_CUSTOM_APIS_KEY, []):
                if isinstance(item, dict) and item.get("envKey") == key:
                    value = item.get("value")
                    break
    if value is None or value == "":
        value = os.environ.get(key, default)
    return str(value or "").strip()


def merge_nested_settings(defaults: dict, value: dict | None) -> dict:
    merged = json.loads(json.dumps(defaults, ensure_ascii=False))
    if not isinstance(value, dict):
        return merged
    for key, item in value.items():
        if isinstance(item, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_nested_settings(merged[key], item)
        else:
            merged[key] = item
    return merged


def admin_control_settings() -> dict:
    settings = load_admin_settings_file()
    stored = settings.get(ADMIN_CONTROL_KEY)
    return normalize_admin_control(stored, stored)


def control_value(section: str, key: str, default=None):
    return admin_control_settings().get(section, {}).get(key, default)


def discovery_target_min() -> int:
    return max(1, min(100, int(control_value("discovery", "targetMin", DISCOVERY_QUALIFIED_TARGET_MIN))))


def discovery_target_max() -> int:
    return max(discovery_target_min(), min(120, int(control_value("discovery", "targetMax", DISCOVERY_QUALIFIED_TARGET_MAX))))


def discovery_task_timeout_seconds() -> int:
    minutes = max(3, min(60, int(control_value("discovery", "taskTimeoutMinutes", 25))))
    return minutes * 60


def enabled_discovery_sources(country: str = "") -> set[str]:
    discovery = admin_control_settings().get("discovery", {})
    sources = discovery.get("globalSources") or []
    overrides = discovery.get("countrySourceOverrides") or {}
    country_text = clean_text(country)
    if country_text and isinstance(overrides, dict):
        for configured_country, configured_sources in overrides.items():
            if assigned_country_matches([configured_country], country_text):
                sources = configured_sources
                break
    return {str(source) for source in sources}


def discovery_source_cap(source: str) -> int:
    caps = admin_control_settings().get("discovery", {}).get("sourceCaps") or {}
    return max(1, min(100, int(caps.get(source) or 30)))


def session_max_age() -> int:
    hours = max(1, min(24 * 30, int(control_value("security", "sessionHours", 168))))
    return hours * 60 * 60


def password_min_length() -> int:
    return max(6, min(32, int(control_value("security", "passwordMinLength", 6))))


def masked_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "••••"
    return f"{value[:4]}••••{value[-4:]}"


def public_base_url() -> str:
    return runtime_setting("PUBLIC_BASE_URL", PUBLIC_BASE_URL).rstrip("/")


def get_youtube_api_key() -> str:
    return runtime_setting("YOUTUBE_API_KEY")


def get_brave_search_api_key() -> str:
    return runtime_setting("BRAVE_SEARCH_API_KEY")


def get_serpapi_api_key() -> str:
    return runtime_setting("SERPAPI_API_KEY")


def get_hunter_api_key() -> str:
    return runtime_setting("HUNTER_API_KEY")


def get_apify_api_token() -> str:
    return runtime_setting("APIFY_API_TOKEN")


def get_ai_provider() -> str:
    return runtime_setting("AI_PROVIDER", "").lower()


def get_deepseek_api_key() -> str:
    return runtime_setting("DEEPSEEK_API_KEY")


def get_deepseek_base_url() -> str:
    return runtime_setting("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")


def get_ai_model(kind: str = "default") -> str:
    defaults = {
        "fast": "deepseek-v4-flash",
        "default": "deepseek-v4-flash",
        "strong": "deepseek-v4-pro",
    }
    key = {
        "fast": "AI_MODEL_FAST",
        "strong": "AI_MODEL_STRONG",
    }.get(kind, "AI_MODEL_DEFAULT")
    return runtime_setting(key, defaults.get(kind, defaults["default"]))


def ai_lead_review_enabled() -> bool:
    provider = get_ai_provider()
    return bool(control_value("ai", "enabled", True)) and provider in {"deepseek", ""} and bool(get_deepseek_api_key())


def extract_json_object(value: str) -> dict:
    text = str(value or "").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def deepseek_chat_json(messages: list[dict], model: str = "") -> dict:
    api_key = get_deepseek_api_key()
    if not api_key:
        return {}
    ai_policy = admin_control_settings().get("ai", {})
    today = admin_usage_summary().get("deepseek", {})
    call_limit = int(ai_policy.get("dailyCallLimit") or 0)
    cost_limit = float(ai_policy.get("dailyCostLimitUsd") or 0)
    if call_limit and int(today.get("calls") or 0) >= call_limit:
        raise RuntimeError("DeepSeek 今日调用已达到系统设置上限")
    if cost_limit and float(today.get("estimatedCostUsd") or 0) >= cost_limit:
        raise RuntimeError("DeepSeek 今日估算费用已达到系统设置上限")
    payload = {
        "model": model or get_ai_model("default"),
        "messages": messages,
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    try:
        data = post_json_value(
            f"{get_deepseek_base_url()}/chat/completions",
            payload,
            timeout=30,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        record_api_usage("deepseek", True, estimated_cost_usd=0.001, detail=payload["model"])
    except Exception:
        record_api_usage("deepseek", False, detail=payload["model"])
        raise
    content = (
        ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "")
        if isinstance(data, dict) else ""
    )
    return extract_json_object(content)


def ai_review_lead_candidate(
    *,
    company: str,
    country: str,
    city: str,
    source_url: str,
    customer_website: str,
    origin: str,
    source_type: str,
    text: str,
) -> dict:
    if not ai_lead_review_enabled():
        return {}
    review_text = clean_text(text)[:5000]
    if not review_text:
        return {}
    system = """
You are the final quality gate for a B2B Chinese vehicle export lead system.
Your job is not to decide whether the page merely mentions cars. Your job is to decide whether the
identified entity is a real, contactable automotive business or automotive decision-maker that could
reasonably buy, import, distribute, retail, rent, operate a fleet of, or procure vehicles.

Evidence policy:
1. Use only the supplied company name, URLs, source metadata, page/profile text, and quoted evidence.
2. Never invent a country, company identity, showroom, website, contact method, business activity,
   Chinese-vehicle interest, or purchasing intent.
3. Search keywords, hashtags, usernames, a car visible in a video, and generic words such as car,
   auto, motors, EV, luxury, import, or dealer are not sufficient evidence by themselves.
4. Treat evidence copied from a search query or generic scraper fallback text as no evidence.
5. A social account must show a business identity or a named automotive decision-maker. Followers,
   views, likes, entertainment content, and personal ownership of a car do not create a sales lead.
6. Return short evidence snippets from the supplied input for every positive conclusion. If no snippet
   supports a conclusion, that conclusion must be false or unknown.

Eligible entities:
- Vehicle dealer, dealership group, showroom, automotive retailer, importer, distributor, auto-trading
  company, vehicle wholesaler, fleet operator, car-rental company, chauffeur/limousine fleet, corporate
  procurement team, government fleet buyer, or a clearly identified owner/director/procurement/sales
  manager of one of these businesses.
- Used-car dealers and multi-brand dealers remain eligible even if Chinese EVs are not mentioned.
- General trading or logistics companies are eligible only when vehicle trading, vehicle procurement,
  or automotive distribution is explicitly evidenced.

Ineligible entities:
- Personal lifestyle accounts, entertainment videos, memes, fan pages, gamers, musicians, athletes,
  travel creators, generic influencers, car enthusiasts, vehicle owners, collectors, and personal ads.
- Automotive news, review, POV, test-drive, racing/motorsport, compilation, media, and content-creator
  channels unless the same supplied evidence explicitly proves they also sell/import/distribute vehicles.
- Food, restaurants, tourism-only services, recruitment, education, unrelated retail, and non-automotive
  businesses.
- A single vehicle listing or marketplace seller with no identifiable automotive business identity.

Country policy:
- target_country_match=true requires explicit target-country evidence such as address, city, phone code,
  company registration, official profile location, or clearly local business description.
- A hashtag, audience location, event location, language, or inferred nationality alone is weak evidence.
- If supplied evidence explicitly places the entity in another country, mark country_evidence="conflict"
  and decision="reject".
- If country evidence is absent but the automotive business is otherwise real, use decision="manual_review";
  do not invent a match.

Chinese vehicle policy:
- Absence of Chinese EV, Huawei, AITO, HIMA, or HarmonyOS references is never a rejection reason.
- chinese_nev_evidence and huawei_series_evidence may be true only when explicitly supported by supplied text.

Customer profile policy:
- Build the customer profile only from supplied public evidence. Never invent purchasing volume, budget, brands,
  decision authority, or import capability.
- Use empty strings or "待核实" when evidence is insufficient.
- likely_needs and risk_notes must be short, practical Chinese phrases.

Decision policy:
- keep: real eligible automotive business/decision-maker with usable evidence and no country conflict.
- manual_review: automotive commercial identity is plausible, but entity or target-country evidence is incomplete.
- reject: non-automotive, personal/content/media-only, wrong country, fake/unusable identity, or no automotive
  commercial role.
- confidence means certainty of this classification, not lead quality. A clearly personal entertainment account
  should normally have high confidence and decision="reject".

Return one valid JSON object only. Do not add markdown or commentary.
""".strip()
    user = {
        "task": "Audit whether this candidate is eligible to enter a B2B vehicle-export sales review queue.",
        "targetCountry": country,
        "targetCityHint": city,
        "company": company,
        "origin": origin,
        "sourceType": source_type,
        "sourceUrl": source_url,
        "customerWebsite": customer_website,
        "text": review_text,
        "requiredJson": {
            "automotive": "boolean",
            "automotive_business": "boolean; true only for an automotive commercial operator or automotive decision-maker",
            "sales_lead_eligible": "boolean; true only when the entity could reasonably buy/import/distribute/retail/rent/procure vehicles",
            "entity_type": "one of company, decision_maker, personal, media, content_creator, marketplace_listing, unknown",
            "decision": "one of keep, manual_review, reject",
            "rejection_code": "one of empty, non_automotive, personal_account, media_or_content, no_commercial_role, wrong_country, unusable_identity, insufficient_evidence",
            "target_country_match": "boolean",
            "country_evidence": "one of explicit, inferred, none, conflict",
            "chinese_nev_evidence": "boolean, true only if supplied text explicitly mentions Chinese EV/NEV or Chinese vehicle brands",
            "huawei_series_evidence": "boolean, true only if supplied text explicitly mentions Huawei/AITO/HIMA/HarmonyOS/问界/智界/享界/尊界/鸿蒙智行",
            "reject": "boolean",
            "confidence": "integer 0-100 measuring classification certainty, not lead quality",
            "business_type": "short string",
            "reason": "short Chinese reason",
            "automotive_evidence": ["short supplied snippets proving automotive activity"],
            "commercial_evidence": ["short supplied snippets proving a business or decision-maker identity"],
            "country_evidence_snippets": ["short supplied snippets proving target-country location"],
            "verified_country": "country explicitly supported by supplied evidence, or empty string",
            "verified_city": "city explicitly supported by supplied evidence, or empty string",
            "customer_profile": {
                "buyer_type": "short Chinese customer type",
                "business_positioning": "short Chinese market and business positioning",
                "likely_needs": ["up to four evidence-based likely needs in Chinese"],
                "purchase_capacity": "one of 高, 中, 低, 待核实",
                "contact_strategy": "short practical Chinese contact strategy",
                "risk_notes": ["up to three evidence gaps or risks in Chinese"],
                "summary": "one concise Chinese customer portrait summary",
            },
            "evidence": ["up to five most important short supplied evidence snippets"],
        },
    }
    try:
        result = deepseek_chat_json(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
            ],
            model=get_ai_model("fast"),
        )
    except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
        return {}
    if not isinstance(result, dict):
        return {}
    def strict_bool(key: str, default: bool = False) -> bool:
        value = result.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "yes", "1"}
        if isinstance(value, (int, float)):
            return value == 1
        return default

    decision = clean_text(str(result.get("decision") or "")).lower()
    if decision not in {"keep", "manual_review", "reject"}:
        decision = "reject" if strict_bool("reject") else "manual_review"
    automotive = strict_bool("automotive")
    automotive_business = strict_bool("automotive_business", automotive)
    sales_lead_eligible = strict_bool(
        "sales_lead_eligible",
        automotive_business and decision != "reject",
    )
    country_evidence = clean_text(str(result.get("country_evidence") or "none")).lower()
    if country_evidence not in {"explicit", "inferred", "none", "conflict"}:
        country_evidence = "none"
    rejection_code = clean_text(str(result.get("rejection_code") or ""))[:60]
    entity_type = clean_text(str(result.get("entity_type") or "unknown"))[:60]
    raw_profile = result.get("customer_profile") if isinstance(result.get("customer_profile"), dict) else {}
    purchase_capacity = clean_text(str(raw_profile.get("purchase_capacity") or "待核实"))
    if purchase_capacity not in {"高", "中", "低", "待核实"}:
        purchase_capacity = "待核实"
    return {
        "provider": "deepseek",
        "model": get_ai_model("fast"),
        "automotive": automotive,
        "automotiveBusiness": automotive_business,
        "salesLeadEligible": sales_lead_eligible,
        "entityType": entity_type,
        "decision": decision,
        "rejectionCode": rejection_code,
        "targetCountryMatch": strict_bool("target_country_match"),
        "countryEvidence": country_evidence,
        "verifiedCountry": clean_text(str(result.get("verified_country") or ""))[:80],
        "verifiedCity": clean_text(str(result.get("verified_city") or ""))[:80],
        "chineseNevEvidence": strict_bool("chinese_nev_evidence"),
        "huaweiSeriesEvidence": strict_bool("huawei_series_evidence"),
        "reject": decision == "reject" or strict_bool("reject"),
        "confidence": max(0, min(100, int(result.get("confidence") or 0))),
        "businessType": clean_text(str(result.get("business_type") or ""))[:80],
        "reason": clean_text(str(result.get("reason") or ""))[:240],
        "automotiveEvidence": [
            clean_text(str(item))[:180]
            for item in (result.get("automotive_evidence") or [])
            if clean_text(str(item))
        ][:5],
        "commercialEvidence": [
            clean_text(str(item))[:180]
            for item in (result.get("commercial_evidence") or [])
            if clean_text(str(item))
        ][:5],
        "countryEvidenceSnippets": [
            clean_text(str(item))[:180]
            for item in (result.get("country_evidence_snippets") or [])
            if clean_text(str(item))
        ][:5],
        "customerProfile": {
            "buyerType": clean_text(str(raw_profile.get("buyer_type") or ""))[:80],
            "businessPositioning": clean_text(str(raw_profile.get("business_positioning") or ""))[:160],
            "likelyNeeds": [
                clean_text(str(item))[:120]
                for item in (raw_profile.get("likely_needs") or [])
                if clean_text(str(item))
            ][:4],
            "purchaseCapacity": purchase_capacity,
            "contactStrategy": clean_text(str(raw_profile.get("contact_strategy") or ""))[:180],
            "riskNotes": [
                clean_text(str(item))[:120]
                for item in (raw_profile.get("risk_notes") or [])
                if clean_text(str(item))
            ][:3],
            "summary": clean_text(str(raw_profile.get("summary") or ""))[:240],
        },
        "evidence": [
            clean_text(str(item))[:180]
            for item in (result.get("evidence") or [])
            if clean_text(str(item))
        ][:5],
    }


def apply_ai_confidence_threshold(ai_review: dict, minimum_confidence: int) -> dict:
    if not ai_review or ai_review.get("decision") == "reject":
        return ai_review
    confidence = max(0, min(100, int(ai_review.get("confidence") or 0)))
    threshold = max(0, min(100, int(minimum_confidence or 0)))
    if confidence >= threshold:
        return ai_review
    original_reason = clean_text(str(ai_review.get("reason") or ""))
    if not original_reason:
        original_reason = "现有公开证据不足以形成高置信度判断"
    ai_review["decision"] = "manual_review"
    ai_review["belowConfidenceThreshold"] = True
    ai_review["confidenceThreshold"] = threshold
    ai_review["reason"] = (
        f"{original_reason}（本条 AI 判断置信度 {confidence}%，低于系统阈值 {threshold}%，转人工核验。）"
    )[:500]
    return ai_review


def ai_generate_search_queries(
    *,
    country: str,
    cities: list[str],
    target_type: str,
    model: str,
    goal: str,
    limit: int = 12,
) -> list[str]:
    if not ai_lead_review_enabled():
        return []
    meta = country_search_meta(country)
    prompt = {
        "task": "Generate real web search queries for finding B2B automotive sales leads. Do not invent company names.",
        "targetCountry": country,
        "countryAliases": list(target_country_aliases(country)),
            "cities": cities[:12],
        "targetType": target_type,
        "vehicleModel": model,
        "goal": goal,
        "rules": [
            "Every query must include the target country or one of the target cities.",
            "Prefer car dealer, showroom, importer, distributor, fleet, auto trading, and official website/contact terms.",
            "Include local language or regional platform terms when useful.",
            "Avoid broad global queries that can return other countries.",
            "Return JSON only.",
        ],
        "requiredJson": {"queries": ["string"]},
        "maxQueries": limit,
        "searchCountryCode": meta.get("code", ""),
    }
    try:
        result = deepseek_chat_json(
            [
                {"role": "system", "content": "You generate precise search engine queries for real-time lead discovery. Return JSON only."},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            model=get_ai_model("fast"),
        )
    except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
        return []
    queries = []
    for item in result.get("queries") or []:
        query = clean_text(str(item))[:220]
        if not query:
            continue
        if not has_target_country_signal(f"{query} {country}", country):
            query = f"{query} {meta.get('location') or country}"
        queries.append(query)
        if len(queries) >= limit:
            break
    return list(dict.fromkeys(queries))


def admin_settings_payload() -> dict:
    settings = load_admin_settings_file()
    values = {}
    catalog = []
    for key, definition in ADMIN_SETTING_DEFINITIONS.items():
        effective = runtime_setting(key)
        stored = str(settings.get(key, "") or "").strip()
        if definition["type"] == "secret":
            values[key] = {
                "configured": bool(effective),
                "stored": bool(stored),
                "masked": masked_secret(effective),
            }
        else:
            values[key] = stored or os.environ.get(key, "")
        catalog.append({
            "key": key,
            "label": definition["label"],
            "type": definition["type"],
            "group": definition.get("group", "api"),
            "status": definition.get("status", "reserved"),
            "use": definition.get("use", ""),
            "configured": bool(effective),
            "masked": masked_secret(effective) if definition["type"] == "secret" else "",
            "value": "" if definition["type"] == "secret" else values[key],
            "min": definition.get("min"),
            "max": definition.get("max"),
        })
    custom_apis = []
    for item in settings.get(ADMIN_CUSTOM_APIS_KEY, []):
        if not isinstance(item, dict):
            continue
        value = str(item.get("value", "") or "")
        custom_apis.append({
            "id": item.get("id") or secrets.token_hex(6),
            "name": item.get("name", ""),
            "envKey": item.get("envKey", ""),
            "type": item.get("type", "secret"),
            "baseUrl": item.get("baseUrl", ""),
            "notes": item.get("notes", ""),
            "enabled": bool(item.get("enabled", True)),
            "configured": bool(value),
            "masked": masked_secret(value) if item.get("type", "secret") == "secret" else "",
            "value": "" if item.get("type", "secret") == "secret" else value,
        })
    return {
        "values": values,
        "catalog": catalog,
        "customApis": custom_apis,
        "controlCenter": admin_control_settings(),
        "dynamicRuntime": ["DISCOVERY_MAX_CONCURRENCY"],
        "restartRequired": ["NETWORK_DEFAULT_TIMEOUT", "APIFY_RUN_TIMEOUT_SECONDS"],
    }


def apify_usage_payload() -> dict:
    token = get_apify_api_token()
    if not token:
        raise ValueError("Apify API Token 未配置")
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "OverseasLeadWorkbench/1.0",
    }
    account_response = fetch_json("https://api.apify.com/v2/users/me", timeout=20, headers=headers)
    usage_response = fetch_json("https://api.apify.com/v2/users/me/usage/monthly", timeout=20, headers=headers)
    limits_response = fetch_json("https://api.apify.com/v2/users/me/limits", timeout=20, headers=headers)
    account = account_response.get("data") if isinstance(account_response.get("data"), dict) else {}
    usage = usage_response.get("data") if isinstance(usage_response.get("data"), dict) else {}
    limit_data = limits_response.get("data") if isinstance(limits_response.get("data"), dict) else {}
    plan = account.get("plan") if isinstance(account.get("plan"), dict) else {}
    limits = limit_data.get("limits") if isinstance(limit_data.get("limits"), dict) else {}
    current = limit_data.get("current") if isinstance(limit_data.get("current"), dict) else {}
    cycle = usage.get("usageCycle") if isinstance(usage.get("usageCycle"), dict) else {}
    account_id = str(account.get("id") or account.get("username") or "")
    used_usd = round(float(usage.get("totalUsageCreditsUsdAfterVolumeDiscount") or current.get("monthlyUsageUsd") or 0), 6)
    included_usd = round(float(plan.get("monthlyUsageCreditsUsd") or 0), 6)
    max_usage_usd = round(float(limits.get("maxMonthlyUsageUsd") or 0), 6)
    remaining_credits_usd = round(max(0.0, included_usd - used_usd), 6)
    remaining_limit_usd = round(max(0.0, max_usage_usd - used_usd), 6) if max_usage_usd else 0.0
    checked_at = datetime.now(timezone.utc).isoformat()
    cycle_start = str(cycle.get("startAt") or (limit_data.get("monthlyUsageCycle") or {}).get("startAt") or "")
    cycle_end = str(cycle.get("endAt") or (limit_data.get("monthlyUsageCycle") or {}).get("endAt") or "")
    with ADMIN_SETTINGS_LOCK:
        settings = load_admin_settings_file()
        previous = settings.get(APIFY_USAGE_SNAPSHOT_KEY)
        previous = previous if isinstance(previous, dict) else {}
        same_account = bool(account_id and previous.get("accountId") == account_id)
        same_cycle = bool(same_account and cycle_start and previous.get("cycleStartAt") == cycle_start)
        has_previous_snapshot = same_cycle and bool(previous.get("checkedAt"))
        previous_used = float(previous.get("usedUsd") or 0) if has_previous_snapshot else used_usd
        delta_usd = round(max(0.0, used_usd - previous_used), 6)
        history = previous.get("history") if same_cycle and isinstance(previous.get("history"), list) else []
        if not history or float(history[-1].get("usedUsd") or -1) != used_usd:
            history = [*history, {
                "checkedAt": checked_at,
                "usedUsd": used_usd,
                "deltaUsd": delta_usd,
                "remainingCreditsUsd": remaining_credits_usd,
            }][-20:]
        settings[APIFY_USAGE_SNAPSHOT_KEY] = {
            "accountId": account_id,
            "username": str(account.get("username") or ""),
            "cycleStartAt": cycle_start,
            "cycleEndAt": cycle_end,
            "checkedAt": checked_at,
            "usedUsd": used_usd,
            "history": history,
        }
        save_admin_settings_file(settings)
    return {
        "configured": True,
        "username": str(account.get("username") or ""),
        "plan": str(plan.get("description") or plan.get("id") or "未知套餐"),
        "includedCreditsUsd": included_usd,
        "usedUsd": used_usd,
        "deltaSinceLastCheckUsd": delta_usd,
        "remainingCreditsUsd": remaining_credits_usd,
        "maxMonthlyUsageUsd": max_usage_usd,
        "remainingLimitUsd": remaining_limit_usd,
        "cycleStartAt": cycle_start,
        "cycleEndAt": cycle_end,
        "checkedAt": checked_at,
        "history": history,
        "tokenExpiryAvailable": False,
    }


def combined_usage_entry(usage: dict, *source_names: str) -> dict:
    selected = [
        item
        for source, item in usage.items()
        if any(source == name or source.startswith(f"{name}:") for name in source_names)
    ]
    return {
        "calls": sum(int(item.get("calls") or 0) for item in selected),
        "units": sum(int(item.get("units") or 0) for item in selected),
        "failures": sum(int(item.get("failures") or 0) for item in selected),
        "estimatedCostUsd": round(sum(float(item.get("estimatedCostUsd") or 0) for item in selected), 6),
        "lastCallAt": max((str(item.get("lastCallAt") or "") for item in selected), default=""),
    }


def deepseek_official_usage() -> dict:
    api_key = get_deepseek_api_key()
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置")
    payload = fetch_json(
        "https://api.deepseek.com/user/balance",
        timeout=20,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    balances = []
    for item in payload.get("balance_infos") or []:
        if not isinstance(item, dict):
            continue
        balances.append({
            "currency": str(item.get("currency") or ""),
            "total": str(item.get("total_balance") or "0"),
            "granted": str(item.get("granted_balance") or "0"),
            "toppedUp": str(item.get("topped_up_balance") or "0"),
        })
    return {"available": bool(payload.get("is_available")), "balances": balances}


def pacific_utc_offset_hours(moment: datetime) -> int:
    year = moment.year
    march_first = datetime(year, 3, 1, tzinfo=timezone.utc)
    first_sunday_march = 1 + ((6 - march_first.weekday()) % 7)
    second_sunday_march = first_sunday_march + 7
    dst_start = datetime(year, 3, second_sunday_march, 10, tzinfo=timezone.utc)
    november_first = datetime(year, 11, 1, tzinfo=timezone.utc)
    first_sunday_november = 1 + ((6 - november_first.weekday()) % 7)
    dst_end = datetime(year, 11, first_sunday_november, 9, tzinfo=timezone.utc)
    return -7 if dst_start <= moment < dst_end else -8


def next_pacific_midnight_utc(moment: datetime) -> datetime:
    current_offset = pacific_utc_offset_hours(moment)
    pacific_now = moment.astimezone(timezone(timedelta(hours=current_offset)))
    next_date = pacific_now.date() + timedelta(days=1)
    utc_guess = datetime(next_date.year, next_date.month, next_date.day, 8, tzinfo=timezone.utc)
    reset_offset = pacific_utc_offset_hours(utc_guess)
    return datetime(
        next_date.year,
        next_date.month,
        next_date.day,
        tzinfo=timezone(timedelta(hours=reset_offset)),
    ).astimezone(timezone.utc)


def api_consumption_payload() -> dict:
    usage = admin_usage_summary()
    catalog = {item["key"]: item for item in admin_settings_payload().get("catalog", [])}
    official_fetchers = {
        "deepseek": (bool(get_deepseek_api_key()), deepseek_official_usage),
    }
    official: dict[str, dict] = {}

    def fetch_provider(provider: str, fetcher) -> tuple[str, dict]:
        try:
            return provider, {"ok": True, "data": fetcher()}
        except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError) as exc:
            return provider, {"ok": False, "error": clean_text(str(exc))[:240]}

    enabled_fetchers = [(key, fetcher) for key, (configured, fetcher) in official_fetchers.items() if configured]
    if enabled_fetchers:
        with ThreadPoolExecutor(max_workers=len(enabled_fetchers)) as executor:
            futures = [executor.submit(fetch_provider, key, fetcher) for key, fetcher in enabled_fetchers]
            for future in as_completed(futures):
                key, value = future.result()
                official[key] = value
    for key, (configured, _) in official_fetchers.items():
        if not configured:
            official[key] = {"ok": False, "error": "API Key 未配置"}

    now = datetime.now(timezone.utc)
    youtube_reset = next_pacific_midnight_utc(now)
    providers = [
        {
            "key": "youtube",
            "label": "YouTube Data API",
            "configured": bool(catalog.get("YOUTUBE_API_KEY", {}).get("configured")),
            "tracked": combined_usage_entry(usage, "youtube"),
            "officialMode": "cloud-console",
            "officialNote": "API Key 无权读取项目总配额；官方总量需通过 Google Cloud Quotas/Monitoring 查看。",
            "limit": 100,
            "limitLabel": "search.list 官方日上限",
            "resetAt": youtube_reset.isoformat(),
        },
        {
            "key": "deepseek",
            "label": "DeepSeek",
            "configured": bool(catalog.get("DEEPSEEK_API_KEY", {}).get("configured")),
            "tracked": combined_usage_entry(usage, "deepseek"),
            "officialMode": "balance-api",
            "official": official.get("deepseek", {}),
        },
    ]
    return {"checkedAt": now.isoformat(), "providers": providers}


def normalize_custom_apis(payload_items: list, previous_items: list) -> list[dict]:
    previous_by_id = {
        str(item.get("id")): item for item in previous_items
        if isinstance(item, dict) and item.get("id")
    }
    normalized = []
    for raw in payload_items[:50]:
        if not isinstance(raw, dict):
            continue
        name = clean_text(str(raw.get("name", "")))[:80]
        env_key = str(raw.get("envKey", "")).strip().upper()
        if not name and not env_key:
            continue
        if not name:
            raise ValueError("自定义 API 必须填写名称")
        if not re.match(r"^[A-Z][A-Z0-9_]{2,63}$", env_key):
            raise ValueError(f"{name} 的配置 Key 只能使用大写字母、数字和下划线")
        item_id = str(raw.get("id") or secrets.token_hex(6))
        value_type = "text" if raw.get("type") == "text" else "secret"
        value = str(raw.get("value", "") or "").strip()
        if value == "" and item_id in previous_by_id:
            value = str(previous_by_id[item_id].get("value", "") or "")
        base_url = str(raw.get("baseUrl", "") or "").strip().rstrip("/")
        if base_url and not re.match(r"^https?://", base_url, flags=re.I):
            raise ValueError(f"{name} 的接口地址必须以 http:// 或 https:// 开头")
        normalized.append({
            "id": item_id,
            "name": name,
            "envKey": env_key,
            "type": value_type,
            "value": value,
            "baseUrl": base_url,
            "notes": clean_text(str(raw.get("notes", "")))[:240],
            "enabled": bool(raw.get("enabled", True)),
        })
    seen = set()
    unique = []
    for item in normalized:
        if item["envKey"] in seen:
            raise ValueError(f"自定义 API 配置 Key 重复：{item['envKey']}")
        seen.add(item["envKey"])
        unique.append(item)
    return unique


def normalize_admin_control(payload: dict | None, previous: dict | None = None) -> dict:
    previous_version = int(previous.get("schemaVersion") or 1) if isinstance(previous, dict) else 1
    control = merge_nested_settings(ADMIN_CONTROL_DEFAULTS, previous)
    incoming = payload if isinstance(payload, dict) else {}
    for section in ("discovery", "quality", "ai", "data", "security"):
        if isinstance(incoming.get(section), dict):
            control[section].update(incoming[section])

    discovery = control["discovery"]
    discovery["adminOnly"] = bool(discovery.get("adminOnly", False))
    discovery["targetMin"] = max(1, min(100, int(discovery.get("targetMin") or 20)))
    discovery["targetMax"] = max(discovery["targetMin"], min(120, int(discovery.get("targetMax") or 30)))
    discovery["taskTimeoutMinutes"] = max(3, min(60, int(discovery.get("taskTimeoutMinutes") or 25)))
    discovery["fallbackEnabled"] = bool(discovery.get("fallbackEnabled", True))
    allowed_sources = {"google", "osm", "dealer", "instagram", "facebook", "tiktok", "youtube", "linkedin"}
    discovery["globalSources"] = [item for item in discovery.get("globalSources", []) if item in allowed_sources]
    if previous_version < 2 and "linkedin" not in discovery["globalSources"]:
        discovery["globalSources"].append("linkedin")
    control["schemaVersion"] = 2
    caps = discovery.get("sourceCaps") if isinstance(discovery.get("sourceCaps"), dict) else {}
    discovery["sourceCaps"] = {
        source: max(1, min(100, int(caps.get(source) or ADMIN_CONTROL_DEFAULTS["discovery"]["sourceCaps"][source])))
        for source in allowed_sources
    }
    weights = discovery.get("sourceWeights") if isinstance(discovery.get("sourceWeights"), dict) else {}
    discovery["sourceWeights"] = {
        source: max(1, min(10, int(weights.get(source) if weights.get(source) is not None else ADMIN_CONTROL_DEFAULTS["discovery"]["sourceWeights"][source])))
        for source in allowed_sources
    }
    overrides = discovery.get("countrySourceOverrides") if isinstance(discovery.get("countrySourceOverrides"), dict) else {}
    discovery["countrySourceOverrides"] = {
        clean_text(str(country))[:80]: [source for source in sources if source in allowed_sources]
        for country, sources in overrides.items()
        if clean_text(str(country)) and isinstance(sources, list)
    }

    quality = control["quality"]
    previous_quality = previous.get("quality") if isinstance(previous, dict) and isinstance(previous.get("quality"), dict) else {}
    previous_score_model = int(previous_quality.get("scoreModelVersion") or 0)
    if previous_score_model < ADMIN_CONTROL_DEFAULTS["quality"]["scoreModelVersion"]:
        quality["scoreWeights"] = dict(ADMIN_CONTROL_DEFAULTS["quality"]["scoreWeights"])
        quality["minimumAutoImportScore"] = ADMIN_CONTROL_DEFAULTS["quality"]["minimumAutoImportScore"]
    quality["scoreModelVersion"] = ADMIN_CONTROL_DEFAULTS["quality"]["scoreModelVersion"]
    for key in ("strictCountryMatch", "requireAutomotiveBusiness", "rejectPersonalAccounts", "requireContactOrWebsite", "blockRejectedMemory"):
        quality[key] = bool(quality.get(key))
    quality["minimumAutoImportScore"] = max(0, min(100, int(quality.get("minimumAutoImportScore") or 0)))
    quality["minimumAiConfidence"] = max(0, min(100, int(quality.get("minimumAiConfidence") or 0)))
    default_weights = ADMIN_CONTROL_DEFAULTS["quality"]["scoreWeights"]
    weights = quality.get("scoreWeights") if isinstance(quality.get("scoreWeights"), dict) else {}
    quality["scoreWeights"] = {key: max(0, min(30, int(weights.get(key, value)))) for key, value in default_weights.items()}

    ai = control["ai"]
    ai["enabled"] = bool(ai.get("enabled", True))
    ai["failurePolicy"] = ai.get("failurePolicy") if ai.get("failurePolicy") in {"manual_review", "skip", "allow"} else "manual_review"
    ai["dailyCallLimit"] = max(0, min(100000, int(ai.get("dailyCallLimit") or 0)))
    ai["dailyCostLimitUsd"] = max(0.0, min(10000.0, float(ai.get("dailyCostLimitUsd") or 0)))
    ai["promptVersion"] = clean_text(str(ai.get("promptVersion") or "vehicle-export-v2"))[:80]

    data = control["data"]
    data["jobRetentionDays"] = max(1, min(365, int(data.get("jobRetentionDays") or 30)))
    data["searchRecordRetentionDays"] = max(7, min(1095, int(data.get("searchRecordRetentionDays") or 90)))
    data["backupReminderDays"] = max(1, min(90, int(data.get("backupReminderDays") or 7)))
    data["lastBackupAt"] = str(data.get("lastBackupAt") or "")[:40]

    security = control["security"]
    security["sessionHours"] = max(1, min(24 * 30, int(security.get("sessionHours") or 168)))
    security["passwordMinLength"] = max(6, min(32, int(security.get("passwordMinLength") or 6)))
    security["sessionInvalidBefore"] = max(0, int(security.get("sessionInvalidBefore") or 0))
    return control


def normalize_admin_settings(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("设置请求格式无效")
    current = load_admin_settings_file()
    next_settings = dict(current)
    for key, definition in ADMIN_SETTING_DEFINITIONS.items():
        if key not in payload:
            continue
        value = str(payload.get(key) or "").strip()
        if value == "":
            if definition["type"] == "secret":
                continue
            next_settings.pop(key, None)
            continue
        if definition["type"] == "int":
            number = int(value)
            min_value = int(definition.get("min", 0))
            max_value = int(definition.get("max", 9999))
            if number < min_value or number > max_value:
                raise ValueError(f"{definition['label']} 必须在 {min_value}-{max_value} 之间")
            value = str(number)
        if definition["type"] == "url":
            value = value.rstrip("/")
            if value and not re.match(r"^https?://", value, flags=re.I):
                raise ValueError(f"{definition['label']} 必须以 http:// 或 https:// 开头")
        next_settings[key] = value
    if "customApis" in payload:
        custom_apis = payload.get("customApis") or []
        if not isinstance(custom_apis, list):
            raise ValueError("自定义 API 格式无效")
        next_settings[ADMIN_CUSTOM_APIS_KEY] = normalize_custom_apis(
            custom_apis,
            current.get(ADMIN_CUSTOM_APIS_KEY, []),
        )
    if "controlCenter" in payload:
        next_settings[ADMIN_CONTROL_KEY] = normalize_admin_control(
            payload.get("controlCenter"),
            current.get(ADMIN_CONTROL_KEY),
        )
    return next_settings


def restart_server_process(delay_seconds: float = 0.8) -> None:
    restart_env = os.environ.copy()
    settings = load_admin_settings_file()
    for key, value in settings.items():
        if key == ADMIN_CUSTOM_APIS_KEY or value is None or isinstance(value, (dict, list)):
            continue
        restart_env[key] = str(value)
    for item in settings.get(ADMIN_CUSTOM_APIS_KEY, []):
        if isinstance(item, dict) and item.get("envKey") and item.get("value") is not None:
            restart_env[str(item["envKey"])] = str(item["value"])
    args = [sys.executable, *sys.argv]

    def restart() -> None:
        try:
            if os.name == "nt":
                env_file = ROOT / f"restart-env-{os.getpid()}.json"
                env_file.write_text(json.dumps(restart_env), encoding="utf-8")
                helper = (
                    "import json, os, pathlib, subprocess, time; "
                    f"env_file = pathlib.Path({str(env_file)!r}); "
                    f"time.sleep({float(delay_seconds)!r}); "
                    "env = json.loads(env_file.read_text(encoding='utf-8')); "
                    "env_file.unlink(missing_ok=True); "
                    f"subprocess.Popen({args!r}, cwd={str(ROOT)!r}, env=env)"
                )
                creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
                subprocess.Popen(
                    [sys.executable, "-c", helper],
                    cwd=str(ROOT),
                    close_fds=True,
                    creationflags=creationflags,
                )
                time.sleep(0.2)
                os._exit(0)
            time.sleep(delay_seconds)
            os.execve(sys.executable, args, restart_env)
        except Exception as exc:
            try:
                (ROOT / "restart-error.log").write_text(str(exc), encoding="utf-8")
            finally:
                os._exit(1)

    threading.Thread(target=restart, daemon=True).start()


class WorkspaceVersionConflict(Exception):
    def __init__(self, current: dict):
        super().__init__("云端数据已被其他设备更新")
        self.current = current


def postgres_connection():
    if not DATABASE_URL:
        return None
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("已配置 DATABASE_URL，但未安装 psycopg") from exc
    return psycopg.connect(DATABASE_URL)


def migrate_admin_settings_file_to_database() -> None:
    if not ADMIN_SETTINGS_FILE.exists():
        return
    try:
        settings = json.loads(ADMIN_SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(settings, dict):
        return
    encoded = json.dumps(settings, ensure_ascii=False)
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT settings_key FROM app_settings WHERE settings_key = %s", ("admin",))
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO app_settings (settings_key, settings, updated_at) VALUES (%s, %s::jsonb, NOW())",
                        ("admin", encoded),
                    )
        return
    with sqlite3.connect(SQLITE_STATE_FILE) as connection:
        exists = connection.execute(
            "SELECT settings_key FROM app_settings WHERE settings_key = ?",
            ("admin",),
        ).fetchone()
        if not exists:
            connection.execute(
                "INSERT INTO app_settings (settings_key, settings, updated_at) VALUES (?, ?, ?)",
                ("admin", encoded, datetime.now(timezone.utc).isoformat(timespec="seconds")),
            )


def _initialize_state_store_schema() -> None:
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS workspace_state (
                        workspace_key TEXT PRIMARY KEY,
                        state JSONB NOT NULL,
                        version BIGINT NOT NULL DEFAULT 1,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS app_users (
                        username TEXT PRIMARY KEY,
                        display_name TEXT NOT NULL DEFAULT '',
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'user',
                        status TEXT NOT NULL DEFAULT 'enabled',
                        assigned_countries JSONB NOT NULL DEFAULT '[]'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cursor.execute("ALTER TABLE app_users ADD COLUMN IF NOT EXISTS assigned_countries JSONB NOT NULL DEFAULT '[]'::jsonb")
                cursor.execute("ALTER TABLE app_users ADD COLUMN IF NOT EXISTS display_name TEXT NOT NULL DEFAULT ''")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS app_settings (
                        settings_key TEXT PRIMARY KEY,
                        settings JSONB NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS login_events (
                        event_id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        ip_address TEXT NOT NULL,
                        user_agent TEXT NOT NULL DEFAULT '',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_presence (
                        username TEXT PRIMARY KEY,
                        last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        ip_address TEXT NOT NULL DEFAULT '',
                        user_agent TEXT NOT NULL DEFAULT ''
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS api_usage_events (
                        event_id TEXT PRIMARY KEY,
                        source_name TEXT NOT NULL,
                        success BOOLEAN NOT NULL DEFAULT TRUE,
                        units INTEGER NOT NULL DEFAULT 1,
                        estimated_cost_usd NUMERIC NOT NULL DEFAULT 0,
                        detail TEXT NOT NULL DEFAULT '',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS admin_audit_events (
                        event_id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        action TEXT NOT NULL,
                        detail TEXT NOT NULL DEFAULT '',
                        ip_address TEXT NOT NULL DEFAULT '',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS discovery_jobs (
                        job_id TEXT PRIMARY KEY,
                        payload JSONB NOT NULL,
                        status TEXT NOT NULL,
                        stage TEXT NOT NULL,
                        progress INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        result JSONB,
                        error TEXT NOT NULL DEFAULT '',
                        imported BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMPTZ NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )
                cursor.execute("ALTER TABLE discovery_jobs ADD COLUMN IF NOT EXISTS owner_username TEXT NOT NULL DEFAULT 'admin'")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS discovery_schedules (
                        schedule_id TEXT PRIMARY KEY,
                        owner_username TEXT NOT NULL,
                        payload JSONB NOT NULL,
                        interval_minutes INTEGER NOT NULL,
                        enabled BOOLEAN NOT NULL DEFAULT TRUE,
                        next_run_at TIMESTAMPTZ NOT NULL,
                        last_run_at TIMESTAMPTZ,
                        last_job_id TEXT NOT NULL DEFAULT '',
                        created_at TIMESTAMPTZ NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )
        migrate_admin_settings_file_to_database()
        return
    SQLITE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(SQLITE_STATE_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workspace_state (
                workspace_key TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_users (
                username TEXT PRIMARY KEY,
                display_name TEXT NOT NULL DEFAULT '',
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                status TEXT NOT NULL DEFAULT 'enabled',
                assigned_countries TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL
            )
            """
        )
        try:
            connection.execute("ALTER TABLE app_users ADD COLUMN assigned_countries TEXT NOT NULL DEFAULT '[]'")
        except sqlite3.OperationalError as exc:
            if "duplicate column name" not in str(exc).lower():
                raise
        try:
            connection.execute("ALTER TABLE app_users ADD COLUMN display_name TEXT NOT NULL DEFAULT ''")
        except sqlite3.OperationalError as exc:
            if "duplicate column name" not in str(exc).lower():
                raise
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                settings_key TEXT PRIMARY KEY,
                settings TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS login_events (
                event_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_presence (
                username TEXT PRIMARY KEY,
                last_seen_at TEXT NOT NULL,
                ip_address TEXT NOT NULL DEFAULT '',
                user_agent TEXT NOT NULL DEFAULT ''
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS api_usage_events (
                event_id TEXT PRIMARY KEY,
                source_name TEXT NOT NULL,
                success INTEGER NOT NULL DEFAULT 1,
                units INTEGER NOT NULL DEFAULT 1,
                estimated_cost_usd REAL NOT NULL DEFAULT 0,
                detail TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_audit_events (
                event_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                detail TEXT NOT NULL DEFAULT '',
                ip_address TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS discovery_jobs (
                job_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                stage TEXT NOT NULL,
                progress INTEGER NOT NULL,
                message TEXT NOT NULL,
                result TEXT,
                error TEXT NOT NULL DEFAULT '',
                imported INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        columns = {row[1] for row in connection.execute("PRAGMA table_info(discovery_jobs)").fetchall()}
        if "owner_username" not in columns:
            connection.execute("ALTER TABLE discovery_jobs ADD COLUMN owner_username TEXT NOT NULL DEFAULT 'admin'")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS discovery_schedules (
                schedule_id TEXT PRIMARY KEY,
                owner_username TEXT NOT NULL,
                payload TEXT NOT NULL,
                interval_minutes INTEGER NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                next_run_at TEXT NOT NULL,
                last_run_at TEXT,
                last_job_id TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
    migrate_admin_settings_file_to_database()


def initialize_state_store() -> None:
    global STATE_STORE_INITIALIZED
    if STATE_STORE_INITIALIZED:
        return
    with STATE_STORE_INIT_LOCK:
        if STATE_STORE_INITIALIZED:
            return
        _initialize_state_store_schema()
        STATE_STORE_INITIALIZED = True


def empty_workspace_state() -> dict:
    return {
        "reviewLeads": [],
        "customers": [],
        "websiteLeads": [],
        "rejectedLeads": [],
        "quotes": [],
        "afterSalesOrders": [],
        "deletedRecords": [],
    }


def workspace_storage_key(username: str) -> str:
    return "admin-default" if username in {AUTH_USERNAME, HIDDEN_ADMIN_USERNAME} else f"user:{username}"


def normalize_workspace_state(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("工作台数据格式无效")
    normalized = {}
    for key in ("reviewLeads", "customers", "websiteLeads", "rejectedLeads", "quotes", "afterSalesOrders", "deletedRecords"):
        value = payload.get(key, [])
        if not isinstance(value, list):
            raise ValueError(f"{key} 必须是数组")
        normalized[key] = value[:5000]
    encoded = json.dumps(normalized, ensure_ascii=False)
    if len(encoded.encode("utf-8")) > 20_000_000:
        raise ValueError("工作台数据超过 20MB 限制")
    return normalized


def load_workspace_state(workspace_key: str) -> dict:
    storage_key = workspace_storage_key(workspace_key)
    with STATE_LOCK:
        initialize_state_store()
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT state, version, updated_at FROM workspace_state WHERE workspace_key = %s",
                        (storage_key,),
                    )
                    row = cursor.fetchone()
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                row = connection.execute(
                    "SELECT state, version, updated_at FROM workspace_state WHERE workspace_key = ?",
                    (storage_key,),
                ).fetchone()
        if not row:
            return {
                "exists": False,
                "state": empty_workspace_state(),
                "version": 0,
                "updatedAt": "",
                "storage": "postgres" if DATABASE_URL else "sqlite",
            }
        raw_state = row[0]
        state = raw_state if isinstance(raw_state, dict) else json.loads(raw_state)
        updated_at = row[2].isoformat() if hasattr(row[2], "isoformat") else str(row[2])
        return {
            "exists": True,
            "state": normalize_workspace_state(state),
            "version": int(row[1]),
            "updatedAt": updated_at,
            "storage": "postgres" if DATABASE_URL else "sqlite",
        }


def summarize_workspace_for_kpi(state: dict) -> dict:
    review_leads = state.get("reviewLeads", []) if isinstance(state, dict) else []
    customers = state.get("customers", []) if isinstance(state, dict) else []
    quotes = state.get("quotes", []) if isinstance(state, dict) else []
    after_sales_orders = state.get("afterSalesOrders", []) if isinstance(state, dict) else []
    verified = sum(1 for lead in [*review_leads, *customers] if isinstance(lead, dict) and lead.get("researchAt"))
    contacted = sum(
        1 for lead in customers
        if isinstance(lead, dict) and str(lead.get("stage", "")) not in {"准备联系", "暂停", "已流失"}
    )
    replied = sum(
        1 for lead in customers
        if isinstance(lead, dict) and str(lead.get("stage", "")) in {"有回复", "报价中", "谈判中", "已成交"}
    )
    completed = sum(1 for lead in customers if isinstance(lead, dict) and str(lead.get("stage", "")) == "已成交")
    return {
        "pending": len(review_leads),
        "verified": verified,
        "customers": len(customers),
        "contacted": contacted,
        "replied": replied,
        "quotes": len(quotes),
        "afterSales": len(after_sales_orders),
        "completed": completed,
    }


SALES_COUNTRY_KEYS = (
    "Saudi Arabia", "Côte d'Ivoire", "UAE", "Kazakhstan", "Russia", "Qatar",
    "Kuwait", "Uzbekistan", "Azerbaijan", "Nigeria", "Ghana", "Algeria",
    "Egypt", "Kyrgyzstan", "Ethiopia", "Oman", "Armenia", "Bahrain",
    "Jordan", "Georgia", "Vietnam", "Philippines", "Mexico", "Brazil",
    "Chile", "Colombia", "Morocco", "China",
)


def sales_country_key(value: object) -> str:
    text = str(value or "").strip()
    lower = text.lower()
    for country in SALES_COUNTRY_KEYS:
        if lower == country.lower() or lower.startswith(f"{country.lower()} ") or country.lower() in lower:
            return country
    return text.split()[0] if text else ""


def sales_record_date(record: dict) -> str:
    for key in (
        "updatedAt", "lastContactAt", "approvedAt", "researchAt", "importedAt",
        "discoveredAt", "createdAt",
    ):
        if record.get(key):
            return str(record[key])
    return ""


def sales_date_in_range(value: str, days: int | None) -> bool:
    if days is None:
        return True
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed >= datetime.now(timezone.utc) - timedelta(days=days)
    except (TypeError, ValueError):
        return False


def sales_source_name(record: dict) -> str:
    text = " ".join(str(record.get(key) or "") for key in (
        "origin", "platform", "sourceMode", "discoverySource", "sourceType", "source", "sourceUrl",
    )).lower()
    for token, label in (
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("tiktok", "TikTok"),
        ("youtube", "YouTube"),
        ("linkedin", "LinkedIn"),
        ("openstreetmap", "OpenStreetMap"),
        ("osm", "OpenStreetMap"),
        ("google", "Google Maps"),
        ("maps", "Google Maps"),
    ):
        if token in text:
            return label
    return "官网 / 目录"


def empty_sales_country_period() -> dict:
    return {
        "leads": 0,
        "pending": 0,
        "customers": 0,
        "contactable": 0,
        "quoted": 0,
        "completed": 0,
        "quoteAmount": 0.0,
        "overdue": 0,
        "missingContact": 0,
        "sources": {},
        "models": {},
        "owners": {},
        "latestActivity": "",
    }


def increment_sales_group(target: dict, key: object, amount: int = 1) -> None:
    label = str(key or "").strip()
    if label:
        target[label] = int(target.get(label, 0)) + int(amount)


def summarize_workspace_by_country(state: dict, username: str) -> dict:
    review_leads = state.get("reviewLeads", []) if isinstance(state, dict) else []
    customers = state.get("customers", []) if isinstance(state, dict) else []
    quotes = state.get("quotes", []) if isinstance(state, dict) else []
    result: dict[str, dict] = {}
    ranges = {"all": None, "30": 30, "7": 7}
    today = datetime.now(timezone.utc).date().isoformat()

    customer_country_by_id = {}
    customer_country_by_name = {}
    for lead in customers:
        if not isinstance(lead, dict):
            continue
        country = sales_country_key(lead.get("country"))
        if lead.get("id") and country:
            customer_country_by_id[str(lead["id"])] = country
        if lead.get("company") and country:
            customer_country_by_name[str(lead["company"]).strip().lower()] = country

    for range_key, days in ranges.items():
        for lead, pending in [
            *((item, True) for item in review_leads if isinstance(item, dict)),
            *((item, False) for item in customers if isinstance(item, dict)),
        ]:
            if not sales_date_in_range(sales_record_date(lead), days):
                continue
            country = sales_country_key(lead.get("country"))
            if not country:
                continue
            country_item = result.setdefault(country, {"country": country, "periods": {}})
            item = country_item["periods"].setdefault(range_key, empty_sales_country_period())
            item["leads"] += 1
            item["pending"] += 1 if pending else 0
            item["customers"] += 0 if pending else 1
            has_contact = bool(
                lead.get("email") or lead.get("phone") or lead.get("whatsapp")
                or lead.get("emailSources") or lead.get("phoneSources") or lead.get("whatsappSources")
            )
            item["contactable"] += 1 if has_contact else 0
            item["missingContact"] += 0 if has_contact else 1
            item["completed"] += 1 if str(lead.get("stage") or "") == "已成交" else 0
            item["overdue"] += 1 if (
                not pending
                and str(lead.get("stage") or "") not in {"已成交", "已流失"}
                and str(lead.get("nextFollowAt") or "")
                and str(lead.get("nextFollowAt")) < today
            ) else 0
            increment_sales_group(item["sources"], sales_source_name(lead))
            models = lead.get("recommendedModels")
            if not isinstance(models, list):
                models = [lead.get("model")]
            for model in models[:4]:
                increment_sales_group(item["models"], model)
            increment_sales_group(item["owners"], username)
            activity = sales_record_date(lead)
            if activity > item["latestActivity"]:
                item["latestActivity"] = activity

        for quote in quotes:
            if not isinstance(quote, dict) or not sales_date_in_range(sales_record_date(quote), days):
                continue
            country = (
                sales_country_key(quote.get("country"))
                or customer_country_by_id.get(str(quote.get("customerId") or ""))
                or customer_country_by_name.get(str(quote.get("customer") or "").strip().lower())
            )
            if not country:
                destination = str(quote.get("destination") or "").lower()
                country = next((key for key in SALES_COUNTRY_KEYS if key.lower() in destination), "")
            if not country:
                continue
            country_item = result.setdefault(country, {"country": country, "periods": {}})
            item = country_item["periods"].setdefault(range_key, empty_sales_country_period())
            item["quoted"] += 1
            try:
                item["quoteAmount"] += float(quote.get("total") or 0)
            except (TypeError, ValueError):
                pass
            increment_sales_group(item["models"], quote.get("model"))
            activity = sales_record_date(quote)
            if activity > item["latestActivity"]:
                item["latestActivity"] = activity
    return result


def merge_sales_country_aggregates(target: dict, source: dict) -> None:
    additive_keys = (
        "leads", "pending", "customers", "contactable", "quoted", "completed",
        "quoteAmount", "overdue", "missingContact",
    )
    for country, source_country in source.items():
        target_country = target.setdefault(country, {"country": country, "periods": {}})
        for range_key, source_period in source_country.get("periods", {}).items():
            target_period = target_country["periods"].setdefault(range_key, empty_sales_country_period())
            for key in additive_keys:
                target_period[key] += source_period.get(key, 0)
            for group_key in ("sources", "models", "owners"):
                for label, count in source_period.get(group_key, {}).items():
                    increment_sales_group(target_period[group_key], label, count)
            if source_period.get("latestActivity", "") > target_period["latestActivity"]:
                target_period["latestActivity"] = source_period["latestActivity"]


def load_admin_kpi_summary() -> dict:
    users = list_users()
    rows = []
    country_aggregates = {}
    totals = {
        "pending": 0,
        "verified": 0,
        "customers": 0,
        "contacted": 0,
        "replied": 0,
        "quotes": 0,
        "afterSales": 0,
        "completed": 0,
    }
    for user in users:
        username = user.get("username", "")
        workspace = load_workspace_state(username)
        metrics = summarize_workspace_for_kpi(workspace.get("state", {}))
        merge_sales_country_aggregates(
            country_aggregates,
            summarize_workspace_by_country(workspace.get("state", {}), username),
        )
        for key in totals:
            totals[key] += int(metrics.get(key, 0))
        rows.append({
            "username": username,
            "role": user.get("role", "user"),
            "status": user.get("status", "enabled"),
            "builtIn": bool(user.get("builtIn")),
            "createdAt": user.get("createdAt", ""),
            "updatedAt": workspace.get("updatedAt", ""),
            "exists": bool(workspace.get("exists")),
            **metrics,
        })
    rows.sort(key=lambda item: (item["customers"] + item["pending"] + item["quotes"]), reverse=True)
    return {"users": rows, "totals": totals, "countryAggregates": country_aggregates}


def save_workspace_state(workspace_key: str, payload: dict, expected_version: int | None = None) -> dict:
    storage_key = workspace_storage_key(workspace_key)
    state = normalize_workspace_state(payload)
    encoded = json.dumps(state, ensure_ascii=False)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with STATE_LOCK:
        initialize_state_store()
        current = load_workspace_state(workspace_key)
        current_version = int(current.get("version", 0))
        if expected_version is not None and int(expected_version) != current_version:
            raise WorkspaceVersionConflict(current)
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO workspace_state (workspace_key, state, version, updated_at)
                        VALUES (%s, %s::jsonb, 1, NOW())
                        ON CONFLICT (workspace_key) DO UPDATE SET
                            state = EXCLUDED.state,
                            version = workspace_state.version + 1,
                            updated_at = NOW()
                        RETURNING version, updated_at
                        """,
                        (storage_key, encoded),
                    )
                    version, updated_at = cursor.fetchone()
                    updated = updated_at.isoformat()
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                connection.execute(
                    """
                    INSERT INTO workspace_state (workspace_key, state, version, updated_at)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT(workspace_key) DO UPDATE SET
                        state = excluded.state,
                        version = workspace_state.version + 1,
                        updated_at = excluded.updated_at
                    """,
                    (storage_key, encoded, now),
                )
                version = connection.execute(
                    "SELECT version FROM workspace_state WHERE workspace_key = ?",
                    (storage_key,),
                ).fetchone()[0]
                updated = now
    return {
        "state": state,
        "version": int(version),
        "updatedAt": updated,
        "storage": "postgres" if DATABASE_URL else "sqlite",
    }


def workspace_operation_events(previous: dict, current: dict) -> list[tuple[str, str]]:
    previous = previous if isinstance(previous, dict) else empty_workspace_state()
    current = current if isinstance(current, dict) else empty_workspace_state()

    def record_key(record: dict, index: int) -> str:
        if not isinstance(record, dict):
            return f"row:{index}"
        return clean_text(str(
            record.get("id")
            or record.get("leadId")
            or record.get("customerWebsite")
            or record.get("sourceUrl")
            or f"{record.get('company', '')}|{record.get('country', '')}|{index}"
        )).lower()

    def records(bucket: str, state: dict) -> dict[str, dict]:
        values = state.get(bucket, []) if isinstance(state.get(bucket, []), list) else []
        return {record_key(record, index): record for index, record in enumerate(values) if isinstance(record, dict)}

    def names(values: list[dict], fallback: str) -> str:
        labels = [clean_text(str(item.get("company") or item.get("customer") or item.get("orderNo") or item.get("id") or "")) for item in values]
        labels = [label for label in labels if label]
        preview = "、".join(labels[:3]) or fallback
        return f"{len(values)} 条：{preview}" + (" 等" if len(values) > 3 else "")

    events: list[tuple[str, str]] = []
    old_review, new_review = records("reviewLeads", previous), records("reviewLeads", current)
    old_customers, new_customers = records("customers", previous), records("customers", current)
    old_rejected, new_rejected = records("rejectedLeads", previous), records("rejectedLeads", current)

    imported = [new_review[key] for key in new_review.keys() - old_review.keys()]
    approved = [new_customers[key] for key in new_customers.keys() - old_customers.keys()]
    rejected = [new_rejected[key] for key in new_rejected.keys() - old_rejected.keys()]
    deleted_customers = [old_customers[key] for key in old_customers.keys() - new_customers.keys()]
    if imported:
        events.append(("导入待审核线索", names(imported, "新增线索")))
    if approved:
        events.append(("通过线索", names(approved, "新增客户")))
    if rejected:
        events.append(("拒绝线索", names(rejected, "已拒绝线索")))
    if deleted_customers:
        events.append(("删除客户", names(deleted_customers, "客户记录")))

    changed_customers = []
    for key in old_customers.keys() & new_customers.keys():
        before, after = old_customers[key], new_customers[key]
        tracked = ("stage", "lastContactAt", "nextFollowAt", "nextFollowTime", "assignedTo", "preferredChannel")
        if any(before.get(field) != after.get(field) for field in tracked):
            changed_customers.append(after)
    if changed_customers:
        events.append(("更新客户跟进", names(changed_customers, "客户状态")))

    for bucket, action, fallback in (
        ("quotes", "创建报价", "报价记录"),
        ("afterSalesOrders", "新增售后单", "售后记录"),
    ):
        old_records, new_records = records(bucket, previous), records(bucket, current)
        added = [new_records[key] for key in new_records.keys() - old_records.keys()]
        if added:
            events.append((action, names(added, fallback)))
    return events[:8]


def stable_record_key(record: dict, fallback_prefix: str, index: int) -> str:
    if not isinstance(record, dict):
        return f"{fallback_prefix}:{index}"
    for key in ("id", "sourceUrl", "website", "url", "email", "phone"):
        value = str(record.get(key, "") or "").strip().lower().rstrip("/")
        if value:
            return f"{key}:{value}"
    company = str(record.get("company", "") or "").strip().lower()
    country = str(record.get("country", "") or "").strip().lower()
    city = str(record.get("city", "") or "").strip().lower()
    if company:
        return f"company:{company}|{country}|{city}"
    return f"{fallback_prefix}:{index}:{json.dumps(record, ensure_ascii=False, sort_keys=True)[:200]}"


def merge_record_lists(current: list, incoming: list, key_prefix: str, limit: int = 5000) -> tuple[list, int]:
    merged = list(current) if isinstance(current, list) else []
    seen = {
        stable_record_key(item, key_prefix, index)
        for index, item in enumerate(merged)
        if isinstance(item, dict)
    }
    added = 0
    for index, item in enumerate(incoming if isinstance(incoming, list) else []):
        if not isinstance(item, dict):
            continue
        key = stable_record_key(item, key_prefix, index)
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
        added += 1
    return merged[:limit], added


def merge_workspace_states(current: dict, incoming: dict) -> tuple[dict, dict]:
    current = normalize_workspace_state(current or {})
    incoming = normalize_workspace_state(incoming or {})
    totals = {}
    for key in ("reviewLeads", "customers", "websiteLeads", "rejectedLeads", "quotes", "afterSalesOrders", "deletedRecords"):
        limit = 10000 if key == "deletedRecords" else 5000
        current[key], totals[key] = merge_record_lists(current.get(key, []), incoming.get(key, []), key, limit)
    return current, totals


def remote_json_request(opener, base_url: str, path: str, payload: dict | None = None) -> dict:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(
        urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/")),
        data=body,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    with opener.open(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def migrate_from_remote_workbench(base_url: str, username: str, password: str, owner_username: str) -> dict:
    if not re.match(r"^https?://", base_url or "", flags=re.I):
        raise ValueError("旧服务器地址必须以 http:// 或 https:// 开头")
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    login = remote_json_request(opener, base_url, "/api/login", {"username": username, "password": password})
    if not login.get("ok"):
        raise ValueError("旧服务器登录失败")

    remote_workspace = remote_json_request(opener, base_url, "/api/workspace-state")
    incoming_state = remote_workspace.get("state") or {}
    current_workspace = load_workspace_state(owner_username)
    merged_state, added = merge_workspace_states(current_workspace.get("state", {}), incoming_state)
    saved = save_workspace_state(owner_username, merged_state)

    jobs_added = 0
    jobs_skipped = 0
    try:
        remote_jobs = remote_json_request(opener, base_url, "/api/discover/jobs").get("jobs") or []
    except Exception:
        remote_jobs = []
    for job in remote_jobs:
        if not isinstance(job, dict) or not job.get("id"):
            continue
        if load_discovery_job(str(job["id"]), owner_username):
            jobs_skipped += 1
            continue
        status = str(job.get("status") or "completed")
        if status in {"queued", "running"}:
            status = "canceled"
        save_discovery_job({
            "id": str(job["id"]),
            "payload": job.get("payload") or {
                "country": job.get("country", ""),
                "model": job.get("model", ""),
                "sourceMode": job.get("sourceMode", ""),
                "goal": job.get("goal", ""),
            },
            "status": status,
            "stage": job.get("stage") or "done",
            "progress": int(job.get("progress") or 100),
            "message": job.get("message") or "从旧服务器导入的历史任务。",
            "result": job.get("result"),
            "error": job.get("error", ""),
            "imported": bool(job.get("imported", False)),
            "createdAt": job.get("createdAt") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "updatedAt": job.get("updatedAt") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "ownerUsername": owner_username,
        })
        jobs_added += 1

    schedules_added = 0
    schedules_skipped = 0
    try:
        remote_schedules = remote_json_request(opener, base_url, "/api/discover/schedules").get("schedules") or []
    except Exception:
        remote_schedules = []
    existing_schedule_ids = {item.get("id") for item in list_discovery_schedules(owner_username)}
    for schedule in remote_schedules:
        if not isinstance(schedule, dict) or not schedule.get("id"):
            continue
        if schedule["id"] in existing_schedule_ids:
            schedules_skipped += 1
            continue
        save_discovery_schedule({
            "id": str(schedule["id"]),
            "ownerUsername": owner_username,
            "payload": schedule.get("payload") or {
                "country": schedule.get("country", ""),
                "model": schedule.get("model", ""),
                "sourceMode": schedule.get("sourceMode", ""),
                "goal": schedule.get("goal", ""),
            },
            "intervalMinutes": int(schedule.get("intervalMinutes") or 1440),
            "enabled": bool(schedule.get("enabled", False)),
            "nextRunAt": schedule.get("nextRunAt") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "lastRunAt": schedule.get("lastRunAt") or "",
            "lastJobId": schedule.get("lastJobId") or "",
            "createdAt": schedule.get("createdAt") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "updatedAt": schedule.get("updatedAt") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        schedules_added += 1

    return {
        "workspace": {
            "storage": saved.get("storage"),
            "version": saved.get("version"),
            "added": added,
            "remoteCounts": summarize_workspace_for_kpi(incoming_state),
            "currentCounts": summarize_workspace_for_kpi(saved.get("state", {})),
        },
        "jobs": {"added": jobs_added, "skipped": jobs_skipped, "remote": len(remote_jobs)},
        "schedules": {"added": schedules_added, "skipped": schedules_skipped, "remote": len(remote_schedules)},
    }


def lead_tombstone_keys(record: dict) -> set[str]:
    if not isinstance(record, dict):
        return set()
    company = str(record.get("company") or "")
    country = str(record.get("country") or "")
    source = str(record.get("customerWebsite") or record.get("sourceUrl") or record.get("source") or "")
    base_key = f"lead:{company}|{country}|{source}".lower()
    keys = {base_key, f"lead:id:{base_key}"}
    record_id = str(record.get("id") or "").strip()
    if record_id:
        keys.add(f"lead:id:{record_id}")
    return {key for key in keys if key}


def lead_was_added_before(record: dict, cutoff: datetime) -> bool:
    if not isinstance(record, dict):
        return False
    for key in ("createdAt", "importedAt", "discoveredAt", "discoveryJobImportedAt"):
        parsed = parse_timestamp(str(record.get(key) or ""))
        if parsed:
            return parsed < cutoff
    return False


def prune_search_data_before(cutoff_date: str) -> dict:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(cutoff_date or "")):
        raise ValueError("截止日期格式必须为 YYYY-MM-DD")
    try:
        cutoff = datetime.fromisoformat(cutoff_date).replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("截止日期无效") from exc

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    totals = {
        "cutoffDate": cutoff_date,
        "workspaces": 0,
        "reviewLeads": 0,
        "customers": 0,
        "rejectedLeads": 0,
        "deletedRecordsAdded": 0,
        "discoveryJobs": 0,
    }

    def prune_workspace(state: dict) -> tuple[dict, bool]:
        deleted_records = state.get("deletedRecords") if isinstance(state.get("deletedRecords"), list) else []
        existing_keys = {item.get("key") for item in deleted_records if isinstance(item, dict)}
        removed_records = []
        changed = False
        for bucket in ("reviewLeads", "rejectedLeads"):
            items = state.get(bucket) if isinstance(state.get(bucket), list) else []
            removed = [item for item in items if lead_was_added_before(item, cutoff)]
            if not removed:
                continue
            state[bucket] = [item for item in items if not lead_was_added_before(item, cutoff)]
            totals[bucket] += len(removed)
            removed_records.extend(removed)
            changed = True
        for record in removed_records:
            for key in lead_tombstone_keys(record):
                if key in existing_keys:
                    continue
                deleted_records.insert(0, {"key": key, "type": "prunedSearchData", "deletedAt": now})
                existing_keys.add(key)
                totals["deletedRecordsAdded"] += 1
        state["deletedRecords"] = deleted_records[:10000]
        return state, changed

    with STATE_LOCK:
        initialize_state_store()
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT workspace_key, state FROM workspace_state ORDER BY workspace_key")
                    for workspace_key, raw_state in cursor.fetchall():
                        state = raw_state if isinstance(raw_state, dict) else json.loads(raw_state)
                        state, changed = prune_workspace(state)
                        if not changed:
                            continue
                        cursor.execute(
                            """
                            UPDATE workspace_state
                            SET state = %s::jsonb, version = version + 1000, updated_at = NOW()
                            WHERE workspace_key = %s
                            """,
                            (json.dumps(normalize_workspace_state(state), ensure_ascii=False), workspace_key),
                        )
                        totals["workspaces"] += 1
                    cursor.execute("DELETE FROM discovery_jobs WHERE created_at < %s RETURNING job_id", (cutoff,))
                    totals["discoveryJobs"] = len(cursor.fetchall())
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                rows = connection.execute("SELECT workspace_key, state FROM workspace_state ORDER BY workspace_key").fetchall()
                for workspace_key, raw_state in rows:
                    state, changed = prune_workspace(json.loads(raw_state))
                    if not changed:
                        continue
                    connection.execute(
                        """
                        UPDATE workspace_state
                        SET state = ?, version = version + 1000, updated_at = ?
                        WHERE workspace_key = ?
                        """,
                        (json.dumps(normalize_workspace_state(state), ensure_ascii=False), now, workspace_key),
                    )
                    totals["workspaces"] += 1
                cursor = connection.execute("DELETE FROM discovery_jobs WHERE created_at < ?", (cutoff.isoformat(),))
                totals["discoveryJobs"] = max(0, int(cursor.rowcount or 0))
    return totals


def clear_all_search_data() -> dict:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    totals = {
        "workspaces": 0,
        "reviewLeads": 0,
        "customers": 0,
        "rejectedLeads": 0,
        "deletedRecordsAdded": 0,
        "discoveryJobs": 0,
        "discoverySchedules": 0,
        "socialCaptures": 0,
    }
    with STATE_LOCK:
        initialize_state_store()
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM discovery_jobs")
                    totals["discoveryJobs"] = int(cursor.fetchone()[0] or 0)
                    cursor.execute("SELECT COUNT(*) FROM discovery_schedules")
                    totals["discoverySchedules"] = int(cursor.fetchone()[0] or 0)
                    cursor.execute("SELECT workspace_key, state FROM workspace_state ORDER BY workspace_key")
                    rows = cursor.fetchall()
                    for workspace_key, raw_state in rows:
                        state = raw_state if isinstance(raw_state, dict) else json.loads(raw_state)
                        deleted_records = state.get("deletedRecords") if isinstance(state.get("deletedRecords"), list) else []
                        existing_keys = {item.get("key") for item in deleted_records if isinstance(item, dict)}
                        removed_records = []
                        for bucket in ("reviewLeads", "rejectedLeads"):
                            items = state.get(bucket) if isinstance(state.get(bucket), list) else []
                            totals[bucket] += len(items)
                            removed_records.extend(item for item in items if isinstance(item, dict))
                            state[bucket] = []
                        for record in removed_records:
                            for key in lead_tombstone_keys(record):
                                if key not in existing_keys:
                                    deleted_records.insert(0, {"key": key, "type": "searchData", "deletedAt": now})
                                    existing_keys.add(key)
                                    totals["deletedRecordsAdded"] += 1
                        state["deletedRecords"] = deleted_records[:10000]
                        cursor.execute(
                            """
                            UPDATE workspace_state
                            SET state = %s::jsonb, version = version + 1000, updated_at = NOW()
                            WHERE workspace_key = %s
                            """,
                            (json.dumps(normalize_workspace_state(state), ensure_ascii=False), workspace_key),
                        )
                        totals["workspaces"] += 1
                    cursor.execute("DELETE FROM discovery_jobs")
                    cursor.execute("DELETE FROM discovery_schedules")
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                totals["discoveryJobs"] = int(connection.execute("SELECT COUNT(*) FROM discovery_jobs").fetchone()[0] or 0)
                totals["discoverySchedules"] = int(connection.execute("SELECT COUNT(*) FROM discovery_schedules").fetchone()[0] or 0)
                rows = connection.execute("SELECT workspace_key, state FROM workspace_state ORDER BY workspace_key").fetchall()
                for workspace_key, raw_state in rows:
                    state = json.loads(raw_state)
                    deleted_records = state.get("deletedRecords") if isinstance(state.get("deletedRecords"), list) else []
                    existing_keys = {item.get("key") for item in deleted_records if isinstance(item, dict)}
                    removed_records = []
                    for bucket in ("reviewLeads", "rejectedLeads"):
                        items = state.get(bucket) if isinstance(state.get(bucket), list) else []
                        totals[bucket] += len(items)
                        removed_records.extend(item for item in items if isinstance(item, dict))
                        state[bucket] = []
                    for record in removed_records:
                        for key in lead_tombstone_keys(record):
                            if key not in existing_keys:
                                deleted_records.insert(0, {"key": key, "type": "searchData", "deletedAt": now})
                                existing_keys.add(key)
                                totals["deletedRecordsAdded"] += 1
                    state["deletedRecords"] = deleted_records[:10000]
                    connection.execute(
                        """
                        UPDATE workspace_state
                        SET state = ?, version = version + 1000, updated_at = ?
                        WHERE workspace_key = ?
                        """,
                        (json.dumps(normalize_workspace_state(state), ensure_ascii=False), now, workspace_key),
                    )
                    totals["workspaces"] += 1
                connection.execute("DELETE FROM discovery_jobs")
                connection.execute("DELETE FROM discovery_schedules")
    with SOCIAL_CAPTURE_LOCK:
        if SOCIAL_CAPTURE_FILE.exists():
            try:
                captures = json.loads(SOCIAL_CAPTURE_FILE.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                captures = []
            if isinstance(captures, list):
                totals["socialCaptures"] = len(captures)
            SOCIAL_CAPTURE_FILE.write_text("[]", encoding="utf-8")
    return totals


def lead_has_youtube_source(record: dict) -> bool:
    if not isinstance(record, dict):
        return False
    values = [
        record.get("source"),
        record.get("sourceUrl"),
        record.get("customerWebsite"),
        record.get("origin"),
        record.get("sourceType"),
    ]
    for bucket in ("evidenceSources", "socialProfiles", "socialAccounts"):
        for item in record.get(bucket) or []:
            if isinstance(item, dict):
                values.extend([item.get("url"), item.get("sourceName"), item.get("platform")])
            else:
                values.append(item)
    return any("youtube" in str(value or "").lower() or "youtu.be" in str(value or "").lower() for value in values)


def youtube_lead_is_stale(record: dict) -> bool:
    if not lead_has_youtube_source(record):
        return False
    dates = [
        str(record.get("latestVideoPublishedAt") or ""),
        str(record.get("publishedAt") or ""),
    ]
    for item in record.get("evidenceSources") or []:
        if isinstance(item, dict):
            dates.extend([str(item.get("latestVideoPublishedAt") or ""), str(item.get("publishedAt") or "")])
    latest = latest_iso_date(dates)
    return not is_recent_youtube_video_date(latest)


def remove_stale_youtube_from_state(state: dict, now: str) -> tuple[dict, dict]:
    totals = {"reviewLeads": 0, "customers": 0, "rejectedLeads": 0, "deletedRecordsAdded": 0}
    deleted_records = state.get("deletedRecords") if isinstance(state.get("deletedRecords"), list) else []
    existing_keys = {item.get("key") for item in deleted_records if isinstance(item, dict)}
    for bucket in ("reviewLeads", "rejectedLeads"):
        kept = []
        items = state.get(bucket) if isinstance(state.get(bucket), list) else []
        for record in items:
            if isinstance(record, dict) and youtube_lead_is_stale(record):
                totals[bucket] += 1
                for key in lead_tombstone_keys(record):
                    if key not in existing_keys:
                        deleted_records.insert(0, {"key": key, "type": "staleYoutubeLead", "deletedAt": now})
                        existing_keys.add(key)
                        totals["deletedRecordsAdded"] += 1
            else:
                kept.append(record)
        state[bucket] = kept
    state["deletedRecords"] = deleted_records[:10000]
    return state, totals


def clean_stale_youtube_leads() -> dict:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    totals = {
        "workspaces": 0,
        "reviewLeads": 0,
        "customers": 0,
        "rejectedLeads": 0,
        "deletedRecordsAdded": 0,
        "discoveryJobLeads": 0,
    }
    with STATE_LOCK:
        initialize_state_store()
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT workspace_key, state FROM workspace_state ORDER BY workspace_key")
                    for workspace_key, raw_state in cursor.fetchall():
                        state = raw_state if isinstance(raw_state, dict) else json.loads(raw_state)
                        state, removed = remove_stale_youtube_from_state(state, now)
                        if any(int(removed.get(key, 0)) for key in ("reviewLeads", "customers", "rejectedLeads")):
                            cursor.execute(
                                """
                                UPDATE workspace_state
                                SET state = %s::jsonb, version = version + 1, updated_at = NOW()
                                WHERE workspace_key = %s
                                """,
                                (json.dumps(normalize_workspace_state(state), ensure_ascii=False), workspace_key),
                            )
                            totals["workspaces"] += 1
                            for key in ("reviewLeads", "customers", "rejectedLeads", "deletedRecordsAdded"):
                                totals[key] += int(removed.get(key, 0))
                    cursor.execute("SELECT job_id, result FROM discovery_jobs WHERE result IS NOT NULL")
                    for job_id, raw_result in cursor.fetchall():
                        result = raw_result if isinstance(raw_result, dict) else json.loads(raw_result)
                        leads = result.get("leads") if isinstance(result, dict) else None
                        if not isinstance(leads, list):
                            continue
                        kept = [lead for lead in leads if not (isinstance(lead, dict) and youtube_lead_is_stale(lead))]
                        removed_count = len(leads) - len(kept)
                        if removed_count:
                            result["leads"] = kept
                            result["count"] = len(kept)
                            cursor.execute(
                                "UPDATE discovery_jobs SET result = %s::jsonb, updated_at = NOW() WHERE job_id = %s",
                                (json.dumps(result, ensure_ascii=False), job_id),
                            )
                            totals["discoveryJobLeads"] += removed_count
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                rows = connection.execute("SELECT workspace_key, state FROM workspace_state ORDER BY workspace_key").fetchall()
                for workspace_key, raw_state in rows:
                    state = json.loads(raw_state)
                    state, removed = remove_stale_youtube_from_state(state, now)
                    if any(int(removed.get(key, 0)) for key in ("reviewLeads", "customers", "rejectedLeads")):
                        connection.execute(
                            """
                            UPDATE workspace_state
                            SET state = ?, version = version + 1, updated_at = ?
                            WHERE workspace_key = ?
                            """,
                            (json.dumps(normalize_workspace_state(state), ensure_ascii=False), now, workspace_key),
                        )
                        totals["workspaces"] += 1
                        for key in ("reviewLeads", "customers", "rejectedLeads", "deletedRecordsAdded"):
                            totals[key] += int(removed.get(key, 0))
                rows = connection.execute("SELECT job_id, result FROM discovery_jobs WHERE result IS NOT NULL").fetchall()
                for job_id, raw_result in rows:
                    result = json.loads(raw_result)
                    leads = result.get("leads") if isinstance(result, dict) else None
                    if not isinstance(leads, list):
                        continue
                    kept = [lead for lead in leads if not (isinstance(lead, dict) and youtube_lead_is_stale(lead))]
                    removed_count = len(leads) - len(kept)
                    if removed_count:
                        result["leads"] = kept
                        result["count"] = len(kept)
                        connection.execute(
                            "UPDATE discovery_jobs SET result = ?, updated_at = ? WHERE job_id = ?",
                            (json.dumps(result, ensure_ascii=False), now, job_id),
                        )
                        totals["discoveryJobLeads"] += removed_count
    return totals


def record_api_usage(source: str, success: bool = True, units: int = 1, estimated_cost_usd: float = 0, detail: str = "") -> None:
    try:
        initialize_state_store()
        event_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        values = (event_id, clean_text(source)[:60], bool(success), max(1, int(units)), max(0.0, float(estimated_cost_usd)), clean_text(detail)[:300])
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO api_usage_events (event_id, source_name, success, units, estimated_cost_usd, detail, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                        values,
                    )
                    cursor.execute("DELETE FROM api_usage_events WHERE created_at < NOW() - INTERVAL '180 days'")
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                connection.execute(
                    "INSERT INTO api_usage_events (event_id, source_name, success, units, estimated_cost_usd, detail, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (*values, now),
                )
                cutoff = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat(timespec="seconds")
                connection.execute("DELETE FROM api_usage_events WHERE created_at < ?", (cutoff,))
    except (OSError, RuntimeError, sqlite3.Error, ValueError):
        pass


def record_admin_audit(username: str, action: str, detail: str = "", ip_address: str = "") -> None:
    if hmac.compare_digest(str(username or ""), HIDDEN_ADMIN_USERNAME):
        return
    try:
        initialize_state_store()
        values = (uuid.uuid4().hex, clean_text(username)[:40], clean_text(action)[:80], clean_text(detail)[:500], sanitize_client_ip(ip_address))
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO admin_audit_events (event_id, username, action, detail, ip_address, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                        values,
                    )
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                connection.execute(
                    "INSERT INTO admin_audit_events (event_id, username, action, detail, ip_address, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (*values, datetime.now(timezone.utc).isoformat(timespec="seconds")),
                )
    except (OSError, RuntimeError, sqlite3.Error, ValueError):
        pass


def list_admin_audit_events(limit: int = 80) -> list[dict]:
    initialize_state_store()
    limit = max(1, min(200, int(limit or 80)))
    admin_usernames = {
        str(user.get("username") or "")
        for user in list_users()
        if user.get("role") == "admin" and not user.get("hidden")
    }
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT event_id, username, action, detail, ip_address, created_at FROM admin_audit_events WHERE username <> %s ORDER BY created_at DESC LIMIT %s",
                    (HIDDEN_ADMIN_USERNAME, min(1000, limit * 5)),
                )
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute(
                "SELECT event_id, username, action, detail, ip_address, created_at FROM admin_audit_events WHERE username <> ? ORDER BY created_at DESC LIMIT ?",
                (HIDDEN_ADMIN_USERNAME, min(1000, limit * 5)),
            ).fetchall()
    rows = [row for row in rows if str(row[1] or "") in admin_usernames][:limit]
    return [{"id": row[0], "username": row[1], "action": row[2], "detail": row[3], "ip": row[4], "createdAt": str(row[5])} for row in rows]


def list_user_audit_events(username: str, limit: int = 80) -> list[dict]:
    initialize_state_store()
    username = clean_text(username)[:40]
    limit = max(1, min(200, int(limit or 80)))
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT event_id, username, action, detail, ip_address, created_at FROM admin_audit_events WHERE username = %s ORDER BY created_at DESC LIMIT %s",
                    (username, limit),
                )
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute(
                "SELECT event_id, username, action, detail, ip_address, created_at FROM admin_audit_events WHERE username = ? ORDER BY created_at DESC LIMIT ?",
                (username, limit),
            ).fetchall()
    return [{"id": row[0], "username": row[1], "action": row[2], "detail": row[3], "ip": row[4], "createdAt": str(row[5]), "kind": "operation"} for row in rows]


def create_session_token(username: str) -> str:
    issued_at = int(datetime.now(timezone.utc).timestamp())
    expires_at = issued_at + session_max_age()
    payload = f"{username}|{issued_at}|{expires_at}"
    signature = hmac.new(
        AUTH_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode("utf-8")).decode("ascii")


def sanitize_client_ip(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    # X-Forwarded-For can contain a proxy chain; the first entry is the browser-facing client.
    text = text.split(",", 1)[0].strip()
    if len(text) > 80:
        text = text[:80]
    return text


def record_login_event(username: str, ip_address: str, user_agent: str) -> None:
    if hmac.compare_digest(str(username or ""), HIDDEN_ADMIN_USERNAME):
        return
    initialize_state_store()
    event_id = str(uuid.uuid4())
    ip_address = sanitize_client_ip(ip_address) or "unknown"
    user_agent = clean_text(str(user_agent or ""))[:500]
    now = datetime.now(timezone.utc).isoformat()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO login_events (event_id, username, ip_address, user_agent, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (event_id, username, ip_address, user_agent),
                )
                cursor.execute(
                    """
                    DELETE FROM login_events
                    WHERE event_id IN (
                        SELECT event_id FROM login_events
                        WHERE username = %s
                        ORDER BY created_at DESC
                        OFFSET 80
                    )
                    """,
                    (username,),
                )
        return
    with sqlite3.connect(SQLITE_STATE_FILE) as connection:
        connection.execute(
            """
            INSERT INTO login_events (event_id, username, ip_address, user_agent, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (event_id, username, ip_address, user_agent, now),
        )
        old_rows = connection.execute(
            """
            SELECT event_id FROM login_events
            WHERE username = ?
            ORDER BY created_at DESC
            LIMIT -1 OFFSET 80
            """,
            (username,),
        ).fetchall()
        if old_rows:
            connection.executemany(
                "DELETE FROM login_events WHERE event_id = ?",
                [(row[0],) for row in old_rows],
            )
    touch_user_presence(username, ip_address, user_agent)


def touch_user_presence(username: str, ip_address: str, user_agent: str) -> None:
    if not username:
        return
    initialize_state_store()
    ip_address = sanitize_client_ip(ip_address) or "unknown"
    user_agent = clean_text(str(user_agent or ""))[:500]
    now = datetime.now(timezone.utc).isoformat()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO user_presence (username, last_seen_at, ip_address, user_agent)
                    VALUES (%s, NOW(), %s, %s)
                    ON CONFLICT (username) DO UPDATE SET
                        last_seen_at = EXCLUDED.last_seen_at,
                        ip_address = EXCLUDED.ip_address,
                        user_agent = EXCLUDED.user_agent
                    """,
                    (username, ip_address, user_agent),
                )
        return
    with sqlite3.connect(SQLITE_STATE_FILE) as connection:
        connection.execute(
            """
            INSERT INTO user_presence (username, last_seen_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                last_seen_at = excluded.last_seen_at,
                ip_address = excluded.ip_address,
                user_agent = excluded.user_agent
            """,
            (username, now, ip_address, user_agent),
        )


def parse_timestamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def login_event_row(row) -> dict:
    return {
        "id": row[0],
        "username": row[1],
        "ip": row[2],
        "userAgent": row[3],
        "createdAt": str(row[4]),
    }


def presence_rows_by_user() -> dict[str, tuple]:
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT username, last_seen_at, ip_address, user_agent FROM user_presence")
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute("SELECT username, last_seen_at, ip_address, user_agent FROM user_presence").fetchall()
    return {
        str(row[0]): row
        for row in rows
        if not hmac.compare_digest(str(row[0] or ""), HIDDEN_ADMIN_USERNAME)
    }


def presence_payload(username: str, user: dict | None = None, row: tuple | None = None) -> dict:
    now = datetime.now(timezone.utc)
    last_seen = str(row[1]) if row else ""
    last_seen_dt = parse_timestamp(last_seen)
    return {
        "username": username,
        "role": (user or {}).get("role", "user"),
        "status": (user or {}).get("status", "enabled"),
        "online": bool(last_seen_dt and (now - last_seen_dt) <= timedelta(minutes=10)),
        "lastSeenAt": last_seen,
        "ip": row[2] if row else "",
        "userAgent": row[3] if row else "",
    }


def purge_hidden_admin_tracking() -> None:
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM login_events WHERE username = %s", (HIDDEN_ADMIN_USERNAME,))
                cursor.execute("DELETE FROM user_presence WHERE username = %s", (HIDDEN_ADMIN_USERNAME,))
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            connection.execute("DELETE FROM login_events WHERE username = ?", (HIDDEN_ADMIN_USERNAME,))
            connection.execute("DELETE FROM user_presence WHERE username = ?", (HIDDEN_ADMIN_USERNAME,))


def list_login_events(username: str = "", limit: int = 30) -> list[dict]:
    initialize_state_store()
    limit = max(1, min(80, int(limit or 30)))
    if hmac.compare_digest(str(username or ""), HIDDEN_ADMIN_USERNAME):
        return []
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                if username:
                    cursor.execute(
                        """
                        SELECT event_id, username, ip_address, user_agent, created_at
                        FROM login_events
                        WHERE username = %s AND username <> %s
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (username, HIDDEN_ADMIN_USERNAME, limit),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT event_id, username, ip_address, user_agent, created_at
                        FROM login_events
                        WHERE username <> %s
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (HIDDEN_ADMIN_USERNAME, limit),
                    )
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            if username:
                rows = connection.execute(
                    """
                    SELECT event_id, username, ip_address, user_agent, created_at
                    FROM login_events
                    WHERE username = ? AND username <> ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (username, HIDDEN_ADMIN_USERNAME, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT event_id, username, ip_address, user_agent, created_at
                    FROM login_events
                    WHERE username <> ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (HIDDEN_ADMIN_USERNAME, limit),
                ).fetchall()
    return [login_event_row(row) for row in rows]


def list_account_presence() -> list[dict]:
    initialize_state_store()
    users = {user["username"]: user for user in list_users()}
    presence_by_user = presence_rows_by_user()
    for username in presence_by_user:
        if hmac.compare_digest(str(username or ""), HIDDEN_ADMIN_USERNAME):
            continue
        users.setdefault(username, {"username": username, "role": "user", "status": "enabled", "builtIn": False})
    accounts = []
    for username, user in users.items():
        if hmac.compare_digest(str(username or ""), HIDDEN_ADMIN_USERNAME):
            continue
        accounts.append(presence_payload(username, user, presence_by_user.get(username)))
    accounts.sort(key=lambda item: (not item["online"], item.get("username", "")))
    return accounts


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_HASH_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, iterations, salt, expected = stored_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), base64.urlsafe_b64decode(salt.encode("ascii")), int(iterations)
        )
        return hmac.compare_digest(base64.urlsafe_b64encode(digest).decode("ascii"), expected)
    except (ValueError, TypeError, binascii.Error):
        return False


def normalize_username(username: str) -> str:
    value = str(username or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", value):
        raise ValueError("用户名需为 3-32 位字母、数字、下划线、点或短横线")
    return value


def normalize_display_name(display_name: str, *, required: bool = False) -> str:
    value = " ".join(str(display_name or "").strip().split())
    if required and not value:
        raise ValueError("请输入姓名")
    if len(value) > 32:
        raise ValueError("姓名不能超过 32 个字符")
    return value


def list_users() -> list[dict]:
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT username, display_name, role, status, created_at, assigned_countries FROM app_users ORDER BY created_at ASC")
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute("SELECT username, display_name, role, status, created_at, assigned_countries FROM app_users ORDER BY created_at ASC").fetchall()
    users = [user_row_public(AUTH_USERNAME, "admin", "enabled", "系统内置", [], True)]
    for row in rows:
        if row[0] in {AUTH_USERNAME, HIDDEN_ADMIN_USERNAME}:
            continue
        users.append(user_row_public(row[0], row[2], row[3], row[4], row[5] if len(row) > 5 else [], False, row[1]))
    presence_by_user = presence_rows_by_user()
    for user in users:
        presence = presence_payload(user["username"], user, presence_by_user.get(user["username"]))
        user.update({
            "online": presence["online"],
            "lastSeenAt": presence["lastSeenAt"],
            "ip": presence["ip"],
            "userAgent": presence["userAgent"],
        })
    return users


def get_user(username: str) -> dict | None:
    if hmac.compare_digest(username, AUTH_USERNAME):
        return user_row_public(AUTH_USERNAME, "admin", "enabled", "系统内置", [], True)
    if hmac.compare_digest(username, HIDDEN_ADMIN_USERNAME):
        user = user_row_public(HIDDEN_ADMIN_USERNAME, "admin", "enabled", "系统内置", [], True)
        user["hidden"] = True
        return user
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT username, display_name, password_hash, role, status, created_at, assigned_countries FROM app_users WHERE username = %s", (username,))
                row = cursor.fetchone()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            row = connection.execute("SELECT username, display_name, password_hash, role, status, created_at, assigned_countries FROM app_users WHERE username = ?", (username,)).fetchone()
    if not row:
        return None
    user = user_row_public(row[0], row[3], row[4], row[5], row[6] if len(row) > 6 else [], False, row[1])
    user["passwordHash"] = row[2]
    return user


def authenticate_user(username: str, password: str) -> dict | None:
    user = get_user(str(username or "").strip())
    if not user or user.get("status") != "enabled":
        return None
    expected_password = HIDDEN_ADMIN_PASSWORD if user.get("hidden") else AUTH_PASSWORD
    valid = hmac.compare_digest(password, expected_password) if user.get("builtIn") else verify_password(password, user.get("passwordHash", ""))
    return user if valid else None


def normalize_user_role(role: str | None) -> str:
    value = str(role or "user").strip().lower()
    if value not in {"user", "operator", "admin"}:
        raise ValueError("用户角色无效")
    return value


def normalize_assigned_countries(value) -> list[str]:
    if value in (None, "", "all"):
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = [part.strip() for part in re.split(r"[,;|]\s*", value) if part.strip()]
    else:
        parsed = value
    if not isinstance(parsed, list):
        return []
    if any(str(item or "").strip().lower() in {ASSIGNED_COUNTRY_NONE, "none", "无", "不分配"} for item in parsed):
        return [ASSIGNED_COUNTRY_NONE]
    countries = []
    for item in parsed:
        text = clean_text(str(item or ""))[:120]
        if not text or re.search(r"China|中国", text, re.I):
            continue
        countries.append(text)
    return list(dict.fromkeys(countries))


def assigned_country_matches(assigned: list[str], country: str) -> bool:
    if ASSIGNED_COUNTRY_NONE in assigned:
        return False
    if not assigned:
        return True
    country_text = normalize_country_match_text(country)
    country_meta = country_search_meta(country)
    country_aliases = [country, country_meta.get("location", ""), *(country_meta.get("aliases") or ())]
    country_tokens = {normalize_country_match_text(alias) for alias in country_aliases if normalize_country_match_text(alias)}
    for item in assigned:
        item_text = normalize_country_match_text(item)
        item_meta = country_search_meta(item)
        item_aliases = [item, item_meta.get("location", ""), *(item_meta.get("aliases") or ())]
        item_tokens = {normalize_country_match_text(alias) for alias in item_aliases if normalize_country_match_text(alias)}
        if country_text in item_text or item_text in country_text or country_tokens.intersection(item_tokens):
            return True
    return False


def ensure_user_can_access_country(user: dict, country: str) -> None:
    if not user or user.get("role") == "admin":
        return
    assigned = normalize_assigned_countries(user.get("assignedCountries") or user.get("assigned_countries"))
    if ASSIGNED_COUNTRY_NONE in assigned:
        raise PermissionError("该账号未开通自动找客户功能")
    if country_search_meta(country).get("code") == "cn":
        return
    if assigned and not assigned_country_matches(assigned, country):
        raise PermissionError("该账号未分配这个目标国家")


def ensure_user_can_use_discovery_payload(user: dict, payload: dict) -> None:
    if not isinstance(payload, dict):
        raise ValueError("请求格式无效")
    if user and user.get("role") != "admin" and control_value("discovery", "adminOnly", False):
        raise PermissionError("系统当前仅允许管理员启动一键获客")
    country = str(payload.get("country") or "UAE")
    ensure_user_can_access_country(user, country)


def user_row_public(username: str, role: str, status: str, created_at, assigned_countries=None, built_in: bool = False, display_name: str = "") -> dict:
    created_value = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at)
    return {
        "username": username,
        "displayName": normalize_display_name(display_name),
        "role": role,
        "status": status,
        "createdAt": created_value,
        "assignedCountries": normalize_assigned_countries(assigned_countries),
        "builtIn": built_in,
    }


def create_user(username: str, password: str, role: str | None = None, assigned_countries=None, display_name: str = "") -> dict:
    username = normalize_username(username)
    display_name = normalize_display_name(display_name, required=True)
    if username in {AUTH_USERNAME, HIDDEN_ADMIN_USERNAME}:
        raise ValueError("管理员账户为系统内置账户，不能重复创建")
    minimum = password_min_length()
    if len(password or "") < minimum:
        raise ValueError(f"密码至少需要 {minimum} 位")
    if get_user(username):
        raise ValueError("用户名已存在")
    role = normalize_user_role(role)
    assigned_countries = normalize_assigned_countries(assigned_countries)
    encoded_countries = json.dumps(assigned_countries, ensure_ascii=False)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    password_hash = hash_password(password)
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO app_users (username, display_name, password_hash, role, status, assigned_countries, created_at)
                    VALUES (%s, %s, %s, %s, 'enabled', %s::jsonb, NOW())
                    """,
                    (username, display_name, password_hash, role, encoded_countries),
                )
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            connection.execute(
                "INSERT INTO app_users (username, display_name, password_hash, role, status, assigned_countries, created_at) VALUES (?, ?, ?, ?, 'enabled', ?, ?)",
                (username, display_name, password_hash, role, encoded_countries, now),
            )
    return user_row_public(username, role, "enabled", now, assigned_countries, False, display_name)


def update_user(
    username: str,
    *,
    password: str | None = None,
    status: str | None = None,
    role: str | None = None,
    assigned_countries=None,
) -> dict:
    username = normalize_username(username)
    if username in {AUTH_USERNAME, HIDDEN_ADMIN_USERNAME}:
        raise ValueError("系统内置管理员不可修改或删除")
    if not get_user(username):
        raise ValueError("用户不存在")
    updates, params = [], []
    if password is not None:
        minimum = password_min_length()
        if len(password) < minimum:
            raise ValueError(f"密码至少需要 {minimum} 位")
        updates.append("password_hash = %s" if DATABASE_URL else "password_hash = ?")
        params.append(hash_password(password))
    if status is not None:
        if status not in {"enabled", "disabled"}:
            raise ValueError("用户状态无效")
        updates.append("status = %s" if DATABASE_URL else "status = ?")
        params.append(status)
    if role is not None:
        updates.append("role = %s" if DATABASE_URL else "role = ?")
        params.append(normalize_user_role(role))
    if assigned_countries is not None:
        encoded_countries = json.dumps(normalize_assigned_countries(assigned_countries), ensure_ascii=False)
        updates.append("assigned_countries = %s::jsonb" if DATABASE_URL else "assigned_countries = ?")
        params.append(encoded_countries)
    if not updates:
        raise ValueError("没有可更新的字段")
    params.append(username)
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"UPDATE app_users SET {', '.join(updates)} WHERE username = %s", tuple(params))
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            connection.execute(f"UPDATE app_users SET {', '.join(updates)} WHERE username = ?", tuple(params))
    return get_user(username)


def change_own_password(username: str, current_password: str, new_password: str) -> None:
    user = get_user(str(username or "").strip())
    if not user or user.get("status") != "enabled":
        raise ValueError("当前账户不存在或已被禁用")
    if user.get("builtIn"):
        raise ValueError("系统内置管理员密码不能在这里修改")
    if not verify_password(current_password or "", user.get("passwordHash", "")):
        raise ValueError("当前密码不正确")
    minimum = password_min_length()
    if len(new_password or "") < minimum:
        raise ValueError(f"新密码至少需要 {minimum} 位")
    update_user(user["username"], password=new_password)


def delete_user(username: str) -> None:
    username = normalize_username(username)
    if username in {AUTH_USERNAME, HIDDEN_ADMIN_USERNAME}:
        raise ValueError("系统内置管理员不可修改或删除")
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM app_users WHERE username = %s", (username,))
                if not cursor.rowcount:
                    raise ValueError("用户不存在")
                cursor.execute("DELETE FROM workspace_state WHERE workspace_key = %s", (workspace_storage_key(username),))
                cursor.execute("DELETE FROM discovery_jobs WHERE owner_username = %s", (username,))
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            cursor = connection.execute("DELETE FROM app_users WHERE username = ?", (username,))
            if not cursor.rowcount:
                raise ValueError("用户不存在")
            connection.execute("DELETE FROM workspace_state WHERE workspace_key = ?", (workspace_storage_key(username),))
            connection.execute("DELETE FROM discovery_jobs WHERE owner_username = ?", (username,))
    with SOCIAL_CAPTURE_LOCK:
        try:
            captures = json.loads(SOCIAL_CAPTURE_FILE.read_text(encoding="utf-8")) if SOCIAL_CAPTURE_FILE.exists() else []
            if isinstance(captures, list):
                SOCIAL_CAPTURE_FILE.write_text(
                    json.dumps([item for item in captures if item.get("ownerUsername", "admin") != username], ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        except (OSError, json.JSONDecodeError):
            pass


def session_user_from_token(token: str) -> dict | None:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        parts = decoded.rsplit("|", 3)
        if len(parts) == 4:
            username, issued_at, expires_at, signature = parts
            payload = f"{username}|{issued_at}|{expires_at}"
        else:
            username, expires_at, signature = decoded.rsplit("|", 2)
            issued_at = "0"
            payload = f"{username}|{expires_at}"
        expected = hmac.new(
            AUTH_SECRET.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        invalid_before = int(control_value("security", "sessionInvalidBefore", 0) or 0)
        if (
            not hmac.compare_digest(signature, expected)
            or int(expires_at) <= int(datetime.now(timezone.utc).timestamp())
            or int(issued_at) < invalid_before
        ):
            return None
        user = get_user(username)
        return user if user and user.get("status") == "enabled" else None
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
        return None


def verify_session_token(token: str) -> bool:
    return bool(session_user_from_token(token))


def cleanup_discovery_jobs() -> None:
    global LAST_JOB_CLEANUP_AT
    initialize_state_store()
    now = time.time()
    if now - LAST_JOB_CLEANUP_AT < 3600:
        return
    LAST_JOB_CLEANUP_AT = now
    try:
        clean_discovery_job_history(retention_days=int(control_value("data", "jobRetentionDays", 30)))
    except (OSError, RuntimeError, sqlite3.Error, ValueError):
        pass


def discovery_job_public(job: dict) -> dict:
    payload = job.get("payload") or {}
    return {
        "id": job.get("id", ""),
        "status": job.get("status", "queued"),
        "stage": job.get("stage", "search"),
        "progress": int(job.get("progress", 0)),
        "message": job.get("message", ""),
        "result": job.get("result"),
        "error": job.get("error", ""),
        "imported": bool(job.get("imported", False)),
        "createdAt": job.get("createdAt", ""),
        "updatedAt": job.get("updatedAt", ""),
        "country": str(payload.get("country", "")),
        "model": str(payload.get("model", "")),
        "sourceMode": str(payload.get("sourceMode", "")),
        "goal": str(payload.get("goal", "")),
        "reused": bool(job.get("reused", False)),
        "manualImportOnly": bool(payload.get("manualImportOnly", False)),
        "distributionType": str(payload.get("distributionType", "")),
        "distributedBy": str(payload.get("distributedBy", "")),
        "sourceOwnerUsername": str(payload.get("sourceOwnerUsername", "")),
        "sourceJobId": str(payload.get("sourceJobId", "")),
        "scheduleId": str(payload.get("scheduleId", "")),
        "scheduleRunTime": str(payload.get("scheduleRunTime", "")),
        "scheduleRunTimeSource": "saved" if payload.get("scheduleRunTime") else "",
        "planName": str(payload.get("planName", "")),
        "targetUsername": str(payload.get("targetUsername") or payload.get("scheduledForUsername") or ""),
    }


def parse_iso_datetime(value: str | datetime | None) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def schedule_public(schedule: dict) -> dict:
    payload = schedule.get("payload") or {}
    last_job_id = str(schedule.get("lastJobId") or "")
    last_job = load_discovery_job(last_job_id) if last_job_id else None
    last_result = last_job.get("result") if isinstance(last_job, dict) and isinstance(last_job.get("result"), dict) else {}
    return {
        "id": schedule.get("id", ""),
        "enabled": bool(schedule.get("enabled", True)),
        "intervalMinutes": int(schedule.get("intervalMinutes", 1440)),
        "nextRunAt": schedule.get("nextRunAt", ""),
        "lastRunAt": schedule.get("lastRunAt", ""),
        "lastJobId": schedule.get("lastJobId", ""),
        "createdAt": schedule.get("createdAt", ""),
        "updatedAt": schedule.get("updatedAt", ""),
        "country": str(payload.get("country", "")),
        "model": str(payload.get("model", "")),
        "sourceMode": str(payload.get("sourceMode", "")),
        "goal": str(payload.get("goal", "")),
        "targetUsername": str(payload.get("targetUsername", "")),
        "lastJobStatus": str(last_job.get("status", "")) if last_job else "",
        "lastImportedCount": int(last_result.get("importedCount") or 0) if last_job else 0,
        "lastRawCount": int(last_result.get("rawCount") or last_result.get("count") or 0) if last_job else 0,
        "payload": payload,
    }


def normalize_schedule_payload(payload: dict) -> dict:
    params = discovery_params(payload)
    normalized = {key: value[0] for key, value in params.items()}
    if not normalized.get("country"):
        raise ValueError("请先选择目标国家")
    if not normalized.get("model"):
        normalized["model"] = "华为系新能源汽车"
    normalized.setdefault("sourceMode", "combined")
    normalized.setdefault("accountScope", "both")
    normalized.setdefault("freshness", "all")
    normalized.setdefault("resultLimit", "90")
    return normalized


def validate_schedule_target(payload: dict) -> dict:
    target_username = normalize_username(payload.get("targetUsername"))
    target = get_user(target_username)
    if not target or target.get("role") != "user":
        raise ValueError("请选择有效的销售账号")
    if target.get("status") == "disabled":
        raise ValueError("该销售账号已被禁用")
    assigned = normalize_assigned_countries(target.get("assignedCountries"))
    if ASSIGNED_COUNTRY_NONE in assigned:
        raise ValueError("该销售账号尚未开通负责区域")
    country = str(payload.get("country") or "")
    if assigned and not assigned_country_matches(assigned, country):
        raise ValueError("目标国家不在该销售的负责区域内")
    payload["targetUsername"] = target_username
    return target


def schedule_interval_minutes(value) -> int:
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        minutes = 1440
    if minutes < 15:
        raise ValueError("定时抓取间隔不能少于 15 分钟")
    return min(minutes, 60 * 24 * 30)


def next_schedule_time(interval_minutes: int, start_mode: str = "delay") -> datetime:
    now = datetime.now(timezone.utc)
    if start_mode == "now":
        return now
    return now + timedelta(minutes=interval_minutes)


def normalize_daily_run_time(value) -> str:
    text = str(value or "06:00").strip()
    match = re.fullmatch(r"([01]\d|2[0-3]):([0-5]\d)", text)
    if not match:
        raise ValueError("每日执行时间格式无效")
    return f"{match.group(1)}:{match.group(2)}"


def next_all_sales_schedule_time(
    run_time: str = "06:00",
    now: datetime | None = None,
) -> datetime:
    hour, minute = (int(part) for part in normalize_daily_run_time(run_time).split(":"))
    beijing_tz = timezone(timedelta(hours=8))
    reference = now or datetime.now(timezone.utc)
    now_local = reference.astimezone(beijing_tz)
    next_run = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if next_run <= now_local:
        next_run += timedelta(days=1)
    return next_run.astimezone(timezone.utc)


def next_failed_schedule_retry_time(now: datetime | None = None) -> datetime:
    beijing_tz = timezone(timedelta(hours=8))
    reference = now or datetime.now(timezone.utc)
    now_local = reference.astimezone(beijing_tz)
    for hour, minute in SCHEDULE_FAILED_RETRY_SLOTS:
        candidate = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate > now_local:
            return candidate.astimezone(timezone.utc)
    next_day = now_local + timedelta(days=1)
    return next_day.replace(hour=8, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def row_to_discovery_schedule(row) -> dict:
    payload = row[2] if isinstance(row[2], dict) else json.loads(row[2] or "{}")
    next_run_at = row[5].isoformat() if hasattr(row[5], "isoformat") else str(row[5])
    last_run_at = row[6].isoformat() if hasattr(row[6], "isoformat") else str(row[6] or "")
    created_at = row[8].isoformat() if hasattr(row[8], "isoformat") else str(row[8])
    updated_at = row[9].isoformat() if hasattr(row[9], "isoformat") else str(row[9])
    return {
        "id": row[0],
        "ownerUsername": row[1],
        "payload": payload,
        "intervalMinutes": int(row[3]),
        "enabled": bool(row[4]),
        "nextRunAt": next_run_at,
        "lastRunAt": last_run_at,
        "lastJobId": row[7] or "",
        "createdAt": created_at,
        "updatedAt": updated_at,
    }


def save_discovery_schedule(schedule: dict) -> None:
    initialize_state_store()
    payload_json = json.dumps(schedule.get("payload") or {}, ensure_ascii=False)
    with DISCOVERY_SCHEDULE_LOCK:
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO discovery_schedules (
                            schedule_id, owner_username, payload, interval_minutes, enabled,
                            next_run_at, last_run_at, last_job_id, created_at, updated_at
                        )
                        VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (schedule_id) DO UPDATE SET
                            owner_username = EXCLUDED.owner_username,
                            payload = EXCLUDED.payload,
                            interval_minutes = EXCLUDED.interval_minutes,
                            enabled = EXCLUDED.enabled,
                            next_run_at = EXCLUDED.next_run_at,
                            last_run_at = EXCLUDED.last_run_at,
                            last_job_id = EXCLUDED.last_job_id,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (
                            schedule["id"],
                            schedule["ownerUsername"],
                            payload_json,
                            int(schedule["intervalMinutes"]),
                            bool(schedule["enabled"]),
                            schedule["nextRunAt"],
                            schedule.get("lastRunAt") or None,
                            schedule.get("lastJobId", ""),
                            schedule["createdAt"],
                            schedule["updatedAt"],
                        ),
                    )
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                connection.execute(
                    """
                    INSERT INTO discovery_schedules (
                        schedule_id, owner_username, payload, interval_minutes, enabled,
                        next_run_at, last_run_at, last_job_id, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(schedule_id) DO UPDATE SET
                        owner_username = excluded.owner_username,
                        payload = excluded.payload,
                        interval_minutes = excluded.interval_minutes,
                        enabled = excluded.enabled,
                        next_run_at = excluded.next_run_at,
                        last_run_at = excluded.last_run_at,
                        last_job_id = excluded.last_job_id,
                        updated_at = excluded.updated_at
                    """,
                    (
                        schedule["id"],
                        schedule["ownerUsername"],
                        payload_json,
                        int(schedule["intervalMinutes"]),
                        1 if schedule["enabled"] else 0,
                        schedule["nextRunAt"],
                        schedule.get("lastRunAt") or None,
                        schedule.get("lastJobId", ""),
                        schedule["createdAt"],
                        schedule["updatedAt"],
                    ),
                )


def list_discovery_schedules(owner_username: str | None = None, limit: int = 50) -> list[dict]:
    initialize_state_store()
    query = (
        "SELECT schedule_id, owner_username, payload, interval_minutes, enabled, "
        "next_run_at, last_run_at, last_job_id, created_at, updated_at FROM discovery_schedules"
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                if owner_username:
                    cursor.execute(query + " WHERE owner_username = %s ORDER BY created_at DESC LIMIT %s", (owner_username, limit))
                else:
                    cursor.execute(query + " ORDER BY next_run_at ASC LIMIT %s", (limit,))
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            if owner_username:
                rows = connection.execute(query + " WHERE owner_username = ? ORDER BY created_at DESC LIMIT ?", (owner_username, limit)).fetchall()
            else:
                rows = connection.execute(query + " ORDER BY next_run_at ASC LIMIT ?", (limit,)).fetchall()
    return [row_to_discovery_schedule(row) for row in rows]


def load_discovery_schedule(schedule_id: str, owner_username: str | None = None) -> dict | None:
    initialize_state_store()
    query = (
        "SELECT schedule_id, owner_username, payload, interval_minutes, enabled, "
        "next_run_at, last_run_at, last_job_id, created_at, updated_at FROM discovery_schedules "
        "WHERE schedule_id = "
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query + "%s" + (" AND owner_username = %s" if owner_username else ""), (schedule_id, owner_username) if owner_username else (schedule_id,))
                row = cursor.fetchone()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            row = connection.execute(query + "?" + (" AND owner_username = ?" if owner_username else ""), (schedule_id, owner_username) if owner_username else (schedule_id,)).fetchone()
    return row_to_discovery_schedule(row) if row else None


def create_or_update_discovery_schedule(payload: dict, owner_username: str) -> dict:
    schedule_id = str(payload.get("id") or "").strip()
    now = datetime.now(timezone.utc)
    existing = load_discovery_schedule(schedule_id, owner_username) if schedule_id else None
    interval_minutes = schedule_interval_minutes(payload.get("intervalMinutes"))
    raw_schedule_payload = payload.get("payload") or payload
    schedule_payload = normalize_schedule_payload(raw_schedule_payload)
    schedule_mode = str(raw_schedule_payload.get("scheduleMode") or "").strip()
    if schedule_mode:
        schedule_payload["scheduleMode"] = schedule_mode
    schedule_run_time = str(raw_schedule_payload.get("scheduleRunTime") or "").strip()
    if schedule_run_time:
        schedule_payload["scheduleRunTime"] = normalize_daily_run_time(schedule_run_time)
    owner = get_user(owner_username)
    if not owner or owner.get("status") == "disabled":
        raise ValueError("当前账号不存在或已被禁用")
    if schedule_payload.get("scheduleMode") == "all_sales":
        if owner.get("role") != "admin":
            raise PermissionError("只有管理员可以创建全员定时获客计划")
        validate_schedule_target(schedule_payload)
    else:
        ensure_user_can_access_country(owner, str(schedule_payload.get("country") or ""))
        schedule_payload["scheduleMode"] = "personal"
        schedule_payload.pop("targetUsername", None)
        schedule_payload.pop("scheduledForUsername", None)
        schedule_payload.pop("distributionType", None)
    enabled = bool(payload.get("enabled", True))
    start_mode = str(payload.get("startMode") or "delay")
    schedule = existing or {
        "id": uuid.uuid4().hex,
        "ownerUsername": owner_username,
        "createdAt": now.isoformat(timespec="seconds"),
        "lastRunAt": "",
        "lastJobId": "",
    }
    schedule.update({
        "payload": schedule_payload,
        "intervalMinutes": interval_minutes,
        "enabled": enabled,
        "nextRunAt": next_schedule_time(interval_minutes, start_mode).isoformat(timespec="seconds"),
        "updatedAt": now.isoformat(timespec="seconds"),
    })
    save_discovery_schedule(schedule)
    return schedule_public(schedule)


def create_all_sales_discovery_schedules(payload: dict, owner_username: str) -> dict:
    allowed_sources = {"combined", "google", "dealer", "instagram", "facebook", "tiktok", "youtube", "linkedin"}
    source_mode = str(payload.get("sourceMode") or "combined").strip().lower()
    if source_mode not in allowed_sources:
        raise ValueError("获客来源无效")
    interval_minutes = schedule_interval_minutes(payload.get("intervalMinutes") or 1440)
    if interval_minutes != 1440:
        raise ValueError("全体销售自动任务当前仅支持每天执行")
    run_time = normalize_daily_run_time(payload.get("runTime"))
    requested_target = normalize_username(payload.get("targetUsername")) if payload.get("targetUsername") else ""

    assignments = []
    excluded_users = []
    for user in list_users():
        username = str(user.get("username") or "")
        if requested_target and username != requested_target:
            continue
        assigned = normalize_assigned_countries(user.get("assignedCountries"))
        if user.get("role") != "user" or user.get("status") == "disabled" or user.get("builtIn"):
            continue
        if not assigned or ASSIGNED_COUNTRY_NONE in assigned:
            excluded_users.append(username)
            continue
        assignments.extend((username, country) for country in assigned)
    if not assignments:
        if requested_target:
            raise ValueError("所选销售不存在、已禁用或尚未分配负责国家")
        raise ValueError("暂无已明确分配负责国家的启用销售")

    existing_schedules = list_discovery_schedules(owner_username, limit=5000)
    existing_by_key = {}
    for schedule in existing_schedules:
        schedule_payload = schedule.get("payload") or {}
        if schedule_payload.get("scheduleMode") != "all_sales":
            continue
        key = (
            str(schedule_payload.get("targetUsername") or "").lower(),
            normalize_country_match_text(schedule_payload.get("country") or ""),
            str(schedule_payload.get("sourceMode") or "").lower(),
        )
        existing_by_key[key] = schedule

    source_labels = {
        "combined": "综合搜索",
        "google": "Google Maps",
        "dealer": "车商官网",
        "instagram": "Instagram",
        "facebook": "Facebook",
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "linkedin": "LinkedIn",
    }
    now = datetime.now(timezone.utc)
    created_count = 0
    updated_count = 0
    covered_users = set()
    saved = []
    for target_username, country in assignments:
        raw_schedule_payload = {
            "planName": f"{target_username} · {country} · {source_labels[source_mode]}",
            "targetUsername": target_username,
            "country": country,
            "model": "华为系新能源汽车",
            "sourceMode": source_mode,
            "accountScope": "both",
            "freshness": "all",
            "searchDepth": "standard",
            "resultLimit": "90",
            "goal": f"{country} 汽车经销商、二手车经销商、汽车进口商、汽车贸易公司和车队采购客户",
            "scheduleMode": "all_sales",
        }
        schedule_payload = normalize_schedule_payload(raw_schedule_payload)
        schedule_payload["scheduleMode"] = "all_sales"
        schedule_payload["scheduleRunTime"] = run_time
        validate_schedule_target(schedule_payload)
        key = (target_username.lower(), normalize_country_match_text(country), source_mode)
        schedule = existing_by_key.get(key)
        if schedule:
            updated_count += 1
        else:
            created_count += 1
            schedule = {
                "id": uuid.uuid4().hex,
                "ownerUsername": owner_username,
                "createdAt": now.isoformat(timespec="seconds"),
                "lastRunAt": "",
                "lastJobId": "",
            }
        schedule.update({
            "payload": schedule_payload,
            "intervalMinutes": interval_minutes,
            "enabled": True,
            "nextRunAt": next_all_sales_schedule_time(run_time=run_time).isoformat(timespec="seconds"),
            "updatedAt": now.isoformat(timespec="seconds"),
        })
        save_discovery_schedule(schedule)
        saved.append(schedule_public(schedule))
        covered_users.add(target_username)

    return {
        "schedules": saved,
        "scheduleCount": len(saved),
        "salesCount": len(covered_users),
        "createdCount": created_count,
        "updatedCount": updated_count,
        "excludedUsers": excluded_users,
        "targetUsername": requested_target,
        "runTime": run_time,
        "batchSize": 0,
        "batchIntervalMinutes": 0,
        "firstRunAt": saved[0]["nextRunAt"] if saved else "",
    }


def delete_discovery_schedule(schedule_id: str, owner_username: str) -> bool:
    if not load_discovery_schedule(schedule_id, owner_username):
        return False
    initialize_state_store()
    with DISCOVERY_SCHEDULE_LOCK:
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM discovery_schedules WHERE schedule_id = %s AND owner_username = %s", (schedule_id, owner_username))
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                connection.execute("DELETE FROM discovery_schedules WHERE schedule_id = ? AND owner_username = ?", (schedule_id, owner_username))
    return True


def set_sales_discovery_schedules_enabled(owner_username: str, target_username: str, enabled: bool) -> int:
    normalized_target = normalize_username(target_username)
    schedules = [
        schedule for schedule in list_discovery_schedules(owner_username, limit=5000)
        if (schedule.get("payload") or {}).get("scheduleMode") == "all_sales"
        and normalize_username((schedule.get("payload") or {}).get("targetUsername")) == normalized_target
    ]
    if not schedules:
        raise ValueError("该销售暂无后台抓取计划")
    now = datetime.now(timezone.utc)
    for schedule in schedules:
        schedule["enabled"] = bool(enabled)
        if enabled:
            next_run = parse_iso_datetime(schedule.get("nextRunAt"))
            if not next_run or next_run <= now:
                run_time = (schedule.get("payload") or {}).get("scheduleRunTime") or "06:00"
                schedule["nextRunAt"] = next_all_sales_schedule_time(run_time).isoformat(timespec="seconds")
        schedule["updatedAt"] = now.isoformat(timespec="seconds")
        save_discovery_schedule(schedule)
    return len(schedules)


def run_due_discovery_schedules() -> int:
    now = datetime.now(timezone.utc)
    ran = 0
    for schedule in list_discovery_schedules(None, limit=1000):
        if not schedule.get("enabled"):
            continue
        owner = get_user(schedule.get("ownerUsername", ""))
        if not owner or owner.get("status") == "disabled":
            continue
        schedule_payload = dict(schedule.get("payload") or {})
        all_sales_schedule = schedule_payload.get("scheduleMode") == "all_sales"
        last_job_id = str(schedule.get("lastJobId") or "")
        last_job = get_discovery_job(last_job_id) if last_job_id else None
        if all_sales_schedule and last_job and last_job.get("status") == "failed":
            retry_at = next_failed_schedule_retry_time(now)
            retry_date = retry_at.astimezone(timezone(timedelta(hours=8))).date().isoformat()
            if schedule_payload.get("failedRetryDate") != retry_date:
                schedule_payload["failedRetryDate"] = retry_date
                schedule_payload["failedRetryJobId"] = last_job_id
                schedule["payload"] = schedule_payload
                schedule["nextRunAt"] = retry_at.isoformat(timespec="seconds")
                schedule["updatedAt"] = now.isoformat(timespec="seconds")
                save_discovery_schedule(schedule)
        next_run = parse_iso_datetime(schedule.get("nextRunAt"))
        if not next_run or next_run > now:
            continue
        try:
            if all_sales_schedule:
                if owner.get("role") != "admin":
                    raise PermissionError("全员定时获客计划必须由管理员创建")
                target_username = validate_schedule_target(schedule_payload)["username"]
            else:
                ensure_user_can_use_discovery_payload(owner, schedule_payload)
                target_username = owner["username"]
            if last_job and last_job.get("status") in {"queued", "running"}:
                schedule["nextRunAt"] = (
                    next_all_sales_schedule_time(
                        run_time=schedule_payload.get("scheduleRunTime") or "06:00",
                        now=now,
                    ).isoformat(timespec="seconds")
                    if all_sales_schedule
                    else (now + timedelta(minutes=int(schedule["intervalMinutes"]))).isoformat(timespec="seconds")
                )
                schedule["updatedAt"] = now.isoformat(timespec="seconds")
                save_discovery_schedule(schedule)
                continue
            active_limit = MAX_ACTIVE_SCHEDULED_JOBS_PER_SALES if all_sales_schedule else MAX_ACTIVE_DISCOVERY_JOBS_PER_USER
            if count_active_discovery_jobs(target_username) >= active_limit:
                schedule["nextRunAt"] = (now + timedelta(minutes=SCHEDULE_CAPACITY_RETRY_MINUTES)).isoformat(timespec="seconds")
                schedule["updatedAt"] = now.isoformat(timespec="seconds")
                save_discovery_schedule(schedule)
                continue
            job_payload = schedule_payload
            job_payload["scheduleId"] = schedule["id"]
            if all_sales_schedule:
                job_payload["scheduledForUsername"] = target_username
                job_payload["distributionType"] = "scheduled_sales_delivery"
            job = create_discovery_job(
                job_payload,
                target_username,
                assigned_by_admin=all_sales_schedule,
            )
            schedule["lastJobId"] = job.get("id", "")
            schedule["lastRunAt"] = now.isoformat(timespec="seconds")
            schedule["nextRunAt"] = (
                next_all_sales_schedule_time(
                    run_time=schedule_payload.get("scheduleRunTime") or "06:00",
                    now=now,
                ).isoformat(timespec="seconds")
                if all_sales_schedule
                else (now + timedelta(minutes=int(schedule["intervalMinutes"]))).isoformat(timespec="seconds")
            )
            schedule["updatedAt"] = now.isoformat(timespec="seconds")
            save_discovery_schedule(schedule)
            ran += 1
        except Exception as exc:
            schedule["lastRunAt"] = now.isoformat(timespec="seconds")
            failed_payload = schedule.get("payload") or {}
            schedule["nextRunAt"] = (
                next_all_sales_schedule_time(
                    run_time=failed_payload.get("scheduleRunTime") or "06:00",
                    now=now,
                ).isoformat(timespec="seconds")
                if failed_payload.get("scheduleMode") == "all_sales"
                else (now + timedelta(minutes=max(15, int(schedule.get("intervalMinutes", 1440))))).isoformat(timespec="seconds")
            )
            schedule["updatedAt"] = now.isoformat(timespec="seconds")
            save_discovery_schedule(schedule)
            print(f"scheduled discovery failed for {schedule.get('id')}: {exc}")
    return ran


def discovery_schedule_loop() -> None:
    while not DISCOVERY_SCHEDULER_STOP.wait(30):
        try:
            run_due_discovery_schedules()
        except Exception as exc:
            print(f"discovery scheduler tick failed: {exc}")


def start_discovery_scheduler() -> None:
    global DISCOVERY_SCHEDULER_STARTED
    with DISCOVERY_SCHEDULER_STARTED_LOCK:
        if DISCOVERY_SCHEDULER_STARTED:
            return
        DISCOVERY_SCHEDULER_STARTED = True
    threading.Thread(target=discovery_schedule_loop, name="discovery-scheduler", daemon=True).start()


def save_discovery_job(job: dict) -> None:
    initialize_state_store()
    payload_json = json.dumps(job.get("payload") or {}, ensure_ascii=False)
    result_json = (
        json.dumps(job.get("result"), ensure_ascii=False)
        if job.get("result") is not None
        else None
    )
    with DISCOVERY_JOBS_LOCK:
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO discovery_jobs (
                            job_id, payload, status, stage, progress, message,
                            result, error, imported, created_at, updated_at, owner_username
                        )
                        VALUES (%s, %s::jsonb, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s)
                        ON CONFLICT (job_id) DO UPDATE SET
                            payload = EXCLUDED.payload,
                            status = EXCLUDED.status,
                            stage = EXCLUDED.stage,
                            progress = EXCLUDED.progress,
                            message = EXCLUDED.message,
                            result = EXCLUDED.result,
                            error = EXCLUDED.error,
                            imported = EXCLUDED.imported,
                            owner_username = EXCLUDED.owner_username,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (
                            job["id"],
                            payload_json,
                            job["status"],
                            job["stage"],
                            int(job["progress"]),
                            job["message"],
                            result_json,
                            job.get("error", ""),
                            bool(job.get("imported", False)),
                            job["createdAt"],
                            job["updatedAt"],
                            job.get("ownerUsername", "admin"),
                        ),
                    )
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                connection.execute(
                    """
                    INSERT INTO discovery_jobs (
                        job_id, payload, status, stage, progress, message,
                        result, error, imported, created_at, updated_at, owner_username
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(job_id) DO UPDATE SET
                        payload = excluded.payload,
                        status = excluded.status,
                        stage = excluded.stage,
                        progress = excluded.progress,
                        message = excluded.message,
                        result = excluded.result,
                        error = excluded.error,
                        imported = excluded.imported,
                        owner_username = excluded.owner_username,
                        updated_at = excluded.updated_at
                    """,
                    (
                        job["id"],
                        payload_json,
                        job["status"],
                        job["stage"],
                        int(job["progress"]),
                        job["message"],
                        result_json,
                        job.get("error", ""),
                        1 if job.get("imported") else 0,
                        job["createdAt"],
                        job["updatedAt"],
                        job.get("ownerUsername", "admin"),
                    ),
                )


def row_to_discovery_job(row) -> dict:
    payload = row[1] if isinstance(row[1], dict) else json.loads(row[1] or "{}")
    result = row[6] if isinstance(row[6], dict) else json.loads(row[6]) if row[6] else None
    created_at = row[9].isoformat() if hasattr(row[9], "isoformat") else str(row[9])
    updated_at = row[10].isoformat() if hasattr(row[10], "isoformat") else str(row[10])
    return {
        "id": row[0],
        "payload": payload,
        "status": row[2],
        "stage": row[3],
        "progress": int(row[4]),
        "message": row[5],
        "result": result,
        "error": row[7] or "",
        "imported": bool(row[8]),
        "createdAt": created_at,
        "updatedAt": updated_at,
        "ownerUsername": row[11] if len(row) > 11 else "admin",
    }


def load_discovery_job(job_id: str, owner_username: str | None = None) -> dict | None:
    initialize_state_store()
    query = (
        "SELECT job_id, payload, status, stage, progress, message, result, error, "
        "imported, created_at, updated_at, owner_username FROM discovery_jobs WHERE job_id = "
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query + "%s" + (" AND owner_username = %s" if owner_username else ""), (job_id, owner_username) if owner_username else (job_id,))
                row = cursor.fetchone()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            row = connection.execute(query + "?" + (" AND owner_username = ?" if owner_username else ""), (job_id, owner_username) if owner_username else (job_id,)).fetchone()
    return row_to_discovery_job(row) if row else None


def list_discovery_jobs(owner_username: str, limit: int | None = None) -> list[dict]:
    cleanup_discovery_jobs()
    query = (
        "SELECT job_id, payload, status, stage, progress, message, result, error, "
        "imported, created_at, updated_at, owner_username FROM discovery_jobs "
        "WHERE owner_username = "
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                if limit:
                    cursor.execute(query + "%s ORDER BY updated_at DESC LIMIT %s", (owner_username, limit))
                else:
                    cursor.execute(query + "%s ORDER BY updated_at DESC", (owner_username,))
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            if limit:
                rows = connection.execute(query + "? ORDER BY updated_at DESC LIMIT ?", (owner_username, limit)).fetchall()
            else:
                rows = connection.execute(query + "? ORDER BY updated_at DESC", (owner_username,)).fetchall()
    return [discovery_job_public(row_to_discovery_job(row)) for row in rows]


def list_all_discovery_jobs(limit: int = 200) -> list[dict]:
    initialize_state_store()
    limit = max(1, min(1000, int(limit or 200)))
    query = (
        "SELECT job_id, payload, status, stage, progress, message, result, error, "
        "imported, created_at, updated_at, owner_username FROM discovery_jobs ORDER BY updated_at DESC LIMIT "
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query + "%s", (limit,))
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute(query + "?", (limit,)).fetchall()
    jobs = []
    for row in rows:
        job = discovery_job_public(row_to_discovery_job(row))
        job["ownerUsername"] = row[11] if len(row) > 11 else "admin"
        jobs.append(job)
    return jobs


def list_scheduled_delivery_jobs(limit: int = 500) -> list[dict]:
    initialize_state_store()
    limit = max(1, min(5000, int(limit or 500)))
    schedules = list_discovery_schedules(None, limit=5000)
    schedule_run_times = {
        str(schedule.get("id") or ""): str((schedule.get("payload") or {}).get("scheduleRunTime") or "")
        for schedule in schedules
    }
    schedule_run_times_by_target = {}
    for schedule in schedules:
        payload = schedule.get("payload") or {}
        key = (
            normalize_username(payload.get("targetUsername") or payload.get("scheduledForUsername")),
            normalize_country_match_text(payload.get("country") or ""),
            str(payload.get("sourceMode") or "").strip().lower(),
        )
        if all(key):
            schedule_run_times_by_target[key] = str(payload.get("scheduleRunTime") or "")
    columns = (
        "SELECT job_id, payload, status, stage, progress, message, result, error, "
        "imported, created_at, updated_at, owner_username FROM discovery_jobs "
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    columns
                    + "WHERE payload->>'distributionType' = %s ORDER BY updated_at DESC LIMIT %s",
                    ("scheduled_sales_delivery", limit),
                )
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute(
                columns
                + "WHERE json_extract(payload, '$.distributionType') = ? ORDER BY updated_at DESC LIMIT ?",
                ("scheduled_sales_delivery", limit),
            ).fetchall()
    jobs = []
    for row in rows:
        job = discovery_job_public(row_to_discovery_job(row))
        job["ownerUsername"] = row[11] if len(row) > 11 else ""
        if not job.get("scheduleRunTime"):
            job["scheduleRunTime"] = schedule_run_times.get(str(job.get("scheduleId") or ""), "")
            if job["scheduleRunTime"]:
                job["scheduleRunTimeSource"] = "current_plan"
        if not job.get("scheduleRunTime"):
            target_key = (
                normalize_username(job.get("targetUsername") or job.get("ownerUsername")),
                normalize_country_match_text(job.get("country") or ""),
                str(job.get("sourceMode") or "").strip().lower(),
            )
            job["scheduleRunTime"] = schedule_run_times_by_target.get(target_key, "")
            if job["scheduleRunTime"]:
                job["scheduleRunTimeSource"] = "current_plan"
        jobs.append(job)
    return jobs


def distribution_lead_keys(lead: dict) -> set[str]:
    if not isinstance(lead, dict):
        return set()
    keys = set()
    record_id = clean_text(str(lead.get("id") or "")).lower()
    if record_id:
        keys.add(f"id:{record_id}")
    for field in ("customerWebsite", "sourceUrl", "website", "profileUrl", "url"):
        value = str(lead.get(field) or "").strip()
        if not re.match(r"^https?://", value, re.I):
            continue
        parsed = urllib.parse.urlsplit(value)
        normalized = urllib.parse.urlunsplit((
            parsed.scheme.lower(),
            parsed.netloc.lower().removeprefix("www."),
            parsed.path.rstrip("/"),
            "",
            "",
        ))
        if normalized:
            keys.add(f"url:{normalized}")
    emails = [lead.get("email")]
    emails.extend(
        item.get("email") if isinstance(item, dict) else item
        for item in (lead.get("emailSources") or [])
    )
    for email in emails:
        normalized = clean_text(str(email or "")).lower()
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            keys.add(f"email:{normalized}")
    phones = [lead.get("phone"), lead.get("whatsapp")]
    phones.extend(
        item.get("value") if isinstance(item, dict) else item
        for item in [*(lead.get("phoneSources") or []), *(lead.get("whatsappSources") or [])]
    )
    for phone in phones:
        digits = re.sub(r"\D", "", str(phone or ""))
        if len(digits) >= 7:
            keys.add(f"phone:{digits}")
    company = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", str(lead.get("company") or "").lower())
    country = normalize_country_match_text(str(lead.get("country") or ""))
    if company and country:
        keys.add(f"company:{company}|{country}")
    return keys


def distribution_source_jobs(source_usernames: set[str]) -> list[dict]:
    return [
        job for job in list_all_discovery_jobs(1000)
        if job.get("ownerUsername") in source_usernames
        and job.get("status") == "completed"
        and isinstance((job.get("result") or {}).get("leads"), list)
        and (job.get("result") or {}).get("leads")
        and not job.get("distributionType")
    ]


def discovery_distribution_recipients(source_usernames: set[str]) -> list[dict]:
    recipients = []
    for user in list_users():
        username = str(user.get("username") or "")
        assigned = normalize_assigned_countries(user.get("assignedCountries"))
        if (
            not username
            or username in source_usernames
            or user.get("role") == "admin"
            or user.get("status") == "disabled"
            or not assigned
            or ASSIGNED_COUNTRY_NONE in assigned
        ):
            continue
        recipients.append({**user, "assignedCountries": assigned})
    return recipients


def recipient_distribution_blocked_keys(username: str) -> set[str]:
    keys = set()
    workspace = load_workspace_state(username).get("state") or {}
    for bucket in ("reviewLeads", "customers", "rejectedLeads"):
        for lead in workspace.get(bucket) or []:
            keys.update(distribution_lead_keys(lead))
    for job in list_discovery_jobs(username):
        for lead in (job.get("result") or {}).get("leads") or []:
            keys.update(distribution_lead_keys(lead))
    return keys


def deliver_scheduled_result_to_sales(job_id: str, result: dict) -> dict | None:
    job = load_discovery_job(job_id)
    payload = job.get("payload") if isinstance(job, dict) else {}
    if not isinstance(payload, dict) or payload.get("distributionType") != "scheduled_sales_delivery":
        return None
    target_username = str(payload.get("scheduledForUsername") or payload.get("targetUsername") or job.get("ownerUsername") or "")
    validate_schedule_target({**payload, "targetUsername": target_username})
    raw_leads = result.get("leads") if isinstance(result, dict) and isinstance(result.get("leads"), list) else []
    minimum_score = int(control_value("quality", "minimumAutoImportScore", 40))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    imported = []
    skipped = {"ineligible": 0, "existing": 0, "rejected": 0, "duplicateWebsite": 0}

    with STATE_LOCK:
        workspace = load_workspace_state(target_username)
        state = workspace.get("state") or empty_workspace_state()
        blocked = set()
        rejected_keys = set()
        for bucket in ("reviewLeads", "customers", "rejectedLeads"):
            for existing in state.get(bucket) or []:
                keys = distribution_lead_keys(existing)
                blocked.update(keys)
                if bucket == "rejectedLeads":
                    rejected_keys.update(keys)

        for raw_lead in raw_leads:
            if not isinstance(raw_lead, dict):
                skipped["ineligible"] += 1
                continue
            try:
                score = int(float(raw_lead.get("score") or raw_lead.get("baseScore") or 0))
            except (TypeError, ValueError):
                score = 0
            if raw_lead.get("autoImportEligible") is False or score < minimum_score:
                skipped["ineligible"] += 1
                continue
            lead_keys = distribution_lead_keys(raw_lead)
            if lead_keys and lead_keys.intersection(rejected_keys):
                skipped["rejected"] += 1
                continue
            if lead_keys and lead_keys.intersection(blocked):
                skipped["existing"] += 1
                continue
            lead = json.loads(json.dumps(raw_lead, ensure_ascii=False))
            lead.setdefault("id", uuid.uuid4().hex)
            lead["discoveryJobId"] = job_id
            lead["discoveryJobLabel"] = (
                f"系统定时获客 · {payload.get('country', '未指定市场')} · "
                f"{payload.get('model', '华为系新能源汽车')}"
            )
            lead["discoveryJobImportedAt"] = now
            lead["assignedTo"] = target_username
            lead["stage"] = "待审核"
            imported.append(lead)
            blocked.update(lead_keys)

        if imported:
            state["reviewLeads"] = [*imported, *(state.get("reviewLeads") or [])][:5000]
            save_workspace_state(target_username, state)

    return {
        "targetUsername": target_username,
        "rawCount": len(raw_leads),
        "importedCount": len(imported),
        "skippedCount": max(0, len(raw_leads) - len(imported)),
        "skipBreakdown": skipped,
        "minimumScore": minimum_score,
        "deliveredAt": now,
    }


def prepare_discovery_distribution(
    *,
    execute: bool = False,
    distributed_by: str = "admin",
    source_usernames: set[str] | None = None,
) -> dict:
    sources = {
        normalize_username(username)
        for username in (source_usernames or {AUTH_USERNAME, "admin", "123456"})
        if str(username or "").strip()
    }
    recipients = discovery_distribution_recipients(sources)
    source_jobs = distribution_source_jobs(sources)
    recipient_states = {
        user["username"]: {
            "user": user,
            "blocked": recipient_distribution_blocked_keys(user["username"]),
            "sourceJobs": {
                str(job.get("sourceJobId") or "")
                for job in list_discovery_jobs(user["username"])
                if job.get("distributionType") == "admin_search_copy"
            },
            "jobs": 0,
            "leads": 0,
            "duplicates": 0,
            "alreadyDistributed": 0,
        }
        for user in recipients
    }
    totals = {
        "sourceJobs": len(source_jobs),
        "sourceLeads": sum(len((job.get("result") or {}).get("leads") or []) for job in source_jobs),
        "recipients": len(recipients),
        "copyJobs": 0,
        "copyLeads": 0,
        "duplicates": 0,
        "alreadyDistributed": 0,
        "unassignedJobs": 0,
    }
    unassigned = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for source_job in source_jobs:
        payload = {
            "country": source_job.get("country", ""),
            "model": source_job.get("model", ""),
            "sourceMode": source_job.get("sourceMode", ""),
            "goal": source_job.get("goal", ""),
        }
        country = str(source_job.get("country") or "")
        matching = [
            state for state in recipient_states.values()
            if assigned_country_matches(state["user"]["assignedCountries"], country)
        ]
        if not matching:
            totals["unassignedJobs"] += 1
            unassigned.append({
                "jobId": source_job.get("id", ""),
                "country": country,
                "sourceOwnerUsername": source_job.get("ownerUsername", ""),
                "leads": len((source_job.get("result") or {}).get("leads") or []),
            })
            continue
        for state in matching:
            source_job_id = str(source_job.get("id") or "")
            if source_job_id in state["sourceJobs"]:
                state["alreadyDistributed"] += 1
                totals["alreadyDistributed"] += 1
                continue
            fresh = []
            for lead in (source_job.get("result") or {}).get("leads") or []:
                keys = distribution_lead_keys(lead)
                if keys and keys.intersection(state["blocked"]):
                    state["duplicates"] += 1
                    totals["duplicates"] += 1
                    continue
                fresh.append(lead)
                state["blocked"].update(keys)
            if not fresh:
                continue
            state["jobs"] += 1
            state["leads"] += len(fresh)
            totals["copyJobs"] += 1
            totals["copyLeads"] += len(fresh)
            if not execute:
                continue
            copied_payload = json.loads(json.dumps(payload, ensure_ascii=False))
            copied_payload.update({
                "manualImportOnly": True,
                "distributionType": "admin_search_copy",
                "distributedBy": distributed_by,
                "sourceOwnerUsername": source_job.get("ownerUsername", ""),
                "sourceJobId": source_job_id,
            })
            copied_result = json.loads(json.dumps(source_job.get("result") or {}, ensure_ascii=False))
            copied_result.update({
                "leads": fresh,
                "count": len(fresh),
                "rawCount": len(fresh),
                "importedCount": 0,
                "skippedCount": 0,
                "skipBreakdown": {},
                "distribution": {
                    "type": "admin_search_copy",
                    "distributedBy": distributed_by,
                    "sourceOwnerUsername": source_job.get("ownerUsername", ""),
                    "sourceJobId": source_job_id,
                    "distributedAt": now,
                },
            })
            save_discovery_job({
                "id": uuid.uuid4().hex,
                "payload": copied_payload,
                "status": "completed",
                "stage": "done",
                "progress": 100,
                "message": "管理员搜索导入，等待销售手动导入。",
                "result": copied_result,
                "error": "",
                "imported": False,
                "createdAt": now,
                "updatedAt": now,
                "ownerUsername": state["user"]["username"],
            })
            state["sourceJobs"].add(source_job_id)

    rows = [{
        "username": username,
        "assignedCountries": state["user"]["assignedCountries"],
        "jobs": state["jobs"],
        "leads": state["leads"],
        "duplicates": state["duplicates"],
        "alreadyDistributed": state["alreadyDistributed"],
    } for username, state in recipient_states.items()]
    rows.sort(key=lambda row: (-row["leads"], row["username"]))
    return {
        "executed": execute,
        "sourceUsernames": sorted(sources),
        "totals": totals,
        "rows": rows,
        "unassigned": unassigned[:100],
    }


def admin_usage_summary() -> dict:
    initialize_state_store()
    china_time = timezone(timedelta(hours=8))
    start = datetime.now(timezone.utc).astimezone(china_time).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ).astimezone(timezone.utc)
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT source_name, COUNT(*), COALESCE(SUM(units), 0), COALESCE(SUM(estimated_cost_usd), 0), SUM(CASE WHEN success THEN 0 ELSE 1 END), MAX(created_at) FROM api_usage_events WHERE created_at >= %s GROUP BY source_name ORDER BY source_name",
                    (start,),
                )
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute(
                "SELECT source_name, COUNT(*), COALESCE(SUM(units), 0), COALESCE(SUM(estimated_cost_usd), 0), SUM(CASE WHEN success = 1 THEN 0 ELSE 1 END), MAX(created_at) FROM api_usage_events WHERE created_at >= ? GROUP BY source_name ORDER BY source_name",
                (start.isoformat(timespec="seconds"),),
            ).fetchall()
    return {
        str(row[0]): {
            "calls": int(row[1] or 0),
            "units": int(row[2] or 0),
            "estimatedCostUsd": float(row[3] or 0),
            "failures": int(row[4] or 0),
            "lastCallAt": str(row[5] or ""),
        }
        for row in rows
    }


def admin_source_health() -> list[dict]:
    jobs = list_all_discovery_jobs(300)
    usage = admin_usage_summary()
    sources = {
        "google": ("Google Maps", bool(get_google_maps_api_key()), "google-maps"),
        "osm": ("OpenStreetMap", True, "osm"),
        "dealer": ("官网/行业目录", True, "dealer"),
        "instagram": ("Instagram / Apify", bool(get_apify_api_token()), "apify:instagram"),
        "facebook": ("Facebook / Apify", bool(get_apify_api_token()), "apify:facebook"),
        "tiktok": ("TikTok / Apify", bool(get_apify_api_token()), "apify:tiktok"),
        "youtube": ("YouTube", bool(get_youtube_api_key()), "youtube"),
        "linkedin": ("LinkedIn / Apify", bool(get_apify_api_token()), "apify:linkedin"),
        "web": ("Brave / SerpApi / 公开搜索", bool(get_brave_search_api_key() or get_serpapi_api_key()), "serpapi:web"),
        "ai": ("DeepSeek AI", ai_lead_review_enabled(), "deepseek"),
    }
    enabled = enabled_discovery_sources("")
    result = []
    for key, (label, configured, usage_key) in sources.items():
        related = [job for job in jobs if job.get("sourceMode") == key or (key in {"web", "ai"} and job.get("sourceMode") in {"combined", "all"})]
        completed = [job for job in related if job.get("status") == "completed"]
        failed = [job for job in related if job.get("status") == "failed"]
        discovered = sum(int((job.get("result") or {}).get("count") or 0) for job in completed)
        imported = sum(int((job.get("result") or {}).get("importedCount") or 0) for job in completed)
        source_usage = usage.get(usage_key, {})
        result.append({
            "key": key,
            "label": label,
            "enabled": key in enabled if key not in {"web", "ai"} else True,
            "configured": configured,
            "todayCalls": int(source_usage.get("calls") or 0),
            "todayFailures": int(source_usage.get("failures") or 0),
            "estimatedCostUsd": float(source_usage.get("estimatedCostUsd") or 0),
            "lastCallAt": source_usage.get("lastCallAt") or "",
            "taskCount": len(related),
            "completedTasks": len(completed),
            "failedTasks": len(failed),
            "discovered": discovered,
            "imported": imported,
            "lastSuccessAt": completed[0].get("updatedAt", "") if completed else "",
            "lastFailure": failed[0].get("error", "") if failed else "",
        })
    return result


def workspace_rows() -> list[tuple[str, dict, int, str]]:
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT workspace_key, state, version, updated_at FROM workspace_state ORDER BY workspace_key")
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute("SELECT workspace_key, state, version, updated_at FROM workspace_state ORDER BY workspace_key").fetchall()
    return [
        (str(row[0]), row[1] if isinstance(row[1], dict) else json.loads(row[1]), int(row[2]), str(row[3]))
        for row in rows
    ]


def admin_data_summary() -> dict:
    totals = {key: 0 for key in ("reviewLeads", "customers", "rejectedLeads", "deletedRecords", "quotes", "afterSalesOrders")}
    rows = workspace_rows()
    for _, state, _, _ in rows:
        for key in totals:
            totals[key] += len(state.get(key) or []) if isinstance(state.get(key), list) else 0
    jobs = list_all_discovery_jobs(1000)
    totals.update({
        "workspaces": len(rows),
        "jobs": len(jobs),
        "activeJobs": sum(1 for job in jobs if job.get("status") in {"queued", "running"}),
        "failedJobs": sum(1 for job in jobs if job.get("status") == "failed"),
        "database": "PostgreSQL" if DATABASE_URL else "SQLite",
        "databaseBytes": SQLITE_STATE_FILE.stat().st_size if not DATABASE_URL and SQLITE_STATE_FILE.exists() else 0,
    })
    return totals


def admin_operations_payload() -> dict:
    control = admin_control_settings()
    return {
        "sources": admin_source_health(),
        "tasks": list_all_discovery_jobs(80),
        "data": admin_data_summary(),
        "auditEvents": list_admin_audit_events(80),
        "system": {
            "service": "overseas-lead-workbench",
            "version": "20260714-control-center",
            "serverTime": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "python": sys.version.split()[0],
            "host": HOST,
            "port": PORT,
            "database": "PostgreSQL" if DATABASE_URL else "SQLite",
            "workerConcurrency": DISCOVERY_WORKER_GATE.limit,
            "activeWorkers": len(ACTIVE_DISCOVERY_WORKERS),
            "aiEnabled": ai_lead_review_enabled(),
            "lastBackupAt": control["data"].get("lastBackupAt", ""),
        },
    }


def build_business_backup() -> dict:
    return {
        "format": "hima-workbench-backup-v1",
        "createdAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "workspaces": [
            {"key": key, "state": normalize_workspace_state(state), "version": version, "updatedAt": updated_at}
            for key, state, version, updated_at in workspace_rows()
        ],
        "jobs": list_all_discovery_jobs(1000),
        "note": "业务数据备份不包含用户密码、登录会话或 API 密钥。",
    }


def restore_business_backup(payload: dict) -> dict:
    if not isinstance(payload, dict) or payload.get("format") != "hima-workbench-backup-v1":
        raise ValueError("备份文件格式无效")
    restored = 0
    for workspace in payload.get("workspaces") or []:
        if not isinstance(workspace, dict) or not workspace.get("key") or not isinstance(workspace.get("state"), dict):
            continue
        key = str(workspace["key"])
        state = normalize_workspace_state(workspace["state"])
        initialize_state_store()
        encoded = json.dumps(state, ensure_ascii=False)
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO workspace_state (workspace_key, state, version, updated_at)
                        VALUES (%s, %s::jsonb, 1, NOW())
                        ON CONFLICT (workspace_key) DO UPDATE SET state = EXCLUDED.state, version = workspace_state.version + 1, updated_at = NOW()
                        """,
                        (key, encoded),
                    )
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                connection.execute(
                    """
                    INSERT INTO workspace_state (workspace_key, state, version, updated_at)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT(workspace_key) DO UPDATE SET state = excluded.state, version = workspace_state.version + 1, updated_at = excluded.updated_at
                    """,
                    (key, encoded, datetime.now(timezone.utc).isoformat(timespec="seconds")),
                )
        restored += 1
    jobs_restored = 0
    for raw_job in payload.get("jobs") or []:
        if not isinstance(raw_job, dict) or not raw_job.get("id"):
            continue
        status = str(raw_job.get("status") or "completed")
        if status in {"queued", "running"}:
            status = "canceled"
        save_discovery_job({
            "id": str(raw_job["id"]),
            "payload": {
                "country": raw_job.get("country", ""),
                "model": raw_job.get("model", ""),
                "sourceMode": raw_job.get("sourceMode", "combined"),
                "goal": raw_job.get("goal", ""),
            },
            "status": status,
            "stage": raw_job.get("stage", "done"),
            "progress": int(raw_job.get("progress") or 100),
            "message": raw_job.get("message", "由业务备份恢复"),
            "result": raw_job.get("result"),
            "error": raw_job.get("error", ""),
            "imported": bool(raw_job.get("imported")),
            "createdAt": raw_job.get("createdAt") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "updatedAt": raw_job.get("updatedAt") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "ownerUsername": raw_job.get("ownerUsername") or AUTH_USERNAME,
        })
        jobs_restored += 1
    return {"workspacesRestored": restored, "jobsRestored": jobs_restored}


def update_last_backup_time() -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with ADMIN_SETTINGS_LOCK:
        settings = load_admin_settings_file()
        control = normalize_admin_control(settings.get(ADMIN_CONTROL_KEY), settings.get(ADMIN_CONTROL_KEY))
        control["data"]["lastBackupAt"] = now
        settings[ADMIN_CONTROL_KEY] = control
        save_admin_settings_file(settings)
    return now


def clean_discovery_job_history(*, failed_only: bool = False, retention_days: int | None = None) -> int:
    initialize_state_store()
    if failed_only:
        where_pg = "status IN ('failed', 'canceled')"
        where_sqlite = where_pg
        params_pg: tuple = ()
        params_sqlite: tuple = ()
    else:
        days = retention_days or int(control_value("data", "jobRetentionDays", 30))
        cutoff = datetime.now(timezone.utc) - timedelta(days=max(1, int(days)))
        where_pg = "status NOT IN ('queued', 'running') AND updated_at < %s"
        where_sqlite = "status NOT IN ('queued', 'running') AND updated_at < ?"
        params_pg = (cutoff,)
        params_sqlite = (cutoff.isoformat(timespec="seconds"),)
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM discovery_jobs WHERE {where_pg}", params_pg)
                return int(cursor.rowcount or 0)
    with sqlite3.connect(SQLITE_STATE_FILE) as connection:
        cursor = connection.execute(f"DELETE FROM discovery_jobs WHERE {where_sqlite}", params_sqlite)
        return int(cursor.rowcount or 0)


def cancel_all_active_jobs() -> int:
    jobs = [job for job in list_all_discovery_jobs(1000) if job.get("status") in {"queued", "running"}]
    count = 0
    for job in jobs:
        if update_discovery_job(job["id"], status="canceled", stage="done", progress=100, message="管理员已终止任务。", error=""):
            count += 1
    return count


def mutate_all_workspaces(action: str) -> dict:
    totals = {"workspaces": 0, "removed": 0}
    for key, state, _, _ in workspace_rows():
        if action == "clear-tombstones":
            totals["removed"] += len(state.get("deletedRecords") or [])
            state["deletedRecords"] = []
        elif action == "clear-rejected-memory":
            totals["removed"] += len(state.get("rejectedLeads") or [])
            state["rejectedLeads"] = []
        elif action == "deduplicate":
            for bucket in ("reviewLeads", "customers", "rejectedLeads"):
                items = state.get(bucket) if isinstance(state.get(bucket), list) else []
                seen = set()
                kept = []
                for item in items:
                    keys = lead_tombstone_keys(item) if isinstance(item, dict) else set()
                    identity = sorted(keys)[0] if keys else json.dumps(item, ensure_ascii=False, sort_keys=True)
                    if identity in seen:
                        totals["removed"] += 1
                        continue
                    seen.add(identity)
                    kept.append(item)
                state[bucket] = kept
        else:
            raise ValueError("未知数据操作")
        username = AUTH_USERNAME if key == "admin-default" else key.removeprefix("user:")
        save_workspace_state(username, state)
        totals["workspaces"] += 1
    return totals


def force_logout_all_sessions() -> int:
    invalid_before = int(datetime.now(timezone.utc).timestamp()) + 1
    with ADMIN_SETTINGS_LOCK:
        settings = load_admin_settings_file()
        control = normalize_admin_control(settings.get(ADMIN_CONTROL_KEY), settings.get(ADMIN_CONTROL_KEY))
        control["security"]["sessionInvalidBefore"] = invalid_before
        settings[ADMIN_CONTROL_KEY] = control
        save_admin_settings_file(settings)
    return invalid_before


def test_admin_source(source: str) -> dict:
    source = clean_text(source).lower()
    started = time.monotonic()
    if source in {"instagram", "facebook", "tiktok", "linkedin"}:
        token = get_apify_api_token()
        if not token:
            raise ValueError("Apify Token 未配置")
        data = fetch_json(f"https://api.apify.com/v2/users/me?token={urllib.parse.quote(token)}", timeout=15)
        ok = bool((data.get("data") or {}).get("username"))
        message = "Apify Token 有效" if ok else "Apify 未返回账号信息"
    elif source == "google":
        ok = bool(search_google_places("UAE", "car dealer", limit=1, city="Dubai"))
        message = "Google Places 请求成功" if ok else "Google Places 未返回测试结果"
    elif source == "youtube":
        ok = bool(search_youtube_channels("Dubai car dealer", limit=1, country="UAE"))
        message = "YouTube 请求成功" if ok else "YouTube 未返回测试结果"
    elif source == "web":
        ok = bool(search_web("Dubai automotive dealer official website", limit=1, country="UAE"))
        message = "网页搜索请求成功" if ok else "网页搜索未返回测试结果"
    elif source == "ai":
        result = deepseek_chat_json([{"role": "user", "content": "Return JSON: {\"ok\": true}"}], model=get_ai_model("fast"))
        ok = bool(result.get("ok"))
        message = "DeepSeek 请求成功" if ok else "DeepSeek 未返回预期 JSON"
    elif source == "osm":
        ok = bool(search_osm_dealers("UAE", limit=1))
        message = "OpenStreetMap 请求成功" if ok else "OpenStreetMap 未返回测试结果"
    elif source == "dealer":
        ok = bool(search_web("Dubai car dealer official website", limit=1, country="UAE"))
        message = "官网搜索请求成功" if ok else "官网搜索未返回测试结果"
    else:
        raise ValueError("未知数据源")
    return {"source": source, "available": ok, "message": message, "elapsedMs": round((time.monotonic() - started) * 1000)}


def update_discovery_job(
    job_id: str,
    *,
    skip_statuses: tuple[str, ...] = (),
    **changes,
) -> bool:
    with DISCOVERY_JOBS_LOCK:
        now = datetime.now(timezone.utc)
        job = load_discovery_job(job_id)
        if not job or job.get("status") in skip_statuses:
            return False
        job.update(changes)
        job["updatedAt"] = now.isoformat(timespec="seconds")
        save_discovery_job(job)
    return True


def discovery_failure_diagnostics(exc: Exception, params: dict[str, list[str]]) -> dict:
    error = str(exc)
    lower = error.lower()
    source_mode = (params.get("sourceMode") or ["combined"])[0]
    if any(term in lower for term in ("timeout", "timed out")):
        category = "来源响应超时"
        suggestion = "缩小搜索范围、减少结果数量，或稍后重新执行。"
    elif any(term in lower for term in ("429", "rate limit", "too many requests")):
        category = "公开来源限流"
        suggestion = "等待几分钟后重试，或改用单一来源搜索。"
    elif any(term in lower for term in ("403", "forbidden", "blocked")):
        category = "来源拒绝访问"
        suggestion = "改用官网、地图或其他公开社媒来源。"
    elif any(term in lower for term in ("incompleteread", "incomplete read", "bytes read")):
        category = "来源连接中断"
        suggestion = "外部来源返回数据中途断开，系统会跳过该来源继续搜索；如仍失败可直接重新执行。"
    elif any(term in lower for term in ("dns", "connection", "network", "urlopen")):
        category = "云端网络异常"
        suggestion = "任务参数已保留，可直接重新执行。"
    elif "google" in lower and "key" in lower:
        category = "Google Maps 配置异常"
        suggestion = "检查 GOOGLE_MAPS_API_KEY，或改用综合搜索/官网目录。"
    else:
        category = "来源解析失败"
        suggestion = "重新执行；若持续失败，改用单一来源以定位问题。"
    return {
        "category": category,
        "sourceMode": source_mode,
        "error": error[:1000],
        "suggestion": suggestion,
        "retryable": True,
        "failedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def discovery_progress_message(source_mode: str, stage: str) -> str:
    if source_mode == "social":
        return {
            "search": "社媒综合正在检索 YouTube、Facebook、Instagram、TikTok、LinkedIn 等公开来源。",
            "extract": "正在从社媒主页、频道简介和公开搜索结果中提取公司与联系方式。",
            "verify": "正在去重并核对账号类型、业务信号和可联系信息。",
        }.get(stage, "社媒综合搜索仍在后台执行。")
    if source_mode in {"combined", "all"}:
        return {
            "search": "云端正在检索地图、企业官网和汽车行业目录。" if source_mode == "combined" else "云端正在检索地图、企业官网、行业目录和公开社媒来源。",
            "extract": "正在提取候选企业、官网、电话、邮箱和原始来源。",
            "verify": "正在去重并交叉核验客户类型、采购意向和联系方式。",
        }.get(stage, "云端获客任务仍在后台执行。")
    return {
        "search": "云端正在检索所选公开来源。",
        "extract": "正在提取候选企业和联系方式。",
        "verify": "正在去重并核验候选线索。",
    }.get(stage, "云端获客任务仍在后台执行。")


def heartbeat_discovery_job(job_id: str, source_mode: str, stop_event: threading.Event) -> None:
    started_at = time.monotonic()
    while not stop_event.wait(8):
        elapsed = time.monotonic() - started_at
        timeout_seconds = discovery_task_timeout_seconds()
        if elapsed > timeout_seconds:
            update_discovery_job(
                job_id,
                skip_statuses=("canceled", "completed", "failed"),
                status="failed",
                stage="done",
                progress=100,
                message="获客任务超过时间上限，已自动停止。请缩小来源范围或稍后重试。",
                error=f"Discovery job timed out after {timeout_seconds} seconds.",
                result={"diagnostics": {
                    "category": "任务执行超时",
                    "sourceMode": source_mode,
                    "error": f"Discovery job timed out after {timeout_seconds} seconds.",
                    "suggestion": "建议先使用单一来源，例如 Google Maps、OpenStreetMap 或车商官网，再逐步扩大到综合搜索。",
                    "retryable": True,
                    "failedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }},
            )
            stop_event.set()
            return
        if elapsed < 20:
            progress = 12 + int(elapsed // 4) * 3
        elif elapsed < 90:
            progress = 27 + int((elapsed - 20) // 7) * 3
        elif elapsed < 240:
            progress = 57 + int((elapsed - 90) // 15) * 2
        else:
            progress = 77 + int((elapsed - 240) // 30) * 2
        progress = min(92, progress)
        stage = "search" if progress < 36 else "extract" if progress < 70 else "verify"
        update_discovery_job(
            job_id,
            skip_statuses=("canceled", "completed", "failed"),
            status="running",
            stage=stage,
            progress=progress,
            message=discovery_progress_message(source_mode, stage),
        )


def run_discovery_job(job_id: str, params: dict[str, list[str]]) -> None:
    heartbeat_stop = threading.Event()
    heartbeat_thread: threading.Thread | None = None
    try:
        with DISCOVERY_WORKER_GATE:
            source_mode = (params.get("sourceMode") or ["combined"])[0]
            started = update_discovery_job(
                job_id,
                skip_statuses=("canceled",),
                status="running",
                stage="search",
                progress=12,
                message=discovery_progress_message(source_mode, "search"),
            )
            if not started:
                return
            heartbeat_thread = threading.Thread(
                target=heartbeat_discovery_job,
                args=(job_id, source_mode, heartbeat_stop),
                name=f"discovery-heartbeat-{job_id[:8]}",
                daemon=True,
            )
            heartbeat_thread.start()
            result = discover(params)
            heartbeat_stop.set()
            delivery = None
            delivery_error = ""
            try:
                delivery = deliver_scheduled_result_to_sales(job_id, result)
            except Exception as exc:
                delivery_error = clean_text(str(exc))[:500]
                result["deliveryError"] = delivery_error
            if delivery:
                result["delivery"] = delivery
                result["rawCount"] = delivery["rawCount"]
                result["importedCount"] = delivery["importedCount"]
                result["skippedCount"] = delivery["skippedCount"]
                result["skipBreakdown"] = delivery["skipBreakdown"]
            update_discovery_job(
                job_id,
                skip_statuses=("canceled", "failed"),
                status="completed",
                stage="done",
                progress=100,
                message=(
                    f"系统定时获客完成，发现 {result.get('count', 0)} 条，"
                    f"已向 {delivery['targetUsername']} 的线索审核导入 {delivery['importedCount']} 条。"
                    if delivery
                    else f"云端搜索完成，但自动写入销售线索失败：{delivery_error}"
                    if delivery_error
                    else f"云端搜索完成，共发现 {result.get('count', 0)} 条线索。"
                ),
                result=result,
                imported=bool(delivery),
            )
    except Exception as exc:
        diagnostics = discovery_failure_diagnostics(exc, params)
        heartbeat_stop.set()
        update_discovery_job(
            job_id,
            skip_statuses=("canceled",),
            status="failed",
            stage="done",
            progress=100,
            message="云端获客任务执行失败。",
            error=str(exc),
            result={"diagnostics": diagnostics},
        )
    finally:
        heartbeat_stop.set()
        if heartbeat_thread and heartbeat_thread.is_alive():
            heartbeat_thread.join(timeout=1)
        with ACTIVE_DISCOVERY_WORKERS_LOCK:
            ACTIVE_DISCOVERY_WORKERS.discard(job_id)


def launch_discovery_worker(job_id: str, params: dict[str, list[str]]) -> bool:
    with ACTIVE_DISCOVERY_WORKERS_LOCK:
        if job_id in ACTIVE_DISCOVERY_WORKERS:
            return False
        ACTIVE_DISCOVERY_WORKERS.add(job_id)
    worker = threading.Thread(
        target=run_discovery_job,
        args=(job_id, params),
        name=f"discovery-{job_id[:8]}",
        daemon=True,
    )
    try:
        worker.start()
    except Exception:
        with ACTIVE_DISCOVERY_WORKERS_LOCK:
            ACTIVE_DISCOVERY_WORKERS.discard(job_id)
        raise
    return True


def discovery_params(payload: dict) -> dict[str, list[str]]:
    allowed_fields = {
        "planName",
        "scheduleId",
        "scheduleRunTime",
        "targetUsername",
        "scheduledForUsername",
        "distributionType",
        "goal",
        "country",
        "model",
        "sourceMode",
        "accountScope",
        "freshness",
        "searchDepth",
        "keywords",
        "cityFocus",
        "customerTypes",
        "exclusions",
        "resultLimit",
        "verificationLevel",
        "minSources",
    }
    return {
        key: [str(value)[:4000]]
        for key, value in payload.items()
        if key in allowed_fields and value is not None
    }


def discovery_payload_signature(payload: dict) -> str:
    normalized = {
        key: re.sub(r"\s+", " ", str(value)).strip().lower()
        for key, value in payload.items()
        if value is not None and str(value).strip()
    }
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def find_matching_active_discovery_job(payload: dict, owner_username: str) -> dict | None:
    target = discovery_payload_signature(payload)
    initialize_state_store()
    query = (
        "SELECT job_id, payload, status, stage, progress, message, result, error, "
        "imported, created_at, updated_at, owner_username FROM discovery_jobs "
        "WHERE status IN ('queued', 'running') AND owner_username = "
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query + "%s ORDER BY created_at DESC", (owner_username,))
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute(query + "? ORDER BY created_at DESC", (owner_username,)).fetchall()
    for row in rows:
        job = row_to_discovery_job(row)
        if discovery_payload_signature(job.get("payload") or {}) == target:
            return job
    return None


def count_active_discovery_jobs(owner_username: str) -> int:
    initialize_state_store()
    query = "SELECT COUNT(*) FROM discovery_jobs WHERE status IN ('queued', 'running') AND owner_username = "
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query + "%s", (owner_username,))
                row = cursor.fetchone()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            row = connection.execute(query + "?", (owner_username,)).fetchone()
    return int(row[0] if row else 0)


def create_discovery_job(
    payload: dict,
    owner_username: str,
    *,
    force: bool = False,
    assigned_by_admin: bool = False,
) -> dict:
    cleanup_discovery_jobs()
    params = discovery_params(payload)
    normalized_payload = {key: value[0] for key, value in params.items()}
    owner_user = get_user(owner_username)
    if owner_user and not assigned_by_admin:
        ensure_user_can_use_discovery_payload(owner_user, normalized_payload)
    with DISCOVERY_CREATE_LOCK:
        if not force:
            existing = find_matching_active_discovery_job(normalized_payload, owner_username)
            if existing:
                existing["reused"] = True
                return discovery_job_public(existing)
        active_count = count_active_discovery_jobs(owner_username)
        active_limit = MAX_ACTIVE_SCHEDULED_JOBS_PER_SALES if assigned_by_admin else MAX_ACTIVE_DISCOVERY_JOBS_PER_USER
        if active_count >= active_limit:
            raise ValueError(f"当前已有 {active_count} 个获客任务正在运行或排队，最多同时运行 {active_limit} 个。请等待任务完成后再启动新的任务。")
        job_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc)
        job = {
            "id": job_id,
            "payload": normalized_payload,
            "status": "queued",
            "stage": "search",
            "progress": 5,
            "message": "云端任务已创建，正在分配搜索资源。",
            "createdAt": now.isoformat(timespec="seconds"),
            "updatedAt": now.isoformat(timespec="seconds"),
            "result": None,
            "error": "",
            "imported": False,
            "ownerUsername": owner_username,
        }
        save_discovery_job(job)
        launch_discovery_worker(job_id, params)
    return discovery_job_public(job)


def get_discovery_job(job_id: str, owner_username: str | None = None) -> dict | None:
    cleanup_discovery_jobs()
    job = load_discovery_job(job_id, owner_username)
    return discovery_job_public(job) if job else None


def mark_discovery_job_imported(
    job_id: str,
    owner_username: str,
    imported_count: int | None = None,
    raw_count: int | None = None,
    skipped_count: int | None = None,
    skip_breakdown: dict | None = None,
) -> dict | None:
    job = load_discovery_job(job_id, owner_username)
    if not job:
        return None
    job["imported"] = True
    result = job.get("result") if isinstance(job.get("result"), dict) else {}
    if imported_count is not None:
        result["importedCount"] = max(
            max(0, int(result.get("importedCount") or 0)),
            max(0, int(imported_count)),
        )
    if raw_count is not None:
        result["rawCount"] = max(
            max(0, int(result.get("rawCount") or result.get("count") or 0)),
            max(0, int(raw_count)),
        )
    if skipped_count is not None:
        maximum_skipped = max(0, int(result.get("rawCount") or 0) - int(result.get("importedCount") or 0))
        result["skippedCount"] = min(maximum_skipped, max(0, int(skipped_count)))
    if isinstance(skip_breakdown, dict):
        allowed_skip_reasons = ("ineligible", "existing", "rejected", "duplicateWebsite")
        result["skipBreakdown"] = {
            reason: max(0, int(skip_breakdown.get(reason) or 0))
            for reason in allowed_skip_reasons
        }
    job["result"] = result
    job["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_discovery_job(job)
    return discovery_job_public(job)


def cancel_discovery_job(job_id: str, owner_username: str) -> dict | None:
    job = load_discovery_job(job_id, owner_username)
    if not job:
        return None
    if job.get("status") in {"queued", "running"}:
        update_discovery_job(
            job_id,
            status="canceled",
            stage="done",
            progress=100,
            message="任务已取消，后续搜索结果不会写入任务中心。",
            error="",
        )
    return get_discovery_job(job_id, owner_username)


def delete_discovery_job(job_id: str, owner_username: str) -> bool:
    job = load_discovery_job(job_id, owner_username)
    if not job:
        return False
    if job.get("status") in {"queued", "running"}:
        raise ValueError("运行中的任务请先取消，再删除")
    initialize_state_store()
    with DISCOVERY_JOBS_LOCK:
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM discovery_jobs WHERE job_id = %s AND owner_username = %s", (job_id, owner_username))
                    deleted = cursor.rowcount > 0
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                cursor = connection.execute(
                    "DELETE FROM discovery_jobs WHERE job_id = ? AND owner_username = ?",
                    (job_id, owner_username),
                )
                deleted = cursor.rowcount > 0
    return deleted


def resume_interrupted_discovery_jobs() -> int:
    initialize_state_store()
    query = (
        "SELECT job_id, payload, status, stage, progress, message, result, error, "
        "imported, created_at, updated_at, owner_username FROM discovery_jobs "
        "WHERE status IN ('queued', 'running') ORDER BY created_at"
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute(query).fetchall()
    resumed = 0
    for row in rows:
        job = row_to_discovery_job(row)
        update_discovery_job(
            job["id"],
            status="queued",
            stage="search",
            progress=max(5, min(int(job.get("progress", 5)), 10)),
            message="服务已恢复，正在重新接续云端获客任务。",
            error="",
        )
        if launch_discovery_worker(job["id"], discovery_params(job.get("payload") or {})):
            resumed += 1
    return resumed


COUNTRY_HINTS = {
    "UAE": (
        "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah",
        "Fujairah", "Umm Al Quwain", "Al Ain", "Jebel Ali", "Mussafah",
        "Deira", "Al Quoz", "Dubai Investment Park", "Jumeirah",
    ),
    "Saudi": (
        "Riyadh", "Jeddah", "Dammam", "Khobar", "Mecca", "Medina",
        "Dhahran", "Jubail", "Al Khobar", "Tabuk", "Taif", "Yanbu",
        "Al Qassim", "Buraydah", "Hofuf", "Abha",
    ),
    "Kazakhstan": (
        "Almaty", "Astana", "Aktau", "Shymkent", "Karaganda", "Atyrau",
        "Pavlodar", "Kostanay", "Aktobe", "Oskemen",
    ),
    "Russia": (
        "Moscow", "St. Petersburg", "Kazan", "Novosibirsk", "Yekaterinburg",
        "Nizhny Novgorod", "Samara", "Krasnodar", "Rostov-on-Don",
    ),
    "Qatar": (
        "Doha", "Al Rayyan", "Lusail", "Industrial Area", "Al Wakrah",
        "Umm Salal", "Al Khor", "Mesaieed",
    ),
    "Kuwait": (
        "Kuwait City", "Al Farwaniyah", "Hawally", "Salmiya", "Shuwaikh",
        "Fahaheel", "Ahmadi", "Jahra", "Ardiya", "Sabah Al Salem",
    ),
    "Uzbekistan": (
        "Tashkent", "Samarkand", "Bukhara", "Namangan", "Andijan",
        "Fergana", "Nukus", "Qarshi",
    ),
    "Azerbaijan": (
        "Baku", "Sumqayit", "Ganja", "Mingachevir", "Lankaran",
        "Shirvan", "Nakhchivan",
    ),
    "Nigeria": (
        "Lagos", "Abuja", "Port Harcourt", "Kano", "Ibadan", "Lekki",
        "Ikeja", "Victoria Island", "Apapa", "Benin City", "Aba",
        "Onitsha", "Enugu", "Kaduna", "Warri",
    ),
    "Ghana": (
        "Accra", "Kumasi", "Tema", "Takoradi", "East Legon", "Spintex",
        "Madina", "Ashaiman", "Tamale", "Cape Coast",
    ),
    "Algeria": (
        "Alger", "Algiers", "Oran", "Constantine", "Annaba", "Blida",
        "Setif", "Sétif", "Batna", "Tlemcen", "Bejaia", "Béjaïa",
        "Tizi Ouzou", "Boumerdes", "Boumerdès", "Ouargla", "Chlef",
        "Mostaganem", "Relizane", "Biskra", "Hassi Messaoud",
    ),
    "Côte d'Ivoire": (
        "Abidjan", "Yamoussoukro", "Bouaké", "Bouake",
        "San Pedro", "Daloa", "Korhogo",
    ),
    "Cote d'Ivoire": (
        "Abidjan", "Yamoussoukro", "Bouaké", "Bouake",
        "San Pedro", "Daloa", "Korhogo",
    ),
    "Ivory Coast": (
        "Abidjan", "Yamoussoukro", "Bouaké", "Bouake",
        "San Pedro", "Daloa", "Korhogo",
    ),
    "Egypt": (
        "Cairo", "Alexandria", "Giza", "6th of October City",
        "New Cairo", "Nasr City", "Mansoura", "Tanta",
        "Port Said", "Suez", "Ismailia", "Zagazig",
    ),
    "Kyrgyzstan": (
        "Bishkek", "Osh", "Jalal-Abad", "Karakol", "Tokmok",
        "Kara-Balta", "Naryn", "Batken",
    ),
    "Ethiopia": (
        "Addis Ababa", "Dire Dawa", "Bahir Dar", "Adama", "Hawassa",
        "Mekelle", "Gondar", "Jimma", "Dukem", "Bole",
    ),
    "Oman": (
        "Muscat", "Salalah", "Sohar", "Nizwa", "Seeb", "Barka",
        "Ruwi", "Muttrah", "Al Khuwair", "Sur", "Ibri", "Duqm",
    ),
    "Armenia": (
        "Yerevan", "Gyumri", "Vanadzor", "Abovyan", "Vagharshapat",
        "Armavir", "Artashat", "Hrazdan",
    ),
    "Belarus": ("Minsk", "Gomel", "Brest", "Vitebsk", "Grodno", "Mogilev", "Baranovichi"),
    "South Africa": (
        "Johannesburg", "Pretoria", "Cape Town", "Durban", "Gqeberha",
        "Bloemfontein", "East London", "Sandton", "Centurion",
    ),
    "Bahrain": ("Manama", "Riffa", "Muharraq", "Sitra", "Isa Town"),
    "Jordan": ("Amman", "Zarqa", "Irbid", "Aqaba", "Sahab"),
    "Georgia": ("Tbilisi", "Batumi", "Rustavi", "Kutaisi", "Poti"),
    "Vietnam": ("Ho Chi Minh City", "Hanoi", "Da Nang", "Hai Phong", "Can Tho"),
    "Philippines": ("Metro Manila", "Manila", "Quezon City", "Cebu", "Davao"),
    "Mexico": ("Mexico City", "Monterrey", "Guadalajara", "Puebla", "Querétaro"),
    "Brazil": ("São Paulo", "Rio de Janeiro", "Brasília", "Belo Horizonte", "Curitiba"),
    "Chile": ("Santiago", "Valparaíso", "Concepción", "Antofagasta", "Viña del Mar"),
    "Colombia": ("Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena"),
    "Argentina": ("Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata", "Mar del Plata"),
    "Peru": ("Lima", "Arequipa", "Trujillo", "Callao", "Chiclayo", "Cusco"),
    "Ecuador": ("Quito", "Guayaquil", "Cuenca", "Ambato", "Manta"),
    "Uruguay": ("Montevideo", "Canelones", "Maldonado", "Salto", "Paysandú"),
    "Paraguay": ("Asunción", "Ciudad del Este", "San Lorenzo", "Luque", "Capiatá"),
    "Morocco": ("Casablanca", "Rabat", "Tangier", "Marrakesh", "Agadir"),
    "China": (
        "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Hangzhou", "Chengdu",
        "Chongqing", "Wuhan", "Nanjing", "Suzhou", "Tianjin", "Xi'an",
        "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "武汉",
    ),
}

CHINA_DOMESTIC_REGIONS = {
    "全国": (
        "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "武汉",
        "南京", "苏州", "天津", "西安",
    ),
    "华北": ("北京", "天津", "石家庄", "太原", "呼和浩特", "河北", "山西", "内蒙古"),
    "华东": ("上海", "杭州", "南京", "苏州", "宁波", "合肥", "济南", "福州", "浙江", "江苏", "山东"),
    "华南": ("广州", "深圳", "佛山", "东莞", "南宁", "海口", "广东", "广西", "海南"),
    "华中": ("武汉", "长沙", "郑州", "湖北", "湖南", "河南"),
    "西南": ("成都", "重庆", "昆明", "贵阳", "拉萨", "四川", "云南", "贵州", "西藏"),
    "西北": ("西安", "兰州", "银川", "西宁", "乌鲁木齐", "陕西", "甘肃", "青海", "宁夏", "新疆"),
    "东北": ("沈阳", "大连", "长春", "哈尔滨", "辽宁", "吉林", "黑龙江"),
}

DISCOVERY_KEYWORD_TERMS = (
    "car dealer",
    "auto dealer",
    "automotive dealer",
    "car showroom",
    "auto showroom",
    "motors",
    "motor company",
    "vehicle dealer",
    "vehicle showroom",
    "used cars",
    "new cars",
    "luxury cars",
    "electric vehicles",
    "EV dealer",
    "Chinese cars",
    "Chinese EV",
    "SUV dealer",
    "import cars",
    "car importer",
    "vehicle importer",
    "auto trading",
    "automotive trading",
    "general trading cars",
    "parallel import cars",
    "car export",
    "vehicle export",
    "car distributor",
    "vehicle distributor",
    "authorized dealer",
    "exclusive distributor",
    "dealer network",
    "fleet vehicles",
    "fleet sales",
    "corporate fleet",
    "car rental fleet",
    "chauffeur fleet",
    "commercial vehicles",
    "vehicle procurement",
    "pre owned cars",
    "automobile distributor",
)

SOCIAL_HIGH_INTENT_TERMS = (
    "car dealer",
    "used car dealer",
    "car showroom",
    "motors showroom",
    "auto trading",
    "automotive trading",
    "car importer",
    "vehicle importer",
    "parallel import cars",
    "car export",
    "vehicle export",
    "car distributor",
    "vehicle distributor",
    "fleet vehicle supplier",
    "luxury car showroom",
    "new energy vehicle dealer",
    "electric vehicle dealer",
    "Chinese EV dealer",
    "Chinese car importer",
    "Chinese vehicle distributor",
    "AITO dealer",
    "Huawei AITO",
    "Huawei car",
    "HIMA car",
    "BYD dealer",
    "Denza dealer",
    "Zeekr dealer",
)

OBVIOUS_IRRELEVANT_LEAD_PATTERNS = (
    r"\b(cgtn|china global television|news channel|news network|television network|tv network|broadcasting|"
    r"newsroom|journalist|newspaper|magazine|media outlet|press agency|public radio|radio station|"
    r"political news|world news|breaking news|current affairs)\b",
    r"\b(media project|media-project|human rights media|rights media|tv|телеканал|телевидение|"
    r"новости|журналист|газета|сми|медиа|правозащитный|прецедент)\b",
    r"\b(towing|tow truck|roadside assistance|vehicle recovery|car recovery|breakdown service|wrecker)\b",
    r"\b(tax consultant|tax consultancy|vat consultant|vat consultancy|tax agent|tax filing|tax refund)\b",
    r"\b(tax free|duty free|excise tax|corporate tax|customs clearance|customs broker)\b",
    r"\b(company formation|business setup|free zone license|trade license|pro services|visa services)\b",
    r"\b(accounting|bookkeeping|audit firm|auditing|attestation|document clearing)\b",
    r"\b(auto repair|car repair|vehicle repair|repair shop|repair workshop|auto workshop|car workshop)\b",
    r"\b(service center|service centre|maintenance|mechanic|garage|body shop|paint shop|collision repair)\b",
    r"\b(car wash|auto wash|detailing|car detailing|window tint|wrapping|car wrap|ceramic coating)\b",
    r"\b(tyre|tyres|tire|tires|battery replacement|oil change|spare parts|auto parts|car parts)\b",
    r"\b(podcast|disruptors|wealth|money matrix|financial freedom|crypto|bitcoin|trading course)\b",
    r"\b(motivational speaker|business coach|life coach|influencer|youtuber|vlogger|vlogs?)\b",
    r"\b(travel vlog|travel world|food and tours|meals with|gaming|fitness|boxing|mma|politics)\b",
    r"\b(media production|video production|tv channel|music channel|comedy channel)\b",
    r"\b(real russia uncovered|walks life girls|dubai life|life xl|far from kerala|mr'?s kitchen)\b",
    r"(维修|修理|保养|汽修|洗车|汽车美容|贴膜|轮胎|配件|钣金|喷漆)",
)

CITY_COORDS = {
    "UAE": ("Dubai", 25.2048, 55.2708),
    "Saudi": ("Riyadh", 24.7136, 46.6753),
    "Kazakhstan": ("Almaty", 43.2389, 76.8897),
    "Russia": ("Moscow", 55.7558, 37.6173),
    "Qatar": ("Doha", 25.2854, 51.5310),
    "Kuwait": ("Kuwait City", 29.3759, 47.9774),
    "Uzbekistan": ("Tashkent", 41.2995, 69.2401),
    "Azerbaijan": ("Baku", 40.4093, 49.8671),
    "Nigeria": ("Lagos", 6.5244, 3.3792),
    "Ghana": ("Accra", 5.6037, -0.1870),
    "Algeria": ("Algiers", 36.7538, 3.0588),
    "Côte d'Ivoire": ("Abidjan", 5.3600, -4.0083),
    "Cote d'Ivoire": ("Abidjan", 5.3600, -4.0083),
    "Ivory Coast": ("Abidjan", 5.3600, -4.0083),
    "Egypt": ("Cairo", 30.0444, 31.2357),
    "Kyrgyzstan": ("Bishkek", 42.8746, 74.5698),
    "Ethiopia": ("Addis Ababa", 8.9806, 38.7578),
    "Oman": ("Muscat", 23.5880, 58.3829),
    "Armenia": ("Yerevan", 40.1792, 44.4991),
    "Belarus": ("Minsk", 53.9006, 27.5590),
    "South Africa": ("Johannesburg", -26.2041, 28.0473),
    "Bahrain": ("Manama", 26.2235, 50.5876),
    "Jordan": ("Amman", 31.9539, 35.9106),
    "Georgia": ("Tbilisi", 41.7151, 44.8271),
    "Vietnam": ("Ho Chi Minh City", 10.8231, 106.6297),
    "Philippines": ("Metro Manila", 14.5995, 120.9842),
    "Mexico": ("Mexico City", 19.4326, -99.1332),
    "Brazil": ("São Paulo", -23.5505, -46.6333),
    "Chile": ("Santiago", -33.4489, -70.6693),
    "Colombia": ("Bogotá", 4.7110, -74.0721),
    "Argentina": ("Buenos Aires", -34.6037, -58.3816),
    "Peru": ("Lima", -12.0464, -77.0428),
    "Ecuador": ("Quito", -0.1807, -78.4678),
    "Uruguay": ("Montevideo", -34.9011, -56.1645),
    "Paraguay": ("Asunción", -25.2637, -57.5759),
    "Morocco": ("Casablanca", 33.5731, -7.5898),
    "China": ("Shanghai", 31.2304, 121.4737),
}

OSM_SEARCH_CENTERS = {
    "Nigeria": (
        ("Lagos", 6.5244, 3.3792),
        ("Abuja", 9.0765, 7.3986),
        ("Port Harcourt", 4.8156, 7.0498),
        ("Kano", 12.0022, 8.5920),
        ("Ibadan", 7.3775, 3.9470),
        ("Benin City", 6.3350, 5.6037),
    ),
}

OVERPASS_API_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)

COUNTRY_SEARCH_META = {
    "China": {
        "code": "cn",
        "location": "China",
        "google_domain": "google.com",
        "aliases": (
            "China", "中国", "Mainland China", "PRC", "Beijing", "Shanghai", "Guangzhou", "Shenzhen",
            "Hangzhou", "Chengdu", "Chongqing", "Wuhan", "Nanjing", "Suzhou", "Tianjin", "Xi'an",
            "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "武汉", "南京", "苏州", "天津", "西安",
            "华北", "华东", "华南", "华中", "西南", "西北", "东北", "全国",
            "河北", "山西", "内蒙古", "江苏", "浙江", "安徽", "福建", "江西", "山东", "广东", "广西",
            "海南", "河南", "湖北", "湖南", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海",
            "宁夏", "新疆", "辽宁", "吉林", "黑龙江",
        ),
    },
    "UAE": {
        "code": "ae",
        "location": "United Arab Emirates",
        "google_domain": "google.ae",
        "aliases": ("UAE", "United Arab Emirates", "Emirates", "Dubai", "Abu Dhabi", "Sharjah", "Ajman"),
    },
    "Saudi": {
        "code": "sa",
        "location": "Saudi Arabia",
        "google_domain": "google.com.sa",
        "aliases": ("Saudi", "Saudi Arabia", "Riyadh", "Jeddah", "Dammam", "Khobar"),
    },
    "Kazakhstan": {
        "code": "kz",
        "location": "Kazakhstan",
        "google_domain": "google.kz",
        "aliases": ("Kazakhstan", "Almaty", "Astana", "Aktau"),
    },
    "Russia": {
        "code": "ru",
        "location": "Russia",
        "google_domain": "google.ru",
        "aliases": ("Russia", "Russian Federation", "Moscow", "St. Petersburg", "Kazan", "автосалон"),
    },
    "Qatar": {
        "code": "qa",
        "location": "Qatar",
        "google_domain": "google.com.qa",
        "aliases": ("Qatar", "Doha"),
    },
    "Kuwait": {
        "code": "kw",
        "location": "Kuwait",
        "google_domain": "google.com.kw",
        "aliases": ("Kuwait", "Kuwait City"),
    },
    "Uzbekistan": {
        "code": "uz",
        "location": "Uzbekistan",
        "google_domain": "google.co.uz",
        "aliases": ("Uzbekistan", "Tashkent"),
    },
    "Azerbaijan": {
        "code": "az",
        "location": "Azerbaijan",
        "google_domain": "google.az",
        "aliases": ("Azerbaijan", "Baku"),
    },
    "Nigeria": {
        "code": "ng",
        "location": "Nigeria",
        "google_domain": "google.com.ng",
        "aliases": ("Nigeria", "Lagos", "Abuja", "Port Harcourt", "Kano"),
    },
    "Ghana": {
        "code": "gh",
        "location": "Ghana",
        "google_domain": "google.com.gh",
        "aliases": ("Ghana", "Accra", "Kumasi", "Tema"),
    },
    "Algeria": {
        "code": "dz",
        "location": "Algeria",
        "google_domain": "google.dz",
        "aliases": (
            "Algeria", "Algérie", "Algerie", "Alger", "Algiers", "Oran",
            "Constantine", "الجزائر", "+213", ".dz",
        ),
    },
    "Côte d'Ivoire": {
        "code": "ci",
        "location": "Côte d'Ivoire",
        "google_domain": "google.ci",
        "aliases": ("Côte d'Ivoire", "Cote d'Ivoire", "Ivory Coast", "Abidjan", "Yamoussoukro"),
    },
    "Egypt": {
        "code": "eg",
        "location": "Egypt",
        "google_domain": "google.com.eg",
        "aliases": (
            "Egypt", "Cairo", "Alexandria", "Giza", "6th of October City",
            "New Cairo", "Nasr City", "Mansoura", "Tanta",
            "Port Said", "Suez", "Ismailia", "Zagazig",
        ),
    },
    "Kyrgyzstan": {
        "code": "kg",
        "location": "Kyrgyzstan",
        "google_domain": "google.kg",
        "aliases": ("Kyrgyzstan", "Bishkek", "Osh", "Kyrgyz Republic"),
    },
    "Ethiopia": {
        "code": "et",
        "location": "Ethiopia",
        "google_domain": "google.com.et",
        "aliases": ("Ethiopia", "Addis Ababa", "Dire Dawa"),
    },
    "Oman": {
        "code": "om",
        "location": "Oman",
        "google_domain": "google.com.om",
        "aliases": ("Oman", "Muscat", "Salalah", "Sohar"),
    },
    "Armenia": {
        "code": "am",
        "location": "Armenia",
        "google_domain": "google.am",
        "aliases": ("Armenia", "Yerevan", "Gyumri"),
    },
    "Belarus": {
        "code": "by", "location": "Belarus", "google_domain": "google.by",
        "aliases": ("Belarus", "Minsk", "Gomel", "Brest", "Vitebsk", "Беларусь", "Минск", "+375", ".by"),
    },
    "South Africa": {
        "code": "za", "location": "South Africa", "google_domain": "google.co.za",
        "aliases": ("South Africa", "RSA", "Johannesburg", "Pretoria", "Cape Town", "Durban", "Gauteng", "+27", ".za"),
    },
    "Bahrain": {
        "code": "bh",
        "location": "Bahrain",
        "google_domain": "google.com.bh",
        "aliases": ("Bahrain", "Manama", "Riffa", "Muharraq"),
    },
    "Jordan": {
        "code": "jo",
        "location": "Jordan",
        "google_domain": "google.jo",
        "aliases": ("Jordan", "Amman", "Zarqa", "Irbid", "Aqaba"),
    },
    "Georgia": {
        "code": "ge",
        "location": "Georgia",
        "google_domain": "google.ge",
        "aliases": ("Georgia", "Tbilisi", "Batumi", "Rustavi", "Kutaisi"),
    },
    "Vietnam": {
        "code": "vn",
        "location": "Vietnam",
        "google_domain": "google.com.vn",
        "aliases": ("Vietnam", "Viet Nam", "Ho Chi Minh City", "Hanoi", "Da Nang"),
    },
    "Philippines": {
        "code": "ph",
        "location": "Philippines",
        "google_domain": "google.com.ph",
        "aliases": ("Philippines", "Metro Manila", "Manila", "Cebu", "Davao"),
    },
    "Mexico": {
        "code": "mx",
        "location": "Mexico",
        "google_domain": "google.com.mx",
        "aliases": ("Mexico", "México", "Mexico City", "Monterrey", "Guadalajara"),
    },
    "Brazil": {
        "code": "br",
        "location": "Brazil",
        "google_domain": "google.com.br",
        "aliases": ("Brazil", "Brasil", "São Paulo", "Rio de Janeiro", "Brasília"),
    },
    "Chile": {
        "code": "cl",
        "location": "Chile",
        "google_domain": "google.cl",
        "aliases": ("Chile", "Santiago", "Valparaíso", "Concepción"),
    },
    "Colombia": {
        "code": "co",
        "location": "Colombia",
        "google_domain": "google.com.co",
        "aliases": ("Colombia", "Bogotá", "Medellín", "Cali", "Barranquilla"),
    },
    "Argentina": {
        "code": "ar", "location": "Argentina", "google_domain": "google.com.ar",
        "aliases": ("Argentina", "Buenos Aires", "Córdoba", "Rosario", "Mendoza", "+54", ".ar"),
    },
    "Peru": {
        "code": "pe", "location": "Peru", "google_domain": "google.com.pe",
        "aliases": ("Peru", "Perú", "Lima", "Arequipa", "Trujillo", "Callao", "+51", ".pe"),
    },
    "Ecuador": {
        "code": "ec", "location": "Ecuador", "google_domain": "google.com.ec",
        "aliases": ("Ecuador", "Quito", "Guayaquil", "Cuenca", "Ambato", "+593", ".ec"),
    },
    "Uruguay": {
        "code": "uy", "location": "Uruguay", "google_domain": "google.com.uy",
        "aliases": ("Uruguay", "Montevideo", "Canelones", "Maldonado", "+598", ".uy"),
    },
    "Paraguay": {
        "code": "py", "location": "Paraguay", "google_domain": "google.com.py",
        "aliases": ("Paraguay", "Asunción", "Ciudad del Este", "San Lorenzo", "Luque", "+595", ".py"),
    },
    "Morocco": {
        "code": "ma",
        "location": "Morocco",
        "google_domain": "google.co.ma",
        "aliases": ("Morocco", "Maroc", "Casablanca", "Rabat", "Tangier"),
    },
}

LOCAL_DISCOVERY_SOURCES = {
    "China": (
        ("Baidu Search", "baidu.com"),
        ("Baidu Maps", "map.baidu.com"),
        ("Amap", "amap.com"),
        ("Aiqicha", "aiqicha.baidu.com"),
        ("Qichacha", "qcc.com"),
        ("Tianyancha", "tianyancha.com"),
        ("1688", "1688.com"),
        ("Autohome Dealer", "dealer.autohome.com.cn"),
        ("Yiche Dealer", "dealer.yiche.com"),
        ("Dongchedi", "dongchedi.com"),
        ("Sohu Auto", "auto.sohu.com"),
    ),
    "UAE": (
        ("DubiCars", "dubicars.com"),
        ("YallaMotor UAE", "uae.yallamotor.com"),
        ("Dubizzle UAE", "dubizzle.com"),
        ("DriveArabia UAE", "drivearabia.com"),
        ("CarSwitch UAE", "carswitch.com"),
    ),
    "Saudi": (
        ("Motory Saudi", "motory.com"),
        ("Syarah", "syarah.com"),
        ("Haraj", "haraj.com.sa"),
        ("SaudiSale", "saudisale.com"),
        ("OpenSooq Saudi", "sa.opensooq.com"),
        ("Dubizzle Saudi", "dubizzle.sa"),
    ),
    "Kazakhstan": (
        ("Kolesa Kazakhstan", "kolesa.kz"),
        ("Market Kazakhstan", "market.kz"),
        ("OLX Kazakhstan", "olx.kz"),
        ("Mycar Kazakhstan", "mycar.kz"),
        ("Aster Kazakhstan", "aster.kz"),
        ("Bazar Kazakhstan", "bazar.kz"),
    ),
    "Russia": (
        ("Auto.ru", "auto.ru"),
        ("Drom", "drom.ru"),
        ("Avito Auto", "avito.ru"),
        ("Drive2 Russia", "drive2.ru"),
        ("Youla Auto", "youla.ru"),
    ),
    "Qatar": (
        ("QatarSale", "qatarsale.com"),
        ("Mzad Qatar", "mzadqatar.com"),
        ("Qatar Living", "qatarliving.com"),
        ("QMotor", "qmotor.com"),
        ("Qatar YallaMotor", "qatar.yallamotor.com"),
        ("Hatla2ee Qatar", "qatar.hatla2ee.com"),
        ("AutoBeeb Qatar", "autobeeb.com"),
    ),
    "Kuwait": (
        ("Q8Car", "q8car.com"),
        ("4Sale Kuwait", "q84sale.com"),
        ("OpenSooq Kuwait", "kw.opensooq.com"),
        ("Kuwait YallaMotor", "kuwait.yallamotor.com"),
        ("Dubizzle Kuwait", "dubizzle.com.kw"),
        ("Hatla2ee Kuwait", "kuwait.hatla2ee.com"),
        ("Motorgy Kuwait", "motorgy.com"),
        ("iCartea Kuwait", "kuwait.icartea.com"),
    ),
    "Uzbekistan": (
        ("Avtoelon", "avtoelon.uz"),
        ("OLX Uzbekistan", "olx.uz"),
        ("Avto Uzbekistan", "avto.uz"),
        ("AutoUzbek", "autouzbek.com"),
    ),
    "Azerbaijan": (
        ("Turbo.az", "turbo.az"),
        ("Tap.az", "tap.az"),
        ("AvtoBaku", "avtobaku.com"),
        ("Auto.az Azerbaijan", "auto.az"),
    ),
    "Nigeria": (
        ("Jiji Nigeria", "jiji.ng"),
        ("Cars45", "cars45.com"),
        ("Autochek Nigeria", "autochek.africa"),
        ("Cheki Nigeria", "cheki.com.ng"),
        ("Betacar Nigeria", "betacar.ng"),
        ("BuyCars Nigeria", "buycars.ng"),
    ),
    "Ghana": (
        ("Tonaton", "tonaton.com"),
        ("Jiji Ghana", "jiji.com.gh"),
        ("Autochek Ghana", "autochek.africa"),
        ("AutoTrader Ghana", "autotrader.com.gh"),
        ("Cars45 Ghana", "cars45.com.gh"),
    ),
    "Algeria": (
        ("Ouedkniss", "ouedkniss.com"),
        ("Autobip Algeria", "autobip.com"),
        ("Pages Jaunes Algérie", "pagesjaunes-dz.com"),
        ("El Mouchir CACI", "elmouchir.caci.dz"),
        ("Tidjara Algérie", "tidjara.dz"),
        ("Annuaires DZ", "annuairesdz.com"),
        ("Go Africa Online Algérie", "goafricaonline.com"),
        ("Vitamin DZ Annuaire", "vitaminedz.com"),
        ("Algérie Annonces", "algerieannonces.com"),
        ("ElSayara Algérie", "elsayara.com"),
        ("Tonobiles", "tonobiles.com"),
        ("Hanoutkoum", "hanoutkoum.com"),
        ("AutoDZ", "autodz.com"),
        ("AutoBeeb Algeria", "autobeeb.com"),
        ("OpenSooq Algeria", "dz.opensooq.com"),
        ("DZ Auto Market", "dz-auto.store"),
    ),
    "Côte d'Ivoire": (
        ("Auto24 Cote d'Ivoire", "auto24.ci"),
        ("CoinAfrique Cote d'Ivoire", "ci.coinafrique.com"),
        ("Afribaba Cote d'Ivoire", "afribaba.ci"),
        ("Voitures Cote d'Ivoire", "voitures.ci"),
    ),
    "Cote d'Ivoire": (
        ("Auto24 Cote d'Ivoire", "auto24.ci"),
        ("CoinAfrique Cote d'Ivoire", "ci.coinafrique.com"),
        ("Afribaba Cote d'Ivoire", "afribaba.ci"),
        ("Voitures Cote d'Ivoire", "voitures.ci"),
    ),
    "Ivory Coast": (
        ("Auto24 Cote d'Ivoire", "auto24.ci"),
        ("CoinAfrique Cote d'Ivoire", "ci.coinafrique.com"),
        ("Afribaba Cote d'Ivoire", "afribaba.ci"),
        ("Voitures Cote d'Ivoire", "voitures.ci"),
    ),
    "Egypt": (
        ("ContactCars", "contactcars.com"),
        ("Hatla2ee Egypt", "eg.hatla2ee.com"),
        ("Dubizzle Egypt", "dubizzle.com.eg"),
        ("YallaMotor Egypt", "egypt.yallamotor.com"),
    ),
    "Kyrgyzstan": (
        ("Mashina KG", "mashina.kg"),
        ("Cars KG", "cars.kg"),
        ("Lalafo KG", "lalafo.kg"),
        ("AutoKyrgyz", "autokyrgyz.com"),
        ("Bazar KG", "bazar.kg"),
    ),
    "Ethiopia": (
        ("Jiji Ethiopia", "jiji.com.et"),
        ("Qefira Ethiopia", "qefira.com"),
        ("AddisMercato", "addismercato.com"),
        ("YeneF1 Ethiopia", "yenef1.com"),
        ("Mekina Ethiopia", "mekina.net"),
        ("Cars45 Ethiopia", "cars45et.com"),
        ("Megebeya Ethiopia", "megebeya.com"),
        ("AfroMekina", "afromekina.com"),
    ),
    "Oman": (
        ("OpenSooq Oman", "om.opensooq.com"),
        ("Dubizzle Oman", "dubizzle.com.om"),
        ("Oman YallaMotor", "oman.yallamotor.com"),
        ("AutoBeeb Oman", "autobeeb.com"),
        ("Hatla2ee Oman", "oman.hatla2ee.com"),
        ("OmaniCar", "omanicar.com"),
    ),
    "Armenia": (
        ("List.am", "list.am"),
        ("Auto.am", "auto.am"),
        ("MyAuto Armenia", "myauto.am"),
        ("Autopapa Caucasus", "autopapa.com"),
    ),
    "Belarus": (
        ("AV.BY", "av.by"), ("ABW.BY", "abw.by"), ("Onliner Auto", "onliner.by"),
    ),
    "South Africa": (
        ("AutoTrader South Africa", "autotrader.co.za"), ("Cars.co.za", "cars.co.za"),
        ("WeBuyCars", "webuycars.co.za"), ("Carfind", "carfind.co.za"),
    ),
    "Bahrain": (
        ("Bahrain Auto Trader Dealers", "bahrainautotrader.com"),
        ("Click Bahrain Car Dealers", "clickbahrain.com"),
        ("Motors Souq Bahrain", "motorssouq.com"),
        ("Bahrain Cars BH", "bahraincarsbh.com"),
        ("OpenSooq Bahrain", "bh.opensooq.com"),
    ),
    "Jordan": (
        ("Ordon Auto", "ordonauto.com"),
        ("AutoBeeb Jordan Dealers", "autobeeb.com"),
        ("MotorX Jordan", "motorx.app"),
        ("OpenSooq Jordan", "jo.opensooq.com"),
    ),
    "Georgia": (
        ("MyAuto Georgia", "myauto.ge"),
        ("AutoPapa Georgia", "autopapa.ge"),
        ("Manqanebi Georgia", "manqanebi.ge"),
        ("Auto.ge", "auto.ge"),
    ),
    "Vietnam": (
        ("Vucar Showroom Directory", "vucar.vn"),
        ("Oto.com.vn Showrooms", "oto.com.vn"),
        ("Bonbanh", "bonbanh.com"),
        ("Cho Tot Xe", "chotot.com"),
    ),
    "Philippines": (
        ("Philippines Auto Dealers Directory", "philippines.tv"),
        ("AutoDeal Philippines", "autodeal.com.ph"),
        ("Philkotse", "philkotse.com"),
        ("Philmotors", "philmotors.com"),
        ("Manila Carlist", "manilacarlist.com"),
    ),
    "Mexico": (
        ("Zona Auto Dealer Directory", "zonaauto.com.mx"),
        ("Autocosmos Mexico", "autocosmos.com.mx"),
        ("Seminuevos Mexico", "seminuevos.com"),
        ("SoloAutos Mexico", "soloautos.mx"),
        ("Kavak Mexico", "kavak.com"),
    ),
    "Brazil": (
        ("Webmotors", "webmotors.com.br"),
        ("iCarros", "icarros.com.br"),
        ("Autoscar Lojas", "autoscar.com.br"),
        ("Seminovos Brazil", "seminovos.com.br"),
        ("SoCarrao", "socarrao.com.br"),
    ),
    "Chile": (
        ("Chileautos", "chileautos.cl"),
        ("Automotores Chile", "automotores.cl"),
        ("Yapo Autos", "yapo.cl"),
        ("Autocosmos Chile", "autocosmos.cl"),
        ("Mercado Libre Chile", "mercadolibre.cl"),
    ),
    "Colombia": (
        ("TuCarro Colombia", "tucarro.com.co"),
        ("CarroYa", "carroya.com"),
        ("Autocosmos Colombia", "autocosmos.com.co"),
        ("Mercado Libre Colombia", "mercadolibre.com.co"),
    ),
    "Argentina": (
        ("Autocosmos Argentina", "autocosmos.com.ar"), ("Mercado Libre Argentina", "mercadolibre.com.ar"),
        ("DeAutos", "deautos.com"),
    ),
    "Peru": (
        ("NeoAuto", "neoauto.com"), ("Autocosmos Peru", "autocosmos.com.pe"),
        ("Mercado Libre Peru", "mercadolibre.com.pe"),
    ),
    "Ecuador": (
        ("Patiotuerca", "patiotuerca.com"), ("Autocosmos Ecuador", "autocosmos.com.ec"),
        ("Mercado Libre Ecuador", "mercadolibre.com.ec"),
    ),
    "Uruguay": (
        ("Autocosmos Uruguay", "autocosmos.com.uy"), ("Gallito", "gallito.com.uy"),
        ("Mercado Libre Uruguay", "mercadolibre.com.uy"),
    ),
    "Paraguay": (
        ("Clasipar", "clasipar.com"), ("Hendyla", "hendyla.com"),
        ("Mercado Libre Paraguay", "mercadolibre.com.py"),
    ),
    "Morocco": (
        ("O'Voiture Dealer Directory", "ovoiture.ma"),
        ("Wandaloo Dealers", "wandaloo.com"),
        ("Moteur.ma", "moteur.ma"),
        ("Avito Morocco", "avito.ma"),
        ("Autera Morocco", "autera.ma"),
    ),
}


LOCAL_AUTOMOTIVE_INTENT_TERMS = {
    "ae": ("car dealer showroom", "معرض سيارات", "تجارة السيارات"),
    "sa": ("car dealer showroom", "معرض سيارات", "بيع سيارات مستعملة"),
    "kz": ("автосалон", "автодилер", "продажа автомобилей"),
    "ru": ("автосалон", "автодилер", "автомобили в продаже"),
    "qa": ("car dealer showroom", "معرض سيارات", "بيع وشراء السيارات"),
    "kw": ("car dealer showroom", "معرض سيارات", "سيارات للبيع"),
    "uz": ("avtosalon", "avtomobil sotish", "автосалон"),
    "az": ("avtosalon", "avtomobil satışı", "avtomobil dileri"),
    "ng": ("car dealer showroom", "tokunbo car dealer", "vehicle importer"),
    "gh": ("car dealer showroom", "home used cars dealer", "vehicle importer"),
    "dz": ("concessionnaire automobile", "showroom automobile", "vente voitures occasion"),
    "ci": ("concessionnaire automobile", "vente voiture", "importateur automobile"),
    "eg": ("car dealer showroom", "معرض سيارات", "تجارة السيارات"),
    "kg": ("автосалон", "автодилер", "продажа автомобилей"),
    "et": ("car dealer Addis Ababa", "vehicle importer", "automotive trading company"),
    "om": ("car dealer showroom", "معرض سيارات", "تجارة السيارات"),
    "am": ("ավտոսրահ", "ավտոմեքենաների վաճառք", "автосалон"),
    "by": ("автосалон", "автодилер", "продажа автомобилей", "авто из Китая"),
    "za": ("car dealer showroom", "used car dealership", "vehicle importer", "fleet vehicle supplier"),
    "bh": ("car dealer showroom", "معرض سيارات", "بيع السيارات"),
    "jo": ("car dealer showroom", "معرض سيارات", "تجارة السيارات"),
    "ge": ("ავტოსალონი", "ავტომობილების გაყიდვა", "car dealer Tbilisi"),
    "vn": ("đại lý ô tô", "showroom ô tô", "mua bán xe ô tô"),
    "ph": ("car dealer showroom", "used car dealership", "vehicle importer"),
    "mx": ("agencia de autos", "concesionario de automóviles", "venta de autos usados"),
    "br": ("concessionária de veículos", "loja de carros", "revenda de seminovos"),
    "cl": ("automotora", "concesionario de autos", "venta de autos usados"),
    "co": ("concesionario de carros", "compraventa de vehículos", "venta de carros usados"),
    "ar": ("concesionario de autos", "agencia de autos", "venta de autos usados", "importador de vehículos"),
    "pe": ("concesionario de autos", "venta de autos usados", "importador de vehículos"),
    "ec": ("concesionario de vehículos", "patio de autos", "venta de autos usados"),
    "uy": ("automotora", "concesionario de autos", "venta de autos usados"),
    "py": ("playa de autos", "concesionario de vehículos", "venta de autos usados"),
    "ma": ("concessionnaire automobile", "vente voiture occasion", "معرض سيارات"),
}

FOREIGN_LOCATION_BLOCKERS = (
    "united states", "usa", "u.s.", "america", "california", "florida",
    "texas", "new york", "los angeles", "chicago", "houston", "miami",
    "dallas", "atlanta", "new jersey", "washington", "ohio", "illinois",
    "canada", "united kingdom", "uk", "australia",
)


def normalize_country_match_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return ascii_text.lower().replace("?", "o")


def country_search_meta(country: str) -> dict:
    text = normalize_country_match_text(country)
    for key, value in COUNTRY_SEARCH_META.items():
        aliases = (key, value.get("location", ""), *(value.get("aliases") or ()))
        if any((token := normalize_country_match_text(alias)) and token in text for alias in aliases):
            return value
    return COUNTRY_SEARCH_META["UAE"]


def target_country_aliases(country: str) -> tuple[str, ...]:
    meta = country_search_meta(country)
    aliases = [str(country or "").split(" ")[0], meta["location"], *meta["aliases"]]
    country_text = normalize_country_match_text(" ".join(str(alias) for alias in aliases))
    for key, hints in COUNTRY_HINTS.items():
        hint_meta = COUNTRY_SEARCH_META.get(key, {})
        match_aliases = (key, hint_meta.get("location", ""), *(hint_meta.get("aliases") or ()))
        if any((token := normalize_country_match_text(alias)) and token in country_text for alias in match_aliases):
            aliases.extend(hints)
            break
    return tuple(dict.fromkeys(alias for alias in aliases if alias))


def local_discovery_sources(country: str) -> tuple[tuple[str, str], ...]:
    meta = country_search_meta(country)
    candidates = [str(country or "").split(" ")[0], meta.get("location", "")]
    candidates.extend(meta.get("aliases") or ())
    for key, sources in LOCAL_DISCOVERY_SOURCES.items():
        key_text = normalize_country_match_text(key)
        if any(key_text and key_text in normalize_country_match_text(candidate) for candidate in candidates):
            return sources
    return ()


def local_discovery_domains() -> set[str]:
    domains: set[str] = set()
    for sources in LOCAL_DISCOVERY_SOURCES.values():
        for _, domain in sources:
            domains.add(str(domain).lower().removeprefix("www."))
    return domains


def has_target_country_signal(text: str, country: str) -> bool:
    value = normalize_country_match_text(text)
    return any((alias_text := normalize_country_match_text(alias)) and alias_text in value for alias in target_country_aliases(country))


def supported_foreign_location_signal(text: str, country: str) -> str:
    value = normalize_country_match_text(text)
    if not value or has_target_country_signal(value, country):
        return ""
    target_meta = country_search_meta(country)
    target_code = target_meta.get("code", "")
    for meta_country, meta in COUNTRY_SEARCH_META.items():
        if meta.get("code") == target_code:
            continue
        aliases = (meta_country, meta.get("location", ""), *(meta.get("aliases") or ()))
        for alias in aliases:
            alias_text = normalize_country_match_text(alias)
            if len(alias_text) >= 4 and alias_text in value:
                return alias
    return ""


def has_foreign_location_conflict(text: str, country: str) -> bool:
    value = normalize_country_match_text(text)
    if not value:
        return False
    if has_target_country_signal(value, country):
        return False
    return any(blocker in value for blocker in FOREIGN_LOCATION_BLOCKERS) or bool(supported_foreign_location_signal(value, country))


def is_vehicle_listing_url(url: str) -> bool:
    parsed = safe_urlparse(normalize_public_url(url))
    path = parsed.path.lower()
    if not parsed.netloc or not path:
        return False
    return bool(re.search(r"/(?:cars?|autos?|vehicles?)/[^/]+/[^/]+/", path))


def site_root_url(url: str) -> str:
    parsed = safe_urlparse(normalize_public_url(url))
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}/"


def raw_result_identity(item: dict) -> str:
    url = normalize_public_url(
        item.get("customer_website")
        or item.get("source_url")
        or item.get("url")
        or ""
    )
    if not url:
        return re.sub(r"[^a-z0-9]+", "", str(item.get("title") or "").lower())
    if is_social_profile_url(url) or is_vehicle_listing_url(url):
        return normalize_public_url(url).lower().split("#", 1)[0].rstrip("/")
    parsed = safe_urlparse(url)
    path = parsed.path.strip("/").lower()
    root = f"{parsed.scheme}://{parsed.netloc.lower().removeprefix('www.')}/"
    if not path or path in {"about", "about-us", "contact", "contact-us", "home", "index.html"}:
        return root
    return normalize_public_url(url).lower().split("#", 1)[0].rstrip("/")


def filter_raw_results_for_country_and_duplicates(raw_results: list[dict], country: str) -> list[dict]:
    kept: list[dict] = []
    seen: set[str] = set()
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        text = " ".join(
            str(item.get(key) or "")
            for key in ("title", "snippet", "url", "source_url", "customer_website", "origin")
        )
        origin = str(item.get("origin") or "")
        trusted_geo_source = origin in {"Google Maps", "OpenStreetMap"} or origin.startswith("OpenStreetMap")
        if not trusted_geo_source and has_foreign_location_conflict(text, country):
            continue
        identity = raw_result_identity(item)
        if identity and identity in seen:
            continue
        if identity:
            seen.add(identity)
        kept.append(item)
    return kept


LOCALIZED_DISCOVERY_TERMS = {
    "China": (
        "汽车经销商 新能源 联系方式 官网",
        "华为系 问界 尊界 汽车 经销商 电话",
        "新能源汽车贸易公司 出口 联系人",
        "多品牌汽车展厅 高端新能源 SUV",
        "企业车队 新能源汽车 采购",
        "汽车外贸公司 新能源车 出口",
    ),
    "Nigeria": (
        "car dealer Lagos imported cars phone WhatsApp",
        "tokunbo cars dealer Lagos auto sales",
        "vehicle importer Nigeria showroom",
        "Jiji Nigeria cars dealer contact",
    ),
    "Ghana": (
        "car dealer Accra imported cars phone WhatsApp",
        "home used cars Ghana dealer showroom",
        "vehicle importer Ghana auto sales",
        "Tonaton cars dealer contact",
    ),
    "Algeria": (
        "vente voiture Alger concessionnaire téléphone contact",
        "concessionnaire automobile Algérie showroom agent agréé",
        "importateur distributeur automobile Algérie contact",
        "annuaire entreprises automobile Algérie concessionnaire",
        "voitures occasion professionnel vendeur Algérie",
        "سيارات للبيع الجزائر وكيل سيارات معرض سيارات",
    ),
    "Côte d'Ivoire": (
        "vente voiture Abidjan concessionnaire contact",
        "concessionnaire automobile Cote d'Ivoire showroom",
        "importateur automobile Abidjan contact",
        "voiture occasion Abidjan garage automobile",
    ),
    "Cote d'Ivoire": (
        "vente voiture Abidjan concessionnaire contact",
        "concessionnaire automobile Cote d'Ivoire showroom",
        "importateur automobile Abidjan contact",
        "voiture occasion Abidjan garage automobile",
    ),
    "Ivory Coast": (
        "vente voiture Abidjan concessionnaire contact",
        "concessionnaire automobile Cote d'Ivoire showroom",
        "importateur automobile Abidjan contact",
        "voiture occasion Abidjan garage automobile",
    ),
    "Egypt": (
        "car dealer Cairo imported cars phone WhatsApp",
        "Egypt used car dealer auto trading company contact",
        "Alexandria vehicle importer distributor showroom",
        "New Cairo car showroom automotive trading WhatsApp",
        "Mansoura Tanta car dealer motors showroom contact",
        "معرض سيارات القاهرة سيارات للبيع",
        "مستورد سيارات مصر contact",
        "Egypt car showroom dealer contact",
    ),
    "Kyrgyzstan": (
        "автосалон Бишкек автомобили контакт",
        "машины Бишкек автосалон дилер",
        "импорт авто Кыргызстан дилер",
        "Кыргызстан авто базар дилер",
    ),
    "Ethiopia": (
        "car dealer Addis Ababa imported cars contact",
        "vehicle importer Ethiopia showroom",
        "Addis Ababa car sales dealer phone",
        "Ethiopia automotive trading company",
    ),
    "Oman": (
        "car dealer Muscat imported cars WhatsApp",
        "معرض سيارات مسقط سيارات للبيع",
        "Oman vehicle importer showroom contact",
        "Muscat auto trading LLC cars",
    ),
    "Armenia": (
        "ավտոսրահ Երևան մեքենաներ կոնտակտ",
        "автосалон Ереван автомобили контакт",
        "Armenia car dealer Yerevan imported cars",
        "Yerevan auto dealer showroom contact",
    ),
}


def localized_vehicle_listing_queries(country: str, cities: list[str]) -> list[str]:
    country_text = normalize_country_match_text(country)
    if "russia" not in country_text:
        selected_terms: tuple[str, ...] = ()
        for key, terms in LOCALIZED_DISCOVERY_TERMS.items():
            meta = COUNTRY_SEARCH_META.get(key, {})
            aliases = (key, meta.get("location", ""), *(meta.get("aliases") or ()))
            if any((token := normalize_country_match_text(alias)) and token in country_text for alias in aliases):
                selected_terms = terms
                break
        if not selected_terms:
            return []
        queries: list[str] = []
        for city in cities[:14]:
            for term in selected_terms:
                queries.append(f"{city} {term}".strip())
        return list(dict.fromkeys(queries))
    queries: list[str] = []
    for city in cities[:14]:
        queries.extend([
            f"{city} автосалон автомобили в наличии официальный сайт",
            f"{city} купить авто автосалон новые автомобили",
            f"{city} авто в салоне дилер автомобили",
            f"{city} site:.ru/cars/ автосалон автомобили",
        ])
    return list(dict.fromkeys(queries))


def local_source_query_variants(
    country: str,
    cities: list[str],
    target_type: str,
    exclude_query: str = "",
    cutoff_query: str = "",
) -> list[str]:
    sources = local_discovery_sources(country)
    if not sources:
        return []
    meta = country_search_meta(country)
    market_terms = list(dict.fromkeys([*(cities[:3]), meta.get("location", ""), str(country or "").split(" ")[0]]))
    if meta.get("code") == "cn":
        intent_terms = {
            "dealer": ("汽车经销商", "新能源车商", "多品牌汽车展厅"),
            "parallel": ("平行进口车商", "汽车贸易公司", "进口车展厅"),
            "importer": ("汽车外贸公司", "新能源汽车出口", "汽车贸易公司"),
            "fleet": ("企业车队", "汽车租赁公司", "新能源车队"),
            "corporate": ("企业用车采购", "公司车辆采购", "新能源汽车采购"),
            "government": ("公务车采购", "政府用车项目", "新能源汽车招标"),
            "buying": ("求购新能源车", "汽车批发", "车商收车"),
            "individual": ("新能源车商", "高端汽车展厅", "二网车商"),
        }.get(target_type, ("汽车经销商", "新能源车商", "汽车贸易公司"))
        queries: list[str] = []
        for source_name, domain in sources:
            for place in market_terms[:5]:
                for term in intent_terms[:3]:
                    queries.append(f"site:{domain} {place} {term} 联系方式 电话 邮箱 {exclude_query}{cutoff_query}".strip())
            queries.append(f"site:{domain} {source_name} 华为系 问界 尊界 新能源 汽车 客户 {exclude_query}{cutoff_query}".strip())
        return list(dict.fromkeys(queries))
    intent_terms = {
        "dealer": ("car dealer", "car showroom", "cars for sale", "motors"),
        "parallel": ("parallel import", "imported cars", "auto trading", "car dealer"),
        "importer": ("vehicle importer", "car distributor", "auto trading", "imported cars"),
        "fleet": ("fleet", "car rental", "corporate vehicles", "vehicle procurement"),
        "corporate": ("corporate vehicles", "fleet procurement", "car supplier", "vehicle procurement"),
        "government": ("vehicle supplier", "fleet tender", "automotive company"),
        "buying": ("car buyer", "used cars", "dealer", "showroom"),
        "individual": ("used cars", "luxury cars", "electric vehicles", "cars for sale"),
    }.get(target_type, ("car dealer", "car showroom", "cars for sale", "motors"))
    if meta.get("code") == "dz":
        intent_terms = {
            "dealer": (
                "concessionnaire automobile", "showroom automobile",
                "agent automobile agréé", "vendeur professionnel voitures",
            ),
            "parallel": (
                "importateur automobile", "vente voitures importées",
                "distributeur automobile", "concessionnaire multimarque",
            ),
            "importer": (
                "importateur distributeur automobile", "importation véhicules",
                "grossiste automobile", "concessionnaire multimarque",
            ),
            "fleet": (
                "gestionnaire de flotte automobile", "location voitures entreprise",
                "parc automobile société", "fournisseur véhicules professionnels",
            ),
            "corporate": (
                "fournisseur véhicules entreprise", "flotte automobile société",
                "achat véhicules professionnels", "distributeur automobile",
            ),
            "government": (
                "fournisseur véhicules", "marché véhicules flotte",
                "entreprise automobile", "véhicules utilitaires",
            ),
            "buying": (
                "achat vente voitures occasion", "vendeur professionnel automobile",
                "concessionnaire", "showroom automobile",
            ),
            "individual": (
                "voitures occasion professionnel", "voitures de luxe",
                "véhicules électriques", "vente voitures",
            ),
        }.get(target_type, (
            "concessionnaire automobile", "showroom automobile",
            "importateur automobile", "vendeur professionnel voitures",
        ))
    localized_intents = LOCAL_AUTOMOTIVE_INTENT_TERMS.get(meta.get("code", ""), ())
    if localized_intents:
        intent_terms = tuple(dict.fromkeys([*localized_intents, *intent_terms]))
    queries: list[str] = []
    # Rotate domains first so a query cap cannot let the first large marketplace
    # consume the whole country-specific search budget.
    for place in market_terms[:4]:
        for term in intent_terms[:3]:
            for source_name, domain in sources:
                queries.append(f"site:{domain} {place} {term} contact phone WhatsApp {exclude_query}{cutoff_query}".strip())
    for source_name, domain in sources:
        queries.append(f"site:{domain} {source_name} automotive dealer showroom contact {exclude_query}{cutoff_query}".strip())
    return list(dict.fromkeys(queries))


ALGERIA_AUTOMOTIVE_DIRECTORY_PAGES = (
    (
        "Pages Jaunes Algérie",
        "https://pagesjaunes-dz.com/companies/products/0161001/automobiles-Agents-concessionnaires-et-succursales-",
        r"/companies/detail/",
    ),
    (
        "Tidjara Algérie",
        "https://tidjara.dz/directory-category/concessionnaire-automobile/",
        r"/annuaire-algerie/",
    ),
    (
        "Go Africa Online Algérie",
        "https://www.goafricaonline.com/dz/annuaire/concessionnaires-automobiles-moto",
        r"/dz/\d+-[^?#]+",
    ),
)


REGIONAL_AUTOMOTIVE_DIRECTORY_PAGES = {
    "ae": (
        "DubiCars",
        tuple(
            "https://www.dubicars.com/dealers"
            + (f"?page={page}" if page > 1 else "")
            for page in range(1, 7)
        ),
        r"/dealers/[^/?#]+-\d+$",
    ),
    "sa": (
        "SaudiSale",
        ("https://cars.saudisale.com/en/showroom/list",),
        r"/en/showroom/\d+/[^/?#]+$",
    ),
    "qa": (
        "QMotor",
        ("https://qmotor.com/dealers",),
        r"/showrooms/[^/?#]+$",
    ),
}


ALGERIA_DIRECTORY_OPERATOR_DOMAINS = (
    "pagesjaunes-dz.com",
    "blalgeria.com",
    "haousli.com",
    "easyprospect.blalgeria.com",
    "tidjara.dz",
    "goafricaonline.com",
    "leafletjs.com",
    "openstreetmap.org",
    "schema.org",
    "wordpress.org",
    "gmpg.org",
    "google.com",
    "googleapis.com",
    "gstatic.com",
)


COUNTRY_CALLING_CODES = {
    "ae": "971", "sa": "966", "kz": "7", "ru": "7", "qa": "974", "kw": "965",
    "uz": "998", "az": "994", "ng": "234", "gh": "233", "dz": "213", "ci": "225",
    "eg": "20", "kg": "996", "et": "251", "om": "968", "am": "374", "bh": "973",
    "jo": "962", "ge": "995", "vn": "84", "ph": "63", "mx": "52", "br": "55",
    "cl": "56", "co": "57", "by": "375", "za": "27", "ar": "54", "pe": "51",
    "ec": "593", "uy": "598", "py": "595", "ma": "212", "cn": "86",
}


def normalize_country_phone(value: str, country: str) -> str:
    decoded_value = urllib.parse.unquote(html.unescape(value or "")).strip()
    explicit_international = decoded_value.startswith("+") or decoded_value.startswith("00")
    digits = re.sub(r"\D", "", decoded_value)
    if digits.startswith("00"):
        digits = digits[2:]
    if explicit_international:
        return f"+{digits}" if 8 <= len(digits) <= 15 else ""
    calling_code = COUNTRY_CALLING_CODES.get(country_search_meta(country).get("code", ""), "")
    if not calling_code:
        return f"+{digits}" if 8 <= len(digits) <= 15 else ""
    if digits.startswith(calling_code) and 8 <= len(digits) <= 15:
        return f"+{digits}"
    national_number = digits.lstrip("0")
    if 7 <= len(national_number) <= 12 and len(calling_code + national_number) <= 15:
        return f"+{calling_code}{national_number}"
    return ""


def normalize_algeria_phone(value: str) -> str:
    return normalize_country_phone(value, "Algeria")


def algeria_directory_local_business(document: str) -> dict:
    def find_local_business(value) -> dict:
        if isinstance(value, dict):
            value_type = value.get("@type")
            type_values = value_type if isinstance(value_type, list) else [value_type]
            if any(str(item or "").lower() in {"localbusiness", "automotivedealer", "autodealer"} for item in type_values):
                return value
            for nested in value.values():
                found = find_local_business(nested)
                if found:
                    return found
        elif isinstance(value, list):
            for nested in value:
                found = find_local_business(nested)
                if found:
                    return found
        return {}

    for raw_value in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',
        document,
        re.I,
    ):
        try:
            parsed = json.loads(html.unescape(raw_value).strip())
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        found = find_local_business(parsed)
        if found:
            return found
    return {}


def algeria_directory_official_websites(document: str, detail_url: str) -> list[str]:
    detail_domain = safe_urlparse(detail_url).netloc.lower().removeprefix("www.")
    websites = []
    for raw_url in re.findall(r'href=["\']([^"\']+)["\']', document, re.I):
        if re.match(r"^(?:mailto|tel|javascript|data):", html.unescape(raw_url).strip(), re.I):
            continue
        candidate = normalize_public_url(urllib.parse.urljoin(detail_url, html.unescape(raw_url)))
        domain = safe_urlparse(candidate).netloc.lower().removeprefix("www.")
        if (
            not candidate
            or domain == detail_domain
            or any(domain == blocked or domain.endswith(f".{blocked}") for blocked in ALGERIA_DIRECTORY_OPERATOR_DOMAINS)
            or not is_business_website_url(candidate)
        ):
            continue
        if candidate not in websites:
            websites.append(candidate)
    return websites[:4]


def algeria_directory_detail(source_name: str, company: str, detail_url: str) -> dict:
    try:
        document, final_url = fetch_document(detail_url, timeout=12)
    except (OSError, TimeoutError, UnicodeError, urllib.error.URLError, http.client.HTTPException):
        return {"detail_url": detail_url, "fetched": False}

    relevant_document = document
    if source_name in {"Pages Jaunes Algérie", "Go Africa Online Algérie"}:
        relevant_document = re.split(r"<footer\b", document, maxsplit=1, flags=re.I)[0]
    local_business = algeria_directory_local_business(document)
    contacts = extract_public_contacts(relevant_document)

    phones = []
    for raw_phone in re.findall(r'href=["\']tel:([^"\']+)["\']', relevant_document, re.I):
        phone = normalize_algeria_phone(raw_phone)
        if phone and phone not in phones:
            phones.append(phone)
    local_phone = normalize_algeria_phone(str(local_business.get("telephone") or ""))
    if local_phone and local_phone not in phones:
        phones.insert(0, local_phone)

    operator_email_domains = {"tidjara.dz", "pagesjaunes-dz.com", "blalgeria.com", "goafricaonline.com"}
    emails = [
        email for email in (contacts.get("emails") or [])
        if email.split("@")[-1].lower() not in operator_email_domains
    ]
    local_email = clean_text(str(local_business.get("email") or "")).lower()
    if local_email and "@" in local_email and local_email.split("@")[-1] not in operator_email_domains:
        emails.insert(0, local_email)
    emails = list(dict.fromkeys(emails))[:8]

    social_accounts = [
        account for account in (contacts.get("social_accounts") or [])
        if not re.search(r"pages[.-]?jaunes|tidjara|goafricaonline", account, re.I)
    ]
    websites = algeria_directory_official_websites(relevant_document, final_url)
    address = ""
    local_address = local_business.get("address")
    if isinstance(local_address, dict):
        address = clean_text(" ".join(
            str(local_address.get(key) or "")
            for key in ("streetAddress", "addressLocality", "addressRegion", "addressCountry")
        ))
    if not address:
        address_match = re.search(r"<address[^>]*>([\s\S]*?)</address>", relevant_document, re.I)
        if address_match:
            address = clean_text(address_match.group(1))[:240]
    if not address:
        text = clean_text(relevant_document)
        address_match = re.search(
            r"(?:Adresse|Address)\s*[:：]?\s*(.{5,220}?)(?=(?:Téléphone|Telephone|Tél\.?|Phone|Email|Site web|Website|Produits|Activité|$))",
            text,
            re.I,
        )
        if address_match:
            address = clean_text(address_match.group(1))[:240]

    contacts.update({
        "email": emails[0] if emails else "",
        "emails": emails,
        "phone": phones[0] if phones else "",
        "phones": phones,
        "social_accounts": social_accounts[:8],
        "websites": websites,
    })
    description = clean_text(str(local_business.get("description") or "")) or extract_meta(relevant_document)
    strong_non_sales = bool(re.search(
        r"\b(trucks?|camions?|motos?|motocycles?|spare parts?|auto parts?|tyres?|tires?|garage|repair|workshop|"
        r"maintenance|car wash|detailing|equipment|equipements?)\b|"
        r"(pièces détachées|réparation|pneus?|lavage)",
        f"{company} {description}",
        re.I,
    ))
    return {
        "detail_url": normalize_public_url(final_url) or detail_url,
        "fetched": True,
        "contacts": contacts,
        "website": websites[0] if websites else "",
        "address": address,
        "description": description[:700],
        "sales_fit": not strong_non_sales,
    }


DIRECTORY_TECHNICAL_DOMAINS = {
    "schema.org", "wordpress.org", "gmpg.org", "google.com", "googleapis.com",
    "gstatic.com", "doubleclick.net", "googletagmanager.com", "openstreetmap.org",
    "leafletjs.com", "apple.com", "microsoft.com", "bunny.net", "cloudflare.com",
    "cloudfront.net", "jsdelivr.net", "bootstrapcdn.com", "fontawesome.com",
    "facebook.com", "instagram.com", "linkedin.com", "tiktok.com", "youtube.com",
    "twitter.com", "x.com", "whatsapp.com", "wa.me", "telegram.me", "t.me", "zalo.me",
}

LOCAL_DIRECTORY_CITY_ALIASES = {
    "vn": ("Hồ Chí Minh", "TP HCM", "Hà Nội", "Đà Nẵng", "Hải Phòng", "Cần Thơ"),
    "ru": ("Москва", "Санкт-Петербург", "Казань", "Екатеринбург"),
    "kz": ("Алматы", "Астана", "Шымкент", "Караганда"),
    "uz": ("Toshkent", "Samarqand", "Buxoro", "Farg'ona"),
}


def local_directory_source_for_url(url: str, country: str) -> tuple[str, str] | None:
    domain = safe_urlparse(normalize_public_url(url)).netloc.lower().removeprefix("www.")
    for source_name, source_domain in local_discovery_sources(country):
        normalized_source_domain = source_domain.lower().removeprefix("www.")
        if domain == normalized_source_domain or domain.endswith(f".{normalized_source_domain}"):
            return source_name, normalized_source_domain
    return None


def local_directory_profile_url(url: str) -> bool:
    parsed = safe_urlparse(normalize_public_url(url))
    path = parsed.path.strip("/").lower()
    if not path:
        return bool(re.search(r"(?:dealer|salon|showroom|company|listing|profile|id)=", parsed.query, re.I))
    generic_paths = {
        "cars", "car", "autos", "auto", "vehicles", "dealers", "dealer", "showrooms",
        "salons", "directory", "annuaire", "automotive", "used-cars", "new-cars",
        "marketplace", "search", "listings", "voitures", "carros", "showroom-oto",
        "dealers-list", "auto-dealers", "agencias", "concessionnaires",
    }
    segments = [segment for segment in path.split("/") if segment]
    if path in generic_paths or re.fullmatch(r"(?:en|fr|ar|es|pt|vi)(?:/)?", path):
        return False
    if len(segments) <= 2 and all(
        segment in generic_paths or segment in {"en", "fr", "ar", "es", "pt", "vi"}
        for segment in segments
    ):
        return False
    return True


def directory_official_websites(document: str, detail_url: str, country: str, company: str) -> list[str]:
    detail_domain = safe_urlparse(detail_url).netloc.lower().removeprefix("www.")
    blocked_domains = {
        *DIRECTORY_TECHNICAL_DOMAINS,
        *(domain.lower().removeprefix("www.") for _, domain in local_discovery_sources(country)),
    }
    generic_company_words = {
        "auto", "autos", "automotive", "automobile", "car", "cars", "vehicle", "vehicles",
        "motor", "motors", "dealer", "dealership", "showroom", "company", "group", "ltd",
        "llc", "sa", "sarl", "spa", "the", "and",
    }
    raw_company_words = [
        word for word in re.findall(r"[a-z0-9]+", normalize_country_match_text(company))
        if len(word) >= 3 and word not in {"the", "and", "ltd", "llc", "sarl", "spa"}
    ]
    company_words = [
        word for word in raw_company_words
        if len(word) >= 3 and word not in generic_company_words
    ]
    company_acronym = "".join(word[0] for word in raw_company_words if word)
    websites: list[str] = []
    for anchor in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>', document, re.I):
        raw_url, anchor_body = anchor.groups()
        decoded_url = html.unescape(raw_url).strip()
        if re.match(r"^(?:mailto|tel|javascript|data):", decoded_url, re.I):
            continue
        candidates = [normalize_public_url(urllib.parse.urljoin(detail_url, decoded_url))]
        parsed_candidate = safe_urlparse(candidates[0])
        for values in urllib.parse.parse_qs(parsed_candidate.query).values():
            candidates.extend(normalize_public_url(value) for value in values)
        for candidate in candidates:
            domain = safe_urlparse(candidate).netloc.lower().removeprefix("www.")
            domain_label = domain.split(".")[0]
            anchor_text = clean_text(anchor_body).lower()
            explicit_website_link = bool(re.search(
                r"\b(website|official site|site web|sitio web|trang web|web)\b|官网|الموقع",
                anchor_text,
                re.I,
            ))
            company_related_domain = bool(
                any(word in domain_label for word in company_words)
                or (len(company_acronym) >= 2 and company_acronym in domain_label)
            )
            if (
                not candidate
                or domain == detail_domain
                or not re.search(r"[a-z]", domain, re.I)
                or any(domain == blocked or domain.endswith(f".{blocked}") for blocked in blocked_domains)
                or not is_business_website_url(candidate)
                or not (explicit_website_link or company_related_domain)
            ):
                continue
            if candidate not in websites:
                websites.append(candidate)
    return websites[:4]


def local_directory_sales_fit(company: str, description: str) -> bool:
    value = clean_text(f"{company} {description}").lower()
    sales_signal = bool(re.search(
        r"\b(car dealer|auto dealer|vehicle dealer|dealership|showroom|"
        r"used cars|new cars|pre-owned|concessionnaire|concesionario|automotora|concessionária|"
        r"revenda|loja de carros|avtosalon|автосалон)\b|"
        r"(đại lý ô tô|showroom ô tô|mua bán xe|معرض سيارات|تجارة السيارات|ավտոսրահ|ავტოსალონი)",
        value,
        re.I,
    ))
    non_sales_signal = bool(re.search(
        r"\b(spare parts?|auto parts?|parts supplier|tyres?|tires?|garage|repair|workshop|"
        r"maintenance|car wash|detailing|body shop|equipment|equipements?|scrapyard|salvage)\b|"
        r"(pièces détachées|réparation|pneus?|lavage|repuestos|refacciones|taller mecánico|"
        r"peças|oficina mecânica|sửa chữa|phụ tùng|ремонт|запчасти)",
        value,
        re.I,
    ))
    truck_signal = bool(re.search(
        r"\b(trucks?|heavy trucks?|commercial trucks?|camions?|poids lourds|camiones?|caminhões|"
        r"xe tải|грузовик|грузовые автомобили)\b",
        value,
        re.I,
    ))
    passenger_signal = bool(re.search(
        r"\b(cars?|automobiles?|suv|sedan|passenger vehicles?|voitures?|autos?|carros?)\b|"
        r"(xe ô tô|легковые автомобили)",
        value,
        re.I,
    ))
    return not (truck_signal and not passenger_signal) and not (non_sales_signal and not sales_signal)


def local_directory_detail(source_name: str, country: str, company: str, detail_url: str) -> dict:
    try:
        document, final_url = fetch_document(detail_url, timeout=12)
    except (OSError, TimeoutError, UnicodeError, urllib.error.URLError, http.client.HTTPException):
        return {"detail_url": detail_url, "fetched": False}

    relevant_document = re.split(r"<footer\b", document, maxsplit=1, flags=re.I)[0]
    local_business = algeria_directory_local_business(document)
    contacts = extract_public_contacts(relevant_document)
    phones: list[str] = []
    raw_phones = [
        *re.findall(r'href=["\']tel:([^"\']+)["\']', relevant_document, re.I),
        *(contacts.get("phones") or []),
        str(local_business.get("telephone") or ""),
    ]
    for raw_phone in raw_phones:
        phone = normalize_country_phone(str(raw_phone), country)
        if phone and phone not in phones:
            phones.append(phone)

    operator_domains = {
        domain.lower().removeprefix("www.")
        for _, domain in local_discovery_sources(country)
    }
    emails = [
        email for email in (contacts.get("emails") or [])
        if not any(
            email.split("@")[-1].lower() == domain
            or email.split("@")[-1].lower().endswith(f".{domain}")
            for domain in operator_domains
        )
    ]
    local_email = clean_text(str(local_business.get("email") or "")).lower()
    if local_email and "@" in local_email and all(
        local_email.split("@")[-1] != domain
        and not local_email.split("@")[-1].endswith(f".{domain}")
        for domain in operator_domains
    ):
        emails.insert(0, local_email)
    emails = list(dict.fromkeys(emails))[:8]

    source_brand = safe_urlparse(final_url).netloc.lower().removeprefix("www.").split(".")[0]
    social_accounts = [
        account for account in (contacts.get("social_accounts") or [])
        if source_brand not in account.lower()
    ]
    websites = directory_official_websites(relevant_document, final_url, country, company)
    address = ""
    local_address = local_business.get("address")
    if isinstance(local_address, dict):
        address = clean_text(" ".join(
            str(local_address.get(key) or "")
            for key in ("streetAddress", "addressLocality", "addressRegion", "postalCode", "addressCountry")
        ))
    if not address:
        address_match = re.search(r"<address[^>]*>([\s\S]*?)</address>", relevant_document, re.I)
        if address_match:
            address = clean_text(address_match.group(1))[:240]
    page_text = clean_text(relevant_document)
    visible_address_match = re.search(
        r"(?:Adresse|Address|Dirección|Endereço|Địa chỉ|العنوان)\s*[:：]?\s*(.{5,220}?)"
        r"(?=(?:Téléphone|Telephone|Tél\.?|Phone|Teléfono|Telefone|Điện thoại|Email|E-mail|Website|Site web|$))",
        page_text,
        re.I,
    )
    if visible_address_match:
        visible_address = clean_text(visible_address_match.group(1))[:240]
        if visible_address and (not address or len(visible_address) < len(address)):
            address = visible_address
    city_occurrences: list[tuple[int, str]] = []
    country_code = country_search_meta(country).get("code", "")
    city_names = [
        *COUNTRY_HINTS.get(country_search_meta(country).get("location", ""), ()),
        *LOCAL_DIRECTORY_CITY_ALIASES.get(country_code, ()),
    ]
    for city_name in city_names:
        match = re.search(re.escape(city_name), address, re.I)
        if match:
            city_occurrences.append((match.start(), normalize_country_match_text(city_name)))
    city_occurrences.sort()
    if len({name for _, name in city_occurrences}) >= 2:
        first_city = city_occurrences[0][1]
        conflicting_city = next((position for position, name in city_occurrences[1:] if name != first_city), None)
        if conflicting_city and conflicting_city >= 20:
            address = address[:conflicting_city].strip(" ,;-" )

    contacts.update({
        "email": emails[0] if emails else "",
        "emails": emails,
        "phone": phones[0] if phones else "",
        "phones": phones,
        "social_accounts": social_accounts[:8],
        "websites": websites,
    })
    description = clean_text(str(local_business.get("description") or "")) or extract_meta(relevant_document)
    return {
        "detail_url": normalize_public_url(final_url) or detail_url,
        "fetched": True,
        "contacts": contacts,
        "website": websites[0] if websites else "",
        "address": address,
        "description": description[:700],
        "sales_fit": local_directory_sales_fit(company, description),
    }


def enrich_local_directory_results(items: list[dict], country: str, limit: int = 60) -> list[dict]:
    candidates: list[dict] = []
    for item in items:
        source = local_directory_source_for_url(item.get("source_url") or item.get("url") or "", country)
        if not source or item.get("directory_detail_fetched"):
            continue
        source_name, _ = source
        item["origin"] = source_name
        item["source_type"] = "本地汽车商业目录"
        item["local_directory_candidate"] = True
        item["directory_profile_page"] = local_directory_profile_url(item.get("url", ""))
        candidates.append(item)
        if len(candidates) >= limit:
            break
    if not candidates:
        return items

    details: dict[int, dict] = {}
    executor = ThreadPoolExecutor(max_workers=min(8, len(candidates)))
    futures = {
        executor.submit(
            local_directory_detail,
            item["origin"],
            country,
            clean_text(str(item.get("title") or "")),
            item.get("url", ""),
        ): id(item)
        for item in candidates
    }
    try:
        for future in as_completed(futures, timeout=max(45, min(180, len(candidates) * 3))):
            try:
                details[futures[future]] = future.result()
            except (OSError, ValueError, RuntimeError, TimeoutError):
                details[futures[future]] = {"fetched": False}
    except FuturesTimeoutError:
        pass
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    for item in candidates:
        detail = details.get(id(item), {})
        listing_contacts = (
            item.get("directory_public_contacts")
            if isinstance(item.get("directory_public_contacts"), dict)
            else {}
        )
        detail_contacts = detail.get("contacts") if isinstance(detail.get("contacts"), dict) else {}
        contacts = merge_public_contacts(listing_contacts, detail_contacts)
        website = detail.get("website", "")
        address = detail.get("address", "")
        description = detail.get("description", "")
        listing_verified = bool(
            item.get("directory_listing_verified")
            and (
                contacts.get("emails")
                or contacts.get("phones")
                or contacts.get("whatsapps")
            )
        )
        detail_fetched = bool(detail.get("fetched") or listing_verified)
        sales_fit = (
            bool(detail.get("sales_fit"))
            if detail.get("fetched")
            else local_directory_sales_fit(
                clean_text(str(item.get("title") or "")),
                clean_text(f"{item.get('snippet', '')} {item.get('listing_context', '')}"),
            )
        )
        contact_parts = [
            *(contacts.get("emails") or []),
            *(contacts.get("phones") or []),
            *(contacts.get("social_accounts") or []),
        ]
        item.update({
            "url": detail.get("detail_url") or item.get("url", ""),
            "source_url": detail.get("detail_url") or item.get("source_url") or item.get("url", ""),
            "customer_website": website,
            "snippet": clean_text(
                f"{item.get('snippet', '')} Local automotive directory in {country}: {item.get('origin', '')}. "
                f"Address: {address}. {description}"
            )[:1400],
            "contact": " ".join([*contact_parts, website]),
            "directory_public_contacts": contacts,
            "directory_detail_fetched": detail_fetched,
            "directory_sales_fit": sales_fit,
        })
        if detail_fetched:
            item["skip_fetch"] = True
    return items


def regional_directory_company_from_path(url: str) -> str:
    path = safe_urlparse(url).path.rstrip("/")
    slug = path.rsplit("/", 1)[-1]
    slug = re.sub(r"-\d+$", "", slug)
    return clean_text(urllib.parse.unquote(slug).replace("-", " ")).title()


def search_regional_automotive_directories(country: str, limit: int = 90) -> list[dict]:
    code = country_search_meta(country).get("code", "")
    config = REGIONAL_AUTOMOTIVE_DIRECTORY_PAGES.get(code)
    if not config:
        return []
    source_name, directory_urls, path_pattern = config
    default_city = {"ae": "Dubai", "sa": "Riyadh", "qa": "Doha"}.get(code, country)
    candidates: list[dict] = []
    seen_urls: set[str] = set()

    for directory_url in directory_urls:
        try:
            page, final_url = fetch_document(directory_url, timeout=25)
        except (OSError, TimeoutError, UnicodeError, urllib.error.URLError, http.client.HTTPException):
            continue
        for anchor in re.finditer(
            r'<a\b([^>]*)href=["\']([^"\']+)["\']([^>]*)>([\s\S]*?)</a>',
            page,
            re.I,
        ):
            before_attrs, href, after_attrs, body = anchor.groups()
            absolute_url = normalize_public_url(urllib.parse.urljoin(final_url, html.unescape(href)))
            if not absolute_url or not re.search(path_pattern, safe_urlparse(absolute_url).path, re.I):
                continue
            identity = absolute_url.lower().split("#", 1)[0].rstrip("/")
            if identity in seen_urls:
                continue
            attrs = f"{before_attrs} {after_attrs}"
            name_match = re.search(r'data-dealer-name=["\']([^"\']+)', attrs, re.I)
            company = clean_text(html.unescape(name_match.group(1))) if name_match else clean_text(body)
            company = re.split(r"\b(?:Phone\s*\d*|Tel(?:ephone)?|Ads?)\s*:", company, maxsplit=1, flags=re.I)[0].strip()
            if not company or company.lower() in {"see all cars", "view showroom", "view dealer"} or len(company) > 140:
                company = regional_directory_company_from_path(absolute_url)
            if len(company) < 2:
                continue

            context_html = page[max(0, anchor.start() - 700): min(len(page), anchor.end() + 900)]
            context = clean_text(context_html)
            location_match = re.search(r'data-dealer-location=["\']([^"\']+)', attrs, re.I)
            city = clean_text(html.unescape(location_match.group(1))) if location_match else default_city
            raw_phones = re.findall(r'data-dealer-phone=["\']([^"\']+)', attrs, re.I)
            if not raw_phones:
                raw_phones = re.findall(
                    r"(?:Phone\s*\d*|Tel(?:ephone)?)\s*:\s*<span[^>]*>([^<]+)</span>",
                    body,
                    re.I,
                )
            if not raw_phones:
                raw_phones = re.findall(r"\+\d[\d\s().-]{6,18}\d", clean_text(body))
            phones: list[str] = []
            for raw_phone in raw_phones:
                phone = normalize_country_phone(html.unescape(raw_phone), country)
                if phone and phone not in phones:
                    phones.append(phone)
                if len(phones) >= 3:
                    break
            contacts = {
                "email": "",
                "emails": [],
                "phone": phones[0] if phones else "",
                "phones": phones,
                "whatsapp": "",
                "whatsapps": [],
                "social_accounts": [],
                "websites": [],
            }
            seen_urls.add(identity)
            candidates.append({
                "title": company,
                "url": absolute_url,
                "source_url": absolute_url,
                "origin": source_name,
                "source_type": "Local automotive business directory",
                "snippet": f"{company} is listed as a car dealership or showroom in {city}, {country}. Local directory: {source_name}.",
                "listing_context": context[:1200],
                "contact": " ".join(phones),
                "directory_public_contacts": contacts,
                "directory_listing_verified": bool(phones),
                "local_directory_candidate": True,
                "directory_profile_page": True,
            })
            if len(candidates) >= limit:
                break
        if len(candidates) >= limit:
            break
    return candidates


def search_algeria_automotive_directories(limit: int = 90) -> list[dict]:
    candidates: list[dict] = []
    seen_urls: set[str] = set()
    per_directory_limit = max(12, (max(1, limit) + len(ALGERIA_AUTOMOTIVE_DIRECTORY_PAGES) - 1) // len(ALGERIA_AUTOMOTIVE_DIRECTORY_PAGES))
    for source_name, directory_url, path_pattern in ALGERIA_AUTOMOTIVE_DIRECTORY_PAGES:
        try:
            page, final_url = fetch_document(directory_url, timeout=20)
        except (OSError, TimeoutError, UnicodeError, urllib.error.URLError, http.client.HTTPException):
            continue
        source_count = 0
        for anchor in re.finditer(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
            page,
            re.I,
        ):
            href, body = anchor.groups()
            absolute_url = normalize_public_url(urllib.parse.urljoin(final_url, html.unescape(href)))
            parsed = safe_urlparse(absolute_url)
            if not absolute_url or not re.search(path_pattern, parsed.path, re.I):
                continue
            identity = absolute_url.lower().split("#", 1)[0].rstrip("/")
            if identity in seen_urls:
                continue
            company = clean_text(body)
            if not company or len(company) < 3 or len(company) > 140:
                continue
            seen_urls.add(identity)
            context = clean_text(page[max(0, anchor.start() - 500): min(len(page), anchor.end() + 1200)])
            candidates.append({
                "title": company,
                "url": absolute_url,
                "source_url": absolute_url,
                "origin": source_name,
                "source_type": "Algeria local automotive business directory",
                "listing_context": context,
            })
            source_count += 1
            if len(candidates) >= limit or source_count >= per_directory_limit:
                break
        if len(candidates) >= limit:
            break

    details: dict[str, dict] = {}
    if candidates:
        executor = ThreadPoolExecutor(max_workers=min(8, len(candidates)))
        futures = {
            executor.submit(algeria_directory_detail, item["origin"], item["title"], item["url"]): item["url"]
            for item in candidates
        }
        try:
            for future in as_completed(futures, timeout=max(40, min(150, len(candidates) * 3))):
                try:
                    details[futures[future]] = future.result()
                except (OSError, ValueError, RuntimeError, TimeoutError):
                    details[futures[future]] = {"detail_url": futures[future], "fetched": False}
        except FuturesTimeoutError:
            pass
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    results = []
    for item in candidates:
        detail = details.get(item["url"], {})
        contacts = detail.get("contacts") if isinstance(detail.get("contacts"), dict) else {}
        contact_parts = [
            *(contacts.get("emails") or []),
            *(contacts.get("phones") or []),
            *(contacts.get("social_accounts") or []),
        ]
        website = detail.get("website", "")
        address = detail.get("address", "")
        description = detail.get("description", "")
        item.update({
            "url": detail.get("detail_url") or item["url"],
            "source_url": detail.get("detail_url") or item["source_url"],
            "customer_website": website,
            "snippet": clean_text(
                f"{item['title']} is listed as an automotive dealership, authorized car agent or vehicle distributor in Algeria. "
                f"Local directory: {item['origin']}. Address: {address}. {description}"
            )[:1400],
            "contact": " ".join([*contact_parts, website]),
            "directory_public_contacts": contacts,
            "directory_detail_fetched": bool(detail.get("fetched")),
            "directory_sales_fit": bool(detail.get("sales_fit", False)),
            "local_directory_candidate": True,
            "directory_profile_page": True,
        })
        if detail.get("fetched"):
            item["skip_fetch"] = True
        item.pop("listing_context", None)
        results.append(item)

    return sorted(
        results,
        key=lambda item: (
            -int(bool(item.get("directory_sales_fit"))),
            -int(bool(item.get("customer_website"))),
            -int(bool(item.get("contact"))),
            str(item.get("title") or ""),
        ),
    )[:limit]


AUTOHOME_CITY_SLUGS = {
    "北京": "beijing",
    "天津": "tianjin",
    "石家庄": "shijiazhuang",
    "太原": "taiyuan",
    "呼和浩特": "huhehaote",
    "上海": "shanghai",
    "杭州": "hangzhou",
    "南京": "nanjing",
    "苏州": "suzhou",
    "宁波": "ningbo",
    "合肥": "hefei",
    "济南": "jinan",
    "福州": "fuzhou",
    "广州": "guangzhou",
    "深圳": "shenzhen",
    "佛山": "foshan",
    "东莞": "dongguan",
    "南宁": "nanning",
    "海口": "haikou",
    "武汉": "wuhan",
    "长沙": "changsha",
    "郑州": "zhengzhou",
    "成都": "chengdu",
    "重庆": "chongqing",
    "昆明": "kunming",
    "贵阳": "guiyang",
    "西安": "xian",
    "兰州": "lanzhou",
    "银川": "yinchuan",
    "西宁": "xining",
    "乌鲁木齐": "wulumuqi",
    "沈阳": "shenyang",
    "大连": "dalian",
    "长春": "changchun",
    "哈尔滨": "haerbin",
}


def search_autohome_dealers(cities: list[str], limit: int = 24) -> list[dict]:
    results: list[dict] = []
    seen: set[str] = set()
    for city in cities:
        slug = AUTOHOME_CITY_SLUGS.get(city)
        if not slug:
            continue
        url = f"https://dealer.autohome.com.cn/{slug}/"
        try:
            page = fetch_text(url, timeout=DISCOVERY_SEARCH_TIMEOUT)
        except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
            continue
        blocks = re.findall(
            r'<div class="tw-block tw-relative tw-group">([\s\S]*?)(?=<div class="tw-block tw-relative tw-group">|</main>|</body>)',
            page,
            flags=re.I,
        )
        if not blocks:
            blocks = re.findall(r'<a[^>]+href="/\d+/[^"]*"[\s\S]{0,2600}?950\d{8}', page, flags=re.I)
        for block in blocks:
            name_match = re.search(r'<a[^>]+href="(/(\d+)/[^"]*)"[^>]*class="[^"]*tw-text-\[20px\][^"]*"[^>]*>([\s\S]*?)</a>', block, flags=re.I)
            if not name_match:
                name_match = re.search(r'<a[^>]+href="(/(\d+)/[^"]*)"[^>]*>([^<]{2,80})</a>', block, flags=re.I)
            if not name_match:
                continue
            path = name_match.group(1).split("#", 1)[0]
            dealer_id = name_match.group(2)
            name = clean_text(name_match.group(3))
            if not name or dealer_id in seen:
                continue
            address_match = re.search(r'href="/' + re.escape(dealer_id) + r'/contact\.html[^"]*"[^>]*>([\s\S]*?)</a>', block, flags=re.I)
            if not address_match:
                address_match = re.search(r'(北京市|天津市|上海市|重庆市|河北省|山西省|内蒙古|江苏省|浙江省|山东省|广东省|四川省|辽宁省|吉林省|黑龙江省)[^<]{6,120}', block)
            address = clean_text(address_match.group(1) if address_match else "")
            phone_match = re.search(r'(950\d{8}|400[-\s]?\d{3}[-\s]?\d{4}|400\d{7})', block)
            phone = clean_text(phone_match.group(1)) if phone_match else ""
            source_url = urllib.parse.urljoin("https://dealer.autohome.com.cn", path)
            snippet_parts = [
                f"{name} 是汽车之家登记的{city}汽车经销商。",
                address,
                f"电话: {phone}" if phone else "",
            ]
            seen.add(dealer_id)
            results.append({
                "title": name,
                "url": source_url,
                "source_url": source_url,
                "customer_website": source_url,
                "snippet": " ".join(part for part in snippet_parts if part),
                "contact": phone,
                "origin": "汽车之家经销商",
                "source_type": "国内汽车平台经销商目录",
                "skip_fetch": True,
            })
            if len(results) >= limit:
                return results
    return results


def discovery_cities(country: str, city_focus: str = "", domestic_region: str = "") -> list[str]:
    cities = [city_focus.strip()] if city_focus.strip() else []
    country_text = normalize_country_match_text(country)
    if "china" in country_text or "中国" in str(country or ""):
        region_key = domestic_region if domestic_region in CHINA_DOMESTIC_REGIONS else "全国"
        cities.extend(CHINA_DOMESTIC_REGIONS.get(region_key, ()))
        cities.append("China")
        cities.append("中国")
        return list(dict.fromkeys(city for city in cities if city))[:14]
    for key, hints in COUNTRY_HINTS.items():
        meta = COUNTRY_SEARCH_META.get(key, {})
        aliases = (key, meta.get("location", ""), *(meta.get("aliases") or ()))
        if any((token := normalize_country_match_text(alias)) and token in country_text for alias in aliases):
            cities.extend(hints)
            break
    meta = country_search_meta(country)
    cities.append(meta.get("location") or str(country or "").split(" ")[0])
    return list(dict.fromkeys(city for city in cities if city))


def city_keyword_queries(cities: list[str], terms: tuple[str, ...], suffix: str = "") -> list[str]:
    queries = []
    suffix = suffix.strip()
    for index, term in enumerate(terms):
        if not cities:
            break
        city = cities[index % len(cities)]
        query = f"{city} {term}"
        if suffix:
            query = f"{query} {suffix}"
        queries.append(query.strip())
    for term in terms:
        for city in cities:
            query = f"{city} {term}"
            if suffix:
                query = f"{query} {suffix}"
            queries.append(query.strip())
    return list(dict.fromkeys(queries))


def is_obviously_irrelevant_lead(text: str) -> bool:
    return any(
        re.search(pattern, text, re.I)
        for pattern in OBVIOUS_IRRELEVANT_LEAD_PATTERNS
    )


def is_media_or_content_channel(text: str) -> bool:
    value = clean_text(text).lower()
    if not value:
        return False
    media_signal = re.search(
        r"\b(news|media|journalist|newspaper|magazine|broadcast|broadcasting|tv channel|television|"
        r"podcast|vlog|blogger|youtuber|influencer|press agency|radio station)\b|"
        r"(телеканал|телевидение|новости|журналист|газета|сми|медиа|правозащитный|прецедент)",
        value,
        re.I,
    )
    if not media_signal:
        return False
    dealer_signal = re.search(
        r"\b(car dealer|dealership|auto dealer|vehicle dealer|car showroom|motors showroom|"
        r"auto trading|automotive trading|vehicle importer|car importer|vehicle distributor|"
        r"cars for sale|used cars|new cars|inventory|stock vehicles|showroom address|"
        r"sales department|book a test drive)\b",
        value,
        re.I,
    )
    return not bool(dealer_signal)


def is_youtube_automotive_lead(title: str, snippet: str, url: str = "") -> bool:
    text = clean_text(f"{title} {snippet} {url}").lower()
    if not text:
        return False
    sales_terms_pattern = (
        r"\b(car dealer|cars dealer|dealership|auto trading|automotive trading|"
        r"car showroom|motors showroom|used cars for sale|cars for sale|new cars for sale|luxury cars for sale|"
        r"car importer|vehicle importer|vehicle distributor|fleet sales|"
        r"vehicle procurement|inventory|stock vehicles|available for sale|"
        r"whatsapp|contact us|call us|showroom address)\b"
    )
    if re.search(
        r"\b(car review|reviews?|test drive|first drive|walkaround|pov|"
        r"owner review|comparison|top 10|news|launch event|trailer|"
        r"vlog|blogger|youtuber|influencer|media|magazine|tv channel)\b",
        text,
        re.I,
    ) and not re.search(sales_terms_pattern, text, re.I):
        return False
    if re.search(
        r"\b(motion capture|mocap|robotics?|humanoid|sensor|sensors|software|"
        r"gaming|game studio|animation|biomechanics|wearable technology|"
        r"industrial automation|simulation|developer platform)\b",
        text,
        re.I,
    ) and not re.search(
        r"\b(car dealer|dealership|auto trading|automotive trading|car showroom|"
        r"used cars|cars for sale|new cars|luxury cars|car importer|vehicle importer|"
        r"vehicle distributor|whatsapp|available for sale|car deals)\b",
        text,
        re.I,
    ):
        return False
    if re.search(
        r"\b(podcast|disruptors|wealth|money matrix|financial freedom|crypto|bitcoin|"
        r"motivational speaker|business coach|life coach|influencer|youtuber|"
        r"vlogger|vlogs?|travel vlog|food and tours|meals with|gaming|fitness|"
        r"boxing|mma|politics|tv channel|music channel|comedy channel)\b",
        text,
        re.I,
    ) and not re.search(
        r"\b(car dealer|dealership|auto trading|automotive trading|car showroom|"
        r"used cars|cars for sale|new cars|luxury cars|car importer|vehicle importer|"
        r"vehicle distributor|fleet sales|vehicle procurement)\b",
        text,
        re.I,
    ):
        return False
    strong_sales_terms = (
        "car dealer", "cars dealer", "dealership", "car showroom", "motors showroom",
        "auto trading", "automotive trading", "used cars", "cars for sale",
        "new cars", "pre owned cars", "pre-owned cars", "luxury cars",
        "car importer", "vehicle importer", "car distributor", "vehicle distributor",
        "car export", "vehicle export", "car deals", "available for sale",
        "brand-new cars", "brand new cars",
    )
    if any(term in text for term in strong_sales_terms):
        return True
    has_auto_subject = re.search(r"\b(car|cars|vehicle|vehicles|auto|automotive|motors)\b", text, re.I)
    has_trade_context = re.search(
        r"\b(showroom|dealer|dealers|importer|distributor|trading|sales|sell|buy|"
        r"offer|offers|price|prices|available|whatsapp|contact)\b",
        text,
        re.I,
    )
    return bool(has_auto_subject and has_trade_context)


def youtube_query_plan(
    searches: list[tuple[str, str]],
    source_mode: str,
    country: str = "",
) -> tuple[list[tuple[str, str]], int]:
    if source_mode == "youtube":
        query_limit = 6 if country_search_meta(country).get("code") == "qa" else 10
        per_query_limit = 12 if query_limit < 10 else 50
    elif source_mode == "social":
        query_limit, per_query_limit = 6, 8
    else:
        query_limit, per_query_limit = 5, 7
    deduped: list[tuple[str, str]] = []
    seen: set[str] = set()
    for query, account_type in searches:
        key = clean_text(query).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append((query, account_type))
        if len(deduped) >= query_limit:
            break
    return deduped, per_query_limit


def youtube_discovery_searches(
    country: str,
    cities: list[str],
    account_scope: str,
) -> list[tuple[str, str]]:
    country_code = country_search_meta(country).get("code", "").lower()
    if country_code == "qa":
        company_queries = [
            "Automall Qatar used cars",
            "Knightsbridge Automotive Qatar",
            "Diar Al Azz Cars Qatar",
            "AutoZ Qatar used cars",
            "QMotor Qatar cars",
            "Auto Class Qatar cars",
        ]
    else:
        active_places = list(dict.fromkeys([*(cities[:5]), country_search_meta(country).get("location", "")]))
        company_queries = [
            f"{place} {term}"
            for place in active_places
            if place
            for term in ("car dealer", "used cars", "car showroom")
        ]
    searches: list[tuple[str, str]] = []
    if account_scope in ("company", "both"):
        searches.extend((query, "company account") for query in company_queries)
    if account_scope in ("person", "both"):
        searches.extend(
            (f"{query} owner manager", "owner or manager account")
            for query in company_queries[:4]
        )
    return searches


YOUTUBE_LOCAL_AUTO_BRANDS = (
    "toyota", "lexus", "nissan", "infiniti", "renault", "hyundai", "genesis",
    "geely", "mg motor", "gac", "mitsubishi", "mercedes", "bmw", "mini",
    "jaguar", "land rover", "volvo", "honda", "ford", "kia", "jetour", "chery",
)

YOUTUBE_QATAR_VERIFIED_HANDLES = (
    "toyotaqatar", "lexusqatar", "nissanqatar580", "infinitiqtr1285",
    "renaultqatar3194", "hyundaiqatarskylineautomot4172", "geelyautoqatar",
    "mgmotorqatar", "gac-qatar", "mitsubishimotorsqatar", "nbkmercedesbenz",
    "alfardanautomobiles3090", "volvocarqatar", "qatarhonda", "fordqtr",
    "kiaqatar", "jetourqatar1", "cheryqatar6926",
)


def search_youtube_verified_handles(handles: tuple[str, ...], country: str) -> list[dict]:
    api_key = get_youtube_api_key()
    if not api_key:
        return []
    country_code = country_search_meta(country).get("code", "").upper()
    results: list[dict] = []
    for raw_handle in handles:
        handle = raw_handle.strip().lstrip("@")
        channel_params = {
            "part": "snippet,brandingSettings,contentDetails",
            "forHandle": handle,
            "fields": (
                "items(id,snippet(title,description,customUrl),brandingSettings(channel(country)),"
                "contentDetails(relatedPlaylists(uploads)))"
            ),
            "key": api_key,
        }
        try:
            channel_payload = fetch_json(
                "https://www.googleapis.com/youtube/v3/channels?" + urllib.parse.urlencode(channel_params),
                timeout=20,
            )
            record_api_usage("youtube", True, detail="channels.forHandle")
        except (OSError, ValueError, TimeoutError, http.client.HTTPException, json.JSONDecodeError):
            record_api_usage("youtube", False, detail="channels.forHandle")
            continue
        channel_items = channel_payload.get("items") if isinstance(channel_payload, dict) else None
        if not channel_items:
            continue
        channel = channel_items[0]
        snippet = channel.get("snippet") or {}
        branding = channel.get("brandingSettings") or {}
        channel_country = str((branding.get("channel") or {}).get("country") or "").upper()
        if country_code and channel_country and channel_country != country_code:
            continue
        uploads = (
            ((channel.get("contentDetails") or {}).get("relatedPlaylists") or {}).get("uploads")
            or ""
        )
        if not uploads:
            continue
        playlist_params = {
            "part": "snippet,contentDetails",
            "playlistId": uploads,
            "maxResults": "1",
            "fields": "items(snippet(title,description,publishedAt),contentDetails(videoPublishedAt))",
            "key": api_key,
        }
        try:
            playlist_payload = fetch_json(
                "https://www.googleapis.com/youtube/v3/playlistItems?" + urllib.parse.urlencode(playlist_params),
                timeout=20,
            )
            record_api_usage("youtube", True, detail="playlistItems.latest")
        except (OSError, ValueError, TimeoutError, http.client.HTTPException, json.JSONDecodeError):
            record_api_usage("youtube", False, detail="playlistItems.latest")
            continue
        playlist_items = playlist_payload.get("items") if isinstance(playlist_payload, dict) else None
        if not playlist_items:
            continue
        latest = playlist_items[0]
        latest_snippet = latest.get("snippet") or {}
        published_at = (
            (latest.get("contentDetails") or {}).get("videoPublishedAt")
            or latest_snippet.get("publishedAt")
            or ""
        )
        if not is_recent_youtube_video_date(published_at):
            continue
        custom_url = snippet.get("customUrl") or f"@{handle}"
        results.append({
            "title": snippet.get("title") or handle,
            "url": f"https://www.youtube.com/{custom_url}" if custom_url.startswith("@") else f"https://www.youtube.com/@{handle}",
            "snippet": clean_text(" ".join(filter(None, [
                snippet.get("description", ""),
                latest_snippet.get("title", ""),
                latest_snippet.get("description", ""),
            ])))[:1200],
            "handle": published_at,
            "channelId": channel.get("id", ""),
            "country": channel_country,
            "latestVideoPublishedAt": published_at,
            "latestVideoTitle": latest_snippet.get("title", ""),
            "apiSource": "YouTube Data API v3 verified handle",
            "youtubeVerifiedHandle": True,
        })
    return results


def is_local_official_youtube_auto_channel(item: dict, country: str) -> bool:
    if country_search_meta(country).get("code") != "qa":
        return False
    title = clean_text(str(item.get("title") or ""))
    snippet = clean_text(str(item.get("snippet") or ""))
    url = normalize_public_url(str(item.get("url") or ""))
    lower_title = title.lower()
    lower_text = f"{title} {snippet} {url}".lower()
    if any(region in lower_title for region in (
        "middle east", "mena", " mea", "europe", "global", "international",
        "usa", " uk", "bangladesh", "australia",
    )) and "qatar" not in lower_title:
        return False
    has_brand = any(brand in lower_title for brand in YOUTUBE_LOCAL_AUTO_BRANDS) or bool(
        item.get("youtubeVerifiedHandle")
        and has_automotive_business_signal(lower_text)
    )
    has_market_identity = bool(
        "qatar" in lower_title
        or (
            re.search(r"(?:qatar|doha|\bqa\b|\bqtr\b)", lower_text, re.I)
            and (item.get("country") == "QA" or item.get("youtubeVerifiedHandle"))
        )
    )
    has_official_identity = bool(
        re.search(r"\b(official|exclusive agent|exclusive dealer|official distributor)\b", lower_text)
        or item.get("country") == "QA"
        or re.search(r"(?:qatar|qtr|qa)(?:\d+)?/?$", safe_urlparse(url).path.lower())
        or "qatar" in lower_title
    )
    return bool(has_brand and has_market_identity and has_official_identity)


def discovery_source_bucket(item: dict) -> str:
    origin = str(item.get("origin") or "").lower()
    source_type = str(item.get("source_type") or "").lower()
    url = str(item.get("url") or item.get("source_url") or "").lower()
    value = f"{origin} {source_type} {url}"
    if "google" in value:
        return "google"
    if "openstreetmap" in value or "osm" in value:
        return "osm"
    if any(name in value for name in (
        "youtube", "youtu.be", "instagram", "facebook", "tiktok", "linkedin",
        "telegram", "t.me", "twitter", "x.com", "threads", "pinterest", "reddit", "vk.com",
    )):
        return "social"
    return "web"


def balance_discovery_sources(items: list[dict]) -> list[dict]:
    buckets: dict[str, list[dict]] = {"google": [], "osm": [], "web": [], "social": []}
    for item in items:
        buckets.setdefault(discovery_source_bucket(item), []).append(item)
    order = ["google", "web", "social", "osm"]
    configured = admin_control_settings().get("discovery", {}).get("sourceWeights") or {}
    weights = {
        "google": int(configured.get("google", 3)),
        "web": int(configured.get("dealer", 3)),
        "social": max(int(configured.get(key, 0)) for key in ("instagram", "facebook", "tiktok", "youtube", "linkedin")),
        "osm": int(configured.get("osm", 1)),
    }
    balanced = []
    while any(buckets.get(key) for key in order):
        for key in order:
            for _ in range(max(1, weights.get(key, 1))):
                if buckets.get(key):
                    balanced.append(buckets[key].pop(0))
    return balanced


def soften_dominant_discovery_sources(items: list[dict], source_mode: str, result_limit: int) -> list[dict]:
    if source_mode == "youtube":
        return items
    youtube_soft_cap = max(6, min(14, max(1, result_limit // 3)))
    kept: list[dict] = []
    delayed: list[dict] = []
    origin_counts: dict[str, int] = {}
    for item in items:
        origin = str(item.get("origin") or "")
        if origin == "YouTube":
            origin_counts[origin] = origin_counts.get(origin, 0) + 1
            if origin_counts[origin] > youtube_soft_cap:
                delayed.append(item)
                continue
        kept.append(item)
    return kept + delayed


def apply_configured_source_caps(items: list[dict], country: str = "", source_mode: str = "") -> list[dict]:
    counts: dict[str, int] = {}
    kept = []
    for item in items:
        origin = str(item.get("origin") or "").lower()
        if "instagram" in origin:
            source = "instagram"
        elif "facebook" in origin:
            source = "facebook"
        elif "tiktok" in origin:
            source = "tiktok"
        elif "youtube" in origin:
            source = "youtube"
        elif "linkedin" in origin:
            source = "linkedin"
        else:
            bucket = discovery_source_bucket(item)
            source = "dealer" if bucket == "web" else bucket
        source_limit = discovery_source_cap(source)
        if source == "dealer" and source_mode in ("all", "combined"):
            source_limit = max(source_limit, 70)
        counts[source] = counts.get(source, 0) + 1
        if counts[source] <= source_limit:
            kept.append(item)
    return kept


TARGET_PROFILES = {
    "importer": {
        "label": "汽车进口商",
        "query": "automotive importer vehicle distributor import company",
        "osm": ('nwr["shop"="car"]',),
    },
    "dealer": {
        "label": "经销商和展厅",
        "query": "car dealer dealership auto showroom motors",
        "osm": ('nwr["shop"="car"]',),
    },
    "parallel": {
        "label": "平行进口商",
        "query": "parallel import car dealer grey market vehicle importer",
        "osm": ('nwr["shop"="car"]',),
    },
    "fleet": {
        "label": "租赁和车队公司",
        "query": "car rental fleet operator chauffeur company corporate fleet",
        "osm": ('nwr["amenity"="car_rental"]', 'nwr["shop"="car_rental"]'),
    },
    "corporate": {
        "label": "企业采购",
        "query": "company fleet procurement vehicle tender corporate buyer",
        "osm": (),
    },
    "government": {
        "label": "政府项目",
        "query": "government vehicle tender public procurement fleet project",
        "osm": (),
    },
    "individual": {
        "label": "个人买家",
        "query": "looking to buy Chinese electric SUV buyer wanted",
        "osm": (),
    },
    "buying": {
        "label": "正在发布求购信息的客户",
        "query": "buying request wanted car buyer RFQ vehicle procurement",
        "osm": (),
    },
}

IMPORT_BUSINESS_TERMS = (
    "importer", "vehicle import", "car import", "automotive import", "parallel import",
    "distributor", "distribution", "dealership", "dealer", "showroom", "motors",
    "automotive trading", "auto trading", "general trading", "fleet", "procurement",
)

BUYING_INTENT_TERMS = (
    "looking for distributor", "seeking distributor", "dealer wanted", "distributor wanted",
    "new brand", "add new brand", "brand partnership", "distribution opportunity",
    "dealership opportunity", "import partnership", "become a dealer", "become a distributor",
    "request for quotation", "rfq", "vehicle procurement", "fleet purchase", "bulk order",
    "looking to buy", "wanted vehicles", "sourcing vehicles", "supplier wanted",
)

BLOCKED_DOMAINS = (
    "baike.baidu.com",
    "wikipedia.org",
    "wikimedia.org",
    "ytcfg.set",
    "youtube.com",
    "youtu.be",
    "ytimg.com",
    "iytimg.com",
    "ggpht.com",
    "gstatic.com",
    "googleusercontent.com",
    "doubleclick.net",
    "googletagmanager.com",
    "google-analytics.com",
    "google.com",
    "google.cn",
    "googleapis.com",
    "youtubei-att.googleapis.com",
    "googlevideo.com",
    "schema.org",
    "w3.org",
    "window.ytplayer",
    "client-channel.google",
    "client.version",
    "x22client.version",
    "channel.about",
    "payments.yo",
    "payments.youtu",
    "cgtn.com",
    "cgtnamerica.com",
    "bing.com",
    "facebook.com/search",
    "linkedin.com/jobs",
    "visitdubai.com",
    "tripadvisor.",
    "booking.com",
)

BLOCKED_TITLE_WORDS = (
    "wikipedia",
    "百科",
    "definition",
    "map",
    "jobs",
    "招聘",
    "news",
    "新闻",
    "tourism",
    "travel",
    "attractions",
    "directory",
    "list of",
    "top 10",
    "best car dealers",
)

BLOCKED_PATH_PARTS = (
    "/blog/",
    "/blogs/",
    "/news/",
    "/article/",
    "/articles/",
    "/press-release",
    "/listings/",
    "/listing/",
    "/product/",
    "/products/",
)


def fetch_text(url: str, timeout: int = 10) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        try:
            raw = response.read(600_000)
        except http.client.IncompleteRead as exc:
            raw = exc.partial or b""
        charset = response.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="ignore")


def fetch_document(url: str, timeout: int = 10, user_agent: str = "") -> tuple[str, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        try:
            raw = response.read(1_200_000)
        except http.client.IncompleteRead as exc:
            raw = exc.partial or b""
        charset = response.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="ignore"), response.geturl()


def fetch_json(url: str, timeout: int = 10, headers: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124 Safari/537.36",
            "Accept": "application/json",
            **(headers or {}),
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        try:
            raw = response.read(1_200_000)
        except http.client.IncompleteRead as exc:
            raw = exc.partial or b""
        charset = response.headers.get_content_charset() or "utf-8"
        data = json.loads(raw.decode(charset, errors="ignore"))
        return data if isinstance(data, dict) else {}


def post_json_value(url: str, payload: dict, timeout: int = 30, headers: dict | None = None):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "User-Agent": "HuaweiEVLeadTool/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            **(headers or {}),
        },
    )
    try:
        response_context = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", None)
        is_apify = safe_urlparse(url).netloc.lower() == "api.apify.com"
        if not (
            is_apify
            and isinstance(reason, ssl.SSLError)
            and "CERTIFICATE_VERIFY_FAILED" in str(reason)
        ):
            raise
        response_context = urllib.request.urlopen(
            req,
            timeout=timeout,
            context=ssl._create_unverified_context(),
        )
    with response_context as response:
        try:
            raw = response.read(2_000_000)
        except http.client.IncompleteRead as exc:
            raw = exc.partial or b""
        charset = response.headers.get_content_charset() or "utf-8"
        if not raw:
            return None
        return json.loads(raw.decode(charset, errors="ignore"))


def fetch_json_value(url: str, timeout: int = 30, headers: dict | None = None):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HuaweiEVLeadTool/1.0",
            "Accept": "application/json",
            **(headers or {}),
        },
    )
    try:
        response_context = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", None)
        is_apify = safe_urlparse(url).netloc.lower() == "api.apify.com"
        if not (
            is_apify
            and isinstance(reason, ssl.SSLError)
            and "CERTIFICATE_VERIFY_FAILED" in str(reason)
        ):
            raise
        response_context = urllib.request.urlopen(
            req,
            timeout=timeout,
            context=ssl._create_unverified_context(),
        )
    with response_context as response:
        try:
            raw = response.read(4_000_000)
        except http.client.IncompleteRead as exc:
            raw = exc.partial or b""
        if not raw:
            return None
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(raw.decode(charset, errors="ignore"))


def clean_text(value: str) -> str:
    value = re.sub(r"<script[\s\S]*?</script>", " ", value, flags=re.I)
    value = re.sub(r"<style[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def load_social_captures(owner_username: str) -> list[dict]:
    if not SOCIAL_CAPTURE_FILE.exists():
        return []
    try:
        data = json.loads(SOCIAL_CAPTURE_FILE.read_text(encoding="utf-8"))
        return [item for item in data if isinstance(item, dict) and item.get("ownerUsername", "admin") == owner_username] if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_social_capture(payload: dict, owner_username: str) -> dict:
    SOCIAL_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    capture_id = uuid.uuid4().hex
    screenshot_data = str(payload.pop("screenshotData", "") or "")
    screenshot_url = ""
    if screenshot_data.startswith("data:image/png;base64,"):
        try:
            screenshot_bytes = base64.b64decode(screenshot_data.split(",", 1)[1], validate=True)
            if len(screenshot_bytes) <= 8_000_000:
                screenshot_path = SOCIAL_CAPTURE_DIR / f"{capture_id}.png"
                screenshot_path.write_bytes(screenshot_bytes)
                public_base = public_base_url() or f"http://127.0.0.1:{PORT}"
                screenshot_url = f"{public_base}/social-captures/{capture_id}.png"
        except (ValueError, OSError):
            screenshot_url = ""
    record = {
        "id": capture_id,
        "ownerUsername": owner_username,
        "platform": clean_text(str(payload.get("platform", "")))[:40],
        "title": clean_text(str(payload.get("title", "")))[:200],
        "url": normalize_public_url(str(payload.get("url", ""))),
        "text": clean_text(str(payload.get("text", "")))[:12_000],
        "emails": list(dict.fromkeys(
            clean_text(str(value)).lower()
            for value in (payload.get("emails") or [])
            if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", clean_text(str(value)))
        ))[:20],
        "phones": list(dict.fromkeys(
            clean_text(str(value))
            for value in (payload.get("phones") or [])
            if clean_text(str(value))
        ))[:20],
        "links": [
            {
                "url": normalize_public_url(str(item.get("url", ""))),
                "text": clean_text(str(item.get("text", "")))[:160],
            }
            for item in (payload.get("links") or [])[:80]
            if isinstance(item, dict) and item.get("url")
        ],
        "screenshotUrl": screenshot_url,
        "capturedAt": clean_text(str(payload.get("capturedAt", ""))) or datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    with SOCIAL_CAPTURE_LOCK:
        try:
            captures = json.loads(SOCIAL_CAPTURE_FILE.read_text(encoding="utf-8")) if SOCIAL_CAPTURE_FILE.exists() else []
        except (OSError, json.JSONDecodeError):
            captures = []
        if not isinstance(captures, list):
            captures = []
        captures.insert(0, record)
        SOCIAL_CAPTURE_FILE.write_text(
            json.dumps(captures[:200], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return record


def normalize_public_url(value: str) -> str:
    value = html.unescape(value or "").strip()
    if not value:
        return ""
    if value.startswith("//"):
        value = "https:" + value
    elif not re.match(r"^https?://", value, flags=re.I):
        value = "https://" + value.lstrip("/")
    try:
        parsed = urllib.parse.urlparse(value)
    except ValueError:
        return ""
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return value


def safe_urlparse(value: str):
    try:
        return urllib.parse.urlparse(normalize_public_url(value))
    except ValueError:
        return urllib.parse.urlparse("")


def is_valid_http_url(value: str) -> bool:
    parsed = safe_urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


SOCIAL_OR_PLATFORM_DOMAINS = (
    "instagram.com", "facebook.com", "linkedin.com", "tiktok.com",
    "tiktokcdn.com", "tiktokcdn-us.com", "tiktokv.us", "tiktokw.us",
    "byteoversea.com", "ibytedtos.com", "ibyteimg.com", "muscdn.com",
    "youtube.com", "youtu.be", "t.me", "telegram.me", "telegram.dog",
    "x.com", "twitter.com", "threads.net", "pinterest.", "reddit.com",
    "vk.com", "wa.me", "whatsapp.com", "linktr.ee", "beacons.ai",
    "taplink.", "bit.ly", "tinyurl.com",
)

STATIC_ASSET_DOMAINS = (
    "bootstrap", "jquery", "fontawesome", "cloudflare", "cloudfront.net",
    "jsdelivr.net", "unpkg.com", "cdnjs.", "akamai", "dlron.us",
    "dealerinspire.com", "dealer.com", "carsforsale.com",
)

SCRIPT_PSEUDO_WEBSITE_DOMAINS = (
    "ytcfg.set",
    "ytinitialdata.",
    "ytinitialplayerresponse.",
    "window.ytplayer",
    "client-channel.google",
    "client.version",
    "x22client.version",
    "channel.about",
    "payments.yo",
    "payments.youtu",
)

NON_CUSTOMER_WEBSITE_DOMAINS = (
    "window.",
    "player.",
    "embed.",
    "widget.",
    "widgets.",
    "analytics.",
    "tracking.",
    "pixel.",
    "ads.",
    "kfc.",
    "mcdonalds.",
    "burgerking.",
    "pizzahut.",
    "dominos.",
    "starbucks.",
)

NON_CUSTOMER_WEBSITE_PATHS = (
    "/generate_204", "/gen_204", "/favicon", "/pixel", "/collect",
    "/analytics", "/ads/", "/static/", "/assets/", "/cdn-cgi/",
    "/embed/", "/iframe/", "/player/", "/watch_fragments",
)

MAX_LEADS_PER_CUSTOMER_WEBSITE = 5


def is_business_website_url(url: str) -> bool:
    normalized = normalize_public_url(url)
    if not normalized:
        return False
    parsed = safe_urlparse(normalized)
    domain = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.lower()
    lowered = normalized.lower()
    if not domain or "." not in domain:
        return False
    if any(pseudo in lowered or pseudo in domain for pseudo in SCRIPT_PSEUDO_WEBSITE_DOMAINS):
        return False
    if (
        domain.endswith((".ytplayer", ".js", ".css"))
        or "ytplayer" in domain
        or "ytplayer" in lowered
        or domain.endswith("ggpht.com")
    ):
        return False
    if any(blocked in domain for blocked in BLOCKED_DOMAINS):
        return False
    if any(blocked in domain for blocked in NON_CUSTOMER_WEBSITE_DOMAINS):
        return False
    if domain.startswith(("cdn.", "static.", "assets.", "img.", "images.", "media.")):
        return False
    if any(asset in domain for asset in STATIC_ASSET_DOMAINS):
        return False
    if any(platform in domain for platform in SOCIAL_OR_PLATFORM_DOMAINS):
        return False
    if any(domain == operator or domain.endswith(f".{operator}") for operator in local_discovery_domains()):
        return False
    if any(part in path for part in NON_CUSTOMER_WEBSITE_PATHS):
        return False
    if re.search(r"\.(?:png|jpe?g|gif|svg|webp|css|js|ico|json|xml|txt|pdf)$", path):
        return False
    return True


def has_automotive_business_signal(text: str) -> bool:
    return bool(re.search(
        r"\b(auto|automotive|car|cars|vehicle|vehicles|motor|motors|dealership|dealer|"
        r"showroom|importer|distributor|fleet|rental|garage|used cars|new cars|"
        r"luxury cars|pre-owned|spare parts|workshop|4x4|suv|ev|electric vehicle)\b|"
        r"(汽车|车辆|车商|经销|展厅|进口|平行进口|车队|租赁|新能源|电动车)",
        clean_text(text),
        re.I,
    ))


def customer_website_key(url: str) -> str:
    if not is_business_website_url(url):
        return ""
    parsed = safe_urlparse(url)
    return parsed.netloc.lower().removeprefix("www.")


def limit_duplicate_customer_websites(leads: list[dict], max_per_website: int = MAX_LEADS_PER_CUSTOMER_WEBSITE) -> list[dict]:
    counts: dict[str, int] = {}
    kept: list[dict] = []
    for lead in leads:
        key = customer_website_key(str(lead.get("customerWebsite") or ""))
        if key:
            next_count = counts.get(key, 0) + 1
            if next_count > max_per_website:
                continue
            counts[key] = next_count
        kept.append(lead)
    return kept


def is_noise_source_url(url: str) -> bool:
    normalized = normalize_public_url(url).lower()
    if not normalized:
        return True
    parsed = safe_urlparse(normalized)
    domain = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.lower()
    if domain in {"window.ytplayer", "about:blank"}:
        return True
    if "ytplayer" in normalized or "youtube-nocookie.com/embed" in normalized:
        return True
    if any(part in path for part in ("/embed/", "/iframe/", "/player/")) and (
        "youtube" in domain or "youtu.be" in domain
    ):
        return True
    return False


def unwrap_public_redirect_url(url: str) -> str:
    url = (
        str(url or "")
        .replace("\\u0026", "&")
        .replace("\\u003d", "=")
        .replace("\\/", "/")
    )
    normalized = normalize_public_url(url)
    parsed = safe_urlparse(normalized)
    domain = parsed.netloc.lower().removeprefix("www.")
    if not domain:
        return normalized
    params = urllib.parse.parse_qs(parsed.query)
    redirect_keys = ("q", "url", "u", "target", "redirect", "redir", "uddg")
    if any(host in domain for host in ("youtube.com", "youtu.be", "google.com", "bing.com", "duckduckgo.com", "facebook.com", "l.facebook.com")):
        for key in redirect_keys:
            for value in params.get(key, []):
                candidate = html.unescape(value).strip()
                if candidate and re.match(r"^https?://|^www\.|^(?:[a-z0-9-]+\.)+[a-z]{2,}", candidate, flags=re.I):
                    return normalize_public_url(candidate)
    return normalized


def extract_business_websites(page: str) -> list[str]:
    page = (
        str(page or "")
        .replace("\\u0026", "&")
        .replace("\\u003d", "=")
        .replace("\\/", "/")
    )
    candidates = []
    for value in re.findall(r'https?://[^"\'\s<]+|www\.[^\s<>"\']+', page, flags=re.I):
        value = html.unescape(value).rstrip(".,;:)]}'\"")
        if value.startswith("www."):
            value = f"https://{value}"
        value = unwrap_public_redirect_url(value)
        if is_business_website_url(value):
            candidates.append(normalize_public_url(value))
    text = clean_text(page)
    for value in re.findall(
        r"(?<![@/\w.-])(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s<>'\"]*)?",
        text,
        flags=re.I,
    ):
        value = html.unescape(value).rstrip(".,;:)]}'\"")
        domain = safe_urlparse(value).netloc.lower()
        if domain in {"example.com", "example.org", "example.net", "mail.com"}:
            continue
        if is_business_website_url(value):
            candidates.append(normalize_public_url(value))
    return list(dict.fromkeys(candidates))[:8]


def is_social_profile_url(url: str) -> bool:
    parsed = safe_urlparse(url)
    domain = parsed.netloc.lower().removeprefix("www.")
    parts = [part for part in parsed.path.split("/") if part]
    if "instagram.com" in domain:
        return bool(parts) and parts[0].lower() not in {"stories", "explore", "accounts", "about"}
    if "facebook.com" in domain:
        if parsed.path.lower() == "/profile.php":
            return bool(urllib.parse.parse_qs(parsed.query).get("id"))
        if len(parts) == 1:
            return parts[0].lower() not in {
                "share", "tr", "plugins", "sharer", "dialog", "login", "marketplace",
            }
        return parts[0].lower() not in {"tr", "plugins", "sharer", "dialog", "login"}
    if "linkedin.com" in domain:
        return bool(parts) and parts[0].lower() in {"company", "in", "posts", "feed", "pulse"}
    if "youtube.com" in domain:
        return bool(parts) and (parts[0].startswith("@") or parts[0].lower() in {"user", "channel", "c", "watch", "shorts"})
    if "tiktok.com" in domain:
        return bool(parts) and (parts[0].startswith("@") or parts[0].lower() in {"tag", "discover"})
    if domain in {"t.me", "telegram.me", "telegram.dog"}:
        if len(parts) >= 2 and parts[0].lower() == "s":
            return parts[1].lower() not in {"share", "iv", "username"}
        return bool(parts) and parts[0].lower() not in {"s", "share", "iv", "username"}
    if "tgstat." in domain:
        return len(parts) >= 2 and parts[0].lower() in {"channel", "chat"}
    if "telemetr." in domain:
        lower_parts = [part.lower() for part in parts]
        return "channels" in lower_parts and lower_parts.index("channels") < len(parts) - 1
    if "telegramchannels." in domain:
        return len(parts) >= 2 and parts[0].lower() in {"channels", "groups"}
    if "tgram." in domain:
        return len(parts) >= 2 and parts[0].lower() in {"channel", "channels", "chat", "joinchat"}
    if "tlgrm." in domain:
        return (
            domain in {"tlgrm.eu", "www.tlgrm.eu"}
            and len(parts) >= 2
            and parts[0].lower() in {"channels", "chat"}
        )
    if "x.com" in domain or "twitter.com" in domain:
        if len(parts) >= 3 and parts[1].lower() == "status":
            return parts[0].lower() not in {"i", "intent", "share", "search"}
        return len(parts) == 1 and parts[0].lower() not in {"search", "share", "intent", "home", "explore", "i"}
    if "threads.net" in domain:
        return bool(parts) and parts[0].startswith("@")
    if "pinterest." in domain:
        return bool(parts) and parts[0].lower() not in {"search", "ideas"}
    if "reddit.com" in domain:
        return len(parts) >= 2 and parts[0].lower() in {"r", "user", "u"}
    if "vk.com" in domain:
        return bool(parts) and parts[0].lower() not in {"feed", "search", "share", "login"}
    return False


def normalize_social_profile_url(url: str) -> str:
    normalized = normalize_public_url(url)
    parsed = safe_urlparse(normalized)
    domain = parsed.netloc.lower().removeprefix("www.")
    parts = [part for part in parsed.path.split("/") if part]
    if domain in {"t.me", "telegram.me", "telegram.dog"} and len(parts) >= 2 and parts[0].lower() == "s":
        return f"https://t.me/{parts[1]}"
    return normalized


def text_from_runs(value) -> str:
    if not isinstance(value, dict):
        return ""
    if value.get("simpleText"):
        return clean_text(value["simpleText"])
    return clean_text("".join(run.get("text", "") for run in value.get("runs", [])))


def parse_meta_tags(page: str) -> dict:
    values = {}
    for tag in re.findall(r"<meta\b[^>]*>", page, flags=re.I):
        attrs = {
            key.lower(): html.unescape(value)
            for key, value in re.findall(r'([\w:-]+)=["\']([^"\']*)["\']', tag)
        }
        name = attrs.get("property") or attrs.get("name")
        content = attrs.get("content")
        if name and content and name not in values:
            values[name] = clean_text(content)
    return values


def social_platform(url: str) -> str:
    domain = safe_urlparse(url).netloc.lower()
    if "facebook.com" in domain:
        return "Facebook"
    if "instagram.com" in domain:
        return "Instagram"
    if "youtube.com" in domain or "youtu.be" in domain:
        return "YouTube"
    if "linkedin.com" in domain:
        return "LinkedIn"
    if "tiktok.com" in domain:
        return "TikTok"
    if (
        domain.endswith("t.me")
        or "telegram." in domain
        or any(name in domain for name in ("tgstat.", "telemetr.", "telegramchannels.", "tgram.", "tlgrm."))
    ):
        return "Telegram"
    if "x.com" in domain or "twitter.com" in domain:
        return "X / Twitter"
    if "threads.net" in domain:
        return "Threads"
    if "pinterest." in domain:
        return "Pinterest"
    if "reddit.com" in domain:
        return "Reddit"
    if "vk.com" in domain:
        return "VK"
    return "社交媒体"


def analyze_social_business_profile(
    text: str,
    platform: str = "",
    account_type: str = "",
) -> dict:
    lower = clean_text(text).lower()
    business_terms = {
        "汽车进口": ("vehicle importer", "car importer", "automotive importer", "parallel import"),
        "汽车经销": ("car dealer", "dealership", "showroom", "auto trading", "motors"),
        "品牌分销": ("distributor", "distribution", "authorized dealer", "brand partner"),
        "新能源业务": ("electric vehicle", "electric cars", " ev ", "hybrid", "new energy", "chinese cars"),
        "车队采购": ("fleet", "procurement", "corporate sales", "rental", "chauffeur"),
        "批发贸易": ("wholesale", "bulk sales", "import export", "trading company"),
    }
    intent_terms = {
        "公开询价": ("rfq", "request for quotation", "quotation request"),
        "正在采购": ("looking to buy", "want to buy", "vehicle procurement", "sourcing vehicles"),
        "寻找供应商": ("supplier wanted", "looking for supplier", "seeking supplier"),
        "招募经销商": ("dealer wanted", "distributor wanted", "seeking distributor"),
        "寻求品牌合作": ("brand partnership", "new brand", "distribution opportunity", "dealership opportunity"),
        "批量采购": ("bulk order", "fleet purchase", "wholesale order"),
    }
    decision_roles = {
        "老板/创始人": ("owner", "founder", "co-founder", "proprietor", "ceo"),
        "总经理": ("general manager", "managing director", "director"),
        "采购负责人": ("procurement manager", "purchasing manager", "buyer", "sourcing manager"),
        "进口负责人": ("import manager", "import director"),
        "销售负责人": ("sales director", "sales manager", "business development manager"),
        "车队负责人": ("fleet manager", "fleet director"),
    }
    business_signals = [
        label for label, terms in business_terms.items()
        if any(term in lower for term in terms)
    ]
    intent_signals = [
        label for label, terms in intent_terms.items()
        if any(term in lower for term in terms)
    ]
    role = next(
        (
            label
            for label, terms in decision_roles.items()
            if any(re.search(rf"\b{re.escape(term)}\b", lower) for term in terms)
        ),
        "",
    )
    contact_signals = []
    if re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", lower, re.I):
        contact_signals.append("公开邮箱")
    if "whatsapp" in lower or "wa.me/" in lower:
        contact_signals.append("公开 WhatsApp")
    if re.search(r"(?:tel|phone|call|mobile)[:\s+]", lower, re.I):
        contact_signals.append("公开电话")
    if any(term in lower for term in ("website", "official site", "link in bio", "www.", "http")):
        contact_signals.append("公开官网链接")

    company_markers = (
        "official", "company", "group", "motors", "automotive", "trading",
        "showroom", "dealer", "importer", "distributor", "cars", "autos",
        "auto ", "vehicles", "luxury car", "supercar",
    )
    person_markers = (
        "owner", "founder", "manager", "director", "ceo", "entrepreneur",
    )
    explicit_person_type = "个人" in account_type and "待核验" not in account_type
    explicit_company_type = "公司" in account_type and "待核验" not in account_type
    if role or explicit_person_type or any(marker in lower for marker in person_markers):
        detected_type = "个人决策人"
    elif business_signals or explicit_company_type or any(marker in lower for marker in company_markers):
        detected_type = "公司商业账号"
    else:
        detected_type = "账号类型待核验"

    confidence = 15
    confidence += min(36, len(business_signals) * 12)
    confidence += min(24, len(intent_signals) * 12)
    confidence += 12 if role else 0
    confidence += min(12, len(contact_signals) * 4)
    if platform:
        confidence += 3
    confidence = min(confidence, 96)
    has_company_marker = any(marker in lower for marker in company_markers)
    has_automotive_marker = any(
        marker in lower
        for marker in (
            "car", "cars", "auto", "automotive", "vehicle", "vehicles",
            "motors", "showroom", "dealer", "importer", "fleet",
        )
    )
    return {
        "accountType": detected_type,
        "businessSignals": business_signals[:5],
        "intentSignals": intent_signals[:5],
        "decisionRole": role,
        "contactSignals": contact_signals,
        "businessConfidence": confidence,
        "hasAutomotiveMarker": has_automotive_marker,
        "hasCompanyMarker": has_company_marker,
        "isCommercial": bool(
            business_signals
            or intent_signals
            or role
            or (has_company_marker and has_automotive_marker)
        ),
    }


def is_social_auth_redirect(original_url: str, final_url: str) -> bool:
    original_platform = social_platform(original_url)
    final_platform = social_platform(final_url)
    if original_platform and final_platform != original_platform:
        return True
    path = safe_urlparse(final_url).path.lower().rstrip("/")
    return path in {"/login", "/checkpoint", "/recover", "/privacy/consent"} or path.startswith(
        ("/login/", "/checkpoint/", "/recover/")
    )


def parse_tiktok_public_profile(page: str) -> dict:
    match = re.search(
        r'<script[^>]+id=["\']__UNIVERSAL_DATA_FOR_REHYDRATION__["\'][^>]*>([\s\S]*?)</script>',
        page,
        flags=re.I,
    )
    if not match:
        return {}
    try:
        payload = json.loads(html.unescape(match.group(1)).strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}
    scope = payload.get("__DEFAULT_SCOPE__") if isinstance(payload, dict) else None
    detail = scope.get("webapp.user-detail") if isinstance(scope, dict) else None
    user_info = detail.get("userInfo") if isinstance(detail, dict) else None
    user = user_info.get("user") if isinstance(user_info, dict) else None
    stats = user_info.get("stats") if isinstance(user_info, dict) else None
    if not isinstance(user, dict):
        return {}
    return {
        "handle": clean_text(str(user.get("uniqueId") or "")),
        "title": clean_text(str(user.get("nickname") or user.get("uniqueId") or "")),
        "description": clean_text(str(user.get("signature") or "")),
        "followers": stats.get("followerCount") if isinstance(stats, dict) else "",
        "isOrganization": user.get("isOrganization") == 1,
        "private": user.get("privateAccount") is True,
        "verified": user.get("verified") is True,
    }


def read_instagram_profile_via_apify(url: str) -> dict:
    token = get_apify_api_token()
    if not token:
        return {}
    fields = (
        "inputUrl", "url", "username", "fullName", "biography", "externalUrl", "externalUrls",
        "isBusinessAccount", "businessCategoryName", "businessAddress", "followersCount",
        "postsCount", "cityName", "addressStreet", "businessEmail", "businessPhoneNumber",
        "private", "verified", "error", "errorDescription",
    )
    try:
        items, status = run_apify_actor_dataset(
            "apify/instagram-scraper",
            {
                "directUrls": [url],
                "resultsType": "details",
                "resultsLimit": 1,
                "addParentData": False,
            },
            token,
            APIFY_RUN_TIMEOUT_SECONDS,
            2,
            fields,
        )
    except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
        record_api_usage("apify:instagram", False, detail="apify/instagram-scraper:manual-profile")
        return {}
    record_api_usage("apify:instagram", bool(items), detail=f"apify/instagram-scraper:{status}:manual-profile")
    expected_handle = safe_urlparse(url).path.strip("/").split("/")[-1].lower()
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("error") == "not_found":
            return {"handle": expected_handle, "notFound": True}
        if item.get("error") or item.get("private") is True:
            continue
        handle = clean_text(str(item.get("username") or "")).lstrip("@").lower()
        if handle != expected_handle:
            continue
        description_parts = [
            item.get("biography"), item.get("businessCategoryName"), item.get("businessAddress"),
            item.get("cityName"), item.get("addressStreet"), item.get("businessEmail"),
            item.get("businessPhoneNumber"),
        ]
        return {
            "handle": handle,
            "title": clean_text(str(item.get("fullName") or handle)),
            "description": clean_text(" ".join(str(value) for value in description_parts if value)),
            "externalWebsites": apify_external_links(item),
            "email": clean_text(str(item.get("businessEmail") or "")),
            "phone": clean_text(str(item.get("businessPhoneNumber") or "")),
            "isOrganization": item.get("isBusinessAccount") is True,
            "verified": item.get("verified") is True,
            "followers": item.get("followersCount") or "",
        }
    return {}


def read_social_profile(
    url: str,
    account_type: str = "公司账号",
    relationship: str = "公开搜索",
    fetch_remote: bool = True,
) -> dict:
    url = normalize_public_url(url)
    platform = social_platform(url)
    parsed = safe_urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    handle = parts[-1] if parts else parsed.netloc
    if platform == "LinkedIn" and parts and parts[0].lower() == "in":
        account_type = "个人决策人"
    if (
        platform == "TikTok"
        and handle.startswith("@")
        and account_type == "公司账号"
        and "官网直接链接" not in relationship
    ):
        account_type = "公开账号（公司/个人待核验）"
    user_agent = (
        "Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) "
        "WindowsPowerShell/5.1.19041.906"
        if platform == "Facebook"
        else ""
    )
    title = f"{platform} · {handle}"
    description = ""
    final_url = url
    external_websites: list[str] = []
    platform_confirmed_organization = False
    profile_not_found = False
    public_email = ""
    public_phone = ""
    try:
        if not fetch_remote:
            raise TimeoutError("skip remote social fetch")
        page, final_url = fetch_document(url, timeout=18, user_agent=user_agent)
        if is_social_auth_redirect(url, final_url):
            final_url = url
        page_contacts = extract_public_contacts(page)
        external_websites = (
            []
            if platform in {"Instagram", "TikTok"}
            else page_contacts.get("websites") or []
        )
        meta = parse_meta_tags(page)
        title = meta.get("og:title") or meta.get("twitter:title") or title
        description = (
            meta.get("og:description")
            or meta.get("twitter:description")
            or meta.get("description")
            or ""
        )
        if platform == "TikTok":
            public_profile = parse_tiktok_public_profile(page)
            if public_profile:
                handle = public_profile.get("handle") or handle
                title = public_profile.get("title") or title
                description = public_profile.get("description") or description
                if public_profile.get("followers"):
                    description = clean_text(f"{description} followers {public_profile['followers']}")
                if public_profile.get("isOrganization"):
                    account_type = "公司账号"
                    platform_confirmed_organization = True
        if platform == "YouTube":
            title = meta.get("og:title") or title
            description = meta.get("og:description") or meta.get("description") or description
            about_url = final_url.rstrip("/") + "/about" if "/about" not in safe_urlparse(final_url).path else final_url
            try:
                about_page, about_final_url = fetch_document(about_url, timeout=18)
                about_contacts = extract_public_contacts(about_page)
                external_websites = list(dict.fromkeys([
                    *external_websites,
                    *(about_contacts.get("websites") or []),
                ]))
                about_meta = parse_meta_tags(about_page)
                title = about_meta.get("og:title") or about_meta.get("twitter:title") or title
                description = (
                    about_meta.get("og:description")
                    or about_meta.get("twitter:description")
                    or about_meta.get("description")
                    or description
                )
                final_url = about_final_url.replace("/about", "")
            except (OSError, TimeoutError, UnicodeError):
                pass
    except (OSError, TimeoutError, UnicodeError):
        pass
    if platform == "Instagram" and fetch_remote and not description:
        apify_profile = read_instagram_profile_via_apify(url)
        if apify_profile:
            profile_not_found = apify_profile.get("notFound") is True
            handle = apify_profile.get("handle") or handle
            title = apify_profile.get("title") or title
            description = apify_profile.get("description") or description
            external_websites = list(dict.fromkeys([
                *external_websites,
                *(apify_profile.get("externalWebsites") or []),
            ]))
            public_email = apify_profile.get("email") or ""
            public_phone = apify_profile.get("phone") or ""
            if apify_profile.get("followers"):
                description = clean_text(f"{description} followers {apify_profile['followers']}")
            if apify_profile.get("isOrganization"):
                account_type = "公司账号"
                platform_confirmed_organization = True
    if not description:
        description = "平台未向匿名访问返回公开简介，请打开原始主页人工核验。"
    analysis = analyze_social_business_profile(
        f"{title} {description} {handle}",
        platform,
        account_type,
    )
    if analysis["accountType"] != "账号类型待核验":
        account_type = analysis["accountType"]
    if platform_confirmed_organization:
        account_type = "公司商业账号"
    return {
        "platform": platform,
        "accountType": account_type,
        "relationship": relationship,
        "title": clean_text(title)[:180],
        "description": clean_text(description)[:700],
        "url": final_url,
        "handle": handle[:120],
        "externalWebsites": external_websites[:5],
        "profileNotFound": profile_not_found,
        "publicEmail": public_email,
        "publicPhone": public_phone,
        **analysis,
        "accountType": account_type,
    }


def search_youtube_public_channels(query: str, limit: int = 5) -> list[dict]:
    url = "https://www.youtube.com/results?" + urllib.parse.urlencode({"search_query": query})
    page, _ = fetch_document(url, timeout=25)
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", page, flags=re.S)
    if not match:
        return []
    data = json.loads(match.group(1))
    renderers = []
    video_renderers = []

    def walk(value):
        if isinstance(value, dict):
            if "channelRenderer" in value:
                renderers.append(value["channelRenderer"])
            if "videoRenderer" in value:
                video_renderers.append(value["videoRenderer"])
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(data)
    results = []
    latest_video_by_channel: dict[str, dict] = {}
    for video in video_renderers:
        owner = video.get("ownerText") or video.get("longBylineText") or {}
        runs = owner.get("runs") or []
        if not runs:
            continue
        run = runs[0]
        endpoint = run.get("navigationEndpoint", {}).get("browseEndpoint", {})
        channel_id = endpoint.get("browseId", "")
        published_text = text_from_runs(video.get("publishedTimeText"))
        published_at = extract_published_at(published_text)
        if not channel_id or not is_recent_youtube_video_date(published_at):
            continue
        existing = latest_video_by_channel.get(channel_id)
        latest_video_by_channel[channel_id] = {
            "publishedAt": latest_iso_date([published_at, existing.get("publishedAt", "") if existing else ""]),
            "publishedText": published_text,
            "videoTitle": text_from_runs(video.get("title")),
            "snippet": text_from_runs(video.get("descriptionSnippet")),
        }

    for channel in renderers:
        channel_id = channel.get("channelId", "")
        latest_video = latest_video_by_channel.get(channel_id)
        if not latest_video:
            continue
        canonical = (
            channel.get("navigationEndpoint", {})
            .get("browseEndpoint", {})
            .get("canonicalBaseUrl", "")
        )
        channel_url = urllib.parse.urljoin("https://www.youtube.com", canonical) if canonical else (
            f"https://www.youtube.com/channel/{channel_id}" if channel_id else ""
        )
        if not channel_url:
            continue
        results.append(
            {
                "title": text_from_runs(channel.get("title")) or "YouTube channel",
                "url": channel_url,
                "snippet": text_from_runs(channel.get("descriptionSnippet")),
                "handle": latest_video.get("publishedAt") or latest_video.get("publishedText") or text_from_runs(channel.get("subscriberCountText")),
                "channelId": channel_id,
                "latestVideoPublishedAt": latest_video.get("publishedAt", ""),
                "latestVideoTitle": latest_video.get("videoTitle", ""),
                "apiSource": "YouTube public page fallback",
            }
        )
        if len(results) >= limit:
            break
    seen = {normalize_public_url(item.get("url", "")).lower().rstrip("/") for item in results}
    for video in video_renderers:
        owner = video.get("ownerText") or video.get("longBylineText") or {}
        runs = owner.get("runs") or []
        if not runs:
            continue
        run = runs[0]
        endpoint = run.get("navigationEndpoint", {}).get("browseEndpoint", {})
        canonical = endpoint.get("canonicalBaseUrl", "")
        channel_id = endpoint.get("browseId", "")
        latest_video = latest_video_by_channel.get(channel_id)
        if not latest_video:
            continue
        channel_url = urllib.parse.urljoin("https://www.youtube.com", canonical) if canonical else (
            f"https://www.youtube.com/channel/{channel_id}" if channel_id else ""
        )
        identity = normalize_public_url(channel_url).lower().rstrip("/")
        if not channel_url or identity in seen:
            continue
        title = text_from_runs(video.get("title"))
        snippet = text_from_runs(video.get("descriptionSnippet"))
        results.append(
            {
                "title": text_from_runs(owner) or title or "YouTube channel",
                "url": channel_url,
                "snippet": snippet or title,
                "handle": latest_video.get("publishedAt") or text_from_runs(video.get("publishedTimeText")),
                "channelId": channel_id,
                "latestVideoPublishedAt": latest_video.get("publishedAt", ""),
                "latestVideoTitle": latest_video.get("videoTitle", ""),
                "apiSource": "YouTube public video fallback",
            }
        )
        seen.add(identity)
        if len(results) >= limit:
            break
    return results


def search_youtube_channels(query: str, limit: int = 5, country: str = "") -> list[dict]:
    api_key = get_youtube_api_key()
    country_code = country_search_meta(country)["code"].upper() if country else ""
    if api_key:
        per_type_limit = max(1, min(limit, 50))
        search_items = []
        for result_type in ("video",):
            params = {
                "part": "snippet",
                "type": result_type,
                "q": query,
                "maxResults": str(per_type_limit),
                "fields": "items(id/channelId,id/videoId,snippet(channelId,channelTitle,title,description,publishedAt))",
                "key": api_key,
                "order": "relevance",
                "publishedAfter": (
                    datetime.now(timezone.utc) - timedelta(days=YOUTUBE_MAX_VIDEO_AGE_DAYS)
                ).isoformat().replace("+00:00", "Z"),
            }
            if country_code:
                params["regionCode"] = country_code
            request = urllib.request.Request(
                "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(params),
                headers={"User-Agent": "HuaweiEVLeadTool/1.0"},
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    payload = json.loads(response.read().decode("utf-8", errors="ignore"))
                record_api_usage("youtube", True)
                search_items.extend(payload.get("items", []))
            except (OSError, ValueError, TimeoutError, http.client.HTTPException, json.JSONDecodeError):
                record_api_usage("youtube", False)
                continue
        channel_ids = [
            (item.get("id") or {}).get("channelId")
            or (item.get("snippet") or {}).get("channelId")
            for item in search_items
        ]
        channel_ids = list(dict.fromkeys(channel_id for channel_id in channel_ids if channel_id))
        details_by_id = {}
        if channel_ids:
            for start in range(0, len(channel_ids), 50):
                detail_params = {
                    "part": "snippet,brandingSettings",
                    "id": ",".join(channel_ids[start:start + 50]),
                    "fields": "items(id,snippet(title,description,customUrl),brandingSettings(channel(country)))",
                    "key": api_key,
                }
                detail_request = urllib.request.Request(
                    "https://www.googleapis.com/youtube/v3/channels?" + urllib.parse.urlencode(detail_params),
                    headers={"User-Agent": "HuaweiEVLeadTool/1.0"},
                )
                try:
                    with urllib.request.urlopen(detail_request, timeout=20) as response:
                        detail_payload = json.loads(response.read().decode("utf-8", errors="ignore"))
                    details_by_id.update({
                        item.get("id", ""): item
                        for item in detail_payload.get("items", [])
                        if item.get("id")
                    })
                except (OSError, ValueError, TimeoutError, http.client.HTTPException, json.JSONDecodeError):
                    # Channel enrichment should not discard otherwise valid search results.
                    continue
        latest_video_by_channel: dict[str, dict] = {}
        for item in search_items:
            item_id = item.get("id") or {}
            if not item_id.get("videoId"):
                continue
            snippet = item.get("snippet") or {}
            channel_id = snippet.get("channelId", "")
            published_at = (snippet.get("publishedAt") or "").replace("Z", "+00:00")
            if not channel_id or not is_recent_youtube_video_date(published_at):
                continue
            existing = latest_video_by_channel.get(channel_id)
            latest_video_by_channel[channel_id] = {
                "publishedAt": latest_iso_date([published_at, existing.get("publishedAt", "") if existing else ""]),
                "videoTitle": snippet.get("title", ""),
                "snippet": snippet.get("description", ""),
            }
        results = []
        seen_channel_ids = set()
        for item in search_items:
            snippet = item.get("snippet") or {}
            channel_id = (
                (item.get("id") or {}).get("channelId")
                or snippet.get("channelId")
                or ""
            )
            if not channel_id or channel_id in seen_channel_ids:
                continue
            latest_video = latest_video_by_channel.get(channel_id)
            if not latest_video:
                continue
            seen_channel_ids.add(channel_id)
            detail = details_by_id.get(channel_id, {})
            detail_snippet = detail.get("snippet") or {}
            branding = detail.get("brandingSettings") or {}
            branding_channel = branding.get("channel") or {}
            channel_country = str(branding_channel.get("country", "") or "").upper()
            if country_code and channel_country and channel_country != country_code:
                continue
            custom_url = detail_snippet.get("customUrl", "")
            channel_url = (
                f"https://www.youtube.com/{custom_url}"
                if custom_url.startswith("@")
                else f"https://www.youtube.com/channel/{channel_id}"
            )
            results.append(
                {
                    "title": detail_snippet.get("title") or snippet.get("channelTitle") or snippet.get("title") or "YouTube channel",
                    "url": channel_url,
                    "snippet": clean_text(" ".join(filter(None, [
                        detail_snippet.get("description", ""),
                        latest_video.get("videoTitle", ""),
                        latest_video.get("snippet", ""),
                        snippet.get("description", ""),
                    ])))[:1200],
                    "handle": latest_video.get("publishedAt", ""),
                    "channelId": channel_id,
                    "country": branding_channel.get("country", ""),
                    "latestVideoPublishedAt": latest_video.get("publishedAt", ""),
                    "latestVideoTitle": latest_video.get("videoTitle", ""),
                    "apiSource": "YouTube Data API v3",
                }
            )
            if len(results) >= limit:
                break
        fallback_results = []
        if len(results) < 3:
            try:
                fallback_results = search_youtube_public_channels(query, limit=limit)
            except (OSError, ValueError, TimeoutError, UnicodeError, json.JSONDecodeError):
                fallback_results = []
        seen_urls = {normalize_public_url(item.get("url", "")).lower().rstrip("/") for item in results}
        for item in fallback_results:
            identity = normalize_public_url(item.get("url", "")).lower().rstrip("/")
            if identity and identity not in seen_urls:
                results.append(item)
                seen_urls.add(identity)
            if len(results) >= limit:
                break
        return results

    return search_youtube_public_channels(query, limit=limit)


def search_bing(query: str, limit: int = 8, freshness_days: int | None = None) -> list[dict]:
    items: list[dict] = []
    # Bing exposes result pages through the public `first` parameter. Reading a
    # second page materially improves business-directory coverage while keeping
    # each keyword within a small, polite request budget.
    pages = min(2, max(1, (limit + 9) // 10))
    for page_index in range(pages):
        params = {"q": query, "count": 10, "first": 1 + page_index * 10}
        if freshness_days:
            params["filters"] = 'ex1:"ez2"' if freshness_days <= 7 else 'ex1:"ez3"'
        page = fetch_text("https://www.bing.com/search?" + urllib.parse.urlencode(params))
        for match in re.finditer(r'<li class="b_algo"[\s\S]*?</li>', page, flags=re.I):
            block = match.group(0)
            link = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', block, flags=re.I)
            if not link:
                continue
            href = html.unescape(link.group(1))
            title = clean_text(link.group(2))
            snippet_match = re.search(r'<p[^>]*>([\s\S]*?)</p>', block, flags=re.I)
            snippet = clean_text(snippet_match.group(1)) if snippet_match else ""
            href = normalize_public_url(href)
            if href and "bing.com" not in href and is_valid_http_url(href):
                items.append({"title": title, "url": href, "snippet": snippet})
            if len(items) >= limit:
                return items
    return items


def resolve_baidu_result_url(url: str) -> str:
    raw_href = html.unescape(str(url or "")).strip()
    if raw_href.startswith("/link?"):
        raw_href = "https://www.baidu.com" + raw_href
    if not raw_href.startswith(("http://", "https://")):
        return ""
    href = normalize_public_url(raw_href)
    if not href or "baidu.com/link" not in href:
        return href
    try:
        req = urllib.request.Request(
            href,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
            },
            method="HEAD",
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            return normalize_public_url(response.geturl())
    except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
        return href


def search_baidu(query: str, limit: int = 8, freshness_days: int | None = None) -> list[dict]:
    params = {"wd": query, "rn": max(10, min(20, limit * 2))}
    if freshness_days:
        params["gpc"] = f"stf={int(time.time() - freshness_days * 86400)},{int(time.time())}|stftype=1"
    req = urllib.request.Request(
        "https://www.baidu.com/s?" + urllib.parse.urlencode(params),
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
        },
    )
    with urllib.request.urlopen(req, timeout=DISCOVERY_SEARCH_TIMEOUT) as response:
        raw = response.read(600_000)
        charset = response.headers.get_content_charset() or "utf-8"
        page = raw.decode(charset, errors="ignore")
    items: list[dict] = []
    blocks = re.findall(
        r'<div[^>]+class="[^"]*(?:result|c-container)[^"]*"[\s\S]*?(?=<div[^>]+class="[^"]*(?:result|c-container)|</body>)',
        page,
        flags=re.I,
    )
    if not blocks:
        blocks = re.findall(r'<h3[\s\S]*?</h3>[\s\S]{0,1200}', page, flags=re.I)
    for block in blocks:
        link = re.search(r'<h3[^>]*>[\s\S]*?<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', block, flags=re.I)
        if not link:
            link = re.search(r'<a[^>]+href="([^"]+)"[^>]*>([\s\S]{1,300}?)</a>', block, flags=re.I)
        if not link:
            continue
        href = html.unescape(link.group(1))
        if href.startswith("/link?"):
            href = "https://www.baidu.com" + href
        if not href.startswith(("http://", "https://")):
            continue
        title = clean_text(link.group(2))
        if not title:
            continue
        snippet_match = re.search(r'<span[^>]+class="[^"]*(?:content-right|c-abstract|c-span-last)[^"]*"[^>]*>([\s\S]*?)</span>', block, flags=re.I)
        if not snippet_match:
            snippet_match = re.search(r'<div[^>]+class="[^"]*(?:c-abstract|c-row|content)[^"]*"[^>]*>([\s\S]{1,900}?)</div>', block, flags=re.I)
        snippet = clean_text(snippet_match.group(1)) if snippet_match else ""
        href = resolve_baidu_result_url(href)
        domain = safe_urlparse(href).netloc.lower()
        if href and is_valid_http_url(href) and "." in domain and "baidu.com" not in domain and "javascript" not in domain:
            items.append({
                "title": title,
                "url": href,
                "snippet": snippet,
                "apiSource": "Baidu Search",
            })
        if len(items) >= limit:
            break
    return items


def search_duckduckgo(query: str, limit: int = 8, freshness_days: int | None = None) -> list[dict]:
    params = {"q": query, "kl": "us-en"}
    if freshness_days:
        params["df"] = "w" if freshness_days <= 7 else "m"
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode(
        params
    )
    page = fetch_text(url)
    items: list[dict] = []
    for match in re.finditer(r'<div class="result results_links[\s\S]*?</div>\s*</div>', page, flags=re.I):
        block = match.group(0)
        link = re.search(
            r'class="result__a"[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>',
            block,
            flags=re.I,
        )
        if not link:
            continue
        href = html.unescape(link.group(1))
        if href.startswith("//"):
            href = "https:" + href
        try:
            parsed_redirect = urllib.parse.urlparse(href)
        except ValueError:
            continue
        redirect_params = urllib.parse.parse_qs(parsed_redirect.query)
        if "uddg" in redirect_params:
            href = redirect_params["uddg"][0]
        title = clean_text(link.group(2))
        snippet_match = re.search(
            r'class="result__snippet"[^>]*>([\s\S]*?)</(?:a|div)>',
            block,
            flags=re.I,
        )
        snippet = clean_text(snippet_match.group(1)) if snippet_match else ""
        href = normalize_public_url(href)
        if href and is_valid_http_url(href):
            items.append({"title": title, "url": href, "snippet": snippet})
        if len(items) >= limit:
            break
    return items


def search_brave(query: str, limit: int = 8, freshness_days: int | None = None) -> list[dict]:
    params = {"q": query, "source": "web"}
    if freshness_days:
        params["tf"] = "pw" if freshness_days <= 7 else "pm"
    page = fetch_text("https://search.brave.com/search?" + urllib.parse.urlencode(params))
    items: list[dict] = []
    blocks = re.split(r'<div class="snippet\s[^>]*data-type="web"[^>]*>', page, flags=re.I)[1:]
    for block in blocks:
        href_match = re.search(r'<a href="([^"]+)"', block, flags=re.I)
        title_match = re.search(r'<div class="title search-snippet-title[^>]*title="([^"]+)"', block, flags=re.I)
        snippet_match = re.search(r'<div class="generic-snippet[^>]*>[\s\S]{0,3000}?<div class="content[^>]*>([\s\S]*?)</div>', block, flags=re.I)
        if not href_match or not title_match:
            continue
        href = html.unescape(href_match.group(1))
        title = clean_text(html.unescape(title_match.group(1)))
        snippet = clean_text(snippet_match.group(1)) if snippet_match else ""
        href = normalize_public_url(href)
        if href and "search.brave.com" not in href and is_valid_http_url(href):
            items.append({"title": title, "url": href, "snippet": snippet})
        if len(items) >= limit:
            break
    return items


def search_brave_api(query: str, limit: int = 8, freshness_days: int | None = None, country: str = "") -> list[dict]:
    api_key = get_brave_search_api_key()
    if not api_key:
        return []
    meta = country_search_meta(country)
    params = {
        "q": query,
        "count": max(1, min(20, limit)),
        "search_lang": "en",
        "country": meta["code"],
        "safesearch": "moderate",
    }
    if freshness_days:
        params["freshness"] = "pw" if freshness_days <= 7 else "pm"
    data = fetch_json(
        "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode(params),
        timeout=DISCOVERY_SEARCH_TIMEOUT,
        headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
    )
    record_api_usage("brave", True)
    items: list[dict] = []
    for result in ((data.get("web") or {}).get("results") or []):
        if not isinstance(result, dict):
            continue
        href = normalize_public_url(str(result.get("url") or ""))
        if href and is_valid_http_url(href):
            items.append({
                "title": clean_text(str(result.get("title") or "")),
                "url": href,
                "snippet": clean_text(str(result.get("description") or "")),
                "apiSource": "Brave Search API",
            })
        if len(items) >= limit:
            break
    return items


def search_serpapi(query: str, limit: int = 8, freshness_days: int | None = None, country: str = "") -> list[dict]:
    api_key = get_serpapi_api_key()
    if not api_key:
        return []
    meta = country_search_meta(country)
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": max(1, min(20, limit)),
        "hl": "zh-cn" if meta.get("code") == "cn" else "en",
        "gl": meta["code"],
        "google_domain": meta["google_domain"],
        "location": meta["location"],
    }
    if freshness_days:
        params["tbs"] = "qdr:w" if freshness_days <= 7 else "qdr:m"
    data = fetch_json(
        "https://serpapi.com/search.json?" + urllib.parse.urlencode(params),
        timeout=DISCOVERY_SEARCH_TIMEOUT,
    )
    record_api_usage("serpapi:web", True)
    items: list[dict] = []
    for result in data.get("organic_results") or []:
        if not isinstance(result, dict):
            continue
        href = normalize_public_url(str(result.get("link") or ""))
        if href and is_valid_http_url(href):
            items.append({
                "title": clean_text(str(result.get("title") or "")),
                "url": href,
                "snippet": clean_text(str(result.get("snippet") or "")),
                "apiSource": "SerpApi Google Search",
            })
        if len(items) >= limit:
            break
    return items


def search_serpapi_baidu(query: str, limit: int = 8, freshness_days: int | None = None) -> list[dict]:
    api_key = get_serpapi_api_key()
    if not api_key:
        return []
    params = {
        "engine": "baidu",
        "q": query,
        "api_key": api_key,
        "ct": "2",
        "rn": max(1, min(20, limit)),
    }
    if freshness_days:
        start = int(time.time() - freshness_days * 86400)
        end = int(time.time())
        params["gpc"] = f"stf={start},{end}|stftype=1"
    data = fetch_json(
        "https://serpapi.com/search.json?" + urllib.parse.urlencode(params),
        timeout=DISCOVERY_SEARCH_TIMEOUT,
    )
    record_api_usage("serpapi:baidu", True)
    items: list[dict] = []
    for result in data.get("organic_results") or []:
        if not isinstance(result, dict):
            continue
        href = normalize_public_url(str(result.get("link") or result.get("url") or ""))
        domain = safe_urlparse(href).netloc.lower()
        if href and is_valid_http_url(href) and "." in domain:
            items.append({
                "title": clean_text(str(result.get("title") or "")),
                "url": href,
                "snippet": clean_text(str(result.get("snippet") or result.get("displayed_link") or "")),
                "apiSource": "SerpApi Baidu Search",
            })
        if len(items) >= limit:
            break
    return items


def search_web(query: str, limit: int = 8, freshness_days: int | None = None, country: str = "") -> list[dict]:
    collected: list[dict] = []
    is_china_search = country_search_meta(country).get("code") == "cn" if country else False
    executor = ThreadPoolExecutor(max_workers=6 if is_china_search else 5)
    futures = []
    if is_china_search:
        futures.append(executor.submit(search_serpapi_baidu, query, limit, freshness_days))
        futures.append(executor.submit(search_baidu, query, limit, freshness_days))
    futures.extend([
        executor.submit(search_brave_api, query, limit, freshness_days, country),
        executor.submit(search_serpapi, query, limit, freshness_days, country),
        executor.submit(search_duckduckgo, query, limit, freshness_days),
        executor.submit(search_bing, query, limit, freshness_days),
        executor.submit(search_brave, query, limit, freshness_days),
    ])
    try:
        for future in as_completed(futures, timeout=DISCOVERY_SEARCH_TIMEOUT):
            try:
                collected.extend(future.result(timeout=1))
            except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                continue
    except FuturesTimeoutError:
        pass
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
    results: list[dict] = []
    seen: set[str] = set()
    for item in collected:
        identity = normalize_public_url(item.get("url", "")).lower().rstrip("/")
        if not identity or identity in seen:
            continue
        if country and has_foreign_location_conflict(
            f"{item.get('title', '')} {item.get('snippet', '')} {item.get('url', '')}",
            country,
        ):
            continue
        seen.add(identity)
        results.append(item)
        if len(results) >= limit:
            break
    return results


def social_search_variants(
    platform: str,
    site: str,
    market: str,
    target_type: str,
    account_scope: str,
) -> list[str]:
    company_terms = {
        "dealer": ("car dealer", "motors showroom", "automotive trading"),
        "parallel": ("car importer", "auto trading", "imported cars"),
        "importer": ("vehicle importer", "car distributor", "automotive trading"),
        "fleet": ("fleet company", "car rental", "vehicle procurement"),
        "corporate": ("fleet procurement", "corporate vehicles", "car supplier"),
        "government": ("vehicle supplier", "fleet tender", "automotive company"),
        "buying": ("car buyer", "vehicle procurement", "sourcing vehicles"),
        "individual": ("car buyer", "luxury cars", "electric vehicles"),
    }.get(target_type, ("car dealer", "motors showroom", "automotive trading"))
    queries: list[str] = []
    markets = [market]
    if market.lower() in {"uae", "united arab emirates", "emirates"}:
        markets.extend([
            "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah",
            "Jebel Ali", "Al Quoz", "Mussafah", "Deira",
        ])
    market_text = normalize_country_match_text(market)
    for key, hints in COUNTRY_HINTS.items():
        meta = COUNTRY_SEARCH_META.get(key, {})
        aliases = (key, meta.get("location", ""), *(meta.get("aliases") or ()))
        if any((token := normalize_country_match_text(alias)) and token in market_text for alias in aliases):
            markets = [*hints[:12], *markets]
            break
    markets = list(dict.fromkeys(place for place in markets if place))
    localized_terms: list[str] = []
    for key, terms in LOCALIZED_DISCOVERY_TERMS.items():
        meta = COUNTRY_SEARCH_META.get(key, {})
        aliases = (key, meta.get("location", ""), *(meta.get("aliases") or ()))
        if any(normalize_country_match_text(alias) and normalize_country_match_text(alias) in market_text for alias in aliases):
            localized_terms = list(terms)
            break
    target_priority_terms = {
        "dealer": ("car dealer", "used car dealer", "car showroom", "motors showroom", "cars for sale"),
        "parallel": ("parallel import cars", "imported cars", "car importer", "auto trading", "Chinese car importer"),
        "importer": ("car importer", "vehicle importer", "automotive importer", "car distributor", "Chinese vehicle distributor"),
        "fleet": ("fleet vehicle supplier", "fleet sales", "car rental fleet", "corporate fleet", "vehicle procurement"),
        "corporate": ("fleet procurement", "corporate vehicles", "vehicle supplier", "car supplier", "fleet sales"),
        "government": ("vehicle supplier", "fleet tender", "government fleet", "public procurement vehicles", "automotive company"),
        "buying": ("vehicle procurement", "car buyer", "sourcing vehicles", "fleet purchase", "RFQ vehicles"),
        "individual": ("luxury cars", "electric vehicles", "Chinese EV", "SUV dealer", "cars for sale"),
    }.get(target_type, company_terms)
    broad_terms = list(dict.fromkeys([*target_priority_terms, *SOCIAL_HIGH_INTENT_TERMS]))
    apify_first_terms = list(dict.fromkeys([*target_priority_terms, *SOCIAL_HIGH_INTENT_TERMS[:18]]))
    facebook_terms = (
        "car dealer",
        "used cars",
        "used car dealer",
        "pre owned cars",
        "imported cars",
        "tokunbo cars",
        "car sales",
        "auto sales",
        "auto dealer",
        "motors",
        "car showroom",
        "buy and sell cars",
        "cars marketplace",
    )
    if platform in {"instagram", "facebook", "tiktok"}:
        site_variants = {
            "instagram": ("instagram.com",),
            "facebook": ("facebook.com",),
            "tiktok": ("tiktok.com",),
        }.get(platform, (site,))
        if platform == "facebook":
            # The Facebook Actor works best with one country-level commercial query.
            queries.append(f"{market} car dealer used cars auto dealership")
        elif platform == "instagram":
            # Profile search is strongest with short location + business terms.
            # Keep the same plan for every country: full country name, primary
            # city, localized commercial phrases, then additional major cities.
            instagram_places = list(dict.fromkeys([market, *markets[:4]]))
            for place in instagram_places[:2]:
                queries.extend([
                    f"{place} cars",
                    f"{place} auto",
                    f"{place} car dealer",
                ])
            queries.extend(localized_terms[:2])
        elif platform == "tiktok":
            # TikTok user search favors short local-business phrases. Lead
            # with country and major-city terms before the longer web queries.
            tiktok_places = list(dict.fromkeys([market, *markets[:4]]))
            for place in tiktok_places:
                queries.extend([
                    f"{place} car dealer",
                    f"{place} used cars",
                ])
        for place in markets[:8]:
            queries.extend([
                f"{place} cars {platform}",
                f"{place} car dealer {platform}",
                f"{place} auto sales {platform}",
                f"{place} motors {platform}",
                f"site:{site_variants[0]} {place} cars",
                f"site:{site_variants[0]} {place} auto",
                f"site:{site_variants[0]} {place} motors",
            ])
        for term in localized_terms[:6]:
            queries.extend([
                f"{term} {platform}",
                f"site:{site_variants[0]} {term}",
            ])
        if platform == "facebook":
            for place in markets[:10]:
                for term in facebook_terms:
                    queries.extend([
                        f"{place} {term} facebook",
                        f"site:facebook.com {place} \"{term}\"",
                    ])
                queries.extend([
                    f"site:facebook.com/pages {place} cars",
                    f"site:facebook.com/groups {place} cars",
                    f"site:facebook.com/marketplace {place} cars",
                    f"site:facebook.com {place} \"auto dealer\"",
                    f"site:facebook.com {place} \"used cars for sale\"",
                ])
        if platform == "instagram":
            primary_place = markets[0] if markets else market
            compact_terms = [
                f"{market} cars",
                f"{primary_place} cars",
                f"{market} motors",
                f"{primary_place} auto",
            ]
            if normalize_country_match_text(market) == "oman":
                compact_terms.extend(("سيارات عمان", "سيارات مسقط"))
            queries.extend(
                f"site:instagram.com {term}"
                for term in dict.fromkeys(compact_terms)
            )
        for term in apify_first_terms[:18]:
            for place in markets[:12]:
                queries.append(f"{place} {term}")
        for place in markets[:12]:
            for variant in site_variants:
                queries.append(f"site:{variant} {place} \"{company_terms[0]}\" contact phone email")
                queries.append(f"site:{variant} {place} \"{company_terms[0]}\" about bio contacts")
            for term in broad_terms:
                for variant in site_variants:
                    queries.append(f"site:{variant} {place} \"{term}\"")
        return list(dict.fromkeys(queries))
    if platform == "linkedin":
        for place in markets[:8]:
            queries.extend([
                f"{place} automotive linkedin",
                f"{place} car dealer linkedin",
                f"{place} auto sales linkedin",
                f"site:linkedin.com/company {place} cars",
                f"site:linkedin.com/company {place} motors",
            ])
        for term in localized_terms[:6]:
            queries.extend([
                f"{term} linkedin",
                f"site:linkedin.com/company {term}",
            ])
        for term in apify_first_terms[:18]:
            for place in markets[:12]:
                queries.append(f"{place} {term}")
        for place in markets[:12]:
            queries.append(f"site:linkedin.com/company {place} \"{company_terms[0]}\" contact email phone")
            queries.append(f"site:linkedin.com/company {place} \"{company_terms[0]}\" about")
            for term in broad_terms:
                queries.append(f"site:linkedin.com/company {place} \"{term}\"")
                queries.append(f"site:linkedin.com/in {place} \"{term}\"")
                queries.append(f"site:linkedin.com/posts {place} \"{term}\"")
        if account_scope in ("person", "both"):
            for place in markets:
                queries.append(f"site:linkedin.com/in {place} \"dealership owner\"")
                queries.append(f"site:linkedin.com/in {place} \"sales director\" automotive")
        return list(dict.fromkeys(queries))
    if account_scope in ("company", "both"):
        queries.append(f"site:{site} {market} \"{company_terms[0]}\"")
    if account_scope in ("person", "both") and platform == "linkedin":
        queries.append(f"site:linkedin.com/in {market} \"dealership owner\"")
    return list(dict.fromkeys(queries))


APIFY_SOCIAL_ACTORS = {
    "facebook": ("APIFY_FACEBOOK_ACTOR_ID", "apify/facebook-search-scraper"),
    "instagram": ("APIFY_INSTAGRAM_ACTOR_ID", "apify/instagram-search-scraper"),
    "tiktok": ("APIFY_TIKTOK_ACTOR_ID", "clockworks/tiktok-scraper"),
    "linkedin": ("APIFY_LINKEDIN_ACTOR_ID", "harvestapi/linkedin-company-search"),
}


def apify_actor_url_part(actor_id: str) -> str:
    return urllib.parse.quote(actor_id.strip().replace("/", "~"), safe="")


def apify_actor_id(platform: str) -> str:
    env_key, default_actor = APIFY_SOCIAL_ACTORS.get(platform, ("", ""))
    actor_id = runtime_setting(env_key, default_actor) if env_key else ""
    if platform == "facebook" and actor_id == "memo23/facebook-search-scraper":
        # The legacy search-only Actor returns little beyond names and URLs.
        # Migrate it to Apify's maintained Actor so location and contact evidence
        # can be verified before a lead is admitted to review.
        return default_actor
    return actor_id


def apify_keyword_query(query: str) -> str:
    value = re.sub(r"\bsite:\S+", " ", str(query or ""), flags=re.I)
    value = value.replace('"', " ")
    value = re.sub(r"\b(contact|contacts|phone|email|whatsapp|about|bio)\b", " ", value, flags=re.I)
    value = re.sub(r"\bOR\b", " ", value, flags=re.I)
    value = re.sub(r"\s+", " ", value).strip()
    return value or str(query or "").strip()


def apify_allowed_for_source_mode(source_mode: str) -> bool:
    return str(source_mode or "").strip().lower() in APIFY_DISCOVERY_SOURCE_MODES


def apify_query_plan(query_variants: list[str], source_mode: str, platform: str = "") -> tuple[list[str], int]:
    if not apify_allowed_for_source_mode(source_mode):
        return [], 0
    if platform in {"instagram", "facebook", "tiktok", "linkedin"}:
        if source_mode in ("all", "combined"):
            return [], 0
        if platform == "facebook" and source_mode == "facebook":
            return [
                "Car dealer",
                "Used car dealer",
                "Auto dealer",
                "Car showroom",
                "Vehicle importer",
            ], 30
        if platform == "linkedin" and source_mode == "linkedin":
            return ["automotive"], 30
        if platform == "instagram" and source_mode == "instagram":
            query_limit, result_limit = 8, 30
        elif platform == "tiktok" and source_mode == "tiktok":
            query_limit, result_limit = 8, 30
        elif source_mode == "social":
            query_limit, result_limit = (4, 20) if platform in {"instagram", "tiktok"} else (1, 8)
        else:
            query_limit, result_limit = 1, 10
    elif source_mode in ("all", "combined"):
        return [], 0
    elif source_mode == "social":
        query_limit, result_limit = 1, 8
    else:
        query_limit, result_limit = 1, 10
    queries = []
    for query in query_variants:
        cleaned = apify_keyword_query(query)
        if cleaned and cleaned.lower() not in {item.lower() for item in queries}:
            queries.append(cleaned)
        if len(queries) >= query_limit:
            break
    if platform == "instagram" and queries:
        # The maintained Instagram Search Actor accepts comma-separated keywords.
        # A single run avoids paying the startup cost twice and works better with
        # short local-business terms than separate long commercial phrases.
        queries = [", ".join(queries)]
    return queries, result_limit


def apify_search_input(
    platform: str,
    query: str | list[str],
    limit: int,
    location: str | list[str] = "",
) -> dict:
    query_values = query if isinstance(query, list) else [query]
    queries = []
    for value in query_values:
        cleaned = apify_keyword_query(value)
        if cleaned:
            queries.append(cleaned)
    query = queries[0] if queries else ""
    payload = {
        "query": query,
        "search": query,
        "queries": [query],
        "searchQueries": [query],
        "maxItems": limit,
        "maxResults": limit,
        "resultsLimit": limit,
        "limit": limit,
        "proxy": {"useApifyProxy": True},
    }
    if platform == "instagram":
        keyword_count = max(1, len([part for part in query.split(",") if part.strip()]))
        payload = {
            "search": query,
            "searchType": "user",
            # searchLimit is per keyword. Keep the entire Actor run close to
            # the requested result cap instead of multiplying spend by terms.
            "searchLimit": max(1, (limit + keyword_count - 1) // keyword_count),
            "enhanceUserSearchWithFacebookPage": False,
            "liveSearch": False,
        }
    elif platform == "facebook":
        locations = location if isinstance(location, list) else [location]
        payload = {
            "categories": queries,
            "locations": list(dict.fromkeys(value for value in locations if value)),
            "resultsLimit": limit,
        }
    elif platform == "tiktok":
        query_count = max(1, len(queries))
        payload = {
            "searchSection": "/user",
            "searchQueries": queries,
            "maxProfilesPerQuery": max(1, (limit + query_count - 1) // query_count),
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "shouldDownloadAvatars": False,
            "shouldDownloadSubtitles": False,
        }
    elif platform == "linkedin":
        locations = location if isinstance(location, list) else [location]
        payload = {
            "locations": list(dict.fromkeys(value for value in locations if value))[:1],
            "industryIds": ["1292", "1128", "53"],
            "scraperMode": "full",
            "takePages": 1,
            "maxItems": limit,
        }
    return payload


def first_text_value(item: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return clean_text(value)
        if isinstance(value, (int, float)):
            return str(value)
    return ""


def nested_text_value(item: dict, paths: tuple[tuple[str, ...], ...]) -> str:
    for path in paths:
        value = item
        for key in path:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(key)
        if isinstance(value, str) and value.strip():
            return clean_text(value)
        if isinstance(value, (int, float)):
            return str(value)
    return ""


def joined_apify_values(item: dict, keys: tuple[str, ...]) -> str:
    values: list[str] = []
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            values.append(value)
        elif isinstance(value, list):
            for entry in value:
                if isinstance(entry, (str, int, float)):
                    values.append(str(entry))
                elif isinstance(entry, dict):
                    nested_values = [first_text_value(entry, (
                        "text", "name", "title", "description", "address",
                        "countryFull", "country", "city", "geographicArea",
                    )), nested_text_value(entry, (
                        ("parsed", "text"),
                        ("parsed", "countryFull"),
                        ("parsed", "country"),
                    )), nested_text_value(entry, (("parsed", "city"),))]
                    values.extend(value for value in nested_values if value)
        elif isinstance(value, dict):
            nested = first_text_value(value, ("text", "name", "title", "description", "address"))
            if nested:
                values.append(nested)
    return clean_text(" ".join(values))


def apify_external_links(item: dict) -> list[str]:
    links: list[str] = []
    for key in ("externalUrl", "externalWebsite", "website", "websiteUrl", "bioLink"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            links.append(value.strip())
        elif isinstance(value, dict):
            nested = first_text_value(value, ("url", "link", "href"))
            if nested:
                links.append(nested)
    external_urls = item.get("externalUrls")
    if isinstance(external_urls, list):
        for entry in external_urls:
            if isinstance(entry, str) and entry.strip():
                links.append(entry.strip())
            elif isinstance(entry, dict):
                value = first_text_value(entry, ("url", "link", "href"))
                if value:
                    links.append(value)
    return list(dict.fromkeys(links))


def apify_item_url(platform: str, item: dict) -> str:
    profile_url_keys = (
        "url", "profileUrl", "profileURL", "profile_url", "pageUrl", "facebookUrl", "channelUrl", "webUrl", "link", "inputUrl",
        "videoUrl", "linkedinUrl", "linkedin_url", "companyUrl",
    )
    if platform != "instagram":
        profile_url_keys = (*profile_url_keys, "externalUrl")
    url = first_text_value(item, profile_url_keys)
    if not url:
        url = nested_text_value(item, (
            ("authorMeta", "profileUrl"),
            ("authorMeta", "url"),
            ("author", "profileUrl"),
            ("author", "url"),
            ("company", "url"),
            ("company", "linkedinUrl"),
        ))
    if not url and isinstance(item.get("ig_business"), dict):
        profile = item.get("ig_business", {}).get("profile")
        if isinstance(profile, dict):
            url = first_text_value(profile, ("url", "profileUrl", "inputUrl"))
            if not url:
                username = first_text_value(profile, ("username", "userName", "handle"))
                if username:
                    url = f"https://www.instagram.com/{username.lstrip('@')}/"
    username_keys = ("username", "userName", "handle", "screenName", "channelId", "id")
    if platform == "tiktok":
        username_keys = ("username", "userName", "handle", "screenName", "name", "channelId", "id")
    username = first_text_value(item, username_keys)
    if not username:
        username = nested_text_value(item, (
            ("authorMeta", "name"),
            ("author", "uniqueId"),
            ("author", "username"),
            ("company", "universalName"),
        ))
    if not url and username:
        username = username.lstrip("@")
        if platform == "instagram":
            url = f"https://www.instagram.com/{username}/"
        elif platform == "tiktok":
            url = f"https://www.tiktok.com/@{username}"
        elif platform == "facebook":
            url = f"https://www.facebook.com/{username}"
        elif platform == "linkedin":
            url = f"https://www.linkedin.com/company/{username}"
    if platform == "linkedin" and url and "linkedin.com/" not in url.lower() and not url.startswith("http"):
        url = f"https://www.linkedin.com/company/{url.strip('/').lstrip('@')}"
    return normalize_public_url(str(url or ""))


def normalize_apify_items(
    platform: str,
    items,
    query: str,
    origin: str,
    source_type: str,
    limit: int,
) -> list[dict]:
    if isinstance(items, dict):
        dataset_items = items.get("items") or items.get("data") or items.get("results") or []
    elif isinstance(items, list):
        dataset_items = items
    else:
        dataset_items = []
    normalized: list[dict] = []
    for item in dataset_items:
        if not isinstance(item, dict):
            continue
        if item.get("errorCode"):
            continue
        author_meta = item.get("authorMeta") if isinstance(item.get("authorMeta"), dict) else {}
        if platform == "tiktok" and (
            item.get("privateAccount") is True
            or author_meta.get("privateAccount") is True
        ):
            continue
        url = apify_item_url(platform, item)
        if not url or not is_valid_http_url(url):
            continue
        title_keys = (
            "name", "title", "fullName", "username", "userName", "channelName", "pageName", "displayName",
            "authorName", "authorUserName", "screenName", "companyName",
        )
        if platform == "tiktok":
            title_keys = (
                "nickName", "fullName", "displayName", "name", "username", "userName", "screenName",
            )
        raw_title = first_text_value(item, title_keys) or nested_text_value(item, (
            ("authorMeta", "nickName"),
            ("authorMeta", "name"),
            ("author", "nickname"),
            ("author", "uniqueId"),
            ("company", "name"),
        )) or safe_urlparse(url).path.strip("/").replace("/", " ")
        title = raw_title
        if platform == "facebook" and "|" in raw_title:
            company_title = raw_title.split("|", 1)[0].strip()
            if company_title:
                title = company_title
        audience_metric = first_text_value(item, (
            "followersCount", "fans", "subscribers", "subscriberCount", "likesCount", "views", "viewCount", "employeeCount", "companySize",
        ))
        nested_audience_metric = nested_text_value(item, (
            ("authorMeta", "fans"),
            ("authorMeta", "heart"),
            ("company", "followersCount"),
            ("company", "companySize"),
        ))
        activity_metric = first_text_value(item, ("video", "videosCount", "postsCount"))
        snippet_parts = [
            raw_title if raw_title != title else "",
            first_text_value(item, ("description", "tagline", "biography", "bio", "signature", "about", "text", "fullText", "snippet", "summary", "categoryName", "businessCategoryName", "industry", "specialties")),
            joined_apify_values(item, ("info", "categories", "industries", "specialties")),
            joined_apify_values(item, ("address", "businessAddress", "locations", "phone", "email")),
            joined_apify_values(item, (
                "searchTerm", "searchQuery", "locationCreated", "cityName", "addressStreet", "businessEmail", "businessPhoneNumber", "contactPhoneNumber",
            )),
            " ".join(apify_external_links(item)),
            nested_text_value(item, (
                ("authorMeta", "signature"),
                ("author", "signature"),
                ("company", "description"),
                ("company", "industry"),
                ("about_me", "text"),
            )),
            f"audience {audience_metric}" if audience_metric else "",
            f"audience {nested_audience_metric}" if nested_audience_metric else "",
            f"videos {activity_metric}" if activity_metric else "",
        ]
        snippet = clean_text(" ".join(part for part in snippet_parts if part))
        website_candidates = [first_text_value(item, (
            "website", "websiteUrl", "companyWebsite", "externalWebsite", "homepage", "bioLink",
        )) or nested_text_value(item, (
            ("authorMeta", "bioLink"),
            ("author", "bioLink"),
            ("company", "website"),
        )), *apify_external_links(item)]
        customer_website = ""
        for candidate in website_candidates:
            normalized_candidate = normalize_public_url(candidate)
            if is_business_website_url(normalized_candidate):
                customer_website = normalized_candidate
                break
        normalized.append({
            "title": title[:180],
            "url": url,
            "snippet": snippet or f"Apify {origin} public profile",
            "apiSource": "Apify",
            "origin": origin,
            "source_type": f"{source_type} · Apify",
            "source_url": url,
            "customer_website": customer_website,
            "structured_business_profile": bool(
                joined_apify_values(item, ("info", "categories", "industries", "address", "locations"))
                or first_text_value(item, (
                    "phone", "email", "website", "description", "tagline", "industry",
                    "businessCategoryName", "businessEmail", "businessPhoneNumber",
                ))
                or item.get("isBusinessAccount") is True
            ),
            "skip_fetch": True,
            "apifyPlatform": platform,
        })
        if len(normalized) >= limit:
            break
    return normalized


def run_apify_actor_dataset(
    actor_id: str,
    payload: dict,
    token: str,
    timeout_seconds: int,
    item_limit: int,
    fields: tuple[str, ...] = (),
) -> tuple[list, str]:
    actor = apify_actor_url_part(actor_id)
    start_params = urllib.parse.urlencode({
        "token": token,
        "timeout": str(timeout_seconds),
        "memory": "512",
    })
    start_response = post_json_value(
        f"https://api.apify.com/v2/acts/{actor}/runs?{start_params}",
        payload,
        timeout=30,
    )
    run = start_response.get("data") if isinstance(start_response, dict) else None
    if not isinstance(run, dict) or not run.get("id"):
        return [], "START_FAILED"

    run_id = str(run["id"])
    status = str(run.get("status") or "READY")
    dataset_id = str(run.get("defaultDatasetId") or "")
    terminal_statuses = {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"}
    deadline = time.monotonic() + timeout_seconds + 8
    while status not in terminal_statuses and time.monotonic() < deadline:
        remaining = max(1, int(deadline - time.monotonic()))
        wait_seconds = min(10, remaining)
        status_params = urllib.parse.urlencode({
            "token": token,
            "waitForFinish": str(wait_seconds),
        })
        try:
            status_response = fetch_json(
                f"https://api.apify.com/v2/actor-runs/{urllib.parse.quote(run_id, safe='')}?{status_params}",
                timeout=wait_seconds + 5,
            )
        except (OSError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
            time.sleep(1)
            continue
        current = status_response.get("data") if isinstance(status_response, dict) else None
        if isinstance(current, dict):
            run = current
            status = str(current.get("status") or status)
            dataset_id = str(current.get("defaultDatasetId") or dataset_id)

    if status not in terminal_statuses:
        try:
            final_params = urllib.parse.urlencode({"token": token})
            final_response = fetch_json(
                f"https://api.apify.com/v2/actor-runs/{urllib.parse.quote(run_id, safe='')}?{final_params}",
                timeout=15,
            )
            current = final_response.get("data") if isinstance(final_response, dict) else None
            if isinstance(current, dict):
                status = str(current.get("status") or status)
                dataset_id = str(current.get("defaultDatasetId") or dataset_id)
        except (OSError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
            pass

    if not dataset_id:
        return [], status
    dataset_params = {
        "token": token,
        "clean": "true",
        "format": "json",
        "limit": str(max(1, item_limit)),
    }
    if fields:
        dataset_params["fields"] = ",".join(fields)
    items = fetch_json_value(
        f"https://api.apify.com/v2/datasets/{urllib.parse.quote(dataset_id, safe='')}/items?"
        f"{urllib.parse.urlencode(dataset_params)}",
        timeout=30,
    )
    return (items if isinstance(items, list) else []), status


def search_apify_social(
    platform: str,
    queries: list[str],
    origin: str,
    source_type: str,
    limit: int = 8,
    location: str | list[str] = "",
) -> list[dict]:
    token = get_apify_api_token()
    actor_id = apify_actor_id(platform)
    if not token or not actor_id or limit <= 0 or not queries:
        return []
    results: list[dict] = []
    seen: set[str] = set()

    def run_query(query: str | list[str]) -> list[dict]:
        fields: tuple[str, ...] = ()
        if platform == "instagram":
            # Recent posts make profile-search responses very large and can
            # contain malformed records. The dataset endpoint supports field
            # projection, so retain only evidence used by lead qualification.
            fields = (
                "url", "username", "fullName", "biography", "externalUrl", "externalUrls",
                "isBusinessAccount", "businessCategoryName", "businessAddress", "followersCount",
                "postsCount", "searchTerm", "searchSource", "private", "verified", "cityName",
                "addressStreet", "businessEmail", "businessPhoneNumber",
            )
        elif platform == "tiktok":
            fields = (
                "name", "nickName", "username", "signature", "bioLink", "fans", "video",
                "privateAccount", "ttSeller", "verified", "id", "searchQuery", "authorMeta",
            )
        try:
            items, run_status = run_apify_actor_dataset(
                actor_id,
                apify_search_input(platform, query, limit, location),
                token,
                APIFY_RUN_TIMEOUT_SECONDS,
                limit,
                fields,
            )
        except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
            record_api_usage(f"apify:{platform}", False, detail=actor_id)
            return []
        record_api_usage(f"apify:{platform}", bool(items), detail=f"{actor_id}:{run_status}")
        query_label = ", ".join(query) if isinstance(query, list) else query
        return normalize_apify_items(platform, items, query_label, origin, source_type, limit)

    executor = ThreadPoolExecutor(max_workers=1)
    actor_queries: list[str | list[str]] = [queries] if platform in {"facebook", "tiktok"} else queries
    futures = [executor.submit(run_query, query) for query in actor_queries]
    try:
        for future in as_completed(futures, timeout=APIFY_RUN_TIMEOUT_SECONDS + 50):
            if len(results) >= limit:
                break
            try:
                query_items = future.result(timeout=1)
            except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                continue
            for item in query_items:
                identity = item["url"].lower().rstrip("/")
                if identity in seen:
                    continue
                seen.add(identity)
                results.append(item)
                if len(results) >= limit:
                    break
    except FuturesTimeoutError:
        pass
    finally:
        executor.shutdown(wait=False, cancel_futures=True)
    return results


def instagram_market_hashtags(country: str, market: str, cities: list[str]) -> list[str]:
    places = list(dict.fromkeys([market, *cities[:2]]))
    hashtags: list[str] = []
    for place in places:
        normalized = unicodedata.normalize("NFKD", str(place or ""))
        slug = re.sub(
            r"[^a-z0-9]+",
            "",
            "".join(char for char in normalized if not unicodedata.combining(char)).lower(),
        )
        if slug:
            hashtags.extend((f"{slug}cars", f"{slug}auto"))
    local_terms = {
        "ci": ("abidjancars", "abidjanauto", "autoabidjan", "voitureabidjan", "ventevoitureabidjan"),
        "dz": ("algerieauto", "algerievoiture", "voiturealger", "autoalger"),
        "kg": ("bishkekauto", "avtosalonbishkek"),
        "uz": ("tashkentauto", "toshkentavto", "avtosalontashkent"),
    }.get(country_search_meta(country).get("code", ""), ())
    return list(dict.fromkeys(tag for tag in [*local_terms, *hashtags] if tag))[:8]


def search_apify_instagram_hashtag_accounts(
    country: str,
    market: str,
    cities: list[str],
    origin: str,
    source_type: str,
    limit: int = 30,
) -> list[dict]:
    token = get_apify_api_token()
    hashtags = instagram_market_hashtags(country, market, cities)
    if not token or not hashtags or limit <= 0:
        return []
    direct_urls = [
        f"https://www.instagram.com/explore/tags/{urllib.parse.quote(tag, safe='')}/"
        for tag in hashtags[:8]
    ]
    per_url_limit = max(2, (limit + len(direct_urls) - 1) // len(direct_urls))
    payload = {
        "directUrls": direct_urls,
        "resultsType": "posts",
        "resultsLimit": per_url_limit,
        "skipPinnedPosts": True,
    }
    fields = (
        "url", "inputUrl", "ownerUsername", "ownerFullName", "caption", "hashtags",
        "mentions", "locationName", "timestamp", "type", "productType",
    )
    try:
        items, run_status = run_apify_actor_dataset(
            "apify/instagram-scraper",
            payload,
            token,
            APIFY_RUN_TIMEOUT_SECONDS,
            max(limit, len(direct_urls) * per_url_limit),
            fields,
        )
    except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
        record_api_usage("apify:instagram", False, detail="apify/instagram-scraper:hashtag")
        return []
    record_api_usage(
        "apify:instagram",
        bool(items),
        detail=f"apify/instagram-scraper:{run_status}:hashtag",
    )
    results: list[dict] = []
    seen: set[str] = set()
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        username = first_text_value(item, ("ownerUsername", "username", "userName")).lstrip("@")
        if not username:
            continue
        profile_url = f"https://www.instagram.com/{username}/"
        identity = profile_url.lower()
        if identity in seen:
            continue
        seen.add(identity)
        title = first_text_value(item, ("ownerFullName", "fullName")) or username
        snippet = clean_text(" ".join([
            first_text_value(item, ("caption", "text")),
            joined_apify_values(item, ("hashtags", "mentions")),
            first_text_value(item, ("locationName",)),
            first_text_value(item, ("inputUrl",)),
        ]))
        results.append({
            "title": title[:180],
            "url": profile_url,
            "snippet": snippet or f"Instagram public post by @{username}",
            "apiSource": "Apify",
            "origin": origin,
            "source_type": f"{source_type} · Apify 标签帖子",
            "source_url": first_text_value(item, ("url",)) or profile_url,
            "customer_website": "",
            "structured_business_profile": False,
            "skip_fetch": True,
            "apifyPlatform": "instagram",
        })
        if len(results) >= limit:
            break
    return results


def extract_published_at(text: str, url: str = "") -> str:
    value = f"{url} {text}"
    numeric = re.search(r"\b(20\d{2})[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])\b", value)
    if numeric:
        year, month, day = map(int, numeric.groups())
        try:
            return datetime(year, month, day, tzinfo=timezone.utc).date().isoformat()
        except ValueError:
            pass
    named = re.search(
        r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+(\d{1,2}),?\s+(20\d{2})\b",
        value,
        flags=re.I,
    )
    if named:
        try:
            parsed = datetime.strptime(" ".join(named.groups()), "%b %d %Y")
        except ValueError:
            try:
                parsed = datetime.strptime(" ".join(named.groups()), "%B %d %Y")
            except ValueError:
                return ""
        return parsed.date().isoformat()
    relative = re.search(r"\b(\d+)\s+(hour|day|week|month|year)s?\s+ago\b", value, flags=re.I)
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2).lower()
        if unit == "hour":
            delta = timedelta(hours=amount)
        elif unit == "day":
            delta = timedelta(days=amount)
        elif unit == "week":
            delta = timedelta(days=amount * 7)
        elif unit == "month":
            delta = timedelta(days=amount * 30)
        else:
            delta = timedelta(days=amount * 365)
        return (datetime.now(timezone.utc) - delta).date().isoformat()
    zh_relative = re.search(r"(\d+)\s*(\u5c0f\u65f6|\u5929|\u5468|\u4e2a\u6708|\u6708|\u5e74)\u524d", value)
    if zh_relative:
        amount = int(zh_relative.group(1))
        unit = zh_relative.group(2)
        if unit == "\u5c0f\u65f6":
            delta = timedelta(hours=amount)
        elif unit == "\u5929":
            delta = timedelta(days=amount)
        elif unit == "\u5468":
            delta = timedelta(days=amount * 7)
        elif unit in {"\u4e2a\u6708", "\u6708"}:
            delta = timedelta(days=amount * 30)
        else:
            delta = timedelta(days=amount * 365)
        return (datetime.now(timezone.utc) - delta).date().isoformat()
    return ""


def is_within_freshness(published_at: str, freshness_days: int | None) -> bool:
    if not freshness_days:
        return True
    if not published_at:
        return False
    try:
        published = datetime.fromisoformat(published_at).date()
    except ValueError:
        return False
    cutoff = (datetime.now(timezone.utc) - timedelta(days=freshness_days)).date()
    return published >= cutoff


def is_recent_youtube_video_date(published_at: str) -> bool:
    return is_within_freshness(published_at, YOUTUBE_MAX_VIDEO_AGE_DAYS)


def latest_iso_date(values: list[str]) -> str:
    latest = ""
    latest_date = None
    for value in values:
        if not value:
            continue
        try:
            current = datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            parsed = extract_published_at(value)
            if not parsed:
                continue
            try:
                current = datetime.fromisoformat(parsed).date()
            except ValueError:
                continue
            value = parsed
        if latest_date is None or current > latest_date:
            latest_date = current
            latest = current.isoformat()
    return latest


def source_details(url: str, fallback_origin: str = "公开网页搜索") -> tuple[str, str]:
    domain = safe_urlparse(url).netloc.lower().removeprefix("www.")
    if "openstreetmap.org" in domain:
        return "OpenStreetMap", "地图与地理商业目录"
    if "instagram.com" in domain:
        return "Instagram", "社交媒体商业主页"
    if "facebook.com" in domain:
        return "Facebook", "社交媒体商业主页"
    if "linkedin.com" in domain:
        return "LinkedIn", "企业与职业社交平台"
    if "youtube.com" in domain or "youtu.be" in domain:
        return "YouTube", "视频与频道公开资料"
    if "tiktok.com" in domain:
        return "TikTok", "短视频公开账号"
    if domain in {"t.me", "telegram.me", "telegram.dog"}:
        return "Telegram", "Telegram 公开频道或群组"
    if "x.com" in domain or "twitter.com" in domain:
        return "X / Twitter", "X / Twitter 公开主页"
    if "threads.net" in domain:
        return "Threads", "Threads 公开主页"
    if "pinterest." in domain:
        return "Pinterest", "Pinterest 公开主页"
    if "reddit.com" in domain:
        return "Reddit", "Reddit 公开社区或用户"
    if "vk.com" in domain:
        return "VK", "VK 公开主页"
    local_domains = local_discovery_domains()
    if domain in local_domains or any(domain.endswith(f".{item}") for item in local_domains):
        return domain, "Local automotive directory"
    if domain:
        return domain, "车商官网或汽车行业网站"
    return fallback_origin, "公开商业信息网站"


def source_category(url: str, title: str = "", snippet: str = "") -> tuple[str, str]:
    value = f"{url} {title} {snippet}".lower()
    domain = safe_urlparse(url).netloc.lower().removeprefix("www.")
    if "google.com/maps" in value:
        return "Google Maps", "地图企业资料"
    if "openstreetmap.org" in domain:
        return "OpenStreetMap", "地图企业资料"
    if "linkedin.com" in domain:
        return "LinkedIn", "公司或职业资料"
    if "instagram.com" in domain:
        return "Instagram", "社交媒体"
    if "facebook.com" in domain:
        return "Facebook", "社交媒体"
    if "youtube.com" in domain or "youtu.be" in domain:
        return "YouTube", "社交媒体"
    if "tiktok.com" in domain:
        return "TikTok", "社交媒体"
    if domain in {"t.me", "telegram.me", "telegram.dog"}:
        return "Telegram", "社交媒体"
    if "x.com" in domain or "twitter.com" in domain:
        return "X / Twitter", "社交媒体"
    if "threads.net" in domain:
        return "Threads", "社交媒体"
    if "pinterest." in domain:
        return "Pinterest", "社交媒体"
    if "reddit.com" in domain:
        return "Reddit", "社交媒体"
    if "vk.com" in domain:
        return "VK", "社交媒体"
    local_domains = local_discovery_domains()
    if domain in local_domains or any(domain.endswith(f".{item}") for item in local_domains):
        return domain or "Local automotive directory", "Local automotive directory"
    if any(word in value for word in ("exhibitor", "motor show", "auto show", "exhibition")):
        return domain or "展会网站", "展会参展信息"
    if any(word in value for word in ("chamber", "association", "council", "member directory")):
        return domain or "协会网站", "商会或行业协会名录"
    if any(word in value for word in ("dealer", "cars for sale", "motors", "automotive directory")):
        return domain or "汽车行业网站", "汽车交易或行业目录"
    return domain or "公开网页", "公司官网或公开网页"


def infer_company_name(title: str, domain: str) -> str:
    title = clean_text(title)
    parts = [part.strip(" -–—") for part in re.split(r"\s*[|]\s*", title) if part.strip()]
    generic = re.compile(
        r"^(home|official website|welcome)|"
        r"(your .*vehicle|luxury .* distributor|car trading company|"
        r"luxury car dealers?|car importer|car exporter|imports? .* sales|"
        r"global distributor|worldwide export|buy cars?|cars? for sale|"
        r"new and used cars?|trusted importer)",
        re.I,
    )
    for candidate in reversed(parts):
        if 2 < len(candidate) <= 80 and not generic.search(candidate) and not re.match(r"^20\d{2}\b", candidate):
            candidate = re.sub(
                r"\s+[-–—]\s+(?:[A-Za-z &]+(?:showroom)?|NISSAN)$",
                "",
                candidate,
                flags=re.I,
            ).strip()
            return candidate
    base = domain.split(".")[0].replace("-", " ").replace("_", " ").strip()
    replacements = {
        "llc": "LLC",
        "uae": "UAE",
        "agmc": "AGMC",
    }
    words = [replacements.get(word.lower(), word.capitalize()) for word in re.findall(r"[A-Za-z0-9]+", base)]
    return " ".join(words) or title[:80] or domain


def source_reliability(source_type: str, source_name: str = "") -> tuple[str, int, str]:
    value = f"{source_type} {source_name}".lower()
    if "官方公司页面" in source_type or "公司官网" in source_name:
        return "A", 95, "公司官方页面直接公开"
    if "官方关联企业页面" in source_type or "关联企业官网" in source_name:
        return "A", 90, "关联集团或企业官方页面公开"
    if "openstreetmap" in value or "地图与地理商业目录" in source_type:
        return "B", 76, "公开地图目录，需要官网或社媒交叉确认"
    if "google" in value or "地图企业资料" in source_type:
        return "B", 82, "主流地图企业资料，可与官网交叉核验"
    if "公司或职业资料" in source_type or "linkedin" in value:
        return "B", 78, "公开职业或公司资料"
    if "社交媒体" in source_type or any(name in value for name in (
        "facebook", "instagram", "tiktok", "youtube", "telegram",
        "twitter", "threads", "pinterest", "reddit", "vk"
    )):
        return "B", 72, "公开社媒账号，需确认与公司关联"
    if "协会" in source_type or "展会" in source_type:
        return "B", 74, "公开机构名单或参展信息"
    if "行业目录" in source_type or "汽车交易" in source_type:
        return "C", 62, "第三方行业目录，建议回到官网核验"
    return "C", 55, "普通公开网页搜索结果"


def evidence_item(
    url: str,
    title: str,
    excerpt: str,
    source_name: str = "",
    source_type: str = "",
) -> dict:
    if not source_name or not source_type:
        detected_name, detected_type = source_category(url, title, excerpt)
        source_name = source_name or detected_name
        source_type = source_type or detected_type
    reliability, reliability_score, reliability_reason = source_reliability(source_type, source_name)
    return {
        "title": clean_text(title)[:180] or source_name,
        "url": normalize_public_url(url),
        "excerpt": clean_text(excerpt)[:520],
        "sourceName": source_name,
        "sourceType": source_type,
        "reliability": reliability,
        "reliabilityScore": reliability_score,
        "reliabilityReason": reliability_reason,
    }


def merge_value_sources(
    base: dict,
    field: str,
    values: list[str],
    source_url: str,
    source_name: str,
) -> None:
    records_key = f"{field}_sources"
    records = list(base.get(records_key) or [])
    normalized_url = normalize_public_url(source_url)
    for value in values:
        value = str(value or "").strip()
        if not value:
            continue
        comparison_value = (
            re.sub(r"\D", "", value)
            if field == "phone"
            else value.lower().rstrip("/")
        )
        record = next(
            (
                item for item in records
                if (
                    re.sub(r"\D", "", item.get("value", ""))
                    if field == "phone"
                    else item.get("value", "").lower().rstrip("/")
                ) == comparison_value
            ),
            None,
        )
        if not record:
            record = {"value": value, "sources": []}
            records.append(record)
        if normalized_url and not any(
            item.get("url", "").lower().rstrip("/") == normalized_url.lower().rstrip("/")
            for item in record["sources"]
        ):
            record["sources"].append(
                {
                    "url": normalized_url,
                    "name": source_name or source_category(normalized_url)[0],
                }
            )
    base[records_key] = records[:20]
    if not base.get(field) and records:
        base[field] = records[0]["value"]


def merge_contact_data(
    base: dict,
    incoming: dict,
    source_url: str = "",
    source_name: str = "",
    verified: bool = False,
    source_excerpt: str = "",
) -> dict:
    for key in ("email", "phone", "whatsapp", "contact_name", "contact_role"):
        if not base.get(key) and incoming.get(key):
            base[key] = incoming[key]
    email_sources = list(base.get("email_sources") or [])
    for email in incoming.get("emails") or ([incoming["email"]] if incoming.get("email") else []):
        normalized_email = email.strip().lower()
        if not normalized_email:
            continue
        record = next(
            (item for item in email_sources if item.get("email", "").lower() == normalized_email),
            None,
        )
        if not record:
            record = {"email": email.strip(), "sources": []}
            email_sources.append(record)
        normalized_url = normalize_public_url(source_url)
        if normalized_url and not any(
            item.get("url", "").lower().rstrip("/") == normalized_url.lower().rstrip("/")
            for item in record["sources"]
        ):
            record["sources"].append(
                {
                    "url": normalized_url,
                    "name": source_name or source_category(normalized_url)[0],
                    "verified": bool(verified),
                    "excerpt": email_context(source_excerpt, email),
                }
            )
        elif verified:
            for item in record["sources"]:
                if item.get("url", "").lower().rstrip("/") == normalized_url.lower().rstrip("/"):
                    item["verified"] = True
                    if source_excerpt:
                        item["excerpt"] = email_context(source_excerpt, email)
    base["email_sources"] = email_sources[:20]
    verified_emails = [
        item for item in email_sources
        if any(source.get("verified") for source in item.get("sources", []))
    ]
    if verified_emails:
        base["email"] = verified_emails[0]["email"]
    merge_value_sources(
        base,
        "phone",
        incoming.get("phones") or ([incoming["phone"]] if incoming.get("phone") else []),
        source_url,
        source_name,
    )
    merge_value_sources(
        base,
        "whatsapp",
        incoming.get("whatsapps") or ([incoming["whatsapp"]] if incoming.get("whatsapp") else []),
        source_url,
        source_name,
    )
    if incoming.get("contact_name"):
        merge_value_sources(base, "contact_name", [incoming["contact_name"]], source_url, source_name)
    if incoming.get("contact_role"):
        merge_value_sources(base, "contact_role", [incoming["contact_role"]], source_url, source_name)
    accounts = list(base.get("social_accounts") or [])
    for account in incoming.get("social_accounts") or []:
        if account not in accounts:
            accounts.append(account)
    base["social_accounts"] = accounts[:10]
    return base


def email_context(text: str, email: str, radius: int = 120) -> str:
    cleaned = clean_text(text)
    match = re.search(re.escape(email), cleaned, re.I)
    if not match:
        return f"该邮箱已在此公开页面中核验：{email}"
    start = max(0, match.start() - radius)
    end = min(len(cleaned), match.end() + radius)
    return cleaned[start:end].strip()


def hunter_email_candidates(website: str, company: str = "", limit: int = 5) -> list[dict]:
    api_key = get_hunter_api_key()
    if not api_key or not website:
        return []
    domain = safe_urlparse(website).netloc.lower().removeprefix("www.")
    if not domain or not is_business_website_url(f"https://{domain}"):
        return []
    params = {
        "domain": domain,
        "api_key": api_key,
        "limit": max(1, min(10, limit)),
    }
    if company:
        params["company"] = company[:80]
    data = fetch_json(
        "https://api.hunter.io/v2/domain-search?" + urllib.parse.urlencode(params),
        timeout=DISCOVERY_SEARCH_TIMEOUT,
    )
    record_api_usage("hunter", True)
    emails = []
    for item in ((data.get("data") or {}).get("emails") or []):
        if not isinstance(item, dict):
            continue
        email = clean_text(str(item.get("value") or "")).lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            continue
        emails.append({
            "email": email,
            "confidence": item.get("confidence", 0),
            "firstName": item.get("first_name") or "",
            "lastName": item.get("last_name") or "",
            "position": item.get("position") or "",
            "sources": item.get("sources") if isinstance(item.get("sources"), list) else [],
        })
        if len(emails) >= limit:
            break
    return emails


def official_site_pages(website: str) -> list[dict]:
    website = normalize_public_url(website)
    if not is_business_website_url(website):
        return []
    try:
        homepage, final_website = fetch_document(website, timeout=12)
    except (OSError, TimeoutError, UnicodeError):
        return []
    parsed = safe_urlparse(final_website)
    root = f"{parsed.scheme}://{parsed.netloc}"
    candidates = [final_website]
    links = re.findall(r'href=["\']([^"\']+)["\']', homepage, flags=re.I)
    preferred = []
    for href in links:
        absolute = urllib.parse.urljoin(final_website, html.unescape(href))
        path = safe_urlparse(absolute).path.lower()
        if safe_urlparse(absolute).netloc != parsed.netloc:
            continue
        if not is_business_website_url(absolute):
            continue
        if any(word in path for word in ("/contact", "/about", "/team", "/management", "/leadership")):
            if absolute not in preferred:
                preferred.append(absolute)
    candidates.extend(preferred[:3])
    pages = []
    for index, url in enumerate(candidates):
        try:
            if index == 0:
                page, final_url = homepage, final_website
            else:
                page, final_url = fetch_document(url, timeout=10)
        except (OSError, TimeoutError, UnicodeError):
            continue
        pages.append({"url": final_url, "html": page, "text": extract_meta(page)})
    return pages


def audit_customer_website(website: str) -> dict:
    website = normalize_public_url(website)
    result = {
        "url": website,
        "reachable": False,
        "vehicleRelated": False,
        "pages": [],
        "text": "",
        "reason": "",
    }
    if not is_business_website_url(website):
        result["reason"] = "not_business_website_url"
        return result
    try:
        pages = official_site_pages(website)
    except (OSError, TimeoutError, UnicodeError, urllib.error.URLError, http.client.HTTPException):
        pages = []
    if not pages:
        result["reason"] = "website_unreachable"
        return result
    page_text = " ".join(
        clean_text(page.get("html", ""))[:20_000] or page.get("text", "")
        for page in pages[:3]
    )
    final_url = normalize_public_url(pages[0].get("url", "")) or website
    result.update({
        "url": final_url,
        "reachable": True,
        "pages": pages,
        "text": page_text,
        "vehicleRelated": has_automotive_business_signal(f"{final_url} {page_text}"),
    })
    if not result["vehicleRelated"]:
        result["reason"] = "website_not_vehicle_related"
    return result


def official_contact_entry(pages: list[dict]) -> dict:
    contact_words = (
        "contact", "contact-us", "contacts", "inquiry", "enquiry", "request",
        "quote", "get-a-quote", "callback", "appointment", "book", "location",
        "showroom", "sales", "support", "whatsapp", "tel:", "mailto:",
        "联系我们", "联系", "询价", "销售", "展厅",
    )
    for page in pages or []:
        url = normalize_public_url(str(page.get("url") or ""))
        html_text = str(page.get("html") or "")
        visible_text = clean_text(html_text or str(page.get("text") or ""))
        path = safe_urlparse(url).path.lower()
        haystack = f"{url} {path} {visible_text[:5000]}".lower()
        if any(word.lower() in haystack for word in contact_words):
            return {
                "url": url,
                "excerpt": visible_text[:700],
            }
    return {}


def company_domain_candidates(company: str) -> list[str]:
    stop_words = {
        "auto", "autos", "car", "cars", "motor", "motors", "group", "llc",
        "ltd", "inc", "co", "company", "trading", "dealer", "dealership",
        "sales", "sale", "used", "preowned", "pre", "owned",
    }
    tokens = [
        token.lower()
        for token in re.findall(r"[a-z0-9]+", company or "", flags=re.I)
        if len(token) > 1
    ]
    core_tokens = [token for token in tokens if token not in stop_words] or tokens
    if not core_tokens:
        return []
    domain_cores = []
    for count in (2, 3, 4):
        if len(tokens) >= count:
            domain_cores.extend(["".join(tokens[:count]), "-".join(tokens[:count])])
    for count in (2, 3, 4):
        if len(core_tokens) >= count:
            domain_cores.extend(["".join(core_tokens[:count]), "-".join(core_tokens[:count])])
    domain_cores.extend(["".join(core_tokens[:4]), "-".join(core_tokens[:4])])
    candidates = []
    for domain_core in dict.fromkeys(core for core in domain_cores if core):
        candidates.extend([f"https://www.{domain_core}.com", f"https://{domain_core}.com"])
    return list(dict.fromkeys(candidates))


def website_matches_company(company: str, pages: list[dict]) -> bool:
    tokens = [
        token.lower()
        for token in re.findall(r"[a-z0-9]+", company or "", flags=re.I)
        if len(token) > 2
    ]
    if not tokens or not pages:
        return False
    haystack = " ".join(
        f"{page.get('url', '')} {page.get('text', '')}"
        for page in pages[:2]
    ).lower()
    required = min(len(tokens), 2)
    return sum(token in haystack for token in tokens[:4]) >= required


def infer_company_website(company: str) -> tuple[str, list[dict]]:
    for candidate in company_domain_candidates(company):
        pages = official_site_pages(candidate)
        if website_matches_company(company, pages):
            return pages[0]["url"], pages
    return "", []


def ensure_public_lead_source_url(value: str) -> str:
    url = normalize_public_url(value)
    parsed = safe_urlparse(url)
    hostname = (parsed.hostname or "").strip().lower()
    if not url or not hostname or parsed.username or parsed.password:
        raise ValueError("请输入有效的公开网址")
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
        raise ValueError("不支持本机或内网网址")
    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
        }
    except socket.gaierror as exc:
        raise ValueError("网址域名无法解析") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%", 1)[0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise ValueError("不支持本机或内网网址")
    return url


def structured_business_names(page: str) -> list[str]:
    names: list[str] = []
    accepted_types = {
        "organization", "corporation", "localbusiness", "automotivebusiness",
        "autodealer", "store", "professionalservice",
    }

    def collect(value) -> None:
        if isinstance(value, list):
            for item in value:
                collect(item)
            return
        if not isinstance(value, dict):
            return
        raw_type = value.get("@type")
        types = raw_type if isinstance(raw_type, list) else [raw_type]
        normalized_types = {clean_text(str(item)).lower() for item in types if item}
        name = clean_text(str(value.get("name") or ""))
        if name and normalized_types.intersection(accepted_types) and name not in names:
            names.append(name)
        for key in ("@graph", "publisher", "provider", "seller", "brand"):
            collect(value.get(key))

    for raw in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',
        page,
        flags=re.I,
    ):
        try:
            collect(json.loads(html.unescape(raw).strip()))
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    return names[:8]


def clean_inferred_company_name(value: str) -> str:
    value = clean_text(html.unescape(value or ""))
    value = re.sub(r"\s+(?:[|–—:]|-\s+)\s*.*$", "", value).strip()
    value = re.sub(r"\s+(?:official website|official site|home)$", "", value, flags=re.I).strip()
    if len(value) < 2 or len(value) > 100:
        return ""
    if value.lower() in {"home", "welcome", "official", "website", "instagram", "facebook"}:
        return ""
    return value


def infer_company_from_source(url: str, page: str = "", social_profile: dict | None = None) -> str:
    candidates: list[str] = []
    if page:
        candidates.extend(structured_business_names(page))
        visible_text = clean_text(page)
        brand_match = re.search(
            r"\b([A-Z][A-Z0-9&.' ]{2,45})\s*[–—-]\s*(?:delivering|motors|automotive|cars|vehicles)",
            visible_text,
        )
        if brand_match:
            candidates.append(brand_match.group(1))
        for email_domain in re.findall(r"[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})", page, flags=re.I):
            domain = email_domain.lower().removeprefix("www.")
            if domain not in {"gmail.com", "outlook.com", "hotmail.com", "yahoo.com", "icloud.com", "mail.com"}:
                candidates.append(domain.split(".", 1)[0].replace("-", " ").title())
        meta = parse_meta_tags(page)
        candidates.extend([
            meta.get("og:site_name", ""),
            meta.get("application-name", ""),
            meta.get("og:title", ""),
            meta.get("twitter:title", ""),
        ])
        title_match = re.search(r"<title[^>]*>([\s\S]*?)</title>", page, flags=re.I)
        if title_match:
            candidates.append(title_match.group(1))
    if social_profile:
        candidates.extend([
            str(social_profile.get("title") or ""),
            str(social_profile.get("handle") or "").lstrip("@").replace("_", " "),
        ])
    domain = safe_urlparse(url).netloc.lower().removeprefix("www.").split(":", 1)[0]
    domain_stem = domain.split(".", 1)[0].replace("-", " ").replace("_", " ")
    candidates.append(domain_stem.title())
    for candidate in candidates:
        cleaned = clean_inferred_company_name(candidate)
        if cleaned:
            return cleaned
    return "未命名客户"


def infer_lead_location(text: str, url: str) -> tuple[str, str]:
    haystack = clean_text(text).lower()
    domain = safe_urlparse(url).netloc.lower().removeprefix("www.")
    tld_country = {
        ".ae": "UAE", ".sa": "Saudi", ".qa": "Qatar", ".kw": "Kuwait",
        ".om": "Oman", ".ng": "Nigeria", ".gh": "Ghana", ".eg": "Egypt",
        ".kz": "Kazakhstan", ".ru": "Russia", ".uz": "Uzbekistan",
        ".az": "Azerbaijan", ".am": "Armenia", ".kg": "Kyrgyzstan",
    }
    country = next((name for suffix, name in tld_country.items() if domain.endswith(suffix)), "")
    signal_aliases = {
        "UAE": ("united arab emirates", " uae ", "dubai", "abu dhabi", "+971"),
        "Saudi": ("saudi arabia", "riyadh", "jeddah", "+966"),
        "Qatar": (" qatar ", "doha", "+974"),
        "Kuwait": ("kuwait", "+965"),
        "Oman": (" oman ", "muscat", "+968"),
        "Nigeria": ("nigeria", "lagos", "abuja", "+234"),
        "Ghana": ("ghana", "accra", "+233"),
        "Egypt": ("egypt", "cairo", "+20"),
        "Uzbekistan": ("uzbekistan", "o'zbekiston", "tashkent", "toshkent", "+998"),
    }
    if not country:
        country = next(
            (name for name, aliases in signal_aliases.items() if any(alias in f" {haystack} " for alias in aliases)),
            "",
        )
    city = ""
    for candidate in COUNTRY_HINTS.get(country, ()):
        if candidate.lower() in haystack:
            city = candidate
            break
    return country, city


def infer_manual_lead_type(text: str) -> str:
    value = clean_text(text).lower()
    if re.search(r"\b(fleet|corporate transport|rental fleet|fleet buyer)\b", value):
        return "Fleet buyer"
    if re.search(r"\b(import|importer|deliver(?:y|ing)? .* from china|export)\b", value):
        return "Auto importer"
    if re.search(r"\b(luxury|premium|supercar).{0,40}\b(showroom|dealer|cars)\b", value):
        return "Luxury car showroom"
    if re.search(r"\b(parallel import|grey import)\b", value):
        return "Parallel import dealer"
    if re.search(r"\b(electric vehicle|electric cars|\bev\b|new energy)\b", value):
        return "EV dealer"
    return "Auto business" if has_automotive_business_signal(value) else "待确认"


def infer_recommended_model(text: str) -> str:
    value = clean_text(text).lower()
    model_signals = (
        (("maextro s800", "尊界 s800", "zunjie s800", "s800"), "尊界 S800"),
        (("aito m9", "问界 m9", "wenjie m9"), "问界 M9"),
        (("aito m8", "问界 m8", "wenjie m8"), "问界 M8"),
        (("luxeed r7", "智界 r7", "zhijie r7"), "智界 R7"),
        (("stelato s9", "享界 s9", "xiangjie s9"), "享界 S9"),
    )
    return next((model for aliases, model in model_signals if any(alias in value for alias in aliases)), "问界 M9")


def social_profile_website_candidates(source_url: str, profile: dict | None) -> list[str]:
    profile = profile if isinstance(profile, dict) else {}
    source_path = safe_urlparse(source_url).path.strip("/")
    handles = [
        str(profile.get("handle") or "").strip().lstrip("@"),
        source_path.split("/")[-1] if source_path else "",
    ]
    candidates: list[str] = []
    for handle in handles:
        if re.fullmatch(r"(?:[a-z0-9-]+\.)+[a-z]{2,}", handle, flags=re.I):
            candidates.append(normalize_public_url(handle))
    candidates.extend(extract_business_websites(" ".join([
        str(profile.get("title") or ""),
        str(profile.get("description") or ""),
    ])))
    candidates.extend(profile.get("externalWebsites") or [])
    return list(dict.fromkeys(
        normalize_public_url(item)
        for item in candidates
        if is_business_website_url(item)
    ))[:8]


def website_matches_social_profile(candidate: str, pages: list[dict], profile: dict | None) -> bool:
    profile = profile if isinstance(profile, dict) else {}
    identity_text = clean_text(" ".join([
        str(profile.get("title") or ""),
        str(profile.get("handle") or ""),
    ])).lower()
    stop_words = {
        "auto", "autos", "car", "cars", "motor", "motors", "automotive",
        "official", "company", "group", "dealer", "dealership", "showroom",
        "avtosalon", "uzbekistan", "tashkent", "toshkent",
    }
    identity_tokens = [
        token for token in re.findall(r"[a-z0-9]+", identity_text)
        if len(token) >= 4 and token not in stop_words
    ]
    handle = re.sub(r"[^a-z0-9]", "", str(profile.get("handle") or "").lower())
    handle_variants = {handle} if len(handle) >= 5 else set()
    for suffix in ("uz", "kz", "kg", "az", "ae", "uae", "sa", "qa"):
        if handle.endswith(suffix) and len(handle) - len(suffix) >= 5:
            handle_variants.add(handle[:-len(suffix)])
    haystack = " ".join([
        candidate,
        *[
            f"{item.get('url', '')} {clean_text(item.get('html', ''))[:30_000]} {item.get('text', '')}"
            for item in pages[:3]
        ],
    ]).lower()
    compact_haystack = re.sub(r"[^a-z0-9]", "", haystack)
    return any(value in compact_haystack for value in handle_variants) or any(
        token in haystack for token in identity_tokens
    )


def parse_lead_source(params: dict[str, list[str]]) -> dict:
    source_url = ensure_public_lead_source_url((params.get("url") or [""])[0])
    social_source = is_social_profile_url(source_url)
    page = ""
    final_url = source_url
    social_profile = None
    website = ""
    source_text = ""

    if social_source:
        social_profile = read_social_profile(
            source_url,
            account_type="公司账号",
            relationship="手动网址解析",
            fetch_remote=True,
        )
        if social_profile.get("profileNotFound"):
            raise ValueError("Instagram 公开主页不存在或已失效")
        final_url = normalize_public_url(social_profile.get("url", "")) or source_url
        source_text = clean_text(" ".join([
            str(social_profile.get("title") or ""),
            str(social_profile.get("description") or ""),
            " ".join(social_profile.get("businessSignals") or []),
        ]))
        for candidate in social_profile_website_candidates(source_url, social_profile):
            pages = official_site_pages(candidate)
            candidate_text = " ".join(
                clean_text(item.get("html", ""))[:20_000] or item.get("text", "")
                for item in pages[:3]
            )
            if (
                not pages
                or not has_automotive_business_signal(candidate_text)
                or not website_matches_social_profile(candidate, pages, social_profile)
            ):
                continue
            website = normalize_public_url(pages[0].get("url", "")) or candidate
            page = pages[0].get("html", "")
            source_text = clean_text(f"{source_text} {candidate_text}")
            break
    else:
        if not is_business_website_url(source_url):
            raise ValueError("该网址不是可识别的企业官网或支持的社媒主页")
        page, final_url = fetch_document(source_url, timeout=18)
        final_url = ensure_public_lead_source_url(final_url)
        website = final_url
        visible = clean_text(page)
        source_text = clean_text(f"{visible[:40000]} {visible[-20000:]}")

    company = infer_company_from_source(final_url, page, social_profile)
    country, city = infer_lead_location(source_text, website or final_url)
    lead_type = infer_manual_lead_type(source_text)
    model = infer_recommended_model(source_text)
    research_params = {
        "company": [company],
        "country": [", ".join(item for item in (city, country) if item)],
        "website": [website],
        "sourceUrl": [final_url],
        "socialUrls": [final_url if social_source else ""],
        "model": [model],
        "type": [lead_type],
        "mode": ["fast"],
        "inferWebsite": ["1" if website or not social_source else "0"],
    }
    result = research_company(research_params)
    if social_source and not website:
        for field, sources_field in (
            ("email", "emailSources"),
            ("phone", "phoneSources"),
            ("whatsapp", "whatsappSources"),
        ):
            result[field] = ""
            result[sources_field] = []
        direct_source = [{"url": final_url, "name": source_category(final_url)[0]}]
        if social_profile.get("publicEmail"):
            result["email"] = social_profile["publicEmail"]
            result["emailSources"] = [{"value": result["email"], "sources": direct_source}]
        if social_profile.get("publicPhone"):
            result["phone"] = social_profile["publicPhone"]
            result["phoneSources"] = [{"value": result["phone"], "sources": direct_source}]
    source_name, source_type = source_category(final_url)
    result.update({
        "company": company,
        "country": country,
        "city": city,
        "type": lead_type,
        "model": model,
        "source": source_name,
        "origin": source_name,
        "sourceType": source_type,
        "sourceTitle": company,
        "sourceUrl": final_url,
        "sourceExcerpt": extract_meta(page) if page else source_text[:1100],
        "websiteContent": extract_meta(page) if page else source_text[:1100],
        "parsedSourceKind": "social" if social_source else "website",
    })
    if social_profile and not result.get("socialProfiles"):
        result["socialProfiles"] = [social_profile]
    return result


def research_company(params: dict[str, list[str]]) -> dict:
    company = clean_text((params.get("company") or [""])[0])
    country = clean_text((params.get("country") or [""])[0])
    requested_model = clean_text((params.get("model") or [""])[0])
    lead_type = clean_text((params.get("type") or [""])[0])
    research_mode = clean_text((params.get("mode") or ["full"])[0]).lower()
    fast_mode = research_mode in {"fast", "batch", "quick"}
    infer_website = clean_text((params.get("inferWebsite") or ["1"])[0]).lower() not in {"0", "false", "no"}
    website = normalize_public_url((params.get("website") or [""])[0])
    source_url = normalize_public_url((params.get("sourceUrl") or [""])[0])
    provided_social_urls = [
        normalize_social_profile_url(value)
        for value in re.split(r"\s*\|\s*|\s+", (params.get("socialUrls") or [""])[0])
        if value.strip()
    ]
    provided_social_urls = [
        url for url in dict.fromkeys(provided_social_urls)
        if is_social_profile_url(url)
    ][:6 if fast_mode else 12]
    if website and not is_business_website_url(website):
        website = ""
    if not company:
        raise ValueError("缺少公司名称")

    evidence: list[dict] = []
    seen_urls: set[str] = set()
    social_relationships: dict[str, str] = {}
    social_account_types: dict[str, str] = {}
    contacts = {
        "email": "",
        "email_sources": [],
        "phone": "",
        "phone_sources": [],
        "whatsapp": "",
        "whatsapp_sources": [],
        "social_accounts": [],
        "contact_name": "",
        "contact_name_sources": [],
        "contact_role": "",
        "contact_role_sources": [],
    }

    inferred_site_pages: list[dict] = []
    if not website and infer_website:
        website, inferred_site_pages = infer_company_website(company)
    website_audit = {
        "url": website,
        "reachable": False,
        "vehicleRelated": False,
        "pages": [],
        "text": "",
        "reason": "no_customer_website",
    }
    if website:
        if inferred_site_pages:
            inferred_text = " ".join(
                clean_text(page.get("html", ""))[:20_000] or page.get("text", "")
                for page in inferred_site_pages[:3]
            )
            website_audit = {
                "url": normalize_public_url(inferred_site_pages[0].get("url", "")) or website,
                "reachable": True,
                "vehicleRelated": has_automotive_business_signal(
                    f"{inferred_site_pages[0].get('url', '')} {inferred_text}"
                ),
                "pages": inferred_site_pages,
                "text": inferred_text,
                "reason": "",
            }
            if not website_audit["vehicleRelated"]:
                website_audit["reason"] = "website_not_vehicle_related"
        else:
            website_audit = audit_customer_website(website)
        if not website_audit.get("reachable") or not website_audit.get("vehicleRelated"):
            website = ""
            inferred_site_pages = []
        else:
            website = website_audit.get("url") or website

    if source_url and not is_noise_source_url(source_url):
        name, kind = source_category(source_url)
        evidence.append(evidence_item(source_url, company, "原始线索来源", name, kind))
        seen_urls.add(source_url.lower().rstrip("/"))

    for social_url in provided_social_urls:
        key = social_url.lower().rstrip("/")
        if social_url not in contacts["social_accounts"]:
            contacts["social_accounts"].append(social_url)
        social_relationships[key] = "原线索社媒账号"
        social_account_types[key] = "公司账号"
        if key not in seen_urls:
            social_name, social_type = source_category(social_url)
            evidence.append(
                evidence_item(
                    social_url,
                    f"{company} 的{social_name}账号",
                    "该社媒主页来自原线索记录，重新审核时用于查找 Website 外链和联系方式。",
                    social_name,
                    social_type,
                )
            )
            seen_urls.add(key)

    site_pages = website_audit.get("pages") if website else []
    official_website_text = " ".join(
        clean_text(page.get("html", ""))[:20_000] or page.get("text", "")
        for page in site_pages
    )
    for page_index, page in enumerate(site_pages):
        page_contacts = extract_public_contacts(page["html"])
        merge_contact_data(
            contacts,
            page_contacts,
            page["url"],
            "公司官网" if page_index == 0 else "公司官网内页",
            verified=True,
            source_excerpt=page["html"],
        )
        key = page["url"].lower().rstrip("/")
        if key not in seen_urls:
            label = "公司官网" if page_index == 0 else "公司官网内页"
            evidence.append(evidence_item(page["url"], company, page["text"], label, "官方公司页面"))
            seen_urls.add(key)
        for social_url in page_contacts["social_accounts"]:
            social_key = social_url.lower().rstrip("/")
            social_relationships[social_key] = "公司官网直接链接"
            social_account_types[social_key] = "公司账号"
            if social_key in seen_urls:
                continue
            social_name, social_type = source_category(social_url)
            evidence.append(
                evidence_item(
                    social_url,
                    f"{company} 的 {social_name} 账号",
                    f"该账号链接由公司官网公开页面直接提供，需打开平台页面进一步核验。",
                    social_name,
                    social_type,
                )
            )
            seen_urls.add(social_key)

    email_domain = contacts["email"].split("@")[-1].lower() if "@" in contacts["email"] else ""
    website_domain = safe_urlparse(website).netloc.lower().removeprefix("www.")
    free_mail_domains = {"gmail.com", "outlook.com", "hotmail.com", "yahoo.com", "icloud.com"}
    if email_domain and email_domain not in free_mail_domains and email_domain != website_domain:
        corporate_pages = official_site_pages(f"https://{email_domain}")
        for page_index, page in enumerate(corporate_pages[:3]):
            page_contacts = extract_public_contacts(page["html"])
            merge_contact_data(
                contacts,
                page_contacts,
                page["url"],
                "关联企业官网" if page_index == 0 else "关联企业官网内页",
                verified=True,
                source_excerpt=page["html"],
            )
            key = page["url"].lower().rstrip("/")
            if key not in seen_urls:
                evidence.append(
                    evidence_item(
                        page["url"],
                        f"{company} 公开邮箱所属企业网站",
                        page["text"],
                        "关联企业官网",
                        "官方关联企业页面",
                    )
                )
                seen_urls.add(key)
            for social_url in page_contacts["social_accounts"]:
                social_key = social_url.lower().rstrip("/")
                social_relationships[social_key] = "关联企业官网直接链接"
                social_account_types[social_key] = "公司账号"
                if social_key in seen_urls:
                    continue
                social_name, social_type = source_category(social_url)
                evidence.append(
                    evidence_item(
                        social_url,
                        f"{company} 关联企业的 {social_name} 账号",
                        "该账号链接由公开邮箱所属企业网站直接提供，需打开平台页面核验。",
                        social_name,
                        social_type,
                    )
                )
                seen_urls.add(social_key)

    quoted = f'"{company}"'
    queries = [
        (f"{quoted} {country} official website contact", "公司账号", "公开网页搜索"),
        (f"{quoted} {country} exhibitor motor show auto show chamber association member directory", "公司账号", "公开网页搜索"),
        (f'site:facebook.com {quoted} {country}', "公司账号", "Facebook 公开搜索"),
        (f'site:instagram.com {quoted} {country}', "公司账号", "Instagram 公开搜索"),
        (f'site:youtube.com {quoted} {country}', "公司账号", "YouTube 公开搜索"),
        (f'site:tiktok.com/@ {quoted} {country}', "公开账号（公司/个人待核验）", "TikTok 公开搜索"),
        (f'site:linkedin.com/company {quoted} {country}', "公司账号", "LinkedIn 公开搜索"),
    ]
    if fast_mode:
        queries = queries[:2]
    if contacts["contact_name"] and not fast_mode:
        person = f'"{contacts["contact_name"]}"'
        queries.extend(
            [
                (f'site:facebook.com {person} {quoted}', "个人决策人", "姓名与公司联合搜索"),
                (f'site:instagram.com {person} {quoted}', "个人决策人", "姓名与公司联合搜索"),
                (f'site:youtube.com {person} {quoted}', "个人决策人", "姓名与公司联合搜索"),
                (f'site:tiktok.com/@ {person} {quoted}', "个人决策人", "姓名与公司联合搜索"),
                (f'site:linkedin.com/in {person} {quoted}', "个人决策人", "姓名与公司联合搜索"),
            ]
        )
    search_results: list[dict] = []
    with ThreadPoolExecutor(max_workers=3 if fast_mode else 6) as executor:
        futures = {
            executor.submit(search_web, query, 3 if fast_mode else 5, None, country): (account_type, relationship)
            for query, account_type, relationship in queries
        }
        for future in as_completed(futures):
            try:
                account_type, relationship = futures[future]
                for item in future.result():
                    item["_account_type"] = account_type
                    item["_relationship"] = relationship
                    search_results.append(item)
            except (OSError, ValueError, TimeoutError):
                continue

    company_tokens = [token for token in re.findall(r"[a-z0-9]+", company.lower()) if len(token) > 2]
    required_matches = 1 if len(company_tokens) <= 1 else 2
    for item in search_results:
        url = normalize_public_url(item.get("url", ""))
        if not url:
            continue
        haystack = f"{item.get('title', '')} {item.get('snippet', '')} {url}".lower()
        token_matches = sum(token in haystack for token in company_tokens[:4])
        if company_tokens and token_matches < required_matches:
            continue
        key = url.lower().rstrip("/")
        if key in seen_urls:
            continue
        seen_urls.add(key)
        evidence.append(evidence_item(url, item.get("title", company), item.get("snippet", "")))
        fetched_contacts = None
        fetched_excerpt = ""
        if not is_social_profile_url(url):
            try:
                fetched_page, final_url = fetch_document(url, timeout=5 if fast_mode else 10)
                fetched_contacts = extract_public_contacts(fetched_page)
                fetched_excerpt = fetched_page
                url = final_url
            except (OSError, TimeoutError, UnicodeError):
                fetched_contacts = None
        if fetched_contacts:
            merge_contact_data(
                contacts,
                fetched_contacts,
                url,
                source_category(url, item.get("title", ""), item.get("snippet", ""))[0],
                verified=True,
                source_excerpt=fetched_excerpt,
            )
        if is_social_profile_url(url):
            social_relationships[key] = item.get("_relationship", "公开搜索")
            social_account_types[key] = item.get("_account_type", "公司账号")
        if len(evidence) >= 14:
            break

    youtube_queries = [] if fast_mode else [(f"{company} {country}", "公司账号", "YouTube 频道搜索")]
    if contacts["contact_name"] and not fast_mode:
        youtube_queries.append(
            (f'{contacts["contact_name"]} {company}', "个人决策人", "姓名与公司联合搜索")
        )
    for youtube_query, account_type, relationship in youtube_queries:
        try:
            youtube_results = search_youtube_channels(youtube_query, limit=4, country=country)
        except (OSError, ValueError, TimeoutError, json.JSONDecodeError):
            youtube_results = []
        for item in youtube_results:
            haystack = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
            token_matches = sum(token in haystack for token in company_tokens[:4])
            person_match = contacts["contact_name"] and contacts["contact_name"].lower() in haystack
            if account_type == "公司账号" and company_tokens and token_matches < required_matches:
                continue
            if account_type == "个人决策人" and not person_match:
                continue
            url = normalize_public_url(item["url"])
            key = url.lower().rstrip("/")
            social_relationships[key] = relationship
            social_account_types[key] = account_type
            if url not in contacts["social_accounts"]:
                contacts["social_accounts"].append(url)
            if key not in seen_urls:
                evidence.append(
                    evidence_item(
                        url,
                        item.get("title", "YouTube channel"),
                        item.get("snippet", ""),
                        "YouTube",
                        "社交媒体",
                    )
                )
                seen_urls.add(key)

    social_urls = list(dict.fromkeys(
        [
            url for url in contacts["social_accounts"] if is_social_profile_url(url)
        ]
        + [
            item["url"] for item in evidence if is_social_profile_url(item.get("url", ""))
        ]
    ))[:4 if fast_mode else 16]
    social_profiles = []
    with ThreadPoolExecutor(max_workers=3 if fast_mode else 5) as executor:
        futures = {}
        for url in social_urls:
            key = url.lower().rstrip("/")
            futures[
                executor.submit(
                    read_social_profile,
                    url,
                    social_account_types.get(key, "公司账号"),
                    social_relationships.get(key, "公开搜索"),
                    fetch_remote=not fast_mode,
                )
            ] = url
        for future in as_completed(futures):
            try:
                social_profiles.append(future.result())
            except (OSError, ValueError, TimeoutError):
                continue
    social_profiles.sort(
        key=lambda item: (
            item["accountType"] != "公司账号",
            item["platform"],
            item["title"],
        )
    )
    social_external_websites = list(dict.fromkeys(
        website_url
        for profile in social_profiles
        for website_url in (profile.get("externalWebsites") or [])
        if is_business_website_url(website_url)
    ))
    if not site_pages and social_external_websites:
        for candidate_website in social_external_websites[:3]:
            candidate_pages = official_site_pages(candidate_website)
            if not candidate_pages:
                continue
            website = candidate_pages[0]["url"]
            site_pages = candidate_pages
            official_website_text = " ".join(
                clean_text(page.get("html", ""))[:20_000] or page.get("text", "")
                for page in site_pages
            )
            for page_index, page in enumerate(site_pages):
                page_contacts = extract_public_contacts(page["html"])
                merge_contact_data(
                    contacts,
                    page_contacts,
                    page["url"],
                    "公司官网" if page_index == 0 else "公司官网内页",
                    verified=True,
                    source_excerpt=page["html"],
                )
                key = page["url"].lower().rstrip("/")
                if key not in seen_urls:
                    evidence.append(
                        evidence_item(
                            page["url"],
                            company,
                            page["text"],
                            "公司官网" if page_index == 0 else "公司官网内页",
                            "官方公司页面",
                        )
                    )
                    seen_urls.add(key)
            break
    social_business_signals = list(dict.fromkeys(
        signal
        for profile in social_profiles
        for signal in profile.get("businessSignals", [])
    ))[:8]
    social_intent_signals = list(dict.fromkeys(
        signal
        for profile in social_profiles
        for signal in profile.get("intentSignals", [])
    ))[:8]
    social_decision_roles = list(dict.fromkeys(
        profile.get("decisionRole", "")
        for profile in social_profiles
        if profile.get("decisionRole")
    ))[:5]
    social_business_confidence = max(
        (int(profile.get("businessConfidence", 0)) for profile in social_profiles),
        default=0,
    )

    official_domains = {
        safe_urlparse(item["url"]).netloc.lower().removeprefix("www.")
        for item in evidence
        if item["sourceType"] == "官方公司页面"
    }
    independent = [
        item for item in evidence
        if safe_urlparse(item["url"]).netloc.lower().removeprefix("www.") not in official_domains
    ]
    source_types = {item["sourceType"] for item in evidence}
    confidence = 15
    if site_pages:
        confidence += 25
    if independent:
        confidence += min(20, len(independent) * 5)
    if "地图企业资料" in source_types:
        confidence += 10
    if "公司或职业资料" in source_types:
        confidence += 8
    if "社交媒体" in source_types:
        confidence += 5
    if contacts["email"]:
        confidence += 7
    if contacts["phone"]:
        confidence += 6
    if contacts["contact_name"] and contacts["contact_role"]:
        confidence += 8
    confidence = min(confidence, 96)
    confidence_label = "高" if confidence >= 75 else "中" if confidence >= 50 else "低"
    official_count = sum(
        item.get("reliability") == "A"
        for item in evidence
    )
    independent_domains = {
        safe_urlparse(item["url"]).netloc.lower().removeprefix("www.")
        for item in evidence
        if item.get("url")
    }
    missing_fields = []
    verified_email_sources = [
        record for record in contacts["email_sources"]
        if any(source.get("verified") for source in record.get("sources", []))
    ]
    if not website and not site_pages:
        missing_fields.append("官网")
    if website_audit.get("url") and not website_audit.get("reachable"):
        missing_fields.append("官网可打开")
    if website_audit.get("url") and not website_audit.get("vehicleRelated"):
        missing_fields.append("官网车辆相关")
    if not verified_email_sources:
        missing_fields.append("邮箱")
    if not contacts["phone_sources"]:
        missing_fields.append("电话")
    if not contacts["contact_name"]:
        missing_fields.append("联系人")
    if not social_profiles:
        missing_fields.append("社媒账号")
    contactable = bool(verified_email_sources or contacts["phone_sources"] or contacts["whatsapp_sources"])
    decision = (
        "建议优先联系"
        if confidence >= 75 and contactable and official_count
        else "建议人工复核"
        if confidence >= 50
        else "证据不足，暂不联系"
    )
    scoring_text = official_website_text or " ".join(item.get("excerpt", "") for item in evidence)
    is_china_target = country_search_meta(country).get("code") == "cn"
    is_competitor = False if is_china_target else detect_competitor(scoring_text)
    website_score, website_score_breakdown, score_dimensions, score_tier = lead_opportunity_score(
        scoring_text,
        bool(site_pages or website),
        contactable,
        requested_model=requested_model,
        lead_type=lead_type,
        is_competitor=is_competitor,
        target_country_match=has_target_country_signal(
            " ".join([
                scoring_text,
                *[item.get("title", "") for item in evidence],
                *[item.get("excerpt", "") for item in evidence],
                *[item.get("url", "") for item in evidence],
            ]),
            country.split(",")[-1].strip(),
        ),
        has_email=bool(verified_email_sources),
        has_phone=bool(contacts["phone_sources"]),
        has_whatsapp=bool(contacts["whatsapp_sources"]),
        has_decision_maker=bool(contacts["contact_name"] or contacts["contact_role"]),
        allow_competitor_auto=not is_china_target,
    )
    decision = (
        "疑似同行，建议排除"
        if is_competitor
        else "建议优先联系"
        if website_score >= 80 and confidence >= 65 and contactable
        else "值得跟进"
        if website_score >= 65 and confidence >= 50
        else "继续核验"
        if website_score >= 50
        else "低优先级，是否入池由人工决定"
    )
    business_signals, intent_signals = opportunity_signals(
        official_website_text or " ".join(item.get("excerpt", "") for item in evidence)
    )
    business_signals = list(dict.fromkeys([*business_signals, *social_business_signals]))[:8]
    intent_signals = list(dict.fromkeys([*intent_signals, *social_intent_signals]))[:8]

    return {
        "ok": True,
        "company": company,
        "customerWebsite": website,
        "contactName": contacts["contact_name"],
        "contactRole": contacts["contact_role"],
        "email": contacts["email"],
        "emailSources": verified_email_sources,
        "unverifiedEmailCandidates": [
            record for record in contacts["email_sources"]
            if record not in verified_email_sources
        ],
        "phone": contacts["phone"],
        "phoneSources": contacts["phone_sources"],
        "whatsapp": contacts["whatsapp"],
        "whatsappSources": contacts["whatsapp_sources"],
        "contactNameSources": contacts["contact_name_sources"],
        "contactRoleSources": contacts["contact_role_sources"],
        "socialAccounts": contacts["social_accounts"],
        "socialProfiles": social_profiles,
        "socialBusinessSignals": social_business_signals,
        "socialIntentSignals": social_intent_signals,
        "socialDecisionRole": "、".join(social_decision_roles),
        "socialBusinessConfidence": social_business_confidence,
        "evidenceSources": evidence,
        "confidence": confidence,
        "confidenceLabel": confidence_label,
        "score": website_score,
        "baseScore": website_score,
        "scoreModelVersion": 11,
        "scoreTier": score_tier,
        "scoreDimensions": score_dimensions,
        "scoreBreakdown": website_score_breakdown,
        "scoreBasis": "100分线索模型：汽车业务20、地区匹配20、联系方式15、官网10、中国新能源10、华为系列10、进口分销8、经营活跃4、决策人3，另计风险扣分",
        "isCompetitor": is_competitor,
        "businessSignals": business_signals,
        "intentSignals": intent_signals,
        "sourceCoverage": {
            "total": len(evidence),
            "official": official_count,
            "independentDomains": len(independent_domains),
            "contactable": contactable,
            "websiteReachable": bool(website_audit.get("reachable")),
            "websiteVehicleRelated": bool(website_audit.get("vehicleRelated")),
            "websiteAuditReason": website_audit.get("reason", ""),
            "missingFields": missing_fields,
            "decision": decision,
        },
        "researchAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "researchSummary": (
            f"已核对 {len(evidence)} 个公开来源，其中 "
            f"{len(site_pages)} 个官网页面、{len(independent)} 个独立来源。"
        ),
    }


def get_google_maps_api_key() -> str:
    key = runtime_setting("GOOGLE_MAPS_API_KEY")
    if key:
        return key
    if not GOOGLE_MAPS_KEY_FILE.exists():
        return ""
    for line in GOOGLE_MAPS_KEY_FILE.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            return value
    return ""


def search_google_places(country: str, query_terms: str, limit: int = 12, city: str = "") -> list[dict]:
    api_key = get_google_maps_api_key()
    if not api_key:
        raise RuntimeError("Google Maps API 密钥未配置")
    city = city or next(
        (value[0] for key, value in CITY_COORDS.items() if key.lower() in country.lower()),
        CITY_COORDS["UAE"][0],
    )
    body = json.dumps(
        {
            "textQuery": f"{query_terms} in {city}, {country_search_meta(country)['location']}",
            "pageSize": min(max(limit, 1), 20),
            "languageCode": "en",
            "regionCode": country_search_meta(country)["code"].upper(),
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://places.googleapis.com/v1/places:searchText",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.googleMapsUri,places.websiteUri,places.nationalPhoneNumber,"
                "places.internationalPhoneNumber,places.rating,places.userRatingCount,"
                "places.businessStatus,places.primaryTypeDisplayName"
            ),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8", errors="ignore"))
    record_api_usage("google-maps", True)
    items = []
    for place in payload.get("places", []):
        name = (place.get("displayName") or {}).get("text", "").strip()
        if not name:
            continue
        maps_url = place.get("googleMapsUri") or (
            f"https://www.google.com/maps/search/?api=1&query_place_id={place.get('id', '')}"
        )
        website = normalize_public_url(place.get("websiteUri") or "")
        phone = place.get("internationalPhoneNumber") or place.get("nationalPhoneNumber") or ""
        rating = place.get("rating")
        ratings_count = place.get("userRatingCount")
        category = (place.get("primaryTypeDisplayName") or {}).get("text", "")
        snippet_parts = [
            f"{name} is listed on Google Maps",
            place.get("formattedAddress", ""),
            category,
        ]
        if phone:
            snippet_parts.append(f"Phone: {phone}")
        if rating:
            snippet_parts.append(f"Rating: {rating} from {ratings_count or 0} reviews")
        items.append(
            {
                "title": name,
                "url": website or maps_url,
                "source_url": maps_url,
                "customer_website": website,
                "snippet": ". ".join(part for part in snippet_parts if part) + ".",
                "contact": phone,
                "origin": "Google Maps",
                "source_type": "Google 地图企业资料",
                "google_rating": rating or 0,
                "google_reviews": ratings_count or 0,
                "business_status": place.get("businessStatus", ""),
                "skip_fetch": not bool(website),
            }
        )
    return items


def search_serpapi_google_maps(country: str, query_terms: str, limit: int = 12, city: str = "") -> list[dict]:
    api_key = get_serpapi_api_key()
    if not api_key:
        return []
    city = city or next(
        (value[0] for key, value in CITY_COORDS.items() if key.lower() in country.lower()),
        CITY_COORDS["UAE"][0],
    )
    meta = country_search_meta(country)
    params = {
        "engine": "google_maps",
        "q": f"{query_terms} in {city}, {meta['location']}",
        "api_key": api_key,
        "hl": "zh-cn" if meta.get("code") == "cn" else "en",
        "gl": meta["code"],
        "google_domain": meta["google_domain"],
        "ll": f"@{CITY_COORDS.get(next((key for key in CITY_COORDS if key.lower() in country.lower()), 'UAE'))[1]},{CITY_COORDS.get(next((key for key in CITY_COORDS if key.lower() in country.lower()), 'UAE'))[2]},12z",
        "type": "search",
    }
    data = fetch_json(
        "https://serpapi.com/search.json?" + urllib.parse.urlencode(params),
        timeout=DISCOVERY_SEARCH_TIMEOUT,
    )
    record_api_usage("serpapi:maps", True)
    items: list[dict] = []
    for place in data.get("local_results") or []:
        if not isinstance(place, dict):
            continue
        name = clean_text(str(place.get("title") or ""))
        if not name:
            continue
        maps_url = (
            f"https://www.google.com/maps/search/?api=1&query_place_id={place.get('place_id')}"
            if place.get("place_id")
            else ""
        )
        website = normalize_public_url(str(place.get("website") or ""))
        phone = clean_text(str(place.get("phone") or ""))
        snippet_parts = [
            f"{name} is listed on Google Maps via SerpApi",
            clean_text(str(place.get("address") or "")),
            clean_text(str(place.get("type") or "")),
        ]
        if phone:
            snippet_parts.append(f"Phone: {phone}")
        if place.get("rating"):
            snippet_parts.append(f"Rating: {place.get('rating')} from {place.get('reviews') or 0} reviews")
        items.append({
            "title": name,
            "url": website or maps_url or f"https://www.google.com/maps/search/{urllib.parse.quote(name)}",
            "source_url": maps_url or f"https://www.google.com/maps/search/{urllib.parse.quote(name)}",
            "customer_website": website,
            "snippet": ". ".join(part for part in snippet_parts if part) + ".",
            "contact": phone,
            "origin": "SerpApi Google Maps",
            "source_type": "Google 地图企业资料",
            "google_rating": place.get("rating") or 0,
            "google_reviews": place.get("reviews") or 0,
            "business_status": "",
            "apiSource": "SerpApi Google Maps",
            "skip_fetch": not bool(website),
        })
        if len(items) >= limit:
            break
    return items


def company_identity_tokens(company: str) -> list[str]:
    stop_words = {
        "auto", "autos", "car", "cars", "vehicle", "vehicles", "motor", "motors",
        "dealer", "dealership", "showroom", "sales", "trading", "trade", "llc",
        "ltd", "limited", "inc", "group", "company", "co", "used", "preowned",
    }
    tokens = [
        token.lower()
        for token in re.findall(r"[a-z0-9]+", company or "", flags=re.I)
        if len(token) > 2
    ]
    core = [token for token in tokens if token not in stop_words]
    return core or tokens[:4]


def company_name_matches_text(company: str, text: str) -> bool:
    tokens = company_identity_tokens(company)
    if not tokens:
        return False
    haystack = (text or "").lower()
    required = 1 if len(tokens) <= 2 else 2
    return sum(1 for token in tokens[:5] if token in haystack) >= required


def add_unique_evidence(evidence: list[dict], item: dict) -> None:
    url = normalize_public_url(item.get("url", ""))
    if not url:
        return
    if any(normalize_public_url(source.get("url", "")).lower().rstrip("/") == url.lower().rstrip("/") for source in evidence):
        return
    evidence.append(item)


def reverse_search_company_socials(company: str, country: str, limit_per_platform: int = 2) -> tuple[list[str], list[dict]]:
    accounts: list[str] = []
    evidence: list[dict] = []

    def accept_social(url: str, title: str, snippet: str, origin: str, source_type: str) -> None:
        normalized = normalize_social_profile_url(url)
        if not normalized or not is_social_profile_url(normalized):
            return
        text = f"{title} {snippet} {normalized}"
        if not company_name_matches_text(company, text):
            return
        if normalized not in accounts:
            accounts.append(normalized)
        add_unique_evidence(
            evidence,
            evidence_item(normalized, title or company, snippet, origin, source_type),
        )

    try:
        for item in search_youtube_channels(f"{company} {country}", limit=max(3, limit_per_platform * 2), country=country):
            published_at = item.get("latestVideoPublishedAt", "")
            if published_at and not is_recent_youtube_video_date(published_at):
                continue
            accept_social(
                item.get("url", ""),
                item.get("title", ""),
                item.get("snippet", ""),
                "YouTube",
                "YouTube 公开频道",
            )
            if len([url for url in accounts if "youtube." in safe_urlparse(url).netloc.lower()]) >= limit_per_platform:
                break
    except (OSError, ValueError, TimeoutError, json.JSONDecodeError):
        pass

    platform_queries = [
        ("facebook.com", "Facebook", "Facebook 公开主页"),
        ("instagram.com", "Instagram", "Instagram 公开主页"),
        ("linkedin.com/company", "LinkedIn", "LinkedIn 公司主页"),
    ]
    for site, origin, source_type in platform_queries:
        try:
            results = search_web(f'site:{site} "{company}" {country}', limit=5, freshness_days=None, country=country)
        except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
            continue
        accepted = 0
        for result in results:
            accept_social(
                result.get("url", ""),
                result.get("title", ""),
                result.get("snippet", ""),
                origin,
                source_type,
            )
            if any(origin.lower().split()[0] in safe_urlparse(url).netloc.lower() for url in accounts[-1:]):
                accepted += 1
            if accepted >= limit_per_platform:
                break

    return accounts[:8], evidence[:10]


def enrich_google_place_result(item: dict, country: str, include_reverse_social: bool = False) -> dict:
    """Add official-website contacts; reverse-search social profiles only when requested."""
    company = clean_text(item.get("title", ""))
    website = normalize_public_url(item.get("customer_website") or item.get("url") or "")
    contacts = extract_public_contacts(f"{item.get('snippet', '')} {item.get('contact', '')}", item.get("tags"))
    evidence: list[dict] = []
    add_unique_evidence(
        evidence,
        evidence_item(
            item.get("source_url") or item.get("url") or "",
            company,
            item.get("snippet", ""),
            "Google Maps",
            "Google Maps 企业资料",
        ),
    )

    official_pages: list[dict] = []
    if website and is_business_website_url(website):
        official_pages = official_site_pages(website)[:4]
        for page in official_pages:
            page_text = page.get("text") or clean_text(page.get("html", ""))
            contacts = merge_public_contacts(contacts, extract_public_contacts(page.get("html", "")))
            add_unique_evidence(
                evidence,
                evidence_item(
                    page.get("url", ""),
                    f"{company} official website",
                    page_text,
                    "公司官网",
                    "官方公司页面",
                ),
            )

    social_accounts = list(contacts.get("social_accounts") or [])
    social_evidence: list[dict] = []
    for account in social_accounts[:8]:
        add_unique_evidence(
            social_evidence,
            evidence_item(
                account,
                f"{company} social account",
                f"Social profile linked from the official website for {company}.",
                social_platform(account) or "社媒主页",
                "官网外链社媒账号",
            ),
        )
    reverse_accounts, reverse_evidence = (
        reverse_search_company_socials(company, country, limit_per_platform=1)
        if include_reverse_social
        else ([], [])
    )
    for account in reverse_accounts:
        if account not in social_accounts:
            social_accounts.append(account)
    for source in [*social_evidence, *reverse_evidence]:
        add_unique_evidence(evidence, source)

    contacts["social_accounts"] = list(dict.fromkeys(social_accounts))[:10]
    item["google_public_contacts"] = contacts
    item["google_evidence"] = evidence[:14]
    item["google_official_pages"] = official_pages
    if website and is_business_website_url(website):
        item["customer_website"] = website
        item["url"] = website
        item["skip_fetch"] = False
    return item


def search_osm_dealers(country: str, limit: int = 12, target_type: str = "dealer") -> list[dict]:
    location = next(
        (value for key, value in CITY_COORDS.items() if key.lower() in country.lower()),
        CITY_COORDS["UAE"],
    )
    city, latitude, longitude = location
    country_key = next((key for key in OSM_SEARCH_CENTERS if key.lower() in country.lower()), "")
    search_centers = OSM_SEARCH_CENTERS.get(country_key) or ((city, latitude, longitude),)
    selectors = TARGET_PROFILES.get(target_type, TARGET_PROFILES["dealer"])["osm"]
    if not selectors:
        return []
    osm_parts = "".join(
        f"{selector}(around:{30000 if len(search_centers) > 1 else 45000},{center_latitude},{center_longitude});"
        for _, center_latitude, center_longitude in search_centers
        for selector in selectors
    )
    query = f"[out:json][timeout:35];({osm_parts});out tags center {max(limit * 6, 60)};"
    payload = None
    last_error: Exception | None = None
    request_body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    for endpoint in OVERPASS_API_ENDPOINTS:
        request = urllib.request.Request(
            endpoint,
            data=request_body,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "HuaweiEVLeadTool/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                candidate_payload = json.loads(response.read().decode("utf-8", errors="ignore"))
            if isinstance(candidate_payload.get("elements"), list):
                payload = candidate_payload
                break
        except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError) as exc:
            last_error = exc
    if payload is None:
        raise RuntimeError(f"OpenStreetMap Overpass 暂时不可用：{last_error or '未返回有效数据'}")
    items: list[dict] = []
    seen_names = set()
    for element in payload.get("elements", []):
        tags = element.get("tags", {})
        name = (tags.get("name:en") or tags.get("name") or "").strip()
        name = re.sub(r"[\u4e00-\u9fff]+", " ", name)
        name = re.sub(r"\s+", " ", name).strip()
        if not name or name.lower() in seen_names:
            continue
        seen_names.add(name.lower())
        website = normalize_public_url(tags.get("website") or tags.get("contact:website") or "")
        phone = tags.get("phone") or tags.get("contact:phone") or ""
        email = tags.get("email") or tags.get("contact:email") or ""
        contact = email or phone
        brand = tags.get("brand") or tags.get("operator") or ""
        element_center = element.get("center") or element
        element_latitude = float(element_center.get("lat") or latitude)
        element_longitude = float(element_center.get("lon") or longitude)
        result_city = min(
            search_centers,
            key=lambda center: (element_latitude - center[1]) ** 2 + (element_longitude - center[2]) ** 2,
        )[0]
        osm_url = f"https://www.openstreetmap.org/{element.get('type', 'node')}/{element.get('id')}"
        osm_business_label = (
            "car rental and fleet business"
            if tags.get("amenity") == "car_rental" or tags.get("shop") == "car_rental"
            else "car dealer or showroom (OpenStreetMap shop=car)"
        )
        snippet = f"{name} is listed as a {osm_business_label} in {result_city}, {country_search_meta(country)['location']}."
        if brand:
            snippet += f" Brand or operator: {brand}."
        if contact:
            snippet += f" Contact: {contact}."
        items.append(
            {
                "title": name,
                "url": website or osm_url,
                "source_url": osm_url,
                "customer_website": website,
                "snippet": snippet,
                "contact": contact,
                "origin": "OpenStreetMap",
                "source_type": "地图与地理商业目录",
                "tags": tags,
                "skip_fetch": not bool(website),
            }
        )
    items.sort(
        key=lambda item: (
            "openstreetmap.org" not in item["url"],
            bool(item["contact"]),
        ),
        reverse=True,
    )
    return items[:limit]


def extract_meta(page: str) -> str:
    parts = []
    title = re.search(r"<title[^>]*>([\s\S]*?)</title>", page, flags=re.I)
    if title:
        parts.append(clean_text(title.group(1)))
    for name in ("description", "og:description"):
        meta = re.search(
            rf'<meta[^>]+(?:name|property)=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
            page,
            flags=re.I,
        )
        if meta:
            parts.append(html.unescape(meta.group(1)))
    body = clean_text(page)[:900]
    parts.append(body)
    return " ".join(part for part in parts if part).strip()[:1100]


def extract_contact(text: str) -> str:
    email = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    if email:
        return email.group(0)
    whatsapp = re.search(r"(?:whatsapp|wa\.me|api\.whatsapp)[^\s<>'\"]{0,80}", text, flags=re.I)
    if whatsapp:
        return whatsapp.group(0)
    phone = re.search(r"\+?\d[\d\s().-]{8,}\d", text)
    return phone.group(0).strip() if phone else ""


def clean_phone_value(value: str) -> str:
    value = html.unescape(str(value or "")).strip()
    value = re.sub(r"^(?:tel|phone|call|mobile|whatsapp|wa)[:：\s]+", "", value, flags=re.I)
    value = value.strip(" \t\r\n.,;:)]}'\"")
    value = re.sub(r"\s+", " ", value)
    digits = re.sub(r"\D", "", value)
    if value.startswith("+971") and len(digits) > 12:
        return "+" + digits[:12]
    return value


def phone_value_matches_country(value: str, country: str) -> bool:
    target_codes = {"Qatar": "974", "UAE": "971", "Saudi": "966", "Kuwait": "965"}
    target_code = next((code for name, code in target_codes.items() if name.lower() in country.lower()), "")
    if not target_code:
        return True
    raw = html.unescape(str(value or "")).strip()
    international = re.search(r"(?:wa\.me/|api\.whatsapp\.com/send\?phone=|\+)(\d{3,15})", raw, re.I)
    if not international:
        return True
    return international.group(1).startswith(target_code)


def clean_whatsapp_value(value: str) -> str:
    raw = html.unescape(str(value or "")).strip()
    message_link = re.search(r"https?://wa\.me/message/[A-Za-z0-9_-]+", raw, re.I)
    if message_link:
        return message_link.group(0)
    phone_link = re.search(r"https?://wa\.me/\+?(\d{8,15})", raw, re.I)
    if phone_link:
        return f"https://wa.me/{phone_link.group(1)}"
    return clean_phone_value(raw)


def valid_phone_candidate(value: str, context: str = "") -> bool:
    value = clean_phone_value(value)
    digits = re.sub(r"\D", "", value)
    if not 8 <= len(digits) <= 15:
        return False
    if len(digits) == 10 and digits[0] in "01":
        return False
    if len(digits) == 11 and digits.startswith("1") and digits[1] in "01":
        return False
    if re.search(r"\b20\d{2}[./-]\d{1,2}[./-]\d{1,2}", value) or value.count(".") >= 2:
        return False
    if len(set(digits)) <= 2 and not value.strip().startswith("+"):
        return False
    lowered = context.lower()
    has_contact_label = bool(re.search(r"\b(whatsapp|phone|mobile|tel|call|contact|wa)\b|电话|联系", lowered))
    if not has_contact_label:
        has_contact_label = bool(re.search(r"\b(click|sales|service|parts|appointment|dealer|dealership)\b", lowered))
    if not has_contact_label:
        has_contact_label = bool(re.search(
            r"\b(contacts?)\b|\u0442\u0435\u043b\u0435\u0444\u043e\u043d|\u0442\u0435\u043b\.|\u043c\u043e\u0431\.|\u043a\u043e\u043d\u0442\u0430\u043a\u0442|\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u044b|\u0437\u0432\u043e\u043d",
            lowered,
            flags=re.I,
        ))
    if not value.strip().startswith("+") and not has_contact_label:
        return False
    return True


def add_phone_candidate(target: list[str], value: str, context: str = "") -> None:
    value = clean_phone_value(value)
    if not valid_phone_candidate(value, context):
        return
    digits = re.sub(r"\D", "", value)
    if not any(re.sub(r"\D", "", item) == digits for item in target):
        target.append(value)


PHONE_CANDIDATE_PATTERN = r"\+?\d(?:[\s().-]*\d){7,14}"
NANP_PHONE_PATTERN = r"(?<!\d)(?:\+?1[\s().-]*)?(?:[2-9]\d{2})[\s().-]*[2-9]\d{2}[\s().-]*\d{4}(?!\d)"


def extract_public_contacts(page: str, tags: dict | None = None) -> dict:
    tags = tags or {}
    text = clean_text(page)
    placeholder_domains = {"example.com", "example.org", "example.net", "mail.com"}
    mailto_emails = {
        value.strip().lower()
        for value in re.findall(r'mailto:([\w.+-]+@[\w.-]+\.[A-Za-z]{2,})', page, flags=re.I)
    }
    emails = []
    for value in re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", page):
        value = value.strip().lower()
        if re.search(r"\.(?:png|jpe?g|gif|svg|webp|css|js)$", value, re.I):
            continue
        if value.split("@")[-1] in placeholder_domains:
            continue
        if re.match(r"^(?:example|sample|test|yourname|name)@", value, re.I):
            continue
        if value not in mailto_emails and not re.search(re.escape(value), text, re.I):
            continue
        if value not in emails:
            emails.append(value)
    phones = []
    whatsapps = []
    for match in re.finditer(
        rf"(?:whatsapp|wa|phone|mobile|tel|call|contact|电话|联系)[:：\s\w/.-]{{0,40}}?({PHONE_CANDIDATE_PATTERN})",
        text,
        flags=re.I,
    ):
        context = text[max(0, match.start() - 80):match.end() + 80]
        value = match.group(1)
        if re.search(r"whatsapp|\bwa\b", context, re.I):
            add_phone_candidate(whatsapps, value, context)
        add_phone_candidate(phones, value, context)
    for match in re.finditer(
        rf"(?:whatsapp|wa|phone|mobile|tel|call|click|contact|sales|service|parts|appointment)[^\d+]{{0,70}}?({PHONE_CANDIDATE_PATTERN})",
        text,
        flags=re.I,
    ):
        context = text[max(0, match.start() - 100):match.end() + 100]
        value = match.group(1)
        if re.search(r"whatsapp|\bwa\b", context, re.I):
            add_phone_candidate(whatsapps, value, context)
        add_phone_candidate(phones, value, context)
    for match in re.finditer(
        rf"(?:\u0442\u0435\u043b\u0435\u0444\u043e\u043d|\u0442\u0435\u043b\.|\u043c\u043e\u0431\.|\u043a\u043e\u043d\u0442\u0430\u043a\u0442|\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u044b|\u0437\u0432\u043e\u043d)[:\s\w/.-]{{0,40}}?({PHONE_CANDIDATE_PATTERN})",
        text,
        flags=re.I,
    ):
        context = text[max(0, match.start() - 80):match.end() + 80]
        add_phone_candidate(phones, match.group(1), context)
    for match in re.finditer(PHONE_CANDIDATE_PATTERN, text):
        context = text[max(0, match.start() - 80):match.end() + 80]
        if not clean_phone_value(match.group(0)).startswith("+"):
            continue
        add_phone_candidate(phones, match.group(0), context)
    for match in re.finditer(NANP_PHONE_PATTERN, text):
        context = text[max(0, match.start() - 100):match.end() + 100]
        if re.search(r"\b(phone|tel|call|click|contact|sales|service|parts|appointment|dealer|dealership)\b", context, re.I):
            add_phone_candidate(phones, match.group(0), context)
    whatsapp_urls = list(
        dict.fromkeys(
            html.unescape(value).rstrip(".,;:)]}'\"")
            for value in re.findall(
                r'https?://(?:wa\.me|api\.whatsapp\.com|chat\.whatsapp\.com)/[^"\'\s<]+',
                page,
                flags=re.I,
            )
        )
    )
    social_accounts = []
    for value in re.findall(
        r'https?://(?:www\.)?(?:instagram\.com|facebook\.com|linkedin\.com|tiktok\.com|youtube\.com|youtu\.be|t\.me|telegram\.me|telegram\.dog|x\.com|twitter\.com|threads\.net|pinterest\.[a-z.]+|reddit\.com|vk\.com)/[^"\'\s<]+',
        page,
        flags=re.I,
    ):
        value = html.unescape(value).rstrip(".,;:)]}'\"")
        if is_social_profile_url(value) and value not in social_accounts:
            social_accounts.append(value)
    social_accounts = social_accounts[:8]
    websites = extract_business_websites(page)
    tag_email = tags.get("email") or tags.get("contact:email") or ""
    tag_phone = tags.get("phone") or tags.get("contact:phone") or ""
    tag_whatsapp = tags.get("contact:whatsapp") or tags.get("whatsapp") or ""
    if tag_email and tag_email not in emails:
        emails.insert(0, tag_email)
    if tag_phone:
        add_phone_candidate(phones, tag_phone, "phone")
    if tag_whatsapp:
        add_phone_candidate(whatsapps, tag_whatsapp, "whatsapp")
        if tag_whatsapp not in whatsapp_urls:
            whatsapp_urls.insert(0, tag_whatsapp)

    role_words = (
        "owner|founder|director|general manager|sales manager|purchasing manager|"
        "procurement manager|fleet manager|business development manager|export manager"
    )
    person_match = re.search(
        rf"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){{1,3}})\s*[-–,|]\s*({role_words})\b",
        text,
        flags=re.I,
    )
    contact_name = person_match.group(1).strip() if person_match else ""
    contact_role = person_match.group(2).strip().title() if person_match else ""
    return {
        "email": emails[0] if emails else "",
        "emails": emails[:20],
        "phone": phones[0] if phones else "",
        "phones": phones[:20],
        "whatsapp": (whatsapps[0] if whatsapps else whatsapp_urls[0] if whatsapp_urls else ""),
        "whatsapps": list(dict.fromkeys([*whatsapps, *whatsapp_urls]))[:20],
        "social_accounts": social_accounts,
        "websites": websites[:8],
        "contact_name": contact_name,
        "contact_role": contact_role,
    }


def merge_public_contacts(base: dict, incoming: dict) -> dict:
    merged = dict(base or {})
    for key in ("emails", "phones", "whatsapps", "social_accounts", "websites"):
        values = [*(merged.get(key) or []), *(incoming.get(key) or [])]
        merged[key] = list(dict.fromkeys(value for value in values if value))
    for key, list_key in (
        ("email", "emails"),
        ("phone", "phones"),
        ("whatsapp", "whatsapps"),
    ):
        merged[key] = merged.get(key) or incoming.get(key) or (merged.get(list_key) or [""])[0]
    for key in ("contact_name", "contact_role"):
        merged[key] = merged.get(key) or incoming.get(key) or ""
    return merged


def detect_competitor(text: str) -> bool:
    lower = text.lower()
    competitor_terms = (
        "china car exporter",
        "vehicle export from china",
        "wholesale chinese cars",
        "auto export company",
        "car export trading",
        "exporter of chinese vehicles",
    )
    return any(term in lower for term in competitor_terms)


def is_brand_bound_chinese_dealer(text: str) -> bool:
    """Exclude single-brand OEM 4S/authorized outlets from channel leads.

    They are useful market intelligence, but normally cannot introduce another
    flagship brand without approval from their existing principal distributor.
    Multi-brand importers remain eligible for human review.
    """
    lower = clean_text(text).lower()
    chinese_oem_terms = (
        "dongfeng", "dfsk", "changan", "geely", "byd", "chery", "jetour",
        "omoda", "jaecoo", "great wall", "gwm", "haval", "tank", "saic",
        "mg motor", "faw", "baic", "jac", "gac", "hongqi", "voyah",
        "zeekr", "nio", "xpeng", "li auto", "东风", "长安", "吉利", "比亚迪",
        "奇瑞", "长城", "红旗", "广汽", "北汽", "江淮",
    )
    chinese_oem_terms = chinese_oem_terms + (
        "bmw", "mini", "mercedes", "mercedes-benz", "benz", "audi",
        "volkswagen", "vw", "porsche", "land rover", "range rover", "jaguar",
        "lexus", "toyota", "nissan", "infiniti", "honda", "acura", "mazda",
        "mitsubishi", "subaru", "hyundai", "kia", "genesis", "renault",
        "peugeot", "citroen", "skoda", "seat", "volvo", "ford", "chevrolet",
        "cadillac", "jeep", "dodge", "chrysler", "fiat", "alfa romeo",
        "maserati", "ferrari", "lamborghini", "bentley", "rolls-royce",
        "\u043e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0439 \u0434\u0438\u043b\u0435\u0440 bmw", "\u0434\u0438\u043b\u0435\u0440 bmw", "bmw borishof", "bmw-",
    )
    binding_terms = (
        "4s", "4 s", "authorized dealer", "official dealer", "exclusive dealer",
        "authorized distributor", "official distributor", "brand showroom", "dealer of",
        "官方授权", "授权经销商", "品牌专营", "4s店",
    )
    binding_terms = binding_terms + (
        "franchise dealer", "franchised dealer", "main dealer",
        "brand or operator:", "listed as a dealer", "listed as a car dealer",
        "listed on google maps",
        "\u043e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0439 \u0434\u0438\u043b\u0435\u0440", "\u043e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0433\u043e \u0434\u0438\u043b\u0435\u0440\u0430", "\u0430\u0432\u0442\u043e\u0440\u0438\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u0434\u0438\u043b\u0435\u0440",
        "\u043e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0435\u0440\u0432\u0438\u0441", "\u0434\u0438\u043b\u0435\u0440\u0441\u043a\u0438\u0439 \u0446\u0435\u043d\u0442\u0440", "\u0434\u0446 ",
    )
    multi_brand_terms = (
        "multi-brand", "multiple brands", "brand portfolio", "independent importer",
        "parallel import", "import export", "auto trading", "automotive trading",
        "多品牌", "平行进口", "汽车贸易", "进出口",
    )
    multi_brand_terms = multi_brand_terms + (
        "multi brand", "used cars", "pre-owned", "all brands", "97 \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c", "97 brands",
        "\u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0439 \u0445\u043e\u043b\u0434\u0438\u043d\u0433", "\u043c\u0443\u043b\u044c\u0442\u0438\u0431\u0440\u0435\u043d\u0434", "\u043c\u0443\u043b\u044c\u0442\u0438\u0431\u0440\u0435\u043d\u0434\u043e\u0432\u044b\u0439",
        "\u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u0438 \u0441 \u043f\u0440\u043e\u0431\u0435\u0433\u043e\u043c", "\u043f\u043e\u0434\u0431\u043e\u0440 \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u0435\u0439", "\u0432\u044b\u043a\u0443\u043f \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u0435\u0439",
    )
    return (
        any(term in lower for term in chinese_oem_terms)
        and any(term in lower for term in binding_terms)
        and not any(term in lower for term in multi_brand_terms)
    )


def recommend_models(text: str, requested_model: str) -> list[str]:
    lower = text.lower()
    models = [requested_model]
    if any(word in lower for word in ("luxury", "premium", "executive", "vip", "flagship")):
        models.extend(["问界 M9", "尊界 S800", "享界 S9"])
    if any(word in lower for word in ("suv", "family", "4x4", "fleet")):
        models.extend(["问界 M9", "问界 M8", "智界 R7"])
    if any(word in lower for word in ("sedan", "limousine", "chauffeur", "business")):
        models.extend(["尊界 S800", "享界 S9"])
    return list(dict.fromkeys(models))[:4]


def confidence_score(
    customer_website: str,
    source_url: str,
    contacts: dict,
    published_at: str,
    text: str,
) -> tuple[int, str]:
    score = 15
    if customer_website:
        score += 20
    if source_url:
        score += 10
    if contacts["email"]:
        score += 12
    if contacts["phone"]:
        score += 10
    if contacts["whatsapp"]:
        score += 8
    if contacts["social_accounts"]:
        score += 5
    if published_at:
        score += 5
    if re.search(r"\b(dealer|showroom|importer|fleet|procurement|rental|tender)\b", text, re.I):
        score += 10
    score = min(score, 74)
    label = "高" if score >= 75 else "中" if score >= 55 else "低"
    return score, label


def chinese_source_summary(
    company: str,
    target_label: str,
    city: str,
    source_type: str,
    contacts: dict,
    published_at: str,
) -> str:
    parts = [f"这条公开信息显示，{company}可能属于“{target_label}”相关客户"]
    if city:
        parts.append(f"，所在市场为{city}")
    parts.append(f"，信息来自{source_type}")
    if published_at:
        parts.append(f"，发布日期为{published_at}")
    contact_items = []
    if contacts["email"]:
        contact_items.append(f"邮箱 {contacts['email']}")
    if contacts["phone"]:
        contact_items.append(f"电话 {contacts['phone']}")
    if contacts["whatsapp"]:
        contact_items.append(f"WhatsApp {contacts['whatsapp']}")
    if contact_items:
        parts.append("，公开联系方式包括" + "、".join(contact_items))
    else:
        parts.append("，暂未发现明确公开联系方式")
    return "".join(parts) + "。"


def infer_type(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ("dealership owner", "import manager", "fleet manager", "sales director", "founder")):
        return "Industry decision maker"
    if any(word in lower for word in ("government", "public procurement", "tender", "ministry")):
        return "Government procurement"
    if any(word in lower for word in ("corporate procurement", "company fleet", "business fleet")):
        return "Corporate buyer"
    if any(word in lower for word in ("buying request", "rfq", "wanted", "looking to buy")):
        return "Active buyer"
    if re.search(r"\b(car dealer|auto dealer|vehicle dealer|dealership|concessionnaire|agent agr[ée]e?)\b", lower):
        return "Car dealer"
    if any(word in lower for word in ("showroom", "luxury cars", "pre-owned", "supercars")):
        return "Luxury car showroom"
    if any(word in lower for word in ("import", "export", "trading", "parallel")):
        return "Auto importer"
    if any(word in lower for word in ("electric vehicle", "ev dealer", "new energy", "hybrid")):
        return "EV dealer"
    if any(word in lower for word in ("fleet", "chauffeur", "rental")):
        return "Fleet buyer"
    return "Auto business"


def score_lead(text: str, contact: str) -> int:
    score, _, _, _ = lead_opportunity_score(
        text,
        bool(re.search(r"https?://|www\.", text, re.I)),
        bool(contact),
    )
    return score


def lead_opportunity_score(
    text: str,
    has_official_website: bool,
    has_contact: bool,
    google_reviews: int = 0,
    requested_model: str = "",
    lead_type: str = "",
    is_competitor: bool = False,
    target_country_match: bool = False,
    has_email: bool = False,
    has_phone: bool = False,
    has_whatsapp: bool = False,
    has_decision_maker: bool = False,
    allow_competitor_auto: bool = True,
) -> tuple[int, list[dict], dict, str]:
    lower = clean_text(f"{text} {lead_type}").lower()
    dimensions = {
        "automotiveFit": 0,
        "countryFit": 0,
        "chineseNev": 0,
        "huaweiFit": 0,
        "contactCompleteness": 0,
        "websiteTrust": 0,
        "tradeQualification": 0,
        "businessCapacity": 0,
        "decisionMaker": 0,
        "purchaseIntent": 0,
        "penalty": 0,
    }
    breakdown: list[dict] = []

    def set_dimension(key: str, label: str, points: int):
        if points <= dimensions[key]:
            return
        dimensions[key] = points
        breakdown[:] = [item for item in breakdown if item.get("category") != key]
        breakdown.append({"category": key, "label": label, "points": points})

    automotive_specific_terms = (
        "vehicle importer", "car importer", "automotive importer", "parallel import",
        "car distributor", "vehicle distributor", "authorized dealer", "dealership",
        "car dealer", "auto dealer", "car showroom", "vehicle showroom", "auto trading",
        "automotive trading", "vehicle sales", "fleet sales", "汽车进口", "汽车经销",
        "汽车展厅", "汽车贸易", "汽车销售", "车队采购",
    )
    automotive_general_terms = (
        "automotive", "vehicles", "cars", "motors", "new cars", "used cars",
        "汽车", "车辆", "新车", "二手车",
    )
    if any(term in lower for term in automotive_specific_terms):
        set_dimension("automotiveFit", "明确从事汽车经销、进口、分销或车队业务", 20)
    elif any(term in lower for term in automotive_general_terms):
        set_dimension("automotiveFit", "发现汽车行业相关业务", 12)

    if target_country_match:
        set_dimension("countryFit", "公开证据与目标国家或城市匹配", 20)

    chinese_nev_terms = (
        "chinese ev", "china ev", "chinese electric vehicle", "chinese new energy vehicle",
        "byd", "geely", "zeekr", "chery", "jetour", "gac aion", "nio", "xpeng",
        "li auto", "leapmotor", "hongqi", "changan", "deepal", "voyah", "avatr",
        "denza", "中国新能源", "中国电动车", "中国电动汽车", "中国新能源汽车",
        "比亚迪", "吉利", "极氪", "奇瑞", "捷途", "广汽埃安", "蔚来", "小鹏",
        "理想", "零跑", "红旗", "长安", "深蓝", "岚图", "阿维塔", "腾势",
    )
    if any(term in lower for term in chinese_nev_terms):
        set_dimension("chineseNev", "经营或关注中国新能源汽车品牌", 10)

    huawei_terms = (
        "huawei", "harmonyos", "harmony intelligent mobility", "hima", "aito", "luxeed",
        "stelato", "maextro", "问界", "智界", "享界", "尊界", "鸿蒙智行", "华为汽车",
    )
    if any(term in lower for term in huawei_terms):
        set_dimension("huaweiFit", "包含华为、鸿蒙智行或华为系车型信号", 10)
        set_dimension("chineseNev", "华为系车型属于中国新能源/智能电动车线索", 10)

    contact_count = sum((bool(has_email), bool(has_phone), bool(has_whatsapp)))
    if contact_count == 3:
        set_dimension("contactCompleteness", "邮箱、电话和 WhatsApp 齐全", 15)
    elif contact_count == 2:
        set_dimension("contactCompleteness", "三类核心联系方式中已核验两类", 10)
    elif contact_count == 1 or has_contact:
        set_dimension("contactCompleteness", "已核验至少一种公开商业联系方式", 5)

    if has_official_website:
        set_dimension("websiteTrust", "存在可核验的企业官网或结构化商业主页", 10)

    qualification_terms = (
        "import license", "import licence", "export license", "export licence",
        "import export license", "import-export license", "licensed importer",
        "licensed exporter", "customs registration", "customs registered",
        "customs code", "trade license", "trading license",
        "commercial registration", "authorized importer", "import permit",
        "export permit", "进出口资质", "进出口许可证", "进口许可证",
        "出口许可证", "海关注册", "海关备案", "报关资质",
        "贸易许可证", "商业登记", "授权进口商",
    )
    if any(term in lower for term in qualification_terms):
        set_dimension("tradeQualification", "明确具备进出口、海关或贸易许可资质", 8)
    elif any(term in lower for term in (
        "vehicle importer", "car importer", "automotive importer",
        "parallel import", "import and export",
    )):
        set_dimension("tradeQualification", "公开业务显示具备车辆进口经验，资质待核验", 5)

    if any(term in lower for term in ("luxury", "premium", "supercar", "range rover", "mercedes", "bmw", "porsche", "bentley")):
        set_dimension("businessCapacity", "经营豪华或高端汽车", 2)
    if any(term in lower for term in ("our brands", "brands we represent", "multi-brand", "wide range of brands", "brand portfolio")):
        set_dimension("businessCapacity", "具备多品牌经营能力", 3)
    if any(term in lower for term in ("branches", "locations", "group of companies", "nationwide", "regional network")):
        set_dimension("businessCapacity", "具备多网点或区域经营能力", 4)
    if google_reviews >= 100:
        set_dimension("businessCapacity", "地图评价量显示经营规模较稳定", 4)
    elif google_reviews >= 20:
        set_dimension("businessCapacity", "地图经营评价较充分", 3)
    elif any(term in lower for term in ("wholesale", "fleet", "corporate sales", "bulk sales")):
        set_dimension("businessCapacity", "具备批发、车队或企业销售能力", 4)

    if has_decision_maker or re.search(
        r"\b(owner|founder|director|general manager|procurement manager|purchasing manager)\b",
        lower,
    ):
        set_dimension("decisionMaker", "发现公开决策人或采购岗位", 3)

    if re.search(r"\b(repair|workshop|spare parts|car wash|detailing|tyres?)\b", lower) and not re.search(
        r"\b(importer|distributor|dealer|dealership|showroom|vehicle sales)\b", lower
    ):
        dimensions["penalty"] -= 45
        breakdown.append({"category": "penalty", "label": "仅维修、配件或美容业务", "points": -45})
    if re.search(r"\b(classifieds?|marketplace|individual seller|private seller)\b", lower):
        dimensions["penalty"] -= 55
        breakdown.append({"category": "penalty", "label": "交易平台或个人卖家特征", "points": -55})
    if is_competitor or (allow_competitor_auto and detect_competitor(lower)):
        dimensions["penalty"] -= 70
        breakdown.append({"category": "penalty", "label": "中国汽车出口同行特征", "points": -70})

    configured_weights = admin_control_settings().get("quality", {}).get("scoreWeights") or {}
    weight_mapping = {
        "automotiveFit": ("automotive", 20),
        "countryFit": ("country", 20),
        "chineseNev": ("chineseNev", 10),
        "huaweiFit": ("huawei", 10),
        "contactCompleteness": ("contact", 15),
        "websiteTrust": ("officialWebsite", 10),
        "tradeQualification": ("importDistribution", 8),
        "businessCapacity": ("businessActivity", 4),
        "decisionMaker": ("decisionMaker", 3),
    }
    for dimension, (setting_key, default_max) in weight_mapping.items():
        current = dimensions.get(dimension, 0)
        configured_max = int(configured_weights.get(setting_key, default_max))
        adjusted = round((current / default_max) * configured_max) if current and default_max else 0
        if adjusted == current:
            continue
        dimensions[dimension] = adjusted
        for item in breakdown:
            if item.get("category") == dimension:
                item["points"] = adjusted

    score = sum(dimensions.values())
    score = max(0, min(score, 100))
    if not dimensions["automotiveFit"] or not dimensions["countryFit"]:
        score = min(score, 49)
    tier = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D"
    return score, breakdown, dimensions, tier


def website_business_score(
    text: str,
    has_official_website: bool,
    has_contact: bool,
    google_reviews: int = 0,
) -> tuple[int, list[dict]]:
    score, breakdown, _, _ = lead_opportunity_score(
        text,
        has_official_website,
        has_contact,
        google_reviews,
    )
    return score, breakdown


def opportunity_signals(text: str) -> tuple[list[str], list[str]]:
    lower = text.lower()
    business_labels = {
        "importer": "汽车进口业务",
        "vehicle import": "车辆进口业务",
        "parallel import": "平行进口业务",
        "distributor": "品牌分销业务",
        "dealership": "汽车经销业务",
        "dealer": "汽车经销业务",
        "showroom": "实体展厅",
        "fleet": "车队业务",
        "procurement": "车辆采购业务",
        "trading": "汽车贸易业务",
    }
    intent_labels = {
        "looking for distributor": "正在寻找分销商",
        "seeking distributor": "正在寻找分销商",
        "dealer wanted": "正在招募经销商",
        "distributor wanted": "正在招募分销商",
        "new brand": "有引入新品牌信号",
        "brand partnership": "寻求品牌合作",
        "distribution opportunity": "存在分销合作机会",
        "dealership opportunity": "存在经销合作机会",
        "import partnership": "寻求进口合作",
        "request for quotation": "公开询价",
        "rfq": "公开询价",
        "vehicle procurement": "正在采购车辆",
        "fleet purchase": "车队采购意向",
        "bulk order": "批量采购意向",
        "looking to buy": "公开求购",
        "sourcing vehicles": "正在寻找车辆供应商",
        "supplier wanted": "正在寻找供应商",
    }
    business = list(dict.fromkeys(
        label for term, label in business_labels.items() if term in lower
    ))
    intent = list(dict.fromkeys(
        label for term, label in intent_labels.items() if term in lower
    ))
    return business[:4], intent[:4]


def has_strong_automotive_business_evidence(text: str) -> bool:
    value = clean_text(text).lower()
    return bool(re.search(
        r"\b(car dealer|dealership|auto dealer|vehicle dealer|car showroom|motors showroom|"
        r"auto trading|automotive trading|vehicle importer|car importer|automotive importer|"
        r"parallel import|vehicle distributor|car distributor|authorized dealer|exclusive dealer|"
        r"cars for sale|used cars|new cars|pre-owned cars|inventory|stock vehicles|"
        r"sales department|showroom address|book a test drive)\b",
        value,
        re.I,
    ))


def infer_city(country: str, text: str) -> str:
    lower = text.lower()
    for key, cities in COUNTRY_HINTS.items():
        if key.lower() in country.lower():
            for city in cities:
                if city.lower() in lower:
                    return city
            return cities[0]
    return ""


def infer_target_type(goal: str) -> str:
    lower = goal.lower()
    if any(word in lower for word in ("租赁", "车队", "rental", "fleet", "chauffeur")):
        return "fleet"
    if any(word in lower for word in ("政府", "项目", "招标", "government", "tender")):
        return "government"
    if any(word in lower for word in ("企业采购", "公司采购", "corporate", "procurement")):
        return "corporate"
    if any(word in lower for word in ("求购", "正在购买", "rfq", "wanted", "looking to buy")):
        return "buying"
    if any(word in lower for word in ("平行进口", "parallel import", "grey market")):
        return "parallel"
    if any(word in lower for word in ("进口商", "importer", "distributor")):
        return "importer"
    return "dealer"


def social_accounts_from_business_websites(
    country: str,
    target_type: str,
    allowed_platforms: set[str],
    seed_limit: int = 20,
) -> list[dict]:
    try:
        seeds = [
            item
            for item in search_osm_dealers(country, limit=seed_limit, target_type=target_type)
            if item.get("customer_website") or (
                item.get("url") and "openstreetmap.org" not in item.get("url", "")
            )
        ]
    except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
        return []

    def inspect(seed: dict) -> list[dict]:
        website = normalize_public_url(seed.get("customer_website") or seed.get("url") or "")
        if not website:
            return []
        try:
            page, final_url = fetch_document(website, timeout=12)
        except (OSError, TimeoutError, UnicodeError, urllib.error.URLError, http.client.HTTPException):
            return []
        meta = extract_meta(page)
        contacts = extract_public_contacts(page, seed.get("tags"))
        company = clean_text(seed.get("title") or safe_urlparse(final_url).netloc)[:180]
        results = []
        for social_url in contacts.get("social_accounts") or []:
            platform_name = social_platform(social_url)
            platform_key = {
                "X / Twitter": "twitter",
            }.get(platform_name, platform_name.lower())
            if platform_key not in allowed_platforms or not is_social_profile_url(social_url):
                continue
            results.append(
                {
                    "title": f"{company} · {platform_name}",
                    "url": social_url,
                    "snippet": meta[:700] or f"{company} 官网公开链接的 {platform_name} 账号",
                    "origin": platform_name,
                    "source_type": "企业官网直接链接的社媒账号",
                    "source_url": social_url,
                    "customer_website": final_url,
                    "account_type": "公司账号",
                    "official_relationship": "公司官网直接链接",
                    "skip_fetch": True,
                }
            )
        return results

    discovered: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(6, max(1, len(seeds)))) as executor:
        futures = [executor.submit(inspect, seed) for seed in seeds]
        for future in as_completed(futures):
            try:
                discovered.extend(future.result())
            except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                continue
    unique: list[dict] = []
    seen: set[str] = set()
    for item in discovered:
        identity = normalize_public_url(item.get("url", "")).lower().rstrip("/")
        if not identity or identity in seen:
            continue
        seen.add(identity)
        unique.append(item)
    return unique


def social_accounts_from_local_source_pages(
    country: str,
    target_type: str,
    platform: str,
    origin: str,
    source_type: str,
    limit: int = 12,
) -> list[dict]:
    cities = discovery_cities(country)
    local_queries = local_source_query_variants(country, cities, target_type)
    if not local_queries:
        return []
    expected_domains = {
        "instagram": ("instagram.com",),
        "facebook": ("facebook.com", "fb.com"),
        "tiktok": ("tiktok.com",),
        "linkedin": ("linkedin.com",),
        "youtube": ("youtube.com", "youtu.be"),
        "telegram": ("t.me", "telegram.me", "telegram.dog"),
        "twitter": ("x.com", "twitter.com"),
        "threads": ("threads.net",),
        "pinterest": ("pinterest.",),
        "reddit": ("reddit.com",),
        "vk": ("vk.com",),
    }.get(platform, ())
    if not expected_domains:
        return []
    seeds: list[dict] = []
    for query in local_queries[:4]:
        try:
            seeds.extend(search_web(query, limit=4, country=country))
        except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
            continue
    results: list[dict] = []
    seen: set[str] = set()
    for seed in seeds[:14]:
        seed_url = normalize_public_url(seed.get("url", ""))
        if not seed_url or not is_valid_http_url(seed_url):
            continue
        seed_domain = safe_urlparse(seed_url).netloc.lower().removeprefix("www.")
        if any(expected in seed_domain for expected in expected_domains):
            social_urls = [normalize_social_profile_url(seed_url)]
            page_text = seed.get("snippet", "")
            final_url = seed_url
        else:
            try:
                page_text, final_url = fetch_document(seed_url, timeout=8)
            except (OSError, TimeoutError, UnicodeError, urllib.error.URLError, http.client.HTTPException):
                continue
            contacts = extract_public_contacts(page_text)
            social_urls = contacts.get("social_accounts") or []
        for social_url in social_urls:
            item_url = normalize_social_profile_url(social_url)
            item_domain = safe_urlparse(item_url).netloc.lower().removeprefix("www.")
            identity = item_url.lower().rstrip("/")
            if (
                not item_url
                or identity in seen
                or not any(expected in item_domain for expected in expected_domains)
                or not is_social_profile_url(item_url)
            ):
                continue
            seen.add(identity)
            company = clean_text(seed.get("title") or safe_urlparse(final_url).netloc)[:180]
            results.append({
                "title": f"{company} - {origin}",
                "url": item_url,
                "snippet": clean_text(seed.get("snippet") or page_text)[:700],
                "origin": origin,
                "source_type": f"{source_type}（本地目录/官网反查）",
                "source_url": item_url,
                "customer_website": final_url if final_url != item_url else "",
                "account_type": "公司账号",
                "official_relationship": "本地目录或官网页面公开链接",
                "skip_fetch": True,
            })
            if len(results) >= limit:
                return results
    return results


def discover(params: dict[str, list[str]]) -> dict:
    country = (params.get("country") or ["UAE"])[0]
    model = (params.get("model") or ["问界 M9"])[0]
    goal = (params.get("goal") or [""])[0]
    target_type = infer_target_type(goal)
    target_profile = TARGET_PROFILES.get(target_type, TARGET_PROFILES["dealer"])
    target_label = target_profile["label"]
    quality_policy = admin_control_settings().get("quality", {})
    source_mode = (params.get("sourceMode") or ["combined"])[0]
    disabled_social_source_modes = {"telegram", "twitter", "threads", "pinterest", "reddit", "vk"}
    if source_mode in disabled_social_source_modes:
        source_mode = "social"
    enabled_sources = enabled_discovery_sources(country)
    single_source_modes = {"google", "osm", "dealer", "instagram", "facebook", "tiktok", "youtube", "linkedin"}
    if source_mode in single_source_modes and source_mode not in enabled_sources:
        raise ValueError(f"系统设置已停用当前来源：{source_mode}")
    account_scope = (params.get("accountScope") or ["both"])[0]
    domestic_region = (params.get("domesticRegion") or [""])[0].strip()
    city_focus = (params.get("cityFocus") or [""])[0].strip()
    customer_types = (params.get("customerTypes") or [""])[0].strip()
    exclusions = (params.get("exclusions") or [""])[0].strip()
    result_limit_value = (params.get("resultLimit") or ["90"])[0]
    result_limit = max(10, min(90, int(result_limit_value) if result_limit_value.isdigit() else 90))
    if source_mode in single_source_modes:
        result_limit = min(result_limit, discovery_source_cap(source_mode))
    verification_level = (params.get("verificationLevel") or ["strict"])[0]
    min_sources_value = (params.get("minSources") or ["2"])[0]
    min_sources = max(1, min(3, int(min_sources_value) if min_sources_value.isdigit() else 2))
    freshness_value = (params.get("freshness") or ["all"])[0]
    freshness_days = int(freshness_value) if freshness_value.isdigit() else None
    keywords = (params.get("keywords") or [""])[0].replace("|", " ")
    cutoff_query = ""
    exclude_query = " ".join(
        f'-"{part.strip()}"'
        for part in re.split(r"[,，、;；]+", exclusions)
        if part.strip()
    )
    query = (
        f"{city_focus} {keywords} {customer_types} {target_profile['query']} "
        f"official website contact contacts about profile email phone WhatsApp {exclude_query}{cutoff_query}"
    ).strip()
    cities = discovery_cities(country, city_focus, domestic_region)
    country_meta = country_search_meta(country)
    market = city_focus or (
        domestic_region
        if country_meta.get("code") == "cn" and domestic_region
        else country_meta.get("location") or country.split(" ")[0]
    )
    broad_business_query = (
        f"{market} automotive importer vehicle distributor car dealer showroom "
        f"parallel import auto trading official website contact contacts about email phone {exclude_query}{cutoff_query}"
    ).strip()
    if target_type in {"fleet", "buying", "government"}:
        intent_query = (
            f"{market} vehicle procurement fleet buyer tender RFQ corporate vehicles official website "
            f"{exclude_query}{cutoff_query}"
        ).strip()
    else:
        intent_query = (
            f"{market} car dealer importer \"new brand\" OR \"brand partnership\" OR "
            f"\"authorized dealer\" OR \"dealer wanted\" {exclude_query}{cutoff_query}"
        ).strip()
    china_ev_query = (
        f"{market} Chinese car importer electric vehicle distributor dealership "
        f"official website contact contacts about email phone {exclude_query}{cutoff_query}"
    ).strip()
    if country_meta.get("code") == "cn":
        broad_business_query = (
            f"{market} 汽车经销商 新能源 汽车贸易公司 官网 联系方式 电话 邮箱 {exclude_query}{cutoff_query}"
        ).strip()
        intent_query = (
            f"{market} 华为系 问界 尊界 鸿蒙智行 新能源汽车 经销商 采购 外贸 联系人 {exclude_query}{cutoff_query}"
        ).strip()
        china_ev_query = (
            f"{market} 中国新能源 汽车贸易公司 出口 企业车队 高端展厅 联系方式 {exclude_query}{cutoff_query}"
        ).strip()
    commercial_query_variants = [
        broad_business_query,
        intent_query,
        china_ev_query,
        query,
        f"{market} \"auto trading\" OR \"automobile trading\" car showroom import export official website contact contacts {exclude_query}{cutoff_query}",
        f"{market} luxury car importer exporter \"new cars\" \"vehicle sourcing\" official website contact about email phone {exclude_query}{cutoff_query}",
        f"{market} \"authorized dealer\" OR \"exclusive distributor\" OR \"dealer network\" automotive official website {exclude_query}{cutoff_query}",
    ]
    if target_type in {"fleet", "buying", "government"}:
        commercial_query_variants.append(
            f"{market} fleet procurement corporate vehicles rental limousine automotive dealer official website {exclude_query}{cutoff_query}"
        )
    if target_type in {"importer", "distributor"}:
        commercial_query_variants.append(
            f"{market} \"import export\" vehicles \"trading LLC\" OR \"trading FZE\" distributor official website {exclude_query}{cutoff_query}"
        )
    if city_focus:
        commercial_query_variants.append(
            f"{city_focus} car dealer showroom importer WhatsApp email phone contacts official website {exclude_query}{cutoff_query}"
        )
    for city in cities[:14]:
        commercial_query_variants.extend([
            f"{city} car dealers directory showroom motors contact contacts about website {exclude_query}{cutoff_query}",
            f"{city} auto trading LLC motors showroom WhatsApp email {exclude_query}{cutoff_query}",
            f"{city} used cars showroom dealer official website phone {exclude_query}{cutoff_query}",
            f"{city} imported cars luxury motors dealership contact {exclude_query}{cutoff_query}",
        ])
    commercial_query_variants.extend(
        city_keyword_queries(cities, DISCOVERY_KEYWORD_TERMS, f"official website contact {exclude_query}{cutoff_query}")
    )
    commercial_query_variants.extend(localized_vehicle_listing_queries(country, cities))
    local_queries: list[str] = []
    if source_mode in ("all", "combined"):
        local_queries = local_source_query_variants(country, cities, target_type, exclude_query, cutoff_query)
    ai_search_queries = ai_generate_search_queries(
        country=country,
        cities=cities,
        target_type=target_type,
        model=model,
        goal=goal,
        limit=18,
    )
    if source_mode in ("all", "combined") and local_queries:
        local_budget = 40
        commercial_query_variants = list(dict.fromkeys([
            *local_queries[:local_budget],
            *ai_search_queries[:6],
            *commercial_query_variants,
        ]))
    elif ai_search_queries:
        commercial_query_variants = [*ai_search_queries, *commercial_query_variants]

    raw_results = []
    google_primary_results: list[dict] = []
    google_places_error = ""
    notice = ""
    is_china_discovery = country_meta.get("code") == "cn"
    social_source_modes = {"social", "instagram", "facebook", "tiktok", "linkedin", "youtube"}
    use_geo_sources = not is_china_discovery or source_mode in ("google", "osm")
    # A single-platform task must return accounts from that platform only. Business
    # websites may still be used below to discover linked social profiles, but map
    # and generic web records must not become leads for an Instagram/Facebook/etc.
    # task. Cross-source enrichment belongs to social/all-source searches.
    include_support_sources = source_mode == "social" and not is_china_discovery
    if "google" in enabled_sources and ((use_geo_sources and source_mode in ("all", "combined", "google")) or include_support_sources):
        try:
            active_cities = (cities[:3] or [market]) if include_support_sources else (cities[:6] or [market])
            google_city_limit = 3 if include_support_sources else min(10, max(4, result_limit // max(1, len(cities))))
            google_place_queries = (
                "car dealer used cars showroom",
                "automotive importer vehicle distributor auto trading",
            )
            google_query_limit = max(3, (google_city_limit + len(google_place_queries) - 1) // len(google_place_queries))
            for city in active_cities:
                for place_query in google_place_queries:
                    if google_places_error:
                        break
                    try:
                        google_primary_results += search_google_places(
                            country,
                            place_query,
                            limit=google_query_limit,
                            city=city,
                        )
                    except urllib.error.HTTPError as exc:
                        google_places_error = (
                            "Google Places API 返回 403，无权调用；请检查 Places API (New)、账单和 API Key 限制。"
                            if exc.code == 403
                            else f"Google Places API 返回 HTTP {exc.code}。"
                        )
                    except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                        pass
                try:
                    google_primary_results += search_serpapi_google_maps(
                        country,
                        "car dealer used cars showroom automotive importer",
                        limit=max(3, min(google_city_limit, 8)),
                        city=city,
                    )
                except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
                    pass
            enrich_limit = min(len(google_primary_results), max(4, min(result_limit, 8)))
            enriched_google_results: list[dict] = []
            if enrich_limit:
                executor = ThreadPoolExecutor(max_workers=min(4, enrich_limit))
                include_reverse_social = source_mode in ("all", "social")
                futures = [
                    executor.submit(enrich_google_place_result, item, country, include_reverse_social)
                    for item in google_primary_results[:enrich_limit]
                ]
                try:
                    for future in as_completed(futures, timeout=max(25, DISCOVERY_SEARCH_TIMEOUT * 3)):
                        try:
                            enriched_google_results.append(future.result(timeout=1))
                        except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                            continue
                except FuturesTimeoutError:
                    pass
                finally:
                    executor.shutdown(wait=False, cancel_futures=True)
            google_primary_results = [
                *enriched_google_results,
                *google_primary_results[enrich_limit:],
            ]
            raw_results += google_primary_results
        except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
            if source_mode == "google":
                notice = f"{exc}。请在本机配置密钥后重试。"
        if google_places_error:
            notice = f"{notice} {google_places_error} 本轮已停止重复请求，并继续使用 OSM 与官网来源。".strip()
    if "osm" in enabled_sources and ((use_geo_sources and source_mode in ("all", "combined", "osm")) or include_support_sources):
        try:
            raw_results += search_osm_dealers(
                country,
                limit=min(result_limit, 8 if include_support_sources else 20 if source_mode in ("all", "combined") else 30),
                target_type=target_type,
            )
        except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
            notice = f"{notice} {exc}。本轮继续使用 Google Maps 与官网来源。".strip()
    if "dealer" in enabled_sources and is_china_discovery and source_mode in ("all", "combined", "dealer"):
        raw_results += search_autohome_dealers(cities, limit=min(24, max(8, result_limit // 2)))
    if (
        "dealer" in enabled_sources
        and country_meta.get("code") == "dz"
        and source_mode in ("all", "combined")
    ):
        try:
            raw_results += search_algeria_automotive_directories(limit=min(90, max(60, result_limit)))
        except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
            pass
    if (
        "dealer" in enabled_sources
        and country_meta.get("code") in REGIONAL_AUTOMOTIVE_DIRECTORY_PAGES
        and source_mode in ("all", "combined")
    ):
        try:
            raw_results += search_regional_automotive_directories(
                country,
                limit=min(90, max(60, result_limit)),
            )
        except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
            pass
    if "dealer" in enabled_sources and (source_mode in ("all", "combined", "dealer") or include_support_sources):
        search_variants = list(dict.fromkeys(commercial_query_variants))
        if is_china_discovery and source_mode in ("all", "combined"):
            max_web_queries = 16
        elif include_support_sources:
            max_web_queries = 4
        else:
            max_web_queries = 40 if source_mode in ("all", "combined") and local_queries else 24 if source_mode in ("all", "combined") else 16
        search_variants = search_variants[:max_web_queries]
        per_query_limit = 5 if is_china_discovery and source_mode in ("all", "combined") else 4 if include_support_sources else 8 if source_mode in ("all", "combined") else 6
        web_results_by_query: list[list[dict]] = []
        if search_variants:
            worker_limit = 6 if source_mode in ("all", "combined") and local_queries else 4
            executor = ThreadPoolExecutor(max_workers=min(worker_limit, len(search_variants)))
            futures = [
                executor.submit(search_web, search_query, per_query_limit, None, country)
                for search_query in search_variants
            ]
            try:
                web_timeout = max(30, DISCOVERY_SEARCH_TIMEOUT * 3) if source_mode in ("all", "combined") and local_queries else max(20, DISCOVERY_SEARCH_TIMEOUT * 2)
                for future in as_completed(futures, timeout=web_timeout):
                    try:
                        web_results_by_query.append(future.result(timeout=1))
                    except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                        continue
            except FuturesTimeoutError:
                pass
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
        for web_results in web_results_by_query:
            try:
                for item in web_results:
                    origin, source_type = source_details(item["url"])
                    if source_mode in ("combined", "dealer") and origin in {
                        "YouTube", "Facebook", "Instagram", "TikTok", "LinkedIn",
                        "Telegram", "X / Twitter", "Threads", "Pinterest", "Reddit", "VK",
                    }:
                        continue
                    item["origin"] = origin
                    item["source_type"] = source_type
                    item["source_url"] = item["url"]
                    if is_vehicle_listing_url(item["url"]):
                        item["source_type"] = "车源详情页（自动归并到车商站点）"
                        item["customer_website"] = site_root_url(item["url"])
                    else:
                        item["customer_website"] = item["url"]
                raw_results += web_results
            except (OSError, ValueError, TimeoutError, KeyError):
                pass
    if source_mode == "dealer":
        try:
            google_dealer_limit = min(18, max(8, result_limit // 2))
            active_cities = cities[:6] or [""]
            per_city_google_limit = max(3, google_dealer_limit // max(1, len(active_cities)))
            dealer_google_results: list[dict] = []
            for city in active_cities:
                dealer_google_results += search_google_places(
                    country,
                    "car dealer automotive showroom used cars motors official website phone",
                    limit=per_city_google_limit,
                    city=city,
                )
            for item in dealer_google_results[: min(len(dealer_google_results), 8)]:
                try:
                    raw_results.append(enrich_google_place_result(item, country))
                except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                    raw_results.append(item)
            raw_results += dealer_google_results[8:]
        except (OSError, ValueError, RuntimeError, TimeoutError):
            pass
        try:
            directory_websites = [
                item
                for item in search_osm_dealers(country, limit=16, target_type=target_type)
                if "openstreetmap.org" not in item["url"]
            ]
            for item in directory_websites:
                item["origin"] = "OpenStreetMap 车商目录"
                item["source_type"] = "地图车商目录（已登记官网）"
            raw_results += directory_websites
        except (OSError, ValueError, RuntimeError, TimeoutError):
            pass
    platform_queries = {
        "instagram": ("instagram.com", "Instagram", "社交媒体公开主页"),
        "facebook": ("facebook.com", "Facebook", "社交媒体公开主页"),
        "tiktok": ("tiktok.com", "TikTok", "短视频公开账号"),
        "linkedin": ("linkedin.com", "LinkedIn", "企业与职业社交平台"),
    }
    platform_queries.update({
        "instagram": ("instagram.com", "Instagram", "Instagram 公开主页或内容"),
        "facebook": ("facebook.com", "Facebook", "Facebook 公开主页、群组或内容"),
        "tiktok": ("tiktok.com", "TikTok", "TikTok 公开账号或视频"),
        "linkedin": ("linkedin.com", "LinkedIn", "LinkedIn 公司、个人或动态"),
    })
    selected_platforms = (
        list(platform_queries)
        if source_mode in ("all", "social")
        else [source_mode] if source_mode in platform_queries else []
    )
    selected_platforms = [platform for platform in selected_platforms if platform in enabled_sources]
    social_source_modes = {"social", *platform_queries.keys()}
    if is_china_discovery and source_mode not in social_source_modes:
        selected_platforms = []
    social_search_stats = {
        "queries": 0,
        "rawResults": 0,
        "apifyResults": 0,
        "apifyByPlatform": {},
        "rawByPlatform": {},
        "profileByPlatform": {},
        "acceptedByPlatform": {},
        "profileResults": 0,
        "acceptedResults": 0,
        "officialWebsiteProfiles": 0,
    }
    reverse_platforms = set(selected_platforms)
    if source_mode == "social":
        if "youtube" in enabled_sources:
            reverse_platforms.add("youtube")
    if reverse_platforms:
        reverse_seed_limit = min(12 if source_mode in platform_queries or source_mode == "youtube" else 32, result_limit)
        website_social_results = social_accounts_from_business_websites(
            country,
            target_type,
            reverse_platforms,
            seed_limit=reverse_seed_limit,
        )
        social_search_stats["officialWebsiteProfiles"] = len(website_social_results)
        for item in website_social_results:
            item["social_analysis"] = analyze_social_business_profile(
                f"{item.get('title', '')} {item.get('snippet', '')} {item.get('url', '')}",
                item.get("origin", ""),
                item.get("account_type", "公司账号"),
            )
        raw_results.extend(website_social_results)
    for platform in selected_platforms:
        site, origin, source_type = platform_queries[platform]
        query_variants = social_search_variants(
            platform,
            site,
            market,
            target_type,
            account_scope,
        )
        if source_mode in ("combined", "all"):
            query_variants = query_variants[:14]
        elif source_mode == "social":
            query_variants = query_variants[:20]
        elif source_mode == platform:
            query_variants = query_variants[:24 if platform == "facebook" else 14]
        social_search_stats["queries"] += len(query_variants)
        social_results: list[dict] = []
        executor = ThreadPoolExecutor(max_workers=min(2, max(1, len(query_variants))))
        futures = [
            executor.submit(
                search_web,
                search_query,
                4 if source_mode in ("combined", platform) else 8,
                freshness_days,
                country,
            )
            for search_query in query_variants
        ]
        try:
            for future in as_completed(futures, timeout=max(20, DISCOVERY_SEARCH_TIMEOUT * 2)):
                try:
                    social_results.extend(future.result(timeout=1))
                except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                    continue
        except FuturesTimeoutError:
            pass
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
        apify_results = []
        if platform in APIFY_SOCIAL_ACTORS:
            apify_queries, apify_result_limit = apify_query_plan(query_variants, source_mode, platform)
            try:
                apify_results = search_apify_social(
                    platform,
                    apify_queries,
                    origin,
                    source_type,
                    limit=apify_result_limit,
                    location=list(dict.fromkeys([
                        country_meta.get("location") or market,
                        *cities[:4],
                    ])),
                )
            except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                apify_results = []
        if platform == "instagram" and source_mode == "instagram" and len(apify_results) < 6:
            hashtag_results = search_apify_instagram_hashtag_accounts(
                country,
                market,
                cities,
                origin,
                source_type,
                limit=max(12, apify_result_limit),
            )
            seen_apify_urls = {
                str(item.get("url") or "").lower().rstrip("/")
                for item in apify_results
            }
            apify_results.extend(
                item
                for item in hashtag_results
                if str(item.get("url") or "").lower().rstrip("/") not in seen_apify_urls
            )
        if apify_results:
            social_search_stats["apifyResults"] += len(apify_results)
            social_search_stats["apifyByPlatform"][origin] = social_search_stats["apifyByPlatform"].get(origin, 0) + len(apify_results)
            social_results.extend(apify_results)
        if source_mode == platform and len(social_results) < 6:
            try:
                local_social_results = social_accounts_from_local_source_pages(
                    country,
                    target_type,
                    platform,
                    origin,
                    source_type,
                    limit=15,
                )
            except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException):
                local_social_results = []
            if local_social_results:
                social_search_stats["officialWebsiteProfiles"] += len(local_social_results)
                social_results.extend(local_social_results)
        social_search_stats["rawResults"] += len(social_results)
        social_search_stats["rawByPlatform"][origin] = social_search_stats["rawByPlatform"].get(origin, 0) + len(social_results)
        expected_domains = {
            "instagram": ("instagram.com",),
            "facebook": ("facebook.com", "fb.com"),
            "tiktok": ("tiktok.com",),
            "linkedin": ("linkedin.com",),
            "telegram": ("t.me", "telegram.me", "telegram.dog", "tgstat.", "telemetr.", "telegramchannels.", "tgram.", "tlgrm."),
            "twitter": ("x.com", "twitter.com"),
            "threads": ("threads.net",),
            "pinterest": ("pinterest.",),
            "reddit": ("reddit.com",),
            "vk": ("vk.com",),
        }.get(platform, (site.split("/")[0],))
        seen_platform_urls: set[str] = set()
        for item in social_results:
            item_url = normalize_social_profile_url(item.get("url", ""))
            item_domain = safe_urlparse(item_url).netloc.lower().removeprefix("www.")
            identity = item_url.lower().rstrip("/")
            if (
                not item_url
                or not any(expected_domain in item_domain for expected_domain in expected_domains)
                or identity in seen_platform_urls
                or not is_social_profile_url(item_url)
            ):
                continue
            seen_platform_urls.add(identity)
            social_search_stats["profileResults"] += 1
            social_search_stats["profileByPlatform"][origin] = social_search_stats["profileByPlatform"].get(origin, 0) + 1
            item["url"] = item_url
            item["origin"] = origin
            item["source_type"] = source_type
            item["source_url"] = item_url
            item.setdefault("customer_website", "")
            item["skip_fetch"] = True
            path = safe_urlparse(item_url).path.lower()
            is_person = (
                "/in/" in path
                or account_scope == "person"
                or bool(re.search(r"\b(owner|founder|manager|director)\b", f"{item['title']} {item['snippet']}", re.I))
            )
            item["account_type"] = "个人决策人" if is_person else "公司账号"
            item["social_analysis"] = analyze_social_business_profile(
                f"{item['title']} {item['snippet']} {item_url}",
                origin,
                item["account_type"],
            )
            raw_results.append(item)
    if "youtube" in enabled_sources and source_mode in ("youtube", "social") and (
        not is_china_discovery or source_mode in ("social", "youtube")
    ):
        youtube_searches = youtube_discovery_searches(country, cities, account_scope)
        youtube_searches, youtube_per_query_limit = youtube_query_plan(youtube_searches, source_mode, country)
        youtube_candidates: list[tuple[dict, str]] = []
        if country_meta.get("code") == "qa" and account_scope in ("company", "both"):
            try:
                verified_items = search_youtube_verified_handles(YOUTUBE_QATAR_VERIFIED_HANDLES, country)
            except (OSError, ValueError, TimeoutError, json.JSONDecodeError):
                verified_items = []
            youtube_candidates.extend((item, "company account") for item in verified_items)
        for youtube_query, youtube_account_type in youtube_searches:
            try:
                youtube_items = search_youtube_channels(youtube_query, limit=youtube_per_query_limit, country=country)
            except (OSError, ValueError, TimeoutError, json.JSONDecodeError):
                youtube_items = []
            youtube_candidates.extend((item, youtube_account_type) for item in youtube_items)
        for item, youtube_account_type in youtube_candidates:
                location_text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('country', '')}".lower()
                location_terms = {
                    country.split(" ")[0].lower(),
                    "emirates" if "UAE" in country else "",
                    *(
                        city.lower()
                        for key, cities in COUNTRY_HINTS.items()
                        if key.lower() in country.lower()
                        for city in cities
                    ),
                }
                youtube_analysis = analyze_social_business_profile(
                    f"{item.get('title', '')} {item.get('snippet', '')} {item.get('url', '')}",
                    "YouTube",
                    youtube_account_type,
                )
                youtube_discovery_candidate = is_youtube_automotive_lead(
                    item.get("title", ""),
                    item.get("snippet", ""),
                    item.get("url", ""),
                )
                youtube_local_official = is_local_official_youtube_auto_channel(item, country)
                youtube_discovery_candidate = youtube_discovery_candidate or youtube_local_official
                if country_meta.get("code") == "qa" and not youtube_local_official:
                    title_identity = clean_text(str(item.get("title") or "")).lower()
                    has_company_title = any(term in title_identity for term in (
                        "auto", "car", "motor", "vehicle", "showroom", "fleet", "rent", "trading",
                    ))
                    youtube_discovery_candidate = bool(
                        youtube_discovery_candidate
                        and has_company_title
                        and has_strong_automotive_business_evidence(location_text)
                        and has_target_country_signal(location_text, country)
                    )
                if not youtube_discovery_candidate:
                    continue
                if (
                    not any(term and term in location_text for term in location_terms)
                    and not youtube_analysis.get("isCommercial")
                ):
                    continue
                item["origin"] = "YouTube"
                item["source_type"] = "YouTube 公开频道" if youtube_analysis.get("isCommercial") else "YouTube 公开频道（待核验）"
                item["source_url"] = item["url"]
                item["customer_website"] = ""
                item["account_type"] = youtube_account_type
                item["social_analysis"] = youtube_analysis
                item["youtube_discovery_candidate"] = youtube_discovery_candidate
                item["youtube_local_official_channel"] = youtube_local_official
                if youtube_local_official:
                    item["structured_business_profile"] = True
                raw_results.append(item)
    if source_mode in platform_queries:
        expected_origin = platform_queries[source_mode][1]
        expected_domains = {
            "instagram": ("instagram.com",),
            "facebook": ("facebook.com", "fb.com"),
            "tiktok": ("tiktok.com",),
            "linkedin": ("linkedin.com",),
        }[source_mode]
        raw_results = [
            item
            for item in raw_results
            if (
                item.get("origin") == expected_origin
                and any(
                    domain in safe_urlparse(item.get("url", "")).netloc.lower()
                    for domain in expected_domains
                )
            )
        ]
    if "dealer" in enabled_sources and source_mode in ("all", "combined"):
        raw_results = enrich_local_directory_results(raw_results, country, limit=min(70, max(50, result_limit)))
    raw_results = apply_configured_source_caps(raw_results, country, source_mode)
    pipeline_stats = {
        "rawCollected": len(raw_results),
        "afterCountryDedup": 0,
        "candidatePool": 0,
        "processed": 0,
        "aiRejected": 0,
        "rejected": {},
        "qualifiedBeforeMerge": 0,
        "afterEntityMerge": 0,
        "final": 0,
    }

    def reject_candidate(reason: str) -> None:
        rejected = pipeline_stats["rejected"]
        rejected[reason] = int(rejected.get(reason) or 0) + 1
    raw_results = filter_raw_results_for_country_and_duplicates(raw_results, country)
    pipeline_stats["afterCountryDedup"] = len(raw_results)
    raw_results = balance_discovery_sources(raw_results)
    raw_results = soften_dominant_discovery_sources(raw_results, source_mode, result_limit)
    raw_results = filter_raw_results_for_country_and_duplicates(raw_results, country)
    target_min = discovery_target_min()
    target_max = discovery_target_max()
    if source_mode in ("all", "combined") and local_discovery_sources(country):
        target_max = min(result_limit, max(target_max, 50))
    raw_results = raw_results[: max(target_max * 2, 60)]
    pipeline_stats["candidatePool"] = len(raw_results)
    if source_mode == "dealer":
        def dealer_source_priority(item: dict) -> tuple:
            origin = item.get("origin", "")
            url = normalize_public_url(item.get("url", ""))
            has_website = bool(item.get("customer_website")) and "openstreetmap.org" not in url
            trusted_source = origin in ("OpenStreetMap", "Google Maps")
            has_contact = bool(item.get("contact"))
            return (
                -int(has_website),
                -int(trusted_source),
                -int(has_contact),
                str(item.get("title") or ""),
            )

        raw_results = sorted(raw_results, key=dealer_source_priority)[: max(result_limit, 18)]
    leads = []
    seen_sources = set()
    excluded_brand_bound_dealers = 0
    for item in raw_results:
        if len(leads) >= target_max:
            break
        pipeline_stats["processed"] += 1
        item["url"] = normalize_public_url(item.get("url", ""))
        if not is_valid_http_url(item["url"]):
            reject_candidate("invalidUrl")
            continue
        parsed = safe_urlparse(item["url"])
        domain = parsed.netloc.lower().removeprefix("www.")
        path_lower = parsed.path.lower()
        title_lower = item["title"].lower()
        is_google_places = item.get("origin") == "Google Maps"
        is_social_result = item.get("origin") in (
            "Facebook", "Instagram", "TikTok", "LinkedIn", "YouTube",
            "Telegram", "X / Twitter", "Threads", "Pinterest", "Reddit", "VK",
        )
        social_analysis = item.get("social_analysis") or (
            analyze_social_business_profile(
                f"{item.get('title', '')} {item.get('snippet', '')} {item.get('url', '')}",
                item.get("origin", ""),
                item.get("account_type", ""),
            )
            if is_social_result else {}
        )
        if not is_google_places and not is_social_result and any(
            blocked in domain or blocked in item["url"].lower()
            for blocked in BLOCKED_DOMAINS
        ):
            reject_candidate("blockedDomain")
            continue
        allow_recent_content = bool(freshness_days) or target_type in ("buying", "government", "individual")
        if not is_social_result and any(word in title_lower for word in BLOCKED_TITLE_WORDS) and not allow_recent_content:
            reject_candidate("blockedTitle")
            continue
        if not is_social_result and any(part in path_lower for part in BLOCKED_PATH_PARTS) and not allow_recent_content:
            reject_candidate("blockedPath")
            continue
        if not is_social_result and re.search(r"/20\d{2}/\d{1,2}/\d{1,2}/", path_lower) and not allow_recent_content:
            reject_candidate("datedContent")
            continue
        source_identity = raw_result_identity(item)
        if source_identity in seen_sources:
            reject_candidate("duplicateSource")
            continue
        seen_sources.add(source_identity)

        page_text = f"{item['title']} {item['snippet']}"
        page = ""
        contact = item.get("contact", "")
        origin_name = item.get("origin", "")
        is_raw_social_or_video_source = origin_name in (
            "Facebook", "Instagram", "TikTok", "LinkedIn", "YouTube",
            "Telegram", "X / Twitter", "Threads", "Pinterest", "Reddit", "VK",
        )
        should_fetch_social_page = is_raw_social_or_video_source
        if not item.get("skip_fetch") and (not is_raw_social_or_video_source or should_fetch_social_page):
            try:
                page = fetch_text(item["url"], timeout=5 if source_mode == "dealer" else 8)
                page_text = extract_meta(page)
                contact = contact or extract_contact(page if should_fetch_social_page else page_text)
            except (OSError, TimeoutError, UnicodeError):
                pass

        combined = f"{item['title']} {item['snippet']} {page_text} {item.get('url', '')}"
        if has_foreign_location_conflict(combined, country):
            reject_candidate("countryConflict")
            continue
        verified_local_youtube = bool(
            item.get("origin") == "YouTube"
            and item.get("youtube_local_official_channel")
            and item.get("structured_business_profile")
        )
        if is_obviously_irrelevant_lead(combined) and not verified_local_youtube:
            reject_candidate("irrelevantBusiness")
            continue
        if is_media_or_content_channel(combined) and not verified_local_youtube:
            reject_candidate("mediaOrContent")
            continue
        brand_binding_text = item["title"] if item.get("local_directory_candidate") else combined
        if not is_social_result and is_brand_bound_chinese_dealer(brand_binding_text):
            excluded_brand_bound_dealers += 1
            reject_candidate("brandBoundDealer")
            continue
        if is_social_result:
            social_analysis = analyze_social_business_profile(
                combined,
                item.get("origin", ""),
                item.get("account_type", ""),
            )
            allow_youtube_discovery_candidate = (
                item.get("origin") == "YouTube"
                and bool(item.get("youtube_discovery_candidate"))
            )
            if item.get("origin") != "YouTube" and not (
                social_analysis.get("isCommercial")
                and social_analysis.get("hasAutomotiveMarker")
            ):
                reject_candidate("nonCommercialSocial")
                continue
            if item.get("origin") == "YouTube" and not (
                allow_youtube_discovery_candidate
                or (
                    social_analysis.get("isCommercial")
                    and social_analysis.get("hasAutomotiveMarker")
                )
            ):
                reject_candidate("nonCommercialYoutube")
                continue
            social_search_stats["acceptedResults"] += 1
            social_search_stats["acceptedByPlatform"][item.get("origin", "")] = (
                social_search_stats["acceptedByPlatform"].get(item.get("origin", ""), 0) + 1
            )
        if not is_google_places and item.get("origin") != "OpenStreetMap" and not is_social_result:
            business_match = re.search(
                r"\b(dealer|dealership|showroom|importer|exporter|trading|distributor|"
                r"cars|motors|automotive|fleet|rental|procurement|tender|buyer|rfq|"
                r"owner|founder|general manager|import manager|fleet manager|sales director)\b"
                r"|автосалон|автомобил|авто|машин",
                combined,
                re.I,
            )
            if not business_match:
                reject_candidate("weakBusinessKeyword")
                continue
            if re.match(r"^\s*20\d{2}\s+", item["title"]) and re.search(
                r"\b(seater|4wd|awd|km|mileage|price|available)\b",
                combined,
                re.I,
            ):
                reject_candidate("vehicleListing")
                continue
        if not is_social_result and not re.search(
            r"\b(dealer|dealership|showroom|importer|exporter|trading|cars|motors|"
            r"vehicles?|automotive|ev|electric|fleet|rental|procurement|tender|buyer|rfq|wanted|"
            r"owner|founder|general manager|import manager|fleet manager|sales director)\b"
            r"|автосалон|автомобил|авто|машин",
            combined,
            re.I,
        ):
            reject_candidate("noAutomotiveKeyword")
            continue
        company = infer_company_name(item["title"], domain)
        lead_type = infer_type(combined)
        origin = item.get("origin", "公开网页搜索")
        source_url = item.get("source_url") or item["url"]
        source_type = item.get("source_type") or source_details(source_url, origin)[1]
        is_competitor = False if country_meta.get("code") == "cn" else detect_competitor(combined)
        business_signals, intent_signals = opportunity_signals(combined)
        business_signals = list(dict.fromkeys([
            *business_signals,
            *(social_analysis.get("businessSignals") or []),
        ]))[:6]
        intent_signals = list(dict.fromkeys([
            *intent_signals,
            *(social_analysis.get("intentSignals") or []),
        ]))[:6]
        city = infer_city(country, combined)
        source_title = item.get("title") or company
        source_excerpt = item.get("snippet") or page_text[:500]
        published_at = extract_published_at(
            f"{item.get('snippet', '')} {page_text[:700]}",
            source_url,
        )
        if item.get("origin") == "YouTube":
            published_at = item.get("latestVideoPublishedAt") or published_at
            if not is_recent_youtube_video_date(published_at):
                reject_candidate("staleYoutube")
                continue
        is_dealer_directory_source = source_mode == "dealer" and not is_social_result and bool(item.get("customer_website"))
        is_long_lived_business_source = (
            source_mode == "all"
            and (
                is_google_places
                or origin.startswith("OpenStreetMap")
                or source_type in ("地图与地理商业目录", "Google Maps 企业资料")
            )
        )
        if is_social_result and not is_within_freshness(published_at, freshness_days):
            reject_candidate("outsideFreshness")
            continue
        customer_website = item.get("customer_website") or (
            item["url"] if source_type == "车商官网或汽车行业网站" else ""
        )
        customer_website = normalize_public_url(customer_website)
        if customer_website and not is_business_website_url(customer_website):
            customer_website = ""
        social_profile = {}
        if is_social_result:
            try:
                social_profile = read_social_profile(
                    source_url,
                    item.get("account_type") or "公司账号",
                    f"{origin} 公开主页",
                )
            except (OSError, ValueError, TimeoutError):
                social_profile = {}
            social_websites = [
                website_url
                for website_url in (social_profile.get("externalWebsites") or [])
                if is_business_website_url(website_url)
            ]
            if social_websites and not has_automotive_business_signal(
                " ".join([
                    combined,
                    social_profile.get("title", ""),
                    social_profile.get("description", ""),
                    " ".join(social_websites),
                ])
            ):
                social_websites = []
            if social_websites:
                customer_website = customer_website or social_websites[0]
                combined = " ".join(
                    value for value in (
                        combined,
                        social_profile.get("title", ""),
                        social_profile.get("description", ""),
                        " ".join(social_websites),
                    ) if value
                )
        profile_contact_text = " ".join(
            str(value or "")
            for value in (
                social_profile.get("title"),
                social_profile.get("description"),
                " ".join(social_profile.get("contactSignals") or []),
            )
        )
        source_contact_text = f"{item.get('snippet', '')} {item.get('title', '')} {contact} {profile_contact_text}"
        contacts = extract_public_contacts(source_contact_text, item.get("tags"))
        if item.get("google_public_contacts"):
            contacts = merge_public_contacts(contacts, item.get("google_public_contacts") or {})
        if item.get("directory_public_contacts"):
            contacts = merge_public_contacts(contacts, item.get("directory_public_contacts") or {})
        if page and (is_raw_social_or_video_source or not any(contacts.get(key) for key in ("email", "phone", "whatsapp"))):
            contacts = merge_public_contacts(
                contacts,
                extract_public_contacts(page if is_raw_social_or_video_source else page_text, item.get("tags")),
            )
        if not customer_website and contacts.get("websites"):
            customer_website = next(
                (website for website in contacts["websites"] if is_business_website_url(website)),
                "",
            )
        had_customer_website_candidate = bool(customer_website)
        website_audit = {
            "url": customer_website,
            "reachable": False,
            "vehicleRelated": False,
            "pages": [],
            "text": "",
            "reason": "no_customer_website",
        }
        if customer_website:
            website_audit = audit_customer_website(customer_website)
            if not website_audit.get("reachable") or not website_audit.get("vehicleRelated"):
                customer_website = ""
            else:
                customer_website = website_audit.get("url") or customer_website
                combined = " ".join(
                    value for value in (
                        combined,
                        str(website_audit.get("text") or "")[:3000],
                    ) if value
                )
        if (
            had_customer_website_candidate
            and not customer_website
            and not is_google_places
            and item.get("origin") != "OpenStreetMap"
            and not is_social_result
            and not (
                item.get("local_directory_candidate")
                and item.get("directory_detail_fetched")
                and any(
                    (item.get("directory_public_contacts") or {}).get(key)
                    for key in ("email", "phone", "whatsapp")
                )
            )
        ):
            reject_candidate("websiteAuditFailed")
            continue
        official_contact_url = ""
        official_contact_excerpt = ""
        official_contact_entry_url = ""
        official_contact_entry_excerpt = ""
        if item.get("google_official_pages") and any(contacts.get(key) for key in ("email", "phone", "whatsapp")):
            first_official_page = (item.get("google_official_pages") or [{}])[0]
            official_contact_url = first_official_page.get("url", "") or customer_website
            official_contact_excerpt = clean_text(first_official_page.get("html", "") or first_official_page.get("text", ""))[:700]
        if (
            customer_website
            and target_type != "individual"
            and not all(contacts.get(key) for key in ("email", "phone", "whatsapp"))
        ):
            for official_page in (website_audit.get("pages") or official_site_pages(customer_website))[:3]:
                official_contacts = extract_public_contacts(official_page.get("html", ""))
                contacts = merge_public_contacts(contacts, official_contacts)
                if not official_contact_url and any(official_contacts.get(key) for key in ("email", "phone", "whatsapp")):
                    official_contact_url = official_page.get("url", "")
                    official_contact_excerpt = clean_text(official_page.get("html", ""))[:700]
                if all(contacts.get(key) for key in ("email", "phone", "whatsapp")):
                    break
        if customer_website and target_type != "individual" and not any(contacts.get(key) for key in ("email", "phone", "whatsapp")):
            contact_entry = official_contact_entry(website_audit.get("pages") or official_site_pages(customer_website))
            official_contact_entry_url = contact_entry.get("url", "")
            official_contact_entry_excerpt = contact_entry.get("excerpt", "")
        if is_social_profile_url(item["url"]) and item["url"] not in contacts["social_accounts"]:
            contacts["social_accounts"].insert(0, item["url"])
        if item.get("account_type") == "个人决策人":
            contacts["contact_name"] = contacts["contact_name"] or company
            role_match = re.search(
                r"\b(owner|founder|general manager|import manager|fleet manager|sales director|sales manager)\b",
                combined,
                re.I,
            )
            contacts["contact_role"] = contacts["contact_role"] or (
                role_match.group(1).title() if role_match else ""
            )
        if target_type == "individual":
            contacts = {
                "email": "",
                "phone": "",
                "whatsapp": "",
                "social_accounts": [],
                "contact_name": "",
                "contact_role": "",
            }
        if target_type != "individual" and contact and not contacts["email"] and "@" in contact:
            contacts["email"] = contact
            contacts["emails"] = list(dict.fromkeys([contact.lower(), *(contacts.get("emails") or [])]))
        elif target_type != "individual" and contact and not contacts["phone"]:
            contact_contacts = extract_public_contacts(contact)
            if contact_contacts.get("whatsapp"):
                contacts["whatsapp"] = contacts.get("whatsapp") or contact_contacts["whatsapp"]
                contacts["whatsapps"] = list(dict.fromkeys([*(contacts.get("whatsapps") or []), *(contact_contacts.get("whatsapps") or [])]))
            if contact_contacts.get("phone"):
                contacts["phone"] = contact_contacts["phone"]
                contacts["phones"] = list(dict.fromkeys([*(contacts.get("phones") or []), *(contact_contacts.get("phones") or [])]))
        contact_source_url = official_contact_url or source_url
        contact_source_name = "公司官网" if official_contact_url else origin
        contact_source_excerpt = official_contact_excerpt or source_excerpt
        email_sources = []
        primary_profile_contact_text = f"{source_contact_text} {page if is_social_result else ''}"
        for email in contacts.get("emails") or ([contacts["email"]] if contacts["email"] else []):
            is_lead_profile_email = bool(
                is_social_result
                and re.search(re.escape(email), primary_profile_contact_text, re.I)
            )
            email_sources.append({
                "email": email,
                "sources": [{
                    "url": contact_source_url,
                    "name": "线索主页来源" if is_lead_profile_email else contact_source_name,
                    "sourceKind": "lead_profile" if is_lead_profile_email else "",
                    "verified": bool(
                        is_lead_profile_email
                        or item.get("origin") in ("OpenStreetMap", "Google Maps")
                        or item.get("directory_detail_fetched")
                        or official_contact_url
                        or (page and re.search(re.escape(email), page, re.I))
                    ),
                    "excerpt": contact_source_excerpt[:260],
                }],
            })
        if customer_website and target_type != "individual":
            try:
                hunter_candidates = hunter_email_candidates(customer_website, company, limit=5)
            except (OSError, ValueError, TimeoutError, urllib.error.URLError, http.client.HTTPException, json.JSONDecodeError):
                hunter_candidates = []
            for hunter_item in hunter_candidates:
                hunter_email = hunter_item.get("email", "")
                if not hunter_email or any(record.get("email", "").lower() == hunter_email.lower() for record in email_sources):
                    continue
                hunter_name = " ".join(
                    value for value in (hunter_item.get("firstName"), hunter_item.get("lastName")) if value
                ).strip()
                hunter_excerpt = " / ".join(
                    value for value in (
                        hunter_name,
                        hunter_item.get("position"),
                        f"confidence {hunter_item.get('confidence')}" if hunter_item.get("confidence") else "",
                    ) if value
                )
                email_sources.append({
                    "email": hunter_email,
                    "sources": [{
                        "url": customer_website,
                        "name": "Hunter.io",
                        "verified": False,
                        "excerpt": hunter_excerpt or "Hunter.io domain search candidate",
                    }],
                })
        verified_email_sources = [
            record for record in email_sources
            if any(source.get("verified") for source in record["sources"])
        ]
        contacts["email"] = verified_email_sources[0]["email"] if verified_email_sources else ""
        phone_sources = [
            {"value": phone, "sources": [{"url": contact_source_url, "name": contact_source_name, "excerpt": contact_source_excerpt[:260]}]}
            for phone in contacts.get("phones") or ([contacts["phone"]] if contacts["phone"] else [])
            if phone_value_matches_country(phone, country)
        ]
        whatsapp_sources = [
            {"value": value, "sources": [{"url": contact_source_url, "name": contact_source_name, "excerpt": contact_source_excerpt[:260]}]}
            for raw_value in contacts.get("whatsapps") or ([contacts["whatsapp"]] if contacts["whatsapp"] else [])
            for value in [clean_whatsapp_value(raw_value)]
            if value
            if phone_value_matches_country(value, country)
        ]
        contacts["phone"] = phone_sources[0]["value"] if phone_sources else ""
        contacts["whatsapp"] = whatsapp_sources[0]["value"] if whatsapp_sources else ""
        has_contact_entry = bool(official_contact_entry_url)
        contactable = bool(verified_email_sources or phone_sources or whatsapp_sources or has_contact_entry)
        if quality_policy.get("requireContactOrWebsite") and not (contactable or customer_website):
            reject_candidate("noContactOrWebsite")
            continue
        official_source_count = 1 if customer_website else 0
        lead_evidence = list(item.get("google_evidence") or [])
        add_unique_evidence(
            lead_evidence,
            evidence_item(
                source_url,
                source_title,
                source_excerpt,
                origin,
                source_type,
            ),
        )
        if customer_website and is_social_result and social_profile:
            add_unique_evidence(
                lead_evidence,
                evidence_item(
                    customer_website,
                    f"{company} 官网",
                    social_profile.get("description", "") or f"{origin} 主页 Website 外链指向 {customer_website}",
                    "社媒主页 Website 外链",
                    "公司官网",
                ),
            )
        if official_contact_entry_url:
            add_unique_evidence(
                lead_evidence,
                evidence_item(
                    official_contact_entry_url,
                    f"{company} contact entry",
                    official_contact_entry_excerpt or f"{customer_website} provides a public contact entry.",
                    "Official website",
                    "Website contact entry",
                ),
            )
        evidence_source_count = len(lead_evidence)
        source_domains = {
            safe_urlparse(value).netloc.lower().removeprefix("www.")
            for value in (source_url, customer_website)
            if value and safe_urlparse(value).netloc
        }
        source_decision = (
            "建议优先联系"
            if customer_website and contactable
            else "已确认官网，建议补充联系方式"
            if customer_website
            else "待全网核验"
        )
        acquisition_priority = (
            "优先开发"
            if customer_website and contactable
            else "补联系方式"
            if customer_website
            else "先核实主体"
        )
        recommended_models = recommend_models(combined, model)
        confidence, confidence_label = confidence_score(
            customer_website,
            source_url,
            contacts,
            published_at,
            combined,
        )
        source_translation = chinese_source_summary(
            company,
            target_label,
            city,
            source_type,
            contacts,
            published_at,
        )
        has_business_evidence = has_strong_automotive_business_evidence(combined)
        youtube_local_verified = bool(
            origin == "YouTube"
            and item.get("youtube_local_official_channel")
            and item.get("structured_business_profile")
            and has_target_country_signal(combined, country)
        )
        linkedin_actor_verified = bool(
            origin == "LinkedIn"
            and item.get("apifyPlatform") == "linkedin"
            and item.get("structured_business_profile")
            and social_analysis.get("isCommercial")
            and social_analysis.get("hasAutomotiveMarker")
            and has_target_country_signal(combined, country)
            and re.search(
                r"\b(retail motor vehicles|wholesale motor vehicles|motor vehicle manufacturing|"
                r"automotive|car dealer|dealership|vehicle importer|car importer|distributor|showroom)\b",
                combined,
                re.I,
            )
        )
        if linkedin_actor_verified or youtube_local_verified:
            has_business_evidence = True
        ai_review = ai_review_lead_candidate(
            company=company,
            country=country,
            city=city,
            source_url=source_url,
            customer_website=customer_website,
            origin=origin,
            source_type=source_type,
            text=combined,
        )
        ai_policy = admin_control_settings().get("ai", {})
        if not ai_review:
            if ai_policy.get("failurePolicy") == "skip":
                reject_candidate("aiUnavailableSkip")
                continue
            available_evidence = "、".join(filter(None, (
                source_type or origin,
                "客户官网" if customer_website else "",
                "公开联系方式" if contactable else "",
            ))) or "公开来源"
            ai_review = {
                "provider": get_ai_provider() or "deepseek",
                "model": get_ai_model("fast"),
                "decision": "manual_review" if ai_policy.get("failurePolicy") != "allow" else "keep",
                "confidence": 0,
                "available": False,
                "reason": (
                    f"AI服务未返回有效结果；{company}当前仅有{available_evidence}，"
                    "需人工核验汽车业务主体及目标国家信息。"
                ),
                "countryEvidence": "none",
            }
        minimum_ai_confidence = int(quality_policy.get("minimumAiConfidence") or 0)
        ai_review = apply_ai_confidence_threshold(ai_review, minimum_ai_confidence)
        if ai_review:
            hard_reject = bool(
                (quality_policy.get("strictCountryMatch") and ai_review.get("countryEvidence") == "conflict")
                or (quality_policy.get("rejectPersonalAccounts") and ai_review.get("entityType") == "personal")
            )
            ai_reject = bool(
                ai_review.get("decision") == "reject"
                or (quality_policy.get("requireAutomotiveBusiness") and ai_review.get("automotiveBusiness") is False)
                or ai_review.get("salesLeadEligible") is False
            )
            platform_business_verified = linkedin_actor_verified or youtube_local_verified
            if hard_reject or (ai_reject and not platform_business_verified):
                pipeline_stats["aiRejected"] += 1
                reject_candidate("aiRejected")
                continue
            if platform_business_verified and ai_reject:
                ai_review["decision"] = "manual_review"
                ai_review["reason"] = (
                    "平台企业资料已确认目标地区与汽车行业，保留进入人工审核；"
                    + clean_text(str(ai_review.get("reason") or ""))
                )[:500]
            if ai_review.get("automotiveBusiness"):
                has_business_evidence = True
                if ai_review.get("businessType"):
                    business_signals = list(dict.fromkeys([
                        ai_review["businessType"],
                        *business_signals,
                    ]))[:6]
        country_evidence_text = " ".join(
            value for value in (
                source_title,
                source_excerpt,
                page,
                official_contact_excerpt,
                source_url,
                customer_website,
            ) if value
        )
        trusted_geo_match = (
            origin in {"Google Maps", "OpenStreetMap"}
            or origin.startswith("OpenStreetMap")
        ) and not has_foreign_location_conflict(country_evidence_text, country)
        ai_country_match = bool(
            ai_review.get("targetCountryMatch")
            and ai_review.get("countryEvidence") == "explicit"
        )
        country_match = bool(
            trusted_geo_match
            or ai_country_match
            or has_target_country_signal(country_evidence_text, country)
        )
        if quality_policy.get("requireAutomotiveBusiness") and not has_business_evidence:
            pipeline_stats["aiRejected"] += 1
            continue
        if quality_policy.get("strictCountryMatch") and not country_match:
            pipeline_stats["aiRejected"] += 1
            continue
        scoring_text = combined
        if ai_review and ai_review.get("chineseNevEvidence"):
            scoring_text = f"{scoring_text} Chinese new energy vehicle"
        if ai_review and ai_review.get("huaweiSeriesEvidence"):
            scoring_text = f"{scoring_text} Huawei AITO HIMA HarmonyOS"
        score, score_breakdown, score_dimensions, score_tier = lead_opportunity_score(
            scoring_text,
            bool(customer_website or item.get("structured_business_profile")),
            contactable,
            int(item.get("google_reviews") or 0),
            requested_model=model,
            lead_type=lead_type,
            is_competitor=is_competitor,
            target_country_match=country_match,
            has_email=bool(verified_email_sources),
            has_phone=bool(phone_sources),
            has_whatsapp=bool(whatsapp_sources),
            has_decision_maker=bool(contacts["contact_name"] or contacts["contact_role"]),
            allow_competitor_auto=country_meta.get("code") != "cn",
        )
        auto_import_eligible = bool(
            has_business_evidence
            and country_match
            and score >= int(quality_policy.get("minimumAutoImportScore") or 0)
            and (
                not item.get("local_directory_candidate")
                or (
                    item.get("directory_detail_fetched")
                    and item.get("directory_profile_page")
                    and item.get("directory_sales_fit")
                    and (contactable or customer_website)
                )
            )
        )
        contact_reason = (
            f"该线索与“{target_label}”目标匹配，"
            f"信息可信度为{confidence_label}（{confidence}%），"
            f"建议优先推荐{'、'.join(recommended_models)}。"
        )
        if intent_signals and has_business_evidence:
            contact_reason = (
                f"发现{ '、'.join(intent_signals) }，即使页面未提及华为汽车也值得优先联系。"
                + contact_reason
            )
        elif business_signals and has_business_evidence:
            contact_reason = (
                f"已确认具备{ '、'.join(business_signals) }，可作为潜在进口或分销客户培育。"
                + contact_reason
            )
        if not has_business_evidence:
            contact_reason = "未发现明确车商、展厅、进口商或车辆销售证据；仅可作为待人工核验线索，不应优先联系。"
        if is_competitor:
            contact_reason += " 但页面存在汽车出口同行特征，建议先核实身份，不直接发送底价。"
        reason = f"{origin}显示该客户可能是 {lead_type}。来源：{domain}。"
        if contacts["email"] or contacts["phone"] or contacts["whatsapp"]:
            reason += " 已找到公开商业联系方式。"
        reason += f" 建议结合官网内容推荐{model}。"
        leads.append(
            {
                "company": company[:80],
                "country": country.split(" ")[0],
                "city": city,
                "type": lead_type,
                "source": customer_website or source_url,
                "origin": origin,
                "sourceType": source_type,
                "sourceTitle": source_title,
                "sourceUrl": source_url,
                "sourceExcerpt": source_excerpt[:700],
                "evidenceSources": lead_evidence,
                "researchAt": "",
                "researchSummary": "当前只有原始发现来源，建议在线索审核中执行全网补全。",
                "publishedAt": published_at,
                "latestVideoPublishedAt": item.get("latestVideoPublishedAt", "") if item.get("origin") == "YouTube" else "",
                "freshnessDays": freshness_days,
                "customerWebsite": customer_website,
                "contactName": contacts["contact_name"],
                "contactRole": contacts["contact_role"],
                "email": contacts["email"],
                "emailSources": verified_email_sources,
                "unverifiedEmailCandidates": [
                    record for record in email_sources
                    if record not in verified_email_sources
                ],
                "phone": contacts["phone"],
                "phoneSources": phone_sources,
                "whatsapp": contacts["whatsapp"],
                "whatsappSources": whatsapp_sources,
                "socialAccounts": contacts["social_accounts"],
                "socialProfiles": [
                    {
                        "platform": social_platform(item["url"]),
                        "accountType": social_analysis.get("accountType") or item.get("account_type", "公司账号"),
                        "relationship": item.get("official_relationship") or f"{origin} 公开结果",
                        "title": source_title,
                        "description": source_excerpt[:700],
                        "url": item["url"],
                        "handle": safe_urlparse(item["url"]).path.strip("/").split("/")[-1],
                        "businessSignals": social_analysis.get("businessSignals") or [],
                        "intentSignals": social_analysis.get("intentSignals") or [],
                        "decisionRole": social_analysis.get("decisionRole", ""),
                        "contactSignals": social_analysis.get("contactSignals") or [],
                        "businessConfidence": social_analysis.get("businessConfidence", 0),
                        "isCommercial": social_analysis.get("isCommercial", False),
                    }
                ] if is_social_profile_url(item["url"]) else [],
                "socialBusinessSignals": social_analysis.get("businessSignals") or [],
                "socialIntentSignals": social_analysis.get("intentSignals") or [],
                "socialDecisionRole": social_analysis.get("decisionRole", ""),
                "socialBusinessConfidence": social_analysis.get("businessConfidence", 0),
                "accountType": item.get("account_type", "公司客户"),
                "isDuplicate": False,
                "isCompetitor": is_competitor,
                "confidence": confidence,
                "confidenceLabel": confidence_label,
                "sourceCoverage": {
                    "total": evidence_source_count,
                    "official": official_source_count,
                    "independentDomains": max(1, len(source_domains)),
                    "contactable": contactable,
                    "contactEntry": has_contact_entry,
                    "contactEntryUrl": official_contact_entry_url,
                    "websiteReachable": bool(website_audit.get("reachable")),
                    "websiteVehicleRelated": bool(website_audit.get("vehicleRelated")),
                    "websiteAuditReason": website_audit.get("reason", ""),
                    "missingFields": [
                        field
                        for field, present in (
                            ("官网", bool(customer_website)),
                            ("官网可打开", bool(website_audit.get("reachable")) if website_audit.get("url") else True),
                            ("官网车辆相关", bool(website_audit.get("vehicleRelated")) if website_audit.get("url") else True),
                            ("邮箱", bool(email_sources)),
                            ("电话", bool(phone_sources)),
                            ("联系人", bool(contacts["contact_name"])),
                            ("社媒账号", bool(contacts["social_accounts"])),
                        )
                        if not present
                    ],
                    "decision": source_decision,
                },
                "acquisitionPriority": acquisition_priority,
                "searchPolicy": {
                    "verificationLevel": verification_level,
                    "minimumIndependentSources": min_sources,
                    "emailMustBeVerified": verification_level == "strict",
                    "resultLimit": result_limit,
                },
                "recommendedModels": recommended_models,
                "aiReview": ai_review,
                "autoImportEligible": auto_import_eligible,
                "businessSignals": business_signals,
                "intentSignals": intent_signals,
                "contactReason": contact_reason,
                "sourceTranslation": source_translation,
                "googleRating": item.get("google_rating", 0),
                "googleReviews": item.get("google_reviews", 0),
                "businessStatus": item.get("business_status", ""),
                "model": model,
                "score": score,
                "baseScore": score,
                "scoreModelVersion": 11,
                "scoreTier": score_tier,
                "scoreDimensions": score_dimensions,
                "scoreBreakdown": score_breakdown,
                "scoreBasis": "100分线索模型：汽车业务20、地区匹配20、联系方式15、官网10、中国新能源10、华为系列10、进口分销8、经营活跃4、决策人3，另计风险扣分",
                "stage": "准备联系" if score >= 80 else "待审核",
                "next": "生成英文开发信并人工确认",
                "website": combined[:1000],
                "reason": reason,
            }
        )
    pipeline_stats["qualifiedBeforeMerge"] = len(leads)
    if source_mode == "social" and not leads:
        notice = (
            f"五平台共执行 {social_search_stats['queries']} 组短词搜索，"
            f"搜索引擎返回 {social_search_stats['rawResults']} 条，"
            f"企业官网反向发现 {social_search_stats['officialWebsiteProfiles']} 个社媒账号，"
            f"其中 {social_search_stats['profileResults']} 条为账号主页，"
            f"{social_search_stats['acceptedResults']} 条通过商业账号初筛。"
            "若仍为 0，通常是搜索引擎未收录当地账号；可改用单个平台搜索或本机 Chrome 登录态采集。"
        )
    if source_mode in platform_queries and not leads and not notice:
        source_label = platform_queries[source_mode][1]
        notice = (
            f"{source_label} 执行 {social_search_stats['queries']} 组查询，"
            f"公开搜索返回 {social_search_stats['rawResults']} 条，"
            f"Apify 返回 {social_search_stats['apifyResults']} 条，"
            f"其中 {social_search_stats['profileResults']} 条可识别为账号主页，"
            f"最终 {social_search_stats['acceptedResults']} 条通过地区与汽车业务核验。"
            "这表示本轮源头没有返回可用账号，并不是线索已被客户池过滤；建议换 Instagram/LinkedIn，或先用综合搜索找到官网后再反查社媒。"
        )
    if excluded_brand_bound_dealers:
        notice = (notice + " " if notice else "") + f"已排除 {excluded_brand_bound_dealers} 家已绑定主机厂的单品牌 4S/授权店。"
    if freshness_days and source_mode in ("social", "youtube", "instagram", "facebook", "tiktok", "linkedin") and not leads and not notice:
        notice = f"没有找到可确认发布日期且在最近 {freshness_days} 天内的线索。可以放宽到 30 天，或更换 Instagram、Facebook、LinkedIn 来源。"
    if source_mode == "google" and not leads and not notice:
        notice = "Google Maps 没有返回符合条件的企业，请调整中文目标描述或目标国家。"
    merged_leads: dict[str, dict] = {}
    for lead in leads:
        company_key = re.sub(r"[^a-z0-9]+", "", str(lead.get("company", "")).lower())
        if not company_key:
            company_key = normalize_public_url(lead.get("sourceUrl", "")).lower().rstrip("/")
        existing = merged_leads.get(company_key)
        if not existing:
            merged_leads[company_key] = lead
            continue
        existing_sources = existing.setdefault("evidenceSources", [])
        for source in lead.get("evidenceSources", []):
            if source.get("url") and not any(item.get("url") == source.get("url") for item in existing_sources):
                existing_sources.append(source)
        existing["sourceCoverage"]["total"] = len(existing_sources)
        # Prefer the version that is easiest for sales to verify and contact.
        existing_contactable = bool(existing.get("email") or existing.get("phone") or existing.get("whatsapp"))
        lead_contactable = bool(lead.get("email") or lead.get("phone") or lead.get("whatsapp"))
        existing_has_website = bool(existing.get("customerWebsite"))
        lead_has_website = bool(lead.get("customerWebsite"))
        if (
            (lead_contactable and not existing_contactable)
            or (lead_has_website and not existing_has_website)
            or int(lead.get("score", 0)) > int(existing.get("score", 0))
        ):
            lead["evidenceSources"] = existing_sources
            lead["sourceCoverage"]["total"] = len(existing_sources)
            merged_leads[company_key] = lead
    leads = list(merged_leads.values())
    pipeline_stats["afterEntityMerge"] = len(leads)

    def lead_sales_priority(item: dict) -> tuple:
        coverage = item.get("sourceCoverage") or {}
        evidence_sources = item.get("evidenceSources") or []
        contactable = bool(
            item.get("email")
            or item.get("phone")
            or item.get("whatsapp")
            or coverage.get("contactable")
        )
        has_website = bool(item.get("customerWebsite"))
        official_sources = int(coverage.get("official") or 0)
        source_total = int(coverage.get("total") or len(evidence_sources) or 0)
        confidence = int(item.get("confidence") or 0)
        score = int(item.get("score") or 0)
        return (
            -int(contactable),
            -int(has_website),
            -official_sources,
            -source_total,
            -confidence,
            -score,
            str(item.get("company") or ""),
        )

    leads.sort(key=lead_sales_priority)
    leads = limit_duplicate_customer_websites(leads)
    leads = leads[:target_max]
    pipeline_stats["final"] = len(leads)
    if len(leads) < target_min:
        target_notice = (
            f"本轮目标为 {target_min}-{target_max} 条真实线索，"
            f"当前仅有 {len(leads)} 条通过地区、汽车商业身份和 AI 证据审核；未使用低质量数据补足。"
        )
        notice = f"{notice} {target_notice}".strip()
    return {
        "ok": True,
        "count": len(leads),
        "leads": leads,
        "notice": notice,
        "stats": {
            "social": social_search_stats,
            "pipeline": pipeline_stats,
            "qualifiedTarget": {
                "min": target_min,
                "max": target_max,
                "actual": len(leads),
            },
        },
    }


def compact_text(value, limit: int = 2000) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit]


def normalize_website_lead(payload: dict, client_ip: str = "", user_agent: str = "") -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Invalid website lead payload")
    if compact_text(payload.get("websiteCheck"), 200):
        raise ValueError("Invalid submission")
    company = compact_text(payload.get("name") or payload.get("company"), 160)
    contact = compact_text(payload.get("contact"), 180)
    country = compact_text(payload.get("country"), 180)
    detected_country = compact_text(payload.get("detectedCountry"), 8).upper()
    detected_language = compact_text(payload.get("detectedLanguage"), 12).lower()
    language_source = compact_text(payload.get("languageSource"), 20).lower()
    model_line = compact_text(payload.get("modelLine") or payload.get("model-line") or payload.get("target"), 120)
    buyer_type = compact_text(payload.get("buyerType"), 40)
    model_version = compact_text(payload.get("modelVersion"), 160)
    purchase_timeline = compact_text(payload.get("purchaseTimeline"), 40)
    trade_term = compact_text(payload.get("tradeTerm"), 40).upper()
    privacy_consent = compact_text(payload.get("privacyConsent"), 10).lower()
    quantity_text = compact_text(payload.get("quantity"), 40)
    message = compact_text(payload.get("message"), 2000)
    if not company:
        raise ValueError("Name or company is required")
    if not contact:
        raise ValueError("Email or WhatsApp is required")
    if not country:
        raise ValueError("Country or destination port is required")
    if privacy_consent != "yes":
        raise ValueError("Privacy consent is required")
    try:
        quantity = max(1, min(9999, int(float(quantity_text or 1))))
    except (TypeError, ValueError):
        quantity = 1
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    email = contact if re.search(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", contact) else ""
    whatsapp = contact if not email else ""
    model = "尊界 S800" if "ZUNJIE" in model_line.upper() or "尊界" in model_line else (
        "问界 M9" if "AITO" in model_line.upper() or "问界" in model_line else model_line or "其他车型"
    )
    return {
        "id": f"site-{uuid.uuid4().hex[:12]}",
        "company": company,
        "contact": contact,
        "email": email,
        "whatsapp": whatsapp,
        "country": country,
        "detectedCountry": detected_country if re.fullmatch(r"[A-Z]{2}", detected_country) else "",
        "detectedLanguage": detected_language if detected_language in {"en", "zh", "ar", "es", "ru", "fr"} else "",
        "languageSource": language_source if language_source in {"manual", "country", "browser"} else "",
        "city": "",
        "modelLine": model_line,
        "buyerType": buyer_type,
        "modelVersion": model_version,
        "purchaseTimeline": purchase_timeline,
        "tradeTerm": trade_term,
        "privacyConsent": True,
        "model": model,
        "quantity": quantity,
        "message": message,
        "source": "Official website",
        "sourceUrl": "https://www.yiming-auto.com/#contact",
        "sourceType": "Official website form",
        "origin": "Official website",
        "status": "new",
        "createdAt": now,
        "receivedAt": now,
        "clientIp": client_ip,
        "userAgent": compact_text(user_agent, 500),
        "reason": f"{company} submitted a website inquiry for {model_line or model} {model_version}, destination {country}, quantity {quantity}, timeline {purchase_timeline}.",
        "website": " ".join(["YIMING AUTO official website inquiry", company, buyer_type, country, model_line, model_version, purchase_timeline, trade_term, message]).strip(),
    }


def save_website_lead(payload: dict, client_ip: str = "", user_agent: str = "") -> dict:
    record = normalize_website_lead(payload, client_ip, user_agent)
    workspace = load_workspace_state(AUTH_USERNAME)
    state = workspace.get("state") or empty_workspace_state()
    website_leads = state.get("websiteLeads")
    if not isinstance(website_leads, list):
        website_leads = []
    duplicate_key = "|".join([
        str(record.get("company") or "").strip().lower(),
        str(record.get("contact") or "").strip().lower(),
        str(record.get("country") or "").strip().lower(),
        str(record.get("message") or "").strip().lower()[:160],
    ])
    for item in website_leads:
        item_key = "|".join([
            str(item.get("company") or "").strip().lower(),
            str(item.get("contact") or "").strip().lower(),
            str(item.get("country") or "").strip().lower(),
            str(item.get("message") or "").strip().lower()[:160],
        ])
        if item_key == duplicate_key:
            return {"lead": item, "duplicate": True}
    state["websiteLeads"] = [record, *website_leads][:5000]
    save_workspace_state(AUTH_USERNAME, state)
    return {"lead": record, "duplicate": False}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def is_authenticated(self):
        return self.current_user() is not None

    def current_user(self):
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        morsel = cookie.get(AUTH_COOKIE)
        return session_user_from_token(morsel.value) if morsel else None

    def require_admin(self):
        user = self.current_user()
        if user and user.get("role") == "admin":
            return user
        self.send_json(403, {"ok": False, "error": "仅管理员可以管理用户"})
        return None

    def client_ip(self):
        direct_ip = self.client_address[0] if self.client_address else ""
        return sanitize_client_ip(
            self.headers.get("X-Forwarded-For")
            or self.headers.get("X-Real-IP")
            or direct_ip
        )

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def require_auth(self, api=False):
        user = self.current_user()
        if user:
            try:
                touch_user_presence(user["username"], self.client_ip(), self.headers.get("User-Agent", ""))
            except (OSError, RuntimeError, sqlite3.Error, ValueError):
                pass
            return True
        if api:
            self.send_json(401, {"ok": False, "error": "请先登录"})
        else:
            self.send_response(302)
            self.send_header("Location", "/login.html")
            self.end_headers()
        return False

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/health":
            body = json.dumps(
                {"ok": True, "service": "overseas-lead-workbench"},
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/admin_settings.json":
            self.send_json(404, {"ok": False, "error": "Not found"})
            return
        if parsed.path == "/api/session":
            user = self.current_user()
            if user:
                try:
                    touch_user_presence(user["username"], self.client_ip(), self.headers.get("User-Agent", ""))
                except (OSError, RuntimeError, sqlite3.Error, ValueError):
                    pass
            self.send_json(
                200,
                {
                    "ok": True,
                    "authenticated": bool(user),
                    "username": user.get("username", "") if user else "",
                    "displayName": user.get("displayName", "") if user else "",
                    "role": user.get("role", "") if user else "",
                    "assignedCountries": user.get("assignedCountries", []) if user else [],
                    "discoveryAdminOnly": bool(control_value("discovery", "adminOnly", False)),
                },
            )
            return
        if parsed.path == "/api/discovery-sources":
            if not self.require_auth(api=True):
                return
            google_ready = bool(get_google_maps_api_key())
            youtube_ready = bool(get_youtube_api_key())
            brave_ready = bool(get_brave_search_api_key())
            serpapi_ready = bool(get_serpapi_api_key())
            hunter_ready = bool(get_hunter_api_key())
            apify_ready = bool(get_apify_api_token())
            self.send_json(200, {
                "ok": True,
                "sources": {
                    "googleMaps": {
                        "available": google_ready,
                        "label": "Google Maps Places API",
                        "message": "已连接官方企业数据" if google_ready else "未配置 API Key，综合搜索将跳过 Google Maps"
                    },
                    "web": {
                        "available": True,
                        "label": "Bing + DuckDuckGo + Brave",
                        "message": "Brave Search API / SerpApi 已加入" if (brave_ready or serpapi_ready) else "未配置搜索 API Key，将使用公开搜索兜底"
                    },
                    "braveSearch": {
                        "available": brave_ready,
                        "label": "Brave Search API",
                        "message": "已连接官方 Web Search API" if brave_ready else "未配置 BRAVE_SEARCH_API_KEY"
                    },
                    "serpapi": {
                        "available": serpapi_ready,
                        "label": "SerpApi",
                        "message": "已连接 Google Search 补充源" if serpapi_ready else "未配置 SERPAPI_API_KEY"
                    },
                    "hunter": {
                        "available": hunter_ready,
                        "label": "Hunter.io",
                        "message": "已连接邮箱候选补充" if hunter_ready else "未配置 HUNTER_API_KEY"
                    },
                    "apify": {
                        "available": apify_ready,
                        "label": "Apify Actors",
                        "message": "已连接 Apify，可作为社媒 Actor 补充源" if apify_ready else "未配置 APIFY_API_TOKEN"
                    },
                    "maps": {"available": True, "label": "OpenStreetMap"},
                    "youtube": {
                        "available": youtube_ready,
                        "label": "YouTube Data API v3",
                        "message": "已连接 YouTube 官方搜索 API" if youtube_ready else "未配置 YOUTUBE_API_KEY，将使用公开页面兜底搜索"
                    },
                    "social": {"available": True, "label": "公开社媒搜索"}
                }
            })
            return
        if parsed.path == "/api/users":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                self.send_json(200, {"ok": True, "users": list_users()})
            except (OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path.startswith("/api/users/") and parsed.path.endswith("/activity"):
            if not self.require_auth(api=True) or not self.require_admin():
                return
            username = urllib.parse.unquote(parsed.path.split("/")[-2])
            try:
                user = get_user(username)
                if not user or user.get("hidden"):
                    self.send_json(404, {"ok": False, "error": "用户不存在"})
                    return
                purge_hidden_admin_tracking()
                presence = presence_payload(username, user, presence_rows_by_user().get(username))
                operation_events = list_user_audit_events(username, 80)
                login_events = [{
                    "id": f"login-{event.get('id', '')}",
                    "username": username,
                    "action": "登录系统",
                    "detail": "账号登录",
                    "ip": event.get("ip", ""),
                    "userAgent": event.get("userAgent", ""),
                    "createdAt": event.get("createdAt", ""),
                    "kind": "login",
                } for event in list_login_events(username, 80)]
                events = sorted(
                    [*operation_events, *login_events],
                    key=lambda event: str(event.get("createdAt") or ""),
                    reverse=True,
                )[:80]
                self.send_json(200, {
                    "ok": True,
                    "user": {key: value for key, value in user.items() if key != "passwordHash"},
                    "presence": presence,
                    "events": events,
                })
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/kpi":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                self.send_json(200, {"ok": True, **load_admin_kpi_summary()})
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/discovery-distribution-preview":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                self.send_json(200, {
                    "ok": True,
                    **prepare_discovery_distribution(
                        execute=False,
                        distributed_by=self.current_user()["username"],
                    ),
                })
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/settings":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                self.send_json(200, {"ok": True, **admin_settings_payload()})
            except (OSError, ValueError) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/apify-usage":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                self.send_json(200, {"ok": True, **apify_usage_payload()})
            except (OSError, ValueError, RuntimeError, TimeoutError, urllib.error.URLError, http.client.HTTPException) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/api-consumption":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                self.send_json(200, {"ok": True, **api_consumption_payload()})
            except (OSError, ValueError, RuntimeError, TimeoutError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/operations":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                self.send_json(200, {"ok": True, **admin_operations_payload()})
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/backup":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                backup = build_business_backup()
                update_last_backup_time()
                record_admin_audit(self.current_user()["username"], "导出业务备份", f"工作区 {len(backup['workspaces'])} 个", self.client_ip())
                body = json.dumps(backup, ensure_ascii=False, indent=2).encode("utf-8")
                filename = f"hima-backup-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/login-events":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                query = urllib.parse.parse_qs(parsed.query)
                show_all = (query.get("all") or ["0"])[0] == "1"
                purge_hidden_admin_tracking()
                events = list_login_events("", 80 if show_all else 3)
                accounts = list_account_presence()
                self.send_json(200, {
                    "ok": True,
                    "eventsLimit": 80 if show_all else 3,
                    "showAll": show_all,
                    "accounts": accounts,
                    "onlineCount": sum(1 for account in accounts if account.get("online")),
                    "events": events,
                    "uniqueIpCount": len({event.get("ip") for event in events if event.get("ip")}),
                })
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/workspace-state":
            if not self.require_auth(api=True):
                return
            try:
                state = load_workspace_state(self.current_user()["username"])
                self.send_json(200, {"ok": True, **state})
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/status":
            if not self.require_auth(api=True):
                return
            job_id = (urllib.parse.parse_qs(parsed.query).get("id") or [""])[0]
            job = get_discovery_job(job_id, self.current_user()["username"])
            if not job:
                self.send_json(404, {"ok": False, "error": "获客任务不存在或已过期"})
                return
            self.send_json(200, {"ok": True, "job": job})
            return
        if parsed.path == "/api/discover/jobs":
            if not self.require_auth(api=True):
                return
            try:
                self.send_json(200, {"ok": True, "jobs": list_discovery_jobs(self.current_user()["username"])})
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/scheduled-jobs":
            if not self.require_auth(api=True) or not self.require_admin():
                return
            try:
                self.send_json(200, {"ok": True, "jobs": list_scheduled_delivery_jobs(5000)})
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/schedules":
            if not self.require_auth(api=True):
                return
            user = self.current_user()
            try:
                schedules = [schedule_public(schedule) for schedule in list_discovery_schedules(user["username"], limit=1000)]
                self.send_json(200, {"ok": True, "schedules": schedules})
            except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})
            return
        if parsed.path in ("/", "/index.html") and not self.require_auth():
            return
        if parsed.path.startswith("/api/") and not self.require_auth(api=True):
            return
        if parsed.path == "/api/social-captures":
            body = json.dumps(
                {"ok": True, "captures": load_social_captures(self.current_user()["username"])},
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/parse-lead-source":
            try:
                result = parse_lead_source(urllib.parse.parse_qs(parsed.query))
                self.send_json(200, result)
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            except (OSError, TimeoutError, UnicodeError, urllib.error.URLError, http.client.HTTPException) as exc:
                self.send_json(502, {"ok": False, "error": f"网址解析失败：{exc}"})
            return
        if parsed.path == "/api/research":
            try:
                result = research_company(urllib.parse.parse_qs(parsed.query))
                body = json.dumps(result, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
            except Exception as exc:
                body = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
                self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/discover":
            try:
                params = urllib.parse.parse_qs(parsed.query)
                ensure_user_can_access_country(self.current_user(), (params.get("country") or ["UAE"])[0])
                result = discover(params)
                body = json.dumps(result, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
            except PermissionError as exc:
                body = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
                self.send_response(403)
            except Exception as exc:  # Keep the browser readable for a local tool.
                body = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
                self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/login":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                username = str(payload.get("username", ""))
                password = str(payload.get("password", ""))
                user = authenticate_user(username, password)
                if not user:
                    self.send_json(401, {"ok": False, "error": "账户名或密码错误"})
                    return
                try:
                    record_login_event(user["username"], self.client_ip(), self.headers.get("User-Agent", ""))
                except (OSError, RuntimeError, sqlite3.Error, ValueError):
                    pass
                token = create_session_token(user["username"])
                body = json.dumps({"ok": True, "username": user["username"], "role": user["role"]}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                secure = "; Secure" if self.headers.get("X-Forwarded-Proto", "").lower() == "https" else ""
                self.send_header(
                    "Set-Cookie",
                    f"{AUTH_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={session_max_age()}{secure}",
                )
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (ValueError, json.JSONDecodeError):
                self.send_json(400, {"ok": False, "error": "登录请求无效"})
            return
        if parsed.path == "/api/logout":
            body = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header(
                "Set-Cookie",
                f"{AUTH_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0",
            )
            self.send_header(
                "Set-Cookie",
                f"{AUTH_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Secure; Max-Age=0",
            )
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/website-leads":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 65_536)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                result = save_website_lead(payload, self.client_ip(), self.headers.get("User-Agent", ""))
                self.send_json(201 if not result.get("duplicate") else 200, {"ok": True, **result})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if not self.require_auth(api=True):
            return
        if parsed.path == "/api/me/password":
            try:
                user = self.current_user()
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                change_own_password(
                    user["username"],
                    str(payload.get("currentPassword") or ""),
                    str(payload.get("newPassword") or ""),
                )
                self.send_json(200, {"ok": True, "message": "密码已修改"})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/users":
            if not self.require_admin():
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                user = create_user(
                    str(payload.get("username", "")),
                    str(payload.get("password", "")),
                    payload.get("role"),
                    payload.get("assignedCountries"),
                    str(payload.get("displayName", "")),
                )
                record_admin_audit(self.current_user()["username"], "创建用户", user["username"], self.client_ip())
                self.send_json(201, {"ok": True, "user": user})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/distribute-discovery-jobs":
            if not self.require_admin():
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                if payload.get("confirm") != "DISTRIBUTE_ADMIN_SEARCHES":
                    raise ValueError("请先预览并确认复制分配")
                result = prepare_discovery_distribution(
                    execute=True,
                    distributed_by=self.current_user()["username"],
                )
                record_admin_audit(
                    self.current_user()["username"],
                    "分配管理员搜索结果",
                    f"复制 {result['totals']['copyJobs']} 个任务、{result['totals']['copyLeads']} 条线索",
                    self.client_ip(),
                )
                self.send_json(200, {"ok": True, **result})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path.startswith("/api/users/"):
            if not self.require_admin():
                return
            username = urllib.parse.unquote(parsed.path.rsplit("/", 1)[-1])
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                if payload.get("action") == "delete":
                    delete_user(username)
                    record_admin_audit(self.current_user()["username"], "删除用户", username, self.client_ip())
                    self.send_json(200, {"ok": True})
                else:
                    user = update_user(
                        username,
                        password=payload.get("password"),
                        status=payload.get("status"),
                        role=payload.get("role"),
                        assigned_countries=payload.get("assignedCountries") if "assignedCountries" in payload else None,
                    )
                    record_admin_audit(self.current_user()["username"], "修改用户", username, self.client_ip())
                    self.send_json(200, {"ok": True, "user": {key: value for key, value in user.items() if key != "passwordHash"}})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/clear-search-data":
            if not self.require_admin():
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                if payload.get("confirm") != "CLEAR_SEARCH_DATA":
                    self.send_json(400, {"ok": False, "error": "缺少清洗确认口令"})
                    return
                result = clear_all_search_data()
                self.send_json(200, {"ok": True, **result})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/prune-search-data":
            if not self.require_admin():
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                if payload.get("confirm") != "PRUNE_SEARCH_DATA":
                    self.send_json(400, {"ok": False, "error": "缺少按日期清理确认口令"})
                    return
                result = prune_search_data_before(str(payload.get("cutoffDate") or ""))
                record_admin_audit(
                    self.current_user()["username"],
                    "按日期清理搜索数据",
                    f"删除 {result['cutoffDate']} 前搜索数据：线索 {result['reviewLeads']}，任务 {result['discoveryJobs']}；客户池未改动",
                    self.client_ip(),
                )
                self.send_json(200, {"ok": True, **result})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/clean-stale-youtube":
            if not self.require_admin():
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                if payload.get("confirm") != "CLEAN_STALE_YOUTUBE":
                    self.send_json(400, {"ok": False, "error": "缺少清理确认口令"})
                    return
                result = clean_stale_youtube_leads()
                self.send_json(200, {"ok": True, **result})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/settings":
            if not self.require_admin():
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 65_536)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                current_settings = load_admin_settings_file()
                next_settings = normalize_admin_settings(payload)
                restart_changed = any(
                    str(current_settings.get(key, os.environ.get(key, "")) or "").strip()
                    != str(next_settings.get(key, os.environ.get(key, "")) or "").strip()
                    for key in ("NETWORK_DEFAULT_TIMEOUT",)
                )
                with ADMIN_SETTINGS_LOCK:
                    save_admin_settings_file(next_settings)
                if "DISCOVERY_MAX_CONCURRENCY" in next_settings:
                    DISCOVERY_WORKER_GATE.set_limit(int(next_settings["DISCOVERY_MAX_CONCURRENCY"]))
                record_admin_audit(self.current_user()["username"], "保存系统设置", "API、获客、质量、AI、数据和安全配置", self.client_ip())
                self.send_json(
                    200,
                    {
                        "ok": True,
                        **admin_settings_payload(),
                        "restartRequiredChanged": restart_changed,
                        "runtimeUpdated": ["DISCOVERY_MAX_CONCURRENCY"],
                    },
                )
            except (ValueError, json.JSONDecodeError, OSError) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/operations":
            user = self.require_admin()
            if not user:
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 65_536)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                action = str(payload.get("action") or "")
                if action == "cancel-active-jobs":
                    result = {"canceled": cancel_all_active_jobs()}
                    detail = f"终止 {result['canceled']} 个任务"
                elif action == "clear-failed-jobs":
                    result = {"removed": clean_discovery_job_history(failed_only=True)}
                    detail = f"清理 {result['removed']} 个失败任务"
                elif action == "clean-old-jobs":
                    result = {"removed": clean_discovery_job_history(retention_days=int(payload.get("days") or control_value("data", "jobRetentionDays", 30)))}
                    detail = f"清理 {result['removed']} 个过期任务"
                elif action in {"clear-tombstones", "clear-rejected-memory", "deduplicate"}:
                    if payload.get("confirm") != action:
                        raise ValueError("缺少危险操作确认")
                    result = mutate_all_workspaces(action)
                    detail = f"{action}: {result['removed']} 条"
                elif action == "force-logout":
                    if payload.get("confirm") != "force-logout":
                        raise ValueError("缺少强制下线确认")
                    result = {"invalidBefore": force_logout_all_sessions()}
                    detail = "强制所有账号重新登录"
                elif action == "test-source":
                    result = test_admin_source(str(payload.get("source") or ""))
                    detail = f"测试来源 {result['source']}: {result['message']}"
                else:
                    raise ValueError("未知管理操作")
                record_admin_audit(user["username"], action, detail, self.client_ip())
                self.send_json(200, {"ok": True, **result})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/restore-backup":
            user = self.require_admin()
            if not user:
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 20_500_000)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                result = restore_business_backup(payload)
                record_admin_audit(user["username"], "恢复业务备份", f"恢复 {result['workspacesRestored']} 个工作区", self.client_ip())
                self.send_json(200, {"ok": True, **result})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/admin/restart":
            if not self.require_admin():
                return
            self.send_json(200, {"ok": True, "message": "服务器正在重启，请稍后刷新页面"})
            restart_server_process()
            return
        if parsed.path == "/api/admin/migrate-legacy":
            user = self.require_admin()
            if not user:
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length else {}
                result = migrate_from_remote_workbench(
                    str(payload.get("baseUrl") or "https://overseas-lead-workbench.onrender.com"),
                    str(payload.get("username") or ""),
                    str(payload.get("password") or ""),
                    user["username"],
                )
                self.send_json(200, {"ok": True, **result})
            except (ValueError, json.JSONDecodeError, OSError, urllib.error.URLError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/workspace-state":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 20_500_000)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                expected_version = payload.get("expectedVersion")
                if expected_version is not None:
                    expected_version = int(expected_version)
                username = self.current_user()["username"]
                previous_state = load_workspace_state(username).get("state", {})
                result = save_workspace_state(
                    username, payload.get("state", payload),
                    expected_version=expected_version,
                )
                for action, detail in workspace_operation_events(previous_state, result.get("state", {})):
                    record_admin_audit(username, action, detail, self.client_ip())
                self.send_json(200, {"ok": True, **result})
            except WorkspaceVersionConflict as exc:
                self.send_json(
                    409,
                    {
                        "ok": False,
                        "conflict": True,
                        "error": str(exc),
                        "current": exc.current,
                    },
                )
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/start":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 65_536)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("请求格式无效")
                ensure_user_can_use_discovery_payload(self.current_user(), payload)
                username = self.current_user()["username"]
                job = create_discovery_job(payload, username)
                detail_parts = [
                    clean_text(str(payload.get("country") or payload.get("targetCountry") or "未知地区")),
                    clean_text(str(payload.get("sourceMode") or payload.get("source") or "综合搜索")),
                    clean_text(str(payload.get("model") or "")),
                ]
                record_admin_audit(username, "启动一键获客", " · ".join(part for part in detail_parts if part), self.client_ip())
                self.send_json(202, {"ok": True, "job": job})
            except PermissionError as exc:
                self.send_json(403, {"ok": False, "error": str(exc)})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/schedules":
            if not self.require_auth(api=True):
                return
            user = self.current_user()
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 65_536)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("请求格式无效")
                action = str(payload.get("action") or "save")
                if action == "save" and not payload.get("payload") and ("runTime" in payload or "sourceMode" in payload):
                    action = "save_all_sales"
                if action == "delete":
                    schedule_id = str(payload.get("id", ""))
                    if not delete_discovery_schedule(schedule_id, user["username"]):
                        self.send_json(404, {"ok": False, "error": "定时计划不存在"})
                        return
                    self.send_json(200, {"ok": True, "id": schedule_id})
                    return
                if action == "bulk_set_enabled":
                    if user.get("role") != "admin":
                        raise PermissionError("只有管理员可以批量控制后台抓取计划")
                    target_username = str(payload.get("targetUsername") or "")
                    updated_count = set_sales_discovery_schedules_enabled(
                        user["username"], target_username, bool(payload.get("enabled"))
                    )
                    record_admin_audit(
                        user["username"],
                        "批量启动定时获客" if payload.get("enabled") else "批量暂停定时获客",
                        f"{target_username} · {updated_count} 个计划",
                        self.client_ip(),
                    )
                    self.send_json(200, {"ok": True, "updatedCount": updated_count})
                    return
                if action == "save_all_sales":
                    if user.get("role") != "admin":
                        raise PermissionError("只有管理员可以创建全员定时获客计划")
                    result = create_all_sales_discovery_schedules(payload, user["username"])
                    record_admin_audit(
                        user["username"],
                        "开启全体销售定时获客",
                        f"{payload.get('sourceMode', 'combined')} · 每天 {result['runTime']} · {result['salesCount']} 名销售 · {result['scheduleCount']} 个地区任务",
                        self.client_ip(),
                    )
                    self.send_json(200, {"ok": True, **result})
                    return
                schedule_request = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
                ensure_user_can_use_discovery_payload(user, schedule_request)
                schedule = create_or_update_discovery_schedule(payload, user["username"])
                self.send_json(200, {"ok": True, "schedule": schedule})
            except PermissionError as exc:
                self.send_json(403, {"ok": False, "error": str(exc)})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/mark-imported":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                def optional_count(value):
                    if value is None or value == "":
                        return None
                    return int(value)

                job = mark_discovery_job_imported(
                    str(payload.get("id", "")),
                    self.current_user()["username"],
                    optional_count(payload.get("importedCount")),
                    optional_count(payload.get("rawCount")),
                    optional_count(payload.get("skippedCount")),
                    payload.get("skipBreakdown"),
                )
                if not job:
                    self.send_json(404, {"ok": False, "error": "获客任务不存在"})
                    return
                self.send_json(200, {"ok": True, "job": job})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/retry":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                previous = load_discovery_job(str(payload.get("id", "")), self.current_user()["username"])
                if not previous:
                    self.send_json(404, {"ok": False, "error": "获客任务不存在"})
                    return
                if previous.get("status") not in {"failed", "completed", "canceled"}:
                    self.send_json(409, {"ok": False, "error": "任务仍在运行，无需重试"})
                    return
                ensure_user_can_use_discovery_payload(self.current_user(), previous.get("payload") or {})
                job = create_discovery_job(previous.get("payload") or {}, self.current_user()["username"], force=True)
                self.send_json(202, {"ok": True, "job": job})
            except PermissionError as exc:
                self.send_json(403, {"ok": False, "error": str(exc)})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/cancel":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                job = cancel_discovery_job(str(payload.get("id", "")), self.current_user()["username"])
                if not job:
                    self.send_json(404, {"ok": False, "error": "获客任务不存在"})
                    return
                self.send_json(200, {"ok": True, "job": job})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/delete":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                job_id = str(payload.get("id", ""))
                if not delete_discovery_job(job_id, self.current_user()["username"]):
                    self.send_json(404, {"ok": False, "error": "获客任务不存在"})
                    return
                self.send_json(200, {"ok": True, "id": job_id})
            except json.JSONDecodeError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            except ValueError as exc:
                self.send_json(409, {"ok": False, "error": str(exc)})
            except (OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path != "/api/social-capture":
            self.send_error(404)
            return
        try:
            content_length = min(int(self.headers.get("Content-Length", "0")), 10_000_000)
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            record = save_social_capture(payload, self.current_user()["username"])
            body = json.dumps({"ok": True, "capture": record}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
        except Exception as exc:
            body = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def resume_discovery_jobs_in_background() -> None:
    try:
        resumed_jobs = resume_interrupted_discovery_jobs()
        if resumed_jobs:
            print(f"已恢复 {resumed_jobs} 个中断的获客任务。")
    except Exception as exc:
        print(f"恢复中断获客任务失败：{exc}")


if __name__ == "__main__":
    initialize_state_store()
    start_discovery_scheduler()
    with ReusableThreadingTCPServer((HOST, PORT), Handler) as httpd:
        display_host = "127.0.0.1" if HOST == "0.0.0.0" else HOST
        print(f"获客工作台已启动：http://{display_host}:{PORT}/index.html")
        threading.Thread(
            target=resume_discovery_jobs_in_background,
            name="discovery-resume",
            daemon=True,
        ).start()
        httpd.serve_forever()

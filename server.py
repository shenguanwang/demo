from __future__ import annotations

import html
import binascii
import hashlib
import hmac
import json
import os
import re
import secrets
import socketserver
import base64
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path


PORT = int(os.environ.get("PORT") or os.environ.get("LEAD_TOOL_PORT", "8815"))
HOST = os.environ.get("LEAD_TOOL_HOST", "127.0.0.1")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")
ROOT = Path(__file__).resolve().parent
GOOGLE_MAPS_KEY_FILE = ROOT / "google_maps_api_key.txt"
SOCIAL_CAPTURE_DIR = ROOT / "social-captures"
SOCIAL_CAPTURE_FILE = SOCIAL_CAPTURE_DIR / "captures.json"
SOCIAL_CAPTURE_LOCK = threading.Lock()
DISCOVERY_JOBS: dict[str, dict] = {}
DISCOVERY_JOBS_LOCK = threading.Lock()
DISCOVERY_JOB_TTL = 60 * 60
AUTH_USERNAME = os.environ.get("APP_USERNAME", "admin")
AUTH_PASSWORD = os.environ.get("APP_PASSWORD", "admin123")
AUTH_SECRET = os.environ.get("APP_AUTH_SECRET") or secrets.token_hex(32)
AUTH_COOKIE = "hima_session"
AUTH_MAX_AGE = 60 * 60 * 24 * 7


def create_session_token(username: str) -> str:
    expires_at = int(datetime.now(timezone.utc).timestamp()) + AUTH_MAX_AGE
    payload = f"{username}|{expires_at}"
    signature = hmac.new(
        AUTH_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode("utf-8")).decode("ascii")


def verify_session_token(token: str) -> bool:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        username, expires_at, signature = decoded.rsplit("|", 2)
        payload = f"{username}|{expires_at}"
        expected = hmac.new(
            AUTH_SECRET.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return (
            hmac.compare_digest(signature, expected)
            and username == AUTH_USERNAME
            and int(expires_at) > int(datetime.now(timezone.utc).timestamp())
        )
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
        return False


def cleanup_discovery_jobs() -> None:
    cutoff = datetime.now(timezone.utc).timestamp() - DISCOVERY_JOB_TTL
    with DISCOVERY_JOBS_LOCK:
        expired = [
            job_id
            for job_id, job in DISCOVERY_JOBS.items()
            if float(job.get("updatedAtTimestamp", 0)) < cutoff
        ]
        for job_id in expired:
            DISCOVERY_JOBS.pop(job_id, None)


def update_discovery_job(job_id: str, **changes) -> None:
    now = datetime.now(timezone.utc)
    with DISCOVERY_JOBS_LOCK:
        job = DISCOVERY_JOBS.get(job_id)
        if not job:
            return
        job.update(changes)
        job["updatedAt"] = now.isoformat(timespec="seconds")
        job["updatedAtTimestamp"] = now.timestamp()


def run_discovery_job(job_id: str, params: dict[str, list[str]]) -> None:
    update_discovery_job(
        job_id,
        status="running",
        stage="search",
        progress=12,
        message="云端正在检索地图、企业官网、行业目录和公开社媒来源。",
    )
    try:
        result = discover(params)
        update_discovery_job(
            job_id,
            status="completed",
            stage="done",
            progress=100,
            message=f"云端搜索完成，共发现 {result.get('count', 0)} 条线索。",
            result=result,
        )
    except Exception as exc:
        update_discovery_job(
            job_id,
            status="failed",
            stage="done",
            progress=100,
            message="云端获客任务执行失败。",
            error=str(exc),
        )


def create_discovery_job(payload: dict) -> dict:
    cleanup_discovery_jobs()
    allowed_fields = {
        "goal",
        "country",
        "model",
        "sourceMode",
        "accountScope",
        "freshness",
        "keywords",
        "cityFocus",
        "customerTypes",
        "exclusions",
        "resultLimit",
        "verificationLevel",
        "minSources",
    }
    params = {
        key: [str(value)[:4000]]
        for key, value in payload.items()
        if key in allowed_fields and value is not None
    }
    job_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    job = {
        "id": job_id,
        "status": "queued",
        "stage": "search",
        "progress": 5,
        "message": "云端任务已创建，正在分配搜索资源。",
        "createdAt": now.isoformat(timespec="seconds"),
        "updatedAt": now.isoformat(timespec="seconds"),
        "updatedAtTimestamp": now.timestamp(),
    }
    with DISCOVERY_JOBS_LOCK:
        DISCOVERY_JOBS[job_id] = job
    worker = threading.Thread(
        target=run_discovery_job,
        args=(job_id, params),
        name=f"discovery-{job_id[:8]}",
        daemon=True,
    )
    worker.start()
    return job.copy()


def get_discovery_job(job_id: str) -> dict | None:
    cleanup_discovery_jobs()
    with DISCOVERY_JOBS_LOCK:
        job = DISCOVERY_JOBS.get(job_id)
        if not job:
            return None
        return {
            key: value
            for key, value in job.items()
            if key != "updatedAtTimestamp"
        }


COUNTRY_HINTS = {
    "UAE": ("Dubai", "Jebel Ali", "Abu Dhabi", "Sharjah"),
    "Saudi": ("Riyadh", "Jeddah", "Dammam"),
    "Kazakhstan": ("Almaty", "Astana", "Aktau"),
    "Russia": ("Moscow", "St. Petersburg"),
    "Qatar": ("Doha",),
    "Kuwait": ("Kuwait City",),
    "Uzbekistan": ("Tashkent",),
    "Azerbaijan": ("Baku",),
}

CITY_COORDS = {
    "UAE": ("Dubai", 25.2048, 55.2708),
    "Saudi": ("Riyadh", 24.7136, 46.6753),
    "Kazakhstan": ("Almaty", 43.2389, 76.8897),
    "Russia": ("Moscow", 55.7558, 37.6173),
    "Qatar": ("Doha", 25.2854, 51.5310),
    "Kuwait": ("Kuwait City", 29.3759, 47.9774),
    "Uzbekistan": ("Tashkent", 41.2995, 69.2401),
    "Azerbaijan": ("Baku", 40.4093, 49.8671),
}

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
    "youtube.com",
    "youtu.be",
    "google.com",
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
        raw = response.read(600_000)
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
        raw = response.read(1_200_000)
        charset = response.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="ignore"), response.geturl()


def clean_text(value: str) -> str:
    value = re.sub(r"<script[\s\S]*?</script>", " ", value, flags=re.I)
    value = re.sub(r"<style[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def load_social_captures() -> list[dict]:
    if not SOCIAL_CAPTURE_FILE.exists():
        return []
    try:
        data = json.loads(SOCIAL_CAPTURE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_social_capture(payload: dict) -> dict:
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
                public_base = PUBLIC_BASE_URL or f"http://127.0.0.1:{PORT}"
                screenshot_url = f"{public_base}/social-captures/{capture_id}.png"
        except (ValueError, OSError):
            screenshot_url = ""
    record = {
        "id": capture_id,
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
        captures = load_social_captures()
        captures.insert(0, record)
        SOCIAL_CAPTURE_FILE.write_text(
            json.dumps(captures[:200], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return record


def normalize_public_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith("//"):
        return "https:" + value
    if not re.match(r"^https?://", value, flags=re.I):
        return "https://" + value.lstrip("/")
    return value


def is_social_profile_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower().removeprefix("www.")
    parts = [part for part in parsed.path.split("/") if part]
    if "instagram.com" in domain:
        return len(parts) == 1 and parts[0].lower() not in {"p", "reel", "stories", "explore"}
    if "facebook.com" in domain:
        return len(parts) == 1 and parts[0].lower() not in {"posts", "photos", "watch", "share"}
    if "linkedin.com" in domain:
        return len(parts) >= 2 and parts[0].lower() in {"company", "in"}
    if "youtube.com" in domain:
        return bool(parts) and (parts[0].startswith("@") or parts[0].lower() in {"user", "channel", "c"})
    return "tiktok.com" in domain and bool(parts) and parts[0].startswith("@")


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
    domain = urllib.parse.urlparse(url).netloc.lower()
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
    return "社交媒体"


def read_social_profile(
    url: str,
    account_type: str = "公司账号",
    relationship: str = "公开搜索",
) -> dict:
    url = normalize_public_url(url)
    platform = social_platform(url)
    parsed = urllib.parse.urlparse(url)
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
    try:
        page, final_url = fetch_document(url, timeout=18, user_agent=user_agent)
        meta = parse_meta_tags(page)
        title = meta.get("og:title") or meta.get("twitter:title") or title
        description = (
            meta.get("og:description")
            or meta.get("twitter:description")
            or meta.get("description")
            or ""
        )
        if platform == "YouTube":
            title = meta.get("og:title") or title
            description = meta.get("og:description") or meta.get("description") or description
    except (OSError, TimeoutError, UnicodeError):
        pass
    if not description:
        description = "平台未向匿名访问返回公开简介，请打开原始主页人工核验。"
    return {
        "platform": platform,
        "accountType": account_type,
        "relationship": relationship,
        "title": clean_text(title)[:180],
        "description": clean_text(description)[:700],
        "url": final_url,
        "handle": handle[:120],
    }


def search_youtube_channels(query: str, limit: int = 5) -> list[dict]:
    url = "https://www.youtube.com/results?" + urllib.parse.urlencode({"search_query": query})
    page, _ = fetch_document(url, timeout=25)
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", page, flags=re.S)
    if not match:
        return []
    data = json.loads(match.group(1))
    renderers = []

    def walk(value):
        if isinstance(value, dict):
            if "channelRenderer" in value:
                renderers.append(value["channelRenderer"])
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(data)
    results = []
    for channel in renderers:
        channel_id = channel.get("channelId", "")
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
                "handle": text_from_runs(channel.get("subscriberCountText")),
                "channelId": channel_id,
            }
        )
        if len(results) >= limit:
            break
    return results


def search_bing(query: str, limit: int = 8, freshness_days: int | None = None) -> list[dict]:
    params = {"q": query, "count": limit}
    if freshness_days:
        params["filters"] = 'ex1:"ez2"' if freshness_days <= 7 else 'ex1:"ez3"'
    url = "https://www.bing.com/search?" + urllib.parse.urlencode(params)
    page = fetch_text(url)
    items: list[dict] = []
    for match in re.finditer(r'<li class="b_algo"[\s\S]*?</li>', page, flags=re.I):
        block = match.group(0)
        link = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', block, flags=re.I)
        if not link:
            continue
        href = html.unescape(link.group(1))
        title = clean_text(link.group(2))
        snippet_match = re.search(r'<p[^>]*>([\s\S]*?)</p>', block, flags=re.I)
        snippet = clean_text(snippet_match.group(1)) if snippet_match else ""
        if href.startswith("http") and "bing.com" not in href:
            items.append({"title": title, "url": href, "snippet": snippet})
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
        parsed_redirect = urllib.parse.urlparse(href)
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
        if href.startswith("http"):
            items.append({"title": title, "url": href, "snippet": snippet})
        if len(items) >= limit:
            break
    return items


def search_web(query: str, limit: int = 8, freshness_days: int | None = None) -> list[dict]:
    results = search_duckduckgo(query, limit, freshness_days)
    if len(results) >= min(3, limit):
        return results
    return results + search_bing(query, limit - len(results), freshness_days)


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
    relative = re.search(r"\b(\d+)\s+(hour|day)s?\s+ago\b", value, flags=re.I)
    if relative:
        amount = int(relative.group(1))
        delta = timedelta(hours=amount) if relative.group(2).lower() == "hour" else timedelta(days=amount)
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


def source_details(url: str, fallback_origin: str = "公开网页搜索") -> tuple[str, str]:
    domain = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
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
    if domain:
        return domain, "车商官网或汽车行业网站"
    return fallback_origin, "公开商业信息网站"


def source_category(url: str, title: str = "", snippet: str = "") -> tuple[str, str]:
    value = f"{url} {title} {snippet}".lower()
    domain = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
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
    if "社交媒体" in source_type or any(name in value for name in ("facebook", "instagram", "tiktok", "youtube")):
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


def official_site_pages(website: str) -> list[dict]:
    website = normalize_public_url(website)
    if not website:
        return []
    try:
        homepage, final_website = fetch_document(website, timeout=12)
    except (OSError, TimeoutError, UnicodeError):
        return []
    parsed = urllib.parse.urlparse(final_website)
    root = f"{parsed.scheme}://{parsed.netloc}"
    candidates = [final_website]
    links = re.findall(r'href=["\']([^"\']+)["\']', homepage, flags=re.I)
    preferred = []
    for href in links:
        absolute = urllib.parse.urljoin(final_website, html.unescape(href))
        path = urllib.parse.urlparse(absolute).path.lower()
        if urllib.parse.urlparse(absolute).netloc != parsed.netloc:
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


def research_company(params: dict[str, list[str]]) -> dict:
    company = clean_text((params.get("company") or [""])[0])
    country = clean_text((params.get("country") or [""])[0])
    website = normalize_public_url((params.get("website") or [""])[0])
    source_url = normalize_public_url((params.get("sourceUrl") or [""])[0])
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

    if source_url:
        name, kind = source_category(source_url)
        evidence.append(evidence_item(source_url, company, "原始线索来源", name, kind))
        seen_urls.add(source_url.lower().rstrip("/"))

    site_pages = official_site_pages(website)
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
    website_domain = urllib.parse.urlparse(website).netloc.lower().removeprefix("www.")
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
    if contacts["contact_name"]:
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
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(search_web, query, 5, None): (account_type, relationship)
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
                fetched_page, final_url = fetch_document(url, timeout=10)
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

    youtube_queries = [(f"{company} {country}", "公司账号", "YouTube 频道搜索")]
    if contacts["contact_name"]:
        youtube_queries.append(
            (f'{contacts["contact_name"]} {company}', "个人决策人", "姓名与公司联合搜索")
        )
    for youtube_query, account_type, relationship in youtube_queries:
        try:
            youtube_results = search_youtube_channels(youtube_query, limit=4)
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
    ))[:16]
    social_profiles = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for url in social_urls:
            key = url.lower().rstrip("/")
            futures[
                executor.submit(
                    read_social_profile,
                    url,
                    social_account_types.get(key, "公司账号"),
                    social_relationships.get(key, "公开搜索"),
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

    official_domains = {
        urllib.parse.urlparse(item["url"]).netloc.lower().removeprefix("www.")
        for item in evidence
        if item["sourceType"] == "官方公司页面"
    }
    independent = [
        item for item in evidence
        if urllib.parse.urlparse(item["url"]).netloc.lower().removeprefix("www.") not in official_domains
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
        urllib.parse.urlparse(item["url"]).netloc.lower().removeprefix("www.")
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
    website_score, website_score_breakdown = website_business_score(
        official_website_text or " ".join(item.get("excerpt", "") for item in evidence),
        bool(site_pages or website),
        contactable,
    )
    business_signals, intent_signals = opportunity_signals(
        official_website_text or " ".join(item.get("excerpt", "") for item in evidence)
    )

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
        "evidenceSources": evidence,
        "confidence": confidence,
        "confidenceLabel": confidence_label,
        "score": website_score,
        "scoreBreakdown": website_score_breakdown,
        "scoreBasis": "根据官网业务、进口分销能力、车型结构、采购意向和公开联系方式评分",
        "businessSignals": business_signals,
        "intentSignals": intent_signals,
        "sourceCoverage": {
            "total": len(evidence),
            "official": official_count,
            "independentDomains": len(independent_domains),
            "contactable": contactable,
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
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if key:
        return key
    if not GOOGLE_MAPS_KEY_FILE.exists():
        return ""
    for line in GOOGLE_MAPS_KEY_FILE.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            return value
    return ""


def search_google_places(country: str, query_terms: str, limit: int = 12) -> list[dict]:
    api_key = get_google_maps_api_key()
    if not api_key:
        raise RuntimeError("Google Maps API 密钥未配置")
    city = next(
        (value[0] for key, value in CITY_COORDS.items() if key.lower() in country.lower()),
        CITY_COORDS["UAE"][0],
    )
    body = json.dumps(
        {
            "textQuery": f"{query_terms} in {city}",
            "pageSize": min(max(limit, 1), 20),
            "languageCode": "en",
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


def search_osm_dealers(country: str, limit: int = 12, target_type: str = "dealer") -> list[dict]:
    location = next(
        (value for key, value in CITY_COORDS.items() if key.lower() in country.lower()),
        CITY_COORDS["UAE"],
    )
    city, latitude, longitude = location
    selectors = TARGET_PROFILES.get(target_type, TARGET_PROFILES["dealer"])["osm"]
    if not selectors:
        return []
    osm_parts = "".join(
        f"{selector}(around:45000,{latitude},{longitude});"
        for selector in selectors
    )
    query = f"[out:json][timeout:25];({osm_parts});out tags center {max(limit * 4, 30)};"
    url = "https://overpass-api.de/api/interpreter?" + urllib.parse.urlencode({"data": query})
    request = urllib.request.Request(url, headers={"User-Agent": "HuaweiEVLeadTool/1.0"})
    with urllib.request.urlopen(request, timeout=35) as response:
        payload = json.loads(response.read().decode("utf-8", errors="ignore"))
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
        osm_url = f"https://www.openstreetmap.org/{element.get('type', 'node')}/{element.get('id')}"
        target_label = TARGET_PROFILES.get(target_type, TARGET_PROFILES["dealer"])["label"]
        snippet = f"{name} is listed as a {target_label} related business in {city}."
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
    for value in re.findall(r"\+?\d[\d\s().-]{7,}\d", text):
        value = value.strip()
        digits = re.sub(r"\D", "", value)
        if not 8 <= len(digits) <= 15:
            continue
        if re.search(r"\b20\d{2}[./-]\d{1,2}[./-]\d{1,2}", value) or value.count(".") >= 2:
            continue
        if value not in phones:
            phones.append(value)
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
        r'https?://(?:www\.)?(?:instagram\.com|facebook\.com|linkedin\.com|tiktok\.com|youtube\.com)/[^"\'\s<]+',
        page,
        flags=re.I,
    ):
        value = html.unescape(value).rstrip(".,;:)]}'\"")
        if is_social_profile_url(value) and value not in social_accounts:
            social_accounts.append(value)
    social_accounts = social_accounts[:8]
    tag_email = tags.get("email") or tags.get("contact:email") or ""
    tag_phone = tags.get("phone") or tags.get("contact:phone") or ""
    tag_whatsapp = tags.get("contact:whatsapp") or tags.get("whatsapp") or ""
    if tag_email and tag_email not in emails:
        emails.insert(0, tag_email)
    if tag_phone and tag_phone not in phones:
        phones.insert(0, tag_phone)
    if tag_whatsapp and tag_whatsapp not in whatsapp_urls:
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
        "whatsapp": whatsapp_urls[0] if whatsapp_urls else "",
        "whatsapps": whatsapp_urls[:20],
        "social_accounts": social_accounts,
        "contact_name": contact_name,
        "contact_role": contact_role,
    }


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
    score, _ = website_business_score(text, bool(re.search(r"https?://|www\.", text, re.I)), bool(contact))
    return score


def website_business_score(
    text: str,
    has_official_website: bool,
    has_contact: bool,
    google_reviews: int = 0,
) -> tuple[int, list[dict]]:
    lower = clean_text(text).lower()
    score = 8
    breakdown: list[dict] = []

    def add(label: str, points: int):
        nonlocal score
        score += points
        breakdown.append({"label": label, "points": points})

    if any(term in lower for term in ("vehicle importer", "car importer", "automotive importer", "parallel import", "import and export")):
        add("官网明确包含汽车进口业务", 26)
    elif any(term in lower for term in ("distributor", "distribution", "authorized dealer", "exclusive dealer")):
        add("官网明确包含品牌分销/代理业务", 23)
    elif any(term in lower for term in ("dealer", "dealership", "showroom", "motors", "auto trading", "automotive trading")):
        add("官网显示汽车经销、展厅或贸易业务", 18)

    if any(term in lower for term in ("luxury", "premium", "supercar", "range rover", "mercedes", "bmw", "porsche", "bentley")):
        add("经营豪华或高端汽车", 12)
    if any(term in lower for term in ("electric vehicle", "electric cars", " ev ", "hybrid", "new energy", "chinese car", "chinese vehicle")):
        add("经营新能源或中国汽车", 12)
    if any(term in lower for term in ("our brands", "brands we represent", "multi-brand", "wide range of brands", "brand portfolio")):
        add("具备多品牌经营能力", 8)
    if any(term in lower for term in BUYING_INTENT_TERMS):
        add("存在采购、招商或供应商合作意向", 14)
    elif any(term in lower for term in ("fleet", "procurement", "wholesale", "bulk order", "corporate sales")):
        add("具备车队、批发或企业采购业务", 9)
    if has_official_website:
        add("可核验企业官网", 7)
    if has_contact:
        add("官网存在公开联系方式", 5)
    if google_reviews >= 20:
        add("地图经营评价较充分", 4)

    if re.search(r"\b(repair|workshop|spare parts|car wash|detailing|tyres?)\b", lower) and not re.search(
        r"\b(importer|distributor|dealer|dealership|showroom|vehicle sales)\b", lower
    ):
        add("仅维修、配件或美容业务", -28)
    if re.search(r"\b(classifieds?|marketplace|individual seller|private seller)\b", lower):
        add("交易平台或个人卖家特征", -18)

    return max(5, min(score, 98)), breakdown


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


def discover(params: dict[str, list[str]]) -> dict:
    country = (params.get("country") or ["UAE"])[0]
    model = (params.get("model") or ["问界 M9"])[0]
    goal = (params.get("goal") or [""])[0]
    target_type = infer_target_type(goal)
    target_profile = TARGET_PROFILES.get(target_type, TARGET_PROFILES["dealer"])
    target_label = target_profile["label"]
    source_mode = (params.get("sourceMode") or ["combined"])[0]
    account_scope = (params.get("accountScope") or ["both"])[0]
    city_focus = (params.get("cityFocus") or [""])[0].strip()
    customer_types = (params.get("customerTypes") or [""])[0].strip()
    exclusions = (params.get("exclusions") or [""])[0].strip()
    result_limit_value = (params.get("resultLimit") or ["40"])[0]
    result_limit = max(10, min(60, int(result_limit_value) if result_limit_value.isdigit() else 40))
    verification_level = (params.get("verificationLevel") or ["strict"])[0]
    min_sources_value = (params.get("minSources") or ["2"])[0]
    min_sources = max(1, min(3, int(min_sources_value) if min_sources_value.isdigit() else 2))
    freshness_value = (params.get("freshness") or ["all"])[0]
    freshness_days = int(freshness_value) if freshness_value.isdigit() else None
    keywords = (params.get("keywords") or [""])[0].replace("|", " ")
    cutoff_query = ""
    if freshness_days:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=freshness_days)).date().isoformat()
        cutoff_query = f" after:{cutoff}"
    exclude_query = " ".join(
        f'-"{part.strip()}"'
        for part in re.split(r"[,，、;；]+", exclusions)
        if part.strip()
    )
    query = (
        f"{city_focus} {keywords} {customer_types} {target_profile['query']} "
        f"official website contact email WhatsApp {exclude_query}{cutoff_query}"
    ).strip()
    market = city_focus or country.split(" ")[0]
    broad_business_query = (
        f"{market} automotive importer vehicle distributor car dealer showroom "
        f"parallel import auto trading official website contact {exclude_query}{cutoff_query}"
    ).strip()
    intent_query = (
        f"{market} car dealer importer \"new brand\" OR \"brand partnership\" OR "
        f"\"vehicle procurement\" OR RFQ OR \"dealer wanted\" {exclude_query}{cutoff_query}"
    ).strip()
    china_ev_query = (
        f"{market} Chinese car importer electric vehicle distributor dealership "
        f"official website contact {exclude_query}{cutoff_query}"
    ).strip()

    raw_results = []
    notice = ""
    if source_mode == "google" and freshness_days:
        return {
            "ok": True,
            "count": 0,
            "leads": [],
            "notice": "Google Maps 企业资料是长期商家数据，没有消息发布日期。请选择“不限时间”。",
        }
    if source_mode == "osm" and freshness_days:
        return {
            "ok": True,
            "count": 0,
            "leads": [],
            "notice": "OpenStreetMap 是长期商业地点目录，没有消息发布日期。请选择“不限时间”，或改选官网、Instagram、Facebook、LinkedIn。",
        }
    if source_mode in ("all", "combined", "google") and (
        not freshness_days or source_mode == "all"
    ):
        try:
            raw_results += search_google_places(
                country,
                "car dealer automotive importer vehicle distributor electric vehicle showroom",
                limit=min(result_limit, 20 if source_mode in ("all", "combined") else 30),
            )
        except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
            if source_mode == "google":
                notice = f"{exc}。请在本机配置密钥后重试。"
    if source_mode in ("all", "combined", "osm") and (
        not freshness_days or source_mode == "all"
    ) and (
        source_mode in ("all", "combined", "osm")
    ):
        try:
            raw_results += search_osm_dealers(
                country,
                limit=min(result_limit, 20 if source_mode in ("all", "combined") else 30),
                target_type=target_type,
            )
        except (OSError, ValueError, TimeoutError):
            pass
    if source_mode in ("all", "combined", "dealer"):
        search_variants = [broad_business_query, intent_query, china_ev_query, query]
        per_query_limit = 10 if source_mode in ("all", "combined") else 14
        for search_query in search_variants:
            try:
                web_results = search_web(
                    search_query,
                    limit=per_query_limit,
                    freshness_days=freshness_days,
                )
                for item in web_results:
                    origin, source_type = source_details(item["url"])
                    item["origin"] = origin
                    item["source_type"] = source_type
                    item["source_url"] = item["url"]
                    item["customer_website"] = item["url"]
                raw_results += web_results
            except (OSError, ValueError, TimeoutError):
                pass
    if source_mode == "dealer":
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
        except (OSError, ValueError, TimeoutError):
            pass
    platform_queries = {
        "instagram": ("instagram.com", "Instagram", "社交媒体公开主页"),
        "facebook": ("facebook.com", "Facebook", "社交媒体公开主页"),
        "tiktok": ("tiktok.com", "TikTok", "短视频公开账号"),
        "linkedin": ("linkedin.com", "LinkedIn", "企业与职业社交平台"),
    }
    selected_platforms = (
        list(platform_queries)
        if source_mode in ("all", "social")
        else [source_mode] if source_mode in platform_queries else []
    )
    role_query = (
        "dealership owner founder general manager import manager fleet manager sales director"
        if account_scope in ("person", "both")
        else ""
    )
    company_query = (
        "automotive importer vehicle distributor car dealer showroom auto trading "
        "brand partnership vehicle procurement"
        if account_scope in ("company", "both") else ""
    )
    for platform in selected_platforms:
        site, origin, source_type = platform_queries[platform]
        try:
            social_results = search_web(
                f"site:{site} {keywords} {company_query} {role_query}{cutoff_query}",
                limit=12,
                freshness_days=freshness_days,
            )
            expected_domain = site.split("/")[0]
            social_results = [
                item
                for item in social_results
                if expected_domain in urllib.parse.urlparse(item["url"]).netloc.lower()
            ]
            for item in social_results:
                item["origin"] = origin
                item["source_type"] = source_type
                item["source_url"] = item["url"]
                item["customer_website"] = ""
                path = urllib.parse.urlparse(item["url"]).path.lower()
                is_person = (
                    "/in/" in path
                    or account_scope == "person"
                    or bool(re.search(r"\b(owner|founder|manager|director)\b", f"{item['title']} {item['snippet']}", re.I))
                )
                item["account_type"] = "个人决策人" if is_person else "公司账号"
            raw_results += social_results
        except (OSError, ValueError, TimeoutError):
            pass
    if source_mode in ("all", "youtube", "social"):
        youtube_searches = []
        if account_scope in ("company", "both"):
            youtube_searches.append(
                (f"{keywords} {company_query} official channel".strip(), "公司账号")
            )
        if account_scope in ("person", "both"):
            city = next(
                (cities[0] for key, cities in COUNTRY_HINTS.items() if key.lower() in country.lower()),
                country.split(" ")[0],
            )
            youtube_searches.append(
                (f"{city} car dealer owner manager channel", "个人/经营者账号（待核验）")
            )
        for youtube_query, youtube_account_type in youtube_searches:
            try:
                youtube_items = search_youtube_channels(youtube_query, limit=10)
            except (OSError, ValueError, TimeoutError, json.JSONDecodeError):
                youtube_items = []
            for item in youtube_items:
                location_text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
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
                if not any(term and term in location_text for term in location_terms):
                    continue
                item["origin"] = "YouTube"
                item["source_type"] = "YouTube 公开频道"
                item["source_url"] = item["url"]
                item["customer_website"] = ""
                item["account_type"] = youtube_account_type
                raw_results.append(item)
    leads = []
    seen_sources = set()
    for item in raw_results:
        if len(leads) >= result_limit:
            break
        parsed = urllib.parse.urlparse(item["url"])
        domain = parsed.netloc.lower().removeprefix("www.")
        path_lower = parsed.path.lower()
        title_lower = item["title"].lower()
        is_google_places = item.get("origin") == "Google Maps"
        is_social_result = item.get("origin") in ("Facebook", "Instagram", "TikTok", "LinkedIn", "YouTube")
        if not is_google_places and not is_social_result and any(
            blocked in domain or blocked in item["url"].lower()
            for blocked in BLOCKED_DOMAINS
        ):
            continue
        allow_recent_content = bool(freshness_days) or target_type in ("buying", "government", "individual")
        if any(word in title_lower for word in BLOCKED_TITLE_WORDS) and not allow_recent_content:
            continue
        if any(part in path_lower for part in BLOCKED_PATH_PARTS) and not allow_recent_content:
            continue
        if re.search(r"/20\d{2}/\d{1,2}/\d{1,2}/", path_lower) and not allow_recent_content:
            continue
        source_identity = (
            item.get("customer_website")
            or item.get("source_url")
            or item["url"]
            or item["title"]
        ).lower()
        if source_identity in seen_sources:
            continue
        seen_sources.add(source_identity)

        page_text = f"{item['title']} {item['snippet']}"
        page = ""
        contact = item.get("contact", "")
        if not item.get("skip_fetch"):
            try:
                page = fetch_text(item["url"], timeout=8)
                page_text = extract_meta(page)
                contact = contact or extract_contact(page_text)
            except (OSError, TimeoutError, UnicodeError):
                pass

        combined = f"{item['title']} {item['snippet']} {page_text}"
        if not is_google_places and item.get("origin") != "OpenStreetMap":
            business_match = re.search(
                r"\b(dealer|dealership|showroom|importer|exporter|trading|distributor|"
                r"cars|motors|automotive|fleet|rental|procurement|tender|buyer|rfq|"
                r"owner|founder|general manager|import manager|fleet manager|sales director)\b",
                combined,
                re.I,
            )
            if not business_match:
                continue
            if re.match(r"^\s*20\d{2}\s+", item["title"]) and re.search(
                r"\b(seater|4wd|awd|km|mileage|price|available)\b",
                combined,
                re.I,
            ):
                continue
        if not re.search(
            r"\b(dealer|dealership|showroom|importer|exporter|trading|cars|motors|"
            r"vehicles?|automotive|ev|electric|fleet|rental|procurement|tender|buyer|rfq|wanted|"
            r"owner|founder|general manager|import manager|fleet manager|sales director)\b",
            combined,
            re.I,
        ):
            continue
        company = infer_company_name(item["title"], domain)
        lead_type = infer_type(combined)
        origin = item.get("origin", "公开网页搜索")
        source_url = item.get("source_url") or item["url"]
        source_type = item.get("source_type") or source_details(source_url, origin)[1]
        score, score_breakdown = website_business_score(
            combined,
            bool(item.get("customer_website") or source_type == "车商官网或汽车行业网站"),
            bool(contact),
            int(item.get("google_reviews") or 0),
        )
        business_signals, intent_signals = opportunity_signals(combined)
        city = infer_city(country, combined)
        source_title = item.get("title") or company
        source_excerpt = item.get("snippet") or page_text[:500]
        published_at = extract_published_at(
            f"{item.get('snippet', '')} {page_text[:700]}",
            source_url,
        )
        is_long_lived_business_source = (
            source_mode == "all"
            and (
                is_google_places
                or origin.startswith("OpenStreetMap")
                or source_type in ("地图与地理商业目录", "Google Maps 企业资料")
            )
        )
        if not is_long_lived_business_source and not is_within_freshness(published_at, freshness_days):
            continue
        customer_website = item.get("customer_website") or (
            item["url"] if source_type == "车商官网或汽车行业网站" else ""
        )
        contacts = extract_public_contacts(page or page_text, item.get("tags"))
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
            contacts["phone"] = contact
        email_sources = [
            {
                "email": email,
                "sources": [{
                    "url": source_url,
                    "name": origin,
                    "verified": bool(
                        item.get("origin") in ("OpenStreetMap", "Google Maps")
                        or (page and re.search(re.escape(email), page, re.I))
                    ),
                    "excerpt": source_excerpt[:260],
                }],
            }
            for email in contacts.get("emails") or ([contacts["email"]] if contacts["email"] else [])
        ]
        verified_email_sources = [
            record for record in email_sources
            if any(source.get("verified") for source in record["sources"])
        ]
        contacts["email"] = verified_email_sources[0]["email"] if verified_email_sources else ""
        phone_sources = [
            {"value": phone, "sources": [{"url": source_url, "name": origin}]}
            for phone in contacts.get("phones") or ([contacts["phone"]] if contacts["phone"] else [])
        ]
        whatsapp_sources = [
            {"value": value, "sources": [{"url": source_url, "name": origin}]}
            for value in contacts.get("whatsapps") or ([contacts["whatsapp"]] if contacts["whatsapp"] else [])
        ]
        is_competitor = detect_competitor(combined)
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
        contact_reason = (
            f"该线索与“{target_label}”目标匹配，"
            f"信息可信度为{confidence_label}（{confidence}%），"
            f"建议优先推荐{'、'.join(recommended_models)}。"
        )
        if intent_signals:
            contact_reason = (
                f"发现{ '、'.join(intent_signals) }，即使页面未提及华为汽车也值得优先联系。"
                + contact_reason
            )
        elif business_signals:
            contact_reason = (
                f"已确认具备{ '、'.join(business_signals) }，可作为潜在进口或分销客户培育。"
                + contact_reason
            )
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
                "evidenceSources": [
                    evidence_item(
                        source_url,
                        source_title,
                        source_excerpt,
                        origin,
                        source_type,
                    )
                ],
                "researchAt": "",
                "researchSummary": "当前只有原始发现来源，建议在线索审核中执行全网补全。",
                "publishedAt": published_at,
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
                        "accountType": item.get("account_type", "公司账号"),
                        "relationship": f"{origin} 公开结果",
                        "title": source_title,
                        "description": source_excerpt[:700],
                        "url": item["url"],
                        "handle": urllib.parse.urlparse(item["url"]).path.strip("/").split("/")[-1],
                    }
                ] if is_social_profile_url(item["url"]) else [],
                "accountType": item.get("account_type", "公司客户"),
                "isDuplicate": False,
                "isCompetitor": is_competitor,
                "confidence": confidence,
                "confidenceLabel": confidence_label,
                "sourceCoverage": {
                    "total": 1,
                    "official": 0,
                    "independentDomains": 1,
                    "contactable": bool(email_sources or phone_sources or whatsapp_sources),
                    "missingFields": [
                        field
                        for field, present in (
                            ("官网", bool(customer_website)),
                            ("邮箱", bool(email_sources)),
                            ("电话", bool(phone_sources)),
                            ("联系人", bool(contacts["contact_name"])),
                            ("社媒账号", bool(contacts["social_accounts"])),
                        )
                        if not present
                    ],
                    "decision": "待全网核验",
                },
                "searchPolicy": {
                    "verificationLevel": verification_level,
                    "minimumIndependentSources": min_sources,
                    "emailMustBeVerified": verification_level == "strict",
                    "resultLimit": result_limit,
                },
                "recommendedModels": recommended_models,
                "businessSignals": business_signals,
                "intentSignals": intent_signals,
                "contactReason": contact_reason,
                "sourceTranslation": source_translation,
                "googleRating": item.get("google_rating", 0),
                "googleReviews": item.get("google_reviews", 0),
                "businessStatus": item.get("business_status", ""),
                "model": model,
                "score": score,
                "scoreBreakdown": score_breakdown,
                "scoreBasis": "根据官网业务、进口分销能力、车型结构、采购意向和公开联系方式评分",
                "stage": "准备联系" if score >= 75 else "待审核",
                "next": "生成英文开发信并人工确认",
                "website": combined[:1000],
                "reason": reason,
            }
        )
    if freshness_days and not leads:
        notice = f"没有找到可确认发布日期且在最近 {freshness_days} 天内的线索。可以放宽到 30 天，或更换 Instagram、Facebook、LinkedIn 来源。"
    if source_mode == "google" and not leads and not notice:
        notice = "Google Maps 没有返回符合条件的企业，请调整中文目标描述或目标国家。"
    leads.sort(key=lambda item: (-int(item.get("score", 0)), item.get("company", "")))
    return {"ok": True, "count": len(leads), "leads": leads, "notice": notice}


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
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        morsel = cookie.get(AUTH_COOKIE)
        return bool(morsel and verify_session_token(morsel.value))

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def require_auth(self, api=False):
        if self.is_authenticated():
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
        if parsed.path == "/api/session":
            self.send_json(
                200,
                {
                    "ok": True,
                    "authenticated": self.is_authenticated(),
                    "username": AUTH_USERNAME if self.is_authenticated() else "",
                },
            )
            return
        if parsed.path == "/api/discover/status":
            if not self.require_auth(api=True):
                return
            job_id = (urllib.parse.parse_qs(parsed.query).get("id") or [""])[0]
            job = get_discovery_job(job_id)
            if not job:
                self.send_json(404, {"ok": False, "error": "获客任务不存在或已过期"})
                return
            self.send_json(200, {"ok": True, "job": job})
            return
        if parsed.path in ("/", "/index.html") and not self.require_auth():
            return
        if parsed.path.startswith("/api/") and not self.require_auth(api=True):
            return
        if parsed.path == "/api/social-captures":
            body = json.dumps(
                {"ok": True, "captures": load_social_captures()},
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
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
                result = discover(urllib.parse.parse_qs(parsed.query))
                body = json.dumps(result, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
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
                valid = hmac.compare_digest(username, AUTH_USERNAME) and hmac.compare_digest(
                    password, AUTH_PASSWORD
                )
                if not valid:
                    self.send_json(401, {"ok": False, "error": "账户名或密码错误"})
                    return
                token = create_session_token(username)
                body = json.dumps({"ok": True, "username": username}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                secure = "; Secure" if self.headers.get("X-Forwarded-Proto", "").lower() == "https" else ""
                self.send_header(
                    "Set-Cookie",
                    f"{AUTH_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={AUTH_MAX_AGE}{secure}",
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
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if not self.require_auth(api=True):
            return
        if parsed.path == "/api/discover/start":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 65_536)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("请求格式无效")
                job = create_discovery_job(payload)
                self.send_json(202, {"ok": True, "job": job})
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path != "/api/social-capture":
            self.send_error(404)
            return
        try:
            content_length = min(int(self.headers.get("Content-Length", "0")), 10_000_000)
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            record = save_social_capture(payload)
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


if __name__ == "__main__":
    with ReusableThreadingTCPServer((HOST, PORT), Handler) as httpd:
        display_host = "127.0.0.1" if HOST == "0.0.0.0" else HOST
        print(f"获客工作台已启动：http://{display_host}:{PORT}/index.html")
        httpd.serve_forever()

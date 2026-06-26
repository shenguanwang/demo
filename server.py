from __future__ import annotations

import html
import binascii
import hashlib
import hmac
import http.client
import json
import os
import re
import secrets
import socketserver
import base64
import sqlite3
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
GOOGLE_MAPS_KEY_FILE = ROOT / "google_maps_api_key.txt"
SOCIAL_CAPTURE_DIR = ROOT / "social-captures"
SOCIAL_CAPTURE_FILE = SOCIAL_CAPTURE_DIR / "captures.json"
SOCIAL_CAPTURE_LOCK = threading.Lock()
DISCOVERY_JOBS: dict[str, dict] = {}
DISCOVERY_JOBS_LOCK = threading.RLock()
DISCOVERY_CREATE_LOCK = threading.Lock()
ACTIVE_DISCOVERY_WORKERS: set[str] = set()
ACTIVE_DISCOVERY_WORKERS_LOCK = threading.Lock()
DISCOVERY_MAX_CONCURRENCY = max(1, int(os.environ.get("DISCOVERY_MAX_CONCURRENCY", "2")))
DISCOVERY_WORKER_SLOTS = threading.BoundedSemaphore(DISCOVERY_MAX_CONCURRENCY)
DISCOVERY_JOB_TTL = 60 * 60 * 24 * 7
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
SQLITE_STATE_FILE = Path(os.environ.get("STATE_DATABASE_PATH") or (ROOT / "workbench-state.db"))
STATE_LOCK = threading.RLock()
AUTH_USERNAME = os.environ.get("APP_USERNAME", "admin")
AUTH_PASSWORD = os.environ.get("APP_PASSWORD", "admin123")
AUTH_SECRET = os.environ.get("APP_AUTH_SECRET") or secrets.token_hex(32)
AUTH_COOKIE = "hima_session"
AUTH_MAX_AGE = 60 * 60 * 24 * 7
PASSWORD_HASH_ITERATIONS = 210_000


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


def initialize_state_store() -> None:
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
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'user',
                        status TEXT NOT NULL DEFAULT 'enabled',
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
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                status TEXT NOT NULL DEFAULT 'enabled',
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


def empty_workspace_state() -> dict:
    return {
        "reviewLeads": [],
        "customers": [],
        "rejectedLeads": [],
        "quotes": [],
        "deletedRecords": [],
    }


def workspace_storage_key(username: str) -> str:
    return "admin-default" if username == AUTH_USERNAME else f"user:{username}"


def normalize_workspace_state(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("工作台数据格式无效")
    normalized = {}
    for key in ("reviewLeads", "customers", "rejectedLeads", "quotes", "deletedRecords"):
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


def create_session_token(username: str) -> str:
    expires_at = int(datetime.now(timezone.utc).timestamp()) + AUTH_MAX_AGE
    payload = f"{username}|{expires_at}"
    signature = hmac.new(
        AUTH_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode("utf-8")).decode("ascii")


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


def list_users() -> list[dict]:
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT username, role, status, created_at FROM app_users ORDER BY created_at ASC")
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute("SELECT username, role, status, created_at FROM app_users ORDER BY created_at ASC").fetchall()
    users = [{"username": AUTH_USERNAME, "role": "admin", "status": "enabled", "createdAt": "系统内置", "builtIn": True}]
    for row in rows:
        if row[0] == AUTH_USERNAME:
            continue
        created_at = row[3].isoformat() if hasattr(row[3], "isoformat") else str(row[3])
        users.append({"username": row[0], "role": row[1], "status": row[2], "createdAt": created_at, "builtIn": False})
    return users


def get_user(username: str) -> dict | None:
    if hmac.compare_digest(username, AUTH_USERNAME):
        return {"username": AUTH_USERNAME, "role": "admin", "status": "enabled", "builtIn": True}
    initialize_state_store()
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT username, password_hash, role, status, created_at FROM app_users WHERE username = %s", (username,))
                row = cursor.fetchone()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            row = connection.execute("SELECT username, password_hash, role, status, created_at FROM app_users WHERE username = ?", (username,)).fetchone()
    if not row:
        return None
    return {"username": row[0], "passwordHash": row[1], "role": row[2], "status": row[3], "builtIn": False}


def authenticate_user(username: str, password: str) -> dict | None:
    user = get_user(str(username or "").strip())
    if not user or user.get("status") != "enabled":
        return None
    valid = hmac.compare_digest(password, AUTH_PASSWORD) if user.get("builtIn") else verify_password(password, user.get("passwordHash", ""))
    return user if valid else None


def create_user(username: str, password: str) -> dict:
    username = normalize_username(username)
    if username == AUTH_USERNAME:
        raise ValueError("管理员账户为系统内置账户，不能重复创建")
    if len(password or "") < 6:
        raise ValueError("密码至少需要 6 位")
    if get_user(username):
        raise ValueError("用户名已存在")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    password_hash = hash_password(password)
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO app_users (username, password_hash, role, status, created_at) VALUES (%s, %s, 'user', 'enabled', NOW())", (username, password_hash))
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            connection.execute("INSERT INTO app_users (username, password_hash, role, status, created_at) VALUES (?, ?, 'user', 'enabled', ?)", (username, password_hash, now))
    return {"username": username, "role": "user", "status": "enabled", "createdAt": now, "builtIn": False}


def update_user(username: str, *, password: str | None = None, status: str | None = None) -> dict:
    username = normalize_username(username)
    if username == AUTH_USERNAME:
        raise ValueError("系统内置管理员不可修改或删除")
    if not get_user(username):
        raise ValueError("用户不存在")
    updates, params = [], []
    if password is not None:
        if len(password) < 6:
            raise ValueError("密码至少需要 6 位")
        updates.append("password_hash = %s" if DATABASE_URL else "password_hash = ?")
        params.append(hash_password(password))
    if status is not None:
        if status not in {"enabled", "disabled"}:
            raise ValueError("用户状态无效")
        updates.append("status = %s" if DATABASE_URL else "status = ?")
        params.append(status)
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


def delete_user(username: str) -> None:
    username = normalize_username(username)
    if username == AUTH_USERNAME:
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
        username, expires_at, signature = decoded.rsplit("|", 2)
        payload = f"{username}|{expires_at}"
        expected = hmac.new(
            AUTH_SECRET.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected) or int(expires_at) <= int(datetime.now(timezone.utc).timestamp()):
            return None
        user = get_user(username)
        return user if user and user.get("status") == "enabled" else None
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
        return None


def verify_session_token(token: str) -> bool:
    return bool(session_user_from_token(token))


def cleanup_discovery_jobs() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=DISCOVERY_JOB_TTL)
    initialize_state_store()
    with DISCOVERY_JOBS_LOCK:
        if DATABASE_URL:
            with postgres_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM discovery_jobs WHERE updated_at < %s", (cutoff,))
        else:
            with sqlite3.connect(SQLITE_STATE_FILE) as connection:
                connection.execute(
                    "DELETE FROM discovery_jobs WHERE updated_at < ?",
                    (cutoff.isoformat(timespec="seconds"),),
                )


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
    }


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


def list_discovery_jobs(owner_username: str, limit: int = 20) -> list[dict]:
    cleanup_discovery_jobs()
    query = (
        "SELECT job_id, payload, status, stage, progress, message, result, error, "
        "imported, created_at, updated_at, owner_username FROM discovery_jobs "
        "WHERE owner_username = "
    )
    if DATABASE_URL:
        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query + "%s ORDER BY updated_at DESC LIMIT %s", (owner_username, limit))
                rows = cursor.fetchall()
    else:
        with sqlite3.connect(SQLITE_STATE_FILE) as connection:
            rows = connection.execute(query + "? ORDER BY updated_at DESC LIMIT ?", (owner_username, limit)).fetchall()
    return [discovery_job_public(row_to_discovery_job(row)) for row in rows]


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


def run_discovery_job(job_id: str, params: dict[str, list[str]]) -> None:
    try:
        with DISCOVERY_WORKER_SLOTS:
            started = update_discovery_job(
                job_id,
                skip_statuses=("canceled",),
                status="running",
                stage="search",
                progress=12,
                message="云端正在检索地图、企业官网、行业目录和公开社媒来源。",
            )
            if not started:
                return
            result = discover(params)
            update_discovery_job(
                job_id,
                skip_statuses=("canceled",),
                status="completed",
                stage="done",
                progress=100,
                message=f"云端搜索完成，共发现 {result.get('count', 0)} 条线索。",
                result=result,
            )
    except Exception as exc:
        diagnostics = discovery_failure_diagnostics(exc, params)
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


def create_discovery_job(payload: dict, owner_username: str, *, force: bool = False) -> dict:
    cleanup_discovery_jobs()
    params = discovery_params(payload)
    normalized_payload = {key: value[0] for key, value in params.items()}
    with DISCOVERY_CREATE_LOCK:
        if not force:
            existing = find_matching_active_discovery_job(normalized_payload, owner_username)
            if existing:
                existing["reused"] = True
                return discovery_job_public(existing)
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


def mark_discovery_job_imported(job_id: str, owner_username: str) -> dict | None:
    job = load_discovery_job(job_id, owner_username)
    if not job:
        return None
    job["imported"] = True
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
    "Saudi": ("Riyadh", "Jeddah", "Dammam", "Khobar", "Mecca", "Medina"),
    "Kazakhstan": ("Almaty", "Astana", "Aktau"),
    "Russia": ("Moscow", "St. Petersburg"),
    "Qatar": ("Doha",),
    "Kuwait": ("Kuwait City",),
    "Uzbekistan": ("Tashkent",),
    "Azerbaijan": ("Baku",),
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

OBVIOUS_IRRELEVANT_LEAD_PATTERNS = (
    r"\b(towing|tow truck|roadside assistance|vehicle recovery|car recovery|breakdown service|wrecker)\b",
    r"\b(tax consultant|tax consultancy|vat consultant|vat consultancy|tax agent|tax filing|tax refund)\b",
    r"\b(tax free|duty free|excise tax|corporate tax|customs clearance|customs broker)\b",
    r"\b(company formation|business setup|free zone license|trade license|pro services|visa services)\b",
    r"\b(accounting|bookkeeping|audit firm|auditing|attestation|document clearing)\b",
    r"\b(auto repair|car repair|vehicle repair|repair shop|repair workshop|auto workshop|car workshop)\b",
    r"\b(service center|service centre|maintenance|mechanic|garage|body shop|paint shop|collision repair)\b",
    r"\b(car wash|auto wash|detailing|car detailing|window tint|wrapping|car wrap|ceramic coating)\b",
    r"\b(tyre|tyres|tire|tires|battery replacement|oil change|spare parts|auto parts|car parts)\b",
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
}


def discovery_cities(country: str, city_focus: str = "") -> list[str]:
    cities = [city_focus.strip()] if city_focus.strip() else []
    for key, hints in COUNTRY_HINTS.items():
        if key.lower() in country.lower():
            cities.extend(hints)
            break
    cities.append(country.split(" ")[0])
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
    balanced = []
    while any(buckets.get(key) for key in order):
        for key in order:
            if buckets.get(key):
                balanced.append(buckets[key].pop(0))
    return balanced


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
                public_base = PUBLIC_BASE_URL or f"http://127.0.0.1:{PORT}"
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
            return parts[1].lower() not in {"share", "iv"}
        return bool(parts) and parts[0].lower() not in {"s", "share", "iv"}
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
    parsed = urllib.parse.urlparse(normalized)
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
    if domain.endswith("t.me") or "telegram." in domain:
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
        (label for label, terms in decision_roles.items() if any(term in lower for term in terms)),
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
    if role or "个人" in account_type or any(marker in lower for marker in person_markers):
        detected_type = "个人决策人"
    elif business_signals or "公司" in account_type or any(marker in lower for marker in company_markers):
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
        "isCommercial": bool(
            business_signals
            or intent_signals
            or role
            or (has_company_marker and has_automotive_marker)
        ),
    }


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
    analysis = analyze_social_business_profile(
        f"{title} {description} {handle}",
        platform,
        account_type,
    )
    if analysis["accountType"] != "账号类型待核验":
        account_type = analysis["accountType"]
    return {
        "platform": platform,
        "accountType": account_type,
        "relationship": relationship,
        "title": clean_text(title)[:180],
        "description": clean_text(description)[:700],
        "url": final_url,
        "handle": handle[:120],
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
                "handle": text_from_runs(video.get("publishedTimeText")),
                "channelId": channel_id,
                "apiSource": "YouTube public video fallback",
            }
        )
        seen.add(identity)
        if len(results) >= limit:
            break
    return results


def search_youtube_channels(query: str, limit: int = 5) -> list[dict]:
    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if api_key:
        per_type_limit = max(1, min(limit, 50))
        search_items = []
        for result_type in ("channel", "video"):
            params = {
                "part": "snippet",
                "type": result_type,
                "q": query,
                "maxResults": str(per_type_limit),
                "fields": "items(id/channelId,id/videoId,snippet(channelId,channelTitle,title,description,publishedAt))",
                "key": api_key,
            }
            request = urllib.request.Request(
                "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(params),
                headers={"User-Agent": "HuaweiEVLeadTool/1.0"},
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    payload = json.loads(response.read().decode("utf-8", errors="ignore"))
                search_items.extend(payload.get("items", []))
            except (OSError, ValueError, TimeoutError, http.client.HTTPException, json.JSONDecodeError):
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
            seen_channel_ids.add(channel_id)
            detail = details_by_id.get(channel_id, {})
            detail_snippet = detail.get("snippet") or {}
            branding = detail.get("brandingSettings") or {}
            branding_channel = branding.get("channel") or {}
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
                    "snippet": detail_snippet.get("description") or snippet.get("description", ""),
                    "handle": snippet.get("publishedAt", ""),
                    "channelId": channel_id,
                    "country": branding_channel.get("country", ""),
                    "apiSource": "YouTube Data API v3",
                }
            )
            if len(results) >= per_type_limit * 2:
                break
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
            if href.startswith("http") and "bing.com" not in href:
                items.append({"title": title, "url": href, "snippet": snippet})
            if len(items) >= limit:
                return items
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
        if href.startswith("http") and "search.brave.com" not in href:
            items.append({"title": title, "url": href, "snippet": snippet})
        if len(items) >= limit:
            break
    return items


def search_web(query: str, limit: int = 8, freshness_days: int | None = None) -> list[dict]:
    collected: list[dict] = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(search_duckduckgo, query, limit, freshness_days),
            executor.submit(search_bing, query, limit, freshness_days),
            executor.submit(search_brave, query, limit, freshness_days),
        ]
        for future in as_completed(futures):
            try:
                collected.extend(future.result())
            except (OSError, ValueError, TimeoutError, urllib.error.URLError):
                continue
    results: list[dict] = []
    seen: set[str] = set()
    for item in collected:
        identity = normalize_public_url(item.get("url", "")).lower().rstrip("/")
        if not identity or identity in seen:
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
        markets.extend(["Dubai", "Abu Dhabi", "Sharjah", "Ajman"])
    markets = list(dict.fromkeys(place for place in markets if place))
    broad_terms = (
        "car dealer",
        "used cars",
        "cars for sale",
        "motors",
        "auto trading",
        "automotive trading",
        "car showroom",
        "luxury cars",
        "imported cars",
        "vehicle importer",
    )
    if platform == "telegram":
        for place in markets:
            for term in broad_terms:
                queries.append(f"site:{site} {place} \"{term}\"")
        return list(dict.fromkeys(queries))
    if platform == "twitter":
        for place in markets:
            for term in broad_terms:
                queries.append(f"site:x.com {place} \"{term}\"")
                queries.append(f"site:twitter.com {place} \"{term}\"")
        return list(dict.fromkeys(queries))
    if platform in {"instagram", "facebook", "tiktok", "threads", "pinterest", "reddit", "vk"}:
        site_variants = {
            "instagram": ("instagram.com",),
            "facebook": ("facebook.com",),
            "tiktok": ("tiktok.com",),
            "threads": ("threads.net",),
            "pinterest": ("pinterest.com",),
            "reddit": ("reddit.com/r", "reddit.com/user"),
            "vk": ("vk.com",),
        }.get(platform, (site,))
        for place in markets:
            for term in broad_terms:
                for variant in site_variants:
                    queries.append(f"site:{variant} {place} \"{term}\"")
        return list(dict.fromkeys(queries))
    if platform == "linkedin":
        for place in markets:
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
    requested_model = clean_text((params.get("model") or [""])[0])
    lead_type = clean_text((params.get("type") or [""])[0])
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
    scoring_text = official_website_text or " ".join(item.get("excerpt", "") for item in evidence)
    is_competitor = detect_competitor(scoring_text)
    website_score, website_score_breakdown, score_dimensions, score_tier = lead_opportunity_score(
        scoring_text,
        bool(site_pages or website),
        contactable,
        requested_model=requested_model,
        lead_type=lead_type,
        is_competitor=is_competitor,
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
        "scoreModelVersion": 6,
        "scoreTier": score_tier,
        "scoreDimensions": score_dimensions,
        "scoreBreakdown": website_score_breakdown,
        "scoreBasis": "100分机会模型：进出口资质30、客户匹配25、采购意向18、经营能力12、车型匹配10、可触达性5，另计风险扣分",
        "isCompetitor": is_competitor,
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


def clean_phone_value(value: str) -> str:
    value = html.unescape(str(value or "")).strip()
    value = re.sub(r"^(?:tel|phone|call|mobile|whatsapp|wa)[:：\s]+", "", value, flags=re.I)
    value = value.strip(" \t\r\n.,;:)]}'\"")
    value = re.sub(r"\s+", " ", value)
    digits = re.sub(r"\D", "", value)
    if value.startswith("+971") and len(digits) > 12:
        return "+" + digits[:12]
    return value


def valid_phone_candidate(value: str, context: str = "") -> bool:
    value = clean_phone_value(value)
    digits = re.sub(r"\D", "", value)
    if not 8 <= len(digits) <= 15:
        return False
    if re.search(r"\b20\d{2}[./-]\d{1,2}[./-]\d{1,2}", value) or value.count(".") >= 2:
        return False
    if len(set(digits)) <= 2 and not value.strip().startswith("+"):
        return False
    lowered = context.lower()
    has_contact_label = bool(re.search(r"\b(whatsapp|phone|mobile|tel|call|contact|wa)\b|电话|联系", lowered))
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


PHONE_CANDIDATE_PATTERN = r"\+?\d(?:[\s().-]?\d){7,14}"


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
    for match in re.finditer(PHONE_CANDIDATE_PATTERN, text):
        context = text[max(0, match.start() - 80):match.end() + 80]
        if not clean_phone_value(match.group(0)).startswith("+"):
            continue
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


def is_brand_bound_chinese_dealer(text: str) -> bool:
    """Exclude single-brand Chinese OEM 4S/authorized outlets from channel leads.

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
    binding_terms = (
        "4s", "4 s", "authorized dealer", "official dealer", "exclusive dealer",
        "authorized distributor", "official distributor", "brand showroom", "dealer of",
        "官方授权", "授权经销商", "品牌专营", "4s店",
    )
    multi_brand_terms = (
        "multi-brand", "multiple brands", "brand portfolio", "independent importer",
        "parallel import", "import export", "auto trading", "automotive trading",
        "多品牌", "平行进口", "汽车贸易", "进出口",
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
) -> tuple[int, list[dict], dict, str]:
    lower = clean_text(f"{text} {lead_type}").lower()
    dimensions = {
        "customerFit": 0,
        "tradeQualification": 0,
        "purchaseIntent": 0,
        "businessCapacity": 0,
        "modelFit": 0,
        "contactability": 0,
        "penalty": 0,
    }
    breakdown: list[dict] = []

    def set_dimension(key: str, label: str, points: int):
        if points <= dimensions[key]:
            return
        dimensions[key] = points
        breakdown[:] = [item for item in breakdown if item.get("category") != key]
        breakdown.append({"category": key, "label": label, "points": points})

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
        set_dimension("tradeQualification", "明确具备进出口、海关或贸易许可资质", 30)
    elif any(term in lower for term in (
        "vehicle importer", "car importer", "automotive importer",
        "parallel import", "import and export",
    )):
        set_dimension("tradeQualification", "公开业务显示具备车辆进口经验，资质待核验", 16)

    if any(term in lower for term in ("vehicle importer", "car importer", "automotive importer", "parallel import", "import and export")):
        set_dimension("customerFit", "汽车进口或平行进口客户", 25)
    elif any(term in lower for term in ("distributor", "distribution", "authorized dealer", "exclusive dealer")):
        set_dimension("customerFit", "品牌分销或代理客户", 23)
    elif any(term in lower for term in ("dealer", "dealership", "showroom", "motors", "auto trading", "automotive trading")):
        set_dimension("customerFit", "汽车经销、展厅或贸易客户", 20)
    elif any(term in lower for term in ("fleet", "rental", "chauffeur", "procurement", "corporate buyer")):
        set_dimension("customerFit", "车队、租赁或企业采购客户", 18)
    elif any(term in lower for term in ("automotive", "vehicles", "cars", "auto business")):
        set_dimension("customerFit", "汽车行业相关客户", 10)

    if any(term in lower for term in ("luxury", "premium", "supercar", "range rover", "mercedes", "bmw", "porsche", "bentley")):
        set_dimension("businessCapacity", "经营豪华或高端汽车", 6)
    if any(term in lower for term in ("our brands", "brands we represent", "multi-brand", "wide range of brands", "brand portfolio")):
        set_dimension("businessCapacity", "具备多品牌经营能力", 9)
    if any(term in lower for term in ("branches", "locations", "group of companies", "nationwide", "regional network")):
        set_dimension("businessCapacity", "具备多网点或区域经营能力", 11)
    if google_reviews >= 100:
        set_dimension("businessCapacity", "地图评价量显示经营规模较稳定", 12)
    elif google_reviews >= 20:
        set_dimension("businessCapacity", "地图经营评价较充分", 7)
    elif any(term in lower for term in ("wholesale", "fleet", "corporate sales", "bulk sales")):
        set_dimension("businessCapacity", "具备批发、车队或企业销售能力", 8)

    if any(term in lower for term in BUYING_INTENT_TERMS):
        set_dimension("purchaseIntent", "存在明确采购、询价或招商意向", 18)
    elif any(term in lower for term in ("fleet", "procurement", "wholesale", "bulk order", "corporate sales")):
        set_dimension("purchaseIntent", "存在车队、批发或企业采购场景", 13)
    elif any(term in lower for term in ("new brand", "brand partnership", "new models", "expanding portfolio")):
        set_dimension("purchaseIntent", "存在引入新品牌或扩充车型信号", 11)

    model_lower = requested_model.lower()
    if any(term in lower for term in ("electric vehicle", "electric cars", " ev ", "hybrid", "new energy", "chinese car", "chinese vehicle")):
        set_dimension("modelFit", "经营新能源或中国汽车", 6)
    if any(term in lower for term in ("luxury", "premium", "executive", "vip", "flagship")) and any(
        term in model_lower for term in ("m9", "s800", "s9", "问界", "尊界", "享界")
    ):
        set_dimension("modelFit", "高端客户画像与目标车型匹配", 10)
    elif any(term in lower for term in ("suv", "4x4", "family")) and any(
        term in model_lower for term in ("m9", "m8", "r7", "问界", "智界")
    ):
        set_dimension("modelFit", "SUV 客群与目标车型匹配", 9)
    elif requested_model and dimensions["modelFit"] == 0:
        set_dimension("modelFit", "汽车业务与目标车型存在基础匹配", 3)

    if has_official_website:
        set_dimension("contactability", "可核验企业官网", 2)
    if has_contact:
        set_dimension("contactability", "存在公开商业联系方式", 4)
    if re.search(r"\b(owner|founder|director|general manager|procurement manager|purchasing manager)\b", lower):
        set_dimension("contactability", "发现公开决策人或采购岗位", 5)

    if re.search(r"\b(repair|workshop|spare parts|car wash|detailing|tyres?)\b", lower) and not re.search(
        r"\b(importer|distributor|dealer|dealership|showroom|vehicle sales)\b", lower
    ):
        dimensions["penalty"] -= 45
        breakdown.append({"category": "penalty", "label": "仅维修、配件或美容业务", "points": -45})
    if re.search(r"\b(classifieds?|marketplace|individual seller|private seller)\b", lower):
        dimensions["penalty"] -= 55
        breakdown.append({"category": "penalty", "label": "交易平台或个人卖家特征", "points": -55})
    if is_competitor or detect_competitor(lower):
        dimensions["penalty"] -= 70
        breakdown.append({"category": "penalty", "label": "中国汽车出口同行特征", "points": -70})

    score = sum(dimensions.values())
    score = max(0, min(score, 100))
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
    except (OSError, ValueError, TimeoutError, urllib.error.URLError):
        return []

    def inspect(seed: dict) -> list[dict]:
        website = normalize_public_url(seed.get("customer_website") or seed.get("url") or "")
        if not website:
            return []
        try:
            page, final_url = fetch_document(website, timeout=12)
        except (OSError, TimeoutError, UnicodeError, urllib.error.URLError):
            return []
        meta = extract_meta(page)
        contacts = extract_public_contacts(page, seed.get("tags"))
        company = clean_text(seed.get("title") or urllib.parse.urlparse(final_url).netloc)[:180]
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
            except (OSError, ValueError, TimeoutError, urllib.error.URLError):
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
    result_limit_value = (params.get("resultLimit") or ["90"])[0]
    result_limit = max(10, min(90, int(result_limit_value) if result_limit_value.isdigit() else 90))
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
    cities = discovery_cities(country, city_focus)
    market = city_focus or country.split(" ")[0]
    broad_business_query = (
        f"{market} automotive importer vehicle distributor car dealer showroom "
        f"parallel import auto trading official website contact {exclude_query}{cutoff_query}"
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
        f"official website contact {exclude_query}{cutoff_query}"
    ).strip()
    commercial_query_variants = [
        broad_business_query,
        intent_query,
        china_ev_query,
        query,
        f"{market} \"auto trading\" OR \"automobile trading\" car showroom import export official website {exclude_query}{cutoff_query}",
        f"{market} luxury car importer exporter \"new cars\" \"vehicle sourcing\" official website contact {exclude_query}{cutoff_query}",
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
            f"{city_focus} car dealer showroom importer WhatsApp email official website {exclude_query}{cutoff_query}"
        )
    for city in cities[:8]:
        commercial_query_variants.extend([
            f"{city} car dealers directory showroom motors contact website {exclude_query}{cutoff_query}",
            f"{city} auto trading LLC motors showroom WhatsApp email {exclude_query}{cutoff_query}",
            f"{city} used cars showroom dealer official website phone {exclude_query}{cutoff_query}",
            f"{city} imported cars luxury motors dealership contact {exclude_query}{cutoff_query}",
        ])
    commercial_query_variants.extend(
        city_keyword_queries(cities, DISCOVERY_KEYWORD_TERMS, f"official website contact {exclude_query}{cutoff_query}")
    )

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
            google_city_limit = min(6, max(3, result_limit // max(2, len(cities) * 2)))
            for city in cities:
                raw_results += search_google_places(
                    country,
                    "car dealer automotive importer vehicle distributor electric vehicle showroom",
                    limit=google_city_limit,
                    city=city,
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
        search_variants = list(dict.fromkeys(commercial_query_variants))
        max_web_queries = 72 if source_mode in ("all", "combined") else 96
        search_variants = search_variants[:max_web_queries]
        per_query_limit = 12 if source_mode in ("all", "combined") else 16
        web_results_by_query: list[list[dict]] = []
        with ThreadPoolExecutor(max_workers=min(4, len(search_variants))) as executor:
            futures = [
                executor.submit(search_web, search_query, per_query_limit, freshness_days)
                for search_query in search_variants
            ]
            for future in as_completed(futures):
                try:
                    web_results_by_query.append(future.result())
                except (OSError, ValueError, TimeoutError, urllib.error.URLError):
                    continue
        for web_results in web_results_by_query:
            try:
                for item in web_results:
                    origin, source_type = source_details(item["url"])
                    item["origin"] = origin
                    item["source_type"] = source_type
                    item["source_url"] = item["url"]
                    item["customer_website"] = item["url"]
                raw_results += web_results
            except (OSError, ValueError, TimeoutError, KeyError):
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
        "telegram": ("t.me", "Telegram", "Telegram 公开频道或群组"),
        "twitter": ("x.com", "X / Twitter", "X / Twitter 公开主页或帖子"),
        "threads": ("threads.net", "Threads", "Threads 公开主页"),
        "pinterest": ("pinterest.com", "Pinterest", "Pinterest 公开主页"),
        "reddit": ("reddit.com", "Reddit", "Reddit 公开社区或用户"),
        "vk": ("vk.com", "VK", "VK 公开主页"),
    }
    selected_platforms = (
        list(platform_queries)
        if source_mode in ("all", "social", "combined")
        else [source_mode] if source_mode in platform_queries else []
    )
    platform_queries.update({
        "instagram": ("instagram.com", "Instagram", "Instagram 公开主页或内容"),
        "facebook": ("facebook.com", "Facebook", "Facebook 公开主页、群组或内容"),
        "tiktok": ("tiktok.com", "TikTok", "TikTok 公开账号或视频"),
        "linkedin": ("linkedin.com", "LinkedIn", "LinkedIn 公司、个人或动态"),
        "telegram": ("t.me", "Telegram", "Telegram 公开频道或群组"),
        "twitter": ("x.com", "X / Twitter", "X / Twitter 公开主页或帖子"),
        "threads": ("threads.net", "Threads", "Threads 公开主页或内容"),
        "pinterest": ("pinterest.com", "Pinterest", "Pinterest 公开主页、图板或内容"),
        "reddit": ("reddit.com", "Reddit", "Reddit 公开社区、用户或帖子"),
        "vk": ("vk.com", "VK", "VK 公开主页或内容"),
    })
    role_query = "dealership owner import manager sales director" if account_scope in ("person", "both") else ""
    company_query = "car dealer importer automotive trading" if account_scope in ("company", "both") else ""
    social_search_stats = {
        "queries": 0,
        "rawResults": 0,
        "profileResults": 0,
        "acceptedResults": 0,
        "officialWebsiteProfiles": 0,
    }
    reverse_platforms = set(selected_platforms)
    if source_mode in ("all", "combined", "social", "youtube"):
        reverse_platforms.add("youtube")
    if reverse_platforms:
        website_social_results = social_accounts_from_business_websites(
            country,
            target_type,
            reverse_platforms,
            seed_limit=min(24, result_limit),
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
            query_variants = query_variants[:8]
        elif source_mode == "social":
            query_variants = query_variants[:12]
        social_search_stats["queries"] += len(query_variants)
        social_results: list[dict] = []
        with ThreadPoolExecutor(max_workers=min(3, max(1, len(query_variants)))) as executor:
            futures = [
                executor.submit(
                    search_web,
                    search_query,
                    4 if source_mode == "combined" else 8,
                    freshness_days,
                )
                for search_query in query_variants
            ]
            for future in as_completed(futures):
                try:
                    social_results.extend(future.result())
                except (OSError, ValueError, TimeoutError, urllib.error.URLError):
                    continue
        social_search_stats["rawResults"] += len(social_results)
        expected_domains = {
            "instagram": ("instagram.com",),
            "facebook": ("facebook.com", "fb.com"),
            "tiktok": ("tiktok.com",),
            "linkedin": ("linkedin.com",),
            "telegram": ("t.me", "telegram.me", "telegram.dog"),
            "twitter": ("x.com", "twitter.com"),
            "threads": ("threads.net",),
            "pinterest": ("pinterest.",),
            "reddit": ("reddit.com",),
            "vk": ("vk.com",),
        }.get(platform, (site.split("/")[0],))
        seen_platform_urls: set[str] = set()
        for item in social_results:
            item_url = normalize_social_profile_url(item.get("url", ""))
            item_domain = urllib.parse.urlparse(item_url).netloc.lower().removeprefix("www.")
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
            item["url"] = item_url
            item["origin"] = origin
            item["source_type"] = source_type
            item["source_url"] = item_url
            item["customer_website"] = ""
            item["skip_fetch"] = True
            path = urllib.parse.urlparse(item_url).path.lower()
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
    if source_mode in ("all", "combined", "youtube", "social"):
        youtube_searches = []
        city = next(
            (cities[0] for key, cities in COUNTRY_HINTS.items() if key.lower() in country.lower()),
            country.split(" ")[0],
        )
        if account_scope in ("company", "both"):
            youtube_searches.append(
                (f"{city} car dealer", "公司账号")
            )
        if account_scope in ("person", "both"):
            youtube_searches.append(
                (f"{city} car dealer owner manager", "个人/经营者账号（待核验）")
            )
        youtube_searches = []
        if account_scope in ("company", "both"):
            youtube_searches.extend(
                (query, "company account")
                for query in city_keyword_queries(cities, DISCOVERY_KEYWORD_TERMS)
            )
        if account_scope in ("person", "both"):
            youtube_searches.extend(
                (query, "owner or manager account")
                for query in city_keyword_queries(cities, DISCOVERY_KEYWORD_TERMS, "owner manager founder")
            )
        max_youtube_queries = 45 if source_mode == "youtube" else 32
        youtube_searches = list(dict.fromkeys(youtube_searches))[:max_youtube_queries]
        for youtube_query, youtube_account_type in youtube_searches:
            try:
                youtube_items = search_youtube_channels(youtube_query, limit=25)
            except (OSError, ValueError, TimeoutError, json.JSONDecodeError):
                youtube_items = []
            for item in youtube_items:
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
                youtube_discovery_candidate = bool(re.search(
                    r"\b(car|cars|dealer|dealership|motors|automotive|vehicle|vehicles|showroom|auto)\b",
                    f"{item.get('title', '')} {item.get('snippet', '')}",
                    re.I,
                ))
                youtube_discovery_candidate = True
                if (
                    not any(term and term in location_text for term in location_terms)
                    and not youtube_analysis.get("isCommercial")
                    and not youtube_discovery_candidate
                ):
                    continue
                item["origin"] = "YouTube"
                item["source_type"] = "YouTube 公开频道" if youtube_analysis.get("isCommercial") else "YouTube 公开频道（待核验）"
                item["source_url"] = item["url"]
                item["customer_website"] = ""
                item["account_type"] = youtube_account_type
                item["social_analysis"] = youtube_analysis
                item["youtube_discovery_candidate"] = youtube_discovery_candidate
                raw_results.append(item)
    raw_results = balance_discovery_sources(raw_results)
    leads = []
    seen_sources = set()
    excluded_brand_bound_dealers = 0
    for item in raw_results:
        if len(leads) >= result_limit:
            break
        parsed = urllib.parse.urlparse(item["url"])
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
            continue
        allow_recent_content = bool(freshness_days) or target_type in ("buying", "government", "individual")
        if not is_social_result and any(word in title_lower for word in BLOCKED_TITLE_WORDS) and not allow_recent_content:
            continue
        if not is_social_result and any(part in path_lower for part in BLOCKED_PATH_PARTS) and not allow_recent_content:
            continue
        if not is_social_result and re.search(r"/20\d{2}/\d{1,2}/\d{1,2}/", path_lower) and not allow_recent_content:
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
        origin_name = item.get("origin", "")
        is_raw_social_or_video_source = origin_name in (
            "Facebook", "Instagram", "TikTok", "LinkedIn", "YouTube",
            "Telegram", "X / Twitter", "Threads", "Pinterest", "Reddit", "VK",
        )
        if not item.get("skip_fetch") and not is_raw_social_or_video_source:
            try:
                page = fetch_text(item["url"], timeout=8)
                page_text = extract_meta(page)
                contact = contact or extract_contact(page_text)
            except (OSError, TimeoutError, UnicodeError):
                pass

        combined = f"{item['title']} {item['snippet']} {page_text}"
        if is_obviously_irrelevant_lead(combined):
            continue
        if not is_social_result and is_brand_bound_chinese_dealer(combined):
            excluded_brand_bound_dealers += 1
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
            social_search_stats["acceptedResults"] += 1
        if not is_google_places and item.get("origin") != "OpenStreetMap" and not is_social_result:
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
        if not is_social_result and not re.search(
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
        is_competitor = detect_competitor(combined)
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
        source_contact_text = f"{item.get('snippet', '')} {item.get('title', '')}"
        contacts = extract_public_contacts(source_contact_text, item.get("tags"))
        if not any(contacts.get(key) for key in ("email", "phone", "whatsapp")) and page:
            contacts = extract_public_contacts(page_text, item.get("tags"))
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
            {"value": phone, "sources": [{"url": source_url, "name": origin, "excerpt": source_excerpt[:260]}]}
            for phone in contacts.get("phones") or ([contacts["phone"]] if contacts["phone"] else [])
        ]
        whatsapp_sources = [
            {"value": value, "sources": [{"url": source_url, "name": origin, "excerpt": source_excerpt[:260]}]}
            for value in contacts.get("whatsapps") or ([contacts["whatsapp"]] if contacts["whatsapp"] else [])
        ]
        recommended_models = recommend_models(combined, model)
        score, score_breakdown, score_dimensions, score_tier = lead_opportunity_score(
            combined,
            bool(customer_website),
            bool(verified_email_sources or phone_sources or whatsapp_sources),
            int(item.get("google_reviews") or 0),
            requested_model=model,
            lead_type=lead_type,
            is_competitor=is_competitor,
        )
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
                        "accountType": social_analysis.get("accountType") or item.get("account_type", "公司账号"),
                        "relationship": item.get("official_relationship") or f"{origin} 公开结果",
                        "title": source_title,
                        "description": source_excerpt[:700],
                        "url": item["url"],
                        "handle": urllib.parse.urlparse(item["url"]).path.strip("/").split("/")[-1],
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
                "baseScore": score,
                "scoreModelVersion": 6,
                "scoreTier": score_tier,
                "scoreDimensions": score_dimensions,
                "scoreBreakdown": score_breakdown,
                "scoreBasis": "100分机会模型：进出口资质30、客户匹配25、采购意向18、经营能力12、车型匹配10、可触达性5，另计风险扣分",
                "stage": "准备联系" if score >= 80 else "待审核",
                "next": "生成英文开发信并人工确认",
                "website": combined[:1000],
                "reason": reason,
            }
        )
    if source_mode == "social" and not leads:
        notice = (
            f"五平台共执行 {social_search_stats['queries']} 组短词搜索，"
            f"搜索引擎返回 {social_search_stats['rawResults']} 条，"
            f"企业官网反向发现 {social_search_stats['officialWebsiteProfiles']} 个社媒账号，"
            f"其中 {social_search_stats['profileResults']} 条为账号主页，"
            f"{social_search_stats['acceptedResults']} 条通过商业账号初筛。"
            "若仍为 0，通常是搜索引擎未收录当地账号；可改用单个平台搜索或本机 Chrome 登录态采集。"
        )
    if source_mode == "telegram" and not leads:
        notice = (
            f"Telegram 公开搜索已执行 {social_search_stats['queries']} 组 t.me 查询，"
            f"搜索引擎返回 {social_search_stats['rawResults']} 条候选，"
            f"其中 {social_search_stats['profileResults']} 条可识别为公开频道或群组。"
            "如果仍为 0，通常是 Telegram 频道/群没有被 Google、Bing、DuckDuckGo 或 Brave 收录；"
            "Telegram 没有免费的全网官方搜索 API，建议把 Telegram 作为补充来源，主来源继续使用 Google Maps、YouTube 和官网目录。"
        )
    if excluded_brand_bound_dealers:
        notice = (notice + " " if notice else "") + f"已排除 {excluded_brand_bound_dealers} 家已绑定中国主机厂的单品牌 4S/授权店。"
    if freshness_days and not leads and not notice:
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
        # Prefer the record with a public contact method or a higher opportunity score.
        existing_contactable = bool(existing.get("email") or existing.get("phone") or existing.get("whatsapp"))
        lead_contactable = bool(lead.get("email") or lead.get("phone") or lead.get("whatsapp"))
        if (lead_contactable and not existing_contactable) or int(lead.get("score", 0)) > int(existing.get("score", 0)):
            lead["evidenceSources"] = existing_sources
            lead["sourceCoverage"]["total"] = len(existing_sources)
            merged_leads[company_key] = lead
    leads = list(merged_leads.values())
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
            user = self.current_user()
            self.send_json(
                200,
                {
                    "ok": True,
                    "authenticated": bool(user),
                    "username": user.get("username", "") if user else "",
                    "role": user.get("role", "") if user else "",
                },
            )
            return
        if parsed.path == "/api/discovery-sources":
            if not self.require_auth(api=True):
                return
            google_ready = bool(get_google_maps_api_key())
            youtube_ready = bool(os.environ.get("YOUTUBE_API_KEY", "").strip())
            self.send_json(200, {
                "ok": True,
                "sources": {
                    "googleMaps": {
                        "available": google_ready,
                        "label": "Google Maps Places API",
                        "message": "已连接官方企业数据" if google_ready else "未配置 API Key，综合搜索将跳过 Google Maps"
                    },
                    "web": {"available": True, "label": "Bing + DuckDuckGo + Brave"},
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
                user = authenticate_user(username, password)
                if not user:
                    self.send_json(401, {"ok": False, "error": "账户名或密码错误"})
                    return
                token = create_session_token(user["username"])
                body = json.dumps({"ok": True, "username": user["username"], "role": user["role"]}, ensure_ascii=False).encode("utf-8")
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
        if parsed.path == "/api/users":
            if not self.require_admin():
                return
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                user = create_user(str(payload.get("username", "")), str(payload.get("password", "")))
                self.send_json(201, {"ok": True, "user": user})
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
                    self.send_json(200, {"ok": True})
                else:
                    user = update_user(username, password=payload.get("password"), status=payload.get("status"))
                    self.send_json(200, {"ok": True, "user": {key: value for key, value in user.items() if key != "passwordHash"}})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/workspace-state":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 20_500_000)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                expected_version = payload.get("expectedVersion")
                if expected_version is not None:
                    expected_version = int(expected_version)
                result = save_workspace_state(
                    self.current_user()["username"], payload.get("state", payload),
                    expected_version=expected_version,
                )
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
                job = create_discovery_job(payload, self.current_user()["username"])
                self.send_json(202, {"ok": True, "job": job})
            except (ValueError, json.JSONDecodeError, OSError, RuntimeError, sqlite3.Error) as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            return
        if parsed.path == "/api/discover/mark-imported":
            try:
                content_length = min(int(self.headers.get("Content-Length", "0")), 16_384)
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                job = mark_discovery_job_imported(str(payload.get("id", "")), self.current_user()["username"])
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
                job = create_discovery_job(previous.get("payload") or {}, self.current_user()["username"], force=True)
                self.send_json(202, {"ok": True, "job": job})
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


if __name__ == "__main__":
    initialize_state_store()
    resumed_jobs = resume_interrupted_discovery_jobs()
    with ReusableThreadingTCPServer((HOST, PORT), Handler) as httpd:
        display_host = "127.0.0.1" if HOST == "0.0.0.0" else HOST
        print(f"获客工作台已启动：http://{display_host}:{PORT}/index.html")
        if resumed_jobs:
            print(f"已恢复 {resumed_jobs} 个中断的获客任务。")
        httpd.serve_forever()

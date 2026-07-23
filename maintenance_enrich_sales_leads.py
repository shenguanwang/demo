import argparse
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_runtime_environment() -> None:
    os.environ.setdefault("STATE_DATABASE_PATH", str(ROOT / "data" / "workbench-state.db"))
    launcher = ROOT / "run-server.ps1"
    if not launcher.exists():
        return
    for line in launcher.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip().removeprefix("$env:")
        if name in {"DEEPSEEK_API_KEY", "GOOGLE_MAPS_API_KEY", "BRAVE_SEARCH_API_KEY", "HUNTER_API_KEY"}:
            os.environ.setdefault(name, value.strip().strip("\"'"))


load_runtime_environment()
sys.path.insert(0, str(ROOT))

import server  # noqa: E402
from maintenance_reevaluate_sales_ai import evaluate_lead, review_is_complete  # noqa: E402


CONTACT_FIELDS = ("email", "phone", "whatsapp")
SAVE_LOCKS: dict[str, threading.Lock] = {}


def eligible_sales_users() -> list[dict]:
    return [
        user
        for user in server.list_users()
        if user.get("role") != "admin" and user.get("status") != "disabled"
    ]


def value_present(lead: dict, field: str) -> bool:
    return bool(str(lead.get(field) or "").strip())


def needs_contact_enrichment(lead: dict, scope: str, retry_researched: bool = False) -> bool:
    if lead.get("researchAt") and not retry_researched:
        return False
    present = sum(value_present(lead, field) for field in CONTACT_FIELDS)
    if scope == "none":
        return False
    if scope == "empty":
        return present == 0
    return present < len(CONTACT_FIELDS)


def stable_lead_key(lead: dict, bucket: str, index: int) -> str:
    for field in ("id", "leadId"):
        value = str(lead.get(field) or "").strip()
        if value:
            return f"{field}:{value}"
    for field in ("sourceUrl", "profileUrl", "customerWebsite", "website"):
        value = server.normalize_public_url(str(lead.get(field) or ""))
        if value:
            return f"url:{value.lower().rstrip('/')}"
    return "|".join(
        (
            bucket,
            str(lead.get("company") or "").strip().lower(),
            str(lead.get("country") or "").strip().lower(),
            str(index),
        )
    )


def merge_email_sources(existing: list, incoming: list) -> list:
    merged: dict[str, dict] = {}
    for record in [*(existing or []), *(incoming or [])]:
        if not isinstance(record, dict):
            continue
        email = str(record.get("email") or record.get("value") or "").strip().lower()
        if not email:
            continue
        target = merged.setdefault(email, {"email": email, "sources": []})
        seen_urls = {
            str(source.get("url") or "").lower().rstrip("/")
            for source in target["sources"]
            if isinstance(source, dict)
        }
        for source in record.get("sources") or []:
            if not isinstance(source, dict):
                continue
            url_key = str(source.get("url") or "").lower().rstrip("/")
            if url_key and url_key in seen_urls:
                continue
            target["sources"].append(source)
            if url_key:
                seen_urls.add(url_key)
    return list(merged.values())[:20]


def merge_value_sources(existing: list, incoming: list) -> list:
    merged: dict[str, dict] = {}
    for record in [*(existing or []), *(incoming or [])]:
        if not isinstance(record, dict):
            continue
        value = str(record.get("value") or "").strip()
        digits = "".join(character for character in value if character.isdigit())
        key = digits if len(digits) >= 7 else value.lower()
        if not key:
            continue
        target = merged.setdefault(key, {"value": value, "sources": []})
        seen_urls = {
            str(source.get("url") or "").lower().rstrip("/")
            for source in target["sources"]
            if isinstance(source, dict)
        }
        for source in record.get("sources") or []:
            if not isinstance(source, dict):
                continue
            url_key = str(source.get("url") or "").lower().rstrip("/")
            if url_key and url_key in seen_urls:
                continue
            target["sources"].append(source)
            if url_key:
                seen_urls.add(url_key)
    return list(merged.values())[:20]


def verified_research_patch(lead: dict, result: dict) -> dict:
    patch: dict = {}
    if not value_present(lead, "email") and result.get("email") and result.get("emailSources"):
        patch["email"] = result["email"]
    if not value_present(lead, "phone") and result.get("phone") and result.get("phoneSources"):
        patch["phone"] = result["phone"]
    if not value_present(lead, "whatsapp") and result.get("whatsapp") and result.get("whatsappSources"):
        patch["whatsapp"] = result["whatsapp"]

    email_sources = merge_email_sources(lead.get("emailSources") or [], result.get("emailSources") or [])
    phone_sources = merge_value_sources(lead.get("phoneSources") or [], result.get("phoneSources") or [])
    whatsapp_sources = merge_value_sources(lead.get("whatsappSources") or [], result.get("whatsappSources") or [])
    if email_sources:
        patch["emailSources"] = email_sources
    if phone_sources:
        patch["phoneSources"] = phone_sources
    if whatsapp_sources:
        patch["whatsappSources"] = whatsapp_sources

    if not str(lead.get("customerWebsite") or "").strip():
        coverage = result.get("sourceCoverage") if isinstance(result.get("sourceCoverage"), dict) else {}
        if result.get("customerWebsite") and coverage.get("official"):
            patch["customerWebsite"] = result["customerWebsite"]

    for field in (
        "contactName",
        "contactRole",
        "contactNameSources",
        "contactRoleSources",
        "evidenceSources",
        "socialAccounts",
        "socialProfiles",
        "sourceCoverage",
        "researchSummary",
    ):
        if result.get(field):
            patch[field] = result[field]
    if result.get("researchAt"):
        patch["researchAt"] = result["researchAt"]
    return patch


def research_lead(lead: dict) -> dict:
    social_urls = [
        *(lead.get("socialAccounts") or []),
        *[
            item.get("url")
            for item in (lead.get("socialProfiles") or [])
            if isinstance(item, dict) and item.get("url")
        ],
        *[
            item.get("url")
            for item in (lead.get("evidenceSources") or [])
            if isinstance(item, dict) and item.get("url")
        ],
    ]
    params = {
        "company": [str(lead.get("company") or "")],
        "country": [", ".join(filter(None, (str(lead.get("city") or ""), str(lead.get("country") or ""))))],
        "website": [str(lead.get("customerWebsite") or lead.get("website") or "")],
        "sourceUrl": [str(lead.get("sourceUrl") or lead.get("profileUrl") or "")],
        "socialUrls": [" | ".join(dict.fromkeys(str(url) for url in social_urls if url))],
        "model": [str(lead.get("model") or "")],
        "type": [str(lead.get("type") or "")],
        "mode": ["fast"],
        "inferWebsite": ["1"],
    }
    return server.research_company(params)


def apply_patch_to_current_lead(username: str, target_key: str, patch: dict) -> bool:
    lock = SAVE_LOCKS.setdefault(username, threading.Lock())
    with lock:
        for _ in range(3):
            workspace = server.load_workspace_state(username)
            state = workspace.get("state") or server.empty_workspace_state()
            target = None
            for bucket in ("reviewLeads", "customers"):
                for index, lead in enumerate(state.get(bucket) or []):
                    if isinstance(lead, dict) and stable_lead_key(lead, bucket, index) == target_key:
                        target = lead
                        break
                if target is not None:
                    break
            if target is None:
                return False
            for field, value in patch.items():
                if field in CONTACT_FIELDS and value_present(target, field):
                    continue
                if field == "aiReview" and review_is_complete(target):
                    continue
                target[field] = value
            try:
                server.save_workspace_state(username, state, expected_version=workspace.get("version"))
                return True
            except server.WorkspaceVersionConflict:
                continue
    return False


def collect_targets(contact_scope: str, include_profile: bool, retry_researched: bool = False) -> list[dict]:
    targets = []
    for user in eligible_sales_users():
        username = user["username"]
        state = server.load_workspace_state(username).get("state") or {}
        for bucket in ("reviewLeads", "customers"):
            for index, lead in enumerate(state.get(bucket) or []):
                if not isinstance(lead, dict):
                    continue
                contact_needed = needs_contact_enrichment(lead, contact_scope, retry_researched)
                profile_needed = include_profile and not review_is_complete(lead)
                if contact_needed or profile_needed:
                    targets.append(
                        {
                            "username": username,
                            "bucket": bucket,
                            "index": index,
                            "key": stable_lead_key(lead, bucket, index),
                            "lead": lead,
                            "contactNeeded": contact_needed,
                            "profileNeeded": profile_needed,
                        }
                    )
    return targets


def process_target(target: dict) -> dict:
    lead = dict(target["lead"])
    patch: dict = {}
    result = {}
    error = ""
    if target["contactNeeded"]:
        try:
            result = research_lead(lead)
            patch.update(verified_research_patch(lead, result))
            lead.update(patch)
        except Exception as exc:
            error = str(exc)[:300]
    if target["profileNeeded"] and not review_is_complete(lead):
        try:
            review = evaluate_lead(lead)
            if review and review.get("reason") and isinstance(review.get("customerProfile"), dict):
                patch["aiReview"] = review
                patch["aiReevaluatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        except Exception as exc:
            error = error or str(exc)[:300]
    changed_contacts = [
        field
        for field in CONTACT_FIELDS
        if patch.get(field) and not value_present(target["lead"], field)
    ]
    saved = bool(patch) and apply_patch_to_current_lead(target["username"], target["key"], patch)
    return {
        "sales": target["username"],
        "company": str(lead.get("company") or "")[:100],
        "saved": saved,
        "contacts": changed_contacts,
        "profile": bool(patch.get("aiReview")),
        "error": error,
    }


def scan_summary(targets: list[dict]) -> dict:
    return {
        "targets": len(targets),
        "contactTargets": sum(target["contactNeeded"] for target in targets),
        "profileTargets": sum(target["profileNeeded"] for target in targets),
        "sales": {
            username: sum(target["username"] == username for target in targets)
            for username in sorted({target["username"] for target in targets})
        },
    }


def run(
    contact_scope: str,
    include_profile: bool,
    limit: int,
    workers: int,
    execute: bool,
    retry_researched: bool,
) -> dict:
    targets = collect_targets(contact_scope, include_profile, retry_researched)
    if limit > 0:
        targets = targets[:limit]
    summary = scan_summary(targets)
    if not execute:
        return {"mode": "scan", **summary}

    totals = {
        "mode": "execute",
        **summary,
        "processed": 0,
        "saved": 0,
        "profilesAdded": 0,
        "contactsAdded": {"email": 0, "phone": 0, "whatsapp": 0},
        "failed": 0,
    }
    with ThreadPoolExecutor(max_workers=max(1, min(6, workers))) as executor:
        futures = [executor.submit(process_target, target) for target in targets]
        for future in as_completed(futures):
            result = future.result()
            totals["processed"] += 1
            totals["saved"] += int(result["saved"])
            totals["profilesAdded"] += int(result["profile"])
            for field in result["contacts"]:
                totals["contactsAdded"][field] += 1
            if result["error"]:
                totals["failed"] += 1
            print(json.dumps(result, ensure_ascii=False), flush=True)
    totals["remaining"] = scan_summary(collect_targets(contact_scope, include_profile, retry_researched))
    return totals


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--contact-scope", choices=("none", "empty", "any"), default="empty")
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--retry-researched", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.contact_scope,
                args.profile,
                max(0, args.limit),
                max(1, args.workers),
                args.execute,
                args.retry_researched,
            ),
            ensure_ascii=False,
        ),
        flush=True,
    )

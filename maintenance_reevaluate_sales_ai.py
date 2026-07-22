import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_runtime_environment() -> None:
    os.environ.setdefault("STATE_DATABASE_PATH", str(ROOT / "data" / "workbench-state.db"))
    if os.environ.get("DEEPSEEK_API_KEY"):
        return
    launcher = ROOT / "run-server.ps1"
    if not launcher.exists():
        return
    for line in launcher.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "DEEPSEEK_API_KEY" not in line or "=" not in line:
            continue
        value = line.split("=", 1)[1].strip().strip("\"'")
        if value:
            os.environ["DEEPSEEK_API_KEY"] = value
        return


load_runtime_environment()
sys.path.insert(0, str(ROOT))

import server  # noqa: E402


def review_is_complete(lead: dict) -> bool:
    review = lead.get("aiReview")
    if not isinstance(review, dict) or not review.get("reason"):
        return False
    profile = review.get("customerProfile")
    return isinstance(profile, dict) and bool(profile.get("summary"))


def lead_review_text(lead: dict) -> str:
    evidence = {
        "company": lead.get("company"),
        "country": lead.get("country"),
        "city": lead.get("city"),
        "customerWebsite": lead.get("customerWebsite") or lead.get("website"),
        "sourceUrl": lead.get("sourceUrl") or lead.get("profileUrl"),
        "source": lead.get("source") or lead.get("origin"),
        "reason": lead.get("reason"),
        "contactReason": lead.get("contactReason"),
        "businessSignals": lead.get("businessSignals"),
        "intentSignals": lead.get("intentSignals"),
        "socialProfiles": lead.get("socialProfiles"),
        "sourceCoverage": lead.get("sourceCoverage"),
        "sourceTranslation": lead.get("sourceTranslation"),
        "publicContent": lead.get("website"),
    }
    return json.dumps(evidence, ensure_ascii=False, default=str)[:12000]


def evaluate_lead(lead: dict) -> dict:
    review = server.ai_review_lead_candidate(
        company=str(lead.get("company") or ""),
        country=str(lead.get("country") or ""),
        city=str(lead.get("city") or ""),
        source_url=str(lead.get("sourceUrl") or lead.get("profileUrl") or ""),
        customer_website=str(lead.get("customerWebsite") or lead.get("website") or ""),
        origin=str(lead.get("source") or lead.get("origin") or "historical lead"),
        source_type=str(lead.get("sourceType") or lead.get("source") or "public lead data"),
        text=lead_review_text(lead),
    )
    if not review:
        return {}
    minimum = int(server.admin_control_settings().get("quality", {}).get("minimumAiConfidence") or 0)
    return server.apply_ai_confidence_threshold(review, minimum)


def eligible_sales_users() -> list[dict]:
    return [
        user
        for user in server.list_users()
        if user.get("role") != "admin" and user.get("status") != "disabled"
    ]


def count_missing() -> int:
    total = 0
    for user in eligible_sales_users():
        state = server.load_workspace_state(user["username"]).get("state") or {}
        total += sum(
            1
            for bucket in ("reviewLeads", "customers")
            for lead in (state.get(bucket) or [])
            if isinstance(lead, dict) and not review_is_complete(lead)
        )
    return total


def temporarily_raise_call_limit(required_calls: int) -> tuple[dict, int]:
    settings = server.load_admin_settings_file()
    control = server.normalize_admin_control(settings.get(server.ADMIN_CONTROL_KEY), settings.get(server.ADMIN_CONTROL_KEY))
    original_limit = int(control.get("ai", {}).get("dailyCallLimit") or 0)
    calls = int(server.admin_usage_summary().get("deepseek", {}).get("calls") or 0)
    required_limit = calls + required_calls + 20
    if original_limit and original_limit >= required_limit:
        return settings, original_limit
    control["ai"]["dailyCallLimit"] = required_limit
    settings[server.ADMIN_CONTROL_KEY] = control
    server.save_admin_settings_file(settings)
    return settings, original_limit


def restore_call_limit(settings: dict, original_limit: int) -> None:
    control = server.normalize_admin_control(settings.get(server.ADMIN_CONTROL_KEY), settings.get(server.ADMIN_CONTROL_KEY))
    control["ai"]["dailyCallLimit"] = original_limit
    settings[server.ADMIN_CONTROL_KEY] = control
    server.save_admin_settings_file(settings)


def run(limit: int = 0) -> dict:
    if not server.get_deepseek_api_key():
        raise RuntimeError("DeepSeek API key is unavailable in the server runtime configuration")
    missing = count_missing()
    target = min(missing, limit) if limit > 0 else missing
    original_settings, original_limit = temporarily_raise_call_limit(target)
    totals = {"target": target, "reviewed": 0, "failed": 0, "skipped": 0, "sales": {}}
    try:
        remaining = target
        for user in eligible_sales_users():
            if remaining <= 0:
                break
            username = user["username"]
            workspace = server.load_workspace_state(username)
            state = workspace.get("state") or server.empty_workspace_state()
            user_stats = {"reviewed": 0, "failed": 0, "skipped": 0}
            pending_since_save = 0
            for bucket in ("reviewLeads", "customers"):
                for lead in state.get(bucket) or []:
                    if remaining <= 0:
                        break
                    if not isinstance(lead, dict) or review_is_complete(lead):
                        user_stats["skipped"] += 1
                        continue
                    review = evaluate_lead(lead)
                    remaining -= 1
                    if review and review.get("reason") and isinstance(review.get("customerProfile"), dict):
                        lead["aiReview"] = review
                        lead["aiReevaluatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                        user_stats["reviewed"] += 1
                        pending_since_save += 1
                    else:
                        user_stats["failed"] += 1
                    if pending_since_save >= 10:
                        server.save_workspace_state(username, state)
                        pending_since_save = 0
                        print(json.dumps({"sales": username, **user_stats}, ensure_ascii=False), flush=True)
            if pending_since_save:
                server.save_workspace_state(username, state)
            totals["sales"][username] = user_stats
            totals["reviewed"] += user_stats["reviewed"]
            totals["failed"] += user_stats["failed"]
            totals["skipped"] += user_stats["skipped"]
            print(json.dumps({"salesComplete": username, **user_stats}, ensure_ascii=False), flush=True)
    finally:
        restore_call_limit(original_settings, original_limit)
    totals["remainingMissing"] = count_missing()
    return totals


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    print(json.dumps(run(max(0, args.limit)), ensure_ascii=False), flush=True)

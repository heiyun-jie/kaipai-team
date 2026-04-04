import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "ai-resume-notification.env"
DEFAULT_SECRET_ENV_KEYS = [
    "AI_RESUME_NOTIFICATION_ENABLED",
    "AI_RESUME_NOTIFICATION_PROVIDER_CODE",
    "AI_RESUME_NOTIFICATION_CALLBACK_HEADER",
    "AI_RESUME_NOTIFICATION_CALLBACK_TOKEN",
]
PLACEHOLDER_PATTERNS = [
    re.compile(r"replace[-_ ]?with[-_ ]?real", re.I),
    re.compile(r"fake", re.I),
    re.compile(r"dummy", re.I),
    re.compile(r"changeme", re.I),
    re.compile(r"example", re.I),
    re.compile(r"placeholder", re.I),
    re.compile(r"todo", re.I),
    re.compile(r"test", re.I),
    re.compile(r"sample", re.I),
]
DEFAULT_CALLBACK_HEADER = "X-Kaipai-Ai-Notification-Token"


def parse_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def resolve_secret_values(secret_file: Path, keys: list[str]) -> dict[str, str]:
    env_values = {key: os.environ.get(key) or "" for key in keys}
    secret_values = parse_dotenv(secret_file)
    resolved: dict[str, str] = {}
    for key in keys:
        value = env_values.get(key) or secret_values.get(key) or ""
        if value:
            resolved[key] = value
    return resolved


def has_placeholder(value: str | None) -> bool:
    normalized = (value or "").strip()
    if not normalized:
        return False
    lowered = normalized.lower()
    return any(pattern.search(lowered) for pattern in PLACEHOLDER_PATTERNS)


def validate_secret_value(key: str, value: str | None) -> list[str]:
    normalized = (value or "").strip()
    if not normalized:
        return ["missing"]

    if key == "AI_RESUME_NOTIFICATION_ENABLED":
        if normalized.lower() not in {"true", "false"}:
            return ["invalid_boolean"]
        if normalized.lower() != "true":
            return ["disabled"]
        return []

    if key == "AI_RESUME_NOTIFICATION_PROVIDER_CODE":
        if has_placeholder(normalized):
            return ["placeholder_provider_code"]
        return []

    if key == "AI_RESUME_NOTIFICATION_CALLBACK_HEADER":
        if has_placeholder(normalized):
            return ["placeholder_callback_header"]
        if len(normalized) < 8:
            return ["header_too_short"]
        return []

    if key == "AI_RESUME_NOTIFICATION_CALLBACK_TOKEN":
        if has_placeholder(normalized):
            return ["placeholder_callback_token"]
        if len(normalized) < 16:
            return ["token_too_short"]
        return []

    return []


def validate_required_secret_values(values: dict[str, str | None], keys: list[str] | None = None) -> dict[str, list[str]]:
    target_keys = keys or DEFAULT_SECRET_ENV_KEYS
    return {key: validate_secret_value(key, values.get(key)) for key in target_keys}

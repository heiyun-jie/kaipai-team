import os
from pathlib import Path

from ai_notification_secret_inputs import has_placeholder, parse_dotenv


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "ai-notification-http-bridge.env"
DEFAULT_SECRET_ENV_KEYS = [
    "AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE",
    "AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT",
    "AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL",
    "AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH",
    "AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER",
    "AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN",
]
DEFAULT_EXPECTED_PROVIDER_CODE = "http"
DEFAULT_CALLBACK_PATH = "/internal/ai/resume/notification-receipts/provider"
DEFAULT_AUTH_HEADER = "Authorization"


def resolve_secret_values(secret_file: Path, keys: list[str]) -> dict[str, str]:
    env_values = {key: os.environ.get(key) or "" for key in keys}
    secret_values = parse_dotenv(secret_file)
    resolved: dict[str, str] = {}
    for key in keys:
        value = env_values.get(key) or secret_values.get(key) or ""
        if value:
            resolved[key] = value
    return resolved


def validate_secret_value(key: str, value: str | None) -> list[str]:
    normalized = (value or "").strip()
    if not normalized:
        return ["missing"]

    if key == "AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE":
        if has_placeholder(normalized):
            return ["placeholder_provider_code"]
        if normalized.lower() != DEFAULT_EXPECTED_PROVIDER_CODE:
            return ["unsupported_provider_code"]
        return []

    if key in {"AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT", "AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL"}:
        if has_placeholder(normalized):
            return ["placeholder_url"]
        if not normalized.lower().startswith(("http://", "https://")):
            return ["invalid_url"]
        return []

    if key == "AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH":
        if has_placeholder(normalized):
            return ["placeholder_callback_path"]
        if not normalized.startswith("/"):
            return ["callback_path_must_start_with_slash"]
        if " " in normalized:
            return ["callback_path_has_spaces"]
        return []

    if key == "AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER":
        if has_placeholder(normalized):
            return ["placeholder_auth_header"]
        if len(normalized) < 3:
            return ["header_too_short"]
        return []

    if key == "AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN":
        if has_placeholder(normalized):
            return ["placeholder_auth_token"]
        if len(normalized) < 8:
            return ["token_too_short"]
        return []

    return []


def validate_required_secret_values(values: dict[str, str | None], keys: list[str] | None = None) -> dict[str, list[str]]:
    target_keys = keys or DEFAULT_SECRET_ENV_KEYS
    validation = {key: validate_secret_value(key, values.get(key)) for key in target_keys}

    auth_header = (values.get("AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER") or "").strip()
    auth_token = (values.get("AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN") or "").strip()
    if auth_token and not auth_header:
        validation["AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER"] = ["missing_auth_header"]
    elif not auth_token:
        validation["AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER"] = []
        validation["AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN"] = []

    return validation


def build_derived_runtime_values(values: dict[str, str | None]) -> dict[str, str]:
    callback_base_url = (values.get("AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL") or "").strip().rstrip("/")
    callback_path = (values.get("AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH") or "").strip() or DEFAULT_CALLBACK_PATH
    callback_url = ""
    if callback_base_url and callback_path.startswith("/"):
        callback_url = f"{callback_base_url}{callback_path}"

    derived = {
        "AI_RESUME_NOTIFICATION_PROVIDER_CODE": DEFAULT_EXPECTED_PROVIDER_CODE,
        "AI_RESUME_NOTIFICATION_CALLBACK_URL": callback_url,
        "AI_RESUME_NOTIFICATION_HTTP_ENDPOINT": (values.get("AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT") or "").strip(),
        "AI_RESUME_NOTIFICATION_HTTP_AUTH_HEADER": (values.get("AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER") or "").strip(),
        "AI_RESUME_NOTIFICATION_HTTP_AUTH_TOKEN": (values.get("AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN") or "").strip(),
    }
    return {key: value for key, value in derived.items() if value}

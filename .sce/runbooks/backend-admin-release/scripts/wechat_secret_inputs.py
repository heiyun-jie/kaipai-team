import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "wechat-miniapp.env"
DEFAULT_SECRET_ENV_KEYS = [
    "WECHAT_MINIAPP_APP_ID",
    "WECHAT_MINIAPP_APP_SECRET",
    "WECHAT_MINIAPP_ENV_VERSION",
]
APP_ID_PATTERN = re.compile(r"^wx[a-zA-Z0-9]{16}$")
PLACEHOLDER_SECRET_PATTERNS = [
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


def validate_secret_value(key: str, value: str | None) -> list[str]:
    normalized = (value or "").strip()
    if not normalized:
        return ["missing"]

    if key == "WECHAT_MINIAPP_APP_ID":
        if not APP_ID_PATTERN.match(normalized):
            return ["invalid_app_id_format"]
        return []

    if key == "WECHAT_MINIAPP_APP_SECRET":
        lowered = normalized.lower()
        for pattern in PLACEHOLDER_SECRET_PATTERNS:
            if pattern.search(lowered):
                return ["placeholder_secret"]
        if len(normalized) < 16:
            return ["secret_too_short"]
        return []

    return []


def validate_required_secret_values(values: dict[str, str | None], keys: list[str] | None = None) -> dict[str, list[str]]:
    target_keys = keys or DEFAULT_SECRET_ENV_KEYS[:2]
    return {key: validate_secret_value(key, values.get(key)) for key in target_keys}

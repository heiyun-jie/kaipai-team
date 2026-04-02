import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "wechat-miniapp.env"
DEFAULT_SECRET_ENV_KEYS = [
    "WECHAT_MINIAPP_APP_ID",
    "WECHAT_MINIAPP_APP_SECRET",
    "WECHAT_MINIAPP_ENV_VERSION",
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


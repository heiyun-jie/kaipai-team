import argparse
import json
import re
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(read_text(path))


def dash(value: Any) -> str:
    if value is None:
        return "--"
    text = str(value).strip()
    if not text:
        return "--"
    return text


def yes_no(value: Any) -> str:
    if value is None:
        return "--"
    return "是" if bool(value) else "否"


def format_datetime(value: Any) -> str:
    text = dash(value)
    if text == "--":
        return text
    return text.replace("T", " ")


def set_field(content: str, label: str, value: str) -> str:
    pattern = rf"(?m)^- {re.escape(label)}:.*$"
    replacement = f"- {label}: {value}"
    if re.search(pattern, content):
        return re.sub(pattern, replacement, content)
    return content.rstrip() + "\n" + replacement + "\n"


def set_list_block(content: str, label: str, items: list[str]) -> str:
    replacement_lines = [f"- {label}:"]
    if items:
        replacement_lines.extend([f"  - {item}" for item in items])
    else:
        replacement_lines.append("  - ")
    replacement = "\n".join(replacement_lines) + "\n"
    pattern = rf"(?ms)^- {re.escape(label)}:\n(?:  - .*\n)*"
    if re.search(pattern, content):
        return re.sub(pattern, replacement, content)
    return content.rstrip() + "\n" + replacement


def infer_metadata(sample_dir: Path) -> dict[str, Any]:
    metadata = load_json(sample_dir / "sample-metadata.json") or {}
    if metadata:
        return metadata

    name = sample_dir.name
    match = re.match(r"^\d{8}-\d{6}-(?P<environment>[^-]+)-(?P<label>.+)$", name)
    if match:
        return {
            "environmentName": match.group("environment"),
            "sampleLabel": match.group("label"),
            "sampleRoot": str(sample_dir),
        }
    return {"sampleRoot": str(sample_dir)}


def build_context(sample_dir: Path) -> dict[str, Any]:
    metadata = infer_metadata(sample_dir)
    capture = load_json(sample_dir / "captures" / "capture-results.json") or {}
    live_probe = capture.get("liveProbe") or {}
    frontend = capture.get("frontend") or {}
    admin = capture.get("admin") or {}
    server = capture.get("server") or {}
    observations = [dash(item) for item in capture.get("observations") or [] if dash(item) != "--"]
    blockers = [dash(item) for item in capture.get("blockers") or [] if dash(item) != "--"]

    send_code_probe = live_probe.get("sendCode") or {}
    wechat_probe = live_probe.get("wechatLogin") or {}
    send_code_json = send_code_probe.get("json") or {}
    wechat_json = wechat_probe.get("json") or {}

    frontend_base = frontend.get("VITE_API_BASE_URL")
    backend_entry = f"{str(frontend_base).rstrip('/')}/api" if frontend_base else "--"

    phone = ((send_code_probe.get("requestBody") or {}).get("phone")) or metadata.get("probePhone")
    invite_code = ((wechat_probe.get("requestBody") or {}).get("inviteCode")) or metadata.get("probeInviteCode")

    status = "局部完成" if blockers else "可继续联调"

    confirmed = list(observations)
    if frontend.get("VITE_USE_MOCK") == "false" and frontend_base:
        confirmed.append("当前小程序运行时已显式关闭全局 mock，并指向真实后端入口。")
    if server.get("exposeWechatMiniappAppId") and server.get("exposeWechatMiniappAppSecret"):
        confirmed.append("后端源码配置已暴露微信小程序 appId/appSecret 占位符。")
    if send_code_probe:
        confirmed.append(
            f"sendCode live probe: transport={dash(send_code_probe.get('statusCode'))}, code={dash(send_code_json.get('code'))}, message={dash(send_code_json.get('message'))}"
        )
    if wechat_probe:
        confirmed.append(
            f"wechat-login live probe: transport={dash(wechat_probe.get('statusCode'))}, code={dash(wechat_json.get('code'))}, message={dash(wechat_json.get('message'))}"
        )

    seen = set()
    deduped_confirmed = []
    for item in confirmed:
        if item not in seen:
            seen.add(item)
            deduped_confirmed.append(item)

    next_actions: list[str] = []
    for blocker in blockers:
        if "VITE_ENABLE_WECHAT_AUTH" in blocker:
            next_actions.append("在目标前端运行时启用并验证 `VITE_ENABLE_WECHAT_AUTH=true`。")
        elif "appId/appSecret" in blocker:
            next_actions.append("按 `00-29` 标准流程补齐并验证远端 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`。")
        elif "VITE_API_BASE_URL" in blocker:
            next_actions.append("先修正前端 `VITE_API_BASE_URL`，再重新执行 login-auth 样本。")
        elif "Live probe requested but no probe base URL" in blocker:
            next_actions.append("为 live probe 显式传入 `-ProbeBaseUrl` 或补齐前端 `.env` 的 base URL。")
    if wechat_probe and dash(wechat_json.get("code")) != "200":
        next_actions.append("补一组真实微信老用户登录样本和一组自动注册 + inviteCode 样本。")
    if send_code_probe and dash(send_code_json.get("code")) == "200":
        next_actions.append("当前 `sendCode` 开发态直返验证码已可作为现阶段样本入口；若未来要推进正式短信能力，统一转入 `00-51 current-phase-formal-sms-capability-deferral`。")

    deduped_actions = []
    seen_actions = set()
    for item in next_actions:
        if item not in seen_actions:
            seen_actions.add(item)
            deduped_actions.append(item)

    return {
        "metadata": metadata,
        "capture": capture,
        "frontend": frontend,
        "admin": admin,
        "server": server,
        "live_probe": live_probe,
        "send_code_probe": send_code_probe,
        "send_code_json": send_code_json,
        "wechat_probe": wechat_probe,
        "wechat_json": wechat_json,
        "observations": observations,
        "blockers": blockers,
        "confirmed": deduped_confirmed,
        "next_actions": deduped_actions,
        "backend_entry": backend_entry,
        "phone": phone,
        "invite_code": invite_code,
        "status": status,
        "generated_at": capture.get("generatedAt") or metadata.get("createdAt"),
    }


def update_ledger(sample_dir: Path, context: dict[str, Any]) -> None:
    ledger_path = sample_dir / "sample-ledger.md"
    content = read_text(ledger_path)

    content = set_field(content, "Environment", dash(context["metadata"].get("environmentName")))
    content = set_field(content, "Sample Label", dash(context["metadata"].get("sampleLabel")))
    content = set_field(content, "Validate At", format_datetime(context["generated_at"]))

    content = set_field(content, "Backend Entry", context["backend_entry"])
    content = set_field(content, "WECHAT_MINIAPP_APP_ID", yes_no(context["server"].get("exposeWechatMiniappAppId")) + " (backend placeholder)")
    content = set_field(content, "WECHAT_MINIAPP_APP_SECRET", yes_no(context["server"].get("exposeWechatMiniappAppSecret")) + " (backend placeholder)")
    content = set_field(content, "Mini Program VITE_API_BASE_URL", dash(context["frontend"].get("VITE_API_BASE_URL")))
    content = set_field(content, "Mini Program VITE_USE_MOCK", dash(context["frontend"].get("VITE_USE_MOCK")))
    content = set_field(content, "Mini Program VITE_ENABLE_WECHAT_AUTH", dash(context["frontend"].get("VITE_ENABLE_WECHAT_AUTH")))
    content = set_field(content, "Admin VITE_API_BASE_URL", dash(context["admin"].get("VITE_API_BASE_URL")))

    content = set_field(content, "Phone", dash(context["phone"]))
    content = set_field(content, "InviteCode", dash(context["invite_code"]))
    content = set_field(content, "Existing User", "not verified in this sample")
    content = set_field(
        content,
        "Wechat Path",
        "live probe only; no real WeChat authorization" if context["wechat_probe"] else "not executed in this sample",
    )

    auth_capture = []
    if context["send_code_probe"]:
        auth_capture.append("captures/live-probe-sendCode.json")
    if context["wechat_probe"]:
        auth_capture.append("captures/live-probe-wechat-login.json")
    content = set_field(content, "Auth Response Capture", ", ".join(auth_capture) if auth_capture else "--")

    content = set_field(content, "Current Status", context["status"])
    content = set_list_block(content, "Confirmed", context["confirmed"])
    content = set_list_block(content, "Blockers", context["blockers"])
    content = set_list_block(content, "Next Action", context["next_actions"])

    write_text(ledger_path, content)


def generate_report(sample_dir: Path, context: dict[str, Any]) -> None:
    send_code_probe = context["send_code_probe"]
    send_code_json = context["send_code_json"]
    wechat_probe = context["wechat_probe"]
    wechat_json = context["wechat_json"]

    lines = [
        "# Login Auth Validation Report",
        "",
        f"- Generated At: {format_datetime(context['generated_at'])}",
        f"- Environment: {dash(context['metadata'].get('environmentName'))}",
        f"- Sample Label: {dash(context['metadata'].get('sampleLabel'))}",
        "",
        "## Local Runtime Scan",
        "",
        f"- Frontend baseURL: {dash(context['frontend'].get('VITE_API_BASE_URL'))}",
        f"- Frontend mock flag: {dash(context['frontend'].get('VITE_USE_MOCK'))}",
        f"- Frontend WeChat flag: {dash(context['frontend'].get('VITE_ENABLE_WECHAT_AUTH'))}",
        f"- Admin baseURL: {dash(context['admin'].get('VITE_API_BASE_URL'))}",
        f"- Backend entry: {context['backend_entry']}",
        f"- Server exposes WeChat placeholders: appId={yes_no(context['server'].get('exposeWechatMiniappAppId'))}, appSecret={yes_no(context['server'].get('exposeWechatMiniappAppSecret'))}",
        "",
        "## Live Probe",
        "",
    ]

    if send_code_probe or wechat_probe:
        lines.append(f"- Probe baseURL: {dash((context['live_probe'] or {}).get('baseUrl'))}")
        if send_code_probe:
            lines.append(
                f"- sendCode: transport={dash(send_code_probe.get('statusCode'))}, code={dash(send_code_json.get('code'))}, message={dash(send_code_json.get('message'))}"
            )
        if wechat_probe:
            lines.append(
                f"- wechat-login: transport={dash(wechat_probe.get('statusCode'))}, code={dash(wechat_json.get('code'))}, message={dash(wechat_json.get('message'))}"
            )
    else:
        lines.append("- [ ] Live probe not executed")

    lines.extend(["", "## Confirmed", ""])
    if context["confirmed"]:
        lines.extend([f"- [x] {item}" for item in context["confirmed"]])
    else:
        lines.append("- [ ] No confirmed fact extracted")

    lines.extend(["", "## Blockers", ""])
    if context["blockers"]:
        lines.extend([f"- [ ] {item}" for item in context["blockers"]])
    else:
        lines.append("- [x] No blocker detected from current scan")

    lines.extend(["", "## Next Actions", ""])
    if context["next_actions"]:
        lines.extend([f"- [ ] {item}" for item in context["next_actions"]])
    else:
        lines.append("- [x] No follow-up action extracted")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- captures/capture-results.json",
            "- captures/live-probe-sendCode.json (if live probe enabled)",
            "- captures/live-probe-wechat-login.json (if live probe enabled)",
            "- runtime-summary.md",
            "- sample-ledger.md",
            "- validation-report.md",
        ]
    )

    write_text(sample_dir / "validation-report.md", "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill login-auth sample ledger and report from capture results.")
    parser.add_argument("--sample-dir", required=True)
    args = parser.parse_args()

    sample_dir = Path(args.sample_dir).resolve()
    context = build_context(sample_dir)
    update_ledger(sample_dir, context)
    generate_report(sample_dir, context)
    print(f"login-auth artifacts synced: {sample_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

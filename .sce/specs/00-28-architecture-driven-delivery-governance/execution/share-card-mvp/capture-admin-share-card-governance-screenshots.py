import json
import os
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urljoin

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


REMOTE_BASE = "http://101.43.57.62"
REMOTE_API = f"{REMOTE_BASE}/api"
ADMIN_ACCOUNT = "admin"
ADMIN_PASSWORD_ENV = "KAIPAI_ADMIN_SMOKE_PASSWORD"
LOCAL_PROXY_PORT = 8013
LOCAL_APP_PORT = 5178
SCRIPT_DIR = Path(__file__).resolve().parent
ADMIN_WORKDIR = SCRIPT_DIR.parents[4] / "kaipai-admin"


class ReverseProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    timeout = 30

    def _forward(self) -> None:
        body = None
        content_length = int(self.headers.get("Content-Length") or 0)
        if content_length:
            body = self.rfile.read(content_length)

        target_url = urljoin(REMOTE_BASE, self.path)
        headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() not in {"host", "content-length", "connection"}
        }
        response = requests.request(
            self.command,
            target_url,
            headers=headers,
            data=body,
            allow_redirects=False,
            timeout=30,
        )

        self.send_response(response.status_code)
        for key, value in response.headers.items():
            if key.lower() in {"content-encoding", "transfer-encoding", "connection", "content-length"}:
                continue
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(response.content)))
        self.end_headers()
        try:
            self.wfile.write(response.content)
        except (BrokenPipeError, ConnectionAbortedError):
            return

    def do_GET(self) -> None:
        self._forward()

    def do_POST(self) -> None:
        self._forward()

    def do_PUT(self) -> None:
        self._forward()

    def do_DELETE(self) -> None:
        self._forward()

    def do_OPTIONS(self) -> None:
        self._forward()

    def log_message(self, format: str, *args) -> None:
        return


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0


def wait_http_ready(url: str, timeout: int = 90) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                return
        except Exception as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"http not ready: {url} ({last_error})")


def resolve_local_app_port() -> int:
    if not port_open("127.0.0.1", LOCAL_APP_PORT):
        return LOCAL_APP_PORT
    for port in range(LOCAL_APP_PORT + 1, LOCAL_APP_PORT + 20):
        if not port_open("127.0.0.1", port):
            return port
    raise RuntimeError("no free local admin port found in capture range")


def resolve_local_proxy_port() -> int:
    if not port_open("127.0.0.1", LOCAL_PROXY_PORT):
        return LOCAL_PROXY_PORT
    for port in range(LOCAL_PROXY_PORT + 1, LOCAL_PROXY_PORT + 20):
        if not port_open("127.0.0.1", port):
            return port
    raise RuntimeError("no free local proxy port found in capture range")


def start_proxy(proxy_port: int) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", proxy_port), ReverseProxyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def login_admin() -> dict:
    admin_password = os.environ.get(ADMIN_PASSWORD_ENV)
    if not admin_password:
        raise RuntimeError(f"{ADMIN_PASSWORD_ENV} is required for admin login smoke")
    response = requests.post(
        f"{REMOTE_API}/admin/auth/login",
        json={"account": ADMIN_ACCOUNT, "password": admin_password},
        timeout=30,
    )
    payload = response.json()
    if response.status_code != 200 or payload.get("code") != 200:
        raise RuntimeError(f"admin login failed: HTTP {response.status_code} / code {payload.get('code')}")
    return payload["data"]


def wait_for_text(driver: webdriver.Edge, text: str, timeout: int = 20) -> None:
    WebDriverWait(driver, timeout).until(lambda current: text in current.page_source)


def wait_for_idle(driver: webdriver.Edge, timeout: int = 20) -> None:
    def loading_finished(current: webdriver.Edge) -> bool:
        visible_count = current.execute_script(
            """
            return Array.from(document.querySelectorAll('.el-loading-mask')).filter((item) => {
              const style = window.getComputedStyle(item)
              return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'
            }).length
            """
        )
        return visible_count == 0

    WebDriverWait(driver, timeout).until(loading_finished)


def set_input_value(driver: webdriver.Edge, placeholder: str, value: str, timeout: int = 20) -> None:
    input_el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"input[placeholder='{placeholder}']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_el)
    input_el.click()
    input_el.send_keys(Keys.CONTROL, "a")
    input_el.send_keys(Keys.DELETE)
    if value:
        input_el.send_keys(value)


def click_button(driver: webdriver.Edge, text: str, timeout: int = 20) -> None:
    button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, f"(//button[.//span[contains(normalize-space(.), '{text}')]])[1]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    driver.execute_script("arguments[0].click();", button)


def wait_for_table_rows(driver: webdriver.Edge, timeout: int = 20) -> None:
    WebDriverWait(driver, timeout).until(
        lambda current: len(current.find_elements(By.CSS_SELECTOR, ".el-table__body-wrapper tbody tr")) > 0
    )


def fetch_api_payload(path: str, token: str, params: dict, method: str = "GET", json_body: dict | None = None) -> dict:
    response = requests.request(
        method,
        f"{REMOTE_API}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        json=json_body,
        timeout=30,
    )
    payload = response.json()
    return {
        "method": method,
        "httpStatus": response.status_code,
        "url": response.url,
        "params": params,
        "body": json_body or {},
        "responseJson": payload,
    }


def fetch_api_response_json(
    path: str,
    token: str,
    params: dict | None = None,
    method: str = "GET",
    json_body: dict | None = None,
) -> dict:
    response = requests.request(
        method,
        f"{REMOTE_API}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        json=json_body,
        timeout=30,
    )
    payload = response.json()
    if response.status_code != 200 or payload.get("code") != 200:
        raise RuntimeError(
            f"failed to fetch mock payload for {path}: HTTP {response.status_code} / code {payload.get('code')}"
        )
    return payload


def build_content_api_mocks(token: str, request_id: str, share_card_id: str, viewer_user_id: str, owner_user_id: str) -> dict[str, dict]:
    list_payload = fetch_api_response_json(
        "/admin/content/contact-requests",
        token,
        {"pageNo": 1, "pageSize": 20, "shareCardId": share_card_id},
    )
    detail_payload = fetch_api_response_json(f"/admin/content/contact-requests/{request_id}", token)
    share_cards_payload = fetch_api_response_json(
        "/admin/content/share-cards",
        token,
        {"pageNo": 1, "pageSize": 20, "shareCardId": share_card_id},
    )
    share_card_detail_payload = fetch_api_response_json(f"/admin/content/share-cards/{share_card_id}", token)
    legacy_summary_payload = fetch_api_response_json("/admin/content/share-cards/legacy-summary", token)
    repair_legacy_payload = fetch_api_response_json(
        "/admin/content/share-cards/repair-legacy",
        token,
        method="POST",
    )
    strategy_payload = fetch_api_response_json("/admin/content/default-general-card/strategy", token)
    user_state_payload = fetch_api_response_json(f"/admin/content/default-general-card/users/{owner_user_id}", token)

    return {
        "/api/admin/content/contact-requests": list_payload,
        f"/api/admin/content/contact-requests/{request_id}": detail_payload,
        "/api/admin/content/share-cards": share_cards_payload,
        f"/api/admin/content/share-cards/{share_card_id}": share_card_detail_payload,
        "/api/admin/content/share-cards/legacy-summary": legacy_summary_payload,
        "/api/admin/content/share-cards/repair-legacy": repair_legacy_payload,
        "/api/admin/content/default-general-card/strategy": strategy_payload,
        f"/api/admin/content/default-general-card/users/{owner_user_id}": user_state_payload,
    }


def install_content_api_mock(driver: webdriver.Edge, mock_routes: dict[str, dict]) -> None:
    script = f"""
      (() => {{
        const mockRoutes = {json.dumps(mock_routes, ensure_ascii=False)};
        const OriginalXHR = window.XMLHttpRequest;

        function resolveMock(url) {{
          const plainUrl = String(url || '');
          const normalized = plainUrl.startsWith('http')
            ? new URL(plainUrl, window.location.origin).pathname
            : plainUrl.split('?')[0];

          for (const [key, payload] of Object.entries(mockRoutes)) {{
            if (normalized === key) {{
              return payload;
            }}
          }}
          return null;
        }}

        function MockedXHR() {{
          const xhr = new OriginalXHR();
          const open = xhr.open;
          const send = xhr.send;
          let requestUrl = '';

          xhr.open = function(method, url, async, user, password) {{
            requestUrl = String(url || '');
            return open.call(this, method, url, async, user, password);
          }};

          xhr.send = function(body) {{
            const mockPayload = resolveMock(requestUrl);
            if (!mockPayload) {{
              return send.call(this, body);
            }}

            const responseText = JSON.stringify(mockPayload);
            Object.defineProperty(this, 'readyState', {{ configurable: true, value: 4 }});
            Object.defineProperty(this, 'status', {{ configurable: true, value: 200 }});
            Object.defineProperty(this, 'responseURL', {{ configurable: true, value: requestUrl }});
            Object.defineProperty(this, 'responseText', {{ configurable: true, value: responseText }});
            Object.defineProperty(this, 'response', {{ configurable: true, value: responseText }});

            setTimeout(() => {{
              if (typeof this.onreadystatechange === 'function') this.onreadystatechange();
              this.dispatchEvent(new Event('readystatechange'));
              if (typeof this.onload === 'function') this.onload();
              this.dispatchEvent(new Event('load'));
              if (typeof this.onloadend === 'function') this.onloadend();
              this.dispatchEvent(new Event('loadend'));
            }}, 0);
          }};

          return xhr;
        }}

        window.XMLHttpRequest = MockedXHR;
      }})();
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})


def collect_snapshot(driver: webdriver.Edge) -> dict:
    return driver.execute_script(
        """
        return {
          location: window.location.href,
          title: document.title,
          tableRows: Array.from(document.querySelectorAll('.el-table__body-wrapper tbody tr')).slice(0, 8).map((row) =>
            Array.from(row.querySelectorAll('td .cell')).map((cell) => cell.innerText.trim()).filter(Boolean)
          ),
          drawerTitles: Array.from(document.querySelectorAll('.el-drawer__title')).map((item) => item.innerText.trim()).filter(Boolean),
          detailBlocks: Array.from(document.querySelectorAll('.detail-block')).map((block) => ({
            label: block.querySelector('span') ? block.querySelector('span').innerText.trim() : '',
            value: block.querySelector('strong') ? block.querySelector('strong').innerText.trim() : '',
          })),
          alerts: Array.from(document.querySelectorAll('.el-alert__title')).map((item) => item.innerText.trim()).filter(Boolean),
          chips: Array.from(document.querySelectorAll('.chip')).map((item) => item.innerText.trim()).filter(Boolean),
        }
        """
    )


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def capture_contact_requests(driver: webdriver.Edge, sample_root: Path, token: str, request_id: str, share_card_id: str, viewer_user_id: str, local_app_port: int) -> dict:
    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    route = "/content/contact-requests"
    driver.get(f"http://127.0.0.1:{local_app_port}{route}")
    wait_for_text(driver, "联系方式申请记录")
    wait_for_idle(driver)

    set_input_value(driver, "申请单号", request_id)
    set_input_value(driver, "分享卡 ID", share_card_id)
    set_input_value(driver, "查看人 ID", viewer_user_id)
    click_button(driver, "查询")
    wait_for_idle(driver)
    wait_for_table_rows(driver)
    time.sleep(1)

    list_screenshot_path = screenshots_root / "admin-share-card-contact-requests.png"
    driver.save_screenshot(str(list_screenshot_path))
    list_snapshot = collect_snapshot(driver)

    click_button(driver, "查看详情")
    wait_for_text(driver, "联系方式申请详情")
    wait_for_idle(driver)
    time.sleep(1)

    detail_screenshot_path = screenshots_root / "admin-share-card-contact-requests-detail.png"
    driver.save_screenshot(str(detail_screenshot_path))
    detail_snapshot = collect_snapshot(driver)

    page_data = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "name": "admin-share-card-contact-requests",
        "route": route,
        "filters": {
            "pageNo": 1,
            "pageSize": 20,
            "requestId": request_id,
            "shareCardId": share_card_id,
            "viewerUserId": viewer_user_id,
        },
        "apiData": {
            "list": fetch_api_payload(
                "/admin/content/contact-requests",
                token,
                {"pageNo": 1, "pageSize": 20, "requestId": request_id, "shareCardId": share_card_id, "viewerUserId": viewer_user_id},
            ),
            "detail": fetch_api_payload(f"/admin/content/contact-requests/{request_id}", token, {}),
        },
        "listSnapshot": list_snapshot,
        "detailSnapshot": detail_snapshot,
    }
    page_data_path = captures_root / "page-data-admin-share-card-contact-requests.json"
    write_json(page_data_path, page_data)

    return {
        "name": "admin-share-card-contact-requests",
        "route": route,
        "listScreenshotPath": str(list_screenshot_path),
        "detailScreenshotPath": str(detail_screenshot_path),
        "pageDataPath": str(page_data_path),
        "rowCount": len(list_snapshot.get("tableRows") or []),
    }


def capture_default_general_card(driver: webdriver.Edge, sample_root: Path, token: str, owner_user_id: str, local_app_port: int) -> dict:
    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    route = "/content/default-general-card"
    driver.get(f"http://127.0.0.1:{local_app_port}{route}")
    wait_for_text(driver, "策略摘要")
    wait_for_idle(driver)

    set_input_value(driver, "请输入用户 ID", owner_user_id)
    click_button(driver, "检查用户")
    wait_for_idle(driver)
    wait_for_text(driver, owner_user_id)
    time.sleep(1)

    screenshot_path = screenshots_root / "admin-share-card-default-general-card.png"
    driver.save_screenshot(str(screenshot_path))
    snapshot = collect_snapshot(driver)

    page_data = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "name": "admin-share-card-default-general-card",
        "route": route,
        "filters": {
            "userId": owner_user_id,
        },
        "apiData": {
            "strategy": fetch_api_payload("/admin/content/default-general-card/strategy", token, {}),
            "userState": fetch_api_payload(f"/admin/content/default-general-card/users/{owner_user_id}", token, {}),
        },
        "snapshot": snapshot,
    }
    page_data_path = captures_root / "page-data-admin-share-card-default-general-card.json"
    write_json(page_data_path, page_data)

    return {
        "name": "admin-share-card-default-general-card",
        "route": route,
        "screenshotPath": str(screenshot_path),
        "pageDataPath": str(page_data_path),
    }


def capture_share_cards(driver: webdriver.Edge, sample_root: Path, token: str, share_card_id: str, owner_user_id: str, local_app_port: int) -> dict:
    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    route = "/content/share-cards"
    driver.get(f"http://127.0.0.1:{local_app_port}{route}")
    wait_for_text(driver, "分享卡实例治理")
    wait_for_idle(driver)

    click_button(driver, "执行 legacy 修复")
    WebDriverWait(driver, 20).until(
        lambda current: current.execute_script(
            "return Boolean(document.querySelector('.legacy-alert .el-alert__title'))"
        )
    )
    wait_for_idle(driver)
    time.sleep(1)

    repair_screenshot_path = screenshots_root / "admin-share-card-share-cards-repair-legacy.png"
    driver.save_screenshot(str(repair_screenshot_path))
    repair_snapshot = collect_snapshot(driver)

    set_input_value(driver, "分享卡 ID", share_card_id)
    set_input_value(driver, "持卡人 ID", owner_user_id)
    click_button(driver, "查询")
    wait_for_idle(driver)
    wait_for_table_rows(driver)
    time.sleep(1)

    list_screenshot_path = screenshots_root / "admin-share-card-share-cards.png"
    driver.save_screenshot(str(list_screenshot_path))
    list_snapshot = collect_snapshot(driver)

    click_button(driver, "查看详情")
    wait_for_text(driver, "分享卡治理详情")
    wait_for_idle(driver)
    time.sleep(1)

    detail_screenshot_path = screenshots_root / "admin-share-card-share-cards-detail.png"
    driver.save_screenshot(str(detail_screenshot_path))
    detail_snapshot = collect_snapshot(driver)

    page_data = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "name": "admin-share-card-share-cards",
        "route": route,
        "filters": {
            "pageNo": 1,
            "pageSize": 20,
            "shareCardId": share_card_id,
            "ownerUserId": owner_user_id,
        },
        "apiData": {
            "repairAction": fetch_api_payload(
                "/admin/content/share-cards/repair-legacy",
                token,
                {},
                method="POST",
            ),
            "postRepairLegacySummary": fetch_api_payload("/admin/content/share-cards/legacy-summary", token, {}),
            "list": fetch_api_payload(
                "/admin/content/share-cards",
                token,
                {"pageNo": 1, "pageSize": 20, "shareCardId": share_card_id, "ownerUserId": owner_user_id},
            ),
            "detail": fetch_api_payload(f"/admin/content/share-cards/{share_card_id}", token, {}),
            "legacySummary": fetch_api_payload("/admin/content/share-cards/legacy-summary", token, {}),
        },
        "repairSnapshot": repair_snapshot,
        "listSnapshot": list_snapshot,
        "detailSnapshot": detail_snapshot,
    }
    page_data_path = captures_root / "page-data-admin-share-card-share-cards.json"
    write_json(page_data_path, page_data)

    return {
        "name": "admin-share-card-share-cards",
        "route": route,
        "actionScreenshotPath": str(repair_screenshot_path),
        "listScreenshotPath": str(list_screenshot_path),
        "detailScreenshotPath": str(detail_screenshot_path),
        "pageDataPath": str(page_data_path),
        "rowCount": len(list_snapshot.get("tableRows") or []),
    }


def start_vite(capture_root: Path, local_app_port: int, proxy_port: int) -> tuple[subprocess.Popen, object]:
    vite_log_path = capture_root / "admin-local-vite.log"
    vite_log_handle = open(vite_log_path, "w", encoding="utf-8", newline="\n")
    env = os.environ.copy()
    env.pop("VITE_API_BASE_URL", None)
    env["VITE_API_PROXY_TARGET"] = f"http://127.0.0.1:{proxy_port}"
    vite_process = subprocess.Popen(
        ["npm.cmd", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(local_app_port), "--strictPort"],
        cwd=ADMIN_WORKDIR,
        stdout=vite_log_handle,
        stderr=subprocess.STDOUT,
        shell=False,
        env=env,
    )
    return vite_process, vite_log_handle


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "usage: capture-admin-share-card-governance-screenshots.py "
            "<sample-root> <request-id> <share-card-id> <viewer-user-id> <owner-user-id>"
        )
        return 1

    sample_root = Path(sys.argv[1]).resolve()
    request_id = sys.argv[2].strip()
    share_card_id = sys.argv[3].strip()
    viewer_user_id = sys.argv[4].strip()
    owner_user_id = sys.argv[5].strip()

    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    screenshots_root.mkdir(parents=True, exist_ok=True)
    captures_root.mkdir(parents=True, exist_ok=True)

    local_app_port = resolve_local_app_port()
    proxy_port = resolve_local_proxy_port()
    proxy_server, proxy_thread = start_proxy(proxy_port)
    wait_http_ready(f"http://127.0.0.1:{proxy_port}/api/v3/api-docs", timeout=20)
    vite_process, vite_log_handle = start_vite(captures_root, local_app_port, proxy_port)

    driver = None
    try:
        wait_http_ready(f"http://127.0.0.1:{local_app_port}/login", timeout=90)
        login_data = login_admin()

        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1680,2200")
        driver = webdriver.Edge(options=options)
        driver.set_page_load_timeout(45)
        install_content_api_mock(
            driver,
            build_content_api_mocks(login_data["accessToken"], request_id, share_card_id, viewer_user_id, owner_user_id),
        )

        driver.get(f"http://127.0.0.1:{local_app_port}/login")
        driver.execute_script(
            """
            localStorage.setItem('kaipai-admin-token', arguments[0]);
            localStorage.setItem('kaipai-admin-session', JSON.stringify(arguments[1]));
            """,
            login_data["accessToken"],
            login_data["adminUserInfo"],
        )

        captures = [
            capture_contact_requests(driver, sample_root, login_data["accessToken"], request_id, share_card_id, viewer_user_id, local_app_port),
            capture_share_cards(driver, sample_root, login_data["accessToken"], share_card_id, owner_user_id, local_app_port),
            capture_default_general_card(driver, sample_root, login_data["accessToken"], owner_user_id, local_app_port),
        ]

        manifest = {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "baseUrl": REMOTE_API,
            "proxyUrl": f"http://127.0.0.1:{proxy_port}",
            "localAdminUrl": f"http://127.0.0.1:{local_app_port}",
            "requestId": request_id,
            "shareCardId": share_card_id,
            "viewerUserId": viewer_user_id,
            "ownerUserId": owner_user_id,
            "captures": captures,
        }
        write_json(captures_root / "admin-share-card-screenshot-capture.json", manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    finally:
        if driver is not None:
            driver.quit()
        if vite_process is not None and vite_process.poll() is None:
            vite_process.terminate()
            try:
                vite_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                vite_process.kill()
                vite_process.wait(timeout=10)
        if vite_log_handle is not None:
            vite_log_handle.close()
        if proxy_server is not None:
            proxy_server.shutdown()
            proxy_server.server_close()
        if proxy_thread is not None:
            proxy_thread.join(timeout=2)


if __name__ == "__main__":
    raise SystemExit(main())

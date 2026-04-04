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
ADMIN_PASSWORD = "admin123"
LOCAL_PROXY_PORT = 8012
LOCAL_APP_PORT = 5177
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


def start_proxy_if_needed() -> tuple[ThreadingHTTPServer | None, threading.Thread | None]:
    if port_open("127.0.0.1", LOCAL_PROXY_PORT):
        return None, None
    server = ThreadingHTTPServer(("127.0.0.1", LOCAL_PROXY_PORT), ReverseProxyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def login_admin() -> dict:
    response = requests.post(
        f"{REMOTE_API}/admin/auth/login",
        json={"account": ADMIN_ACCOUNT, "password": ADMIN_PASSWORD},
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
        masks = current.find_elements(By.CSS_SELECTOR, ".el-loading-mask")
        return all(not mask.is_displayed() for mask in masks)

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


def wait_for_table_text(driver: webdriver.Edge, text: str, timeout: int = 20) -> None:
    WebDriverWait(driver, timeout).until(
        lambda current: text in current.page_source
        and len(current.find_elements(By.CSS_SELECTOR, ".el-table__body-wrapper tbody tr")) > 0
    )


def wait_for_empty_text(driver: webdriver.Edge, text: str, timeout: int = 20) -> None:
    WebDriverWait(driver, timeout).until(lambda current: text in current.page_source)


def fetch_api_payload(path: str, token: str, params: dict | None = None) -> dict:
    response = requests.get(
        f"{REMOTE_API}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=30,
    )
    payload = response.json()
    return {
        "httpStatus": response.status_code,
        "url": response.url,
        "params": params,
        "responseJson": payload,
    }


def collect_table_snapshot(driver: webdriver.Edge) -> dict:
    return driver.execute_script(
        """
        const rows = Array.from(document.querySelectorAll('.el-table__body-wrapper tbody tr')).map((row) =>
          Array.from(row.querySelectorAll('td .cell')).map((cell) => cell.innerText.trim()).filter(Boolean)
        );
        return {
          location: window.location.href,
          title: document.title,
          tableRows: rows,
          emptyTexts: Array.from(document.querySelectorAll('.verify-empty')).map((item) => item.innerText.trim()).filter(Boolean),
          drawerTitles: Array.from(document.querySelectorAll('.el-drawer__title')).map((item) => item.innerText.trim()).filter(Boolean),
          detailBlocks: Array.from(document.querySelectorAll('.detail-block')).map((block) => ({
            label: block.querySelector('span') ? block.querySelector('span').innerText.trim() : '',
            value: block.querySelector('strong') ? block.querySelector('strong').innerText.trim() : '',
          })),
        };
        """
    )


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def capture_pending_empty_page(driver: webdriver.Edge, sample_root: Path, token: str, user_id: str) -> dict:
    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    route = "/verify/pending"
    driver.get(f"http://127.0.0.1:{LOCAL_APP_PORT}{route}")
    wait_for_text(driver, "待审核申请清单")
    wait_for_idle(driver)

    set_input_value(driver, "用户 ID", user_id)
    click_button(driver, "查询")
    wait_for_idle(driver)
    wait_for_empty_text(driver, "当前没有待审核申请")
    time.sleep(1)

    screenshot_path = screenshots_root / "admin-verify-pending-empty.png"
    driver.save_screenshot(str(screenshot_path))
    snapshot = collect_table_snapshot(driver)

    page_data = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "name": "admin-verify-pending-empty",
        "route": route,
        "filters": {
            "pageNo": 1,
            "pageSize": 20,
            "userId": int(user_id),
            "status": 1,
        },
        "apiData": fetch_api_payload(
            "/admin/verify/list",
            token,
            {
                "pageNo": 1,
                "pageSize": 20,
                "userId": int(user_id),
                "status": 1,
            },
        ),
        "listSnapshot": snapshot,
    }
    page_data_path = captures_root / "page-data-admin-verify-pending-empty.json"
    write_json(page_data_path, page_data)

    return {
        "name": "admin-verify-pending-empty",
        "route": route,
        "listScreenshotPath": str(screenshot_path),
        "detailScreenshotPath": None,
        "pageDataPath": str(page_data_path),
        "rowCount": len(snapshot.get("tableRows") or []),
    }


def capture_history_page(
    driver: webdriver.Edge,
    sample_root: Path,
    token: str,
    user_id: str,
    real_name: str,
    detail_id: str,
) -> dict:
    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    route = "/verify/history"
    driver.get(f"http://127.0.0.1:{LOCAL_APP_PORT}{route}")
    wait_for_text(driver, "历史审核记录")
    wait_for_idle(driver)

    set_input_value(driver, "用户 ID", user_id)
    click_button(driver, "查询")
    wait_for_idle(driver)
    wait_for_table_text(driver, real_name)
    time.sleep(1)

    list_screenshot_path = screenshots_root / "admin-verify-history.png"
    driver.save_screenshot(str(list_screenshot_path))
    list_snapshot = collect_table_snapshot(driver)

    click_button(driver, "查看详情")
    wait_for_text(driver, "认证申请详情")
    wait_for_idle(driver)
    time.sleep(1)

    detail_screenshot_path = screenshots_root / "admin-verify-history-detail.png"
    driver.save_screenshot(str(detail_screenshot_path))
    detail_snapshot = collect_table_snapshot(driver)

    page_data = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "name": "admin-verify-history",
        "route": route,
        "filters": {
            "pageNo": 1,
            "pageSize": 20,
            "userId": int(user_id),
        },
        "listApiData": fetch_api_payload(
            "/admin/verify/list",
            token,
            {
                "pageNo": 1,
                "pageSize": 20,
                "userId": int(user_id),
            },
        ),
        "detailApiData": fetch_api_payload(f"/admin/verify/{detail_id}", token),
        "listSnapshot": list_snapshot,
        "detailSnapshot": detail_snapshot,
    }
    page_data_path = captures_root / "page-data-admin-verify-history.json"
    write_json(page_data_path, page_data)

    return {
        "name": "admin-verify-history",
        "route": route,
        "listScreenshotPath": str(list_screenshot_path),
        "detailScreenshotPath": str(detail_screenshot_path),
        "pageDataPath": str(page_data_path),
        "rowCount": len(list_snapshot.get("tableRows") or []),
    }


def start_vite(capture_root: Path) -> tuple[subprocess.Popen, object]:
    vite_log_path = capture_root / "admin-local-vite.log"
    vite_log_handle = open(vite_log_path, "w", encoding="utf-8", newline="\n")
    env = os.environ.copy()
    env["VITE_API_PROXY_TARGET"] = f"http://127.0.0.1:{LOCAL_PROXY_PORT}"
    vite_process = subprocess.Popen(
        ["npm.cmd", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(LOCAL_APP_PORT), "--strictPort"],
        cwd=ADMIN_WORKDIR,
        stdout=vite_log_handle,
        stderr=subprocess.STDOUT,
        shell=False,
        env=env,
    )
    return vite_process, vite_log_handle


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: capture-admin-verify-screenshots.py "
            "<sample-root> <user-id> <real-name> <detail-verification-id>"
        )
        return 1

    sample_root = Path(sys.argv[1]).resolve()
    user_id = sys.argv[2].strip()
    real_name = sys.argv[3].strip()
    detail_verification_id = sys.argv[4].strip()

    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    screenshots_root.mkdir(parents=True, exist_ok=True)
    captures_root.mkdir(parents=True, exist_ok=True)

    proxy_server, proxy_thread = start_proxy_if_needed()
    wait_http_ready(f"http://127.0.0.1:{LOCAL_PROXY_PORT}/api/v3/api-docs", timeout=20)
    vite_process, vite_log_handle = start_vite(captures_root)

    driver = None
    try:
        wait_http_ready(f"http://127.0.0.1:{LOCAL_APP_PORT}/login", timeout=90)
        login_data = login_admin()

        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1680,1800")
        driver = webdriver.Edge(options=options)
        driver.set_page_load_timeout(45)

        driver.get(f"http://127.0.0.1:{LOCAL_APP_PORT}/login")
        driver.execute_script(
            """
            localStorage.setItem('kaipai-admin-token', arguments[0]);
            localStorage.setItem('kaipai-admin-session', JSON.stringify(arguments[1]));
            """,
            login_data["accessToken"],
            login_data["adminUserInfo"],
        )

        captures = [
            capture_pending_empty_page(driver, sample_root, login_data["accessToken"], user_id),
            capture_history_page(driver, sample_root, login_data["accessToken"], user_id, real_name, detail_verification_id),
        ]

        manifest = {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "baseUrl": REMOTE_API,
            "proxyUrl": f"http://127.0.0.1:{LOCAL_PROXY_PORT}",
            "localAdminUrl": f"http://127.0.0.1:{LOCAL_APP_PORT}",
            "captures": captures,
        }
        manifest_path = captures_root / "admin-verify-screenshot-capture.json"
        write_json(manifest_path, manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    finally:
        if driver is not None:
            driver.quit()
        if vite_process.poll() is None:
            vite_process.terminate()
            try:
                vite_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                vite_process.kill()
                vite_process.wait(timeout=10)
        vite_log_handle.close()
        if proxy_server is not None:
            proxy_server.shutdown()
            proxy_server.server_close()
        if proxy_thread is not None:
            proxy_thread.join(timeout=2)


if __name__ == "__main__":
    raise SystemExit(main())

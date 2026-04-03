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


def click_xpath(driver: webdriver.Edge, xpath: str, timeout: int = 20) -> None:
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    driver.execute_script("arguments[0].click();", element)


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


def wait_for_page(driver: webdriver.Edge) -> None:
    wait_for_text(driver, "AI 简历治理", timeout=30)
    wait_for_idle(driver, timeout=30)


def wait_for_table_text(driver: webdriver.Edge, text: str, timeout: int = 20) -> None:
    WebDriverWait(driver, timeout).until(lambda current: text in current.page_source)


def wait_for_xpath(driver: webdriver.Edge, xpath: str, timeout: int = 20) -> None:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def fetch_api_payload(path: str, token: str, params: dict) -> dict:
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


def collect_snapshot(driver: webdriver.Edge) -> dict:
    return driver.execute_script(
        """
        return {
          location: window.location.href,
          title: document.title,
          drawers: Array.from(document.querySelectorAll('.el-drawer__title')).map((item) => item.innerText.trim()).filter(Boolean),
          tableRows: Array.from(document.querySelectorAll('.el-table__body-wrapper tbody tr')).slice(0, 8).map((row) =>
            Array.from(row.querySelectorAll('td .cell')).map((cell) => cell.innerText.trim()).filter(Boolean)
          ),
          overviewCards: Array.from(document.querySelectorAll('.overview-card')).map((card) => ({
            label: card.querySelector('span') ? card.querySelector('span').innerText.trim() : '',
            value: card.querySelector('strong') ? card.querySelector('strong').innerText.trim() : '',
            description: card.querySelector('p') ? card.querySelector('p').innerText.trim() : '',
          })),
          recentItems: Array.from(document.querySelectorAll('.recent-item')).slice(0, 5).map((item) => item.innerText.trim()),
        }
        """
    )


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def start_vite(capture_root: Path) -> tuple[subprocess.Popen, object]:
    if port_open("127.0.0.1", LOCAL_APP_PORT):
        return None, None
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


def capture_overview(driver: webdriver.Edge, sample_root: Path, token: str) -> dict:
    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    driver.get(f"http://127.0.0.1:{LOCAL_APP_PORT}/system/ai-resume-governance")
    wait_for_page(driver)
    time.sleep(1)

    screenshot_path = screenshots_root / "admin-ai-governance-overview.png"
    driver.save_screenshot(str(screenshot_path))
    page_data = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "name": "admin-ai-governance-overview",
        "route": "/system/ai-resume-governance",
        "apiData": fetch_api_payload("/admin/ai/resume/overview", token, {}),
        "snapshot": collect_snapshot(driver),
    }
    page_data_path = captures_root / "page-data-admin-ai-governance-overview.json"
    write_json(page_data_path, page_data)
    return {
        "name": "admin-ai-governance-overview",
        "route": "/system/ai-resume-governance",
        "screenshotPath": str(screenshot_path),
        "pageDataPath": str(page_data_path),
    }


def capture_history_detail(driver: webdriver.Edge, sample_root: Path, token: str, history_id: str) -> dict:
    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    driver.get(f"http://127.0.0.1:{LOCAL_APP_PORT}/system/ai-resume-governance")
    wait_for_page(driver)

    set_input_value(driver, "historyId / draftId / 指令 / 回复", history_id)
    click_xpath(
        driver,
        "//div[contains(@class,'filter-panel') and .//input[@placeholder='historyId / draftId / 指令 / 回复']]//button[.//span[normalize-space(.)='查询']]",
    )
    wait_for_idle(driver)
    wait_for_table_text(driver, history_id)
    time.sleep(1)

    list_screenshot_path = screenshots_root / "admin-ai-governance-history-list.png"
    driver.save_screenshot(str(list_screenshot_path))

    click_xpath(driver, "(//button[.//span[normalize-space(.)='查看详情']])[1]")
    wait_for_text(driver, "AI 简历历史详情")
    wait_for_idle(driver)
    time.sleep(1)

    detail_screenshot_path = screenshots_root / "admin-ai-governance-history-detail.png"
    driver.save_screenshot(str(detail_screenshot_path))
    page_data = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "name": "admin-ai-governance-history-detail",
        "route": "/system/ai-resume-governance",
        "historyId": history_id,
        "apiData": {
            "histories": fetch_api_payload("/admin/ai/resume/histories", token, {"pageNo": 1, "pageSize": 20, "keyword": history_id}),
            "detail": fetch_api_payload(f"/admin/ai/resume/histories/{history_id}", token, {}),
        },
        "snapshot": collect_snapshot(driver),
    }
    page_data_path = captures_root / "page-data-admin-ai-governance-history-detail.json"
    write_json(page_data_path, page_data)
    return {
        "name": "admin-ai-governance-history-detail",
        "route": "/system/ai-resume-governance",
        "historyId": history_id,
        "listScreenshotPath": str(list_screenshot_path),
        "detailScreenshotPath": str(detail_screenshot_path),
        "pageDataPath": str(page_data_path),
    }


def capture_failure_detail(driver: webdriver.Edge, sample_root: Path, token: str, failure_id: str, failure_request_id: str) -> dict:
    screenshots_root = sample_root / "screenshots"
    captures_root = sample_root / "captures"
    driver.get(f"http://127.0.0.1:{LOCAL_APP_PORT}/system/ai-resume-governance")
    wait_for_page(driver)

    set_input_value(driver, "failureId / 指令 / 错误 / 命中词", failure_id)
    click_xpath(
        driver,
        "//div[contains(@class,'filter-panel') and .//input[@placeholder='failureId / 指令 / 错误 / 命中词']]//button[.//span[normalize-space(.)='查询']]",
    )
    wait_for_idle(driver)
    wait_for_xpath(
        driver,
        "(//section[contains(@class,'notice-grid')]//div[contains(@class,'el-table__body-wrapper')]//tbody/tr)[1]",
    )
    time.sleep(1)

    list_screenshot_path = screenshots_root / "admin-ai-governance-failure-list.png"
    driver.save_screenshot(str(list_screenshot_path))

    click_xpath(driver, "(//button[normalize-space(.)='处置记录'])[1]")
    wait_for_text(driver, "AI 失败样本处置记录")
    wait_for_idle(driver)
    time.sleep(1)

    detail_screenshot_path = screenshots_root / "admin-ai-governance-failure-detail.png"
    driver.save_screenshot(str(detail_screenshot_path))
    page_data = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "name": "admin-ai-governance-failure-detail",
        "route": "/system/ai-resume-governance",
        "failureId": failure_id,
        "failureRequestId": failure_request_id,
        "apiData": {
            "failures": fetch_api_payload("/admin/ai/resume/failures", token, {"keyword": failure_id, "limit": 20}),
            "sensitiveHits": fetch_api_payload("/admin/ai/resume/sensitive-hits", token, {"keyword": failure_id, "limit": 20}),
            "auditLogs": fetch_api_payload(
                "/admin/system/operation-logs",
                token,
                {
                    "pageNo": 1,
                    "pageSize": 10,
                    "targetType": "ai_resume_failure",
                    "requestId": failure_request_id,
                },
            ),
        },
        "snapshot": collect_snapshot(driver),
    }
    page_data_path = captures_root / "page-data-admin-ai-governance-failure-detail.json"
    write_json(page_data_path, page_data)
    return {
        "name": "admin-ai-governance-failure-detail",
        "route": "/system/ai-resume-governance",
        "failureId": failure_id,
        "listScreenshotPath": str(list_screenshot_path),
        "detailScreenshotPath": str(detail_screenshot_path),
        "pageDataPath": str(page_data_path),
    }


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: capture-admin-ai-governance-screenshots.py "
            "<sample-root> <history-id> <failure-id> <failure-request-id>"
        )
        return 1

    sample_root = Path(sys.argv[1]).resolve()
    history_id = sys.argv[2].strip()
    failure_id = sys.argv[3].strip()
    failure_request_id = sys.argv[4].strip()

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
        options.add_argument("--window-size=1680,2200")
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
            capture_overview(driver, sample_root, login_data["accessToken"]),
            capture_history_detail(driver, sample_root, login_data["accessToken"], history_id),
            capture_failure_detail(driver, sample_root, login_data["accessToken"], failure_id, failure_request_id),
        ]

        manifest = {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "baseUrl": REMOTE_API,
            "proxyUrl": f"http://127.0.0.1:{LOCAL_PROXY_PORT}",
            "localAdminUrl": f"http://127.0.0.1:{LOCAL_APP_PORT}",
            "historyId": history_id,
            "failureId": failure_id,
            "failureRequestId": failure_request_id,
            "captures": captures,
        }
        write_json(captures_root / "admin-ai-governance-screenshot-capture.json", manifest)
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

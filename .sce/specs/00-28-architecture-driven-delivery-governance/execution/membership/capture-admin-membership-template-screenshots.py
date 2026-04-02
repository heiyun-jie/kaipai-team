import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urljoin

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


REMOTE_BASE = "http://101.43.57.62"
REMOTE_API = f"{REMOTE_BASE}/api"
ADMIN_ACCOUNT = "admin"
ADMIN_PASSWORD = "admin123"
LOCAL_PROXY_PORT = 8010
LOCAL_APP_PORT = 5174
ADMIN_WORKDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "kaipai-admin"))


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
        self.wfile.write(response.content)

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
    WebDriverWait(driver, timeout).until(
        lambda current: text in current.page_source
    )


def click_button(driver: webdriver.Edge, text: str, timeout: int = 20) -> None:
    button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, f"//button[.//span[contains(normalize-space(.), '{text}')]]"))
    )
    button.click()


def fill_input_by_placeholder(driver: webdriver.Edge, placeholder: str, value: str, timeout: int = 20) -> None:
    input_el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"input[placeholder='{placeholder}']"))
    )
    input_el.clear()
    input_el.send_keys(value)


def capture_membership_page(driver: webdriver.Edge, base_url: str, screenshot_path: str) -> dict:
    driver.get(f"{base_url}/membership/accounts")
    wait_for_text(driver, "会员账户")
    fill_input_by_placeholder(driver, "用户 ID", "10000")
    click_button(driver, "查询")
    wait_for_text(driver, "10000")
    driver.save_screenshot(screenshot_path)
    return {"route": "/membership/accounts", "screenshot": screenshot_path}


def capture_template_page(driver: webdriver.Edge, base_url: str, screenshot_path: str, dialog_path: str) -> dict:
    driver.get(f"{base_url}/content/templates")
    wait_for_text(driver, "场景模板")
    fill_input_by_placeholder(driver, "sceneKey", "general")
    click_button(driver, "查询")
    wait_for_text(driver, "Smoke Template")
    driver.save_screenshot(screenshot_path)

    rollback_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//tr[.//*[contains(normalize-space(.), 'Smoke Template')]]//button[.//span[contains(normalize-space(.), '回滚')]]"))
    )
    rollback_button.click()
    wait_for_text(driver, "回滚模板")
    driver.save_screenshot(dialog_path)

    close_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'el-dialog')]//button[.//span[contains(normalize-space(.), '取消')]]"))
    )
    close_button.click()
    return {
        "route": "/content/templates",
        "screenshot": screenshot_path,
        "rollbackDialogScreenshot": dialog_path,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: capture-admin-membership-template-screenshots.py <sample-root>")
        return 1

    sample_root = os.path.abspath(sys.argv[1])
    screenshot_root = os.path.join(sample_root, "screenshots")
    capture_root = os.path.join(sample_root, "captures")
    os.makedirs(screenshot_root, exist_ok=True)
    os.makedirs(capture_root, exist_ok=True)

    proxy_server, proxy_thread = start_proxy_if_needed()
    wait_http_ready(f"http://127.0.0.1:{LOCAL_PROXY_PORT}/api/v3/api-docs", timeout=20)

    vite_log_path = os.path.join(capture_root, "admin-local-vite.log")
    vite_log_handle = open(vite_log_path, "w", encoding="utf-8", newline="\n")
    vite_process = subprocess.Popen(
        ["npm.cmd", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(LOCAL_APP_PORT), "--strictPort"],
        cwd=ADMIN_WORKDIR,
        stdout=vite_log_handle,
        stderr=subprocess.STDOUT,
        shell=False,
    )

    driver = None
    try:
        wait_http_ready(f"http://127.0.0.1:{LOCAL_APP_PORT}/login", timeout=90)
        login_data = login_admin()

        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1600,1400")
        driver = webdriver.Edge(options=options)
        driver.set_page_load_timeout(45)

        base_url = f"http://127.0.0.1:{LOCAL_APP_PORT}"
        driver.get(f"{base_url}/login")
        driver.execute_script(
            """
            localStorage.setItem('kaipai-admin-token', arguments[0]);
            localStorage.setItem('kaipai-admin-session', JSON.stringify(arguments[1]));
            """,
            login_data["accessToken"],
            login_data["adminUserInfo"],
        )

        membership_path = os.path.join(screenshot_root, "admin-membership-accounts.png")
        templates_path = os.path.join(screenshot_root, "admin-content-templates.png")
        rollback_dialog_path = os.path.join(screenshot_root, "admin-content-templates-rollback-dialog.png")

        membership_result = capture_membership_page(driver, base_url, membership_path)
        template_result = capture_template_page(driver, base_url, templates_path, rollback_dialog_path)

        result = {
            "generatedAt": datetime_now_iso(),
            "baseUrl": base_url,
            "proxyUrl": f"http://127.0.0.1:{LOCAL_PROXY_PORT}",
            "remoteApi": REMOTE_API,
            "membership": membership_result,
            "templates": template_result,
        }

        with open(os.path.join(capture_root, "admin-screenshot-capture.json"), "w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
        print(json.dumps(result, ensure_ascii=False, indent=2))
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


def datetime_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


if __name__ == "__main__":
    raise SystemExit(main())

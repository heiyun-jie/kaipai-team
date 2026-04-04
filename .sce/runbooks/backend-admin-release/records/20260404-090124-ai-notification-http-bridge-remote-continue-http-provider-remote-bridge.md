# AI 通知 HTTP Bridge Mock 远端发布记录

## 1. 基本信息

- 发布批次号：`20260404-090124-ai-notification-http-bridge-remote-continue-http-provider-remote-bridge`
- 执行时间：`2026-04-04 09:02:00 +0800`
- 操作人：`codex`
- 目标主机：`101.43.57.62`
- dry-run：`否`
- 最终状态：`public_probe_failed`
- 中止/结束原因：`public_probe_failed`

## 2. 远端进程

- 远端目录：`/home/kaipaile/ai-notification-http-bridge/releases/20260404-090124-ai-notification-http-bridge-remote-continue-http-provider-remote-bridge`
- 当前脚本：`/home/kaipaile/ai-notification-http-bridge/current/run-ai-notification-http-bridge-mock.py`
- 日志：`/home/kaipaile/ai-notification-http-bridge/releases/20260404-090124-ai-notification-http-bridge-remote-continue-http-provider-remote-bridge/bridge.log`
- PID 文件：`/home/kaipaile/ai-notification-http-bridge/current/bridge.pid`
- 启动前旧进程处理：`not-running`
- 当前 PID：`1031095`
- 绑定地址：`http://0.0.0.0:19081/`
- 公网地址：`http://101.43.57.62:19081/`

## 3. 探活结果

- 远端本机探活：`HTTP 200`
- 远端本机回包：`{"success": true, "providerCode": "http", "channelCode": "sms", "providerMessageId": "mock-http-20260404090153-0001", "sendStatus": "sent"}`
- 公网探活：`HTTP 0`
- 公网回包：`Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "C:\Python311\Lib\urllib\request.py", line 216, in urlopen
    return opener.open(url, data, timeout)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python311\Lib\urllib\request.py", line 525, in open
    response = meth(req, response)
               ^^^^^^^^^^^^^^^^^^^
  File "C:\Python311\Lib\urllib\request.py", line 634, in http_response
    response = self.parent.error(
               ^^^^^^^^^^^^^^^^^^
  File "C:\Python311\Lib\urllib\request.py", line 563, in error
    return self._call_chain(*args)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python311\Lib\urllib\request.py", line 496, in _call_chain
    result = func(*args)
             ^^^^^^^^^^^
  File "C:\Python311\Lib\urllib\request.py", line 643, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 502: Bad Gateway`

## 4. 日志尾部

```text
--
```

## 5. 本地 bridge secret

- 已回写：`否`

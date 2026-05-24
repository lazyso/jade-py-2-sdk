# JadeView Python SDK

[JadeView](https://jade.run) 2.1.1 的 Python 绑定库，基于 ctypes 封装 JadeView DLL，使用 Python 构建基于 WebView2 的 Windows 桌面应用。

## 特性

- 窗口管理 — 标准/无边框/title-overlay 窗口，运行时切换边框样式
- IPC 通信 — 事件订阅、通道处理器、双向消息推送
- 对话框 — 打开/保存文件、消息框，同步 + 异步
- 系统托盘 — 图标、提示文字、多级右键菜单
- 系统通知 — Windows 原生通知，支持按钮和动作回调
- WebView — 导航、JS 执行、缩放、打印、防截屏
- 2.1.1 新能力 — `cors_whitelist` 跨域来源白名单、JAPK 内存加载 API
- 工具函数 — 版本信息、系统路径、YAML 配置、全局热键、URL Scheme、文件关联
- 零依赖 — 仅使用 Python 标准库
- 自动适配 — 根据 Python 位数加载 x64/x86 DLL

## 系统要求

- Windows 10 / Windows 11
- Python 3.11+
- WebView2 Runtime（Windows 11 已内置）

## 安装

```bash
pip install jadeview
```

或使用 [uv](https://github.com/astral-sh/uv)：

```bash
uv add jadeview
```

## 快速开始

```python
import jadeview
from jadeview import events

def on_ready(window_id, data):
    jadeview.window.create_webview_window(
        "https://example.com",
        title="Hello JadeView",
        width=1024,
        height=768,
    )

def on_all_closed(window_id, data):
    jadeview.cleanup()

# 注册事件（必须在 init 之前）
jadeview.ipc.on(events.APP_READY, on_ready)
jadeview.ipc.on(events.WINDOW_ALL_CLOSED, on_all_closed)

# 初始化并启动
jadeview.init("MyApp", "myapp1")
jadeview.run()
```

## 加载本地 HTML

```python
from jadeview import tools, window

def on_ready(window_id, data):
    base_url = tools.set_protocol_service_path("./web")
    window.create_webview_window(f"{base_url}index.html", title="本地应用")
```

也支持加载 `.japk` 资源包：

```python
base_url = tools.set_protocol_service_path("./app.japk")
```

## 2.1.1 新增能力

创建窗口时可设置 `cors_whitelist`，允许指定跨域页面调用 JadeView 内部 API：

```python
window.create_webview_window(
    "http://localhost:3000",
    title="Dev App",
    cors_whitelist="http://localhost:3000, http://198.18.0.1:8001",
)
```

也可以从内存直接加载 JAPK：

```python
from jadeview import japk

with open("app.japk", "rb") as f:
    payload = f.read()

rc = japk.load_from_bytes(payload)
print(rc, japk.is_loaded(), japk.get_app_signature())
```

## 模块一览

| 模块 | 功能 |
|------|------|
| `jadeview` | 初始化、消息循环、清理 |
| `jadeview.window` | 窗口创建与管理、边框样式、打印 |
| `jadeview.webview` | 导航、JS 执行、缩放 |
| `jadeview.ipc` | 事件订阅、IPC 通信 |
| `jadeview.dialog` | 系统对话框（同步 + 异步） |
| `jadeview.tray` | 系统托盘 |
| `jadeview.notification` | 系统通知 |
| `jadeview.tools` | 工具函数（路径/热键/YAML/协议注册等） |
| `jadeview.events` | 事件名称常量 |

## 运行示例

```bash
git clone https://github.com/lazyso/jade-py-2-sdk.git
cd jade-py-2-sdk
uv sync
uv run examples/demo_full.py
```

## 应用打包

SDK 支持 PyInstaller、Nuitka、cx_Freeze 等打包工具。打包时需将 DLL 包含到输出中：

```bash
# PyInstaller
pyinstaller --add-binary "jadeview/dll/x64/JadeView_x64.dll;." main.py

# Nuitka
nuitka --include-data-files=jadeview/dll/x64/JadeView_x64.dll=JadeView_x64.dll main.py
```

DLL 搜索优先级：环境变量 `JADEVIEW_DLL_PATH` → PyInstaller `_MEIPASS` → exe 目录 → 工作目录 → SDK 包内部。

## 文档

完整 API 文档请访问：https://jade.run/python-sdk2

## AI 辅助开发

仓库根目录的 [`LLM.md`](./LLM.md) 是为 AI 助手优化的精简参考文档，包含完整 API 签名、约定和高频代码模式。在 Cursor/Copilot/Claude 等工具中将其作为上下文，可直接让 AI 基于本 SDK 编写代码。

## 版本

- SDK：2.1.1+26E26
- 兼容 JadeView：v2.1.1.26E26

## 许可证

MIT

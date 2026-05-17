# JadeView Python SDK — AI 开发参考

> 本文档为 AI 助手优化，包含完整的 API 签名、约定和可复制的代码模式。
> 用户在 IDE 中将此文档作为上下文喂给 AI 后，可直接基于本 SDK 编写代码。

## 库信息

- **名称**：`jadeview`
- **版本**：2.0.0（兼容 JadeView DLL v2.0.0.26E03）
- **平台**：仅 Windows 10/11，Python 3.11+
- **底层**：基于 ctypes 封装 JadeView Rust DLL，渲染层使用 WebView2
- **依赖**：无（仅 Python 标准库）
- **安装**：`pip install jadeview`

## 核心架构

```
Python 后端 (jadeview.*) ──ctypes──> JadeView DLL (x64/x86) ──> WebView2 ──> HTML/JS 前端
```

- **Python 端**：调用 SDK 函数、处理事件、注册 IPC handler
- **前端**：通过 `jade.invoke(channel, payload)` 调 Python，通过 `jade.on(type, cb)` 接收 Python 推送
- **DLL**：根据 Python 位数自动加载 `JadeView_x64.dll` 或 `JadeView_x86.dll`

## 标准应用骨架（必须遵循）

```python
import jadeview
from jadeview import events, ipc, window, tools

def on_ready(window_id, data):
    """app-ready 后才能创建窗口、调用其他 API"""
    win_id = window.create_webview_window("https://example.com", title="App")

def on_all_closed(window_id, data):
    """所有窗口关闭后清理退出"""
    jadeview.cleanup()

# === 关键顺序 ===
# 1. 必须先注册事件（特别是 app-ready）
ipc.on(events.APP_READY, on_ready)
ipc.on(events.WINDOW_ALL_CLOSED, on_all_closed)

# 2. 再调用 init
jadeview.init("AppName", "appid_>=6chars")

# 3. 最后启动消息循环（阻塞）
jadeview.run()
```

**关键约定**：
- `app-ready` 事件必须在 `init()` 之前注册，否则错过通知
- `app_signature` 至少 6 个字符
- `init()` 返回 True 仅表示已启动，需等 `app-ready` 才能继续操作
- `run()` 是阻塞的，所有窗口关闭前不返回

## 模块导入

```python
import jadeview                      # 顶层：init/run/cleanup
from jadeview import events          # 事件名常量
from jadeview import ipc             # 事件订阅、IPC 通信
from jadeview import window          # 窗口管理
from jadeview import webview         # 导航/JS/缩放
from jadeview import dialog          # 系统对话框
from jadeview import tray            # 系统托盘
from jadeview import notification    # 系统通知
from jadeview import tools           # 工具函数
```

---

## API 完整参考

### jadeview（顶层）

```python
jadeview.init(
    app_name: str,                    # 应用显示名（必填）
    app_signature: str,               # 唯一标识，>=6 字符（必填）
    *,
    enable_devmod: bool = False,      # 启用 DevTools/调试快捷键
    log_path: str | None = None,      # 日志文件路径
    data_directory: str | None = None,# 数据根目录（None 用 %LOCALAPPDATA%）
    single_instance: bool = False,    # 单实例模式
) -> bool

jadeview.run() -> bool                # 启动消息循环（阻塞）
jadeview.cleanup() -> bool            # 关闭所有窗口并退出循环
```

### jadeview.window（窗口管理）

```python
# === 创建窗口 ===
window.create_webview_window(
    url: str,                          # 加载的 URL
    parent_window_id: int = 0,         # 父窗口（0 = 顶级）
    *,
    title: str | None = None,
    width: int = 800, height: int = 600,
    resizable: int = 1,
    frame_style: str | None = None,    # "normal"/"no-titlebar"/"borderless"/"title-overlay"
    transparent: int = 0,
    background_color: str | None = None,  # "#RRGGBB"
    always_on_top: int = 0,
    theme: str | None = None,          # "Light"/"Dark"/"System"
    maximized: int = 0,
    maximizable: int = 1, minimizable: int = 1,
    x: int = -1, y: int = -1,         # 均为 -1 时居中
    min_width: int = 0, min_height: int = 0,
    max_width: int = 0, max_height: int = 0,
    fullscreen: int = 0,
    focus: int = 1,
    hide_window: int = 0,
    use_page_icon: int = 0,            # 用 favicon 作窗口图标
    content_protection: int = 0,       # 防截屏
    auto_save_state: int = 0,          # 自动记忆窗口位置
    # WebView 设置
    autoplay: int = 0,
    background_throttling: int = 1,
    disable_right_click: int = 0,
    ua: str | None = None,
    preload_js: str | None = None,
    allow_fullscreen: int = 1,
    postmessage_whitelist: str | None = None,
) -> int  # window_id（>0 成功，0 失败）

window.create_borderless_webview_window(url: str, **webview_settings) -> int
window.get_window_hwnd(window_id: int) -> int  # 仅 borderless 窗口可用

# === 窗口操作 ===
window.set_window_title(window_id, title) -> bool
window.set_window_size(window_id, width, height) -> bool
window.set_window_position(window_id, x, y) -> bool
window.set_window_visible(window_id, visible: bool) -> bool
window.set_window_focus(window_id) -> bool
window.set_window_always_on_top(window_id, always_on_top: bool) -> bool
window.close_window(window_id) -> bool
window.minimize_window(window_id) -> bool
window.toggle_maximize_window(window_id) -> bool
window.is_window_maximized(window_id) -> bool
window.set_window_fullscreen(window_id, fullscreen: bool) -> bool
window.set_window_enabled(window_id, enabled: bool) -> bool
window.request_redraw(window_id) -> bool

# === 主题与外观 ===
window.set_window_theme(window_id, theme: str) -> bool          # Light/Dark/System
window.get_window_theme(window_id) -> int
window.set_window_backdrop(window_id, backdrop_type: str) -> bool   # mica/micaAlt/acrylic
window.set_window_background_color(window_id, color: str) -> bool   # #RRGGBB

# === 边框样式（v2.0 新增）===
window.set_window_frame_style(window_id, frame_style: str) -> bool  # 运行时切换

window.set_titlebar_overlay_style(
    window_id: int,
    height: int = 0,                   # 0 = 默认 32
    icon_color_hex: str | None = None, # "#RRGGBB"
    hover_bg_hex: str | None = None,   # "#RRGGBB" 或 "#RRGGBBAA"
) -> bool

window.jade_print(window_id) -> bool   # 打开系统打印对话框
```

### jadeview.webview

```python
webview.navigate_to_url(window_id, url: str) -> bool
webview.reload(window_id) -> bool
webview.execute_javascript(window_id, script: str) -> bool   # 结果通过 javascript-result 事件
webview.set_zoom(window_id, level: float = 1.0) -> bool      # 1.0 = 100%
webview.set_content_protection(window_id, enabled: bool) -> bool
```

### jadeview.ipc（事件 + IPC 通信）

```python
# === 事件订阅 ===
ipc.on(
    event_name: str,
    callback: Callable[[int, str], str | bool | None],
) -> int  # callback_id（>0 成功）

# 回调返回值：
#   None  -> 放行/无操作
#   True  -> 拦截事件（用于可拦截事件如 window-closing）
#   str   -> 自定义返回数据

ipc.off(event_name: str, callback_id: int) -> bool

# === IPC 通道（前端 jade.invoke 入口）===
ipc.register_ipc_handler(
    channel: str,
    handler: Callable[[int, str], str | dict | None],
) -> bool

# Handler 返回值：
#   None    -> 默认成功响应
#   dict    -> 自动 json.dumps 返回前端
#   str     -> 直接作为返回值

# === Python -> 前端推送 ===
ipc.send_ipc_message(
    window_id: int,
    message_type: str,        # 前端用 jade.on(message_type, ...) 接收
    content: str | dict,       # dict 自动序列化
) -> bool
```

### jadeview.dialog

```python
# === 同步（阻塞）===
dialog.show_open_dialog(
    window_id: int = 0,
    *,
    title: str | None = None,
    default_path: str | None = None,
    button_label: str | None = None,
    filters: str | None = None,        # JSON 字符串
    properties: str = "openFile",       # 逗号分隔
) -> dict | None
# 返回: {"canceled": bool, "file_paths": [...]}

dialog.show_save_dialog(window_id=0, *, title=None, default_path=None,
                        button_label=None, filters=None) -> dict | None
# 返回: {"canceled": bool, "file_path": "..." | None}

dialog.show_message_box(
    window_id: int = 0, *,
    title: str | None = None,
    message: str | None = None,
    detail: str | None = None,
    buttons: str | None = None,        # "确定|取消"
    default_id: int = 0,
    cancel_id: int = -1,
    type_: str = "info",                # none/info/warning/error/question
) -> dict | None
# 返回: {"response": int}  (按钮索引)

dialog.show_error_box(window_id=0, title="错误", content="") -> int

# === 异步（不阻塞）===
dialog.show_open_dialog_async(callback, window_id=0, **kwargs) -> bool
dialog.show_save_dialog_async(callback, window_id=0, **kwargs) -> bool
dialog.show_message_box_async(callback, window_id=0, **kwargs) -> bool
# callback 签名: (result: dict | None) -> None
```

**filters 格式**：
```python
filters='[{"name":"图片","extensions":["jpg","png"]},{"name":"所有文件","extensions":["*"]}]'
```

**properties 取值**（逗号分隔）：`openFile`, `openDirectory`, `multiSelections`, `showHiddenFiles`, `createDirectory`

### jadeview.tray

```python
tray.tray_create() -> int                              # 返回 tray_id（全进程仅一个）
tray.tray_destroy(tray_id) -> bool
tray.tray_set_visible(tray_id, visible: bool) -> bool
tray.tray_set_tooltip(tray_id, tooltip: str) -> bool
tray.tray_set_icon_from_file(tray_id, icon_path: str) -> bool   # .ico 文件
tray.tray_set_menu_items(tray_id, items: list[dict]) -> bool

# items 格式:
[
    {"item_type": 0, "key": "open",    "label": "打开"},                    # 普通项
    {"item_type": 1, "key": "submenu", "label": "更多"},                    # 子菜单
    {"item_type": 0, "key": "child",   "label": "子项", "parent_key": "submenu"},
    {"item_type": 2, "key": "sep",     "label": ""},                        # 分隔线（也要 key）
    {"item_type": 0, "key": "exit",    "label": "退出", "dangerous": 1},     # 危险项
]
# item_type: 0=普通 / 1=子菜单 / 2=分隔线 / 3=分组
```

### jadeview.notification

```python
notification.show_notification(
    summary: str,                      # 标题（必填）
    *,
    body: str | None = None,
    icon: str | None = None,           # 图标绝对路径
    timeout: int = 0,                  # ms，<=0 用系统默认
    button1: str | None = None,
    button2: str | None = None,
    text3: str | None = None,
    action: str | None = None,         # 通过 notification-action 事件回传
) -> bool
```

### jadeview.tools

```python
# === 版本与系统 ===
tools.jadeview_version() -> str | None        # "2.0.0.xxxx"
tools.get_webview_version() -> str | None     # WebView2 运行时版本
tools.is_windows_11() -> bool
tools.get_window_count() -> int
tools.get_locale() -> str | None              # "zh-CN"
tools.get_displays_info() -> list[dict] | None  # 多显示器信息
tools.get_path(name: str) -> str | None       # home/appData/temp/desktop/...

# === 协议服务（本地静态资源）===
tools.set_protocol_service_path(root_path: str) -> str | None
# root_path: 目录路径 或 .japk 文件路径
# 返回: 内置协议 URL，前缀给 create_webview_window 用

# === YAML 配置 ===
tools.yaml_set(file_name: str, key_path: str, value: str) -> bool
tools.yaml_get(file_name: str, key_path: str) -> str | None
# file_name 不含路径（保存在数据目录），key_path 用点分隔如 "ui.theme"

# === 系统集成 ===
tools.register_url_scheme(scheme: str) -> bool        # 注册 myapp://
tools.unregister_url_scheme(scheme: str) -> bool
tools.register_file_association(extension, friendly_name) -> bool
tools.unregister_file_association(extension) -> bool

# === 全局热键 ===
tools.register_global_hotkey(modifiers, vk) -> int
# modifiers: int 位掩码 / "CTRL+ALT" / ["CTRL", "SHIFT"]
# vk: int 虚拟键码 / "A"-"Z" / "F1"-"F24" / "Enter"/"Space"/"ESC" 等
tools.unregister_global_hotkey(hotkey_id) -> bool

tools.clear_data_directory() -> bool   # 清空数据目录（不可逆）
```

### jadeview.events（事件常量）

```python
# === 应用生命周期 ===
events.APP_READY                # "app-ready"  必须在 init 前订阅
events.SECOND_INSTANCE          # "second-instance"

# === 窗口 ===
events.WINDOW_CREATED           # "window-created"
events.WINDOW_CLOSING           # "window-closing"      可拦截（return True）
events.WINDOW_CLOSED            # "window-closed"
events.WINDOW_DESTROYED         # "window-destroyed"
events.WINDOW_ALL_CLOSED        # "window-all-closed"
events.WINDOW_RESIZED           # "window-resized"      data: {"width":n,"height":n}
events.WINDOW_MOVED             # "window-moved"        data: {"x":n,"y":n}
events.WINDOW_STATE_CHANGED     # "window-state-changed" data: {"isMaximized":bool}
events.WINDOW_FULLSCREEN        # "window-fullscreen"   data: {"fullscreen":bool}
events.WINDOW_FOCUSED           # "window-focused"
events.WINDOW_BLURRED           # "window-blurred"

# === WebView ===
events.WEBVIEW_WILL_NAVIGATE        # 可拦截
events.WEBVIEW_DID_START_LOADING
events.WEBVIEW_DID_FINISH_LOAD
events.WEBVIEW_NEW_WINDOW           # 可拦截
events.WEBVIEW_PAGE_TITLE_UPDATED
events.WEBVIEW_PAGE_ICON_UPDATED
events.WEBVIEW_DOWNLOAD_STARTED     # 默认拦截，return None 才允许下载
events.JAVASCRIPT_RESULT            # execute_javascript 结果
events.FILE_DROP                    # 文件拖入
events.POSTMESSAGE_RECEIVED         # 页面 postMessage

# === 托盘 / 通知 / 热键 / 主题 ===
events.TRAY_MENU_COMMAND        # 菜单项点击, data 含 key
events.TRAY_EVENT               # 图标交互
events.NOTIFICATION_SHOWN
events.NOTIFICATION_DISMISSED
events.NOTIFICATION_FAILED
events.NOTIFICATION_ACTION      # 按钮点击, data 含 action
events.GLOBAL_HOTKEY            # 全局热键触发
events.THEME_CHANGED
```

---

## 关键模式

### 模式 1：加载本地 HTML

```python
def on_ready(window_id, data):
    base_url = tools.set_protocol_service_path("./web")
    window.create_webview_window(f"{base_url}index.html", title="App")
```

### 模式 2：前端调 Python（jade.invoke）

```python
# Python 端
def handle_get_user(window_id, payload):
    # payload 是前端传的 JSON 字符串
    return {"name": "Alice", "age": 30}  # dict 自动转 JSON

ipc.register_ipc_handler("get-user", handle_get_user)
```

```javascript
// 前端
const user = await jade.invoke("get-user", JSON.stringify({id: 1}));
console.log(user.name);  // "Alice"
```

### 模式 3：Python 推送给前端（send_ipc_message）

```python
# Python 端
ipc.send_ipc_message(window_id, "data-update", {"count": 42})
```

```javascript
// 前端
jade.on("data-update", (data) => console.log(data.count));
```

### 模式 4：拦截窗口关闭（确认对话框）

```python
def on_window_closing(window_id, data):
    result = dialog.show_message_box(
        window_id, message="确定关闭？", buttons="确定|取消", type_="question",
    )
    if result and result["response"] == 1:
        return True   # 拦截关闭
    return None       # 允许关闭

ipc.on(events.WINDOW_CLOSING, on_window_closing)
```

### 模式 5：系统托盘 + 主窗口最小化到托盘

```python
main_win_id = 0
tray_id = 0

def on_ready(window_id, data):
    global main_win_id, tray_id
    main_win_id = window.create_webview_window("...", title="App")
    tray_id = tray.tray_create()
    tray.tray_set_tooltip(tray_id, "App 运行中")
    tray.tray_set_menu_items(tray_id, [
        {"item_type": 0, "key": "show", "label": "显示窗口"},
        {"item_type": 2, "key": "sep", "label": ""},
        {"item_type": 0, "key": "exit", "label": "退出", "dangerous": 1},
    ])

def on_tray_menu(window_id, data):
    info = json.loads(data)
    if info["key"] == "show":
        window.set_window_visible(main_win_id, True)
        window.set_window_focus(main_win_id)
    elif info["key"] == "exit":
        window.close_window(main_win_id)

def on_window_closing(window_id, data):
    # 关闭按钮 = 隐藏到托盘，不真正退出
    window.set_window_visible(window_id, False)
    return True  # 拦截

ipc.on(events.TRAY_MENU_COMMAND, on_tray_menu)
ipc.on(events.WINDOW_CLOSING, on_window_closing)
```

### 模式 6：title-overlay（自定义标题栏 + 系统按钮）

```python
# Python 端
def on_ready(window_id, data):
    win_id = window.create_webview_window(
        url, title="App",
        frame_style="title-overlay",       # 关键：使用 title-overlay
        background_color="#f3f3f3",
    )
    # 可选：自定义按钮外观
    window.set_titlebar_overlay_style(
        win_id, height=40, icon_color_hex="#333", hover_bg_hex="#00000020",
    )
```

```html
<!-- 前端：标题栏区域用 app-region: drag -->
<div style="-webkit-app-region: drag; height: 40px; padding: 0 16px;">
    <span>我的应用</span>
</div>
<div style="-webkit-app-region: no-drag;"><!-- 内容 --></div>
```

### 模式 7：全局热键

```python
hotkey_id = 0

def on_ready(window_id, data):
    global hotkey_id
    hotkey_id = tools.register_global_hotkey("CTRL+ALT", "K")  # Ctrl+Alt+K

def on_hotkey(window_id, data):
    # data: '{"id":n,"modifiers":n,"vk":n}'
    print("热键触发！")

ipc.on(events.GLOBAL_HOTKEY, on_hotkey)
```

### 模式 8：异步执行 JS 并拿结果

```python
def on_ready(window_id, data):
    win_id = window.create_webview_window("...")
    webview.execute_javascript(win_id, "document.title")

def on_js_result(window_id, data):
    # data: '{"id":n,"result":...}'
    info = json.loads(data)
    print("JS 返回:", info.get("result"))

ipc.on(events.JAVASCRIPT_RESULT, on_js_result)
```

### 模式 9：YAML 持久化用户配置

```python
# 保存
tools.yaml_set("config.yaml", "ui.theme", "dark")
tools.yaml_set("config.yaml", "ui.lang", "zh-CN")

# 读取（值返回 JSON 字符串，需要解析）
theme = tools.yaml_get("config.yaml", "ui.theme")
# theme == '"dark"'，需要 json.loads(theme) 得到 "dark"
```

### 模式 10：异步对话框

```python
def on_file_chosen(result):
    if result and not result["canceled"]:
        print("选择:", result["file_paths"])

dialog.show_open_dialog_async(
    on_file_chosen, window_id=0,
    title="选择文件", properties="openFile,multiSelections",
)
```

---

## 常见陷阱与注意事项

1. **app-ready 必须先注册**：在 `init()` 之前调用 `ipc.on(events.APP_READY, ...)`，否则错过通知
2. **`run()` 是阻塞的**：所有窗口关闭前不会返回；通过 `events.WINDOW_ALL_CLOSED` 触发 `cleanup()`
3. **回调返回值有特殊语义**：`None` 放行 / `True` 拦截 / `str` 数据
4. **整型 0/1 而非 bool**：窗口选项很多用 `int` 类型（历史原因），传 0 或 1
5. **frame_style 删了旧字段**：v2.0 不能用 `remove_titlebar`、`borderless` 等旧字段，统一用 `frame_style`
6. **居中**：`x=-1, y=-1` 同时为 -1 才居中
7. **app_signature**：必须 ≥ 6 字符，否则 `app-ready` 收到失败 JSON
8. **协议 URL 拼接**：`set_protocol_service_path` 返回的 URL 已带 `/` 结尾，直接拼文件名即可
9. **postmessage_whitelist 默认不放行**：如果用 `set_protocol_service_path` 加载的内置静态页则跳过白名单
10. **托盘单例**：整个进程只能有一个托盘，重复 `tray_create` 返回同一个 id
11. **send_ipc_message 大消息**：单次建议 ≤ 252MB
12. **DLL 自动按位选择**：不用手动选 x64/x86，Python 解释器位数决定
13. **打包**：DLL 不会被自动打包工具识别，需手动添加（见 README）

## 完整最小应用模板

```python
"""完整可运行的最小 JadeView 应用模板"""
import json
import jadeview
from jadeview import events, ipc, window, webview, dialog, tray, notification, tools

# 全局状态
main_win_id = 0
tray_id = 0


def on_ready(window_id, data):
    global main_win_id, tray_id

    print(f"JadeView {tools.jadeview_version()}")

    # 加载本地资源
    base_url = tools.set_protocol_service_path("./web")
    main_win_id = window.create_webview_window(
        f"{base_url}index.html",
        title="My App",
        width=1024, height=768,
        theme="System",
        min_width=600, min_height=400,
    )

    # 创建托盘
    tray_id = tray.tray_create()
    tray.tray_set_tooltip(tray_id, "My App")
    tray.tray_set_menu_items(tray_id, [
        {"item_type": 0, "key": "show", "label": "显示"},
        {"item_type": 2, "key": "sep", "label": ""},
        {"item_type": 0, "key": "exit", "label": "退出", "dangerous": 1},
    ])


def on_tray_menu(window_id, data):
    key = json.loads(data).get("key")
    if key == "show":
        window.set_window_visible(main_win_id, True)
        window.set_window_focus(main_win_id)
    elif key == "exit":
        window.close_window(main_win_id)


def on_all_closed(window_id, data):
    if tray_id:
        tray.tray_destroy(tray_id)
    jadeview.cleanup()


# IPC handler 示例：前端 await jade.invoke('get-info')
def handle_get_info(window_id, payload):
    return {
        "version": tools.jadeview_version(),
        "locale": tools.get_locale(),
        "is_win11": tools.is_windows_11(),
    }


# 事件订阅（必须在 init 前）
ipc.on(events.APP_READY, on_ready)
ipc.on(events.WINDOW_ALL_CLOSED, on_all_closed)
ipc.on(events.TRAY_MENU_COMMAND, on_tray_menu)

# IPC handler 注册
ipc.register_ipc_handler("get-info", handle_get_info)

# 启动
jadeview.init("MyApp", "myapp1", enable_devmod=True)
jadeview.run()
```

---

## 项目链接

- **GitHub**：https://github.com/lazyso/jade-py-2-sdk
- **PyPI**：https://pypi.org/project/jadeview/
- **完整文档**：https://jade.run/python-sdk2

"""JadeView 2.1.1 SDK 全功能演示

覆盖全部 SDK 模块: 窗口/WebView/IPC/对话框/托盘/通知/工具函数。
前端通过 set_protocol_service_path 加载本地 HTML。

用法:
    cd examples
    python demo_full.py
"""

import os
import sys
import json

# 添加 SDK 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import jadeview
from jadeview import events, ipc, window, webview, dialog, tray, notification, tools

# --- 全局状态 ---
main_win_id = 0            # 主窗口 ID
child_windows = []         # 子窗口列表
tray_id = 0                # 托盘 ID
tray_visible = True        # 托盘可见状态
hotkey_id = 0              # 全局热键 ID
content_protected = False  # 内容保护状态
win_enabled = True         # 窗口启用状态
win_visible = True         # 窗口可见状态


def push_log(win_id, msg):
    """向前端推送事件日志"""
    ipc.send_ipc_message(win_id, "event-log", {"message": msg})


def push_log_all(msg):
    """向所有窗口推送日志"""
    if main_win_id:
        push_log(main_win_id, msg)


# ========== 事件回调 ==========

def on_ready(window_id, data):
    """应用就绪 - 设置协议服务并创建主窗口"""
    global main_win_id

    # 设置本地文件服务路径
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    print(f"[启动] 网页目录: {web_dir}")
    base_url = tools.set_protocol_service_path(web_dir)
    print(f"[启动] 协议服务: {base_url}")
    print(f"[启动] JadeView {tools.jadeview_version()}, WebView2 {tools.get_webview_version()}")

    # 创建主窗口 - 加载主控面板
    main_win_id = window.create_webview_window(
        f"{base_url}index.html",
        title="JadeView 2.1.1 全功能演示",
        width=1100,
        height=800,
        theme="System",
        min_width=800,
        min_height=600,
        # 如需允许跨域页面调用 JadeView 内部 API，可显式配置来源白名单
        # cors_whitelist="http://localhost:3000, http://198.18.0.1:8001",
    )
    print(f"[启动] 主窗口 ID: {main_win_id}")


def on_window_closing(window_id, data):
    """窗口关闭拦截"""
    print(f"[事件] 窗口 {window_id} 关闭中")
    if window_id in child_windows:
        child_windows.remove(window_id)
    return None  # 允许关闭


def on_all_closed(window_id, data):
    """所有窗口关闭 → 退出"""
    global tray_id
    if tray_id:
        tray.tray_destroy(tray_id)
        tray_id = 0
    print("[退出] 所有窗口已关闭")
    jadeview.cleanup()


def on_window_created(window_id, data):
    push_log_all(f"窗口已创建: {window_id}")

def on_window_destroyed(window_id, data):
    push_log_all(f"窗口已销毁: {window_id}")

def on_window_resized(window_id, data):
    push_log_all(f"窗口 {window_id} 大小变化: {data}")

def on_window_moved(window_id, data):
    push_log_all(f"窗口 {window_id} 位置变化: {data}")

def on_window_focused(window_id, data):
    push_log_all(f"窗口 {window_id} 获得焦点")

def on_window_blurred(window_id, data):
    push_log_all(f"窗口 {window_id} 失去焦点")

def on_window_state_changed(window_id, data):
    push_log_all(f"窗口 {window_id} 状态变化: {data}")

def on_window_fullscreen(window_id, data):
    push_log_all(f"窗口 {window_id} 全屏: {data}")

def on_theme_changed(window_id, data):
    push_log_all(f"主题变化: {data}")

def on_webview_will_navigate(window_id, data):
    push_log_all(f"即将导航: {data}")

def on_webview_start_loading(window_id, data):
    push_log_all(f"开始加载: 窗口 {window_id}")

def on_webview_finish_load(window_id, data):
    push_log_all(f"加载完成: 窗口 {window_id}")

def on_webview_title_updated(window_id, data):
    push_log_all(f"标题更新: {data}")

def on_webview_new_window(window_id, data):
    push_log_all(f"新窗口请求: {data}")

def on_file_drop(window_id, data):
    push_log_all(f"文件拖放: {data}")

def on_postmessage(window_id, data):
    push_log_all(f"PostMessage: {data}")

def on_js_result(window_id, data):
    push_log_all(f"JS结果: {data}")
    if main_win_id:
        ipc.send_ipc_message(main_win_id, "js-result", {"result": data})

def on_tray_menu(window_id, data):
    push_log_all(f"托盘菜单: {data}")

def on_tray_event(window_id, data):
    push_log_all(f"托盘事件: {data}")

def on_notification_shown(window_id, data):
    push_log_all(f"通知已显示")

def on_notification_dismissed(window_id, data):
    push_log_all(f"通知已关闭")

def on_notification_action(window_id, data):
    push_log_all(f"通知动作: {data}")

def on_global_hotkey(window_id, data):
    print(f"[热键] 收到全局热键事件: window_id={window_id}, data={data}")
    push_log_all(f"全局热键触发: {data}")
    # 切换主窗口可见
    if main_win_id:
        window.set_window_focus(main_win_id)


# ========== IPC Handler (前端 jade.invoke → Python) ==========

def handle_win_create(window_id, payload):
    """创建子窗口"""
    base_url = tools.set_protocol_service_path(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    )
    wid = window.create_webview_window(
        f"{base_url}ipc_test.html",
        parent_window_id=main_win_id,
        title=f"子窗口 #{len(child_windows)+1}",
        width=640, height=480,
    )
    if wid:
        child_windows.append(wid)
    return json.dumps({"window_id": wid})


def handle_win_create_borderless(window_id, payload):
    """创建无边框窗口"""
    base_url = tools.set_protocol_service_path(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    )
    wid = window.create_borderless_webview_window(f"{base_url}ipc_test.html")
    if wid:
        child_windows.append(wid)
        hwnd = window.get_window_hwnd(wid)
        return json.dumps({"window_id": wid, "hwnd": hwnd})
    return json.dumps({"error": "创建失败"})


def _last_child_or_main():
    """获取最后一个子窗口或主窗口"""
    return child_windows[-1] if child_windows else main_win_id


def handle_win_set_title(window_id, payload):
    wid = _last_child_or_main()
    window.set_window_title(wid, "新标题 - JadeView Demo")
    return "ok"

def handle_win_set_size(window_id, payload):
    wid = _last_child_or_main()
    window.set_window_size(wid, 900, 700)
    return "ok"

def handle_win_set_position(window_id, payload):
    wid = _last_child_or_main()
    window.set_window_position(wid, 100, 100)
    return "ok"

def handle_win_minimize(window_id, payload):
    wid = _last_child_or_main()
    window.minimize_window(wid)
    return "ok"

def handle_win_toggle_maximize(window_id, payload):
    wid = _last_child_or_main()
    window.toggle_maximize_window(wid)
    is_max = window.is_window_maximized(wid)
    return json.dumps({"maximized": is_max})

def handle_win_fullscreen(window_id, payload):
    wid = _last_child_or_main()
    window.set_window_fullscreen(wid, True)
    return "ok"

def handle_win_always_on_top(window_id, payload):
    wid = _last_child_or_main()
    window.set_window_always_on_top(wid, True)
    return "ok"

def handle_win_set_enabled(window_id, payload):
    global win_enabled
    wid = _last_child_or_main()
    win_enabled = not win_enabled
    window.set_window_enabled(wid, win_enabled)
    return json.dumps({"enabled": win_enabled})

def handle_win_hide_show(window_id, payload):
    global win_visible
    wid = _last_child_or_main()
    win_visible = not win_visible
    window.set_window_visible(wid, win_visible)
    return json.dumps({"visible": win_visible})

def handle_win_focus(window_id, payload):
    wid = _last_child_or_main()
    window.set_window_focus(wid)
    return "ok"

def handle_win_redraw(window_id, payload):
    wid = _last_child_or_main()
    window.request_redraw(wid)
    return "ok"

def handle_win_close_last(window_id, payload):
    if child_windows:
        wid = child_windows.pop()
        window.close_window(wid)
        return json.dumps({"closed": wid})
    return json.dumps({"error": "没有子窗口可关闭"})


# --- 主题与外观 ---

def handle_theme_light(window_id, payload):
    window.set_window_theme(window_id, "Light")
    return "ok"

def handle_theme_dark(window_id, payload):
    window.set_window_theme(window_id, "Dark")
    return "ok"

def handle_theme_system(window_id, payload):
    window.set_window_theme(window_id, "System")
    return "ok"

def handle_backdrop_mica(window_id, payload):
    window.set_window_backdrop(window_id, "mica")
    return "ok"

def handle_backdrop_micaalt(window_id, payload):
    window.set_window_backdrop(window_id, "micaAlt")
    return "ok"

def handle_backdrop_acrylic(window_id, payload):
    window.set_window_backdrop(window_id, "acrylic")
    return "ok"

def handle_theme_bgcolor(window_id, payload):
    window.set_window_background_color(window_id, payload)
    return "ok"


# --- 边框样式 ---

def handle_frame_style(window_id, payload):
    """切换窗口边框样式"""
    window.set_window_frame_style(window_id, payload)
    return json.dumps({"frame_style": payload})

def handle_titlebar_overlay(window_id, payload):
    """设置 title-overlay 样式参数"""
    try:
        params = json.loads(payload) if payload else {}
    except (json.JSONDecodeError, TypeError):
        params = {}
    height = params.get("height", 32)
    icon_color = params.get("icon_color", None)
    hover_bg = params.get("hover_bg", None)
    ok = window.set_titlebar_overlay_style(window_id, height, icon_color, hover_bg)
    return json.dumps({"success": ok, "height": height, "icon_color": icon_color, "hover_bg": hover_bg})

def handle_print(window_id, payload):
    """打印 WebView 内容"""
    ok = window.jade_print(window_id)
    return json.dumps({"success": ok})

def handle_open_overlay_demo(window_id, payload):
    """打开 title-overlay 演示窗口 (复刻官方 demo)"""
    base_url = tools.set_protocol_service_path(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    )
    wid = window.create_webview_window(
        f"{base_url}overlay_demo.html",
        title="Titlebar Overlay Demo",
        width=860,
        height=600,
        frame_style="title-overlay",
        theme="System",
        background_color="#f3f3f3",
    )
    if wid:
        child_windows.append(wid)
    push_log(window_id, f"打开 Overlay 演示窗口: id={wid}")
    return json.dumps({"window_id": wid})


# --- WebView ---

def handle_webview_navigate(window_id, payload):
    wid = _last_child_or_main()
    webview.navigate_to_url(wid, payload)
    return "ok"

def handle_webview_reload(window_id, payload):
    wid = _last_child_or_main()
    webview.reload(wid)
    return "ok"

def handle_webview_exec_js(window_id, payload):
    wid = _last_child_or_main()
    webview.execute_javascript(wid, "document.title + ' [' + navigator.userAgent.slice(0,30) + '...]'")
    return "ok (结果通过 javascript-result 事件返回)"

def handle_webview_zoom_in(window_id, payload):
    wid = _last_child_or_main()
    webview.set_zoom(wid, 1.5)
    return "ok"

def handle_webview_zoom_reset(window_id, payload):
    wid = _last_child_or_main()
    webview.set_zoom(wid, 1.0)
    return "ok"

def handle_webview_content_protect(window_id, payload):
    global content_protected
    wid = _last_child_or_main()
    content_protected = not content_protected
    webview.set_content_protection(wid, content_protected)
    return json.dumps({"protected": content_protected})


# --- IPC ---

def handle_ipc_send(window_id, payload):
    """前端发消息到 Python, Python 回显"""
    push_log(window_id, f"收到前端消息: {payload}")
    return json.dumps({"echo": payload, "from": "python"})

def handle_ipc_ping(window_id, payload):
    return json.dumps({"pong": True, "window": window_id})

def handle_ipc_get_info(window_id, payload):
    info = {
        "jadeview_version": tools.jadeview_version(),
        "webview_version": tools.get_webview_version(),
        "locale": tools.get_locale(),
        "is_win11": tools.is_windows_11(),
        "window_count": tools.get_window_count(),
    }
    return json.dumps(info, ensure_ascii=False)

def handle_ipc_echo(window_id, payload):
    """IPC 回显 (用于 IPC 测试页)"""
    return json.dumps({"echo": payload})


# --- 对话框 (2.0: 同步返回 JSON 结果) ---

def handle_dialog_open_file(window_id, payload):
    """打开文件对话框"""
    result = dialog.show_open_dialog(
        window_id,
        title="选择文件",
        properties="openFile",
    )
    push_log(window_id, f"打开文件对话框: {result}")
    return json.dumps({"result": result})

def handle_dialog_open_files(window_id, payload):
    """打开多个文件"""
    result = dialog.show_open_dialog(
        window_id,
        title="选择多个文件",
        properties="openFile,multiSelections",
    )
    push_log(window_id, f"多选文件对话框: {result}")
    return json.dumps({"result": result})

def handle_dialog_open_folder(window_id, payload):
    """打开文件夹"""
    result = dialog.show_open_dialog(
        window_id,
        title="选择文件夹",
        properties="openDirectory",
    )
    push_log(window_id, f"选择文件夹对话框: {result}")
    return json.dumps({"result": result})

def handle_dialog_save(window_id, payload):
    """保存文件对话框"""
    result = dialog.show_save_dialog(
        window_id,
        title="保存文件",
        default_path="untitled.txt",
        filters='[{"name":"文本文件","extensions":["txt","md"]},{"name":"所有文件","extensions":["*"]}]',
    )
    push_log(window_id, f"保存文件对话框: {result}")
    return json.dumps({"result": result})

def handle_dialog_msg_info(window_id, payload):
    """信息消息框"""
    result = dialog.show_message_box(
        window_id,
        title="提示",
        message="这是一条信息提示",
        detail="来自 JadeView SDK 的消息框测试",
        buttons="确定|取消",
        type_="info",
    )
    push_log(window_id, f"信息消息框: {result}")
    return json.dumps({"result": result})

def handle_dialog_msg_warning(window_id, payload):
    """警告消息框"""
    result = dialog.show_message_box(
        window_id,
        title="警告",
        message="确定要执行此操作吗?",
        buttons="继续|取消",
        type_="warning",
    )
    push_log(window_id, f"警告消息框: {result}")
    return json.dumps({"result": result})

def handle_dialog_msg_error(window_id, payload):
    """错误消息框"""
    result = dialog.show_message_box(
        window_id,
        title="错误",
        message="发生了一个错误",
        detail="错误代码: 0x80070005",
        buttons="重试|忽略|取消",
        type_="error",
    )
    push_log(window_id, f"错误消息框: {result}")
    return json.dumps({"result": result})

def handle_dialog_error_box(window_id, payload):
    """简单错误框"""
    ret = dialog.show_error_box(window_id, "致命错误", "这是一个 showErrorBox 测试")
    push_log(window_id, f"错误框: 返回={ret}")
    return json.dumps({"ret": ret})


# --- 托盘 ---

def handle_tray_create(window_id, payload):
    global tray_id
    if tray_id:
        return json.dumps({"error": "托盘已存在", "tray_id": tray_id})
    tray_id = tray.tray_create()
    if tray_id:
        tray.tray_set_tooltip(tray_id, "JadeView Demo")
    push_log(window_id, f"创建托盘: {tray_id}")
    return json.dumps({"tray_id": tray_id})

def handle_tray_set_tooltip(window_id, payload):
    if tray_id:
        tray.tray_set_tooltip(tray_id, "JadeView 全功能演示 - 运行中")
        return "ok"
    return json.dumps({"error": "托盘未创建"})

def handle_tray_set_menu(window_id, payload):
    if not tray_id:
        return json.dumps({"error": "托盘未创建"})
    menu_items = [
        {"item_type": 0, "key": "show", "label": "显示主窗口"},
        {"item_type": 0, "key": "hide", "label": "隐藏主窗口"},
        {"item_type": 2, "key": "sep1", "label": ""},  # 分隔线
        {"item_type": 1, "key": "sub_theme", "label": "主题"},  # 子菜单
        {"item_type": 0, "key": "theme_light", "label": "亮色", "parent_key": "sub_theme"},
        {"item_type": 0, "key": "theme_dark", "label": "暗色", "parent_key": "sub_theme"},
        {"item_type": 0, "key": "theme_sys", "label": "跟随系统", "parent_key": "sub_theme"},
        {"item_type": 2, "key": "sep2", "label": ""},  # 分隔线
        {"item_type": 0, "key": "quit", "label": "退出", "dangerous": 1},
    ]
    tray.tray_set_menu_items(tray_id, menu_items)
    return "ok"

def handle_tray_toggle_visible(window_id, payload):
    global tray_visible
    if not tray_id:
        return json.dumps({"error": "托盘未创建"})
    tray_visible = not tray_visible
    tray.tray_set_visible(tray_id, tray_visible)
    return json.dumps({"visible": tray_visible})

def handle_tray_destroy(window_id, payload):
    global tray_id
    if tray_id:
        tray.tray_destroy(tray_id)
        push_log(window_id, "托盘已销毁")
        tray_id = 0
        return "ok"
    return json.dumps({"error": "托盘未创建"})


# --- 通知 ---

def handle_notify_basic(window_id, payload):
    notification.show_notification("JadeView 通知", body="这是一条基本通知测试")
    return "ok"

def handle_notify_with_buttons(window_id, payload):
    notification.show_notification(
        "操作确认",
        body="你有一个待处理的任务",
        button1="查看",
        button2="忽略",
    )
    return "ok"

def handle_notify_with_action(window_id, payload):
    notification.show_notification(
        "新消息",
        body="收到来自 SDK 的消息",
        action="open_main",
        timeout=5000,
    )
    return "ok"


# --- 工具函数 ---

def handle_tools_versions(window_id, payload):
    info = {
        "jadeview": tools.jadeview_version(),
        "webview2": tools.get_webview_version(),
    }
    return json.dumps(info)

def handle_tools_paths(window_id, payload):
    path_names = ["home", "appData", "temp", "desktop", "documents", "downloads"]
    paths = {name: tools.get_path(name) for name in path_names}
    return json.dumps(paths, ensure_ascii=False)

def handle_tools_locale(window_id, payload):
    return json.dumps({"locale": tools.get_locale()})

def handle_tools_displays(window_id, payload):
    info = tools.get_displays_info()
    return json.dumps(info, ensure_ascii=False) if info else "null"

def handle_tools_win_count(window_id, payload):
    return json.dumps({"count": tools.get_window_count()})

def handle_tools_is_win11(window_id, payload):
    return json.dumps({"is_win11": tools.is_windows_11()})

def handle_tools_yaml_set(window_id, payload):
    tools.yaml_set("demo_config.yaml", "ui.theme", "dark")
    tools.yaml_set("demo_config.yaml", "ui.lang", "zh-CN")
    tools.yaml_set("demo_config.yaml", "app.version", "2.1.1")
    push_log(window_id, "YAML 已写入 demo_config.yaml")
    return "ok"

def handle_tools_yaml_get(window_id, payload):
    result = {
        "ui.theme": tools.yaml_get("demo_config.yaml", "ui.theme"),
        "ui.lang": tools.yaml_get("demo_config.yaml", "ui.lang"),
        "app.version": tools.yaml_get("demo_config.yaml", "app.version"),
    }
    return json.dumps(result, ensure_ascii=False)

def handle_tools_hotkey_reg(window_id, payload):
    global hotkey_id
    if hotkey_id:
        return json.dumps({"error": "热键已注册", "id": hotkey_id})
    # Ctrl+Alt+K
    hotkey_id = tools.register_global_hotkey("CTRL+ALT", "K")
    push_log(window_id, f"注册热键 Ctrl+Alt+K: id={hotkey_id}")
    return json.dumps({"hotkey_id": hotkey_id})

def handle_tools_hotkey_unreg(window_id, payload):
    global hotkey_id
    if hotkey_id:
        tools.unregister_global_hotkey(hotkey_id)
        push_log(window_id, f"注销热键: id={hotkey_id}")
        hotkey_id = 0
        return "ok"
    return json.dumps({"error": "没有已注册的热键"})


# --- 性能测试 ---

def handle_bench_open(window_id, payload):
    """打开性能测试窗口"""
    base_url = tools.set_protocol_service_path(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    )
    wid = window.create_webview_window(
        f"{base_url}benchmark.html",
        title="JadeView 2.1.1 性能测试",
        width=900,
        height=700,
        theme="System",
    )
    if wid:
        child_windows.append(wid)
    push_log(window_id, f"打开性能测试窗口: id={wid}")
    return json.dumps({"window_id": wid})


import time
import threading

_pong_event = threading.Event()
_pong_data = None


def _fmt(ms):
    return f"{ms:.2f}"


def _calc_stats(times):
    if not times:
        return {"count": 0, "avg": "0", "min": "0", "max": "0", "total": "0"}
    total = sum(times)
    return {
        "count": len(times),
        "avg": _fmt(total / len(times)),
        "min": _fmt(min(times)),
        "max": _fmt(max(times)),
        "total": _fmt(total),
    }


def _bench_push(win_id, msg):
    ipc.send_ipc_message(win_id, "bench-progress", {"message": msg})


def _bench_result(win_id, key, stats):
    stats["key"] = key
    ipc.send_ipc_message(win_id, "bench-result", stats)


def handle_bench_windows(window_id, payload):
    """批量创建/销毁窗口"""
    count = 20
    _bench_push(window_id, f"窗口测试: 创建 {count} 个窗口...")
    create_times = []
    win_ids = []
    for i in range(count):
        t0 = time.perf_counter()
        wid = window.create_webview_window(
            "about:blank", title=f"Bench #{i+1}", width=400, height=300, hide_window=1,
        )
        elapsed = (time.perf_counter() - t0) * 1000
        create_times.append(elapsed)
        if wid:
            win_ids.append(wid)
        _bench_push(window_id, f"  创建窗口 {i+1}/{count}: {_fmt(elapsed)}ms (id={wid})")

    stats = _calc_stats(create_times)
    _bench_push(window_id, f"创建统计: avg={stats['avg']}ms, min={stats['min']}ms, max={stats['max']}ms")

    _bench_push(window_id, f"窗口测试: 销毁 {len(win_ids)} 个窗口...")
    for wid in win_ids:
        window.close_window(wid)

    _bench_result(window_id, "windows", stats)
    return json.dumps(stats)


def handle_bench_ipc_throughput(window_id, payload):
    """IPC 吞吐测试"""
    count = 1000
    _bench_push(window_id, f"IPC吞吐: Python→JS 发送 {count} 条消息...")
    times = []
    t_start = time.perf_counter()
    for i in range(count):
        t0 = time.perf_counter()
        ipc.send_ipc_message(window_id, "bench-ping", {"seq": i})
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
    total_ms = (time.perf_counter() - t_start) * 1000

    stats = _calc_stats(times)
    throughput = count / (total_ms / 1000) if total_ms > 0 else 0
    _bench_push(window_id, f"IPC吞吐: {count}条/{_fmt(total_ms)}ms, 吞吐={throughput:.0f}条/秒")
    _bench_result(window_id, "ipc", stats)

    # RTT
    global _pong_data
    rtt_count = 100
    _bench_push(window_id, f"IPC RTT: 往返测试 {rtt_count} 次...")
    rtt_times = []
    for i in range(rtt_count):
        _pong_event.clear()
        _pong_data = None
        t0 = time.perf_counter()
        ipc.send_ipc_message(window_id, "bench-ping", {"seq": i, "rtt": True})
        if _pong_event.wait(timeout=2.0):
            rtt_times.append((time.perf_counter() - t0) * 1000)

    if rtt_times:
        rtt_stats = _calc_stats(rtt_times)
        _bench_push(window_id, f"RTT统计: avg={rtt_stats['avg']}ms, min={rtt_stats['min']}ms, max={rtt_stats['max']}ms")
        _bench_result(window_id, "ipc-rtt", rtt_stats)

    return json.dumps(stats)


def handle_bench_pong(window_id, payload):
    """接收前端 pong"""
    global _pong_data
    _pong_data = payload
    _pong_event.set()
    return "ok"


def handle_bench_js_exec(window_id, payload):
    """批量 JS 执行"""
    count = 200
    _bench_push(window_id, f"JS执行: 批量执行 {count} 次...")
    times = []
    for i in range(count):
        t0 = time.perf_counter()
        webview.execute_javascript(window_id, f"1 + {i}")
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)

    stats = _calc_stats(times)
    _bench_push(window_id, f"JS提交统计: avg={stats['avg']}ms, total={stats['total']}ms")
    _bench_result(window_id, "js", stats)
    return json.dumps(stats)


def handle_bench_pipeline(window_id, payload):
    """综合流水线"""
    iterations = 5
    _bench_push(window_id, f"流水线: {iterations} 轮 创建→导航→JS→关闭...")
    base_url = tools.set_protocol_service_path(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    )
    times = []
    for i in range(iterations):
        t0 = time.perf_counter()
        wid = window.create_webview_window(
            "about:blank", title=f"Pipeline #{i+1}", width=400, height=300, hide_window=1,
        )
        if wid:
            webview.navigate_to_url(wid, f"{base_url}ipc_test.html")
            webview.execute_javascript(wid, "'pipeline-test'")
            window.close_window(wid)
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
        _bench_push(window_id, f"  第 {i+1}/{iterations} 轮: {_fmt(elapsed)}ms")

    stats = _calc_stats(times)
    _bench_push(window_id, f"流水线统计: avg={stats['avg']}ms, total={stats['total']}ms")
    _bench_result(window_id, "pipeline", stats)
    return json.dumps(stats)


# ========== 注册一切 ==========

def register_all():
    """注册所有事件监听和 IPC handler"""

    # --- 生命周期事件 ---
    ipc.on(events.APP_READY, on_ready)
    ipc.on(events.WINDOW_CLOSING, on_window_closing)
    ipc.on(events.WINDOW_ALL_CLOSED, on_all_closed)

    # --- 窗口事件 ---
    ipc.on(events.WINDOW_CREATED, on_window_created)
    ipc.on(events.WINDOW_DESTROYED, on_window_destroyed)
    ipc.on(events.WINDOW_RESIZED, on_window_resized)
    ipc.on(events.WINDOW_MOVED, on_window_moved)
    ipc.on(events.WINDOW_FOCUSED, on_window_focused)
    ipc.on(events.WINDOW_BLURRED, on_window_blurred)
    ipc.on(events.WINDOW_STATE_CHANGED, on_window_state_changed)
    ipc.on(events.WINDOW_FULLSCREEN, on_window_fullscreen)

    # --- 主题 ---
    ipc.on(events.THEME_CHANGED, on_theme_changed)

    # --- WebView 事件 ---
    ipc.on(events.WEBVIEW_WILL_NAVIGATE, on_webview_will_navigate)
    ipc.on(events.WEBVIEW_DID_START_LOADING, on_webview_start_loading)
    ipc.on(events.WEBVIEW_DID_FINISH_LOAD, on_webview_finish_load)
    ipc.on(events.WEBVIEW_PAGE_TITLE_UPDATED, on_webview_title_updated)
    ipc.on(events.WEBVIEW_NEW_WINDOW, on_webview_new_window)
    ipc.on(events.JAVASCRIPT_RESULT, on_js_result)
    ipc.on(events.FILE_DROP, on_file_drop)
    ipc.on(events.POSTMESSAGE_RECEIVED, on_postmessage)

    # --- 托盘/通知/热键 ---
    ipc.on(events.TRAY_MENU_COMMAND, on_tray_menu)
    ipc.on(events.TRAY_EVENT, on_tray_event)
    ipc.on(events.NOTIFICATION_SHOWN, on_notification_shown)
    ipc.on(events.NOTIFICATION_DISMISSED, on_notification_dismissed)
    ipc.on(events.NOTIFICATION_ACTION, on_notification_action)
    ipc.on(events.GLOBAL_HOTKEY, on_global_hotkey)

    # --- IPC Handlers (前端 jade.invoke 通道) ---
    handlers = {
        # 窗口管理
        "win:create": handle_win_create,
        "win:create_borderless": handle_win_create_borderless,
        "win:set_title": handle_win_set_title,
        "win:set_size": handle_win_set_size,
        "win:set_position": handle_win_set_position,
        "win:minimize": handle_win_minimize,
        "win:toggle_maximize": handle_win_toggle_maximize,
        "win:fullscreen": handle_win_fullscreen,
        "win:always_on_top": handle_win_always_on_top,
        "win:set_enabled": handle_win_set_enabled,
        "win:hide_show": handle_win_hide_show,
        "win:focus": handle_win_focus,
        "win:redraw": handle_win_redraw,
        "win:close_last": handle_win_close_last,
        # 主题
        "theme:light": handle_theme_light,
        "theme:dark": handle_theme_dark,
        "theme:system": handle_theme_system,
        "backdrop:mica": handle_backdrop_mica,
        "backdrop:micaAlt": handle_backdrop_micaalt,
        "backdrop:acrylic": handle_backdrop_acrylic,
        "theme:bgcolor": handle_theme_bgcolor,
        # 边框样式
        "frame:set_style": handle_frame_style,
        "frame:titlebar_overlay": handle_titlebar_overlay,
        "frame:print": handle_print,
        "frame:open_overlay_demo": handle_open_overlay_demo,
        "setTitlebarOverlayStyle": handle_titlebar_overlay,
        # WebView
        "webview:navigate": handle_webview_navigate,
        "webview:reload": handle_webview_reload,
        "webview:exec_js": handle_webview_exec_js,
        "webview:zoom_in": handle_webview_zoom_in,
        "webview:zoom_reset": handle_webview_zoom_reset,
        "webview:content_protect": handle_webview_content_protect,
        # IPC
        "ipc:send": handle_ipc_send,
        "ipc:ping": handle_ipc_ping,
        "ipc:get_info": handle_ipc_get_info,
        "ipc:echo": handle_ipc_echo,
        # 对话框
        "dialog:open_file": handle_dialog_open_file,
        "dialog:open_files": handle_dialog_open_files,
        "dialog:open_folder": handle_dialog_open_folder,
        "dialog:save": handle_dialog_save,
        "dialog:msg_info": handle_dialog_msg_info,
        "dialog:msg_warning": handle_dialog_msg_warning,
        "dialog:msg_error": handle_dialog_msg_error,
        "dialog:error_box": handle_dialog_error_box,
        # 托盘
        "tray:create": handle_tray_create,
        "tray:set_tooltip": handle_tray_set_tooltip,
        "tray:set_menu": handle_tray_set_menu,
        "tray:toggle_visible": handle_tray_toggle_visible,
        "tray:destroy": handle_tray_destroy,
        # 通知
        "notify:basic": handle_notify_basic,
        "notify:with_buttons": handle_notify_with_buttons,
        "notify:with_action": handle_notify_with_action,
        # 工具
        "tools:versions": handle_tools_versions,
        "tools:paths": handle_tools_paths,
        "tools:locale": handle_tools_locale,
        "tools:displays": handle_tools_displays,
        "tools:win_count": handle_tools_win_count,
        "tools:is_win11": handle_tools_is_win11,
        "tools:yaml_set": handle_tools_yaml_set,
        "tools:yaml_get": handle_tools_yaml_get,
        "tools:hotkey_reg": handle_tools_hotkey_reg,
        "tools:hotkey_unreg": handle_tools_hotkey_unreg,
        # 性能测试
        "bench:open_window": handle_bench_open,
        "bench:windows": handle_bench_windows,
        "bench:ipc_throughput": handle_bench_ipc_throughput,
        "bench:js_exec": handle_bench_js_exec,
        "bench:pipeline": handle_bench_pipeline,
        "bench:pong": handle_bench_pong,
    }

    for channel, handler in handlers.items():
        ipc.register_ipc_handler(channel, handler)


def main():
    print("=" * 50)
    print("  JadeView 2.1.1 SDK 全功能演示")
    print("=" * 50)

    register_all()

    ok = jadeview.init(
        "JadeViewFullDemo",
        "jvfulldemo",
        enable_devmod=True,
    )
    if not ok:
        print("[错误] 初始化失败!")
        return

    jadeview.run()
    print("[完成] 应用已退出")


if __name__ == "__main__":
    main()

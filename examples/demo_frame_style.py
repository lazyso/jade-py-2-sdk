"""JadeView 2.1.1 SDK 边框样式演示

演示 frame_style 四种模式切换 + title-overlay 自定义样式。
使用 SDK 封装 (非直接 ctypes 调用)。

用法:
    cd examples
    python demo_frame_style.py
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import jadeview
from jadeview import events, ipc, window, tools

# --- 全局状态 ---
main_win_id = 0


# ========== IPC Handlers ==========

def handle_set_frame_style(window_id, payload):
    """切换边框样式: normal / no-titlebar / borderless / title-overlay"""
    style = payload.strip().strip('"')
    ok = window.set_window_frame_style(window_id, style)
    print(f"[frame] set_window_frame_style({window_id}, {style}) -> {ok}")
    return json.dumps({"success": ok, "style": style})


def handle_set_overlay_style(window_id, payload):
    """自定义 title-overlay 按钮外观"""
    try:
        params = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        params = {}
    height = params.get("height", 32)
    icon_color = params.get("icon_color", None)
    hover_bg = params.get("hover_bg", None)
    ok = window.set_titlebar_overlay_style(window_id, height, icon_color, hover_bg)
    print(f"[overlay] set_titlebar_overlay_style({window_id}, h={height}, icon={icon_color}, hover={hover_bg}) -> {ok}")
    return json.dumps({"success": ok})


def handle_print_page(window_id, payload):
    """打印当前页面"""
    ok = window.jade_print(window_id)
    return json.dumps({"success": ok})


def handle_close(window_id, payload):
    """关闭窗口"""
    window.close_window(window_id)
    return json.dumps({"success": True})


# ========== 生命周期 ==========

def on_ready(window_id, data):
    global main_win_id

    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    base_url = tools.set_protocol_service_path(web_dir)
    print(f"[启动] 协议服务: {base_url}")

    # 创建窗口, 初始使用 title-overlay 样式
    main_win_id = window.create_webview_window(
        f"{base_url}frame_style.html",
        title="边框样式演示",
        width=900,
        height=650,
        frame_style="title-overlay",
        theme="System",
        background_color="#f3f3f3",
    )
    # 设置 overlay 按钮高度, 使命中区域与标题栏一致 (40px)
    window.set_titlebar_overlay_style(main_win_id, height=40)
    print(f"[启动] 窗口 ID: {main_win_id}, frame_style=title-overlay")


def on_all_closed(window_id, data):
    print("[退出] 所有窗口已关闭")
    jadeview.cleanup()


# ========== 入口 ==========

def main():
    print("=" * 50)
    print("  JadeView 2.1.1 边框样式演示")
    print("=" * 50)

    # 事件
    ipc.on(events.APP_READY, on_ready)
    ipc.on(events.WINDOW_ALL_CLOSED, on_all_closed)

    # IPC handlers
    ipc.register_ipc_handler("setFrameStyle", handle_set_frame_style)
    ipc.register_ipc_handler("setOverlayStyle", handle_set_overlay_style)
    ipc.register_ipc_handler("printPage", handle_print_page)
    ipc.register_ipc_handler("closeWindow", handle_close)

    ok = jadeview.init(
        "FrameStyleDemo",
        "cn.jade.frame_style_demo",
        enable_devmod=True,
    )
    if not ok:
        print("[错误] 初始化失败!")
        return

    print(f"[信息] JadeView {tools.jadeview_version()}")
    jadeview.run()
    print("[完成] 已退出")


if __name__ == "__main__":
    main()

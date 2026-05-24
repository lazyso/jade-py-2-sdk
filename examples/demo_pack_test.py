"""JadeView 2.1.1 打包手测演示

默认加载 examples/web_pack_test 目录。
运行后可在页面里手动选择 .japk 文件切换载入，也可一键切回目录版。

用法:
    python examples/demo_pack_test.py
    python examples/demo_pack_test.py examples\\web_pack_test
    python examples/demo_pack_test.py D:\\path\\to\\app.japk
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import jadeview
from jadeview import dialog, events, ipc, tools, webview, window


main_win_id = 0
target_path = ""
default_target_path = ""


def resolve_target() -> str:
    if len(sys.argv) > 1:
        return os.path.abspath(sys.argv[1])
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_pack_test")


def build_source_info() -> dict:
    return {
        "target_path": target_path,
        "is_file": os.path.isfile(target_path),
        "is_dir": os.path.isdir(target_path),
        "window_count": tools.get_window_count(),
    }


def load_target_into_window(window_id: int) -> dict:
    base_url = tools.set_protocol_service_path(target_path)
    if not base_url:
        return {
            "ok": False,
            "message": "set_protocol_service_path failed",
            **build_source_info(),
        }

    page_url = f"{base_url}index.html"
    if window_id and window_id == main_win_id:
        ok = webview.navigate_to_url(window_id, page_url)
        if ok:
            webview.reload(window_id)
    else:
        ok = True

    return {
        "ok": ok,
        "message": "loaded" if ok else "navigate_to_url failed",
        "base_url": base_url,
        "page_url": page_url,
        **build_source_info(),
    }


def on_ready(window_id, data):
    global main_win_id

    initial = load_target_into_window(0)
    print(f"[启动] JadeView: {tools.jadeview_version()}")
    print(f"[启动] WebView2: {tools.get_webview_version()}")
    print(f"[启动] 资源路径: {target_path}")
    print(f"[启动] 协议地址: {initial.get('base_url')}")

    if not initial["ok"]:
        print(f"[错误] {initial['message']}")
        jadeview.cleanup()
        return None

    main_win_id = window.create_webview_window(
        initial["page_url"],
        title="JadeView 打包手测",
        width=1040,
        height=760,
        theme="System",
        min_width=860,
        min_height=620,
    )
    print(f"[启动] 主窗口 ID: {main_win_id}")
    return None


def on_all_closed(window_id, data):
    print("[退出] 所有窗口已关闭")
    jadeview.cleanup()
    return None


def handle_ping(window_id, payload):
    return {
        "ok": True,
        "message": "pong from python",
        "payload": payload,
        "jadeview_version": tools.jadeview_version(),
    }


def handle_pack_info(window_id, payload):
    return build_source_info()


def handle_choose_japk(window_id, payload):
    global target_path

    result = dialog.show_open_dialog(
        window_id,
        title="选择 JAPK 文件",
        default_path=os.path.dirname(default_target_path),
        filters='[{"name":"JAPK 文件","extensions":["japk"]}]',
        properties="openFile",
    )
    if not result or result.get("canceled"):
        return {
            "ok": False,
            "message": "user canceled",
            "dialog_result": result,
            **build_source_info(),
        }

    selected = result.get("file_path") or result.get("filePath")
    if not selected:
        selected = (result.get("file_paths") or result.get("filePaths") or [None])[0]
    if not selected:
        return {
            "ok": False,
            "message": "no file selected",
            "dialog_result": result,
            **build_source_info(),
        }

    target_path = selected
    loaded = load_target_into_window(window_id)
    loaded["dialog_result"] = result
    return loaded


def handle_reset_source(window_id, payload):
    global target_path
    target_path = default_target_path
    return load_target_into_window(window_id)


def main() -> int:
    global default_target_path, target_path
    default_target_path = resolve_target()
    target_path = default_target_path

    if not os.path.exists(target_path):
        print(f"[错误] 目标不存在: {target_path}")
        return 1

    ipc.on(events.APP_READY, on_ready)
    ipc.on(events.WINDOW_ALL_CLOSED, on_all_closed)
    ipc.register_ipc_handler("pack:ping", handle_ping)
    ipc.register_ipc_handler("pack:info", handle_pack_info)
    ipc.register_ipc_handler("pack:choose-japk", handle_choose_japk)
    ipc.register_ipc_handler("pack:reset-source", handle_reset_source)

    if not jadeview.init("PackTest", "packt1", enable_devmod=True):
        print("[错误] JadeView_init 失败")
        return 1

    return 0 if jadeview.run() else 1


if __name__ == "__main__":
    raise SystemExit(main())

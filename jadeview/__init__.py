"""JadeView 2.0 Python SDK

基于 WebView2 的 Windows 桌面应用框架 Python 绑定。

基本用法:
    import jadeview

    # 注册 app-ready 回调 (必须在 init 之前)
    def on_ready(window_id, data):
        jadeview.window.create_webview_window("https://example.com", title="Hello")

    jadeview.ipc.on("app-ready", on_ready)

    # 初始化并启动消息循环
    jadeview.init("MyApp", "myapp1")
    jadeview.run()
"""

from .core import get_dll

# 子模块
from . import dialog
from . import events
from . import ipc
from . import japk
from . import notification
from . import tray
from . import tools
from . import webview
from . import window


def _encode(s: str | None) -> bytes | None:
    return s.encode("utf-8") if s else None


def init(
    app_name: str,
    app_signature: str,
    *,
    enable_devmod: bool = False,
    log_path: str | None = None,
    data_directory: str | None = None,
    single_instance: bool = False,
) -> bool:
    """初始化 JadeView 应用

    注意: 必须先通过 jadeview.ipc.on("app-ready", callback) 注册就绪回调，再调用此函数。

    参数:
        app_name: 应用显示名称
        app_signature: 应用唯一标识 (>=6 字符)
        enable_devmod: 是否启用开发者工具/调试快捷键
        log_path: 日志文件路径, None 不写文件
        data_directory: 数据根目录, None 使用系统默认
        single_instance: 是否单实例模式

    返回:
        是否成功启动 (True 表示已启动, 等待 app-ready 事件)
    """
    return get_dll().JadeView_init(
        1 if enable_devmod else 0,
        _encode(log_path),
        _encode(data_directory),
        _encode(app_name),
        _encode(app_signature),
        1 if single_instance else 0,
    ) == 1


def run() -> bool:
    """启动消息循环 (阻塞当前线程)

    通常在 init() 之后调用，程序会阻塞在此处直到所有窗口关闭。

    返回:
        是否正常退出
    """
    return get_dll().run_message_loop() == 1


def cleanup() -> bool:
    """清理所有窗口并准备退出"""
    return get_dll().cleanup_all_windows() == 1

"""JadeView 2.0 WebView 模块 - 导航、JS 执行、缩放等"""

from .core import get_dll


def _encode(s: str | None) -> bytes | None:
    return s.encode("utf-8") if s else None


def navigate_to_url(window_id: int, url: str) -> bool:
    """导航到指定 URL

    参数:
        window_id: 窗口 ID
        url: 目标网址
    """
    return get_dll().navigate_to_url(window_id, _encode(url)) == 1


def reload(window_id: int) -> bool:
    """重新加载当前页面"""
    return get_dll().reload_webview_window(window_id) == 1


def execute_javascript(window_id: int, script: str) -> bool:
    """在 WebView 中执行 JavaScript 代码

    参数:
        window_id: 窗口 ID
        script: JS 代码字符串

    返回:
        是否成功发起执行 (结果通过 javascript-result 事件异步返回)
    """
    return get_dll().execute_javascript(window_id, _encode(script)) == 1


def set_zoom(window_id: int, level: float = 1.0) -> bool:
    """设置 WebView 缩放级别

    参数:
        window_id: 窗口 ID
        level: 缩放比例, 1.0=100%, 1.5=150%
    """
    return get_dll().set_webview_zoom(window_id, level) == 1


def set_content_protection(window_id: int, enabled: bool = True) -> bool:
    """启用/禁用内容保护 (防截屏)"""
    return get_dll().set_content_protection(window_id, 1 if enabled else 0) == 1

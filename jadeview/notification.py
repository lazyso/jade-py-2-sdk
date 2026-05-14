"""JadeView 2.0 通知模块"""

import ctypes

from .core import get_dll
from .types import NotificationParams


def _encode(s: str | None) -> bytes | None:
    return s.encode("utf-8") if s else None


def show_notification(
    summary: str,
    *,
    body: str | None = None,
    icon: str | None = None,
    timeout: int = 0,
    button1: str | None = None,
    button2: str | None = None,
    text3: str | None = None,
    action: str | None = None,
) -> bool:
    """显示系统通知

    参数:
        summary: 通知标题 (必填)
        body: 通知正文
        icon: 图标文件绝对路径
        timeout: 超时毫秒数, <=0 使用系统默认 (~10秒)
        button1: 第一个按钮文字
        button2: 第二个按钮文字
        text3: 附加文本行
        action: 动作参数 (通过 notification-action 事件回传)

    返回:
        是否成功入队
    """
    params = NotificationParams()
    params.summary = _encode(summary)
    params.body = _encode(body)
    params.icon = _encode(icon)
    params.timeout = timeout
    params.button1 = _encode(button1)
    params.button2 = _encode(button2)
    params.text3 = _encode(text3)
    params.action = _encode(action)

    return get_dll().show_notification(ctypes.byref(params)) == 1

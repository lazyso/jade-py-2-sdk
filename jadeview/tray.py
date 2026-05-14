"""JadeView 2.0 系统托盘模块"""

import ctypes

from .core import get_dll
from .types import TrayMenuItemDesc


def _encode(s: str | None) -> bytes | None:
    return s.encode("utf-8") if s else None


def tray_create() -> int:
    """创建系统托盘图标

    返回:
        tray_id (>0 成功)
    """
    return get_dll().tray_create()


def tray_destroy(tray_id: int) -> bool:
    """销毁托盘图标"""
    return get_dll().tray_destroy(tray_id) == 1


def tray_set_visible(tray_id: int, visible: bool = True) -> bool:
    """显示/隐藏托盘图标"""
    return get_dll().tray_set_visible(tray_id, 1 if visible else 0) == 1


def tray_set_tooltip(tray_id: int, tooltip: str) -> bool:
    """设置托盘图标悬停提示文字"""
    return get_dll().tray_set_tooltip(tray_id, _encode(tooltip)) == 1


def tray_set_icon_from_file(tray_id: int, icon_path: str) -> bool:
    """设置托盘图标 (从文件)

    参数:
        icon_path: 图标文件的绝对路径 (.ico)
    """
    return get_dll().tray_set_icon_from_file(tray_id, _encode(icon_path)) == 1


def tray_set_menu_items(tray_id: int, items: list[dict]) -> bool:
    """设置托盘右键菜单

    参数:
        tray_id: 托盘 ID
        items: 菜单项列表, 每项为 dict:
            - item_type: 0=普通 1=子菜单 2=分隔线 3=分组
            - key: 唯一标识 (必填)
            - label: 显示文字
            - parent_key: 父项 key, None 表示根级
            - disabled: 是否禁用 (默认 0)
            - dangerous: 是否标记危险 (默认 0)

    示例:
        tray_set_menu_items(tray_id, [
            {"item_type": 0, "key": "open", "label": "打开"},
            {"item_type": 2, "key": "sep1", "label": ""},
            {"item_type": 0, "key": "exit", "label": "退出", "dangerous": 1},
        ])
    """
    if not items:
        # 空列表 = 清除菜单
        return get_dll().tray_set_menu_items(tray_id, None, 0) == 1

    count = len(items)
    ItemArray = TrayMenuItemDesc * count
    arr = ItemArray()
    for i, item in enumerate(items):
        arr[i].item_type = item.get("item_type", 0)
        arr[i].key = _encode(item.get("key", ""))
        arr[i].label = _encode(item.get("label", ""))
        arr[i].parent_key = _encode(item.get("parent_key"))
        arr[i].disabled = item.get("disabled", 0)
        arr[i].dangerous = item.get("dangerous", 0)

    return get_dll().tray_set_menu_items(tray_id, arr, count) == 1

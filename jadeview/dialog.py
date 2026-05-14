"""JadeView 2.0 对话框模块

提供打开文件、保存文件、消息框、错误框等系统对话框。

2.0 变更:
- 同步接口直接返回 JSON 字符串 (char*), 使用后必须 jade_text_free() 释放
- 新增 *_async 异步接口
- 删除 blocking/callback 参数
- OpenDialogParams/SaveDialogParams 合并为 FileDialogParams
"""

import ctypes
import json
from typing import Optional, Callable

from .core import get_dll
from .types import FileDialogParams, MessageBoxParams, DialogAsyncCallback


def _encode(s: str | None) -> bytes | None:
    return s.encode("utf-8") if s else None


def _call_sync_and_parse(raw_ptr) -> dict | None:
    """读取 DLL 返回的 char* JSON, 解析后释放内存

    所有同步对话框接口共用此逻辑, 保证 jade_text_free 一定被调用。
    """
    if not raw_ptr:
        return None
    try:
        json_bytes = ctypes.string_at(raw_ptr)
        return json.loads(json_bytes.decode("utf-8"))
    finally:
        get_dll().jade_text_free(raw_ptr)


# ============================================================
# 同步 API
# ============================================================

def show_open_dialog(
    window_id: int = 0,
    *,
    title: str | None = None,
    default_path: str | None = None,
    button_label: str | None = None,
    filters: str | None = None,
    properties: str = "openFile",
) -> dict | None:
    """弹出打开文件对话框 (同步阻塞)

    参数:
        window_id: 父窗口 ID, 0 表示无父窗口
        title: 对话框标题
        default_path: 默认路径
        button_label: 确认按钮文字
        filters: 文件过滤器 JSON
        properties: 属性, 逗号分隔: openFile,openDirectory,multiSelections,showHiddenFiles

    返回:
        {"canceled": bool, "file_paths": [...]} 或 None
    """
    params = FileDialogParams()
    params.window_id = window_id
    params.title = _encode(title)
    params.default_path = _encode(default_path)
    params.button_label = _encode(button_label)
    params.filters = _encode(filters)
    params.properties = _encode(properties)

    raw_ptr = get_dll().jade_dialog_show_open_dialog(ctypes.byref(params))
    return _call_sync_and_parse(raw_ptr)


def show_save_dialog(
    window_id: int = 0,
    *,
    title: str | None = None,
    default_path: str | None = None,
    button_label: str | None = None,
    filters: str | None = None,
) -> dict | None:
    """弹出保存文件对话框 (同步阻塞)

    参数:
        window_id: 父窗口 ID
        title: 对话框标题
        default_path: 默认路径/文件名
        button_label: 确认按钮文字
        filters: 文件过滤器 JSON

    返回:
        {"canceled": bool, "file_path": "..." | null} 或 None
    """
    params = FileDialogParams()
    params.window_id = window_id
    params.title = _encode(title)
    params.default_path = _encode(default_path)
    params.button_label = _encode(button_label)
    params.filters = _encode(filters)
    params.properties = None

    raw_ptr = get_dll().jade_dialog_show_save_dialog(ctypes.byref(params))
    return _call_sync_and_parse(raw_ptr)


def show_message_box(
    window_id: int = 0,
    *,
    title: str | None = None,
    message: str | None = None,
    detail: str | None = None,
    buttons: str | None = None,
    default_id: int = 0,
    cancel_id: int = -1,
    type_: str = "info",
) -> dict | None:
    """弹出消息框 (同步阻塞)

    参数:
        window_id: 父窗口 ID
        title: 标题
        message: 消息内容
        detail: 详细信息
        buttons: 按钮列表, "|" 分隔, 如 "确定|取消"
        default_id: 默认按钮索引
        cancel_id: 取消按钮索引, -1 无取消
        type_: 类型: none/info/warning/error/question

    返回:
        {"response": int} 或 None
    """
    params = MessageBoxParams()
    params.window_id = window_id
    params.title = _encode(title)
    params.message = _encode(message)
    params.detail = _encode(detail)
    params.buttons = _encode(buttons)
    params.default_id = default_id
    params.cancel_id = cancel_id
    params.type_ = _encode(type_)

    raw_ptr = get_dll().jade_dialog_show_message_box(ctypes.byref(params))
    return _call_sync_and_parse(raw_ptr)


def show_error_box(
    window_id: int = 0,
    title: str = "错误",
    content: str = "",
) -> int:
    """弹出错误框 (简单模式, 无 JSON 返回)

    参数:
        window_id: 父窗口 ID
        title: 标题
        content: 错误内容

    返回:
        1=成功, 0=失败
    """
    return get_dll().jade_dialog_show_error_box(
        window_id,
        _encode(title),
        _encode(content),
    )


# ============================================================
# 异步 API
# ============================================================

# 保持回调引用防止被 GC 回收
_async_callbacks = []


def _wrap_async_callback(user_callback: Callable[[dict | None], None]) -> DialogAsyncCallback:
    """将 Python 回调包装为 C 回调, 自动解析 JSON"""
    def _c_callback(json_result_ptr):
        try:
            if json_result_ptr:
                result = json.loads(json_result_ptr.decode("utf-8"))
            else:
                result = None
            user_callback(result)
        finally:
            # 异步回调的指针由库侧管理, 回调返回后失效, 不需要 jade_text_free
            pass

    cb = DialogAsyncCallback(_c_callback)
    _async_callbacks.append(cb)  # prevent GC
    return cb


def show_open_dialog_async(
    callback: Callable[[dict | None], None],
    window_id: int = 0,
    *,
    title: str | None = None,
    default_path: str | None = None,
    button_label: str | None = None,
    filters: str | None = None,
    properties: str = "openFile",
) -> bool:
    """弹出打开文件对话框 (异步)

    返回:
        True=成功发起, False=失败
    """
    params = FileDialogParams()
    params.window_id = window_id
    params.title = _encode(title)
    params.default_path = _encode(default_path)
    params.button_label = _encode(button_label)
    params.filters = _encode(filters)
    params.properties = _encode(properties)

    cb = _wrap_async_callback(callback)
    return get_dll().jade_dialog_show_open_dialog_async(ctypes.byref(params), cb) == 1


def show_save_dialog_async(
    callback: Callable[[dict | None], None],
    window_id: int = 0,
    *,
    title: str | None = None,
    default_path: str | None = None,
    button_label: str | None = None,
    filters: str | None = None,
) -> bool:
    """弹出保存文件对话框 (异步)

    返回:
        True=成功发起, False=失败
    """
    params = FileDialogParams()
    params.window_id = window_id
    params.title = _encode(title)
    params.default_path = _encode(default_path)
    params.button_label = _encode(button_label)
    params.filters = _encode(filters)
    params.properties = None

    cb = _wrap_async_callback(callback)
    return get_dll().jade_dialog_show_save_dialog_async(ctypes.byref(params), cb) == 1


def show_message_box_async(
    callback: Callable[[dict | None], None],
    window_id: int = 0,
    *,
    title: str | None = None,
    message: str | None = None,
    detail: str | None = None,
    buttons: str | None = None,
    default_id: int = 0,
    cancel_id: int = -1,
    type_: str = "info",
) -> bool:
    """弹出消息框 (异步)

    返回:
        True=成功发起, False=失败
    """
    params = MessageBoxParams()
    params.window_id = window_id
    params.title = _encode(title)
    params.message = _encode(message)
    params.detail = _encode(detail)
    params.buttons = _encode(buttons)
    params.default_id = default_id
    params.cancel_id = cancel_id
    params.type_ = _encode(type_)

    cb = _wrap_async_callback(callback)
    return get_dll().jade_dialog_show_message_box_async(ctypes.byref(params), cb) == 1

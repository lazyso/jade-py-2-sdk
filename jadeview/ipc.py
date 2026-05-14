"""JadeView 2.0 IPC 通信模块 - 事件订阅、IPC 处理、消息发送"""

import ctypes
import json
import traceback
from typing import Callable

from .core import get_dll
from .types import IpcCallbackType

# 全局回调引用表，防止 Python 回调被 GC 回收
_callback_refs: dict[int, IpcCallbackType] = {}
_handler_refs: dict[str, IpcCallbackType] = {}
# 保持 on() 回调返回的字符串缓冲区引用, 防止 GC (DLL 读取期间需要有效)
_last_return_buf: ctypes.Array | None = None


def _encode(s: str | None) -> bytes | None:
    """字符串转 UTF-8 bytes"""
    return s.encode("utf-8") if s else None


def on(event_name: str, callback: Callable[[int, str], str | None]) -> int:
    """订阅事件

    参数:
        event_name: 事件名称 (见 events.py 中的常量)
        callback: 回调函数 (window_id: int, event_data: str) -> str | None
                  - 返回 None 表示放行/无特殊处理
                  - 对 window-closing 等可拦截事件，返回非 None 字符串表示拦截

    返回:
        callback_id: 回调 ID (>0 成功, 0 失败)，用于 off() 取消订阅
    """
    def _wrapper(window_id, event_data):
        global _last_return_buf
        try:
            data_str = event_data.decode("utf-8") if event_data else ""
            result = callback(window_id, data_str)
            if result is None:
                return None
            # 返回 (const char*)1 表示拦截
            if result is True:
                return 1
            if isinstance(result, str):
                # c_void_p 返回类型不接受 bytes, 需转为原始指针
                _last_return_buf = ctypes.create_string_buffer(result.encode("utf-8"))
                return ctypes.addressof(_last_return_buf)
            return None
        except Exception:
            traceback.print_exc()
            return None

    c_callback = IpcCallbackType(_wrapper)
    callback_id = get_dll().jade_on(_encode(event_name), c_callback)
    if callback_id > 0:
        _callback_refs[callback_id] = c_callback
    return callback_id


def off(event_name: str, callback_id: int) -> bool:
    """取消事件订阅

    参数:
        event_name: 事件名称
        callback_id: on() 返回的回调 ID

    返回:
        是否成功
    """
    result = get_dll().jade_off(_encode(event_name), callback_id)
    _callback_refs.pop(callback_id, None)
    return result == 1


def register_ipc_handler(channel: str, handler: Callable[[int, str], str | dict | None]) -> bool:
    """注册 IPC 通道处理器 (接收前端 jade.invoke() 调用)

    参数:
        channel: 通道名称
        handler: 处理函数 (window_id: int, payload: str) -> str | dict | None
                 - 返回 None: 默认成功响应
                 - 返回 dict: 自动序列化为 JSON 返回给前端
                 - 返回 str: 直接作为 JSON 返回给前端

    返回:
        是否成功
    """
    def _wrapper(window_id, event_data):
        try:
            data_str = event_data.decode("utf-8") if event_data else ""
            result = handler(window_id, data_str)
            if result is None:
                return None
            if isinstance(result, dict):
                result = json.dumps(result, ensure_ascii=False)
            if isinstance(result, str):
                # jade_text_create 返回 c_void_p (原始指针), DLL 会 jade_text_free
                return get_dll().jade_text_create(result.encode("utf-8"))
            return None
        except Exception:
            traceback.print_exc()
            return None

    c_callback = IpcCallbackType(_wrapper)
    _handler_refs[channel] = c_callback
    return get_dll().register_ipc_handler(_encode(channel), c_callback) == 1


def send_ipc_message(window_id: int, message_type: str, content: str | dict) -> bool:
    """向指定窗口的前端发送 IPC 消息

    参数:
        window_id: 目标窗口 ID
        message_type: 消息类型 (前端通过 jade.on(message_type, ...) 接收)
        content: 消息内容 (str 或 dict，dict 会自动转 JSON)

    返回:
        是否成功
    """
    if isinstance(content, dict):
        content = json.dumps(content, ensure_ascii=False)
    return get_dll().send_ipc_message(
        window_id,
        _encode(message_type),
        _encode(content),
    ) == 1

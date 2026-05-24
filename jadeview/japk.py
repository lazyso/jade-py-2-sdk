"""JadeView 2.1 JAPK 内存载入模块"""

import ctypes
import json

from .core import get_dll


def _encode(s: str | None) -> bytes | None:
    return s.encode("utf-8") if s else None


def _read_owned_text(raw_ptr) -> str | None:
    """读取 DLL 返回的 char* 并释放内存"""
    if not raw_ptr:
        return None
    try:
        return ctypes.string_at(raw_ptr).decode("utf-8")
    finally:
        get_dll().jade_text_free(raw_ptr)


def set_public_key(public_key: str) -> int:
    """设置 Ed25519 公钥(Base64)"""
    return get_dll().JadeView_set_public_key(_encode(public_key))


def load_from_bytes(data: bytes | bytearray | memoryview) -> int:
    """从内存加载 JAPK 包"""
    view = memoryview(data)
    if view.nbytes == 0:
        return get_dll().JadeView_load_from_bytes(None, 0)

    buf = ctypes.create_string_buffer(view.tobytes())
    ptr = ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint8))
    return get_dll().JadeView_load_from_bytes(ptr, view.nbytes)


def is_loaded() -> bool:
    """JAPK 是否已加载"""
    return get_dll().JadeView_is_loaded() == 1


def get_app_signature() -> str | None:
    """获取当前加载包的 app_signature"""
    return _read_owned_text(get_dll().JadeView_get_app_signature())


def get_signature_info() -> dict | str | None:
    """获取签名信息 JSON，解析失败时返回原始字符串"""
    text = _read_owned_text(get_dll().JadeView_get_signature_info())
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def unload() -> int:
    """清除加载状态并释放内存"""
    return get_dll().JadeView_unload()

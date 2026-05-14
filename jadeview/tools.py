"""JadeView 2.0 工具函数模块 - 版本、路径、热键、YAML 配置等"""

import ctypes
import json

from .core import get_dll


def _encode(s: str | None) -> bytes | None:
    return s.encode("utf-8") if s else None


def _read_buffer(func, *args, buf_size: int = 4096) -> str | None:
    """通用缓冲区读取辅助"""
    buf = ctypes.create_string_buffer(buf_size)
    if func(*args, buf, buf_size) == 1:
        return buf.value.decode("utf-8")
    return None


def _normalize_hotkey_modifiers(modifiers: int | str | list[int | str] | tuple[int | str, ...] | set[int | str]) -> int:
    """将热键修饰键参数转换为 Win32 modifiers 位掩码"""
    if isinstance(modifiers, int):
        return modifiers

    modifier_map = {
        "ALT": MOD_ALT,
        "CONTROL": MOD_CONTROL,
        "CTRL": MOD_CONTROL,
        "SHIFT": MOD_SHIFT,
        "WIN": MOD_WIN,
        "WINDOWS": MOD_WIN,
        "CMD": MOD_WIN,
        "SUPER": MOD_WIN,
    }

    if isinstance(modifiers, str):
        parts = [part.strip() for part in modifiers.replace("+", "|").split("|") if part.strip()]
    else:
        parts = list(modifiers)

    result = 0
    for part in parts:
        if isinstance(part, int):
            result |= part
            continue
        key = str(part).strip().upper()
        if key not in modifier_map:
            raise ValueError(f"不支持的修饰键: {part}")
        result |= modifier_map[key]
    return result


def _normalize_hotkey_vk(vk: int | str) -> int:
    """将热键主键参数转换为 Win32 虚拟键码"""
    if isinstance(vk, int):
        return vk

    key = vk.strip().upper()
    if len(key) == 1:
        return ord(key)

    function_keys = {f"F{i}": 0x6F + i for i in range(1, 25)}
    special_keys = {
        "ENTER": 0x0D,
        "RETURN": 0x0D,
        "ESC": 0x1B,
        "ESCAPE": 0x1B,
        "SPACE": 0x20,
        "TAB": 0x09,
        "BACKSPACE": 0x08,
        "DELETE": 0x2E,
        "INSERT": 0x2D,
        "HOME": 0x24,
        "END": 0x23,
        "PAGEUP": 0x21,
        "PAGEDOWN": 0x22,
        "LEFT": 0x25,
        "UP": 0x26,
        "RIGHT": 0x27,
        "DOWN": 0x28,
    }

    if key in function_keys:
        return function_keys[key]
    if key in special_keys:
        return special_keys[key]

    raise ValueError(f"不支持的热键主键: {vk}")


# ============================================================
# 版本信息
# ============================================================

def jadeview_version() -> str | None:
    """获取 JadeView 库版本号, 如 "2.0.0.1234" """
    return _read_buffer(get_dll().jadeview_version, buf_size=256)


def get_webview_version() -> str | None:
    """获取 WebView2 运行时版本号, 如 "130.0.2849.52" """
    return _read_buffer(get_dll().get_webview_version, buf_size=256)


def is_windows_11() -> bool:
    """检测当前系统是否为 Windows 11"""
    return get_dll().is_windows_11() == 1


def get_window_count() -> int:
    """获取当前打开的窗口数量"""
    return get_dll().get_window_count()


# ============================================================
# 路径
# ============================================================

def get_path(name: str) -> str | None:
    """获取系统特殊路径

    参数:
        name: 路径名称, 可选:
            home, appData, sessionData, temp, exe, desktop,
            documents, downloads, music, pictures, videos, logs, app

    返回:
        路径字符串, 失败返回 None
    """
    return _read_buffer(get_dll().getPath, _encode(name), buf_size=1024)


# ============================================================
# 国际化
# ============================================================

def get_locale() -> str | None:
    """获取系统语言区域设置, 如 "zh-CN", "en-US" """
    return _read_buffer(get_dll().getLocale, buf_size=32)


# ============================================================
# 显示器信息
# ============================================================

def get_displays_info() -> list[dict] | None:
    """获取所有显示器信息

    返回:
        显示器信息列表, 每项包含 bounds, work_area, scale_factor, dpi_x, dpi_y, is_primary
    """
    result = _read_buffer(get_dll().get_displays_info, buf_size=8192)
    if result:
        return json.loads(result)
    return None


# ============================================================
# YAML 配置存储
# ============================================================

def yaml_set(file_name: str, key_path: str, value: str) -> bool:
    """写入 YAML 配置值

    参数:
        file_name: 文件名 (不含路径, 存储在数据目录)
        key_path: 键路径, 点号分隔, 如 "ui.theme"
        value: 值字符串
    """
    return get_dll().yaml_set(_encode(file_name), _encode(key_path), _encode(value)) == 1


def yaml_get(file_name: str, key_path: str) -> str | None:
    """读取 YAML 配置值

    参数:
        file_name: 文件名
        key_path: 键路径, 点号分隔

    返回:
        JSON 编码的值字符串, 失败返回 None
    """
    return _read_buffer(get_dll().yaml_get, _encode(file_name), _encode(key_path), buf_size=4096)


# ============================================================
# 数据目录
# ============================================================

def clear_data_directory() -> bool:
    """清除应用数据目录 (缓存、配置等)

    注意: 此操作不可逆
    """
    return get_dll().clear_data_directory(b"I_UNDERSTAND_CLEAR_DATA") == 1


# ============================================================
# 协议服务 (本地文件服务器)
# ============================================================

def set_protocol_service_path(root_path: str) -> str | None:
    """设置本地文件服务路径, 获取访问 URL

    参数:
        root_path: 静态文件根目录的绝对路径, 支持两种形式:
            - 目录路径: 指向包含 index.html 等前端产物的文件夹
            - .japk 文件路径: 指向 JAPK 资源包文件 (JadeView 会直接从包内读取资源, 无需解压)

    返回:
        生成的基础 URL (如 "JADE://..."), 失败返回 None
    """
    buf = ctypes.create_string_buffer(512)
    if get_dll().set_protocol_service_path(_encode(root_path), buf, 512) == 1:
        url = buf.value.decode("utf-8")
        # 确保 URL 以 "/" 结尾, 否则拼接文件名会变成域名的一部分
        # 例如 "http://jade.myapp" + "index.html" = "http://jade.myappindex.html" (错误)
        if not url.endswith("/"):
            url += "/"
        return url
    return None


# ============================================================
# URL Scheme 注册
# ============================================================

def register_url_scheme(scheme: str) -> bool:
    """注册自定义 URL 协议 (如 myapp://)

    参数:
        scheme: 协议名 (如 "myapp")
    """
    return get_dll().register_url_scheme(_encode(scheme)) == 1


def unregister_url_scheme(scheme: str) -> bool:
    """取消注册自定义 URL 协议"""
    return get_dll().unregister_url_scheme(_encode(scheme)) == 1


# ============================================================
# 文件关联
# ============================================================

def register_file_association(extension: str, friendly_name: str) -> bool:
    """注册文件类型关联

    参数:
        extension: 扩展名 (不含点, 如 "mydata")
        friendly_name: 显示名称 (如 "My Data File")
    """
    return get_dll().register_file_association(_encode(extension), _encode(friendly_name)) == 1


def unregister_file_association(extension: str) -> bool:
    """取消文件类型关联"""
    return get_dll().unregister_file_association(_encode(extension)) == 1


# ============================================================
# 全局热键
# ============================================================

# Win32 修饰键常量
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008


def register_global_hotkey(
    modifiers: int | str | list[int | str] | tuple[int | str, ...] | set[int | str],
    vk: int | str,
) -> int:
    """注册全局热键

    参数:
        modifiers: 修饰键组合, 支持整数位掩码, 也支持 "CTRL+ALT"、["CTRL", "ALT"]
        vk: 主键, 支持虚拟键码整数, 也支持 "F1"、"J"、"Enter" 等字符串

    返回:
        hotkey_id (>0 成功, 0 失败), 用于 unregister_global_hotkey()
        热键触发时通过 global-hotkey 事件通知
    """
    return get_dll().register_global_hotkey(
        _normalize_hotkey_modifiers(modifiers),
        _normalize_hotkey_vk(vk),
    )


def unregister_global_hotkey(hotkey_id: int) -> bool:
    """取消全局热键注册"""
    return get_dll().unregister_global_hotkey(hotkey_id) == 1

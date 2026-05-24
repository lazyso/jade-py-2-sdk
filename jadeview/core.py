"""JadeView 2.0 核心模块 - DLL 加载、初始化、消息循环"""

import ctypes
import os
import platform
import struct
import sys
from ctypes import (
    POINTER, c_char_p, c_double, c_int32, c_size_t, c_uint8, c_uint32, c_void_p,
)
from pathlib import Path

from .types import (
    DialogAsyncCallback,
    IpcCallbackType,
    FileDialogParams, MessageBoxParams, NotificationParams,
    TrayMenuItemDesc, WebViewSettings, WebViewWindowOptions,
)

# ============================================================
# DLL 加载
# ============================================================

def _load_dll() -> ctypes.WinDLL:
    """根据 Python 位数自动加载对应的 JadeView DLL

    按以下优先级搜索 DLL 文件:
      1. 环境变量 JADEVIEW_DLL_PATH 指定的目录
      2. PyInstaller 临时解压目录 (sys._MEIPASS)
      3. 可执行文件所在目录 (适配 Nuitka / cx_Freeze / 通用 exe)
      4. 当前工作目录
      5. SDK 包内部 dll 目录 (开发模式)

    每个目录下同时检查两种文件布局:
      - 子目录: {dir}/x64/JadeView_x64.dll  或  {dir}/dll/x64/JadeView_x64.dll
      - 扁平:   {dir}/JadeView_x64.dll
    """
    bits = struct.calcsize("P") * 8  # 32 or 64
    dll_name = f"JadeView_x{'64' if bits == 64 else '86'}.dll"
    sub_dir = "x64" if bits == 64 else "x86"

    # -- 构建搜索目录列表 --
    search_dirs: list[Path] = []

    # 1. 环境变量指定 (最高优先级, 用户可完全控制)
    env_path = os.environ.get("JADEVIEW_DLL_PATH")
    if env_path:
        search_dirs.append(Path(env_path))

    # 2. PyInstaller _MEIPASS (打包后的临时解压目录)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        search_dirs.append(Path(meipass))

    # 3. 可执行文件所在目录 (Nuitka / cx_Freeze / 通用 exe)
    exe_dir = Path(sys.executable).parent
    search_dirs.append(exe_dir)

    # 4. 当前工作目录
    search_dirs.append(Path.cwd())

    # 5. SDK 包内部 (开发模式, 兼容原有逻辑)
    search_dirs.append(Path(__file__).parent / "dll")

    # -- 在每个目录中尝试多种文件布局 --
    for d in search_dirs:
        for candidate in [
            d / sub_dir / dll_name,        # {dir}/x64/JadeView_x64.dll
            d / "dll" / sub_dir / dll_name, # {dir}/dll/x64/JadeView_x64.dll
            d / dll_name,                   # {dir}/JadeView_x64.dll
        ]:
            if candidate.exists():
                return ctypes.WinDLL(str(candidate))

    # 全部找不到, 给出详细错误信息
    searched = "\n  ".join(str(d) for d in search_dirs)
    raise FileNotFoundError(
        f"找不到 {dll_name}, 已搜索以下目录:\n  {searched}\n"
        f"提示: 可设置环境变量 JADEVIEW_DLL_PATH 指定 DLL 所在目录"
    )


_dll = _load_dll()


# ============================================================
# 函数签名声明
# ============================================================

def _setup_functions():
    """声明所有 DLL 函数的参数类型和返回类型"""
    d = _dll

    # --- JAPK 内存载入 (2.1.1) ---
    d.JadeView_set_public_key.argtypes = [c_char_p]
    d.JadeView_set_public_key.restype = c_int32

    d.JadeView_load_from_bytes.argtypes = [POINTER(c_uint8), c_size_t]
    d.JadeView_load_from_bytes.restype = c_int32

    d.JadeView_is_loaded.argtypes = []
    d.JadeView_is_loaded.restype = c_int32

    d.JadeView_get_app_signature.argtypes = []
    d.JadeView_get_app_signature.restype = c_void_p

    d.JadeView_get_signature_info.argtypes = []
    d.JadeView_get_signature_info.restype = c_void_p

    d.JadeView_unload.argtypes = []
    d.JadeView_unload.restype = c_int32

    # --- 初始化与生命周期 ---
    d.JadeView_init.argtypes = [c_int32, c_char_p, c_char_p, c_char_p, c_char_p, c_int32]
    d.JadeView_init.restype = c_int32

    d.run_message_loop.argtypes = []
    d.run_message_loop.restype = c_int32

    d.cleanup_all_windows.argtypes = []
    d.cleanup_all_windows.restype = c_int32

    # --- 窗口创建 ---
    d.create_webview_window.argtypes = [c_char_p, c_uint32, POINTER(WebViewWindowOptions), POINTER(WebViewSettings)]
    d.create_webview_window.restype = c_uint32

    d.create_borderless_webview_window.argtypes = [c_char_p, POINTER(WebViewSettings)]
    d.create_borderless_webview_window.restype = c_uint32

    d.get_window_hwnd.argtypes = [c_uint32]
    d.get_window_hwnd.restype = c_size_t

    # --- 窗口管理 ---
    d.navigate_to_url.argtypes = [c_uint32, c_char_p]
    d.navigate_to_url.restype = c_int32

    d.reload_webview_window.argtypes = [c_uint32]
    d.reload_webview_window.restype = c_int32

    d.execute_javascript.argtypes = [c_uint32, c_char_p]
    d.execute_javascript.restype = c_int32

    d.set_window_title.argtypes = [c_uint32, c_char_p]
    d.set_window_title.restype = c_int32

    d.set_window_size.argtypes = [c_uint32, c_int32, c_int32]
    d.set_window_size.restype = c_int32

    d.set_window_position.argtypes = [c_uint32, c_int32, c_int32]
    d.set_window_position.restype = c_int32

    d.set_window_visible.argtypes = [c_uint32, c_int32]
    d.set_window_visible.restype = c_int32

    d.set_window_focus.argtypes = [c_uint32]
    d.set_window_focus.restype = c_int32

    d.set_window_always_on_top.argtypes = [c_uint32, c_int32]
    d.set_window_always_on_top.restype = c_int32

    d.close_window.argtypes = [c_uint32]
    d.close_window.restype = c_int32

    d.minimize_window.argtypes = [c_uint32]
    d.minimize_window.restype = c_int32

    d.toggle_maximize_window.argtypes = [c_uint32]
    d.toggle_maximize_window.restype = c_int32

    d.is_window_maximized.argtypes = [c_uint32]
    d.is_window_maximized.restype = c_int32

    d.set_window_fullscreen.argtypes = [c_uint32, c_int32]
    d.set_window_fullscreen.restype = c_int32

    d.set_window_enabled.argtypes = [c_uint32, c_int32]
    d.set_window_enabled.restype = c_int32

    d.request_redraw.argtypes = [c_uint32]
    d.request_redraw.restype = c_int32

    # --- 边框样式 ---
    d.set_window_frame_style.argtypes = [c_uint32, c_char_p]
    d.set_window_frame_style.restype = c_int32

    d.set_titlebar_overlay_style.argtypes = [c_uint32, c_int32, c_char_p, c_char_p]
    d.set_titlebar_overlay_style.restype = c_int32

    # --- 打印 ---
    d.jade_print.argtypes = [c_uint32]
    d.jade_print.restype = c_int32

    # --- 主题与外观 ---
    d.set_window_theme.argtypes = [c_uint32, c_char_p]
    d.set_window_theme.restype = c_int32

    d.get_window_theme.argtypes = [c_uint32]
    d.get_window_theme.restype = c_int32

    d.set_window_backdrop.argtypes = [c_uint32, c_char_p]
    d.set_window_backdrop.restype = c_int32

    d.set_window_background_color.argtypes = [c_uint32, c_char_p]
    d.set_window_background_color.restype = c_int32

    d.set_content_protection.argtypes = [c_uint32, c_int32]
    d.set_content_protection.restype = c_int32

    d.set_webview_zoom.argtypes = [c_uint32, c_double]
    d.set_webview_zoom.restype = c_int32

    # --- IPC ---
    d.jade_on.argtypes = [c_char_p, IpcCallbackType]
    d.jade_on.restype = c_uint32

    d.jade_off.argtypes = [c_char_p, c_uint32]
    d.jade_off.restype = c_int32

    d.register_ipc_handler.argtypes = [c_char_p, IpcCallbackType]
    d.register_ipc_handler.restype = c_int32

    d.send_ipc_message.argtypes = [c_uint32, c_char_p, c_char_p]
    d.send_ipc_message.restype = c_int32

    # --- 协议服务 ---
    d.set_protocol_service_path.argtypes = [c_char_p, c_char_p, c_size_t]
    d.set_protocol_service_path.restype = c_int32

    # --- 托盘 ---
    d.tray_create.argtypes = []
    d.tray_create.restype = c_uint32

    d.tray_destroy.argtypes = [c_uint32]
    d.tray_destroy.restype = c_int32

    d.tray_set_visible.argtypes = [c_uint32, c_int32]
    d.tray_set_visible.restype = c_int32

    d.tray_set_tooltip.argtypes = [c_uint32, c_char_p]
    d.tray_set_tooltip.restype = c_int32

    d.tray_set_icon_from_file.argtypes = [c_uint32, c_char_p]
    d.tray_set_icon_from_file.restype = c_int32

    d.tray_set_menu_items.argtypes = [c_uint32, POINTER(TrayMenuItemDesc), c_uint32]
    d.tray_set_menu_items.restype = c_int32

    # --- 对话框 (2.0: 同步返回 char*, 需 jade_text_free 释放) ---
    d.jade_dialog_show_open_dialog.argtypes = [POINTER(FileDialogParams)]
    d.jade_dialog_show_open_dialog.restype = c_void_p  # char* 用 c_void_p 保留原始指针

    d.jade_dialog_show_save_dialog.argtypes = [POINTER(FileDialogParams)]
    d.jade_dialog_show_save_dialog.restype = c_void_p

    d.jade_dialog_show_message_box.argtypes = [POINTER(MessageBoxParams)]
    d.jade_dialog_show_message_box.restype = c_void_p

    d.jade_dialog_show_error_box.argtypes = [c_uint32, c_char_p, c_char_p]
    d.jade_dialog_show_error_box.restype = c_int32

    # --- 对话框 (2.0 异步) ---
    d.jade_dialog_show_open_dialog_async.argtypes = [POINTER(FileDialogParams), DialogAsyncCallback]
    d.jade_dialog_show_open_dialog_async.restype = c_int32

    d.jade_dialog_show_save_dialog_async.argtypes = [POINTER(FileDialogParams), DialogAsyncCallback]
    d.jade_dialog_show_save_dialog_async.restype = c_int32

    d.jade_dialog_show_message_box_async.argtypes = [POINTER(MessageBoxParams), DialogAsyncCallback]
    d.jade_dialog_show_message_box_async.restype = c_int32

    # --- 通知 ---
    d.show_notification.argtypes = [POINTER(NotificationParams)]
    d.show_notification.restype = c_int32

    # --- 工具函数 ---
    d.jadeview_version.argtypes = [c_char_p, c_size_t]
    d.jadeview_version.restype = c_int32

    d.get_webview_version.argtypes = [c_char_p, c_size_t]
    d.get_webview_version.restype = c_int32

    d.getPath.argtypes = [c_char_p, c_char_p, c_size_t]
    d.getPath.restype = c_int32

    d.getLocale.argtypes = [c_char_p, c_size_t]
    d.getLocale.restype = c_int32

    d.get_displays_info.argtypes = [c_char_p, c_size_t]
    d.get_displays_info.restype = c_int32

    d.get_window_count.argtypes = []
    d.get_window_count.restype = c_uint32

    d.is_windows_11.argtypes = []
    d.is_windows_11.restype = c_int32

    d.yaml_set.argtypes = [c_char_p, c_char_p, c_char_p]
    d.yaml_set.restype = c_int32

    d.yaml_get.argtypes = [c_char_p, c_char_p, c_char_p, c_size_t]
    d.yaml_get.restype = c_int32

    d.clear_data_directory.argtypes = [c_char_p]
    d.clear_data_directory.restype = c_int32

    d.register_url_scheme.argtypes = [c_char_p]
    d.register_url_scheme.restype = c_int32

    d.unregister_url_scheme.argtypes = [c_char_p]
    d.unregister_url_scheme.restype = c_int32

    d.register_file_association.argtypes = [c_char_p, c_char_p]
    d.register_file_association.restype = c_int32

    d.unregister_file_association.argtypes = [c_char_p]
    d.unregister_file_association.restype = c_int32

    d.register_global_hotkey.argtypes = [c_uint32, c_uint32]
    d.register_global_hotkey.restype = c_uint32

    d.unregister_global_hotkey.argtypes = [c_uint32]
    d.unregister_global_hotkey.restype = c_int32

    d.jade_text_create.argtypes = [c_char_p]
    d.jade_text_create.restype = c_void_p  # 必须用 c_void_p 保留原始指针, c_char_p 会自动转 bytes 导致指针丢失

    d.jade_text_free.argtypes = [c_void_p]  # 接受 c_void_p 原始指针
    d.jade_text_free.restype = None


_setup_functions()


def get_dll():
    """获取已加载的 DLL 实例"""
    return _dll

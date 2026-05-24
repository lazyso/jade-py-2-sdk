"""JadeView 2.0 ctypes 结构体定义"""

import ctypes
from ctypes import c_int32, c_uint32, c_char_p, c_void_p, CFUNCTYPE

# ============================================================
# 回调函数类型
# ============================================================

# IPC 回调: (window_id, event_data) -> void* (原始指针)
# 返回类型用 c_void_p 而非 c_char_p, 避免 ctypes 自动将指针转为 bytes 导致丢失
IpcCallbackType = CFUNCTYPE(c_void_p, c_uint32, c_char_p)


# ============================================================
# WebView 设置
# ============================================================

class WebViewSettings(ctypes.Structure):
    """WebView 渲染引擎设置"""
    _fields_ = [
        ("autoplay", c_int32),               # 是否自动播放媒体
        ("background_throttling", c_int32),   # 后台时是否降低帧率
        ("disable_right_click", c_int32),     # 是否禁用右键菜单
        ("ua", c_char_p),                     # 自定义 User-Agent
        ("preload_js", c_char_p),             # 页面加载前注入的 JS
        ("allow_fullscreen", c_int32),        # 是否允许全屏 API
        ("postmessage_whitelist", c_char_p),  # postMessage 来源白名单
        ("cors_whitelist", c_char_p),         # CORS 来源白名单
    ]


# ============================================================
# 窗口创建选项
# ============================================================

class WebViewWindowOptions(ctypes.Structure):
    """窗口创建时的配置项"""
    _fields_ = [
        ("title", c_char_p),              # 窗口标题
        ("width", c_int32),               # 宽度(像素)
        ("height", c_int32),              # 高度(像素)
        ("resizable", c_int32),           # 是否可调整大小
        ("frame_style", c_char_p),        # 边框样式: "normal"/"no-titlebar"/"borderless"
        ("transparent", c_int32),         # 是否透明背景
        ("background_color", c_char_p),   # 背景颜色 "#RRGGBB"
        ("always_on_top", c_int32),       # 是否置顶
        ("theme", c_char_p),             # 主题: "Light"/"Dark"/"System"
        ("maximized", c_int32),           # 是否最大化打开
        ("maximizable", c_int32),         # 是否允许最大化按钮
        ("minimizable", c_int32),         # 是否允许最小化按钮
        ("x", c_int32),                   # 左上角 X 坐标, -1 居中
        ("y", c_int32),                   # 左上角 Y 坐标, -1 居中
        ("min_width", c_int32),           # 最小宽度, 0 不限制
        ("min_height", c_int32),          # 最小高度, 0 不限制
        ("max_width", c_int32),           # 最大宽度, 0 不限制
        ("max_height", c_int32),          # 最大高度, 0 不限制
        ("fullscreen", c_int32),          # 是否全屏打开
        ("focus", c_int32),               # 创建时是否获取焦点
        ("hide_window", c_int32),         # 是否隐藏创建 (后续 show)
        ("use_page_icon", c_int32),       # 是否使用网页 favicon 作为窗口图标
        ("content_protection", c_int32),  # 是否启用内容保护(防截图/录屏)
        ("auto_save_state", c_int32),     # 是否自动保存/恢复窗口位置
    ]


# ============================================================
# 对话框参数
# ============================================================

class FileDialogParams(ctypes.Structure):
    """文件对话框参数 (2.0 统一结构, 用于 open/save)"""
    _fields_ = [
        ("window_id", c_uint32),
        ("title", c_char_p),
        ("default_path", c_char_p),
        ("button_label", c_char_p),
        ("filters", c_char_p),
        ("properties", c_char_p),
    ]


class MessageBoxParams(ctypes.Structure):
    """消息框参数 (2.0 不再包含 blocking/callback)"""
    _fields_ = [
        ("window_id", c_uint32),
        ("title", c_char_p),
        ("message", c_char_p),
        ("detail", c_char_p),
        ("buttons", c_char_p),
        ("default_id", c_int32),
        ("cancel_id", c_int32),
        ("type_", c_char_p),
    ]


# 异步对话框回调: void (JADEVIEW_CALL *)(const char* json_result)
DialogAsyncCallback = CFUNCTYPE(None, c_char_p)


# ============================================================
# 通知参数
# ============================================================

class NotificationParams(ctypes.Structure):
    """系统通知参数"""
    _fields_ = [
        ("summary", c_char_p),   # 通知标题 (必填)
        ("body", c_char_p),      # 通知正文
        ("icon", c_char_p),      # 图标文件绝对路径
        ("timeout", c_int32),    # 超时毫秒数, <=0 使用系统默认
        ("button1", c_char_p),   # 第一个按钮文字
        ("button2", c_char_p),   # 第二个按钮文字
        ("text3", c_char_p),     # 附加文本行
        ("action", c_char_p),    # 动作回调参数
    ]


# ============================================================
# 托盘菜单项
# ============================================================

class TrayMenuItemDesc(ctypes.Structure):
    """托盘菜单项描述"""
    _fields_ = [
        ("item_type", c_int32),    # 类型: 0=普通 1=子菜单 2=分隔线 3=分组
        ("key", c_char_p),         # 唯一标识
        ("label", c_char_p),       # 显示文字
        ("parent_key", c_char_p),  # 父项 key, None 表示根级
        ("disabled", c_int32),     # 是否禁用
        ("dangerous", c_int32),    # 是否标记为危险操作
    ]

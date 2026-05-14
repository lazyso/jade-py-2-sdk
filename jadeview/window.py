"""JadeView 2.0 窗口模块 - 窗口创建与管理"""

from ctypes import byref

from .core import get_dll
from .types import WebViewSettings, WebViewWindowOptions


def _encode(s: str | None) -> bytes | None:
    return s.encode("utf-8") if s else None


def _build_window_options(
    title: str | None = None,
    width: int = 800,
    height: int = 600,
    resizable: int = 1,
    frame_style: str | None = None,
    transparent: int = 0,
    background_color: str | None = None,
    always_on_top: int = 0,
    theme: str | None = None,
    maximized: int = 0,
    maximizable: int = 1,
    minimizable: int = 1,
    x: int = -1,
    y: int = -1,
    min_width: int = 0,
    min_height: int = 0,
    max_width: int = 0,
    max_height: int = 0,
    fullscreen: int = 0,
    focus: int = 1,
    hide_window: int = 0,
    use_page_icon: int = 0,
    content_protection: int = 0,
    auto_save_state: int = 0,
) -> WebViewWindowOptions:
    """构建窗口选项结构体"""
    opts = WebViewWindowOptions()
    opts.title = _encode(title)
    opts.width = width
    opts.height = height
    opts.resizable = resizable
    opts.frame_style = _encode(frame_style)
    opts.transparent = transparent
    opts.background_color = _encode(background_color)
    opts.always_on_top = always_on_top
    opts.theme = _encode(theme)
    opts.maximized = maximized
    opts.maximizable = maximizable
    opts.minimizable = minimizable
    opts.x = x
    opts.y = y
    opts.min_width = min_width
    opts.min_height = min_height
    opts.max_width = max_width
    opts.max_height = max_height
    opts.fullscreen = fullscreen
    opts.focus = focus
    opts.hide_window = hide_window
    opts.use_page_icon = use_page_icon
    opts.content_protection = content_protection
    opts.auto_save_state = auto_save_state
    return opts


def _build_webview_settings(
    autoplay: int = 0,
    background_throttling: int = 1,
    disable_right_click: int = 0,
    ua: str | None = None,
    preload_js: str | None = None,
    allow_fullscreen: int = 1,
    postmessage_whitelist: str | None = None,
) -> WebViewSettings:
    """构建 WebView 设置结构体"""
    s = WebViewSettings()
    s.autoplay = autoplay
    s.background_throttling = background_throttling
    s.disable_right_click = disable_right_click
    s.ua = _encode(ua)
    s.preload_js = _encode(preload_js)
    s.allow_fullscreen = allow_fullscreen
    s.postmessage_whitelist = _encode(postmessage_whitelist)
    return s


def create_webview_window(
    url: str,
    parent_window_id: int = 0,
    *,
    # 窗口选项
    title: str | None = None,
    width: int = 800,
    height: int = 600,
    resizable: int = 1,
    frame_style: str | None = None,
    transparent: int = 0,
    background_color: str | None = None,
    always_on_top: int = 0,
    theme: str | None = None,
    maximized: int = 0,
    maximizable: int = 1,
    minimizable: int = 1,
    x: int = -1,
    y: int = -1,
    min_width: int = 0,
    min_height: int = 0,
    max_width: int = 0,
    max_height: int = 0,
    fullscreen: int = 0,
    focus: int = 1,
    hide_window: int = 0,
    use_page_icon: int = 0,
    content_protection: int = 0,
    auto_save_state: int = 0,
    # WebView 设置
    autoplay: int = 0,
    background_throttling: int = 1,
    disable_right_click: int = 0,
    ua: str | None = None,
    preload_js: str | None = None,
    allow_fullscreen: int = 1,
    postmessage_whitelist: str | None = None,
) -> int:
    """创建标准 WebView 窗口

    参数:
        url: 要加载的网址
        parent_window_id: 父窗口 ID, 0 表示顶级窗口
        title: 窗口标题
        width/height: 窗口宽高(像素)
        resizable: 是否可调整大小 (1=是 0=否)
        frame_style: 边框样式 "normal"/"no-titlebar"/"borderless"/"title-overlay"
        transparent: 是否透明背景
        background_color: 背景色 "#RRGGBB"
        always_on_top: 是否置顶
        theme: 主题 "Light"/"Dark"/"System"
        maximized: 是否最大化打开
        maximizable/minimizable: 是否允许最大化/最小化
        x/y: 窗口位置, 均为-1时居中
        min_width/min_height/max_width/max_height: 尺寸约束
        fullscreen: 是否全屏打开
        focus: 创建时是否获取焦点
        hide_window: 是否隐藏创建
        use_page_icon: 是否用网页图标作窗口图标
        content_protection: 是否启用防截屏
        auto_save_state: 是否自动记忆窗口位置
        autoplay: 是否自动播放媒体
        background_throttling: 后台是否降帧
        disable_right_click: 是否禁用右键
        ua: 自定义 User-Agent
        preload_js: 预注入 JS
        allow_fullscreen: 是否允许全屏 API
        postmessage_whitelist: postMessage 白名单

    返回:
        window_id (>0 成功, 0 失败)
    """
    opts = _build_window_options(
        title=title, width=width, height=height, resizable=resizable,
        frame_style=frame_style, transparent=transparent, background_color=background_color,
        always_on_top=always_on_top, theme=theme, maximized=maximized,
        maximizable=maximizable, minimizable=minimizable, x=x, y=y,
        min_width=min_width, min_height=min_height, max_width=max_width, max_height=max_height,
        fullscreen=fullscreen, focus=focus, hide_window=hide_window,
        use_page_icon=use_page_icon, content_protection=content_protection,
        auto_save_state=auto_save_state,
    )
    settings = _build_webview_settings(
        autoplay=autoplay, background_throttling=background_throttling,
        disable_right_click=disable_right_click, ua=ua, preload_js=preload_js,
        allow_fullscreen=allow_fullscreen, postmessage_whitelist=postmessage_whitelist,
    )
    return get_dll().create_webview_window(
        _encode(url), parent_window_id, byref(opts), byref(settings)
    )


def create_borderless_webview_window(
    url: str,
    *,
    autoplay: int = 0,
    background_throttling: int = 1,
    disable_right_click: int = 0,
    ua: str | None = None,
    preload_js: str | None = None,
    allow_fullscreen: int = 1,
    postmessage_whitelist: str | None = None,
) -> int:
    """创建无边框 WebView 窗口 (可获取 HWND)

    参数:
        url: 要加载的网址
        (其余参数同 WebView 设置)

    返回:
        window_id (>0 成功, 0 失败)
    """
    settings = _build_webview_settings(
        autoplay=autoplay, background_throttling=background_throttling,
        disable_right_click=disable_right_click, ua=ua, preload_js=preload_js,
        allow_fullscreen=allow_fullscreen, postmessage_whitelist=postmessage_whitelist,
    )
    return get_dll().create_borderless_webview_window(_encode(url), byref(settings))


def get_window_hwnd(window_id: int) -> int:
    """获取无边框窗口的 HWND

    参数:
        window_id: 窗口 ID (仅限 borderless 窗口)

    返回:
        HWND (0 表示失败或非 borderless 窗口)
    """
    return get_dll().get_window_hwnd(window_id)


def set_window_title(window_id: int, title: str) -> bool:
    """设置窗口标题"""
    return get_dll().set_window_title(window_id, _encode(title)) == 1


def set_window_size(window_id: int, width: int, height: int) -> bool:
    """设置窗口大小 (像素)"""
    return get_dll().set_window_size(window_id, width, height) == 1


def set_window_position(window_id: int, x: int, y: int) -> bool:
    """设置窗口位置"""
    return get_dll().set_window_position(window_id, x, y) == 1


def set_window_visible(window_id: int, visible: bool = True) -> bool:
    """显示或隐藏窗口"""
    return get_dll().set_window_visible(window_id, 1 if visible else 0) == 1


def set_window_focus(window_id: int) -> bool:
    """使窗口获取焦点"""
    return get_dll().set_window_focus(window_id) == 1


def set_window_always_on_top(window_id: int, always_on_top: bool = True) -> bool:
    """设置窗口是否置顶"""
    return get_dll().set_window_always_on_top(window_id, 1 if always_on_top else 0) == 1


def close_window(window_id: int) -> bool:
    """关闭窗口"""
    return get_dll().close_window(window_id) == 1


def minimize_window(window_id: int) -> bool:
    """最小化窗口"""
    return get_dll().minimize_window(window_id) == 1


def toggle_maximize_window(window_id: int) -> bool:
    """切换最大化/还原"""
    return get_dll().toggle_maximize_window(window_id) == 1


def is_window_maximized(window_id: int) -> bool:
    """查询窗口是否最大化"""
    return get_dll().is_window_maximized(window_id) == 1


def set_window_fullscreen(window_id: int, fullscreen: bool = True) -> bool:
    """设置窗口全屏/退出全屏"""
    return get_dll().set_window_fullscreen(window_id, 1 if fullscreen else 0) == 1


def set_window_enabled(window_id: int, enabled: bool = True) -> bool:
    """启用或禁用窗口交互"""
    return get_dll().set_window_enabled(window_id, 1 if enabled else 0) == 1


def request_redraw(window_id: int) -> bool:
    """请求窗口重绘"""
    return get_dll().request_redraw(window_id) == 1


def set_window_theme(window_id: int, theme: str) -> bool:
    """设置窗口主题

    参数:
        window_id: 窗口 ID
        theme: "Light"/"Dark"/"System"
    """
    return get_dll().set_window_theme(window_id, _encode(theme)) == 1


def get_window_theme(window_id: int) -> int:
    """获取窗口当前主题代码"""
    return get_dll().get_window_theme(window_id)


def set_window_backdrop(window_id: int, backdrop_type: str) -> bool:
    """设置窗口背景效果

    参数:
        backdrop_type: "mica"/"micaAlt"/"acrylic"
    """
    return get_dll().set_window_backdrop(window_id, _encode(backdrop_type)) == 1


def set_window_background_color(window_id: int, color: str) -> bool:
    """设置窗口背景颜色

    参数:
        color: 颜色值 "#RRGGBB"
    """
    return get_dll().set_window_background_color(window_id, _encode(color)) == 1


def set_window_frame_style(window_id: int, frame_style: str) -> bool:
    """运行时修改窗口边框样式 (无需重新创建窗口)

    参数:
        window_id: 窗口 ID
        frame_style: 边框样式字符串, 可选值:
            - "normal": 有边框+标题栏
            - "no-titlebar": 有边框+无标题栏
            - "borderless": 无边框+无标题栏
            - "title-overlay": 有边框+无标题栏+内置标题栏按钮 (Windows 专属)
    """
    return get_dll().set_window_frame_style(window_id, _encode(frame_style)) == 1


def set_titlebar_overlay_style(
    window_id: int,
    height: int = 0,
    icon_color_hex: str | None = None,
    hover_bg_hex: str | None = None,
) -> bool:
    """自定义 title-overlay 样式窗口的标题栏按钮覆盖层外观 (Windows 专属)

    仅对 frame_style="title-overlay" 的窗口有效。

    参数:
        window_id: 窗口 ID
        height: 按钮高度(像素), 0 或负数使用默认值 32
        icon_color_hex: 图标颜色 "#RRGGBB", None 使用默认颜色
        hover_bg_hex: 非关闭按钮悬浮背景色 "#RRGGBB" 或 "#RRGGBBAA", None 使用默认深灰色

    注意:
        关闭按钮悬浮背景色固定为红色(#E81123), 图标固定为白色, 不受此 API 影响。
    """
    return get_dll().set_titlebar_overlay_style(
        window_id, height, _encode(icon_color_hex), _encode(hover_bg_hex)
    ) == 1


def jade_print(window_id: int) -> bool:
    """打印 WebView 内容 (打开系统打印对话框)

    参数:
        window_id: 窗口 ID

    返回:
        True=打印对话框已打开, False=失败(窗口不存在或不支持)
    """
    return get_dll().jade_print(window_id) == 1

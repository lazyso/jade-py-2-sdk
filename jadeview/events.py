"""JadeView 2.0 事件名称常量

与前端 jade.on() 事件名保持一致，方便对照使用。
"""


# ============================================================
# 应用生命周期
# ============================================================
APP_READY = "app-ready"                      # 应用就绪 (初始化完成)
SECOND_INSTANCE = "second-instance"          # 第二个实例启动 (单实例模式)

# ============================================================
# 窗口生命周期
# ============================================================
WINDOW_CREATED = "window-created"            # 窗口已创建
APP_WINDOW_CREATED = "app-window-created"    # 窗口已创建 (别名)
WINDOW_CLOSING = "window-closing"            # 窗口即将关闭 (可拦截)
WINDOW_CLOSED = "window-closed"              # 窗口已关闭
WINDOW_DESTROYED = "window-destroyed"        # 窗口已销毁
WINDOW_ALL_CLOSED = "window-all-closed"      # 所有窗口已关闭

# ============================================================
# 窗口状态
# ============================================================
WINDOW_RESIZED = "window-resized"            # 窗口大小改变
WINDOW_STATE_CHANGED = "window-state-changed"  # 最大化状态改变
WINDOW_FULLSCREEN = "window-fullscreen"      # 全屏状态改变
WINDOW_MOVED = "window-moved"                # 窗口位置改变
WINDOW_FOCUSED = "window-focused"            # 窗口获得焦点
WINDOW_BLURRED = "window-blurred"            # 窗口失去焦点

# ============================================================
# WebView / 导航事件
# ============================================================
WEBVIEW_WILL_NAVIGATE = "webview-will-navigate"        # 即将导航 (可拦截)
WEBVIEW_DID_START_LOADING = "webview-did-start-loading"  # 开始加载
WEBVIEW_DID_FINISH_LOAD = "webview-did-finish-load"    # 加载完成
WEBVIEW_NEW_WINDOW = "webview-new-window"              # 请求打开新窗口 (可拦截)
WEBVIEW_PAGE_TITLE_UPDATED = "webview-page-title-updated"  # 页面标题变化
WEBVIEW_PAGE_ICON_UPDATED = "webview-page-icon-updated"    # 页面图标变化
WEBVIEW_DOWNLOAD_STARTED = "webview-download-started"      # 下载开始 (默认拦截)

# ============================================================
# JavaScript / 数据事件
# ============================================================
JAVASCRIPT_RESULT = "javascript-result"      # execute_javascript 执行结果
FILE_DROP = "file-drop"                      # 文件拖放到 WebView
POSTMESSAGE_RECEIVED = "postmessage-received"  # 收到 postMessage

# ============================================================
# 托盘事件
# ============================================================
TRAY_MENU_COMMAND = "tray-menu-command"      # 托盘菜单项被点击
TRAY_EVENT = "tray-event"                    # 托盘图标交互 (点击/悬停等)

# ============================================================
# 通知事件
# ============================================================
NOTIFICATION_SHOWN = "notification-shown"        # 通知已显示
NOTIFICATION_DISMISSED = "notification-dismissed"  # 通知已关闭
NOTIFICATION_FAILED = "notification-failed"      # 通知显示失败
NOTIFICATION_ACTION = "notification-action"      # 通知按钮被点击

# ============================================================
# 全局热键
# ============================================================
GLOBAL_HOTKEY = "global-hotkey"              # 全局热键触发

# ============================================================
# 主题
# ============================================================
THEME_CHANGED = "theme-changed"              # 系统/窗口主题变化
UPDATE_WINDOW_ICON = "update-window-icon"    # 窗口图标需要刷新

# ============================================================
# 托盘菜单项类型常量
# ============================================================
TRAY_ITEM_NORMAL = 0    # 普通菜单项
TRAY_ITEM_SUBMENU = 1   # 子菜单
TRAY_ITEM_DIVIDER = 2   # 分隔线
TRAY_ITEM_GROUP = 3     # 分组

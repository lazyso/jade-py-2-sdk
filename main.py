"""JadeView 2.1.1 SDK 使用示例"""
"""测试是没什么问题了，终于好用的ui框架啦！"""
import jadeview
from jadeview import events


def on_ready(window_id, data):
    """app-ready 回调 - 在此创建窗口"""
    print(f"应用就绪! window_id={window_id}, data={data}")

    # 获取版本信息
    print(f"JadeView 版本: {jadeview.tools.jadeview_version()}")
    print(f"WebView2 版本: {jadeview.tools.get_webview_version()}")

    # 设置本地文件服务
    # base_url = jadeview.tools.set_protocol_service_path("C:/path/to/your/web")

    # 创建窗口
    win_id = jadeview.window.create_webview_window(
        "https://example.com",
        title="JadeView Demo",
        width=1024,
        height=768,
        theme="System",
    )
    print(f"创建窗口: {win_id}")


def on_window_closing(window_id, data):
    """窗口关闭拦截 - 返回 None 放行, 返回 True 拦截"""
    print(f"窗口 {window_id} 正在关闭...")
    # 可以在这里弹出确认对话框
    # result = jadeview.dialog.show_message_box(
    #     window_id, message="确定关闭?", buttons=["是", "否"]
    # )
    # if result and result["response"] == 1:
    #     return True  # 拦截关闭
    return None  # 允许关闭


def on_all_closed(window_id, data):
    """所有窗口关闭后退出消息循环"""
    print("所有窗口已关闭，正在退出...")
    jadeview.cleanup()


def main():
    # 1. 注册事件 (必须在 init 之前)
    jadeview.ipc.on(events.APP_READY, on_ready)
    jadeview.ipc.on(events.WINDOW_CLOSING, on_window_closing)
    jadeview.ipc.on(events.WINDOW_ALL_CLOSED, on_all_closed)

    # 2. 初始化
    ok = jadeview.init(
        "JadeView Demo",
        "jadedemo",
        enable_devmod=True,
    )
    if not ok:
        print("初始化失败!")
        return

    # 3. 启动消息循环 (阻塞)
    jadeview.run()
    print("应用已退出")


if __name__ == "__main__":
    main()

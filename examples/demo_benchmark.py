"""JadeView 2.1.1 SDK 性能基准测试

测试项目:
  1. 窗口创建/销毁速度
  2. IPC 通信吞吐
  3. JS 执行性能
  4. 综合流水线

用法:
    cd examples
    python demo_benchmark.py
"""

import os
import sys
import json
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import jadeview
from jadeview import events, ipc, window, webview, tools

# --- 全局状态 ---
bench_win_id = 0       # 基准测试主窗口
base_url = ""          # 协议服务基础 URL
pong_event = threading.Event()
pong_data = None


def fmt(ms):
    """格式化毫秒数"""
    return f"{ms:.2f}"


def calc_stats(times):
    """计算统计数据"""
    if not times:
        return {"count": 0, "avg": "0", "min": "0", "max": "0", "total": "0"}
    total = sum(times)
    return {
        "count": len(times),
        "avg": fmt(total / len(times)),
        "min": fmt(min(times)),
        "max": fmt(max(times)),
        "total": fmt(total),
    }


def push_progress(msg):
    """推送进度消息到前端"""
    print(f"  {msg}")
    if bench_win_id:
        ipc.send_ipc_message(bench_win_id, "bench-progress", {"message": msg})


def push_result(key, stats):
    """推送结果到前端"""
    stats["key"] = key
    if bench_win_id:
        ipc.send_ipc_message(bench_win_id, "bench-result", stats)


# ========== 测试: 窗口创建/销毁 ==========

def bench_windows(window_id, payload):
    """批量创建/销毁窗口"""
    count = 20
    push_progress(f"窗口测试: 创建 {count} 个窗口...")

    # 创建
    create_times = []
    win_ids = []
    for i in range(count):
        t0 = time.perf_counter()
        wid = window.create_webview_window(
            "about:blank",
            title=f"Bench #{i+1}",
            width=400, height=300,
            hide_window=1,  # 隐藏窗口避免闪烁
        )
        elapsed = (time.perf_counter() - t0) * 1000
        create_times.append(elapsed)
        if wid:
            win_ids.append(wid)
        push_progress(f"  创建窗口 {i+1}/{count}: {fmt(elapsed)}ms (id={wid})")

    stats = calc_stats(create_times)
    push_progress(f"创建统计: avg={stats['avg']}ms, min={stats['min']}ms, max={stats['max']}ms, total={stats['total']}ms")

    # 销毁
    push_progress(f"窗口测试: 销毁 {len(win_ids)} 个窗口...")
    destroy_times = []
    for wid in win_ids:
        t0 = time.perf_counter()
        window.close_window(wid)
        elapsed = (time.perf_counter() - t0) * 1000
        destroy_times.append(elapsed)

    d_stats = calc_stats(destroy_times)
    push_progress(f"销毁统计: avg={d_stats['avg']}ms, total={d_stats['total']}ms")

    # 汇总 (使用创建时间作为主要指标)
    push_result("windows", stats)
    return json.dumps({"create": stats, "destroy": d_stats})


# ========== 测试: IPC 吞吐 ==========

def bench_ipc_throughput(window_id, payload):
    """Python → JS 发送吞吐测试"""
    count = 1000
    push_progress(f"IPC吞吐: Python→JS 发送 {count} 条消息...")

    times = []
    t_start = time.perf_counter()
    for i in range(count):
        t0 = time.perf_counter()
        ipc.send_ipc_message(bench_win_id, "bench-ping", {"seq": i})
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
    total_ms = (time.perf_counter() - t_start) * 1000

    stats = calc_stats(times)
    throughput = count / (total_ms / 1000) if total_ms > 0 else 0
    push_progress(f"IPC吞吐: {count}条/{fmt(total_ms)}ms, 吞吐={throughput:.0f}条/秒")
    push_result("ipc", stats)

    # RTT 测试 (逐条发送并等待回复)
    rtt_count = 100
    push_progress(f"IPC RTT: 往返测试 {rtt_count} 次...")
    rtt_times = []
    for i in range(rtt_count):
        global pong_data
        pong_event.clear()
        pong_data = None
        t0 = time.perf_counter()
        ipc.send_ipc_message(bench_win_id, "bench-ping", {"seq": i, "rtt": True})
        # 等待前端 pong 回来 (通过 bench:pong handler)
        got_pong = pong_event.wait(timeout=2.0)
        elapsed = (time.perf_counter() - t0) * 1000
        if got_pong:
            rtt_times.append(elapsed)

    if rtt_times:
        rtt_stats = calc_stats(rtt_times)
        push_progress(f"RTT统计: avg={rtt_stats['avg']}ms, min={rtt_stats['min']}ms, max={rtt_stats['max']}ms")
        push_result("ipc-rtt", rtt_stats)
    else:
        push_progress("RTT测试: 未收到回复")

    return json.dumps({"throughput": stats})


def handle_bench_pong(window_id, payload):
    """接收前端 pong 回复"""
    global pong_data
    pong_data = payload
    pong_event.set()
    return "ok"


# ========== 测试: JS 执行 ==========

js_result_event = threading.Event()
js_result_count = 0

def bench_js_exec(window_id, payload):
    """批量 execute_javascript"""
    global js_result_count
    count = 200
    push_progress(f"JS执行: 批量执行 {count} 次...")

    js_result_count = 0
    times = []
    for i in range(count):
        t0 = time.perf_counter()
        webview.execute_javascript(bench_win_id, f"1 + {i}")
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)

    stats = calc_stats(times)
    push_progress(f"JS提交统计: avg={stats['avg']}ms, total={stats['total']}ms")
    push_progress(f"(注: 以上为提交耗时, 结果通过 javascript-result 异步返回)")
    push_result("js", stats)
    return json.dumps(stats)


def on_js_result_bench(window_id, data):
    """收集 JS 执行结果"""
    global js_result_count
    js_result_count += 1


# ========== 测试: 综合流水线 ==========

def bench_pipeline(window_id, payload):
    """创建窗口 → 导航 → 执行JS → 关闭 的完整流水线"""
    iterations = 5
    push_progress(f"流水线: {iterations} 轮 创建→导航→JS→关闭...")

    times = []
    for i in range(iterations):
        t0 = time.perf_counter()

        # 创建
        wid = window.create_webview_window(
            "about:blank",
            title=f"Pipeline #{i+1}",
            width=400, height=300,
            hide_window=1,
        )
        if not wid:
            push_progress(f"  第 {i+1} 轮: 创建窗口失败")
            continue

        # 导航
        webview.navigate_to_url(wid, f"{base_url}ipc_test.html")

        # 执行 JS
        webview.execute_javascript(wid, "'pipeline-test'")

        # 关闭
        window.close_window(wid)

        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
        push_progress(f"  第 {i+1}/{iterations} 轮: {fmt(elapsed)}ms")

    stats = calc_stats(times)
    push_progress(f"流水线统计: avg={stats['avg']}ms, total={stats['total']}ms")
    push_result("pipeline", stats)
    return json.dumps(stats)


# ========== 生命周期 ==========

def on_ready(window_id, data):
    global bench_win_id, base_url

    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    base_url = tools.set_protocol_service_path(web_dir)
    print(f"[启动] 协议服务: {base_url}")

    bench_win_id = window.create_webview_window(
        f"{base_url}benchmark.html",
        title="JadeView 2.1.1 性能测试",
        width=900,
        height=700,
        theme="System",
    )
    print(f"[启动] 测试窗口 ID: {bench_win_id}")


def on_all_closed(window_id, data):
    print("\n[退出] 窗口关闭")
    jadeview.cleanup()


def print_summary():
    """在控制台输出汇总"""
    print("\n" + "=" * 60)
    print("  JadeView 2.1.1 性能基准测试 - 汇总报告")
    print("=" * 60)
    print(f"  JadeView: {tools.jadeview_version()}")
    print(f"  WebView2: {tools.get_webview_version()}")
    print(f"  Win11: {tools.is_windows_11()}")
    print("=" * 60)


def main():
    print("=" * 50)
    print("  JadeView 2.1.1 性能基准测试")
    print("=" * 50)

    # 事件
    ipc.on(events.APP_READY, on_ready)
    ipc.on(events.WINDOW_ALL_CLOSED, on_all_closed)
    ipc.on(events.JAVASCRIPT_RESULT, on_js_result_bench)

    # IPC handlers (前端触发)
    ipc.register_ipc_handler("bench:windows", bench_windows)
    ipc.register_ipc_handler("bench:ipc_throughput", bench_ipc_throughput)
    ipc.register_ipc_handler("bench:js_exec", bench_js_exec)
    ipc.register_ipc_handler("bench:pipeline", bench_pipeline)
    ipc.register_ipc_handler("bench:pong", handle_bench_pong)

    ok = jadeview.init(
        "JadeViewBenchmark",
        "jvbenchmark",
        enable_devmod=True,
    )
    if not ok:
        print("[错误] 初始化失败!")
        return

    print_summary()
    jadeview.run()
    print("[完成] 测试已退出")


if __name__ == "__main__":
    main()
